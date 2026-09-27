from unittest.mock import Mock, patch

from fastapi.testclient import TestClient

from app.main import app
from app.models import Agent


client = TestClient(app)


def _request(agent_id="agent-1"):
    return {
        "agent_id": agent_id,
        "action": "read",
        "resource": "test-resource",
        "sensitivity": 0,
    }


def test_agent_authorize_without_key_returns_401():
    response = client.post(
        "/api/v1/actions/agent-authorize",
        json=_request(),
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Valid agent API key required"


def test_agent_authorize_invalid_key_returns_401():
    with patch(
        "app.api.actions.authenticate_agent_key",
        return_value=None,
    ):
        response = client.post(
            "/api/v1/actions/agent-authorize",
            headers={"X-Sentinel-Key": "sntl_invalid"},
            json=_request(),
        )

    assert response.status_code == 401
    assert response.json()["detail"] == "Valid agent API key required"


def test_agent_authorize_key_for_different_agent_returns_401():
    authenticated_agent = Mock(spec=Agent)
    authenticated_agent.id = "agent-2"

    with patch(
        "app.api.actions.authenticate_agent_key",
        return_value=authenticated_agent,
    ):
        response = client.post(
            "/api/v1/actions/agent-authorize",
            headers={"X-Sentinel-Key": "sntl_valid"},
            json=_request("agent-1"),
        )

    assert response.status_code == 401
    assert response.json()["detail"] == "Valid agent API key required"


def test_agent_authorize_valid_key_for_same_agent_reaches_authorize():
    authenticated_agent = Mock(spec=Agent)
    authenticated_agent.id = "agent-1"

    decision = {
        "decision": "allow",
        "risk_score": 0,
        "reasons": [],
        "approval_required": False,
        "event_id": "test-event",
    }

    with patch(
        "app.api.actions.authenticate_agent_key",
        return_value=authenticated_agent,
    ), patch(
        "app.api.actions._authorize",
        return_value=decision,
    ) as mock_authorize:
        response = client.post(
            "/api/v1/actions/agent-authorize",
            headers={"X-Sentinel-Key": "sntl_valid"},
            json=_request("agent-1"),
        )

    assert response.status_code == 200
    assert response.json() == decision
    mock_authorize.assert_called_once()
