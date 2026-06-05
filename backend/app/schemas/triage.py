import uuid
from pydantic import BaseModel, Field


class TriageRequest(BaseModel):
    symptoms: str = Field(..., min_length=10, max_length=5000)


class ConditionSuggested(BaseModel):
    name: str
    probability: str
    description: str


class TriageResponse(BaseModel):
    session_id: uuid.UUID
    urgency_level: str
    confidence_score: float
    conditions_suggested: list[ConditionSuggested]
    reasoning: str
    recommended_actions: list[str]
    follow_up_questions: list[str] = []
    disclaimer: str
    flagged_for_review: bool
    flag_reason: str | None = None
    bypassed_ai: bool = False
