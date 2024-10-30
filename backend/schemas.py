from typing import Optional
from datetime import time

from pydantic import BaseModel


class SuccessSchema(BaseModel):
    result: Optional[bool] = True
    status_code: Optional[int] = 200


class ErrorSchema(SuccessSchema):
    result: Optional[bool] = False
    detail: str


class HabitSchema(BaseModel):
    id: Optional[int] = None
    title: str
    description: Optional[str] = None
    count_repeat: Optional[int] = None

    class Config:
        orm_mode = True


class PatchHabitSchema(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None


class HabitRemindTelegramSchema(BaseModel):
    habit_id: Optional[int] = None
    remind_time: time
    chat_id: int
    user_id: int

    class Config:
        orm_mode = True


class SuccessGetHabitsListSchema(SuccessSchema):
    data: list[HabitSchema]


class SuccessGetHabitSchema(SuccessSchema):
    data: HabitSchema


class LoginSchema(BaseModel):
    username: str
    password: str


class CreateUserSchema(LoginSchema):
    email: str


class SuccessLoginSchema(SuccessSchema):
    session_id: str
    access_token: str
