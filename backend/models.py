from sqlalchemy import Column, ForeignKey, String, Text, Integer, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(length=50), nullable=False)

    habits = relationship("Habit", back_populates="user", lazy="subquery")


class Habit(Base):
    __tablename__ = "habits"

    id = Column(Integer, primary_key=True)
    title = Column(String(length=100), nullable=False)
    description = Column(String(length=500))
    create_at = Column(DateTime, nullable=False, default=func.now())
    user_id = Column(Integer, ForeignKey('users.id'))

    user = relationship("User", back_populates="habits", lazy="joined")
