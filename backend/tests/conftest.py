import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession

from src.main import app
from src.models.base import Base


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


@pytest.fixture
async def session():
    """In-memory async SQLite session for unit tests that need persistence.

    Creates all tables on a fresh in-memory database for each test, so tests
    stay isolated and do not require a running PostgreSQL instance.
    """
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    SessionLocal = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
    )
    async with SessionLocal() as db:
        yield db
    await engine.dispose()
