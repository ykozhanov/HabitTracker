from typing import Optional
from datetime import datetime, time

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models import User, HabitTrackerTelegram
from backend.exceptions import NotFoundError


class HabitTrackerTelegramController:

    def __init__(self, user: User, session: AsyncSession, habit_id: int):
        if habit_id not in [i_habit.id for i_habit in user.habits]:
            raise NotFoundError("Привычка не найдена или недостаточно прав.")
        self._user = user
        self._session = session
        self._habit_id = habit_id

    async def add(self, chat_id: int, user_id: int, remind_time: time, last_time_check: Optional[datetime] = None) -> HabitTrackerTelegram:
        new_habit_tracker = HabitTrackerTelegram(chat_id=chat_id, user_id=user_id, remind_time=remind_time, last_time_check=last_time_check, habit_id=self._habit_id)
        self._session.add(new_habit_tracker)
        await self._session.commit()
        await self._session.refresh(new_habit_tracker)
        return new_habit_tracker

    async def update_remind_time(self, remind_time: time) -> HabitTrackerTelegram:
        await self._session.execute(
            update(HabitTrackerTelegram).where(HabitTrackerTelegram.habit_id == self._habit_id).values(
                remind_time=remind_time))
        await self._session.commit()
        updated_habittracker_select = await self._session.execute(
            select(HabitTrackerTelegram).where(HabitTrackerTelegram.habit_id == self._habit_id))
        return updated_habittracker_select.scalar()

    async def update_last_time_check(self, last_time_check: datetime) -> HabitTrackerTelegram:
        await self._session.execute(
            update(HabitTrackerTelegram).where(HabitTrackerTelegram.habit_id == self._habit_id).values(
                last_time_check=last_time_check))
        await self._session.commit()
        updated_habittracker_select = await self._session.execute(
            select(HabitTrackerTelegram).where(HabitTrackerTelegram.habit_id == self._habit_id))
        return updated_habittracker_select.scalar()
