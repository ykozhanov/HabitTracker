from datetime import time

from telebot.apihelper import ApiTelegramException
from telebot.types import CallbackQuery, Message

from frontend.telegram_bot.api import HabitAPIController
from frontend.telegram_bot.bot import bot
from frontend.telegram_bot.bot.keyboards import GenKeyboards
from frontend.telegram_bot.bot.states import (
    CommandsStatesGroup,
    HabitStatesGroup,
    HabitUpdateStatesGroup,
)
from frontend.telegram_bot.config import VIEW_MESSAGES
from frontend.telegram_bot.database import User
from frontend.telegram_bot.exceptions import AuthenticationError
from frontend.telegram_bot.schemas import HabitSchema
from remind import RemindHabitSchema, RemindTelegramController

from ..utils import get_user, send_habits, update_token


@bot.callback_query_handler(
    func=lambda call: call.data.split("#")[0] == "update", state=HabitStatesGroup.habits
)  # type: ignore
def update_habit_callback(call: CallbackQuery):
    with bot.retrieve_data(
        user_id=call.from_user.id, chat_id=call.message.chat.id
    ) as data:
        user = get_user(data=data, user_id=call.from_user.id)
        data["update"] = {"page": int(call.data.split("#")[1])}

    bot.delete_message(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
    )

    if user:
        bot.send_message(
            chat_id=call.message.chat.id,
            text="Хотите изменить заголовок?",
            reply_markup=GenKeyboards.yes_or_no_inline(),
        )
        bot.set_state(
            user_id=call.from_user.id,
            state=HabitUpdateStatesGroup.update_title,
            chat_id=call.message.chat.id,
        )
    else:
        bot.send_message(
            chat_id=call.message.chat.id,
            text="Для начала вам необходимой авторизоваться.\nДля этого нажмите /login.",
        )


@bot.callback_query_handler(state=HabitUpdateStatesGroup.update_title)  # type: ignore
def update_title_callback(call: CallbackQuery):
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.id)
    if call.data == "yes":
        bot.send_message(
            chat_id=call.message.chat.id,
            text="Введите новый заголовок:",
        )
        bot.set_state(
            user_id=call.from_user.id,
            state=HabitUpdateStatesGroup.waiting_title,
            chat_id=call.message.chat.id,
        )
    elif call.data == "no":
        with bot.retrieve_data(
            user_id=call.from_user.id, chat_id=call.message.chat.id
        ) as data:
            habits: list[HabitSchema] = data.get("habits")
            habit: HabitSchema = habits[data["update"]["page"] - 1]
            data["update"]["title"] = habit.title
        bot.send_message(
            chat_id=call.message.chat.id,
            text="Хотите изменить описание?",
            reply_markup=GenKeyboards.yes_or_no_inline(),
        )
        bot.set_state(
            user_id=call.from_user.id,
            state=HabitUpdateStatesGroup.update_description,
            chat_id=call.message.chat.id,
        )
    else:
        bot.send_message(
            chat_id=call.message.chat.id,
            text="Извините, я вас не совсем понял.\nПодскажите пожалуйста, вы хотите изменить заголовок?",
            reply_markup=GenKeyboards.yes_or_no_inline(),
        )


@bot.message_handler(state=HabitUpdateStatesGroup.waiting_title)  # type: ignore
def waiting_updated_title(message: Message):
    with bot.retrieve_data(
        user_id=message.from_user.id, chat_id=message.chat.id
    ) as data:
        data["update"]["title"] = message.text
    bot.send_message(
        chat_id=message.chat.id,
        text="Хотите изменить описание?",
        reply_markup=GenKeyboards.yes_or_no_inline(),
    )
    bot.set_state(
        user_id=message.from_user.id,
        state=HabitUpdateStatesGroup.update_description,
        chat_id=message.chat.id,
    )


@bot.callback_query_handler(state=HabitUpdateStatesGroup.update_description)  # type: ignore
def update_description_callback(call: CallbackQuery):
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.id)
    if call.data == "yes":
        bot.send_message(
            chat_id=call.message.chat.id,
            text="Введите новое описание:",
        )
        bot.set_state(
            user_id=call.from_user.id,
            state=HabitUpdateStatesGroup.waiting_description,
            chat_id=call.message.chat.id,
        )
    elif call.data == "no":
        with bot.retrieve_data(
            user_id=call.from_user.id, chat_id=call.message.chat.id
        ) as data:
            habits: list[HabitSchema] = data.get("habits", [])
            habit: HabitSchema = habits[data["update"]["page"] - 1]
            data["update"]["description"] = habit.description
        bot.send_message(
            chat_id=call.message.chat.id,
            text="Хотите изменить время напоминания?",
            reply_markup=GenKeyboards.yes_or_no_inline(),
        )
        bot.set_state(
            user_id=call.from_user.id,
            state=HabitUpdateStatesGroup.update_remind_time,
            chat_id=call.message.chat.id,
        )
    else:
        bot.send_message(
            chat_id=call.message.chat.id,
            text="Извините, я вас не совсем понял.\nПодскажите пожалуйста, вы хотите изменить время напоминания?",
            reply_markup=GenKeyboards.yes_or_no_inline(),
        )


@bot.message_handler(state=HabitUpdateStatesGroup.waiting_description)  # type: ignore
def waiting_updated_description(message: Message):
    with bot.retrieve_data(
        user_id=message.from_user.id, chat_id=message.chat.id
    ) as data:
        data["update"]["description"] = message.text
    bot.send_message(
        chat_id=message.chat.id,
        text="Хотите изменить время напоминания?",
        reply_markup=GenKeyboards.yes_or_no_inline(),
    )
    bot.set_state(
        user_id=message.from_user.id,
        state=HabitUpdateStatesGroup.update_remind_time,
        chat_id=message.chat.id,
    )


@bot.callback_query_handler(state=HabitUpdateStatesGroup.update_remind_time)  # type: ignore
def update_remind_time_callback(call: CallbackQuery):
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.id)
    if call.data == "yes":
        bot.send_message(
            chat_id=call.message.chat.id,
            text="Введите *час* когда будет приходить уведомление (от 0 до 23):\n\n*Используйте московское время!* 🕐",
            parse_mode="Markdown",
        )
        bot.set_state(
            user_id=call.from_user.id,
            state=HabitUpdateStatesGroup.waiting_remind_time_hour,
            chat_id=call.message.chat.id,
        )
    elif call.data == "no":
        with bot.retrieve_data(
            user_id=call.from_user.id, chat_id=call.message.chat.id
        ) as data:
            habits: list[HabitSchema] = data.get("habits")
            habit: HabitSchema = habits[data["update"]["page"] - 1]
            data["update"]["remind_time"] = habit.remind_time
            text = VIEW_MESSAGES["check"].format(
                title=data["update"]["title"],
                description=data["update"]["description"],
                hour=data["update"]["remind_time"].hour,
                minute=data["update"]["remind_time"].minute,
            )
            bot.send_message(
                chat_id=call.message.chat.id,
                text=f"Вот ваша обновленная привычка:\n\n{text}\n\nВсё верно?",
                reply_markup=GenKeyboards.yes_or_no_inline(),
                parse_mode="Markdown",
            )
            bot.set_state(
                user_id=call.from_user.id,
                state=HabitUpdateStatesGroup.check_habit,
                chat_id=call.message.chat.id,
            )
    else:
        bot.send_message(
            chat_id=call.message.chat.id,
            text="Извините, я вас не совсем понял.\nПодскажите пожалуйста, вы подтверждаете обновление привычки?",
            reply_markup=GenKeyboards.yes_or_no_inline(),
        )


@bot.message_handler(state=HabitUpdateStatesGroup.waiting_remind_time_hour)  # type: ignore
def waiting_update_remind_time_hour(message: Message):
    if not message.text.isdigit() or not 0 <= int(message.text) < 25:
        bot.send_message(
            chat_id=message.chat.id,
            text="Введите число! От 0 до 24.",
        )
    else:
        with bot.retrieve_data(
            user_id=message.from_user.id, chat_id=message.chat.id
        ) as data:
            data["update"]["remind_time_data"] = {"hour": int(message.text)}
        bot.send_message(
            chat_id=message.chat.id,
            text="Введите минуту когда будет приходить уведомление (от 0 до 59):",
            parse_mode="Markdown",
        )
        bot.set_state(
            user_id=message.from_user.id,
            state=HabitUpdateStatesGroup.waiting_remind_time_minute,
            chat_id=message.chat.id,
        )


@bot.message_handler(state=HabitUpdateStatesGroup.waiting_remind_time_minute)  # type: ignore
def waiting_update_remind_time_minute(message: Message):
    if not message.text.isdigit() or not 0 <= int(message.text) < 60:
        bot.send_message(
            chat_id=message.chat.id,
            text="Введите число! От 0 до 59.",
        )
    else:
        with bot.retrieve_data(
            user_id=message.from_user.id, chat_id=message.chat.id
        ) as data:
            data["update"]["remind_time_data"]["minute"] = int(message.text)
            data["update"]["remind_time"] = time(
                hour=data["update"]["remind_time_data"]["hour"],
                minute=data["update"]["remind_time_data"]["minute"],
            )
            text = VIEW_MESSAGES["check"].format(
                title=data["update"]["title"],
                description=data["update"]["description"],
                hour=data["update"]["remind_time"].hour,
                minute=data["update"]["remind_time"].minute,
            )
        if text:
            try:
                bot.send_message(
                    chat_id=message.chat.id,
                    text=f"Вот ваша обновленная привычка:\n\n{text}\n\nВсё верно?",
                    reply_markup=GenKeyboards.yes_or_no_inline(),
                    parse_mode="Markdown",
                )
                bot.set_state(
                    user_id=message.from_user.id,
                    state=HabitUpdateStatesGroup.check_habit,
                    chat_id=message.chat.id,
                )
            except ApiTelegramException:
                bot.set_state(
                    user_id=message.from_user.id,
                    state=CommandsStatesGroup.select_action,
                    chat_id=message.chat.id,
                )
                bot.send_message(
                    chat_id=message.chat.id,
                    text="Ошибка чтения привычки.\nВернуться к действиями /help",
                )


@bot.callback_query_handler(state=HabitUpdateStatesGroup.check_habit)  # type: ignore
def check_update_habit(call: CallbackQuery):
    if call.data == "yes":
        with bot.retrieve_data(
            user_id=call.from_user.id, chat_id=call.message.chat.id
        ) as data:
            habits: list[HabitSchema] = data.get("habits")
            if habits is None:
                bot.send_message(
                    chat_id=call.message.chat.id,
                    text="Что-то пошло не так. Выбрать новое действие /help.",
                )
                return
            page = data["update"]["page"]
            habit: HabitSchema = habits[page - 1]
            new_title = data["update"]["title"]
            new_description = data["update"]["description"]
            user: User = data["login"]["user"]
            remind_time: time = data["update"]["remind_time"]
            remind_time_str = remind_time.strftime("%H:%M")
        if not habit:
            bot.send_message(
                chat_id=call.message.chat.id,
                text="Что-то пошло не так. Выбрать новое действие /help.",
            )
            return
        if user:
            try:
                habit_api_controller = HabitAPIController(user=user)
                new_habit = habit_api_controller.update_habit(
                    habit_id=habit.id,  # type: ignore
                    title=new_title,
                    description=new_description,
                    remind_time=remind_time_str,
                )
                remind_telegram_controller = RemindTelegramController(
                    refresh_token=user.refresh_token
                )
                remind_telegram_controller.add_habit(
                    habit=RemindHabitSchema(**new_habit.model_dump()), update=True
                )
                data["habits"] = habit_api_controller.get_list_not_done_habits()
            except AuthenticationError:
                if update_token(user=user, chat_id=call.message.chat.id):
                    check_update_habit(call=call)
                return
            bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.id)
            bot.set_state(
                user_id=call.from_user.id,
                state=HabitStatesGroup.habits,
                chat_id=call.message.chat.id,
            )
            bot.answer_callback_query(
                callback_query_id=call.id,
                text="Привычка успешно обновлена!",
                show_alert=True,
            )
            send_habits(page=page, user_id=call.from_user.id, message=call.message)
        else:
            bot.send_message(
                chat_id=call.message.chat.id,
                text="Для начала вам необходимой авторизоваться.\nДля этого нажмите /login.",
            )
    elif call.data == "no":
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.id)
        bot.send_message(
            chat_id=call.message.chat.id,
            text="Попробовать снова?",
            reply_markup=GenKeyboards.yes_or_no_inline(),
        )
        bot.set_state(
            user_id=call.from_user.id,
            state=HabitUpdateStatesGroup.back_or_again_update,
            chat_id=call.message.chat.id,
        )
    else:
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.id)
        bot.send_message(
            chat_id=call.message.chat.id,
            text="Извините, я вас не совсем понял.\nПодскажите пожалуйста, вы подтверждаете обновление привычки?",
            reply_markup=GenKeyboards.yes_or_no_inline(),
        )


@bot.callback_query_handler(state=HabitUpdateStatesGroup.back_or_again_update)  # type: ignore
def back_or_again_update(call: CallbackQuery):
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.id)
    if call.data == "yes":
        bot.send_message(
            chat_id=call.message.chat.id,
            text="Хотите изменить заголовок?",
            reply_markup=GenKeyboards.yes_or_no_inline(),
        )
        bot.set_state(
            user_id=call.from_user.id,
            state=HabitUpdateStatesGroup.update_title,
            chat_id=call.message.chat.id,
        )
    elif call.data == "no":
        with bot.retrieve_data(
            user_id=call.from_user.id, chat_id=call.message.chat.id
        ) as data:
            page = data["update"]["page"]
            del data["update"]
        bot.set_state(
            user_id=call.from_user.id,
            state=HabitStatesGroup.habits,
            chat_id=call.message.chat.id,
        )
        send_habits(page=page, user_id=call.from_user.id, message=call.message)
    else:
        bot.send_message(
            chat_id=call.message.chat.id,
            text="Извините, я вас не совсем понял.\nПодскажите пожалуйста, вы хотите попробовать снова?",
            reply_markup=GenKeyboards.yes_or_no_inline(),
        )
