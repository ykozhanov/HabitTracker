from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True)
    telegram_user_id = Column(Integer, nullable=False)
    session_id = Column(String(length=36), unique=True, nullable=False)
    access_token = Column(String, nullable=False)
