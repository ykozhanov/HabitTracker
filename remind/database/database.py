# from os import getenv
from typing import Generator
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session as SessionORM

from .models import Base

# from remind.config import get_database_url

# POSTGRES_USER=getenv("POSTGRES_USER", "admin")
# POSTGRES_PASSWORD=getenv("POSTGRES_PASSWORD", "admin")
# POSTGRES_DB=getenv("POSTGRES_DB", "habit_tracker")

engine = create_engine("sqlite:///habittracker_remind.db")
Base.metadata.create_all(engine)

SessionLocal = sessionmaker(bind=engine)


@contextmanager
def get_session() -> Generator[SessionORM, None, None]:
    with SessionLocal() as s:
        yield s
