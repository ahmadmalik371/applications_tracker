import pytest
from httpx import AsyncClient

from src.core.database import check_database_connection


@pytest.mark.asyncio
async def test_database_connection():
    assert await check_database_connection() is True


@pytest.mark.asyncio
async def test_pgvector_extension_enabled():
    from sqlalchemy import text

    from src.core.database import engine

    async with engine.connect() as connection:
        result = await connection.execute(
            text(
                "SELECT EXISTS("
                "SELECT 1 FROM pg_extension WHERE extname = 'vector'"
                ")"
            )
        )
        assert result.scalar() is True


@pytest.mark.asyncio
async def test_health_check_includes_database(client: AsyncClient):
    response = await client.get("/api/v1/health")
    data = response.json()
    assert response.status_code == 200
    assert data["database"] == "ok"
    assert data["status"] == "ok"
