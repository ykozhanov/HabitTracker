from sqlalchemy import update

from remind.database import User, get_session


class UserController:

    def __init__(self, user_token: str):
        self._user_token = user_token

    def add_user(self) -> User:
        with get_session() as session:
            new_user = User(user_token=self._user_token)
            session.add(new_user)
            session.commit()
            session.refresh(new_user)
            return new_user

    def get_user(self) -> User | None:
        with get_session() as session:
            return session.query(User).filter(User.user_token == self._user_token).scalar()

    @staticmethod
    def get_all_users() -> list[User]:
        with get_session() as session:
            return session.query(User).scalars().all()

    def update_user_token(self, new_user_token: str) -> None:
        with get_session() as session:
            update_sql = update(User).where(User.user_token == self._user_token).values(user_token=new_user_token)
            session.execute(update_sql)
            session.commit()
