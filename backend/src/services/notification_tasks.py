"""Celery tasks for notification dispatch with retries."""

import json
import logging
from src.core.celery_app import app

logger = logging.getLogger(__name__)


@app.task(bind=True, max_retries=5, default_retry_delay=30)
def send_notification_task(self, notification_id: str, channel: str, payload: str):
    """Send a notification via the specified channel. Retries on failure."""
    try:
        data = json.loads(payload)

        if channel == "email":
            _send_email(data)
        elif channel == "in_app":
            _send_in_app(data)
        elif channel == "webhook":
            _send_webhook(data)
        else:
            raise ValueError(f"Unknown channel: {channel}")

        logger.info(f"Notification {notification_id} sent via {channel}")
        return {"status": "success", "notification_id": notification_id}

    except Exception as exc:
        logger.error(f"Failed to send notification {notification_id}: {exc}")
        raise self.retry(exc=exc, countdown=30 * (2 ** self.request.retries))


def _send_email(data: dict):
    """Stub email sender — in production this would use SMTP or a service."""
    logger.info(f"Email sent to {data.get('to', 'unknown')}: {data.get('subject', '')}")


def _send_in_app(data: dict):
    """In-app notifications are stored in DB; this marks them as sent."""
    logger.info(f"In-app notification stored: {data.get('title', '')}")


def _send_webhook(data: dict):
    """Stub webhook sender."""
    logger.info(f"Webhook dispatched to {data.get('url', 'unknown')}")
