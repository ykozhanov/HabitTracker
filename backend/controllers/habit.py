from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy.orm import subqueryload

from ..models import User, Habit
from ..exceptions import NotFoundError, AuthorizationError, HabitError
from ..config import COUNT_REPEAT_HABIT


class HabitController:

    def __init__(self, user: User, session: AsyncSession):
        self._user = user
        self._session = session

    async def get_list(self) -> list[Habit]:
        return [habit for habit in self._user.habits if not habit.done]

    async def get_habit_by_id(self, habit_id: int):
        habit_select = await self._session.execute(select(Habit).where(Habit.id == habit_id))
        habit: Habit | None = habit_select.scalar_one_or_none()
        if habit is None:
            raise NotFoundError("Привычка по id: {} не найдена.".format(habit_id))
        return habit

    async def add(self, title: str, description: str | None) -> Habit:
        new_habit = Habit(title=title, description=description, user_id=self._user.id)
        self._session.add(new_habit)
        await self._session.commit()
        return new_habit

    async def delete(self, habit_id: int) -> None:
        habit_select = await self._session.execute(select(Habit).where(Habit.id == habit_id))
        habit: Habit | None = habit_select.scalar_one_or_none()
        if habit is None:
            raise NotFoundError("Привычка по id: {habit_id} не найдена.".format(habit_id=habit_id))
        if habit.user_id != self._user.id:
            raise AuthorizationError("Вы не можете удалить чужую привычку.")
        await self._session.delete(habit)
        await self._session.commit()

    async def mark_habit_by_id(self, habit_id: int) -> Habit:
        habit_select = await self._session.execute(select(Habit).where(Habit.id == habit_id))
        habit: Habit | None = habit_select.scalar_one_or_none()
        if habit is None:
            raise NotFoundError("Привычка по id: {habit_id} не найдена.".format(habit_id=habit_id))
        if habit.user_id != self._user.id:
            raise AuthorizationError("Вы не можете удалить чужую привычку.")
        if habit.done:
            raise HabitError("Привычка уже выполнена.")
        if habit.count_repeat < COUNT_REPEAT_HABIT:
            habit.count_repeat += 1
        else:
            habit.done = True
        await self._session.commit()
        await self._session.refresh(habit)
        return habit

    async def update_habit_by_id(self, habit_id: int, title: str | None, description: str | None) -> Habit:
        habit_select = await self._session.execute(select(Habit).where(Habit.id == habit_id))
        habit: Habit | None = habit_select.scalar_one_or_none()

        if habit is None:
            raise NotFoundError("Привычка по id: {habit_id} не найдена.".format(habit_id=habit_id))
        if habit.user_id != self._user.id:
            raise AuthorizationError("Вы не можете изменить чужую привычку.")

        if title is not None:
            habit.title = title
        if description is not None:
            habit.description = description

        await self._session.commit()
        await self._session.refresh(habit)
        return habit
