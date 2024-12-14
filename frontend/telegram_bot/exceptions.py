from typing import Optional


class AuthenticationError(Exception):

    def __init__(self, detail: Optional[str] = "Необходимой войти снова."):
        self.detail = detail


class HabitError(Exception):

    def __init__(
        self, detail: Optional[str] = "При работе с привычками что-то пошло не так."
    ):
        self.detail = detail


class TimeOutError(Exception):

    def __init__(self, detail: Optional[str] = "Запрос выполнялся слишком долго."):
        self.detail = detail


class UserError(Exception):

    def __init__(self, detail: Optional[str] = "Ошибка пользователя."):
        self.detail = detail


class EnvError(Exception):

    def __init__(
        self, detail: Optional[str] = "Одна из переменных окружения не заполнена!"
    ):
        self.detail = detail
