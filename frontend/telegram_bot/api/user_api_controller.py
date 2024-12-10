import logging
from typing import Optional

import requests

# from backend.database.models import UserSession
from frontend.telegram_bot.config import URL_BACKEND
from frontend.telegram_bot.schemas import UserSchema
from frontend.telegram_bot.exceptions import TimeOutError, AuthenticationError, AuthorizationError

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        # logging.FileHandler('frontend.log'),
        logging.StreamHandler(),
    ]
)

logger = logging.getLogger(__name__)


class UserAPIController:
    _urls = {
        "login": "/users/login/",
        "register": "/users/register/",
        "token": "/users/token/",
    }

    # def __init__(self, username: str, password: str):
        # logger.info("start UserAPIController")
        # self._username = username
        # self._password = password

    @classmethod
    def login(cls, username: str, password: str, email: Optional[bool] = False) -> UserSchema:
        logger.info("start login")
        url = URL_BACKEND + cls._urls["register"] if email else URL_BACKEND + cls._urls["login"]
        data = {
            "username": username,
            "password": password,
        }

        if email:
            data["email"] = email

        try:
            # logger.info(f"url: {url}")
            response = requests.post(url=url, data=data, timeout=60)
            logger.info(f"response: {response.json()}")
            # logger.info(f"detail: {response.json().get("detail", None)}")
        except requests.exceptions.Timeout:
            raise TimeOutError()

        # logger.info(f"status code: {response.status_code}")
        if response.status_code in (200, 201):
            return UserSchema.model_validate(response.json())
            # with get_session() as s:
            #     session_id = response.json()["session_id"]
            #     access_token = response.json()["access_token"]
            #     session = UserSession(session_id=session_id, access_token=access_token)
            #     # logger.info(f"session: {session}")
            #
            #     s.add(session)
            #     s.commit()
            #     s.refresh(session)
            #
            #     return session
        elif response.status_code == 401:
            raise AuthenticationError(detail=response.json().get("detail", None))

    @classmethod
    def get_token(cls, refresh_token: str) -> UserSchema:
        url = URL_BACKEND + cls._urls["token"]
        headers = {
            "Authorization": f"Bearer {refresh_token}",
        }
        response = requests.get(url=url, headers=headers)
        logger.info(f"get_token data: {response.json()}")
        if response.status_code == 401:
            raise AuthenticationError()

        return UserSchema.model_validate(response.json())
