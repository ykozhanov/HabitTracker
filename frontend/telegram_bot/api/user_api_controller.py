from typing import Optional

import requests

from frontend.telegram_bot.config import URL_BACKEND
from frontend.telegram_bot.exceptions import (
    AuthenticationError,
    TimeOutError,
    UserError,
)
from frontend.telegram_bot.schemas import UserSchema


class UserAPIController:
    _urls = {
        "login": "/users/login/",
        "register": "/users/register/",
        "token": "/users/token/",
    }

    @classmethod
    def login(
        cls, username: str, password: str, email: Optional[str] = None
    ) -> UserSchema:
        url = (
            URL_BACKEND + cls._urls["register"]
            if email
            else URL_BACKEND + cls._urls["login"]
        )
        data = {
            "username": username,
            "password": password,
        }

        if email:
            data["email"] = email

        try:
            response = requests.post(url=url, data=data, timeout=60)
        except requests.exceptions.Timeout:
            raise TimeOutError()

        if response.status_code in (200, 201):
            return UserSchema.model_validate(response.json())
        elif response.status_code == 401:
            raise AuthenticationError(detail=response.json().get("detail", None))
        else:
            raise UserError(detail="Не удалось получить данные пользователя.")

    @classmethod
    def get_token(cls, refresh_token: str) -> UserSchema:
        url = URL_BACKEND + cls._urls["token"]
        headers = {
            "Authorization": f"Bearer {refresh_token}",
        }
        response = requests.get(url=url, headers=headers)
        if response.status_code == 401:
            raise AuthenticationError()

        return UserSchema.model_validate(response.json())
