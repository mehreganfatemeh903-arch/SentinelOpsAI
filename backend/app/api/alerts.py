from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.deps import current_user
from app.db.session import get_db
from app.models import EventType, RuntimeEvent
router=APIRouter(prefix='/alerts',tags=['security'])
@router.get('')
def alerts(limit:int=50,db:Session=Depends(get_db),_=Depends(current_user)):
    rows=db.scalars(select(RuntimeEvent).where(RuntimeEvent.event_type==EventType.SECURITY).order_by(RuntimeEvent.created_at.desc()).limit(min(limit,200))).all()
    return rows
