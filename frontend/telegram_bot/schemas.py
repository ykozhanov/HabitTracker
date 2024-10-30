from typing import Optional
from datetime import time

from pydantic import BaseModel


class HabitSchema(BaseModel):
    id: Optional[int] = None
    title: str
    description: Optional[str] = None
    count_repeat: Optional[int] = None


class HabitRemindTelegramSchema(BaseModel):
    remind_time: time
    chat_id: int
    user_id: int
