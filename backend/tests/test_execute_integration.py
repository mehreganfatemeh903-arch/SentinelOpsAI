from fastapi.testclient import TestClient

from app.main import app
from app.db.session import SessionLocal
from app.models import Agent, AgentTool, Tool


client = TestClient(app)


def _get_agent_and_tool():
    db = SessionLocal()
    try:
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

        return agent.id, tool.id
    finally:
        db.close()


def test_execute_requires_tool_id():
    agent_id, _ = _get_agent_and_tool()

    response = client.post(
        "/actions/execute",
        json={
            "agent_id": agent_id,
            "action": "read",
            "resource": "test-resource",
            "sensitivity": 0,
        },
    )

    assert response.status_code == 404
