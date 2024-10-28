from typing import Generator
from contextlib import contextmanager

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

Base = declarative_base()


class UserSession(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True)
    session_id = Column(String(length=36), unique=True, nullable=False)
    access_token = Column(String, nullable=False)
    username = Column(String, nullable=False)
    time_notifications_hour = Column(Integer)
    time_notifications_minutes = Column(Integer)


engine = create_engine("sqlite:///habittracker_frontend.db")
Base.metadata.create_all(engine)

SessionLocal = sessionmaker(bind=engine)


@contextmanager
def get_session() -> Generator[Session, None, None]:
    with SessionLocal() as s:
        yield s
