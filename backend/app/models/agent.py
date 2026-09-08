from enum import Enum
from uuid import uuid4

from sqlalchemy import Boolean, Enum as SAEnum, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class AutonomyLevel(str, Enum):
    OBSERVE = "observe"
    ASSIST = "assist"
    EXECUTE = "execute"
    AUTONOMOUS = "autonomous"
    CRITICAL = "critical"


class Agent(Base):
    __tablename__ = "agents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    owner: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500))
    autonomy_level: Mapped[AutonomyLevel] = mapped_column(SAEnum(AutonomyLevel), default=AutonomyLevel.ASSIST, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
