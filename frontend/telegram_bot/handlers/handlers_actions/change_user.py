from telebot.types import Message

from frontend.telegram_bot.bot import bot
from frontend.telegram_bot.bot.states import CommandsStatesGroup
from ..utils import get_user


@bot.message_handler(func=lambda message: "🔄" in message.text, state=CommandsStatesGroup.select_action)
def change_user(message: Message):
    with bot.retrieve_data(user_id=message.from_user.id, chat_id=message.chat.id) as data:
        user = get_user(data=data, user_id=message.from_user.id)

        if user:
            del data["login"]
            bot.send_message(
                chat_id=message.chat.id,
                text="Вы успешно вышли из профиля, для того чтобы войти заново нажмите /login.",
            )
        else:
            bot.send_message(
                chat_id=message.chat.id,
                text="Для начала вам необходимой авторизоваться. Для этого нажмите /login.",
            )
