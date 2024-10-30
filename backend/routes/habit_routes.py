from fastapi import APIRouter, Depends, Header, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_session
from ..controllers.habit_controller import HabitController
from ..models import User, Habit
from ..exceptions import NotFoundError, AuthorizationError
from ..schemas import HabitSchema, SuccessGetHabitsListSchema, SuccessGetHabitSchema, SuccessSchema, PatchHabitSchema
from ..utils import get_token, get_user

router = APIRouter()


@router.get("/")
async def get_list_habits(authorization: str = Header(...), session: AsyncSession = Depends(get_session)) -> SuccessGetHabitsListSchema:
    token = get_token(authorization=authorization)
    user: User = await get_user(token=token, session=session)
    habits_controller = HabitController(user=user, session=session)

    try:
        habits: list[Habit | None] = await habits_controller.get_list()
    except NotFoundError as exc:
        raise HTTPException(detail=exc.detail, status_code=exc.status_code)
    except Exception as exc:
        raise HTTPException(detail=exc, status_code=400)

    return SuccessGetHabitsListSchema(data=habits)


@router.get("/{habit_id:int}/")
async def get_habit_by_id(habit_id: int, authorization: str = Header(...), session: AsyncSession = Depends(get_session)) -> SuccessGetHabitSchema:
    token = get_token(authorization=authorization)
    user: User = await get_user(token=token, session=session)
    habits_controller = HabitController(user=user, session=session)

    try:
        habit: Habit = await habits_controller.get_habit_by_id(habit_id=habit_id)
    except NotFoundError as exc:
        raise HTTPException(detail=exc.detail, status_code=exc.status_code)
    except Exception as exc:
        raise HTTPException(detail=exc, status_code=400)

    return SuccessGetHabitSchema(data=habit)


@router.post("/")
async def add_habit(habit: HabitSchema, authorization: str = Header(...), session: AsyncSession = Depends(get_session)) -> JSONResponse:
    token = get_token(authorization=authorization)
    user: User = await get_user(token=token, session=session)
    habits_controller = HabitController(user=user, session=session)

    try:
        new_habit = await habits_controller.add(**habit.model_dump(include={"title", "description", "remind_time"}))
    except NotFoundError as exc:
        raise HTTPException(detail=exc.detail, status_code=exc.status_code)
    except Exception as exc:
        raise HTTPException(detail=exc, status_code=400)

    result = SuccessGetHabitSchema(data=new_habit, status_code=201)
    return JSONResponse(content=result, status_code=result.status_code)


@router.delete("/{habit_id:int}/")
async def delete_habit(habit_id: int, authorization: str = Header(...), session: AsyncSession = Depends(get_session)) -> SuccessSchema:
    token = get_token(authorization=authorization)
    user: User = await get_user(token=token, session=session)
    habits_controller = HabitController(user=user, session=session)

    try:
        await habits_controller.delete(habit_id=habit_id)
    except (NotFoundError, AuthorizationError) as exc:
        raise HTTPException(detail=exc.detail, status_code=exc.status_code)
    except Exception as exc:
        raise HTTPException(detail=exc, status_code=400)

    return SuccessSchema()


@router.put("/{habit_id:int}/")
async def put_habit(habit: HabitSchema, authorization: str = Header(...), session: AsyncSession = Depends(get_session)) -> SuccessGetHabitSchema:
    token = get_token(authorization=authorization)
    user: User = await get_user(token=token, session=session)
    habits_controller = HabitController(user=user, session=session)

    try:
        update_habit = await habits_controller.update_habit_by_id(**habit.model_dump(include={"title", "description"}))
    except (NotFoundError, AuthorizationError) as exc:
        raise HTTPException(detail=exc.detail, status_code=exc.status_code)
    except Exception as exc:
        raise HTTPException(detail=exc, status_code=400)

    return SuccessGetHabitSchema(data=update_habit)


@router.patch("/{habit_id:int}/")
async def patch_habit(habit: PatchHabitSchema, authorization: str = Header(...), session: AsyncSession = Depends(get_session)) -> SuccessGetHabitSchema:
    token = get_token(authorization=authorization)
    user: User = await get_user(token=token, session=session)
    habits_controller = HabitController(user=user, session=session)

    try:
        update_habit = await habits_controller.update_habit_by_id(**habit.model_dump(include={"title", "description"}))
    except (NotFoundError, AuthorizationError) as exc:
        raise HTTPException(detail=exc.detail, status_code=exc.status_code)
    except Exception as exc:
        raise HTTPException(detail=exc, status_code=400)

    return SuccessGetHabitSchema(data=update_habit)


@router.patch("/{habit_id:int}/complete/")
async def mark_habit_complete(habit_id: int, authorization: str = Header(...), session: AsyncSession = Depends(get_session)) -> SuccessSchema:
    token = get_token(authorization=authorization)
    user: User = await get_user(token=token, session=session)
    habits_controller = HabitController(user=user, session=session)

    try:
        await habits_controller.mark_complete_habit_by_id(habit_id=habit_id)
    except (NotFoundError, AuthorizationError) as exc:
        raise HTTPException(detail=exc.detail, status_code=exc.status_code)
    except Exception as exc:
        raise HTTPException(detail=exc, status_code=400)

    return SuccessSchema()