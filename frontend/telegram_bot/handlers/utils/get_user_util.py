from typing import Any

from frontend.telegram_bot.database import User, UserController


def get_user(data: dict[str, Any], user_id: int) -> User | None:
    data["login"] = data.get("login", {})
    user: User | None = data["login"].get("user")
    if not user:
        user = UserController(user_id=user_id).get_user()
        if user:
            data["login"]["user"] = user
    return user
