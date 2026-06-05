import uuid
from datetime import date, datetime
from sqlalchemy import String, Date, ARRAY, TIMESTAMP, func, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Patient(Base):
    __tablename__ = "patients"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    name: Mapped[str | None] = mapped_column(String(255))
    dob: Mapped[date | None] = mapped_column(Date)
    gender: Mapped[str | None] = mapped_column(String(20))
    known_conditions: Mapped[list[str] | None] = mapped_column(ARRAY(Text))
    medications: Mapped[list[str] | None] = mapped_column(ARRAY(Text))
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
