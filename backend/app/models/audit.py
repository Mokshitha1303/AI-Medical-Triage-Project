import uuid
from datetime import datetime
from sqlalchemy import String, BigInteger, TIMESTAMP, func, text
from sqlalchemy.dialects.postgresql import UUID, JSONB, INET
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class AuditLog(Base):
    __tablename__ = "audit_log"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    actor_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    actor_role: Mapped[str | None] = mapped_column(String(20))
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_type: Mapped[str | None] = mapped_column(String(50))
    entity_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    payload: Mapped[dict | None] = mapped_column(JSONB)
    ip_address: Mapped[str | None] = mapped_column(INET)
    ts: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
