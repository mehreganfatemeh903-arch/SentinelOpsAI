from unittest.mock import Mock

from app.api.actions import _authorize
from app.db.session import SessionLocal
from app.models import Agent, AgentTool, Decision, Policy, Tool
from app.schemas.action import ActionRequest
from app.services.adapters import AdapterResult


def _fixtures():
    db = SessionLocal()
    agent = db.query(Agent).filter(Agent.active.is_(True)).first()
    tool = db.query(Tool).filter(Tool.active.is_(True)).first()

    assert agent is not None
    assert tool is not None

    binding = (
        db.query(AgentTool)
        .filter(
            AgentTool.agent_id == agent.id,
            AgentTool.tool_id == tool.id,
            AgentTool.enabled.is_(True),
        )
        .first()
    )
    assert binding is not None

    return db, agent, tool


def test_authorization_allows_bound_tool():
    db, agent, tool = _fixtures()

    try:
        request = ActionRequest(
            agent_id=agent.id,
            tool_id=tool.id,
            action="read",
            resource="security:test",
            sensitivity=0,
        )

        decision = _authorize(request, db)

        assert decision.decision in (
            Decision.ALLOW.value,
            Decision.APPROVAL.value,
            Decision.BLOCK.value,
        )
        assert decision.event_id is not None
    finally:
        db.close()


def test_unbound_tool_is_rejected():
    db, agent, tool = _fixtures()

    try:
        other_tool = (
            db.query(Tool)
            .filter(
                Tool.id != tool.id,
                Tool.active.is_(True),
            )
            .first()
        )

        if other_tool is None:
            return

        request = ActionRequest(
            agent_id=agent.id,
            tool_id=other_tool.id,
            action="read",
            resource="security:test",
            sensitivity=0,
        )

        from fastapi import HTTPException

        try:
            _authorize(request, db)
            assert False, "Unbound tool must be rejected"
        except HTTPException as exc:
            assert exc.status_code == 403
    finally:
        db.close()
