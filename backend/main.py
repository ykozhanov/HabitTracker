from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from . import routes
from .database import engine
from .schemas import ErrorSchema


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    yield
    await engine.dispose()


app = FastAPI(lifespan=lifespan)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    error_response = ErrorSchema(
        detail=str(exc.detail),
        status_code=exc.status_code,
    )
    return JSONResponse(
        status_code=exc.status_code, content=error_response.model_dump()
    )


app.include_router(routes.user_routes.router, prefix="/api/users", tags=["User"])
app.include_router(routes.habit_routes.router, prefix="/api/habits", tags=["Habit"])
