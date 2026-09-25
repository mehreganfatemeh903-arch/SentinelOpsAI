import httpx
from unittest.mock import Mock, patch

from app.api.actions import execute_action
from app.models import Tool, Decision
from app.schemas.action import ActionDecision, ActionRequest


def test_gateway_executes_http_tool_with_server_side_secret(monkeypatch):
    monkeypatch.setenv("SENTINELOPS_EXTERNAL_TOOL_SECRET", "integration-secret")

    db = Mock()

    tool = Tool(
        id="tool-http",
        name="HTTP Integration Tool",
        description="Integration test",
        sensitivity=0,
        active=True,
        adapter_name="http",
        credential_ref="SENTINELOPS_EXTERNAL_TOOL_SECRET",
        endpoint="https://example.com/tool",
    )

    db.get.return_value = tool

    request = ActionRequest(
        agent_id="agent-test",
        tool_id="tool-http",
        action="run",
        resource="/health",
        sensitivity=0,
        context={"integration": True},
    )

    decision = ActionDecision(
        decision=Decision.ALLOW.value,
        risk_score=5,
        reasons=[],
        approval_required=False,
        event_id="integration-event",
    )

    captured = {}

    def fake_post(url, **kwargs):
        captured["url"] = url
        captured["headers"] = kwargs["headers"]
        captured["json"] = kwargs["json"]
        return httpx.Response(
            200,
            request=httpx.Request("POST", url),
        )

    with patch(
        "app.api.actions._authorize",
        return_value=decision,
    ), patch(
        "app.services.adapters.socket.getaddrinfo",
        return_value=[
            (2, 1, 6, "", ("93.184.216.34", 443))
        ],
    ), patch(
        "app.services.adapters.httpx.post",
        side_effect=fake_post,
    ):
        result = execute_action(request, db)

    assert result.executed is True
    assert result.output["status"] == "executed"
    assert result.output["data"]["status_code"] == 200
    assert captured["headers"]["Authorization"] == "Bearer integration-secret"
    assert captured["json"]["action"] == "run"
    assert captured["json"]["resource"] == "/health"
    assert "integration-secret" not in str(result)
