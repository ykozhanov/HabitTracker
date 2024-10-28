from telebot.types import CallbackQuery, Message

from .. import bot, UserSession, HabitAPIController, HabitSchema, HabitStatesGroup, HabitError, TimeOutError, GenKeyboards, LoginError, HabitUpdateStatesGroup, VIEW_MESSAGES
from ..actions.get_all_habits import send_habit


@bot.callback_query_handler(func=lambda call: call.data.split("#")[0] == "update", state=HabitStatesGroup.habits)
def update_habit_callback(call: CallbackQuery):
    with bot.retrieve_data(user_id=call.from_user.id, chat_id=call.message.chat.id) as data:
        user: UserSession = data["login"].get("user", None)
        data["update"]["page"] = int(call.message.text.split("#")[1])

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
            text="Для начала вам необходимой авторизоваться. Для этого нажмите /login.",
        )


@bot.callback_query_handler(state=HabitUpdateStatesGroup.update_title)
def update_title_callback(call: CallbackQuery):
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
        with bot.retrieve_data(user_id=call.from_user.id, chat_id=call.message.chat.id) as data:
            habits: list[HabitSchema] = data.get("habits", [])
            habit: HabitSchema = habits[data["update"]["page"]]
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
            text="Извините, я вас не совсем понял. Подскажите пожалуйста, вы хотите изменить заголовок?",
            reply_markup=GenKeyboards.yes_or_no_inline(),
        )


@bot.message_handler(state=HabitUpdateStatesGroup.waiting_title)
def waiting_updated_title(message: Message):
    with bot.retrieve_data(user_id=message.from_user.id, chat_id=message.chat.id) as data:
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


@bot.callback_query_handler(state=HabitUpdateStatesGroup.update_description)
def update_description_callback(call: CallbackQuery):
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
        with bot.retrieve_data(user_id=call.from_user.id, chat_id=call.message.chat.id) as data:
            habits: list[HabitSchema] = data.get("habits", [])
            habit: HabitSchema = habits[data["update"]["page"]]
            data["update"]["description"] = habit.description
            text = f"""
            **Заголовок**: {data["update"]["title"]}
            **Описание**: {data["update"]["description"]}
            """
        bot.send_message(
            chat_id=call.message.chat.id,
            text=f"Вот ваша обновленная привычка:\n{text}\nВсё верно?",
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
            text="Извините, я вас не совсем понял. Подскажите пожалуйста, вы хотите изменить описание?",
            reply_markup=GenKeyboards.yes_or_no_inline(),
        )


@bot.message_handler(state=HabitUpdateStatesGroup.waiting_description)
def waiting_updated_description(message: Message):
    with bot.retrieve_data(user_id=message.from_user.id, chat_id=message.chat.id) as data:
        data["update"]["description"] = message.text
        text = VIEW_MESSAGES["check"].format(
            title=data["update"]["title"] ,
            description=message.text,
        )
    bot.send_message(
        chat_id=message.chat.id,
        text=f"Вот ваша обновленная привычка:\n{text}\nВсё верно?",
        reply_markup=GenKeyboards.yes_or_no_inline(),
        parse_mode="Markdown",
    )
    bot.set_state(
        user_id=message.from_user.id,
        state=HabitUpdateStatesGroup.check_habit,
        chat_id=message.chat.id,
    )


@bot.callback_query_handler(state=HabitUpdateStatesGroup.check_habit)
def check_update_habit(call: CallbackQuery):
    if call.data == "yes":
        with bot.retrieve_data(user_id=call.from_user.id, chat_id=call.message.chat.id) as data:
            user: UserSession = data["login"].get("user", None)

        if user:
            habits: list[HabitSchema] = data.get("habits", [])
            page = data["update"]["page"]
            habit: HabitSchema = habits[page]
            new_title = data["update"]["title"]
            new_description = data["update"]["description"]
            del data["update"]
            habit_api_controller = HabitAPIController(user=user)

            try:
                habit_api_controller.update_habit(habit_id=habit.id, title=new_title, description=new_description)
                bot.delete_message(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id
                )
                data["habits"] = habit_api_controller.get_list_habits()
                bot.set_state(
                    user_id=call.from_user.id,
                    state=HabitStatesGroup.habits,
                    chat_id=call.message.chat.id,
                )
                send_habit(message=call.message, page=page - 1)
            except (HabitError, TimeOutError) as exc:
                bot.send_message(
                    chat_id=call.message.chat.id,
                    text=f"Что-то пошло не так. {exc.detail}",
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
                text="Для начала вам необходимой авторизоваться. Для этого нажмите /login.",
            )
    elif call.data == "no":
        bot.send_message(
            chat_id=call.message.chat.id,
            text=f"Попробовать снова?",
            reply_markup=GenKeyboards.yes_or_no_inline(),
        )
        bot.set_state(
            user_id=call.from_user.id,
            state=HabitUpdateStatesGroup.back_or_again_update,
            chat_id=call.message.chat.id,
        )
    else:
        bot.send_message(
            chat_id=call.message.chat.id,
            text="Извините, я вас не совсем понял. Подскажите пожалуйста, вы подтверждаете обновление привычки?",
            reply_markup=GenKeyboards.yes_or_no_inline(),
        )


@bot.callback_query_handler(state=HabitUpdateStatesGroup.back_or_again_update)
def back_or_again_update(call: CallbackQuery):
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
        with bot.retrieve_data(user_id=call.from_user.id, chat_id=call.message.chat.id) as data:
            page = data["update"]["page"]
            del data["update"]
        bot.set_state(
            user_id=call.from_user.id,
            state=HabitStatesGroup.habits,
            chat_id=call.message.chat.id,
        )
        send_habit(message=call.message, page=page - 1)
    else:
        bot.send_message(
            chat_id=call.message.chat.id,
            text="Извините, я вас не совсем понял. Подскажите пожалуйста, вы хотите попробовать снова?",
            reply_markup=GenKeyboards.yes_or_no_inline(),
        )
