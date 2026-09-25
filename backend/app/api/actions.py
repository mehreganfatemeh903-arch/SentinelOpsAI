
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.services.credentials import CredentialError
from app.api.deps import current_user
from app.api.api_keys import authenticate_agent_key
from app.db.session import get_db
from app.models import (
    Agent,
    AgentTool,
    Approval,
    Decision,
    EventType,
    Policy,
    RuntimeEvent,
    Tool,
)
from app.schemas.action import ActionDecision, ActionRequest, ExecutionResult
from app.services.adapters import AdapterRequest, registry
from app.services.policy import evaluate_policies
from app.services.risk import calculate_risk

router = APIRouter(prefix="/actions", tags=["runtime-control"])


def _authorize(req: ActionRequest, db: Session) -> ActionDecision:
    agent = db.get(Agent, req.agent_id)

    if not agent:
        raise HTTPException(404, "Agent not found")

    if not agent.active:
        raise HTTPException(409, "Agent is suspended")

    tool = None

    if req.tool_id:
        tool = db.get(Tool, req.tool_id)

        if not tool or not tool.active:
            raise HTTPException(404, "Tool not found or inactive")

        binding = db.scalar(
            select(AgentTool).where(
                AgentTool.agent_id == agent.id,
                AgentTool.tool_id == req.tool_id,
                AgentTool.enabled.is_(True),
            )
        )

        if not binding:
            raise HTTPException(
                403,
                "Tool is not authorized for this agent",
            )

    score, risk_reasons = calculate_risk(
        req,
        agent.autonomy_level.value,
    )

    if tool and tool.sensitivity > req.sensitivity:
        score = min(
            100,
            score + (tool.sensitivity - req.sensitivity) // 2,
        )
        risk_reasons.append(
            "Registered tool sensitivity applied"
        )

    policies = list(
        db.scalars(
            select(Policy).where(
                Policy.enabled.is_(True)
            )
        )
    )

    decision, approval_required, policy_reasons = evaluate_policies(
        req,
        score,
        policies,
    )

    reasons = risk_reasons + policy_reasons

    event_type = (
        EventType.SECURITY
        if decision == Decision.BLOCK
        else EventType.ACTION
    )

    event = RuntimeEvent(
        agent_id=agent.id,
        event_type=event_type,
        action=req.action,
        resource=req.resource,
        decision=decision,
        risk_score=score,
        reasons=reasons,
        metadata_json={
            "tool_id": req.tool_id,
            "sensitivity": req.sensitivity,
            "financial_amount": req.financial_amount,
            "external_destination": req.external_destination,
            "context": req.context,
            "session_actions": req.session_actions,
        },
    )

    db.add(event)
    db.flush()

    if approval_required:
        db.add(Approval(event_id=event.id))

    db.commit()
    db.refresh(event)

    return ActionDecision(
        decision=decision.value,
        risk_score=score,
        reasons=reasons,
        approval_required=approval_required,
        event_id=event.id,
    )


@router.post(
    "/authorize",
    response_model=ActionDecision,
)
def authorize_action(
    req: ActionRequest,
    db: Session = Depends(get_db),
    _=Depends(current_user),
):
    return _authorize(req, db)


@router.post(
    "/agent-authorize",
    response_model=ActionDecision,
)
def agent_authorize(
    req: ActionRequest,
    x_sentinel_key: str | None = Header(
        default=None,
        alias="X-Sentinel-Key",
    ),
    db: Session = Depends(get_db),
):
    agent = authenticate_agent_key(
        x_sentinel_key,
        db,
    )

    if not agent or agent.id != req.agent_id:
        raise HTTPException(
            401,
            "Valid agent API key required",
        )

    return _authorize(req, db)


@router.post(
    "/execute",
    response_model=ExecutionResult,
)
def execute_action(
    req: ActionRequest,
    db: Session = Depends(get_db),
    _=Depends(current_user),
):
    decision = _authorize(req, db)

    # Security boundary:
    # Only an explicit ALLOW decision can reach an adapter.
    if decision.decision != Decision.ALLOW.value:
        return ExecutionResult(
            **decision.model_dump(),
            executed=False,
            output=None,
        )

    # A tool must be explicitly selected for execution.
    if not req.tool_id:
        raise HTTPException(
            400,
            "tool_id is required for execution",
        )

    # Tool execution is routed through the configured adapter registry.
    # The adapter is server-side; the agent never receives credentials.
    tool = db.get(Tool, req.tool_id)
    if not tool or not tool.active:
        raise HTTPException(
            404,
            "Tool not found or inactive",
        )

    try:
        adapter = registry.get(
            tool.adapter_name,
            tool.credential_ref,
            tool.endpoint,
        )
    except (ValueError, CredentialError) as exc:
        raise HTTPException(
            500,
            "Execution adapter is not configured",
        ) from exc

    adapter_request = AdapterRequest(
        agent_id=req.agent_id,
        tool_id=req.tool_id,
        action=req.action,
        resource=req.resource,
        context=req.context,
    )

    try:
        result = adapter.execute(adapter_request)
    except Exception as exc:
        raise HTTPException(
            502,
            "Tool adapter execution failed",
        ) from exc

    return ExecutionResult(
        **decision.model_dump(),
        executed=True,
        output={
            "status": result.status,
            "action": result.action,
            "resource": result.resource,
            "message": result.message,
            "data": result.data,
        },
    )

