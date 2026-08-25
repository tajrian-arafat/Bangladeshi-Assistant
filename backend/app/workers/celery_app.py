"""Celery application and background tasks."""

from celery import Celery

from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "bda",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.workers.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Dhaka",
    enable_utc=True,
    beat_schedule={
        "check-broken-links-hourly": {
            "task": "app.workers.tasks.check_broken_links",
            "schedule": 3600.0,
        },
        "purge-temp-documents": {
            "task": "app.workers.tasks.purge_temp_documents",
            "schedule": 3600.0,
        },
    },
)
