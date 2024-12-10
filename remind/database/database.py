from typing import Generator
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session as SessionORM

from remind.config import get_database_url
from .models import Base

DATABASE_URL = get_database_url(sync=True)

engine = create_engine(url=DATABASE_URL)
Base.metadata.create_all(engine)

SessionLocal = sessionmaker(bind=engine)


@contextmanager
def get_session() -> Generator[SessionORM, None, None]:
    with SessionLocal() as s:
        yield s
