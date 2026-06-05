import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import AuditLog


async def log_action(
    db: AsyncSession,
    actor_id: uuid.UUID,
    actor_role: str,
    action: str,
    entity_type: str | None = None,
    entity_id: uuid.UUID | None = None,
    payload: dict | None = None,
    ip_address: str | None = None,
) -> None:
    """Append-only audit log — never call UPDATE or DELETE on audit_log."""
    entry = AuditLog(
        actor_id=actor_id,
        actor_role=actor_role,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        payload=payload,
        ip_address=ip_address,
    )
    db.add(entry)
    await db.commit()
