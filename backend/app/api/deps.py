from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from app.core.security import decode_token
from app.db.session import get_db
from app.models import User, UserRole
bearer=HTTPBearer(auto_error=False)
def current_user(creds:HTTPAuthorizationCredentials=Depends(bearer), db:Session=Depends(get_db)):
    if not creds: raise HTTPException(status_code=401,detail='Authentication required')
    payload=decode_token(creds.credentials)
    if not payload: raise HTTPException(status_code=401,detail='Invalid or expired token')
    user=db.get(User,payload.get('sub'))
    if not user or not user.active: raise HTTPException(status_code=401,detail='User is inactive')
    return user
def require_roles(*roles:UserRole):
    def dep(user=Depends(current_user)):
        if user.role not in roles: raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail='Insufficient permissions')
        return user
    return dep
