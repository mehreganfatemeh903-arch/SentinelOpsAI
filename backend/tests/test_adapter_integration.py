from app.db.session import SessionLocal
from app.models import Agent, AgentTool, Tool
from app.services.adapters import AdapterRequest, AdapterResult, registry


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
        return agent.id, tool
    finally:
        db.close()


def test_simulated_adapter_executes_without_secret():
    agent_id, tool = _get_bound_tool()

    assert tool.adapter_name == "simulated"

    adapter = registry.get(
        tool.adapter_name,
        tool.credential_ref,
    )

    result = adapter.execute(
        AdapterRequest(
            agent_id=agent_id,
            tool_id=tool.id,
            action="read",
            resource="security:test",
            context={},
        )
    )

    assert isinstance(result, AdapterResult)
    assert result.status == "simulated"
    assert result.action == "read"
    assert result.resource == "security:test"


def test_unknown_adapter_is_rejected():
    from pytest import raises

    with raises(ValueError):
        registry.get("unknown-adapter")


def test_environment_adapter_requires_credential_ref():
    from pytest import raises

    with raises(Exception):
        registry.get("environment")
