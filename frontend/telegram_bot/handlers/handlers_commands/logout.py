from telebot.types import Message

from frontend.telegram_bot.bot import bot
from frontend.telegram_bot.bot.states import CommandsStatesGroup
from frontend.telegram_bot.database import User, UserController
from remind import RemindTelegramController


@bot.message_handler(commands=["logout"])  # type: ignore
def handle_logout(message: Message) -> None:
    with bot.retrieve_data(
        user_id=message.from_user.id, chat_id=message.chat.id
    ) as data:
        if data.get("login", {}).get("user", None):
            user: User = data["login"]["user"]
            remind_telegram_controller = RemindTelegramController(
                refresh_token=user.refresh_token
            )
            remind_telegram_controller.delete_user()
            del data["login"]["user"]
            if data.get("habits", None):
                del data["habits"]
    user_controller = UserController(user_id=message.from_user.id)
    user_controller.delete_user()
    bot.send_message(
        chat_id=message.chat.id,
        text="Вы успешно вышли!\n\nЧтобы войти заново, нажмите /login",
    )
    bot.set_state(
        user_id=message.from_user.id,
        state=CommandsStatesGroup.logout,
        chat_id=message.chat.id,
    )
