from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.models import User
from backend.database.controllers import UserController
from backend.exceptions import NotFoundError, AuthenticationError


async def get_user(token: str, session: AsyncSession) -> User:
    try:
        user: User = await UserController(session=session).get(token=token)
    except (NotFoundError, AuthenticationError) as exc:
        raise HTTPException(detail=exc.detail, status_code=exc.status_code)
    except Exception as exc:
        raise HTTPException(detail=exc, status_code=400)
    return user
