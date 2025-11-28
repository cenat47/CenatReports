from celery import Celery
from src.config import settings

celery_app = Celery(
    "tasks",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        "src.tasks.tasks",
        "src.tasks.email_tasks",
    ],
)
celery_app.conf.beat_schedule = {
    "refresh_mv": {
        "task": "refresh_materialized_views",
        "schedule": 3600.0,  # every hour
    }
}
