from typing import Optional

import requests

from . import URL_FOR_FRONTEND
from . import UserSession
from . import HabitError, TimeOutError
from . import HabitSchema
from ..exceptions import LoginError


class HabitAPIController:
    _urls = {
        "habits": "/habits/",
        "habit_id": "/habits/{habit_id}/",
        "mark": "/habits/{habit_id}/mark/",
    }

    def __init__(self, user: UserSession):
        self._user = UserSession
        self._headers = {
            "Authorization": f"Bearer {user.access_token}",
        }

    def get_list_habits(self) -> list[HabitSchema]:
        url = URL_FOR_FRONTEND + self._urls["habits"]

        try:
            response = requests.get(url=url, headers=self._headers, timeout=60)
        except requests.exceptions.Timeout:
            raise TimeOutError()

        if response.status_code == 200:
            get_data = response.json().get("data", [])
            return [HabitSchema(**i_habit) for i_habit in get_data]
        elif response.status_code == 401:
            raise LoginError(detail="Ошибка аутентификации.")
        else:
            raise HabitError(detail=response.json().get("detail", ""))

    def add_habit(self, title: str, description: Optional[str] = None) -> HabitSchema:
        url = URL_FOR_FRONTEND + self._urls["habits"]
        data = {
            "title": title,
            "description": description,
        }

        try:
            response = requests.post(url=url, headers=self._headers, json=data, timeout=60)
        except requests.exceptions.Timeout:
            raise TimeOutError()

        if response.status_code != 201:
            raise HabitError(detail=response.json().get("detail", ""))
        elif response.status_code == 401:
            raise LoginError(detail="Ошибка аутентификации.")

        try:
            return response.json()["data"]
        except KeyError:
            raise HabitError(detail="Привычка не загрузилась.")

    def delete_habit(self, habit_id: int) -> None:
        url = URL_FOR_FRONTEND + self._urls["habit_id"].format(habit_id=habit_id)

        try:
            response = requests.delete(url=url, headers=self._headers, timeout=60)
        except requests.exceptions.Timeout:
            raise TimeOutError()

        if response.status_code != 200:
            raise HabitError(detail=response.json().get("detail", ""))
        elif response.status_code == 401:
            raise LoginError(detail="Ошибка аутентификации.")

    def update_habit(self, habit_id: int, title: str, description: str, patch: Optional[bool] = False) -> HabitSchema:
        url = URL_FOR_FRONTEND + self._urls["habit_id"].format(habit_id=habit_id)
        data = {
            "title": title,
            "description": description,
        }

        try:
            response = requests.patch(url=url, headers=self._headers, json=data, timeout=60) if patch \
                else requests.put(url=url, headers=self._headers, json=data, timeout=60)
        except requests.exceptions.Timeout:
            raise TimeOutError()

        if response.status_code != 200:
            raise HabitError(detail=response.json().get("detail", ""))
        elif response.status_code == 401:
            raise LoginError(detail="Ошибка аутентификации.")

        try:
            return response.json()["data"]
        except KeyError:
            raise HabitError(detail="Привычка не загрузилась.")
