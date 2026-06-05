import uuid
from datetime import datetime
from pydantic import BaseModel


class CaseDetail(BaseModel):
    id: uuid.UUID
    patient_id: uuid.UUID
    symptoms_raw: str
    symptoms_structured: dict | None
    urgency_level: str | None
    conditions_suggested: list | None
    confidence_score: float | None
    ai_reasoning: str | None
    recommended_actions: list[str] | None
    flagged_for_review: bool
    flag_reason: str | None
    created_at: datetime


class ReviewRequest(BaseModel):
    agreed_with_ai: bool
    override_decision: str | None = None
    override_reason: str | None = None
    notes: str | None = None
