import logging
import re
import sys

from pythonjsonlogger.json import JsonFormatter

from src.core.config import get_settings

settings = get_settings()

# Patterns of sensitive data to mask in log records
SENSITIVE_KEYS = {
    "password", "token", "secret", "api_key", "apikey",
    "authorization", "refresh_token", "access_token",
    "hashed_password", "stripe_customer_id", "stripe_subscription_id",
}
SENSITIVE_PATTERNS = [
    (re.compile(r"(Bearer\s+)[A-Za-z0-9\-._~+/]+=*", re.IGNORECASE), r"\1***MASKED***"),
    (re.compile(r"(sk_)[a-zA-Z0-9]+"), r"\1***MASKED***"),
    (re.compile(r"(pk_)[a-zA-Z0-9]+"), r"\1***MASKED***"),
    (re.compile(r"([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})"), "***EMAIL***"),
]


def mask_sensitive(value):
    """Recursively mask sensitive values in dicts, lists, and strings."""
    if isinstance(value, dict):
        return {
            k: "***MASKED***" if k.lower() in SENSITIVE_KEYS else mask_sensitive(v)
            for k, v in value.items()
        }
    if isinstance(value, list):
        return [mask_sensitive(item) for item in value]
    if isinstance(value, str):
        masked = value
        for pattern, replacement in SENSITIVE_PATTERNS:
            masked = pattern.sub(replacement, masked)
        return masked
    return value


class MaskedJsonFormatter(JsonFormatter):
    """JSON formatter that masks sensitive data before serializing."""

    def add_fields(self, log_record, record_dict, message_dict):
        super().add_fields(log_record, record_dict, message_dict)
        for key, value in list(log_record.items()):
            if key in ("msg", "message"):
                continue
            log_record[key] = mask_sensitive(value)


def setup_logging():
    logger = logging.getLogger()

    # Don't add handlers if they already exist
    if logger.hasHandlers():
        return

    log_handler = logging.StreamHandler(sys.stdout)
    formatter = MaskedJsonFormatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s",
        rename_fields={"levelname": "level", "asctime": "timestamp"},
    )
    log_handler.setFormatter(formatter)
    logger.addHandler(log_handler)
    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))

    # Silence noisy loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

    return logger
