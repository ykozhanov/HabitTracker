from typing import Optional


class NotFoundError(Exception):

    def __init(self, message: Optional[str] = "Объект не найден."):
        self.message = message
