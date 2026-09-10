from pydantic import BaseModel, ConfigDict, Field

class ToolCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    description: str | None = None
    sensitivity: int = Field(0, ge=0, le=100)
    adapter_name: str = Field(default="simulated", min_length=2, max_length=80)
    credential_ref: str | None = Field(default=None, max_length=120)

class ToolRead(ToolCreate):
    id: str
    active: bool
    model_config = ConfigDict(from_attributes=True)

class ToolBinding(BaseModel):
    tool_id: str
    enabled: bool = True
