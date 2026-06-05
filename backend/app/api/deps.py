import uuid
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.patient import Patient


# Stub patient — replaced with real JWT auth in Phase 3
async def get_current_patient(db: AsyncSession = Depends(get_db)) -> Patient:
    """
    Temporary stub that returns a hardcoded patient for Phase 1 testing.
    Real JWT-based auth is implemented in Phase 3 (app/api/routes/auth.py).
    """
    stub = Patient(
        id=uuid.UUID("00000000-0000-0000-0000-000000000001"),
        email="test@example.com",
        password_hash="stub",
        name="Test Patient",
        known_conditions=[],
        medications=[],
    )
    return stub
