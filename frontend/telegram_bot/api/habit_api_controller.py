import logging
import requests

from frontend.telegram_bot.config import URL_BACKEND
from frontend.telegram_bot.database import User
from frontend.telegram_bot.exceptions import HabitError, TimeOutError, AuthenticationError, AuthorizationError
from frontend.telegram_bot.schemas import HabitSchema


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        # logging.FileHandler('frontend.log'),
        logging.StreamHandler(),
    ]
)

logger = logging.getLogger(__name__)


class HabitAPIController:
    _urls = {
        "habits": "/habits/",
        "habit_id": "/habits/{habit_id}/",
        "complete": "/habits/{habit_id}/complete/",
    }

    def __init__(self, user: User):
        self._user = user
        self._headers = {
            "Authorization": f"Bearer {user.access_token}",
        }

    def get_list_not_done_habits(self) -> list[HabitSchema]:
        url = URL_BACKEND + self._urls["habits"]

        try:
            response = requests.get(url=url, headers=self._headers, timeout=60)
        except requests.exceptions.Timeout:
            raise TimeOutError()

        if response.status_code == 200:
            get_data = response.json().get("data", [])
            logger.info(f"get_data: {get_data}")
            logger.info(f"result: {[HabitSchema.model_validate(i_habit) for i_habit in get_data]}")
            return [HabitSchema.model_validate(i_habit) for i_habit in get_data]
        elif response.status_code == 401:
            raise AuthenticationError(detail="Не удалось войти.")
        else:
            raise HabitError(detail=response.json().get("detail", ""))

    def add_habit(self, title: str, description: str, remind_time: str) -> HabitSchema:
        url = URL_BACKEND + self._urls["habits"]
        data = {
            "title": title,
            "description": description,
            "remind_time": remind_time,
        }

        try:
            response = requests.post(url=url, headers=self._headers, json=data, timeout=60)
            logger.info(f"add_habit data: {response.json()}")
        except requests.exceptions.Timeout:
            raise TimeOutError()

        if response.status_code == 401:
            raise AuthenticationError(detail="Не удалось войти.")
        elif response.status_code != 201:
            raise HabitError(detail=response.json().get("detail", ""))

        try:
            return HabitSchema.model_validate(response.json().get("data", {}))
        except KeyError:
            raise HabitError(detail="Привычка не загрузилась.")

    def delete_habit(self, habit_id: int) -> None:
        url = URL_BACKEND + self._urls["habit_id"].format(habit_id=habit_id)

        try:
            response = requests.delete(url=url, headers=self._headers, timeout=60)
        except requests.exceptions.Timeout:
            raise TimeOutError()

        if response.status_code == 401:
            raise AuthenticationError(detail="Не удалось войти.")
        elif response.status_code != 200:
            raise HabitError(detail=response.json().get("detail", ""))

    def update_habit(self, habit_id: int, title: str, description: str, remind_time: str) -> HabitSchema:
        url = URL_BACKEND + self._urls["habit_id"].format(habit_id=habit_id)
        data = {
            "title": title,
            "description": description,
            "remind_time": remind_time,
        }

        try:
            response = requests.put(url=url, headers=self._headers, json=data, timeout=60)
        except requests.exceptions.Timeout:
            raise TimeOutError()

        if response.status_code == 401:
            raise AuthenticationError(detail="Не удалось войти.")
        elif response.status_code != 200:
            raise HabitError(detail=response.json().get("detail", ""))

        response_data = response.json().get("data")
        if not response_data:
            raise HabitError(detail="Привычка не загрузилась.")
        logger.info(f"update_habit data (type {type(response.json())}): {response.json().get("data")}")
        try:
            HabitSchema.model_validate(response_data)
        except Exception as exc:
            logger.info(f"update_habit exc: {exc}")
        return HabitSchema.model_validate(response_data)

    def complete_habit(self, habit_id: int) -> None:
        url = URL_BACKEND + self._urls["complete"].format(habit_id=habit_id)

        try:
            response = requests.patch(url=url, headers=self._headers, timeout=60)
        except requests.exceptions.Timeout:
            raise TimeOutError()

        if response.status_code == 401:
            raise AuthenticationError(detail="Не удалось войти.")
        elif response.status_code != 200:
            raise HabitError(detail=response.json().get("detail", ""))
