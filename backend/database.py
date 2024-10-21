from os import getenv
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from config import get_database_url

POSTGRES_USER=getenv("POSTGRES_USER", "admin")
POSTGRES_PASSWORD=getenv("POSTGRES_PASSWORD", "admin")
POSTGRES_DB=getenv("POSTGRES_DB", "habit_tracker")

DATABASE_URL = get_database_url()

engine = create_async_engine(DATABASE_URL)

Session = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with Session() as s:
        yield s
