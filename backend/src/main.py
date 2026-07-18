from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.v1.routers import (
    health, auth, candidates, rules, rankings, recruiter, dashboard,
    workflow, interviews, notifications, templates_router, analytics, reports,
    websocket,
)
from src.core.config import get_settings
from src.core.exceptions import setup_exception_handlers
from src.core.logging import setup_logging

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

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    setup_exception_handlers(app)

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

    return app


app = create_app()
