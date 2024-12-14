from frontend.telegram_bot.api import UserAPIController
from frontend.telegram_bot.bot import bot
from frontend.telegram_bot.database import User, UserController
from frontend.telegram_bot.exceptions import AuthenticationError
from remind import RemindTelegramController


def update_token(user: User, chat_id: int) -> bool:
    try:
        new_user_data = UserAPIController().get_token(refresh_token=user.refresh_token)
        user_controller = UserController(user_id=user.telegram_user_id)
        new_user: User = user_controller.update(**new_user_data.model_dump())
        with bot.retrieve_data(user_id=user.telegram_user_id, chat_id=chat_id) as data:
            data["login"]["user"] = new_user
        return True
    except AuthenticationError:
        with bot.retrieve_data(user_id=user.telegram_user_id, chat_id=chat_id) as data:
            if data.get("login", {}).get("user", None):
                remind_telegram_controller = RemindTelegramController(
                    refresh_token=user.refresh_token
                )
                remind_telegram_controller.delete_user()
                del data["login"]["user"]
                if data.get("habits"):
                    del data["habits"]
        user_controller = UserController(user_id=user.telegram_user_id)
        user_controller.delete_user()
        bot.send_message(chat_id=chat_id, text="Пожалуйста, авторизуйтесь снова /login")
        return False
