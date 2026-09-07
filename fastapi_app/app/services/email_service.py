import logging
import smtplib
import secrets
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailService:

    @staticmethod
    def generate_code() -> str:
        return f"{secrets.randbelow(1_000_000):06d}"

    @staticmethod
    async def send_email(to_email: str, subject: str, html_content: str) -> bool:
        if not settings.email_enabled:
            logger.info("email disabled; would have sent %r to %s", subject, to_email)
            return False

        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = settings.EMAIL_FROM
        message["To"] = to_email
        message.attach(MIMEText(html_content, "html"))

        try:
            with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as server:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.sendmail(settings.EMAIL_FROM, to_email, message.as_string())
            return True
        except Exception as exc:
            logger.warning("email send failed: %s", exc)
            return False

    @staticmethod
    def verification_email_html(code: str, expire_minutes: int) -> str:
        return f"""<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>Confirm your email</title></head>
<body style="font-family:Inter,Arial,sans-serif;background:#0b1020;color:#e6e9f2;margin:0;padding:40px 16px;">
  <div style="max-width:560px;margin:0 auto;background:#141a2e;border:1px solid #1f2a44;border-radius:14px;padding:32px;">
    <h1 style="margin:0 0 16px;font-size:22px;color:#fafafa;">DevStudio Pro</h1>
    <p style="font-size:15px;line-height:1.55;color:#a4adc8;">Confirm your email address to activate your account.</p>
    <div style="margin:24px 0;text-align:center;">
      <span style="display:inline-block;font-family:JetBrains Mono,monospace;font-size:30px;letter-spacing:8px;color:#60a5fa;background:#0b1020;border:1px dashed #2b3a5e;padding:14px 22px;border-radius:10px;">{code}</span>
    </div>
    <p style="font-size:13px;color:#6b7390;">This code expires in {expire_minutes} minutes. If you did not request it, ignore this message.</p>
  </div>
</body>
</html>"""

    @staticmethod
    def reset_password_email_html(code: str, expire_minutes: int) -> str:
        return f"""<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>Reset password</title></head>
<body style="font-family:Inter,Arial,sans-serif;background:#0b1020;color:#e6e9f2;margin:0;padding:40px 16px;">
  <div style="max-width:560px;margin:0 auto;background:#141a2e;border:1px solid #1f2a44;border-radius:14px;padding:32px;">
    <h1 style="margin:0 0 16px;font-size:22px;color:#fafafa;">Password reset</h1>
    <p style="font-size:15px;line-height:1.55;color:#a4adc8;">Use the code below to choose a new password.</p>
    <div style="margin:24px 0;text-align:center;">
      <span style="display:inline-block;font-family:JetBrains Mono,monospace;font-size:30px;letter-spacing:8px;color:#f59e0b;background:#0b1020;border:1px dashed #2b3a5e;padding:14px 22px;border-radius:10px;">{code}</span>
    </div>
    <p style="font-size:13px;color:#6b7390;">This code expires in {expire_minutes} minutes. If you did not request it, ignore this message.</p>
  </div>
</body>
</html>"""
