import os
os.environ["DATABASE_URL"] = "postgresql+asyncpg://ats_user:13851098@localhost:5433/ats_db"
os.environ["POSTGRES_USER"] = "ats_user"
os.environ["POSTGRES_PASSWORD"] = "13851098"
os.environ["POSTGRES_HOST"] = "localhost"
os.environ["POSTGRES_PORT"] = "5433"
os.environ["POSTGRES_DB"] = "ats_db"

import sys
sys.path.insert(0, r"c:\ATS\backend")

from src.core.database import engine
from src.models import Base
import asyncio

async def init():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Tables created successfully")

asyncio.run(init())