import requests

from frontend.telegram_bot.config import URL_FOR_FRONTEND
from frontend.telegram_bot.database import UserSession
from frontend.telegram_bot.exceptions import HabitError, TimeOutError, LoginError
from frontend.telegram_bot.schemas import HabitSchema


class HabitAPIController:
    _urls = {
        "habits": "/habits/",
        "habit_id": "/habits/{habit_id}/",
        "complete": "/habits/{habit_id}/complete/",
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

    def add_habit(self, title: str, description: str) -> HabitSchema:
        url = URL_FOR_FRONTEND + self._urls["habits"]
        data = {
            "title": title,
            "description": description,
        }

        try:
            response = requests.post(url=url, headers=self._headers, json=data, timeout=60)
        except requests.exceptions.Timeout:
            raise TimeOutError()

        if response.status_code == 401:
            raise LoginError(detail="Ошибка аутентификации.")
        elif response.status_code != 201:
            raise HabitError(detail=response.json().get("detail", ""))

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

        if response.status_code == 401:
            raise LoginError(detail="Ошибка аутентификации.")
        elif response.status_code != 200:
            raise HabitError(detail=response.json().get("detail", ""))

    def update_habit(self, habit_id: int, title: str, description: str) -> HabitSchema:
        url = URL_FOR_FRONTEND + self._urls["habit_id"].format(habit_id=habit_id)
        data = {
            "title": title,
            "description": description,
        }

        try:
            response = requests.put(url=url, headers=self._headers, json=data, timeout=60)
        except requests.exceptions.Timeout:
            raise TimeOutError()

        if response.status_code == 401:
            raise LoginError(detail="Ошибка аутентификации.")
        elif response.status_code != 200:
            raise HabitError(detail=response.json().get("detail", ""))

        try:
            return response.json()["data"]
        except KeyError:
            raise HabitError(detail="Привычка не загрузилась.")

    def complete_habit(self, habit_id: int):
        url = URL_FOR_FRONTEND + self._urls["complete"].format(habit_id=habit_id)

        try:
            response = requests.patch(url=url, headers=self._headers, timeout=60)
        except requests.exceptions.Timeout:
            raise TimeOutError()

        if response.status_code == 401:
            raise LoginError(detail="Ошибка аутентификации.")
        elif response.status_code != 200:
            raise HabitError(detail=response.json().get("detail", ""))
