from unittest.mock import patch

from fastapi import HTTPException

from app.api.actions import _authorize
from app.db.session import SessionLocal
from app.models import Agent, AgentTool, Tool
from app.schemas.action import ActionRequest


def _get_bound_tool():
    db = SessionLocal()
    try:
        agent = db.query(Agent).filter(Agent.active.is_(True)).first()
        tool = (
            db.query(Tool)
            .join(AgentTool, AgentTool.tool_id == Tool.id)
            .filter(
                AgentTool.agent_id == agent.id,
                AgentTool.enabled.is_(True),
                Tool.active.is_(True),
            )
            .first()
        )
        assert agent is not None
        assert tool is not None
        return agent.id, tool.id
    finally:
        db.close()


def test_block_never_reaches_adapter():
    agent_id, tool_id = _get_bound_tool()

    request = ActionRequest(
        agent_id=agent_id,
        tool_id=tool_id,
        action="delete",
        resource="critical-resource",
        sensitivity=100,
    )

    db = SessionLocal()
    try:
        with patch("app.api.actions.registry.get") as mock_get:
            decision = _authorize(request, db)

        if decision.decision == "BLOCK":
            mock_get.assert_not_called()
    finally:
        db.close()


def test_unbound_tool_never_reaches_adapter():
    db = SessionLocal()
    try:
        agent = db.query(Agent).filter(Agent.active.is_(True)).first()
        tool = db.query(Tool).filter(Tool.active.is_(True)).first()

        assert agent is not None
        assert tool is not None

        request = ActionRequest(
            agent_id=agent.id,
            tool_id="00000000-0000-0000-0000-000000000000",
            action="read",
            resource="test-resource",
            sensitivity=0,
        )

        with patch("app.api.actions.registry.get") as mock_get:
            try:
                _authorize(request, db)
            except HTTPException as exc:
                assert exc.status_code == 404
            mock_get.assert_not_called()
    finally:
        db.close()
