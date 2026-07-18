import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture(autouse=True)
async def reset_db_engine():
    """Dispose pooled connections between tests to avoid stale asyncpg loops."""
    from src.core.database import engine

    await engine.dispose()
    yield
    await engine.dispose()
