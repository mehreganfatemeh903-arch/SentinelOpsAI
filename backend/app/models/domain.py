from datetime import datetime
from enum import Enum
from uuid import uuid4
from sqlalchemy import Boolean, DateTime, Enum as SAEnum, Float, ForeignKey, Integer, JSON, String, Text, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.db.session import Base

class AutonomyLevel(str, Enum):
    OBSERVE='observe'; ASSIST='assist'; EXECUTE='execute'; AUTONOMOUS='autonomous'; CRITICAL='critical'
class Decision(str, Enum):
    ALLOW='allow'; APPROVAL='approval'; BLOCK='block'
class UserRole(str, Enum):
    ADMIN='admin'; OPERATOR='operator'; VIEWER='viewer'
class EventType(str, Enum):
    ACTION='action'; APPROVAL='approval'; SECURITY='security'; SYSTEM='system'

class User(Base):
    __tablename__='users'
    id: Mapped[str]=mapped_column(String(36), primary_key=True, default=lambda:str(uuid4()))
    email: Mapped[str]=mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str]=mapped_column(String(255), nullable=False)
    name: Mapped[str]=mapped_column(String(120), nullable=False)
    role: Mapped[UserRole]=mapped_column(SAEnum(UserRole), default=UserRole.VIEWER, nullable=False)
    active: Mapped[bool]=mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

class Agent(Base):
    __tablename__='agents'
    id: Mapped[str]=mapped_column(String(36), primary_key=True, default=lambda:str(uuid4()))
    name: Mapped[str]=mapped_column(String(120), nullable=False)
    owner: Mapped[str]=mapped_column(String(120), nullable=False)
    description: Mapped[str|None]=mapped_column(String(500))
    autonomy_level: Mapped[AutonomyLevel]=mapped_column(SAEnum(AutonomyLevel), default=AutonomyLevel.ASSIST, nullable=False)
    active: Mapped[bool]=mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

class AgentApiKey(Base):
    __tablename__='agent_api_keys'
    id: Mapped[str]=mapped_column(String(36), primary_key=True, default=lambda:str(uuid4()))
    agent_id: Mapped[str]=mapped_column(String(36), ForeignKey('agents.id'), index=True, nullable=False)
    key_hash: Mapped[str]=mapped_column(String(64), unique=True, nullable=False)
    name: Mapped[str]=mapped_column(String(120), default='default', nullable=False)
    active: Mapped[bool]=mapped_column(Boolean, default=True, nullable=False)
    last_used_at: Mapped[datetime|None]=mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

class Tool(Base):
    __tablename__='tools'
    id: Mapped[str]=mapped_column(String(36), primary_key=True, default=lambda:str(uuid4()))
    name: Mapped[str]=mapped_column(String(120), unique=True, nullable=False)
    description: Mapped[str|None]=mapped_column(String(500))
    sensitivity: Mapped[int]=mapped_column(Integer, default=0, nullable=False)
    active: Mapped[bool]=mapped_column(Boolean, default=True, nullable=False)
    adapter_name: Mapped[str] = mapped_column(
        String(80),
        default="simulated",
        nullable=False,
    )
    credential_ref: Mapped[str | None] = mapped_column(
        String(120),
        nullable=True,
    )
    endpoint: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

class AgentTool(Base):
    __tablename__='agent_tools'
    id: Mapped[str]=mapped_column(String(36), primary_key=True, default=lambda:str(uuid4()))
    agent_id: Mapped[str]=mapped_column(String(36), ForeignKey('agents.id', ondelete='CASCADE'), index=True, nullable=False)
    tool_id: Mapped[str]=mapped_column(String(36), ForeignKey('tools.id', ondelete='CASCADE'), index=True, nullable=False)
    enabled: Mapped[bool]=mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    __table_args__=(UniqueConstraint('agent_id','tool_id',name='uq_agent_tool'),)

class Policy(Base):
    __tablename__='policies'
    id: Mapped[str]=mapped_column(String(36), primary_key=True, default=lambda:str(uuid4()))
    name: Mapped[str]=mapped_column(String(160), nullable=False)
    action_pattern: Mapped[str]=mapped_column(String(120), default='*', nullable=False)
    min_risk: Mapped[int]=mapped_column(Integer, default=0, nullable=False)
    max_financial_amount: Mapped[float|None]=mapped_column(Float)
    require_approval: Mapped[bool]=mapped_column(Boolean, default=False, nullable=False)
    effect: Mapped[Decision]=mapped_column(SAEnum(Decision), default=Decision.ALLOW, nullable=False)
    enabled: Mapped[bool]=mapped_column(Boolean, default=True, nullable=False)
    version: Mapped[int]=mapped_column(Integer, default=1, nullable=False)

class RuntimeEvent(Base):
    __tablename__='runtime_events'
    id: Mapped[str]=mapped_column(String(36), primary_key=True, default=lambda:str(uuid4()))
    agent_id: Mapped[str]=mapped_column(String(36), index=True, nullable=False)
    event_type: Mapped[EventType]=mapped_column(SAEnum(EventType), default=EventType.ACTION, nullable=False)
    action: Mapped[str]=mapped_column(String(120), nullable=False)
    resource: Mapped[str]=mapped_column(String(500), nullable=False)
    decision: Mapped[Decision]=mapped_column(SAEnum(Decision), nullable=False)
    risk_score: Mapped[int]=mapped_column(Integer, nullable=False)
    reasons: Mapped[list]=mapped_column(JSON, default=list, nullable=False)
    metadata_json: Mapped[dict]=mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

class Approval(Base):
    __tablename__='approvals'
    id: Mapped[str]=mapped_column(String(36), primary_key=True, default=lambda:str(uuid4()))
    event_id: Mapped[str]=mapped_column(String(36), ForeignKey('runtime_events.id'), nullable=False)
    status: Mapped[str]=mapped_column(String(30), default='pending', nullable=False)
    reviewer_id: Mapped[str|None]=mapped_column(String(36), ForeignKey('users.id'))
    note: Mapped[str|None]=mapped_column(Text)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
