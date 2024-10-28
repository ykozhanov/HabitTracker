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
    description: str | None
    count_repeat: Optional[int] = None

    class Config:
        orm_mode = True


class PatchHabitSchema(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None


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
