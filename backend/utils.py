from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from models import User
from controllers import UserController
from exceptions import NotFoundError, AuthenticationError


async def get_user(token: str, session: AsyncSession) -> User:
    try:
        user: User = await UserController(session=session).get(token=token)
    except (NotFoundError, AuthenticationError) as exc:
        raise HTTPException(detail=exc.detail, status_code=exc.status_code)
    except Exception as exc:
        raise HTTPException(detail=exc, status_code=400)
    return user


def get_token(authorization: str) -> str:
    if not authorization.startswith("Bearer"):
        raise HTTPException(detail="Неверный тип токена.", status_code=400)

    token = authorization.split(" ")[1]

    if not token:
        raise HTTPException(detail="Токен отсутствует.", status_code=400)

    return token
