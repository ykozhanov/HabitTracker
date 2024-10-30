from os import getenv
from typing import Generator
from contextlib import contextmanager

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker, Session as SessionORM

from backend.config import get_database_url
from backend.models import User, HabitCeleryTelegram

POSTGRES_USER=getenv("POSTGRES_USER", "admin")
POSTGRES_PASSWORD=getenv("POSTGRES_PASSWORD", "admin")
POSTGRES_DB=getenv("POSTGRES_DB", "habit_tracker")

DATABASE_URL = get_database_url(sync=True)

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(bind=engine)


@contextmanager
def get_session() -> Generator[SessionORM, None, None]:
    with SessionLocal() as s:
        yield s



class CeleryDatabaseController:

    @classmethod
    def get_all_user(cls) -> list[User]:
        with get_session() as session:
            users = session.execute(select(User)).scalars().all()
            return list(users)

    @classmethod
    def add_new_habit_celery(cls, habit_id: int, celery_task_id: str) -> None:
        with get_session() as session:
            new_habit_celery = HabitCeleryTelegram(celery_task_id=celery_task_id, habit_id=habit_id)
            session.add(new_habit_celery)
            session.commit()
