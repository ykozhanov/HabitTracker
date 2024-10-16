from abc import ABC, abstractmethod
from typing import Optional

from sqlalchemy import select

from database import Session
from models import User, Habit
from exceptions import NotFoundError


# class UserControllerBase(ABC):
#
#     @abstractmethod
#     async def add(self):
#         pass
#
#     @abstractmethod
#     async def delete(self):
#         pass
#
#
# class HabitControllerBase(ABC):
#
#     @abstractmethod
#     async def get(self) -> list[Habit]:
#         pass
#
#     @abstractmethod
#     async def add(self, title: str, description: Optional[str] = None) -> Habit:
#         pass
#
#     @abstractmethod
#     async def delete(self):
#         pass


class UserController:

    def __init__(self, user: User):
        self.user = user

    async def add(self):
        async with Session() as session:
            pass

    async def delete(self):
        async with Session() as session:
            pass


class HabitController:

    def __init__(self, user: User):
        self.user = user

    async def get(self) -> list[Habit]:
        return self.user.habits

    async def add(self, title: str, description: Optional[str] = None) -> Habit:
        async with Session() as session:
            new_habit = Habit(title=title, description=description)
            session.add(new_habit)
            await session.commit()
            return new_habit

    async def delete(self, habit_id: int) -> None:
        async with Session() as session:
            habit_select = await session.execute(select(Habit).where(Habit.id == habit_id))
            habit: Habit = habit_select.scalar_one_or_none()
            if not habit is None:
                await session.delete(habit)
            else:
                raise NotFoundError("Привычка по id: {} не найдена.".format(habit_id))
