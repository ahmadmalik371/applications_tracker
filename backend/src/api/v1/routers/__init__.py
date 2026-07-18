from .health import router as health
from .auth import router as auth
from .candidates import router as candidates

__all__ = ["health", "auth", "candidates"]
