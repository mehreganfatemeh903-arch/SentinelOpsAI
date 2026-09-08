from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.deps import current_user, require_roles
from app.db.session import get_db
from app.models import Agent, UserRole
from app.schemas.agent import AgentCreate, AgentRead
router=APIRouter(prefix='/agents',tags=['agents'])
@router.post('',response_model=AgentRead,status_code=201)
def create_agent(p:AgentCreate,db:Session=Depends(get_db),_=Depends(require_roles(UserRole.ADMIN,UserRole.OPERATOR))):
    a=Agent(**p.model_dump()); db.add(a); db.commit(); db.refresh(a); return a
@router.get('',response_model=list[AgentRead])
def list_agents(db:Session=Depends(get_db),_=Depends(current_user)): return list(db.scalars(select(Agent).order_by(Agent.name)))
@router.post('/{agent_id}/suspend',response_model=AgentRead)
def suspend(agent_id:str,db:Session=Depends(get_db),_=Depends(require_roles(UserRole.ADMIN,UserRole.OPERATOR))):
    a=db.get(Agent,agent_id)
    if not a: raise HTTPException(404,'Agent not found')
    a.active=False; db.commit(); db.refresh(a); return a
@router.post('/{agent_id}/resume',response_model=AgentRead)
def resume(agent_id:str,db:Session=Depends(get_db),_=Depends(require_roles(UserRole.ADMIN,UserRole.OPERATOR))):
    a=db.get(Agent,agent_id)
    if not a: raise HTTPException(404,'Agent not found')
    a.active=True; db.commit(); db.refresh(a); return a
