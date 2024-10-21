from telebot.types import Message, CallbackQuery

from ..keyboards import GenKeyboards
from ..states import UserStatesGroup, HabitStatesGroup
from ..bot import bot


@bot.message_handler(commands=["start"])
def handle_start(message: Message) -> None:
    username = message.from_user.username
    bot.send_message(
        chat_id=message.chat.id,
        text="Добро пожаловать, {username}!/nВы уже зарегистрированы в приложении HabitTracker?"
        .format(username=username),
        reply_markup=GenKeyboards.login_keyboard(),
    )
    bot.set_state(
        user_id=message.from_user.id,
        state=UserStatesGroup.login,
        chat_id=message.chat.id,
    )


@bot.callback_query_handler(func=None, state=UserStatesGroup.login)
def handle_login(call: CallbackQuery):
    if "Да" in call.message.text:
        bot.send_message(chat_id=call.message.chat.id, text="Отлично! Введите ваш логин:")
        bot.set_state(
            user_id=call.from_user.id,
            state=UserStatesGroup.waiting_login,
            chat_id=call.message.chat.id,
        )
    if "Нет" in call.message.text:
        bot.send_message(chat_id=call.message.chat.id, text="Давайте зарегистрируемся! Введите логин:")
        bot.set_state(
            user_id=call.from_user.id,
            state=UserStatesGroup.waiting_login,
            chat_id=call.message.chat.id,
        )
    else:
        bot.send_message(
            chat_id=call.message.chat.id,
            text="Извините, я вас не совсем понял. Подскажите пожалуйста, вы уже зарегистрированы в приложении HabitTracker?",
            reply_markup=GenKeyboards.login_keyboard(),
        )