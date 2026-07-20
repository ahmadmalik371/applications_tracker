"""Sentry integration for backend, Celery, and frontend error tracking.

Initializes Sentry SDK when SENTRY_DSN is configured. Sensitive data is
sanitized before sending to Sentry via before_send hooks.
"""
from __future__ import annotations

import logging
from typing import Any, Optional

from src.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

try:
    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastApiIntegration
    from sentry_sdk.integrations.celery import CeleryIntegration
    from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
    _HAS_SENTRY = True
except ImportError:
    _HAS_SENTRY = False


SENSITIVE_KEYS = {
    "password", "token", "secret", "api_key", "apikey",
    "authorization", "refresh_token", "access_token",
    "hashed_password", "stripe_customer_id", "stripe_subscription_id",
}


def _scrub_sensitive(data: Any) -> Any:
    """Recursively remove sensitive values from event data."""
    if isinstance(data, dict):
        return {
            k: "***REDACTED***" if k.lower() in SENSITIVE_KEYS else _scrub_sensitive(v)
            for k, v in data.items()
        }
    if isinstance(data, list):
        return [_scrub_sensitive(item) for item in data]
    return data


def _before_send(event: dict, hint: dict) -> Optional[dict]:
    """Sentry before_send hook to scrub sensitive data."""
    try:
        if "request" in event:
            event["request"] = _scrub_sensitive(event["request"])
        if "extra" in event:
            event["extra"] = _scrub_sensitive(event["extra"])
        if "breadcrumbs" in event:
            event["breadcrumbs"] = _scrub_sensitive(event["breadcrumbs"])
    except Exception:
        pass
    return event


def init_sentry() -> bool:
    """Initialize Sentry SDK if configured. Returns True if initialized."""
    if not _HAS_SENTRY:
        logger.info("sentry_sdk not installed; skipping Sentry initialization")
        return False

    if not settings.SENTRY_DSN:
        logger.info("SENTRY_DSN not set; Sentry disabled")
        return False

    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.ENVIRONMENT,
        traces_sample_rate=0.1,
        send_default_pii=False,
        before_send=_before_send,
        integrations=[
            FastApiIntegration(),
            CeleryIntegration(),
            SqlalchemyIntegration(),
        ],
    )
    logger.info("Sentry initialized for environment=%s", settings.ENVIRONMENT)
    return True
