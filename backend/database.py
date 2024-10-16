from os import getenv
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

POSTGRES_USER=getenv("POSTGRES_USER", "admin")
POSTGRES_PASSWORD=getenv("POSTGRES_PASSWORD", "admin")
POSTGRES_DB=getenv("POSTGRES_DB", "habit_tracker")

DATABASE_URL = getenv(
    "DATABASE_URL_DEFAULT",
    "postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@db:5432/{POSTGRES_DB}",
).format(
    POSTGRES_USER=POSTGRES_USER,
    POSTGRES_PASSWORD=POSTGRES_PASSWORD,
    POSTGRES_DB=POSTGRES_DB,
)

engine = create_async_engine(DATABASE_URL)

Session = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with Session() as s:
        yield s
