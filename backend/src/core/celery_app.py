import logging
import sys
from celery import Celery
from celery.signals import after_setup_logger, after_setup_task_logger, worker_shutdown
from kombu import Queue
from pythonjsonlogger.json import JsonFormatter

from src.core.config import get_settings

settings = get_settings()

# Initialize Celery
celery_app = Celery(
    "ai_ats",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

# Celery Configurations
celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    broker_transport_options={"visibility_timeout": 3600},
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=100,
    task_default_retry_delay=30,
    task_time_limit=300,
    task_soft_time_limit=240,
    task_ignore_result=False,
    # Task routing by queue (Task 20)
    task_routes={
        "src.tasks.parse_resume_task": {"queue": "parsing"},
        "src.tasks.generate_candidate_embedding_task": {"queue": "embeddings"},
        "src.tasks.generate_job_embedding_task": {"queue": "embeddings"},
        "src.services.notification_tasks.*": {"queue": "notifications"},
    },
    task_default_queue="default",
    task_queues=(
        Queue("default", routing_key="default.#"),
        Queue("parsing", routing_key="parsing.#"),
        Queue("embeddings", routing_key="embeddings.#"),
        Queue("ranking", routing_key="ranking.#"),
        Queue("notifications", routing_key="notifications.#"),
        Queue("reports", routing_key="reports.#"),
        Queue("ai_tasks", routing_key="ai_tasks.#"),
    ),
    # Dead Letter Queue: failed tasks are sent here after max retries
    task_reject_on_worker_lost=True,
    # Beat configuration
    beat_schedule={
        "check-expired-sessions-every-hour": {
            "task": "src.core.celery_app.cleanup_expired_sessions",
            "schedule": 3600.0,
        }
    },
)

# Task Auto-discovery (discover tasks in core, models, api, services, etc.)
celery_app.autodiscover_tasks(["src.core", "src.services"])


# Celery Logging Configuration
def setup_celery_logging(*args, **kwargs):
    logger = logging.getLogger()
    
    # Check if handlers already configured
    if logger.handlers:
        for handler in list(logger.handlers):
            logger.removeHandler(handler)
            
    logHandler = logging.StreamHandler(sys.stdout)
    formatter = JsonFormatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s",
        rename_fields={"levelname": "level", "asctime": "timestamp"},
    )
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)
    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))


# Register logging signals
after_setup_logger.connect(setup_celery_logging)
after_setup_task_logger.connect(setup_celery_logging)


@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=5,
)
def debug_task(self):
    """A debug task to verify Celery workers are operating correctly."""
    logger = logging.getLogger(__name__)
    logger.info(f"Request: {self.request!r}")
    return "Celery is working!"


@celery_app.task(
    bind=True,
    max_retries=5,
    default_retry_delay=60,
    queue="default",
)
def cleanup_expired_sessions(self):
    """Dummy periodic task to clean up expired sessions."""
    logger = logging.getLogger(__name__)
    logger.info("Cleaning up expired sessions...")
    return "Expired sessions cleaned."


@celery_app.task(bind=True, queue="default")
def send_to_dlq(self, task_name: str, task_id: str, args: list, kwargs: dict, error: str):
    """Send a permanently failed task to the Dead Letter Queue for inspection."""
    logger = logging.getLogger("dlq")
    logger.error(
        "Task sent to DLQ: task_name=%s task_id=%s error=%s",
        task_name, task_id, error,
    )
    return {"status": "dlq", "task_name": task_name, "task_id": task_id}


# Graceful shutdown handling
@worker_shutdown.connect
def on_worker_shutdown(sender, **kwargs):
    logger = logging.getLogger(__name__)
    logger.info("Celery worker is shutting down gracefully.")
