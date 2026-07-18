from .health import router as health
from .auth import router as auth
from .candidates import router as candidates
from .rules import router as rules
from .rankings import router as rankings
from .recruiter import router as recruiter

__all__ = ["health", "auth", "candidates", "rules", "rankings", "recruiter"]
