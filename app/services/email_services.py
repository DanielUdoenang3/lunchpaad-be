import os
from datetime import date

import resend
from jinja2 import Environment, FileSystemLoader

from app.utils.settings import settings

# Resend SDK setup
resend.api_key = settings.RESEND_API_KEY

# Templates live at app/templates/
_template_dir = os.path.join(settings.BASE_DIR, "app", "templates")
_env = Environment(loader=FileSystemLoader(_template_dir))


# ── Core sender ───────────────────────────────────────────────────────────────

def send_email(to_email: str, subject: str, html_body: str) -> dict:
    """
    Send a transactional email via Resend.
    Returns a dict with 'status' and 'message' keys.
    """
    try:
        params: resend.Emails.SendParams = {
            "from": settings.RESEND_EMAIL,
            "to": [to_email],
            "subject": subject,
            "html": html_body,
        }
        response: resend.Email = resend.Emails.send(params)
        email_id = response.get("id") if isinstance(response, dict) else str(response)
        print(f"[email] Sent '{subject}' → {to_email} (id={email_id})")
        return {"status": "success", "message": f"Email sent to {to_email}.", "email_id": email_id}
    except Exception as exc:
        print(f"[email] Failed to send '{subject}' → {to_email}: {exc}")
        return {"status": "error", "message": str(exc)}


# ── Template renderers ────────────────────────────────────────────────────────

def _render(template_name: str, **context) -> str:
    template = _env.get_template(template_name)
    return template.render(year=date.today().year, **context)


# ── Public email dispatchers ──────────────────────────────────────────────────

def send_verification_email(to_email: str, name: str, token: str) -> dict:
    """Send the email-verification magic link."""
    link = f"{settings.VERIFY_LINK}?token={token}"
    html_body = _render("email-verification.html", name=name, email=to_email, link=link)
    return send_email(to_email, "Verify your Lunchpaad email address", html_body)


def send_password_reset_email(to_email: str, token: str) -> dict:
    """Send the password-reset magic link."""
    link = f"{settings.FORGOT_PWD_LINK}?token={token}"
    html_body = _render("forgot-password.html", email=to_email, link=link)
    return send_email(to_email, "Reset your Lunchpaad password", html_body)
