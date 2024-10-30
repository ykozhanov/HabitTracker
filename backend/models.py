from sqlalchemy import Column, ForeignKey, String, Integer, DateTime, LargeBinary, Boolean, Time
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(length=50), unique=True, nullable=False)
    email = Column(String, nullable=False)
    password_hash = Column(LargeBinary, nullable=False)
    salt = Column(LargeBinary, nullable=False)

    habits = relationship("Habit", back_populates="user", lazy="subquery")
    sessions = relationship("Session", back_populates="user", lazy="select")


class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True)
    session_id = Column(String(length=36), unique=True, nullable=False)
    refresh_token = Column(String, nullable=False, unique=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=func.now())

    user = relationship("User", back_populates="sessions", lazy="select")


class Habit(Base):
    __tablename__ = "habits"

    id = Column(Integer, primary_key=True)
    title = Column(String(length=100), nullable=False)
    description = Column(String(length=500))
    done = Column(Boolean, default=False)
    count_repeat = Column(Integer, default=0)
    create_at = Column(DateTime, nullable=False, default=func.now())
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="habits", lazy="select")
    habit_tracker_telegram = relationship("HabitTracker", back_populates="habit", lazy="joined")
    habit_celery_telegram = relationship("HabitCeleryTelegram", back_populates="habit", lazy="joined")


class HabitTrackerTelegram(Base):
    __tablename__ = "habittracker"

    id = Column(Integer, primary_key=True)
    remind_time = Column(Time, nullable=False)
    last_time_check = Column(DateTime, nullable=False, default=func.now())
    chat_id = Column(Integer, nullable=False)
    user_id = Column(Integer, nullable=False)
    habit_id = Column(Integer, ForeignKey("habits.id"))

    habit = relationship("Habit", back_populates="habit_tracker_telegram", lazy="select")


class HabitCeleryTelegram(Base):
    __tablename__ = "habitcelerytelegram"

    id = Column(Integer, primary_key=True)
    celery_task_id = Column(Integer, unique=True)
    habit_id = Column(Integer, ForeignKey("habits.id"))

    habit = relationship("Habit", back_populates="habit_celery_telegram", lazy="joined")
