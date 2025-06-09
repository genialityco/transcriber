from celery import Celery

celery_app = Celery(
    "celery_app",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)
import celery_tasks  # <-- this makes sure the task is registered