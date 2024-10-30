from sqlalchemy import update, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models import User, HabitCeleryTelegram
from backend.exceptions import NotFoundError


class HabitCeleryTelegramController:

    def __init__(self, user: User, session: AsyncSession):
        self._user = user
        self._session = session

    # async def add_new_habit_celery(self, habit_id: int, celery_task_id: str) -> None:
    #     new_habit_celery = HabitCeleryTelegram(celery_task_id=celery_task_id, habit_id=habit_id)
    #     self._session.add(new_habit_celery)
    #     await self._session.commit()

    async def get_celery_task_id(self, habit_id: int) -> str:
        if habit_id not in [i_habit.id for i_habit in self._user.habits]:
            raise NotFoundError("Привычка не найдена или недостаточно прав.")
        habit_celery_telegram_select = await self._session.execute(select(HabitCeleryTelegram.celery_task_id).where(HabitCeleryTelegram.habit_id == habit_id))
        return habit_celery_telegram_select.scalar_one_or_none()

    async def update_celery_task_id(self, celery_task_id: str, habit_id: int) -> HabitCeleryTelegram:
        if habit_id not in [i_habit.id for i_habit in self._user.habits]:
            raise NotFoundError("Привычка не найдена или недостаточно прав.")
        await self._session.execute(update(HabitCeleryTelegram).where(HabitCeleryTelegram.habit_id == habit_id).values(celery_task_id=celery_task_id))
        await self._session.commit()
        updated_habit_celery_telegram_select = await self._session.execute(select(HabitCeleryTelegram).where(HabitCeleryTelegram.habit_id == habit_id))
        return updated_habit_celery_telegram_select.scalar()
