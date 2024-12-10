from fastapi import APIRouter, Depends, HTTPException, Header, status, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_session, User
from backend.database.controllers import UserController
from backend.schemas import LoginSchema, SuccessLoginSchema, CreateUserSchema, SuccessSchema, GetToken
from backend.exceptions import AuthorizationError, NotFoundError, AuthenticationError
from .utils import get_current_user

router = APIRouter()
http_bearer = HTTPBearer()
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/token/")


async def validate_auth_user(
        user_data: OAuth2PasswordRequestForm = Depends(OAuth2PasswordRequestForm)
) -> User:
    async for session in get_session():
        user_controller = UserController(session=session)
        try:
            user: User = await user_controller.login(username=user_data.username, password=user_data.password)
        except (NotFoundError, AuthorizationError) as exc:
            raise HTTPException(detail=exc.detail, status_code=exc.status_code)
        except Exception as exc:
            raise HTTPException(detail=exc, status_code=400)
        return user


# @router.post("/token/")
# async def login_user(user: User = Depends(validate_auth_user), session: AsyncSession = Depends(get_session)) -> SuccessLoginSchema:
#     user_controller = UserController(session=session)
#     user_session = await user_controller.new_session(user=user)
#     try:
#         access_token = await user_controller.get_access_token(session_id=user_session.session_id)
#         return SuccessLoginSchema.model_validate({"session_id": user_session.session_id, "access_token": access_token, "token_type": "Bearer"})
#     except AuthorizationError as exc:
#         raise HTTPException(detail=exc.detail, status_code=exc.status_code)

    # user_controller = UserController(session=session)
    # try:
    #     user: User = await user_controller.login(**user_data.model_dump())
    # except (NotFoundError, AuthorizationError) as exc:
    #     raise HTTPException(detail=exc.detail, status_code=exc.status_code)
    # except Exception as exc:
    #     raise HTTPException(detail=exc, status_code=400)
    #
    # user_session = await user_controller.new_session(user=user)
    # session_id = user_session.session_id
    # access_token = await user_controller.get_access_token(session_id=session_id)
    #
    # return SuccessLoginSchema.model_validate({"session_id": session_id, "access_token": access_token, "token_type": "Bearer"})


@router.post("/login/")
async def login_user(user: User = Depends(validate_auth_user), session: AsyncSession = Depends(get_session)) -> SuccessLoginSchema:
    user_controller = UserController(session=session)
    access_token, refresh_token = await user_controller.update_refresh_token(user_id=user.id)
    return SuccessLoginSchema(access_token=access_token, refresh_token=user.refresh_token)

# @router.post("/login/")
# async def login_user(user_data: LoginSchema, session: AsyncSession = Depends(get_session)) -> SuccessLoginSchema:
#     user_controller = UserController(session=session)
#     try:
#         user: User = await user_controller.login(**user_data.model_dump())
#     except (NotFoundError, AuthorizationError) as exc:
#         raise HTTPException(detail=exc.detail, status_code=exc.status_code)
#     except Exception as exc:
#         raise HTTPException(detail=exc, status_code=400)
#
#     user_session = await user_controller.new_session(user=user)
#     session_id = user_session.session_id
#     access_token = await user_controller.get_access_token(session_id=session_id)
#
#     return SuccessLoginSchema.model_validate({"session_id": session_id, "access_token": access_token, "token_type": "Bearer"})

# @router.post("/logout/")
# async def logout_user(user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)) -> SuccessSchema:
#     user_controller = UserController(session=session)
#     await user_controller.delete_user_sessions(user=user)
#     return SuccessSchema(result=True, status_code=200)


@router.get("/token/", response_model_exclude_none=True)
async def get_access_token(credentials: HTTPAuthorizationCredentials = Depends(http_bearer), session: AsyncSession = Depends(get_session)) -> SuccessLoginSchema:
    user_controller = UserController(session=session)
    try:
        access_token = await user_controller.get_access_token(refresh_token=credentials.credentials)
    except (NotFoundError, AuthenticationError) as exc:
        raise HTTPException(detail=exc.detail, status_code=exc.status_code)
    except Exception as exc:
        raise HTTPException(detail=exc, status_code=400)
    return SuccessLoginSchema(access_token=access_token)


# @router.post("/token/")
# async def get_access_token(x_session_id: str = Header(...), session: AsyncSession = Depends(get_session)) -> SuccessLoginSchema:
#     user_controller = UserController(session=session)
#     try:
#         access_token = await user_controller.get_access_token(session_id=x_session_id)
#     except NotFoundError as exc:
#         raise HTTPException(detail=exc.detail, status_code=exc.status_code)
#     except Exception as exc:
#         raise HTTPException(detail=exc, status_code=400)
#     return SuccessLoginSchema.model_validate({"session_id": x_session_id, "access_token": access_token})


@router.post("/register/", status_code=status.HTTP_201_CREATED)
async def create_user(username = Form(), password = Form(), email = Form(), session: AsyncSession = Depends(get_session)) -> SuccessLoginSchema:
    user_controller = UserController(session=session)
    try:
        access_token, refresh_token = await user_controller.add(username=username, password=password, email=email)
    except (NotFoundError, AuthorizationError) as exc:
        raise HTTPException(detail=exc.detail, status_code=exc.status_code)
    except Exception as exc:
        raise HTTPException(detail=exc, status_code=400)
    # result = SuccessLoginSchema.model_validate({"session_id": session_id, "access_token": access_token, "status_code": 201})
    return SuccessLoginSchema(access_token=access_token, refresh_token=refresh_token, status_code=201)
