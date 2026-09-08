from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.deps import current_user
from app.db.session import get_db
from app.models import RuntimeEvent
router=APIRouter(prefix='/events',tags=['audit'])
@router.get('')
def list_events(limit:int=50,db:Session=Depends(get_db),_=Depends(current_user)):
    return db.scalars(select(RuntimeEvent).order_by(RuntimeEvent.created_at.desc()).limit(min(limit,200))).all()
