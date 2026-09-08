
from app.models import Decision, Policy
from app.schemas.action import ActionRequest


DESTRUCTIVE_ACTION_PREFIXES = (
    "delete",
    "drop",
    "destroy",
    "terminate",
    "purge",
    "remove",
)

PRODUCTION_ONLY_DESTRUCTIVE_ACTIONS = {
    "disable_backup",
}


def matches(pattern: str, action: str) -> bool:
    return (
        pattern == "*"
        or pattern == action
        or (pattern.endswith("*") and action.startswith(pattern[:-1]))
    )


def is_destructive_action(action: str) -> bool:
    normalized = action.strip().lower()
    return normalized.startswith(DESTRUCTIVE_ACTION_PREFIXES) or normalized in (
        PRODUCTION_ONLY_DESTRUCTIVE_ACTIONS
    )


def is_production_context(request: ActionRequest) -> bool:
    environment = request.context.get("environment")
    return isinstance(environment, str) and environment.strip().lower() == "production"


def evaluate_policies(
    request: ActionRequest,
    risk_score: int,
    policies: list[Policy],
):
    reasons = []
    approval = False
    decision = Decision.ALLOW

    # Security invariant:
    # destructive operations against production must never be allowed
    # merely because their calculated runtime risk is below a threshold.
    if is_production_context(request) and is_destructive_action(request.action):
        return (
            Decision.BLOCK,
            False,
            ["Production destructive action is blocked by default"],
        )

    for p in policies:
        if not p.enabled or not matches(p.action_pattern, request.action):
            continue

        if risk_score < p.min_risk:
            continue

        if (
            p.max_financial_amount is not None
            and request.financial_amount > p.max_financial_amount
        ):
            continue

        reasons.append(f"Policy matched: {p.name} v{p.version}")

        if p.effect == Decision.BLOCK:
            return Decision.BLOCK, False, reasons

        if p.require_approval or p.effect == Decision.APPROVAL:
            approval = True
            decision = Decision.APPROVAL

    if risk_score >= 90:
        return (
            Decision.BLOCK,
            False,
            reasons + ["Critical runtime risk threshold reached"],
        )
    if risk_score >= 70 and decision == Decision.ALLOW:
        return (
           Decision.APPROVAL,
           True,
           reasons + ["High runtime risk requires human approval"],
        )

    return decision, approval, reasons
