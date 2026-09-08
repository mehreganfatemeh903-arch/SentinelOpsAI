from pydantic import BaseModel, ConfigDict, Field
from app.models import AutonomyLevel
class AgentCreate(BaseModel):
    name:str=Field(min_length=2,max_length=120); owner:str=Field(min_length=2,max_length=120); description:str|None=None; autonomy_level:AutonomyLevel=AutonomyLevel.ASSIST
class AgentRead(AgentCreate):
    id:str; active:bool
    model_config=ConfigDict(from_attributes=True)
