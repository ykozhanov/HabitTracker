from telebot.types import Message

from frontend.telegram_bot.bot import bot
from frontend.telegram_bot.states import CommandsStatesGroup
from frontend.telegram_bot.database import UserSession
from frontend.telegram_bot.keyboards import GenKeyboards


@bot.message_handler(commands=["help"])
def handle_help(message: Message) -> None:
    with bot.retrieve_data(user_id=message.from_user.id, chat_id=message.chat.id) as data:
        user: UserSession = data["login"].get("user", None)

    if user:
        bot.send_message(
            chat_id=message.chat.id,
            text=f"Что хотите сделать, {user.username}?",
            reply_markup=GenKeyboards.select_action_reply(),
        )
        bot.set_state(
            user_id=message.from_user.id,
            state=CommandsStatesGroup.select_action,
            chat_id=message.chat.id,
        )
    else:
        bot.send_message(
            chat_id=message.chat.id,
            text="Для начала вам необходимой авторизоваться. Для этого нажмите /login.",
        )
