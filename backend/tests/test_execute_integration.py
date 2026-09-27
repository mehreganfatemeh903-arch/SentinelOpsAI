from unittest.mock import patch

from fastapi.testclient import TestClient

from app.api.deps import current_user
from app.main import app
from app.schemas.action import ActionDecision


client = TestClient(app)


def test_execute_requires_tool_id():
    app.dependency_overrides[current_user] = lambda: object()

    decision = ActionDecision(
        decision="allow",
        risk_score=0,
        reasons=[],
        approval_required=False,
        event_id="test-event",
    )

    try:
        with patch(
            "app.api.actions._authorize",
            return_value=decision,
        ):
            response = client.post(
                "/api/v1/actions/execute",
                json={
                    "agent_id": "test-agent",
                    "action": "read",
                    "resource": "test-resource",
                    "sensitivity": 0,
                },
            )
    finally:
        app.dependency_overrides.clear()

    print(response.status_code, response.json())
    assert response.status_code == 400
    assert response.json()["detail"] == "tool_id is required for execution"
