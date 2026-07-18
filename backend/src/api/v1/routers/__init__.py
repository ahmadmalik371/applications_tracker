from .health import router as health
from .auth import router as auth
from .candidates import router as candidates
from .rules import router as rules
from .rankings import router as rankings
from .recruiter import router as recruiter
from .dashboard import router as dashboard
from .workflow import router as workflow
from .interviews import router as interviews
from .notifications import router as notifications, templates_router
from .analytics import router as analytics
from .reports import router as reports
from .websocket import router as websocket

__all__ = ["health", "auth", "candidates", "rules", "rankings", "recruiter", "dashboard", "workflow", "interviews", "notifications", "templates_router", "analytics", "reports", "websocket"]
