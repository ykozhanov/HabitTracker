from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_session
from backend.database.controllers import HabitController
from backend.database.models import Habit, User
from backend.exceptions import AuthenticationError, AuthorizationError, NotFoundError
from backend.schemas import (
    HabitSchema,
    PatchHabitSchema,
    SuccessGetHabitSchema,
    SuccessGetHabitsListSchema,
    SuccessSchema,
)

from .utils import get_current_user

router = APIRouter()


@router.get("/")
async def get_list_habits(
    user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)
) -> SuccessGetHabitsListSchema:
    habits_controller = HabitController(user=user, session=session)
    try:
        habits: list[Habit] = await habits_controller.get_done_list()
    except (NotFoundError, AuthenticationError, AuthorizationError) as exc:
        raise HTTPException(detail=exc.detail, status_code=exc.status_code)
    except Exception as exc:
        raise HTTPException(detail=exc, status_code=400)
    return SuccessGetHabitsListSchema.model_validate({"data": habits})


@router.get("/{habit_id:int}/")
async def get_habit_by_id(
    habit_id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> SuccessGetHabitSchema:
    habits_controller = HabitController(user=user, session=session)

    try:
        habit: Habit = await habits_controller.get_habit_by_id(habit_id=habit_id)
    except (NotFoundError, AuthenticationError, AuthorizationError) as exc:
        raise HTTPException(detail=exc.detail, status_code=exc.status_code)
    except Exception as exc:
        raise HTTPException(detail=exc, status_code=400)

    return SuccessGetHabitSchema.model_validate({"data": habit})


@router.post("/", status_code=status.HTTP_201_CREATED)
async def add_habit(
    habit: HabitSchema,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> SuccessGetHabitSchema:
    habits_controller = HabitController(user=user, session=session)

    try:
        new_habit_create: Habit = await habits_controller.add(
            **habit.model_dump(include={"title", "description", "remind_time"})
        )
    except (NotFoundError, AuthenticationError, AuthorizationError) as exc:
        raise HTTPException(detail=exc.detail, status_code=exc.status_code)
    except Exception as exc:
        raise HTTPException(detail=exc, status_code=400)

    new_habit = HabitSchema.model_validate(new_habit_create).model_dump()
    return SuccessGetHabitSchema.model_validate({"data": new_habit, "status_code": 201})


@router.delete("/{habit_id:int}/")
async def delete_habit(
    habit_id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> SuccessSchema:
    habits_controller = HabitController(user=user, session=session)

    try:
        await habits_controller.delete(habit_id=habit_id)
    except (NotFoundError, AuthenticationError, AuthorizationError) as exc:
        raise HTTPException(detail=exc.detail, status_code=exc.status_code)
    except Exception as exc:
        raise HTTPException(detail=exc, status_code=400)

    return SuccessSchema()


@router.put("/{habit_id:int}/")
async def put_habit(
    habit_id: int,
    habit: HabitSchema,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> SuccessGetHabitSchema:
    habits_controller = HabitController(user=user, session=session)

    try:
        update_habit = await habits_controller.update_habit_by_id(
            habit_id=habit_id,
            **habit.model_dump(include={"title", "description", "remind_time"})
        )
    except (NotFoundError, AuthenticationError, AuthorizationError) as exc:
        raise HTTPException(detail=exc.detail, status_code=exc.status_code)
    except Exception as exc:
        raise HTTPException(detail=exc, status_code=400)

    return SuccessGetHabitSchema.model_validate({"data": update_habit})


@router.patch("/{habit_id:int}/")
async def patch_habit(
    habit_id: int,
    habit: PatchHabitSchema,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> SuccessGetHabitSchema:
    habits_controller = HabitController(user=user, session=session)

    try:
        update_habit = await habits_controller.update_habit_by_id(
            habit_id=habit_id,
            **habit.model_dump(include={"title", "description", "remind_time"})
        )
    except (NotFoundError, AuthenticationError, AuthorizationError) as exc:
        raise HTTPException(detail=exc.detail, status_code=exc.status_code)
    except Exception as exc:
        raise HTTPException(detail=exc, status_code=400)

    return SuccessGetHabitSchema.model_validate({"data": update_habit})


@router.patch("/{habit_id:int}/complete/")
async def mark_habit_complete(
    habit_id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> SuccessSchema:
    habits_controller = HabitController(user=user, session=session)

    try:
        await habits_controller.mark_complete_habit_by_id(habit_id=habit_id)
    except (NotFoundError, AuthenticationError, AuthorizationError) as exc:
        raise HTTPException(detail=exc.detail, status_code=exc.status_code)
    except Exception as exc:
        raise HTTPException(detail=exc, status_code=400)

    return SuccessSchema()
