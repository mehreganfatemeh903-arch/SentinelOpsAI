from pydantic import BaseModel, Field
class PolicyCreate(BaseModel):
    name:str=Field(min_length=2,max_length=160); action_pattern:str='*'; min_risk:int=Field(0,ge=0,le=100); max_financial_amount:float|None=None; require_approval:bool=False; effect:str='allow'
class PolicyRead(PolicyCreate):
    id:str; enabled:bool; version:int
