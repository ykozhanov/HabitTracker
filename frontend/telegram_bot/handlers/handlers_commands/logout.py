from telebot.types import Message

from frontend.telegram_bot.bot import bot
from frontend.telegram_bot.bot.states import CommandsStatesGroup


@bot.message_handler(commands=["logout"])
def handle_logout(message: Message) -> None:
    with bot.retrieve_data(user_id=message.from_user.id, chat_id=message.chat.id) as data:
        if data.get("login", {}).get("user", None):
            del data["login"]["user"]
            if data.get("habits", None):
                del data["habits"]

    bot.send_message(
        chat_id=message.chat.id,
        text=f"Вы успешно вышли! Чтобы войти заново, нажмите /login",
    )
    bot.set_state(
        user_id=message.from_user.id,
        state=CommandsStatesGroup.logout,
        chat_id=message.chat.id,
    )


