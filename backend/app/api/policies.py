from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.deps import current_user, require_roles
from app.db.session import get_db
from app.models import Policy, UserRole
from app.schemas.policy import PolicyCreate, PolicyRead
router=APIRouter(prefix='/policies',tags=['policies'])
@router.post('',response_model=PolicyRead,status_code=201)
def create_policy(p:PolicyCreate,db:Session=Depends(get_db),_=Depends(require_roles(UserRole.ADMIN,UserRole.OPERATOR))):
    x=Policy(**p.model_dump()); db.add(x); db.commit(); db.refresh(x); return x
@router.get('',response_model=list[PolicyRead])
def list_policies(db:Session=Depends(get_db),_=Depends(current_user)): return list(db.scalars(select(Policy).order_by(Policy.name)))
