
from app.models import Decision
from app.schemas.action import ActionRequest
from app.services.policy import evaluate_policies
from app.services.risk import calculate_risk


def make_request(**overrides):
    data = {
        "agent_id": "test-agent",
        "action": "read_customer_profile",
        "resource": "/customers/123",
        "tool_id": None,
        "sensitivity": 0,
        "financial_amount": 0,
        "external_destination": False,
        "session_actions": [],
        "context": {},
    }
    data.update(overrides)
    return ActionRequest(**data)


def test_low_risk_read_action():
    request = make_request(
        action="read_customer_profile",
        sensitivity=10,
    )

    score, reasons = calculate_risk(request, "assist")

    assert score < 70
    assert "Sensitive data access" not in reasons


def test_high_sensitivity_action_increases_risk():
    request = make_request(
        action="read_sensitive",
        sensitivity=80,
    )

    score, reasons = calculate_risk(request, "assist")

    assert score >= 30
    assert "Sensitive data access" in reasons


def test_high_value_external_action_is_high_risk():
    request = make_request(
        action="transfer_funds",
        financial_amount=5000,
        external_destination=True,
        sensitivity=80,
        session_actions=["login", "view_account", "prepare_transfer"],
    )

    score, reasons = calculate_risk(request, "assist")

    assert score >= 70
    assert "High-value financial action" in reasons
    assert "External destination" in reasons


def test_production_destructive_action_is_blocked_by_policy():
    request = make_request(
        action="delete_production_database",
        resource="/production/database",
        sensitivity=100,
        context={"environment": "production"},
        session_actions=[
            "login",
            "access_production",
            "disable_backup",
        ],
    )

    score, risk_reasons = calculate_risk(request, "assist")

    decision, approval_required, policy_reasons = evaluate_policies(
        request,
        score,
        [],
    )

    assert score == 45
    assert decision == Decision.BLOCK
    assert approval_required is False
    assert "Production destructive action is blocked by default" in policy_reasons
