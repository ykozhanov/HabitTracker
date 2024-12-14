from datetime import datetime, time
from typing import Optional

from pydantic import BaseModel, field_validator


class RemindHabitSchema(BaseModel):
    id: Optional[int] = None
    title: str
    description: Optional[str] = None
    remind_time: Optional[time] = None
    last_time_check: Optional[datetime] = None
    count_repeat: Optional[int] = None

    @classmethod
    @field_validator("remind_time", mode="before")
    def parse_remind_time(cls, value: str | time) -> time:
        if isinstance(value, str):
            return datetime.strptime(value, "%H:%M").time()
        return value

    @classmethod
    @field_validator("last_time_check", mode="before")
    def parse_last_time_check(cls, value: str | datetime) -> datetime:
        if isinstance(value, str):
            return datetime.strptime(value, "%Y-%m-%d %H:%M")
        return value

    class Config:
        from_attributes = True
        json_encoders = {
            "remind_time": lambda v: v.strftime("%H:%M"),
            "last_time_check": lambda v: v.strftime("%Y-%m-%d %H:%M"),
        }
