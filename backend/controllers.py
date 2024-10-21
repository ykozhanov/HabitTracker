from abc import ABC, abstractmethod
from typing import Optional, Any
import datetime
import uuid

import bcrypt
import jwt
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy.orm import subqueryload

from models import User, Habit, Session
from exceptions import NotFoundError, AuthenticationError, AuthorizationError, HabitError
from config import JWT_SECRET_KEY, JWT_ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS, COUNT_REPEAT_HABIT


class UserController:

    def __init__(self, session: AsyncSession):
        self._session = session

    @staticmethod
    def _password_hash(password: str, salt: bytes) -> bytes:
        return bcrypt.hashpw(password.encode('utf-8'), salt)

    @staticmethod
    def _check_password(password_hash: bytes, password: str) -> bool:
        return bcrypt.checkpw(password.encode('utf-8'), password_hash)

    @staticmethod
    def _get_token(username: str, timedelta: datetime.timedelta):
        payload = {
            'username': username,
            'exp': datetime.datetime.now() + timedelta,
        }
        return jwt.encode(payload=payload, key=JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

    @staticmethod
    def _decode_token(token: str) -> dict[str, Any]:
        try:
            payload = jwt.decode(jwt=token, key=JWT_SECRET_KEY, algorithms=JWT_ALGORITHM)
        except jwt.ExpiredSignatureError:
            raise AuthenticationError("Токен устарел.")
        except jwt.InvalidTokenError:
            raise AuthenticationError("Неверный токен.")
        return payload

    async def login(self, username: str, password: str) -> User:
        user_select = await self._session.execute(select(User).where(User.username == username))
        user: User | None = user_select.scalar_one_or_none()
        if user is None:
            raise NotFoundError("Пользователь не найден.")
        check_password = self._check_password(password=password, password_hash=user.password_hash)
        if not check_password:
            raise AuthenticationError("Неверный логин или пароль.")
        return user

    async def get(self, token: str) -> User:
        username = self._decode_token(token=token)["username"]
        user_select = await self._session.execute(select(User).where(User.username == username))
        # user_select = await self._session.execute(select(User).options(subqueryload(User.habits)).where(User.username == username))
        user: User | None = user_select.scalar_one_or_none()
        if user is None:
            raise NotFoundError("Пользователь не найден.")
        return user

    async def add(self, username: str, password: str) -> (str, str):
        user_select = await self._session.execute(select(User.username).where(User.username == username))
        user: User | None = user_select.scalar_one_or_none()
        if not user is None:
            raise AuthenticationError("Пользователь с username '{username}' уже существует.".format(username=username))
        salt = bcrypt.gensalt()
        password_hash = self._password_hash(password=password, salt=salt)

        new_user = User(username=username, password_hash=password_hash, salt=salt)
        self._session.add(new_user)
        await self._session.refresh(new_user)
        await self._session.commit()

        user_session: Session = await self.new_session(user=new_user)
        self._session.add(user_session)

        return user_session.session_id, self._get_token(username=username, timedelta=datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))

    async def get_access_token(self, session_id: str) -> str:
        session_select = await self._session.execute(select(Session).where(Session.session_id == session_id))
        session: Session | None = session_select.scalar_one_or_none()
        if session is None:
            raise NotFoundError("Сессии с указанными session id не найдено.")
        refresh_token = session.refresh_token
        try:
            username = self._decode_token(token=refresh_token)["username"]
        except AuthenticationError:
            raise AuthorizationError("Истек срок действия сессии.")
        access_token = self._get_token(username=username, timedelta=datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
        return access_token

    async def new_session(self, user: User) -> Session:
        refresh_token = self._get_token(username=user.username,
                                        timedelta=datetime.timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))
        user_session = Session(session_id=uuid.uuid4(), refresh_token=refresh_token, user_id=user.id)
        self._session.add(user_session)
        await self._session.refresh(user_session)
        await self._session.commit()
        return user_session

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

    async def add(self, title: str, description: Optional[str] = None) -> Habit:
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


