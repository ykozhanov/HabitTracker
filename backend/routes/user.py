from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_session
from ..controllers import UserController
from ..schemas import LoginSchema, SuccessLoginSchema, CreateUserSchema
from ..models import User
from ..exceptions import AuthorizationError, NotFoundError

router = APIRouter()


@router.post("/login/")
async def login_user(user_data: LoginSchema, session: AsyncSession = Depends(get_session)) -> SuccessLoginSchema:
    user_controller = UserController(session=session)
    try:
        user: User = await user_controller.login(**user_data.model_dump())
    except (NotFoundError, AuthorizationError) as exc:
        raise HTTPException(detail=exc.detail, status_code=exc.status_code)
    except Exception as exc:
        raise HTTPException(detail=exc, status_code=400)

    user_session = await user_controller.new_session(user=user)
    session_id = user_session.session_id
    access_token = user_controller.get_access_token(session_id=session_id)

    return SuccessLoginSchema(session_id=session_id, access_token=access_token)


@router.get("/get_access_token/")
async def get_access_token(x_session_id: str = Header(...), session: AsyncSession = Depends(get_session)) -> SuccessLoginSchema:
    user_controller = UserController(session=session)
    try:
        access_token = user_controller.get_access_token(session_id=x_session_id)
    except NotFoundError as exc:
        raise HTTPException(detail=exc.detail, status_code=exc.status_code)
    except Exception as exc:
        raise HTTPException(detail=exc, status_code=400)
    return SuccessLoginSchema(session_id=x_session_id, access_token=access_token)


@router.post("/create/")
async def create_user(user_data: CreateUserSchema, session: AsyncSession = Depends(get_session)) -> SuccessLoginSchema:
    user_controller = UserController(session=session)
    try:
        session_id, access_token = await user_controller.add(**user_data.model_dump())
    except (NotFoundError, AuthorizationError) as exc:
        raise HTTPException(detail=exc.detail, status_code=exc.status_code)
    except Exception as exc:
        raise HTTPException(detail=exc, status_code=400)
    return SuccessLoginSchema(session_id=session_id, access_token=access_token)
