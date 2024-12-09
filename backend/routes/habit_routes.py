from fastapi import APIRouter, Depends, Header, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_session
from backend.database.controllers import HabitController, UserController
from backend.database.models import User, Habit
from backend.exceptions import NotFoundError, AuthorizationError, AuthenticationError
from backend.schemas import HabitSchema, SuccessGetHabitsListSchema, SuccessGetHabitSchema, SuccessSchema, PatchHabitSchema
from .utils import get_current_user

router = APIRouter()
# http_bearer = HTTPBearer()
#
#
# async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(http_bearer)) -> User:
#     async for session in get_session():
#         token = credentials.credentials
#         try:
#             user: User = await UserController(session=session).get(token=token)
#         except (NotFoundError, AuthenticationError) as exc:
#             raise HTTPException(detail=exc.detail, status_code=exc.status_code)
#         except Exception as exc:
#             raise HTTPException(detail=exc, status_code=400)
#         return user


@router.get("/")
async def get_list_habits(user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)) -> SuccessGetHabitsListSchema:
    habits_controller = HabitController(user=user, session=session)
    try:
        habits: list[Habit | None] = await habits_controller.get_done_list()
    except (NotFoundError, AuthenticationError, AuthorizationError) as exc:
        raise HTTPException(detail=exc.detail, status_code=exc.status_code)
    except Exception as exc:
        raise HTTPException(detail=exc, status_code=400)
    return SuccessGetHabitsListSchema.model_validate({"data": habits})


@router.get("/{habit_id:int}/")
async def get_habit_by_id(habit_id: int, user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)) -> SuccessGetHabitSchema:
    # token = get_token(x_token=x_token)
    # user: User = await get_user(token=token, session=session)
    habits_controller = HabitController(user=user, session=session)

    try:
        habit: Habit = await habits_controller.get_habit_by_id(habit_id=habit_id)
    except (NotFoundError, AuthenticationError, AuthorizationError) as exc:
        raise HTTPException(detail=exc.detail, status_code=exc.status_code)
    except Exception as exc:
        raise HTTPException(detail=exc, status_code=400)

    return SuccessGetHabitSchema.model_validate({"data": habit})


@router.post("/", status_code=status.HTTP_201_CREATED)
async def add_habit(habit: HabitSchema, user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)) -> SuccessGetHabitSchema:
    # token = get_token(x_token=x_token)
    # user: User = await get_user(token=token, session=session)
    habits_controller = HabitController(user=user, session=session)

    try:
        new_habit_create: Habit = await habits_controller.add(**habit.model_dump(include={"title", "description", "remind_time"}))
    except (NotFoundError, AuthenticationError, AuthorizationError) as exc:
        raise HTTPException(detail=exc.detail, status_code=exc.status_code)
    except Exception as exc:
        raise HTTPException(detail=exc, status_code=400)

    new_habit = HabitSchema.model_validate(new_habit_create).model_dump()
    # result = SuccessGetHabitSchema.model_validate({"data": new_habit, "status_code": 201})
    return SuccessGetHabitSchema.model_validate({"data": new_habit, "status_code": 201})


@router.delete("/{habit_id:int}/")
async def delete_habit(habit_id: int, user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)) -> SuccessSchema:
    # token = get_token(x_token=x_token)
    # user: User = await get_user(token=token, session=session)
    habits_controller = HabitController(user=user, session=session)

    try:
        await habits_controller.delete(habit_id=habit_id)
    except (NotFoundError, AuthenticationError, AuthorizationError) as exc:
        raise HTTPException(detail=exc.detail, status_code=exc.status_code)
    except Exception as exc:
        raise HTTPException(detail=exc, status_code=400)

    return SuccessSchema()


@router.put("/{habit_id:int}/")
async def put_habit(habit_id: int, habit: HabitSchema, user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)) -> SuccessGetHabitSchema:
    # token = get_token(x_token=x_token)
    # user: User = await get_user(token=token, session=session)
    habits_controller = HabitController(user=user, session=session)

    try:
        update_habit = await habits_controller.update_habit_by_id(habit_id=habit_id, **habit.model_dump(include={"title", "description", "remind_time"}))
    except (NotFoundError, AuthenticationError, AuthorizationError) as exc:
        raise HTTPException(detail=exc.detail, status_code=exc.status_code)
    except Exception as exc:
        raise HTTPException(detail=exc, status_code=400)

    return SuccessGetHabitSchema.model_validate({"data": update_habit})


@router.patch("/{habit_id:int}/")
async def patch_habit(habit_id: int, habit: PatchHabitSchema, user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)) -> SuccessGetHabitSchema:
    # token = get_token(x_token=x_token)
    # user: User = await get_user(token=token, session=session)
    habits_controller = HabitController(user=user, session=session)

    try:
        update_habit = await habits_controller.update_habit_by_id(habit_id=habit_id, **habit.model_dump(include={"title", "description", "remind_time"}))
    except (NotFoundError, AuthenticationError, AuthorizationError) as exc:
        raise HTTPException(detail=exc.detail, status_code=exc.status_code)
    except Exception as exc:
        raise HTTPException(detail=exc, status_code=400)

    return SuccessGetHabitSchema.model_validate({"data": update_habit})


@router.patch("/{habit_id:int}/complete/")
async def mark_habit_complete(habit_id: int, user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)) -> SuccessSchema:
    # token = get_token(x_token=x_token)
    # user: User = await get_user(token=token, session=session)
    habits_controller = HabitController(user=user, session=session)

    try:
        await habits_controller.mark_complete_habit_by_id(habit_id=habit_id)
    except (NotFoundError, AuthenticationError, AuthorizationError) as exc:
        raise HTTPException(detail=exc.detail, status_code=exc.status_code)
    except Exception as exc:
        raise HTTPException(detail=exc, status_code=400)

    return SuccessSchema()