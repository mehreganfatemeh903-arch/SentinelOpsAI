from unittest.mock import Mock, patch

from app.api.approvals import execute_approved
from app.models import Agent, Approval, Decision, RuntimeEvent, Tool


def test_execute_approved_uses_tool_adapter():
    db = Mock()

    approval = Approval(
        id="approval-test",
        event_id="event-test",
        status="approved",
    )
    event = RuntimeEvent(
        id="event-test",
        agent_id="agent-test",
        action="read",
        resource="test-resource",
        decision=Decision.ALLOW,
        risk_score=10,
        reasons=[],
        metadata_json={
            "tool_id": "tool-test",
            "context": {"source": "test"},
        },
    )
    agent = Agent(
        id="agent-test",
        active=True,
    )
    tool = Tool(
        id="tool-test",
        name="test-tool",
        adapter_name="simulated",
        active=True,
    )

    def get(model, key):
        if model is Approval:
            return approval
        if model is RuntimeEvent:
            return event
        if model is Agent:
            return agent
        if model is Tool:
            return tool
        return None

    db.get.side_effect = get

    adapter = Mock()
    adapter.execute.return_value = Mock(
        status="executed",
        action="read",
        resource="test-resource",
        message="adapter executed",
        data={"ok": True},
    )

    user = Mock()
    user.id = "reviewer-test"

    with patch(
        "app.api.approvals.registry.get",
        return_value=adapter,
    ) as mock_registry:
        result = execute_approved("approval-test", db, user)

    mock_registry.assert_called_once_with(
        "simulated",
        None,
        None,
    )
    adapter.execute.assert_called_once()

    assert result["executed"] is True
    assert result["output"]["status"] == "executed"
    assert result["output"]["data"]["ok"] is True
    assert event.metadata_json["executed"] is True
