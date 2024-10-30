from typing import Optional


class NotFoundError(Exception):

    def __init(self, detail: Optional[str] = "Объект не найден."):
        self.detail = detail
        self.status_code = 404


class AuthenticationError(Exception):

    def __init(self, detail: Optional[str] = "Ошибка входа."):
        self.detail = detail
        self.status_code = 401


class AuthorizationError(Exception):

    def __init(self, detail: Optional[str] = "Недостаточно прав."):
        self.detail = detail
        self.status_code = 403


class HabitError(Exception):

    def __init(self, detail: Optional[str] = "При редактировании привычки что-то пошло не так."):
        self.detail = detail
        self.status_code = 409
