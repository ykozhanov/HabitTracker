from fastapi import APIRouter, Depends, Form, HTTPException, status
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
    OAuth2PasswordRequestForm,
)
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import User, get_session
from backend.database.controllers import UserController
from backend.exceptions import AuthenticationError, AuthorizationError, NotFoundError
from backend.schemas import SuccessLoginSchema

router = APIRouter()
http_bearer = HTTPBearer()


async def validate_auth_user(  # type: ignore
    user_data: OAuth2PasswordRequestForm = Depends(OAuth2PasswordRequestForm),
) -> User:
    async for session in get_session():
        user_controller = UserController(session=session)
        try:
            user: User = await user_controller.login(
                username=user_data.username, password=user_data.password
            )
        except (NotFoundError, AuthorizationError) as exc:
            raise HTTPException(detail=exc.detail, status_code=exc.status_code)
        except Exception as exc:
            raise HTTPException(detail=exc, status_code=400)
        else:
            return user


@router.post("/login/")
async def login_user(
    user: User = Depends(validate_auth_user),
    session: AsyncSession = Depends(get_session),
) -> SuccessLoginSchema:
    user_controller = UserController(session=session)
    access_token, refresh_token = await user_controller.update_refresh_token(
        user_id=user.id
    )
    return SuccessLoginSchema(
        access_token=access_token, refresh_token=user.refresh_token
    )


@router.get("/token/", response_model_exclude_none=True)
async def get_access_token(
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
    session: AsyncSession = Depends(get_session),
) -> SuccessLoginSchema:
    user_controller = UserController(session=session)
    try:
        access_token = await user_controller.get_access_token(
            refresh_token=credentials.credentials
        )
    except (NotFoundError, AuthenticationError) as exc:
        raise HTTPException(detail=exc.detail, status_code=exc.status_code)
    except Exception as exc:
        raise HTTPException(detail=exc, status_code=400)
    return SuccessLoginSchema(access_token=access_token)


@router.post("/register/", status_code=status.HTTP_201_CREATED)
async def create_user(
    username: str = Form(),
    password: str = Form(),
    email: str = Form(),
    session: AsyncSession = Depends(get_session),
) -> SuccessLoginSchema:
    user_controller = UserController(session=session)
    try:
        access_token, refresh_token = await user_controller.add(
            username=username, password=password, email=email
        )
    except (NotFoundError, AuthorizationError) as exc:
        raise HTTPException(detail=exc.detail, status_code=exc.status_code)
    except Exception as exc:
        raise HTTPException(detail=exc, status_code=400)
    return SuccessLoginSchema(
        access_token=access_token, refresh_token=refresh_token, status_code=201
    )
