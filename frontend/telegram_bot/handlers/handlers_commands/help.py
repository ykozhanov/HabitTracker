from telebot.types import Message

from frontend.telegram_bot.bot import bot
from frontend.telegram_bot.bot.keyboards import GenKeyboards
from frontend.telegram_bot.bot.states import CommandsStatesGroup

from ..utils import get_user


@bot.message_handler(commands=["help"])  # type: ignore
def handle_help(message: Message) -> None:
    with bot.retrieve_data(
        user_id=message.from_user.id, chat_id=message.chat.id
    ) as data:
        user = get_user(data=data, user_id=message.from_user.id)

    if user:
        bot.send_message(
            chat_id=message.chat.id,
            text="Что хотите сделать?",
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
            text="Для начала вам необходимо авторизоваться.\n\nДля этого нажмите /login.",
        )
