from datetime import datetime
from typing import Optional

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
    done: Optional[bool] = None
    count_repeat: Optional[int] = None
    create_at: Optional[datetime] = None
    user_id: Optional[int] = None

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
