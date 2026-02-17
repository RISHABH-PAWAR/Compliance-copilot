"""Alert Sender Worker"""
from app.workers.celery_app import celery_app
from app.core.logging import get_logger

logger = get_logger("alert_sender")


@celery_app.task(name="send_alert_email")
def send_alert_email(alert_id: int, email: str, subject: str, body: str):
    """Send alert notification via email"""
    try:
        from app.utils.email import send_email
        send_email(to=email, subject=subject, body=body)
        logger.info("alert_email_sent", alert_id=alert_id, email=email)
        return {"status": "sent", "alert_id": alert_id}
    except Exception as e:
        logger.error("alert_email_failed", error=str(e))
        return {"status": "failed", "error": str(e)}


@celery_app.task(name="send_slack_notification")
def send_slack_notification(webhook_url: str, message: dict):
    """Send alert via Slack webhook"""
    try:
        import httpx
        response = httpx.post(webhook_url, json=message)
        logger.info("slack_notification_sent", status=response.status_code)
        return {"status": "sent"}
    except Exception as e:
        logger.error("slack_notification_failed", error=str(e))
        return {"status": "failed", "error": str(e)}
