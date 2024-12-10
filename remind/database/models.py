from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    refresh_token = Column(String, unique=True, nullable=False)

    user_info_telegram = relationship(argument="UserInfoTelegram", back_populates="user", lazy="joined", uselist=False)
    user_celery_tasks = relationship(argument="CeleryTask", back_populates="user", lazy="subquery")


class CeleryTask(Base):
    __tablename__ = "celery_tasks"

    id = Column(Integer, primary_key=True)
    habit_id = Column(Integer, unique=True)
    celery_task_id = Column(String, nullable=False)
    last_time_send_celery_task = Column(DateTime(timezone=True), nullable=False)
    user_id = Column(ForeignKey(column="users.id"), nullable=False)

    user = relationship(argument="User", back_populates="user_celery_tasks")


class UserInfoTelegram(Base):
    __tablename__ = "users_telegram_info"

    id = Column(Integer, primary_key=True)
    user_id_telegram = Column(Integer, nullable=False)
    chat_id_telegram = Column(Integer, nullable=False)
    telegram_bot_token = Column(String, nullable=False)
    user_id = Column(ForeignKey(column="users.id"), nullable=False)

    user = relationship(argument="User", back_populates="user_info_telegram")
