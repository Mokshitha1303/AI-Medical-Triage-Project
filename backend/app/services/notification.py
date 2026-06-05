import logging
from app.config import settings
from app.models.session import Session

logger = logging.getLogger(__name__)


async def notify_doctors_if_flagged(session: Session) -> None:
    """Send email/SMS alert to doctors when a case is flagged for review."""
    if not session.flagged_for_review:
        return

    if settings.sendgrid_api_key:
        await _send_email(session)
    else:
        logger.info(
            "STUB notification: session %s flagged (%s) — set SENDGRID_API_KEY to send real emails",
            session.id,
            session.flag_reason,
        )


async def _send_email(session: Session) -> None:
    """SendGrid email notification — only called when API key is configured."""
    try:
        from sendgrid import SendGridAPIClient
        from sendgrid.helpers.mail import Mail

        message = Mail(
            from_email=settings.sendgrid_from_email,
            to_emails=settings.sendgrid_from_email,  # Replace with actual doctor emails in production
            subject=f"[Medical Triage] Flagged case — {session.urgency_level}",
            plain_text_content=(
                f"A triage session has been flagged for review.\n\n"
                f"Session ID: {session.id}\n"
                f"Urgency: {session.urgency_level}\n"
                f"Reason: {session.flag_reason}\n\n"
                f"Please review at your earliest convenience."
            ),
        )
        sg = SendGridAPIClient(settings.sendgrid_api_key)
        sg.send(message)
    except Exception:
        logger.exception("Failed to send email notification for session %s", session.id)
