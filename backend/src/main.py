from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.v1.routers import health, auth, candidates, rules, rankings
from src.core.config import get_settings
from src.core.exceptions import setup_exception_handlers
from src.core.logging import setup_logging

# Setup logging before anything else
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

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, restrict this
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Setup exception handlers
    setup_exception_handlers(app)

    # Include routers
    app.include_router(health.router, prefix=settings.API_V1_STR)
    app.include_router(auth.router, prefix=settings.API_V1_STR)
    app.include_router(candidates.router, prefix=settings.API_V1_STR)
    app.include_router(rules.router, prefix=settings.API_V1_STR)
    app.include_router(rankings.router, prefix=settings.API_V1_STR)

    return app


app = create_app()
