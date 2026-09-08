from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.deps import require_roles
from app.core.api_keys import generate_api_key, hash_api_key
from app.db.session import get_db
from app.models import Agent, AgentApiKey, UserRole
from app.schemas.api_key import ApiKeyCreate, ApiKeyCreated, ApiKeyRead

router=APIRouter(prefix='/agents',tags=['agent-credentials'])

@router.post('/{agent_id}/keys',response_model=ApiKeyCreated,status_code=201)
def create_key(agent_id:str,p:ApiKeyCreate,db:Session=Depends(get_db),_=Depends(require_roles(UserRole.ADMIN,UserRole.OPERATOR))):
    agent=db.get(Agent,agent_id)
    if not agent: raise HTTPException(404,'Agent not found')
    raw,digest=generate_api_key()
    key=AgentApiKey(agent_id=agent_id,key_hash=digest,name=p.name)
    db.add(key); db.commit(); db.refresh(key)
    return ApiKeyCreated(id=key.id,agent_id=key.agent_id,name=key.name,active=key.active,last_used_at=key.last_used_at,created_at=key.created_at,api_key=raw)

@router.get('/{agent_id}/keys',response_model=list[ApiKeyRead])
def list_keys(agent_id:str,db:Session=Depends(get_db),_=Depends(require_roles(UserRole.ADMIN,UserRole.OPERATOR))):
    return list(db.scalars(select(AgentApiKey).where(AgentApiKey.agent_id==agent_id).order_by(AgentApiKey.created_at.desc())))

@router.delete('/{agent_id}/keys/{key_id}',status_code=204)
def revoke_key(agent_id:str,key_id:str,db:Session=Depends(get_db),_=Depends(require_roles(UserRole.ADMIN,UserRole.OPERATOR))):
    key=db.get(AgentApiKey,key_id)
    if not key or key.agent_id!=agent_id: raise HTTPException(404,'API key not found')
    key.active=False; db.commit(); return None


def authenticate_agent_key(raw_key:str|None,db:Session):
    if not raw_key: return None
    key=db.scalar(select(AgentApiKey).where(AgentApiKey.key_hash==hash_api_key(raw_key),AgentApiKey.active.is_(True)))
    if not key: return None
    key.last_used_at=datetime.now(timezone.utc); db.commit()
    return db.get(Agent,key.agent_id)
