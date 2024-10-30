from datetime import time

import requests

from frontend.telegram_bot.config import URL_FOR_FRONTEND
from frontend.telegram_bot.database import UserSession
from frontend.telegram_bot.exceptions import HabitError, TimeOutError, LoginError


class RemindAPIController:
    url = "/reminds/telegram/{habit_id}/"

    def __init__(self, user: UserSession, habit_id: int):
        self._habit_id = habit_id
        self._user = UserSession
        self._headers = {
            "Authorization": f"Bearer {user.access_token}",
        }

    def add_habit_remind(self, remind_time: time, chat_id: int, user_id: int) -> None:
        url = URL_FOR_FRONTEND + self.url.format(habit_id=self._habit_id)
        data = {
            "habit_id": self._habit_id,
            "remind_time": remind_time,
            "chat_id": chat_id,
            "user_id": user_id,
        }

        try:
            response = requests.post(url=url, headers=self._headers, json=data, timeout=60)
        except requests.exceptions.Timeout:
            raise TimeOutError()

        if response.status_code == 401:
            raise LoginError(detail="Ошибка аутентификации.")
        elif response.status_code != 201:
            raise HabitError(detail=response.json().get("detail", ""))

    def update_habit_remind(self, remind_time: time, chat_id: int, user_id: int) -> None:
        url = URL_FOR_FRONTEND + self.url.format(habit_id=self._habit_id)
        data = {
            "habit_id": self._habit_id,
            "remind_time": remind_time,
            "chat_id": chat_id,
            "user_id": user_id,
        }

        try:
            response = requests.put(url=url, headers=self._headers, json=data, timeout=60)
        except requests.exceptions.Timeout:
            raise TimeOutError()

        if response.status_code == 401:
            raise LoginError(detail="Ошибка аутентификации.")
        elif response.status_code != 200:
            raise HabitError(detail=response.json().get("detail", ""))
