from sqlalchemy import update

from remind.database import User, get_session


class UserController:

    def __init__(self, refresh_token: str):
        self._refresh_token = refresh_token

    def add_user(self) -> User:
        with get_session() as session:
            new_user = User(refresh_token=self._refresh_token)
            session.add(new_user)
            session.commit()
            session.refresh(new_user)
            return new_user

    def delete_user(self) -> None:
        with get_session() as session:
            user = (
                session.query(User)
                .filter(User.refresh_token == self._refresh_token)
                .scalar()
            )
            session.delete(user)
            session.commit()

    def get_user(self) -> User:
        with get_session() as session:
            user: User = (
                session.query(User)
                .filter(User.refresh_token == self._refresh_token)
                .scalar()
            )
            return user

    @staticmethod
    def get_all_users() -> list[User]:
        with get_session() as session:
            users: list[User] = session.query(User).all()
            return users

    def update_refresh_token(self, new_refresh_token: str) -> None:
        with get_session() as session:
            update_sql = (
                update(User)
                .where(User.refresh_token == self._refresh_token)
                .values(refresh_token=new_refresh_token)
            )
            session.execute(update_sql)
            session.commit()
