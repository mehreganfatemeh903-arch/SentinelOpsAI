from pydantic import BaseModel, Field


class ActionRequest(BaseModel):
    agent_id: str
    action: str = Field(min_length=1, max_length=120)
    resource: str = Field(min_length=1, max_length=500)
    tool_id: str | None = None
    sensitivity: int = Field(default=0, ge=0, le=100)
    financial_amount: float = Field(default=0, ge=0)
    external_destination: bool = False
    session_actions: list[str] = Field(default_factory=list)
    context: dict = Field(default_factory=dict)


class ActionDecision(BaseModel):
    decision: str
    risk_score: int
    reasons: list[str]
    approval_required: bool
    event_id: str


class ExecutionResult(ActionDecision):
    executed: bool
    output: dict | None = None
