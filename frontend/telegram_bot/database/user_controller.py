from typing import Optional

from frontend.telegram_bot.exceptions import UserError

from .database import get_session
from .models import User


class UserController:

    def __init__(self, user_id: int):
        self._user_id = user_id

    def add_new_user(self, access_token: str, refresh_token: str) -> User:
        with get_session() as session:
            if (
                session.query(User.telegram_user_id)
                .filter(User.telegram_user_id == self._user_id)
                .scalar()
            ):
                raise UserError("Пользователь уже вошел.")

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
        with get_session() as session:
            user: User = (
                session.query(User)
                .filter(User.telegram_user_id == self._user_id)
                .scalar()
            )
            if not user:
                raise UserError("Пользователя не существует.")

            user.access_token = access_token
            if refresh_token:
                user.refresh_token = refresh_token

            session.commit()
            session.refresh(user)
            return user

    def get_user(self) -> User | None:
        with get_session() as session:
            user: User = (
                session.query(User)
                .filter(User.telegram_user_id == self._user_id)
                .scalar()
            )
            return user

    def delete_user(self) -> None:
        with get_session() as session:
            if (
                user := session.query(User)
                .filter(User.telegram_user_id == self._user_id)
                .scalar()
            ):
                session.delete(user)
                session.commit()
