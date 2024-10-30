from typing import Optional

import requests

from frontend.telegram_bot.config import URL_FOR_FRONTEND
from frontend.telegram_bot.database import UserSession, get_session
from frontend.telegram_bot.exceptions import TimeOutError, LoginError


class UserAPIController:
    _urls = {
        "login": "/users/login/",
        "register": "/users/register/",
    }


    def __init__(self, username: str, password: str):
        self._username = username
        self._password = password

    def login(self, register: Optional[bool] = False) -> UserSession:
        url = URL_FOR_FRONTEND + self._urls["register"] if register else URL_FOR_FRONTEND + self._urls["login"]
        data = {
            "username": self._username,
            "password": self._password,
        }

        try:
            response = requests.post(url=url, json=data, timeout=60)
        except requests.exceptions.Timeout:
            raise TimeOutError()

        if response.status_code in (200, 201):
            with (get_session() as s):
                get_data = response.json()
                session_id = get_data["session_id"]
                access_token = get_data["access_token"]
                session = UserSession(session_id=session_id, access_token=access_token)

                s.add(session)
                s.commit()
                s.refresh(session)

                return session
        else:
            raise LoginError
