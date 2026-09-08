from fastapi import FastAPI
from app.core.config import settings
from app.db.session import Base, engine
from app.api.auth import router as auth_router
from app.api.agents import router as agents_router
from app.api.tools import router as tools_router
from app.api.policies import router as policies_router
from app.api.actions import router as actions_router
from app.api.approvals import router as approvals_router
from app.api.events import router as events_router
from app.api.api_keys import router as api_keys_router
from app.api.alerts import router as alerts_router
import app.models
app=FastAPI(title=settings.app_name,version='0.3.0',description='Runtime control plane for AI agents')
@app.on_event('startup')
def startup(): Base.metadata.create_all(bind=engine)
app.include_router(auth_router,prefix='/api/v1'); app.include_router(agents_router,prefix='/api/v1'); app.include_router(tools_router,prefix='/api/v1'); app.include_router(policies_router,prefix='/api/v1'); app.include_router(actions_router,prefix='/api/v1'); app.include_router(approvals_router,prefix='/api/v1'); app.include_router(events_router,prefix='/api/v1'); app.include_router(api_keys_router,prefix='/api/v1'); app.include_router(alerts_router,prefix='/api/v1')
@app.get('/health',tags=['system'])
def health(): return {'status':'ok','service':settings.app_name,'version':'0.3.0'}
