from .health import router as health
from .auth import router as auth
from .candidates import router as candidates
from .rules import router as rules
from .rankings import router as rankings

__all__ = ["health", "auth", "candidates", "rules", "rankings"]
