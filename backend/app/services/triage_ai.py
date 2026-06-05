from app.services.safety_rules import check_emergency_escalation
from app.services.rag_pipeline import get_rag_pipeline
from app.utils.symptom_extractor import extract_structured_symptoms
from app.config import settings


async def run_full_triage(
    symptoms_raw: str,
    patient_id: str,
    patient_context: dict,
) -> dict:
    """
    4-step pipeline:
    1. Safety check  — keyword match, bypasses AI if emergency found
    2. Symptom extraction  — Claude converts free text → structured JSON
    3. RAG triage  — LangChain retrieves guidelines + Claude triages
    4. Auto-flag  — marks cases for doctor review based on urgency/confidence
    """
    # Step 1: safety check — runs with no LLM call
    emergency = check_emergency_escalation(symptoms_raw)
    if emergency:
        return {**emergency, "flagged_for_review": True, "flag_reason": "emergency_keyword"}

    # Step 2: structured extraction
    symptoms_structured = await extract_structured_symptoms(symptoms_raw)

    # Step 3: RAG triage
    triage_result = await get_rag_pipeline().run_triage(symptoms_structured, patient_context)

    # Step 4: auto-flag logic
    high_urgency = triage_result["urgency_level"] in ("er", "urgent_care")
    low_confidence = triage_result["confidence_score"] < settings.confidence_threshold

    flag_reason: str | None = None
    if high_urgency:
        flag_reason = "high_urgency"
    elif low_confidence:
        flag_reason = "low_confidence"

    return {
        **triage_result,
        "symptoms_structured": symptoms_structured,
        "flagged_for_review": high_urgency or low_confidence,
        "flag_reason": flag_reason,
        "bypassed_ai": False,
    }
