"""Celery Application Configuration"""
from celery import Celery
from app.config import get_settings

settings = get_settings()

celery_app = Celery(
    "compliance_copilot",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Kolkata",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_routes={
        "app.workers.document_processor.*": {"queue": "documents"},
        "app.workers.compliance_analyzer.*": {"queue": "analysis"},
        "app.workers.alert_sender.*": {"queue": "alerts"},
        "app.workers.report_generator.*": {"queue": "reports"},
    },
)
