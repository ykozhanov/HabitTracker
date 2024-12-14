from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = Column(Integer, primary_key=True)
    telegram_user_id: Mapped[int] = Column(Integer, nullable=False)
    access_token: Mapped[str] = Column(String, nullable=False)
    refresh_token: Mapped[str] = Column(String, unique=True, nullable=False)
