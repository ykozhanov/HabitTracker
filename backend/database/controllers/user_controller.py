import datetime
from typing import Any

import bcrypt
import jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.config import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    JWT_ALGORITHM,
    JWT_PRIVATE_KEY,
    JWT_PUBLIC_KEY,
    REFRESH_TOKEN_EXPIRE_DAYS,
)
from backend.database.models import User
from backend.exceptions import AuthenticationError, AuthorizationError, NotFoundError


class UserController:

    def __init__(self, session: AsyncSession):
        self._session = session

    @staticmethod
    def _password_hash(password: str) -> bytes:
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password=password.encode("utf-8"), salt=salt)

    @staticmethod
    def _check_password(password_hash: bytes, password: str) -> bool:
        return bcrypt.checkpw(
            password=password.encode("utf-8"), hashed_password=password_hash
        )

    @staticmethod
    def _encode_token(
        user_id: int, timedelta: datetime.timedelta, type_token: str
    ) -> str:
        payload = {
            "sub": str(user_id),
            "exp": datetime.datetime.now(datetime.timezone.utc) + timedelta,
            "type": type_token,
        }
        encoded = jwt.encode(
            payload=payload, key=JWT_PRIVATE_KEY, algorithm=JWT_ALGORITHM  # type: ignore
        )
        return encoded

    @staticmethod
    def _decode_token(token: str | bytes) -> dict[str, Any]:
        try:
            payload = jwt.decode(
                jwt=token, key=JWT_PUBLIC_KEY, algorithms=[JWT_ALGORITHM]  # type: ignore
            )
            if not isinstance(payload, dict):
                raise AuthenticationError("Ошибка чтения токена.")
        except jwt.InvalidTokenError:
            raise AuthenticationError("Ошибка чтения токена.")
        else:
            return payload

    async def login(self, username: str, password: str) -> User:
        user_select = await self._session.execute(
            select(User).where(User.username == username)
        )
        user: User | None = user_select.scalar_one_or_none()
        if not user:
            raise NotFoundError("Пользователь не найден.")
        check_password = self._check_password(
            password=password, password_hash=user.password_hash
        )
        if not check_password:
            raise AuthenticationError("Неверный логин или пароль.")
        return user

    async def get(self, token: str) -> User:
        payload = self._decode_token(token=token)
        if payload.get("type") != "access":
            raise AuthorizationError("Неверный тип токена.")
        sub_value = payload.get("sub")
        if sub_value is None:
            raise AuthenticationError("Ошибка чтения токена.")
        try:
            user_id = int(sub_value)
        except ValueError:
            raise AuthenticationError("Ошибка чтения токена.")
        user_select = await self._session.execute(
            select(User).where(User.id == user_id)
        )
        user: User | None = user_select.scalar_one_or_none()
        if not user:
            raise NotFoundError("Пользователь не найден.")
        return user

    async def add(self, username: str, password: str, email: str) -> tuple[str, str]:
        user_select = await self._session.execute(
            select(User.username).where(User.username == username)
        )
        user: str | None = user_select.scalar_one_or_none()
        if user:
            raise AuthenticationError(f"Пользователь {username!r} уже существует.")
        password_hash = self._password_hash(password=password)

        new_user = User(username=username, password_hash=password_hash, email=email)
        self._session.add(new_user)
        await self._session.commit()
        await self._session.refresh(new_user)

        refresh_token = self._encode_token(
            user_id=new_user.id,
            timedelta=datetime.timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
            type_token="refresh",
        )
        access_token = self._encode_token(
            user_id=new_user.id,
            timedelta=datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
            type_token="access",
        )

        new_user.refresh_token = refresh_token
        await self._session.commit()

        return access_token, refresh_token

    async def get_access_token(self, refresh_token: str) -> str:
        payload = self._decode_token(token=refresh_token)
        if payload.get("type") != "refresh":
            raise AuthenticationError("Неверный токен.")
        sub_value = payload.get("sub")
        if sub_value is None:
            raise AuthenticationError("Ошибка чтения токена.")
        try:
            user_id = int(sub_value)
        except ValueError:
            raise AuthenticationError("Ошибка чтения токена.")
        return self._encode_token(
            user_id=user_id,
            timedelta=datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
            type_token="access",
        )

    async def update_refresh_token(self, user_id: int) -> tuple[str, str]:
        user_select = await self._session.execute(
            select(User).where(User.id == user_id)
        )
        user: User | None = user_select.scalar_one_or_none()
        if not user:
            raise NotFoundError("Пользователь не найден.")
        refresh_token = self._encode_token(
            user_id=user.id,
            timedelta=datetime.timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
            type_token="refresh",
        )
        access_token = self._encode_token(
            user_id=user.id,
            timedelta=datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
            type_token="access",
        )
        user.refresh_token = refresh_token
        await self._session.commit()
        return access_token, refresh_token
