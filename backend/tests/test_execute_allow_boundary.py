from unittest.mock import Mock, patch
import pytest
from app.api.actions import execute_action
from app.models import Tool, Decision
from app.schemas.action import ActionDecision, ActionRequest
from app.services.adapters import AdapterResult


def _request():
    return ActionRequest(
        agent_id="agent-test",
        tool_id="tool-test",
        action="read",
        resource="test-resource",
        sensitivity=0,
    )


def test_execute_allow_calls_adapter():
    db = Mock()

    tool = Tool(
        id="tool-test",
        name="Test Tool",
        description="Test",
        sensitivity=0,
        active=True,
        adapter_name="simulated",
        credential_ref=None,
    )

    db.get.return_value = tool

    decision = ActionDecision(
        decision=Decision.ALLOW.value,
        risk_score=5,
        reasons=[],
        approval_required=False,
        event_id="event-test",
    )

    adapter = Mock()
    adapter.execute.return_value = AdapterResult(
        status="simulated",
        action="read",
        resource="test-resource",
        message="ok",
        data={"verified": True},
    )

    with patch(
        "app.api.actions._authorize",
        return_value=decision,
    ), patch(
        "app.api.actions.registry.get",
        return_value=adapter,
    ) as mock_get:

        result = execute_action(_request(), db)

    assert result.executed is True
    assert result.output["status"] == "simulated"
    assert result.output["action"] == "read"
    assert result.output["resource"] == "test-resource"
    assert result.output["data"]["verified"] is True

    mock_get.assert_called_once_with("simulated", None)
    adapter.execute.assert_called_once()

def test_execute_environment_adapter_requires_server_credential():
    db = Mock()

    tool = Tool(
        id="tool-test",
        name="Environment Tool",
        description="Test",
        sensitivity=0,
        active=True,
        adapter_name="environment",
        credential_ref="SENTINELOPS_EXTERNAL_TOOL_SECRET",
    )

    db.get.return_value = tool

    decision = ActionDecision(
        decision=Decision.ALLOW.value,
        risk_score=5,
        reasons=[],
        approval_required=False,
        event_id="event-test",
    )

    with patch(
        "app.api.actions._authorize",
        return_value=decision,
    ):
        result = execute_action(_request(), db)

    assert result.executed is False
def test_execute_environment_adapter_missing_credential_returns_502():
    db = Mock()

    tool = Tool(
        id="tool-test",
        name="Environment Tool",
        description="Test",
        sensitivity=0,
        active=True,
        adapter_name="environment",
        credential_ref="SENTINELOPS_MISSING_SECRET",
    )

    db.get.return_value = tool

    decision = ActionDecision(
        decision=Decision.ALLOW.value,
        risk_score=5,
        reasons=[],
        approval_required=False,
        event_id="event-test",
    )

    with patch(
        "app.api.actions._authorize",
        return_value=decision,
    ), patch(
        "app.api.actions.registry.get",
    ) as mock_get:

        with pytest.raises(Exception) as exc_info:
            execute_action(_request(), db)

    assert exc_info.value.status_code == 502
    mock_get.assert_called_once_with(
        "environment",
        "SENTINELOPS_MISSING_SECRET",
    )
