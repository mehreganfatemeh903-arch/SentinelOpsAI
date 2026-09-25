from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.db.session import get_db
from app.services.credentials import CredentialError
from app.services.adapters import AdapterRequest, registry

from app.models import (
    Agent,
    Approval,
    Decision,
    EventType,
    RuntimeEvent,
    Tool,
    User,
    UserRole,
)

router = APIRouter(prefix="/approvals", tags=["approvals"])


@router.get("")
def pending(
    db: Session = Depends(get_db),
    _=Depends(require_roles(UserRole.ADMIN, UserRole.OPERATOR)),
):
    rows = db.scalars(
        select(Approval)
        .where(Approval.status == "pending")
        .order_by(Approval.created_at.desc())
    ).all()

    result = []

    for approval in rows:
        event = db.get(RuntimeEvent, approval.event_id)

        result.append(
            {
                "id": approval.id,
                "event_id": approval.event_id,
                "status": approval.status,
                "created_at": approval.created_at,
                "action": event.action if event else None,
                "resource": event.resource if event else None,
                "risk_score": event.risk_score if event else None,
                "reasons": event.reasons if event else [],
            }
        )

    return result


@router.post("/{approval_id}/decision")
def decide(
    approval_id: str,
    approve: bool,
    note: str = "",
    db: Session = Depends(get_db),
    u: User = Depends(
        require_roles(UserRole.ADMIN, UserRole.OPERATOR)
    ),
):
    approval = db.get(Approval, approval_id)

    if not approval or approval.status != "pending":
        raise HTTPException(
            status_code=404,
            detail="Pending approval not found",
        )

    event = db.get(RuntimeEvent, approval.event_id)

    approval.status = "approved" if approve else "rejected"
    approval.reviewer_id = u.id
    approval.note = note

    if event:
        event.event_type = EventType.APPROVAL
        event.decision = (
            Decision.ALLOW if approve else Decision.BLOCK
        )

        event.reasons = (event.reasons or []) + [
            (
                "Approved by human reviewer"
                if approve
                else "Rejected by human reviewer"
            )
        ]

    db.commit()

    return {
        "status": approval.status,
        "event_id": approval.event_id,
        "execution_required": approve,
    }


@router.post("/{approval_id}/execute")
def execute_approved(
    approval_id: str,
    db: Session = Depends(get_db),
    u: User = Depends(
        require_roles(UserRole.ADMIN, UserRole.OPERATOR)
    ),
):
    approval = db.get(Approval, approval_id)

    if not approval:
        raise HTTPException(
            status_code=404,
            detail="Approval not found",
        )

    if approval.status != "approved":
        raise HTTPException(
            status_code=409,
            detail="Approval must be approved before execution",
        )

    event = db.get(RuntimeEvent, approval.event_id)

    if not event:
        raise HTTPException(
            status_code=404,
            detail="Approved event not found",
        )

    metadata = event.metadata_json or {}

    if metadata.get("executed") is True:
        raise HTTPException(
            status_code=409,
            detail="Approved action has already been executed",
        )

    agent = db.get(Agent, event.agent_id)

    if not agent:
        raise HTTPException(
            status_code=404,
            detail="Agent not found",
        )

    if not agent.active:
        raise HTTPException(
            status_code=409,
            detail="Agent is suspended",
        )

    if event.decision != Decision.ALLOW:
        raise HTTPException(
            status_code=409,
            detail="Approved event is not executable",
        )

    tool_id = metadata.get("tool_id")
    if not tool_id:
        raise HTTPException(status_code=400, detail="Approved event has no tool_id")

    tool = db.get(Tool, tool_id)
    if not tool or not tool.active:
        raise HTTPException(status_code=404, detail="Tool not found or inactive")

    try:
        adapter = registry.get(
            tool.adapter_name,
            tool.credential_ref,
            tool.endpoint,
        )
    except (ValueError, CredentialError) as exc:
        raise HTTPException(status_code=500, detail="Execution adapter is not configured") from exc

    adapter_request = AdapterRequest(
        agent_id=event.agent_id,
        tool_id=tool.id,
        action=event.action,
        resource=event.resource,
        context=metadata.get("context") or {},
    )

    try:
        result = adapter.execute(adapter_request)
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Tool adapter execution failed") from exc

    output = {
        "status": result.status,
        "action": result.action,
        "resource": result.resource,
        "message": result.message,
        "data": result.data,
    }

    event.metadata_json = {
        **(event.metadata_json or {}),
        "executed": True,
        "executed_by": u.id,
        "execution_output": output,
    }
    event.event_type = EventType.ACTION

    db.commit()

    return {
        "status": "executed",
        "approval_id": approval.id,
        "event_id": event.id,
        "action": event.action,
        "resource": event.resource,
        "executed": True,
        "output": output,
    }


