from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.db.session import get_db
from app.models import (
    Agent,
    Approval,
    Decision,
    EventType,
    RuntimeEvent,
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

    output = {
        "status": "simulated",
        "action": event.action,
        "resource": event.resource,
        "message": "Approved tool execution passed through SentinelOps Gateway",
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

