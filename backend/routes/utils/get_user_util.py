from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_session
from backend.database.models import User
from backend.database.controllers import UserController
from backend.exceptions import NotFoundError, AuthenticationError
#
#
# async def get_user(token: str, session: AsyncSession) -> User:
#     try:
#         user: User = await UserController(session=session).get(token=token)
#     except (NotFoundError, AuthenticationError) as exc:
#         raise HTTPException(detail=exc.detail, status_code=exc.status_code)
#     except Exception as exc:
#         raise HTTPException(detail=exc, status_code=400)
#     return user

# http_bearer = HTTPBearer()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/login/")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    async for session in get_session():
        try:
            user: User = await UserController(session=session).get(token=token)
        except (NotFoundError, AuthenticationError) as exc:
            raise HTTPException(detail=exc.detail, status_code=exc.status_code)
        except Exception as exc:
            raise HTTPException(detail=exc, status_code=400)
        return user
