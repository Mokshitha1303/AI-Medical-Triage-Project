import uuid
from datetime import datetime
from sqlalchemy import String, Text, Float, Boolean, ARRAY, TIMESTAMP, func, CheckConstraint, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base

URGENCY_LEVELS = ("er", "urgent_care", "gp", "self_care")


class Session(Base):
    __tablename__ = "sessions"
    __table_args__ = (
        CheckConstraint("urgency_level IN ('er','urgent_care','gp','self_care')", name="ck_sessions_urgency"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("patients.id", ondelete="CASCADE"))
    symptoms_raw: Mapped[str] = mapped_column(Text, nullable=False)
    symptoms_structured: Mapped[dict | None] = mapped_column(JSONB)
    urgency_level: Mapped[str | None] = mapped_column(String(20))
    conditions_suggested: Mapped[list | None] = mapped_column(JSONB)
    confidence_score: Mapped[float | None] = mapped_column(Float)
    ai_reasoning: Mapped[str | None] = mapped_column(Text)
    recommended_actions: Mapped[list[str] | None] = mapped_column(ARRAY(Text))
    flagged_for_review: Mapped[bool] = mapped_column(Boolean, default=False)
    flag_reason: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
