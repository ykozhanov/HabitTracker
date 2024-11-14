from frontend.telegram_bot.api import UserAPIController
from frontend.telegram_bot.database import User, UserController
from frontend.telegram_bot.bot import bot
from frontend.telegram_bot.exceptions import AuthorizationError


def update_token(user: User, chat_id: int):
    try:
        new_user_data = UserAPIController().token(session_id=user.session_id)
        UserController.update(**new_user_data.model_dump())
    except AuthorizationError:
        bot.send_message(chat_id=chat_id, text="Пожалуйста, авторизуйтесь снова /login")
