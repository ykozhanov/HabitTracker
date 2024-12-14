from datetime import datetime, time, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    LargeBinary,
    String,
    Time,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, relationship

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = Column(Integer, primary_key=True)
    username: Mapped[str] = Column(String(length=50), unique=True, nullable=False)
    email: Mapped[str] = Column(String, nullable=False)
    password_hash: Mapped[bytes] = Column(LargeBinary, nullable=False)
    refresh_token: Mapped[str | None] = Column(String)
    # salt = Column(LargeBinary, nullable=False)

    habits: Mapped[list["Habit"]] = relationship(
        "Habit",
        back_populates="user",
        lazy="subquery",
        cascade="all, delete-orphan",
        order_by="Habit.id",
    )


class Habit(Base):
    __tablename__ = "habits"

    id: Mapped[int] = Column(Integer, primary_key=True)
    title: Mapped[str] = Column(String(length=100), nullable=False)
    description: Mapped[str | None] = Column(String(length=500))
    done: Mapped[bool] = Column(Boolean, default=False)
    remind_time: Mapped[time] = Column(Time, nullable=False)
    last_time_check: Mapped[datetime | None] = Column(DateTime(timezone=True))
    count_repeat: Mapped[int] = Column(Integer, default=0)
    create_at: Mapped[datetime] = Column(
        DateTime(timezone=True), nullable=False, default=datetime.now(tz=timezone.utc)
    )
    user_id: Mapped[int] = Column(Integer, ForeignKey("users.id"))

    user: Mapped["User"] = relationship("User", back_populates="habits", lazy="select")
