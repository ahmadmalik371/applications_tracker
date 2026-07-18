import logging
import sys

from pythonjsonlogger.json import JsonFormatter

from src.core.config import get_settings

settings = get_settings()


def setup_logging():
    logger = logging.getLogger()

    # Don't add handlers if they already exist
    if logger.hasHandlers():
        return

    logHandler = logging.StreamHandler(sys.stdout)
    formatter = JsonFormatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s",
        rename_fields={"levelname": "level", "asctime": "timestamp"},
    )
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)
    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))

    # Silence noisy loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

    return logger
