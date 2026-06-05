import uuid
from datetime import datetime
from sqlalchemy import String, TIMESTAMP, func, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Doctor(Base):
    __tablename__ = "doctors"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    name: Mapped[str | None] = mapped_column(String(255))
    specialty: Mapped[str | None] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
