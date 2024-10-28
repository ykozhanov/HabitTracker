from pydantic import BaseModel


class HabitSchema(BaseModel):
    id: int
    title: str
    description: str | None
    count_repeat: int
