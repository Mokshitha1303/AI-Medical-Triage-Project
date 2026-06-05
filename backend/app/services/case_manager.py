import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.session import Session
from app.models.review import Review


async def create_session(db: AsyncSession, patient_id: uuid.UUID, symptoms_raw: str, result: dict) -> Session:
    session = Session(
        patient_id=patient_id,
        symptoms_raw=symptoms_raw,
        symptoms_structured=result.get("symptoms_structured"),
        urgency_level=result.get("urgency_level"),
        conditions_suggested=result.get("conditions_suggested"),
        confidence_score=result.get("confidence_score"),
        ai_reasoning=result.get("reasoning"),
        recommended_actions=result.get("recommended_actions"),
        flagged_for_review=result.get("flagged_for_review", False),
        flag_reason=result.get("flag_reason"),
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session


async def get_flagged_sessions(db: AsyncSession, limit: int = 50) -> list[Session]:
    result = await db.execute(
        select(Session)
        .where(Session.flagged_for_review == True)
        .order_by(Session.created_at.desc())
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_session_by_id(db: AsyncSession, session_id: uuid.UUID) -> Session | None:
    result = await db.execute(select(Session).where(Session.id == session_id))
    return result.scalar_one_or_none()


async def create_review(db: AsyncSession, session_id: uuid.UUID, doctor_id: uuid.UUID, data: dict) -> Review:
    review = Review(session_id=session_id, doctor_id=doctor_id, **data)
    db.add(review)
    await db.commit()
    await db.refresh(review)
    return review
