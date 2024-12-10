import logging
from typing import Any
import datetime

import bcrypt
import jwt
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy.orm import subqueryload

from backend.database.models import User
from backend.exceptions import NotFoundError, AuthenticationError, AuthorizationError
from backend.config import JWT_PRIVATE_KEY, JWT_PUBLIC_KEY, JWT_ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        # logging.FileHandler('frontend.log'),
        logging.StreamHandler(),
    ]
)

logger = logging.getLogger(__name__)


class UserController:

    def __init__(self, session: AsyncSession):
        self._session = session

    @staticmethod
    def _password_hash(password: str) -> bytes:
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password=password.encode('utf-8'), salt=salt)

    @staticmethod
    def _check_password(password_hash: bytes, password: str) -> bool:
        return bcrypt.checkpw(password=password.encode('utf-8'), hashed_password=password_hash)

    @staticmethod
    def _encode_token(user_id: int, timedelta: datetime.timedelta, type_token: str) -> str:
        payload = {
            'sub': str(user_id),
            'exp': datetime.datetime.now(datetime.timezone.utc) + timedelta,
            'type': type_token,
        }
        encoded = jwt.encode(payload=payload, key=JWT_PRIVATE_KEY, algorithm=JWT_ALGORITHM)
        return encoded

    @staticmethod
    def _decode_token(token: str | bytes) -> dict[str, Any]:
        logger.info(f"_decode_token token: {token}")
        try:
            payload = jwt.decode(jwt=token, key=JWT_PUBLIC_KEY, algorithms=[JWT_ALGORITHM])
        except jwt.InvalidTokenError:
            raise AuthenticationError("Проблема с токеном.")
        return payload


    # @staticmethod
    # def _get_token(user_id: int, timedelta: datetime.timedelta):
    #     payload = {
    #         'user_id': user_id,
    #         'exp': datetime.datetime.now() + timedelta,
    #     }
    #     return jwt.encode(payload=payload, private_key=JWT_PRIVATR_KEY, algorithm=JWT_ALGORITHM)

    # @staticmethod
    # def _decode_token(token: str) -> dict[str, Any]:
    #     try:
    #         payload = jwt.decode(jwt=token, key=JWT_SECRET_KEY, algorithms=JWT_ALGORITHM)
    #     except jwt.ExpiredSignatureError:
    #         raise AuthenticationError("Токен устарел.")
    #     except jwt.InvalidTokenError:
    #         raise AuthenticationError("Неверный токен.")
    #     return payload

    async def login(self, username: str, password: str) -> (str, str):
        user_select = await self._session.execute(select(User).where(User.username == username))
        user: User | None = user_select.scalar_one_or_none()
        if not user:
            raise NotFoundError("Пользователь не найден.")
        check_password = self._check_password(password=password, password_hash=user.password_hash)
        if not check_password:
            raise AuthenticationError("Неверный логин или пароль.")
        return user


    # async def get_all_user(self) -> list[User]:
    #     users_select = await self._session.execute(select(User))
    #     return [i_user for i_user in users_select.scalars().all()]

    async def get(self, token: str) -> User:
        payload = self._decode_token(token=token)
        logger.info(f"get_user payload: {payload}")
        if payload.get("type") != "access":
            raise AuthorizationError("Неверный тип токена.")
        user_id: int = int(payload.get("sub"))
        user_select = await self._session.execute(select(User).where(User.id == user_id))
    # user_select = await self._session.execute(select(User).options(subqueryload(User.habits)).where(User.username == username))
        user: User | None = user_select.scalar_one_or_none()
        if not user:
            raise NotFoundError("Пользователь не найден.")
        return user

    async def add(self, username: str, password: str, email: str) -> (str, str):
        user_select = await self._session.execute(select(User.username).where(User.username == username))
        user: User | None = user_select.scalar_one_or_none()
        if user:
            raise AuthenticationError(f"Пользователь {username!r} уже существует.")
        # salt = bcrypt.gensalt()
        password_hash = self._password_hash(password=password)

        new_user = User(username=username, password_hash=password_hash, email=email)
        self._session.add(new_user)
        await self._session.commit()
        await self._session.refresh(new_user)

        refresh_token = self._encode_token(user_id=new_user.id, timedelta=datetime.timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS), type_token="refresh")
        access_token = self._encode_token(user_id=new_user.id, timedelta=datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES), type_token="access")

        new_user.refresh_token = refresh_token
        await self._session.commit()

        # user_session: UserSession = await self.new_session(user=new_user)
        # self._session.add(user_session)
        # await self._session.commit()
        # await self._session.refresh(user_session)

        return access_token, refresh_token

    async def get_access_token(self, refresh_token: str) -> str:
        # refresh_token_select = await self._session.execute(select(UserSession.refresh_token).where(UserSession.session_id == session_id))
        # if not (refresh_token := refresh_token_select.scalar_one_or_none()):
        #     raise NotFoundError("Сессии с указанным session_id не найдено.")
        payload = self._decode_token(token=refresh_token)
        if payload.get("type") != "refresh":
            raise AuthenticationError("Неверный токен.")
        user_id = int(payload.get("sub"))
        return self._encode_token(user_id=user_id, timedelta=datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES), type_token="access")

    async def update_refresh_token(self, user_id: int) -> (str, str):
        user_select = await self._session.execute(select(User).where(User.id == user_id))
        user: User | None = user_select.scalar_one_or_none()
        if not user:
            raise NotFoundError("Пользователь не найден.")
        refresh_token = self._encode_token(user_id=user.id, timedelta=datetime.timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS), type_token="refresh")
        access_token = self._encode_token(user_id=user.id,
                                          timedelta=datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
                                          type_token="access")
        user.refresh_token = refresh_token
        await self._session.commit()
        return access_token, refresh_token

    # async def get_user_session(self, user: User) -> UserSession:
    #     refresh_token = self._encode_token(user_id=user.id,
    #                                     timedelta=datetime.timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS), type_token="refresh")
    #     user_session_select = await self._session.execute(select(UserSession).where(UserSession.user_id == user.id))
    #     if not (user_session := user_session_select.scalar_one_or_none()):
    #         user_session = UserSession(session_id=str(uuid.uuid4()), refresh_token=refresh_token, user_id=user.id)
    #         self._session.add(user_session)
    #         await self._session.commit()
    #         await self._session.refresh(user_session)
    #     return user_session
    #
    # async def delete_user_sessions(self, user: User) -> None:
    #     await self._session.execute(delete(UserSession).where(UserSession.user_id == user.id))
    #     await self._session.commit()