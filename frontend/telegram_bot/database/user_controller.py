import logging
from typing import Optional

from frontend.telegram_bot.exceptions import UserError
from .models import User
from .database import get_session

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

    def __init__(self, user_id: int):
        self._user_id = user_id

    # @staticmethod
    # def _telegram_user_id_hash(user_id: str, salt: bytes) -> bytes:
    #     return bcrypt.hashpw(user_id.encode('utf-8'), salt)
    #
    # @staticmethod
    # def _check_telegram_user_id(user_id_hash: bytes, password: str) -> bool:
    #     return bcrypt.checkpw(password.encode('utf-8'), user_id_hash)

    def add_new_user(self, access_token: str, refresh_token: str) -> User:
        with get_session() as session:
            if session.query(User.telegram_user_id).filter(User.telegram_user_id == self._user_id).scalar():
                raise UserError(f"Пользователь уже вошел.")
            # salt = bcrypt.gensalt()
            # telegram_user_id_hash = self._telegram_user_id_hash(user_id=user_id, salt=salt)

            new_user = User(
                telegram_user_id=self._user_id,
                access_token=access_token,
                refresh_token=refresh_token,
            )

            session.add(new_user)
            session.commit()
            session.refresh(new_user)

            return new_user

    def update(self, access_token: str, refresh_token: Optional[str] = None) -> User:
        logger.info(f"update access_token: {access_token}, refresh_token: {refresh_token}")
        with get_session() as session:
            if not (user := session.query(User).filter(User.telegram_user_id == self._user_id).scalar()):
                raise UserError(f"Пользователя не существует.")

            user.access_token = access_token
            if refresh_token:
                user.refresh_token = refresh_token

            session.commit()
            session.refresh(user)
            logger.info(f"update user.access_token: {user.access_token}")
            return user

    def get_user(self) -> User | None:
        with get_session() as session:
            return session.query(User).filter(User.telegram_user_id == self._user_id).scalar()

    def delete_user(self) -> None:
        with get_session() as session:
            if user := session.query(User).filter(User.telegram_user_id == self._user_id).scalar():
                session.delete(user)
                session.commit()

    # @staticmethod
    # def _get_token(username: str, timedelta: datetime.timedelta):
    #     payload = {
    #         'username': username,
    #         'exp': datetime.datetime.now() + timedelta,
    #     }
    #     return jwt.encode(payload=payload, key=JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

    # @staticmethod
    # def _decode_token(token: str) -> dict[str, Any]:
    #     try:
    #         payload = jwt.decode(jwt=token, key=JWT_SECRET_KEY, algorithms=JWT_ALGORITHM)
    #     except jwt.ExpiredSignatureError:
    #         raise AuthenticationError("Токен устарел.")
    #     except jwt.InvalidTokenError:
    #         raise AuthenticationError("Неверный токен.")
    #     return payload



    # async def login(self, username: str, password: str) -> User:
    #     user_select = await self._session.execute(select(User).where(User.username == username))
    #     user: User | None = user_select.scalar_one_or_none()
    #     if user is None:
    #         raise NotFoundError("Пользователь не найден.")
    #     check_password = self._check_password(password=password, password_hash=user.password_hash)
    #     if not check_password:
    #         raise AuthenticationError("Неверный логин или пароль.")
    #     return user

    # async def get_all_user(self) -> list[User]:
    #     users_select = await self._session.execute(select(User))
    #     return [i_user for i_user in users_select.scalars().all()]
    #
    # async def get(self, token: str) -> User:
    #     username: str = self._decode_token(token=token)["username"]
    #     user_select = await self._session.execute(select(User).where(User.username == username))
    #     # user_select = await self._session.execute(select(User).options(subqueryload(User.habits)).where(User.username == username))
    #     user: User | None = user_select.scalar_one_or_none()
    #     if user is None:
    #         raise NotFoundError("Пользователь не найден.")
    #     return user
    #
    # async def add(self, username: str, password: str, email: str) -> (str, str):
    #     user_select = await self._session.execute(select(User.username).where(User.username == username))
    #     user: User | None = user_select.scalar_one_or_none()
    #     if not user is None:
    #         raise AuthenticationError(f"Пользователь {username!r} уже существует.")
    #     salt = bcrypt.gensalt()
    #     password_hash = self._password_hash(password=password, salt=salt)
    #
    #     new_user = User(username=username, password_hash=password_hash, salt=salt, email=email)
    #     self._session.add(new_user)
    #     await self._session.commit()
    #     await self._session.refresh(new_user)
    #
    #     user_session: UserSession = await self.new_session(user=new_user)
    #     # self._session.add(user_session)
    #     # await self._session.commit()
    #     # await self._session.refresh(user_session)
    #
    #     return user_session.session_id, self._get_token(username=username, timedelta=datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    #
    # async def get_access_token(self, session_id: str) -> str:
    #     session_select = await self._session.execute(select(UserSession).where(UserSession.session_id == session_id))
    #     session: UserSession | None = session_select.scalar_one_or_none()
    #     if session is None:
    #         raise NotFoundError("Сессии с указанным session_id не найдено.")
    #     refresh_token = session.refresh_token
    #     try:
    #         username = self._decode_token(token=refresh_token)["username"]
    #     except AuthenticationError:
    #         raise AuthorizationError("Истек срок действия сессии.")
    #     access_token = self._get_token(username=username, timedelta=datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    #     return access_token
    #
    # async def new_session(self, user: User) -> UserSession:
    #     refresh_token = self._get_token(username=user.username,
    #                                     timedelta=datetime.timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))
    #     user_session = UserSession(session_id=str(uuid.uuid4()), refresh_token=refresh_token, user_id=user.id)
    #     self._session.add(user_session)
    #     await self._session.commit()
    #     await self._session.refresh(user_session)
    #     return user_session
