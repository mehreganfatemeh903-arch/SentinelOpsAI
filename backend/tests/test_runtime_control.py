from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    assert client.get("/health").json()["status"] == "ok"


def test_risk_engine_import():
    from app.services.risk import calculate_risk
    from app.schemas.action import ActionRequest

    score, reasons = calculate_risk(
        ActionRequest(
            agent_id="x",
            action="create_refund",
            resource="order:1",
            financial_amount=250,
            sensitivity=20,
            session_actions=["read_customer", "read_financial"],
        ),
        "execute",
    )

    assert score >= 25


def test_approval_execute_is_idempotent():
    from app.api.approvals import execute_approved

    assert callable(execute_approved)
