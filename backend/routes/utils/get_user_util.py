from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from backend.database import get_session
from backend.database.controllers import UserController
from backend.database.models import User
from backend.exceptions import AuthenticationError, NotFoundError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/login/")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:  # type: ignore
    async for session in get_session():
        try:
            user: User = await UserController(session=session).get(token=token)
        except (NotFoundError, AuthenticationError) as exc:
            raise HTTPException(detail=exc.detail, status_code=exc.status_code)
        except Exception as exc:
            raise HTTPException(detail=exc, status_code=400)
        else:
            return user
