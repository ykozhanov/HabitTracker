from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from backend.config import get_database_url

DATABASE_URL = get_database_url(host="db_backend")

engine = create_async_engine(DATABASE_URL)

Session = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with Session() as s:
        yield s
