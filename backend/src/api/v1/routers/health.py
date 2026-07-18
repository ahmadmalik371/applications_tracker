from fastapi import APIRouter

from src.core.config import get_settings
from src.core.database import check_database_connection

router = APIRouter(prefix="/health", tags=["System"])
settings = get_settings()


@router.get("")
async def health_check():
    """Health check including PostgreSQL connectivity."""
    db_status = "ok"
    try:
        await check_database_connection()
    except Exception:
        db_status = "error"

    overall_status = "ok" if db_status == "ok" else "degraded"

    return {
        "success": overall_status == "ok",
        "status": overall_status,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "database": db_status,
    }
