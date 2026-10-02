"""
Email service — Send invitation emails via the Resend SDK.

If RESEND_API_KEY is not configured, emails are silently skipped
(invitation is still persisted in the DB). This allows development
without an email provider.
"""
import logging
from typing import Optional

import resend

from app.core.config import get_settings

logger = logging.getLogger(__name__)


def is_email_configured() -> bool:
    """Check whether email sending is enabled."""
    settings = get_settings()
    return bool(settings.RESEND_API_KEY)


def send_invitation_email(
    to_email: str,
    event_name: str,
    inviter_email: str,
    invitation_id: int,
) -> bool:
    """
    Send a styled invitation email via Resend.

    Returns True if the email was sent successfully, False otherwise
    (including when email is not configured).
    """
    settings = get_settings()

    if not settings.RESEND_API_KEY:
        logger.info(
            "Email not configured (RESEND_API_KEY is empty). "
            "Skipping invitation email to %s for event '%s'.",
            to_email, event_name,
        )
        return False

    resend.api_key = settings.RESEND_API_KEY

    accept_url = f"{settings.FRONTEND_URL}/?accept_invite={invitation_id}"

    html_body = _build_invite_html(event_name, inviter_email, accept_url)

    try:
        result = resend.Emails.send({
            "from": settings.RESEND_FROM_EMAIL,
            "to": [to_email],
            "subject": f"You're invited to {event_name} — EventLens AI",
            "html": html_body,
        })
        logger.info(
            "Invitation email sent to %s for event '%s' (resend id: %s).",
            to_email, event_name, result.get("id", "unknown"),
        )
        return True
    except Exception as exc:
        logger.error(
            "Failed to send invitation email to %s: %s",
            to_email, exc,
        )
        return False


def _build_invite_html(
    event_name: str,
    inviter_email: str,
    accept_url: str,
) -> str:
    """Build the HTML body for the invitation email — EventLens dark branding."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
<body style="margin:0;padding:0;background:#0F172A;font-family:'Segoe UI',Roboto,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#0F172A;padding:40px 0;">
<tr><td align="center">
<table width="560" cellpadding="0" cellspacing="0" style="background:#1E293B;border-radius:16px;overflow:hidden;border:1px solid rgba(148,163,184,0.15);">

<!-- Header -->
<tr><td style="padding:32px 40px 0 40px;text-align:center;">
    <div style="font-size:28px;font-weight:700;color:#F8FAFC;letter-spacing:-0.5px;">
        📸 EventLens AI
    </div>
</td></tr>

<!-- Body -->
<tr><td style="padding:24px 40px;">
    <div style="font-size:20px;font-weight:600;color:#F8FAFC;margin-bottom:16px;">
        You've been invited!
    </div>
    <div style="color:#94A3B8;font-size:15px;line-height:1.6;margin-bottom:24px;">
        <strong style="color:#C4B5FD;">{inviter_email}</strong> has invited you
        to join the event <strong style="color:#F8FAFC;">"{event_name}"</strong>
        on EventLens AI as a photographer.
    </div>
    <div style="color:#94A3B8;font-size:14px;line-height:1.6;margin-bottom:28px;">
        Once you accept, you'll be able to upload photos to this event.
        The AI pipeline will automatically detect faces, create embeddings,
        and cluster people so guests can find their photos instantly.
    </div>

    <!-- CTA Button -->
    <div style="text-align:center;margin-bottom:24px;">
        <a href="{accept_url}"
           style="display:inline-block;padding:14px 36px;background:linear-gradient(135deg,#7C3AED,#8B5CF6);
                  color:#FFFFFF;text-decoration:none;border-radius:10px;font-weight:600;font-size:15px;
                  letter-spacing:0.3px;">
            Accept Invitation →
        </a>
    </div>

    <div style="color:#64748B;font-size:12px;line-height:1.5;">
        If the button doesn't work, copy and paste this link into your browser:<br>
        <a href="{accept_url}" style="color:#7C3AED;word-break:break-all;">{accept_url}</a>
    </div>
</td></tr>

<!-- Footer -->
<tr><td style="padding:20px 40px;border-top:1px solid rgba(148,163,184,0.12);text-align:center;">
    <div style="color:#475569;font-size:12px;">
        EventLens AI — AI-powered event photography platform
    </div>
</td></tr>

</table>
</td></tr>
</table>
</body>
</html>"""
