from typing import Optional


class LoginError(Exception):

    def __init__(self, detail: Optional[str] = "При входе что-то пошло не так."):
        self.detail = detail


class HabitError(Exception):

    def __init__(self, detail: Optional[str] = "При работе с привычками что-то пошло не так."):
        self.detail = detail


class TimeOutError(Exception):

    def __init__(self, detail: Optional[str] = "Запрос выполнялся слишком долго."):
        self.detail = detail
