import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from sqlalchemy import text

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
    async with SessionLocal() as s:
        yield s
    await engine.dispose()


@pytest.fixture
async def db(session: AsyncSession):
    """Alias for the `session` fixture, for tests that use the name `db`."""
    yield session


@pytest.fixture
async def test_org(db: AsyncSession):
    """Create a test organization for unit tests using the in-memory session."""
    from src.models import Organization, Role

    org = Organization(name="Test Org Inc.")
    db.add(org)
    await db.flush()

    role = Role(name="Company Admin", description="Default Company Admin role")
    db.add(role)
    await db.flush()

    return org


def _pg_available() -> bool:
    """Return True only if a real PostgreSQL database is configured and reachable."""
    from src.core.config import get_settings

    settings = get_settings()
    if settings.DATABASE_URL.startswith("sqlite"):
        return False
    import asyncio
    from src.core.database import check_database_connection

    try:
        asyncio.run(check_database_connection())
        return True
    except Exception:
        return False


def pytest_collection_modifyitems(config, items):
    """Skip tests that require a live PostgreSQL connection when none is available."""
    if _pg_available():
        return
    skip_marker = pytest.mark.skip(reason="No PostgreSQL database available")
    db_test_ids = {
        "test_database_connection",
        "test_pgvector_extension_enabled",
        "test_health_check_includes_database",
        "test_admin_requires_super_admin_role",
    }
    for item in items:
        if any(test_id in item.nodeid for test_id in db_test_ids):
            item.add_marker(skip_marker)
