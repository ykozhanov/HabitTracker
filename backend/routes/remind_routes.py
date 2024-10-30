from datetime import datetime

from fastapi import APIRouter, Depends, Header, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_session
from backend.schemas import HabitRemindTelegramSchema, SuccessSchema
from backend.utils import get_token, get_user
from backend.controllers import HabitTrackerTelegramController, HabitCeleryTelegramController, HabitController
from backend.models import User
from backend.exceptions import NotFoundError
from remind import CeleryTelegramBotController

router = APIRouter()


@router.post("/telegram/{habit_id:int}/")
async def add_habit_remind(habit_id: int, habit_remind: HabitRemindTelegramSchema, authorization: str = Header(...), session: AsyncSession = Depends(get_session)) -> JSONResponse:
    token = get_token(authorization=authorization)
    user: User = await get_user(token=token, session=session)
    habittracker_controller = HabitTrackerTelegramController(user=user, session=session, habit_id=habit_id)

    try:
        await habittracker_controller.add(**habit_remind.model_dump(include={"remind_time", "chat_id", "user_id"}))
    except NotFoundError as exc:
        raise HTTPException(detail=exc.detail, status_code=exc.status_code)
    except Exception as exc:
        raise HTTPException(detail=exc, status_code=400)

    result = SuccessSchema(status_code=201)
    return JSONResponse(content=result, status_code=result.status_code)


@router.put("/telegram/{habit_id:int}/")
async def update_habit_remind_time(habit_id: int, habit_remind: HabitRemindTelegramSchema, authorization: str = Header(...), session: AsyncSession = Depends(get_session)) -> SuccessSchema:
    token = get_token(authorization=authorization)
    user: User = await get_user(token=token, session=session)
    habittracker_controller = HabitTrackerTelegramController(user=user, session=session, habit_id=habit_id)
    habitcelery_telegram_controller = HabitCeleryTelegramController(user=user, session=session)

    try:
        await habittracker_controller.update_remind_time(**habit_remind.model_dump(include={"remind_time", "chat_id", "user_id"}))
    except NotFoundError as exc:
        raise HTTPException(detail=exc.detail, status_code=exc.status_code)
    except Exception as exc:
        raise HTTPException(detail=exc, status_code=400)

    celery_task_id = await habitcelery_telegram_controller.get_celery_task_id(habit_id=habit_id)
    CeleryTelegramBotController.revoke_task_by_id(celery_task_id=celery_task_id)
    new_remind_time = datetime.now().replace(hour=habit_remind.remind_time.hour, minute=habit_remind.remind_time.minute)

    if datetime.now() > new_remind_time:
        habit_controller = HabitController(user=user, session=session)
        habit = await habit_controller.get_habit_by_id(habit_id=habit_id)
        new_celery_task = CeleryTelegramBotController.send_reminder_telegram_bot.apply_async({"chat_id": habit_remind.chat_id, "habit": habit, "user_id": habit_remind.user_id},
                    eta=new_remind_time)
        await habitcelery_telegram_controller.update_celery_task_id(celery_task_id=new_celery_task.id, habit_id=habit_id)

    return SuccessSchema()
