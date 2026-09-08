from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.deps import current_user
from app.core.security import create_access_token, hash_password, verify_password
from app.db.session import get_db
from app.models import User, UserRole
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserRead
router=APIRouter(prefix='/auth',tags=['auth'])
def user_read(u): return UserRead(id=u.id,email=u.email,name=u.name,role=u.role.value,active=u.active)
@router.post('/register',response_model=TokenResponse,status_code=201)
def register(p:RegisterRequest,db:Session=Depends(get_db)):
    if db.scalar(select(User).where(User.email==p.email)): raise HTTPException(409,'Email already registered')
    count=db.scalar(select(User.id).limit(1)); role=UserRole.ADMIN if count is None else UserRole.VIEWER
    u=User(email=p.email,password_hash=hash_password(p.password),name=p.name,role=role); db.add(u); db.commit(); db.refresh(u)
    return TokenResponse(access_token=create_access_token(u.id,u.role.value),user=user_read(u))
@router.post('/login',response_model=TokenResponse)
def login(p:LoginRequest,db:Session=Depends(get_db)):
    u=db.scalar(select(User).where(User.email==p.email))
    if not u or not verify_password(p.password,u.password_hash): raise HTTPException(401,'Invalid email or password')
    return TokenResponse(access_token=create_access_token(u.id,u.role.value),user=user_read(u))
@router.get('/me',response_model=UserRead)
def me(u=Depends(current_user)): return user_read(u)
