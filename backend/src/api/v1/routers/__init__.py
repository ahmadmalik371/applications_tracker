from .admin import router as admin
from .ai_assistant import router as ai_assistant
from .analytics import router as analytics
from .audit import router as audit
from .auth import router as auth
from .candidates import router as candidates
from .dashboard import router as dashboard
from .health import router as health
from .interviews import router as interviews
from .ml_management import router as ml_management
from .notifications import router as notifications
from .notifications import templates_router
from .public_jobs import router as public_jobs
from .rankings import router as rankings
from .recommendations import router as recommendations
from .recruiter import router as recruiter
from .reports import router as reports
from .rules import router as rules
from .websocket import router as websocket
from .workflow import router as workflow

__all__ = [
    "health",
    "auth",
    "candidates",
    "rules",
    "rankings",
    "recruiter",
    "dashboard",
    "workflow",
    "interviews",
    "notifications",
    "templates_router",
    "analytics",
    "reports",
    "websocket",
    "admin",
    "ai_assistant",
    "recommendations",
    "ml_management",
    "audit",
    "public_jobs",
]
