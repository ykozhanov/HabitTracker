from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from routes import user, habit
from database import engine
from models import Base


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(lifespan=lifespan)

app.include_router(user.router, prefix="/users")
app.include_router(habit.router, prefix="/habits")