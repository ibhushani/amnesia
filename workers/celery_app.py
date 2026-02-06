"""
Celery App Configuration
"""
import os
from celery import Celery
from utils import get_logger

log = get_logger(__name__)

# CHANGE THIS LINE: Use 'localhost' instead of 'redis' for Windows execution
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "amnesia_worker",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["workers.tasks"]  # Explicitly register tasks
)

# Configuration for robustness
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_acks_late=True,
)

log.info(f"Celery Worker initialized with Broker: {REDIS_URL}")