from unittest.mock import Mock, patch

from app.api.actions import execute_action
from app.schemas.action import ActionDecision, ActionRequest


def _request():
    return ActionRequest(
        agent_id="agent-test",
        tool_id="tool-test",
        action="read",
        resource="test-resource",
        sensitivity=0,
    )


def _decision(value):
    return ActionDecision(
        decision=value,
        risk_score=10,
        reasons=[],
        approval_required=(value == "APPROVAL"),
        event_id="event-test",
    )


def test_execute_block_never_calls_adapter():
    db = Mock()

    with patch(
        "app.api.actions._authorize",
        return_value=_decision("BLOCK"),
    ), patch("app.api.actions.registry.get") as mock_get:

        result = execute_action(_request(), db)

    assert result.executed is False
    assert result.output is None
    mock_get.assert_not_called()


def test_execute_approval_never_calls_adapter():
    db = Mock()

    with patch(
        "app.api.actions._authorize",
        return_value=_decision("APPROVAL"),
    ), patch("app.api.actions.registry.get") as mock_get:

        result = execute_action(_request(), db)

    assert result.executed is False
    assert result.output is None
    mock_get.assert_not_called()
