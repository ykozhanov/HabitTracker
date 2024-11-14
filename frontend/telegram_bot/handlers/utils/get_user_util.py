import logging
from typing import Any

from frontend.telegram_bot.database import User, UserController

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        # logging.FileHandler('frontend.log'),
        logging.StreamHandler(),
    ]
)

logger = logging.getLogger(__name__)

def get_user(data: dict[str, Any], user_id: int) -> User | None:
    data["login"] = data.get("login", {})
    user: User | None = data["login"].get("user")
    if not user:
        user = UserController(user_id=user_id).get_user()
        if user:
            data["login"]["user"] = user
    logger.info(f"get_user user: {user}")
    return user
