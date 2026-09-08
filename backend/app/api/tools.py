from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.deps import current_user, require_roles
from app.db.session import get_db
from app.models import Agent, AgentTool, Tool, UserRole
from app.schemas.tool import ToolCreate, ToolRead, ToolBinding
router=APIRouter(prefix='/tools',tags=['tools'])
@router.post('',response_model=ToolRead,status_code=201)
def create_tool(p:ToolCreate,db:Session=Depends(get_db),_=Depends(require_roles(UserRole.ADMIN,UserRole.OPERATOR))):
    t=Tool(**p.model_dump()); db.add(t); db.commit(); db.refresh(t); return t
@router.get('',response_model=list[ToolRead])
def list_tools(db:Session=Depends(get_db),_=Depends(current_user)): return list(db.scalars(select(Tool).order_by(Tool.name)))
@router.post('/{tool_id}/bind/{agent_id}',status_code=201)
def bind_tool(tool_id:str,agent_id:str,p:ToolBinding|None=None,db:Session=Depends(get_db),_=Depends(require_roles(UserRole.ADMIN,UserRole.OPERATOR))):
    tool=db.get(Tool,tool_id); agent=db.get(Agent,agent_id)
    if not tool or not agent: raise HTTPException(404,'Agent or tool not found')
    existing=db.scalar(select(AgentTool).where(AgentTool.agent_id==agent_id,AgentTool.tool_id==tool_id))
    if existing:
        existing.enabled=True if p is None else p.enabled
    else:
        db.add(AgentTool(agent_id=agent_id,tool_id=tool_id,enabled=True if p is None else p.enabled))
    db.commit(); return {'agent_id':agent_id,'tool_id':tool_id,'enabled':True if p is None else p.enabled}
@router.get('/agent/{agent_id}',response_model=list[ToolRead])
def agent_tools(agent_id:str,db:Session=Depends(get_db),_=Depends(current_user)):
    return list(db.scalars(select(Tool).join(AgentTool,AgentTool.tool_id==Tool.id).where(AgentTool.agent_id==agent_id,AgentTool.enabled.is_(True),Tool.active.is_(True)).order_by(Tool.name)))
