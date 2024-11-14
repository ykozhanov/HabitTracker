import logging
from datetime import time
from typing import Optional

from telebot.types import Message, CallbackQuery, ReplyKeyboardRemove
from telebot.apihelper import ApiTelegramException

from remind import RemindHabitSchema, RemindTelegramController

from frontend.telegram_bot.bot import bot
from frontend.telegram_bot.bot.states import CommandsStatesGroup, HabitStatesGroup, HabitCreateStatesGroup
from frontend.telegram_bot.bot.keyboards import GenKeyboards
from frontend.telegram_bot.api import HabitAPIController
from frontend.telegram_bot.exceptions import TimeOutError, LoginError, HabitError
from frontend.telegram_bot.config import VIEW_MESSAGES
from ..utils import get_user

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        # logging.FileHandler('frontend.log'),
        logging.StreamHandler(),
    ]
)

logger = logging.getLogger(__name__)


@bot.callback_query_handler(func=lambda call: call.data.split("#")[0] == "create", state=HabitStatesGroup.habits)
def create_new_habit_callback(call: CallbackQuery):
    bot.delete_message(
        chat_id=call.message.chat.id,
        message_id=call.message.id,
    )
    # with bot.retrieve_data(user_id=call.from_user.id, chat_id=call.message.chat.id) as data:
    #     logger.info(f"create_new_habit_callback - data: {data}\nuser_id: {call.from_user.id}\nchat_id: {call.message.chat.id}")
    create_new_habit(message=call.message, user_id=call.from_user.id)


@bot.message_handler(func=lambda message: "➕" in message.text, state=CommandsStatesGroup.select_action)
def create_new_habit(message: Message, user_id: Optional[int] = None):
    with bot.retrieve_data(user_id=user_id if user_id else message.from_user.id, chat_id=message.chat.id) as data:
        user = get_user(data=data, user_id=message.from_user.id)
        logger.info(f"create_new_habit - data: {data}\nuser_id: {message.from_user.id}\nchat_id: {message.chat.id}")

        if user:
            bot.send_message(
                chat_id=message.chat.id,
                text="Введите *заголовок* для новой привычки:",
                reply_markup=ReplyKeyboardRemove(),
                parse_mode="Markdown",
            )
            bot.set_state(
                user_id=user_id if user_id else message.from_user.id,
                state=HabitCreateStatesGroup.waiting_title,
                chat_id=message.chat.id,
            )
        else:
            bot.send_message(
                chat_id=message.chat.id,
                text="Для начала вам необходимой авторизоваться.\nДля этого нажмите /login.",
            )


@bot.message_handler(state=HabitCreateStatesGroup.waiting_title)
def waiting_new_title(message: Message):
    with bot.retrieve_data(user_id=message.from_user.id, chat_id=message.chat.id) as data:
        data["create"] = {}
        data["create"]["title"] = message.text
    bot.send_message(
        chat_id=message.chat.id,
        text="Введите *описание* для новой привычки:",
        parse_mode="Markdown",
    )
    bot.set_state(
        user_id=message.from_user.id,
        state=HabitCreateStatesGroup.waiting_description,
        chat_id=message.chat.id,
    )


@bot.message_handler(state=HabitCreateStatesGroup.waiting_description)
def waiting_new_description(message: Message):
    with bot.retrieve_data(user_id=message.from_user.id, chat_id=message.chat.id) as data:
        data["create"]["description"] = message.text
    bot.send_message(
        chat_id=message.chat.id,
        text="Установите ежедневное напоминание.\nВведите *час* когда будет приходить уведомление (от 0 до 23):",
        parse_mode="Markdown",
    )
    bot.set_state(
        user_id=message.from_user.id,
        state=HabitCreateStatesGroup.waiting_remind_time_hour,
        chat_id=message.chat.id,
    )


@bot.message_handler(state=HabitCreateStatesGroup.waiting_remind_time_hour)
def waiting_new_remind_time_hour(message: Message):
    if not message.text.isdigit():
        bot.send_message(
            chat_id=message.chat.id,
            text="Введите число!",
        )
    else:
        if not 0 <= int(message.text) < 24:
            bot.send_message(
                chat_id=message.chat.id,
                text="Введите число от 0 до 23!",
            )
        else:
            with bot.retrieve_data(user_id=message.from_user.id, chat_id=message.chat.id) as data:
                data["create"]["hour"] = int(message.text)
            bot.send_message(
                chat_id=message.chat.id,
                text="Введите *минуту* когда будет приходить уведомление (от 0 до 59):",
                parse_mode="Markdown",
            )
            bot.set_state(
                user_id=message.from_user.id,
                state=HabitCreateStatesGroup.waiting_remind_time_minute,
                chat_id=message.chat.id,
            )


@bot.message_handler(state=HabitCreateStatesGroup.waiting_remind_time_minute)
def waiting_new_remind_time_minute(message: Message):
    if not message.text.isdigit():
        bot.send_message(
            chat_id=message.chat.id,
            text="Введите число!",
        )
    else:
        if not 0 <= int(message.text) < 60:
            bot.send_message(
                chat_id=message.chat.id,
                text="Введите число от 0 до 59!",
            )
        else:
            with bot.retrieve_data(user_id=message.from_user.id, chat_id=message.chat.id) as data:
                data["create"]["minute"] = int(message.text)
                text = VIEW_MESSAGES["check"].format(
                    title=data["create"]["title"] ,
                    description=data["create"]["description"],
                    hour=data["create"]["hour"],
                    minute=data["create"]["minute"],
                )
                bot.set_state(
                    user_id=message.from_user.id,
                    state=HabitCreateStatesGroup.check_habit,
                    chat_id=message.chat.id,
                )
            try:
                bot.send_message(
                    chat_id=message.chat.id,
                    text=f"Вот ваша новая привычка:\n\n{text}\n\nВсё верно?",
                    reply_markup=GenKeyboards.yes_or_no_inline(),
                    parse_mode="Markdown",
                )
            except ApiTelegramException:
                bot.set_state(
                    user_id=message.from_user.id,
                    state=CommandsStatesGroup.select_action,
                    chat_id=message.chat.id,
                )
                bot.send_message(
                    chat_id=message.chat.id,
                    text="Ошибка чтения привычки. Вернуться к действиями /help"
                )


@bot.callback_query_handler(state=HabitCreateStatesGroup.check_habit)
def check_create_new_habit(call: CallbackQuery):
    if call.data == "yes":
        with bot.retrieve_data(user_id=call.from_user.id, chat_id=call.message.chat.id) as data:
            user = get_user(data=data, user_id=call.from_user.id)

        if user:
            title = data["create"]["title"]
            description = data["create"]["description"]
            remind_time = time(hour=data["create"]["hour"], minute=data["create"]["minute"])
            remind_time_str = remind_time.strftime('%H:%M')
            del data["create"]
            habit_api_controller = HabitAPIController(user=user)

            try:
                habit = habit_api_controller.add_habit(title=title, description=description, remind_time=remind_time_str)
                remind_telegram_controller = RemindTelegramController(user_token=user.access_token)
                remind_telegram_controller.add_habit(habit=RemindHabitSchema.model_validate(habit.model_dump()))
                bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.id)
                bot.send_message(
                    chat_id=call.message.chat.id,
                    text="Новая привычка успешно создана!\n\nЧто вы хотите сделать теперь? ⏬",
                    reply_markup=GenKeyboards.select_action_reply(),
                )
                bot.set_state(
                    user_id=call.from_user.id,
                    state=CommandsStatesGroup.select_action,
                    chat_id=call.message.chat.id,
                )
            except (HabitError, TimeOutError) as exc:
                bot.send_message(
                    chat_id=call.message.chat.id,
                    text=f"Что-то пошло не так.\n\n_{exc.detail}_\n\nВернуться в меню действий /help",
                    parse_mode="Markdown",
                )
            except LoginError:
                bot.send_message(
                    chat_id=call.message.chat.id,
                    text=f"Ошибка аутентификации, попробуйте войти снова /login.",
                )
            except Exception as exc:
                bot.send_message(
                    chat_id=call.message.chat.id,
                    text=f"Что-то пошло не так. {exc}",
                )
        else:
            bot.send_message(
                chat_id=call.message.chat.id,
                text="Для начала вам необходимой авторизоваться.\nДля этого нажмите /login.",
            )
    elif call.data == "no":
        bot.send_message(
            chat_id=call.message.chat.id,
            text=f"Попробовать снова?",
            reply_markup=GenKeyboards.yes_or_no_inline(),
        )
        bot.set_state(
            user_id=call.from_user.id,
            state=HabitCreateStatesGroup.back_or_again_create,
            chat_id=call.message.chat.id,
        )
    else:
        bot.send_message(
            chat_id=call.message.chat.id,
            text="Извините, я вас не совсем понял.\nПодскажите пожалуйста, вы подтверждаете создание новой привычки?",
            reply_markup=GenKeyboards.yes_or_no_inline(),
        )


@bot.callback_query_handler(state=HabitCreateStatesGroup.back_or_again_create)
def back_or_again_create(call: CallbackQuery):
    if call.data == "yes":
        bot.send_message(
            chat_id=call.message.chat.id,
            text="Введите заголовок для новой привычки:",
        )
        bot.set_state(
            user_id=call.from_user.id,
            state=HabitCreateStatesGroup.waiting_title,
            chat_id=call.message.chat.id,
        )
    elif call.data == "no":
        bot.send_message(
            chat_id=call.message.chat.id,
            text="Что вы хотите сделать?",
            reply_markup=GenKeyboards.select_action_reply(),
        )
        bot.set_state(
            user_id=call.from_user.id,
            state=CommandsStatesGroup.select_action,
            chat_id=call.message.chat.id,
        )
    else:
        bot.send_message(
            chat_id=call.message.chat.id,
            text="Извините, я вас не совсем понял.\nПодскажите пожалуйста, вы хотите попробовать снова?",
            reply_markup=GenKeyboards.yes_or_no_inline(),
        )
