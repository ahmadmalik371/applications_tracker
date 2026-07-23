from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.core.config import get_settings

settings = get_settings()

# Use SQLite for local dev when no PostgreSQL is configured,
# otherwise use the configured DATABASE_URL (PostgreSQL/Supabase).
_db_url = settings.DATABASE_URL
_is_sqlite = _db_url.startswith("sqlite")

if _is_sqlite:
    engine = create_async_engine(
        _db_url,
        echo=settings.ENVIRONMENT == "development",
        future=True,
    )
else:
    engine = create_async_engine(
        _db_url,
        echo=settings.ENVIRONMENT == "development",
        future=True,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
    )

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def check_database_connection() -> bool:
    """Verify the application can reach the database."""
    async with engine.connect() as connection:
        await connection.execute(text("SELECT 1"))
    return True


async def init_db():
    """Create all tables. Used for SQLite/local dev mode."""
    from src.models.base import Base
    import src.models  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
