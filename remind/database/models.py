from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, relationship

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = Column(Integer, primary_key=True)
    refresh_token: Mapped[str] = Column(String, unique=True, nullable=False)

    user_info_telegram: Mapped["UserInfoTelegram"] = relationship(
        argument="UserInfoTelegram",
        back_populates="user",
        lazy="joined",
        uselist=False,
        cascade="all, delete-orphan",
    )
    user_celery_tasks: Mapped[list["CeleryTask"]] = relationship(
        argument="CeleryTask",
        back_populates="user",
        lazy="subquery",
        cascade="all, delete-orphan",
    )


class CeleryTask(Base):
    __tablename__ = "celery_tasks"

    id: Mapped[int] = Column(Integer, primary_key=True)
    habit_id: Mapped[int] = Column(Integer, unique=True)
    celery_task_id: Mapped[str] = Column(String, nullable=False)
    last_time_send_celery_task: Mapped[datetime] = Column(
        DateTime(timezone=True), nullable=False
    )
    user_id: Mapped[int] = Column(ForeignKey(column="users.id"), nullable=False)

    user: Mapped["User"] = relationship(
        argument="User", back_populates="user_celery_tasks"
    )


class UserInfoTelegram(Base):
    __tablename__ = "users_telegram_info"

    id: Mapped[int] = Column(Integer, primary_key=True)
    user_id_telegram: Mapped[int] = Column(Integer, nullable=False)
    chat_id_telegram: Mapped[int] = Column(Integer, nullable=False)
    telegram_bot_token: Mapped[str] = Column(String, nullable=False)
    user_id: Mapped[int] = Column(ForeignKey(column="users.id"), nullable=False)

    user: Mapped["User"] = relationship(
        argument="User", back_populates="user_info_telegram"
    )
