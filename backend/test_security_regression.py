from app.db.session import SessionLocal
from app.models import Agent, Approval, Decision, EventType, RuntimeEvent, User, UserRole
from app.api.approvals import decide, execute_approved
from fastapi import HTTPException


def get_operator(db):
    user = db.query(User).filter(User.role.in_([UserRole.ADMIN, UserRole.OPERATOR])).first()
    assert user is not None
    return user


def create_test_event(db, decision=Decision.APPROVAL):
    agent = db.query(Agent).filter(Agent.active.is_(True)).first()
    assert agent is not None

    event = RuntimeEvent(
        agent_id=agent.id,
        event_type=EventType.ACTION,
        action="security.regression_test",
        resource="/security/test",
        decision=decision,
        risk_score=85,
        reasons=["Security regression test"],
        metadata_json={},
    )
    db.add(event)
    db.flush()

    approval = Approval(
        event_id=event.id,
        status="pending",
    )
    db.add(approval)
    db.commit()
    db.refresh(approval)
    db.refresh(event)

    return agent, event, approval


def test_approval_approval_updates_audit_event():
    db = SessionLocal()
    try:
        user = get_operator(db)
        _, event, approval = create_test_event(db)

        result = decide(
            approval.id,
            approve=True,
            note="Regression approval",
            db=db,
            u=user,
        )

        db.refresh(event)
        db.refresh(approval)

        assert result["status"] == "approved"
        assert approval.status == "approved"
        assert approval.reviewer_id == user.id
        assert event.event_type == EventType.APPROVAL
        assert event.decision == Decision.ALLOW
        assert "Approved by human reviewer" in event.reasons
    finally:
        db.close()


def test_approval_rejection_blocks_execution():
    db = SessionLocal()
    try:
        user = get_operator(db)
        _, event, approval = create_test_event(db)

        result = decide(
            approval.id,
            approve=False,
            note="Regression rejection",
            db=db,
            u=user,
        )

        db.refresh(event)
        db.refresh(approval)

        assert result["status"] == "rejected"
        assert approval.status == "rejected"
        assert event.event_type == EventType.APPROVAL
        assert event.decision == Decision.BLOCK
        assert "Rejected by human reviewer" in event.reasons

        try:
            execute_approved(
                approval.id,
                db=db,
                u=user,
            )
            assert False, "Rejected approval must not execute"
        except HTTPException as exc:
            assert exc.status_code == 409
            assert exc.detail == "Approval must be approved before execution"
    finally:
        db.close()


def test_approved_event_executes_only_once():
    db = SessionLocal()
    try:
        user = get_operator(db)
        _, event, approval = create_test_event(db)

        decide(
            approval.id,
            approve=True,
            note="Execute-once regression",
            db=db,
            u=user,
        )

        result = execute_approved(
            approval.id,
            db=db,
            u=user,
        )

        assert result["status"] == "executed"
        assert result["executed"] is True

        db.refresh(event)

        assert event.metadata_json["executed"] is True
        assert event.event_type == EventType.ACTION

        try:
            execute_approved(
                approval.id,
                db=db,
                u=user,
            )
            assert False, "Approved action must not execute twice"
        except HTTPException as exc:
            assert exc.status_code == 409
            assert exc.detail == "Approved action has already been executed"
    finally:
        db.close()
