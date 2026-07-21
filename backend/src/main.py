from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.v1.routers import (
    health, auth, candidates, rules, rankings, recruiter, dashboard,
    workflow, interviews, notifications, templates_router, analytics, reports,
    websocket, admin, ai_assistant, recommendations, ml_management, audit,
    public_jobs,
)
from src.core.config import get_settings
from src.core.exceptions import setup_exception_handlers
from src.core.middleware import RateLimitMiddleware, RequestLoggingMiddleware
from src.core.logging import setup_logging
from src.core.security_audit import security_headers_middleware

logger = setup_logging()


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url=f"{settings.API_V1_STR}/docs",
        redoc_url=f"{settings.API_V1_STR}/redoc",
    )

    allowed_origins = settings.CORS_ORIGINS.split(",") if settings.CORS_ORIGINS else ["*"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[o.strip() for o in allowed_origins],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization", "X-Client-Info", "Apikey", "X-Request-ID"],
    )

    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(RateLimitMiddleware)
    app.middleware("http")(security_headers_middleware)

    if settings.PROMETHEUS_ENABLED:
        from src.core.metrics import PrometheusMiddleware
        app.add_middleware(PrometheusMiddleware)

    setup_exception_handlers(app)

    from src.core.sentry import init_sentry
    init_sentry()

    app.include_router(health, prefix=settings.API_V1_STR)
    app.include_router(auth, prefix=settings.API_V1_STR)
    app.include_router(candidates, prefix=settings.API_V1_STR)
    app.include_router(rules, prefix=settings.API_V1_STR)
    app.include_router(rankings, prefix=settings.API_V1_STR)
    app.include_router(recruiter, prefix=settings.API_V1_STR)
    app.include_router(dashboard, prefix=settings.API_V1_STR)
    app.include_router(workflow, prefix=settings.API_V1_STR)
    app.include_router(interviews, prefix=settings.API_V1_STR)
    app.include_router(notifications, prefix=settings.API_V1_STR)
    app.include_router(templates_router, prefix=settings.API_V1_STR)
    app.include_router(analytics, prefix=settings.API_V1_STR)
    app.include_router(reports, prefix=settings.API_V1_STR)
    app.include_router(websocket, prefix=settings.API_V1_STR)
    app.include_router(admin, prefix=settings.API_V1_STR)
    app.include_router(ai_assistant, prefix=settings.API_V1_STR)
    app.include_router(recommendations, prefix=settings.API_V1_STR)
    app.include_router(ml_management, prefix=settings.API_V1_STR)
    app.include_router(audit, prefix=settings.API_V1_STR)
    app.include_router(public_jobs, prefix=settings.API_V1_STR)

    if settings.PROMETHEUS_ENABLED:
        from src.core.metrics import get_metrics_router
        app.include_router(get_metrics_router())

    return app


app = create_app()
