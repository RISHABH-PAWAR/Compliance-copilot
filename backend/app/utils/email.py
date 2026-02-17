"""Email Utilities"""
from app.config import get_settings
from app.core.logging import get_logger

settings = get_settings()
logger = get_logger("email")


def send_email(to: str, subject: str, body: str, html: bool = False):
    """Send email via SMTP"""
    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart

        msg = MIMEMultipart()
        msg["From"] = f"{settings.EMAILS_FROM_NAME} <{settings.SMTP_USER}>"
        msg["To"] = to
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "html" if html else "plain"))

        if settings.SMTP_USER and settings.SMTP_PASSWORD:
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)
            logger.info("email_sent", to=to, subject=subject)
        else:
            logger.warning("email_skipped", reason="no_credentials")
    except Exception as e:
        logger.error("email_failed", error=str(e))
