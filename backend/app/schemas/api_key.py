from datetime import datetime
from pydantic import BaseModel, Field

class ApiKeyCreate(BaseModel):
    name: str = Field(default='runtime', min_length=1, max_length=120)

class ApiKeyRead(BaseModel):
    id: str
    agent_id: str
    name: str
    active: bool
    last_used_at: datetime | None = None
    created_at: datetime

class ApiKeyCreated(ApiKeyRead):
    api_key: str
