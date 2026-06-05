import traceback
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.triage import TriageRequest, TriageResponse
from app.services.triage_ai import run_full_triage
from app.services.case_manager import create_session
from app.services.audit_logger import log_action
from app.services.notification import notify_doctors_if_flagged
from app.api.deps import get_current_patient
from app.database import get_db
from app.models.patient import Patient

router = APIRouter(prefix="/api/triage", tags=["triage"])


@router.post("/", response_model=TriageResponse)
async def submit_symptoms(
    request: TriageRequest,
    current_patient: Patient = Depends(get_current_patient),
    db: AsyncSession = Depends(get_db),
):
    patient_context = {
        "known_conditions": current_patient.known_conditions or [],
        "medications": current_patient.medications or [],
    }

    try:
        result = await run_full_triage(
            symptoms_raw=request.symptoms,
            patient_id=str(current_patient.id),
            patient_context=patient_context,
        )

        session = await create_session(db, current_patient.id, request.symptoms, result)

        await log_action(
            db,
            actor_id=current_patient.id,
            actor_role="patient",
            action="triage_submitted",
            entity_type="session",
            entity_id=session.id,
            payload={"urgency_level": result.get("urgency_level"), "flagged": result.get("flagged_for_review")},
        )

        if result.get("flagged_for_review"):
            await notify_doctors_if_flagged(session)

        return TriageResponse(session_id=session.id, **result)

    except Exception as exc:
        raise HTTPException(status_code=500, detail=traceback.format_exc()) from exc
