from telebot.types import Message, CallbackQuery, InlineKeyboardButton, ReplyKeyboardRemove
from telegram_bot_pagination import InlineKeyboardPaginator

from .. import bot, CommandsStatesGroup, UserSession, HabitAPIController, HabitSchema, HabitStatesGroup, COUNT_REPEAT_HABIT, VIEW_MESSAGES


@bot.message_handler(func=lambda message: "📝" in message.text, state=CommandsStatesGroup.select_action)
def get_all_habits(message: Message):
    with bot.retrieve_data(user_id=message.from_user.id, chat_id=message.chat.id) as data:
        user: UserSession = data["login"].get("user", None)

        if user:
            habit_api_controller = HabitAPIController(user=user)
            data["habits"] = habit_api_controller.get_list_habits()
            bot.set_state(
                user_id=message.from_user.id,
                state=HabitStatesGroup.habits,
                chat_id=message.chat.id,
            )
            bot.send_message(
                chat_id=message.chat.id,
                reply_markup=ReplyKeyboardRemove(),
            )
            send_habit(message=message)
        else:
            bot.send_message(
                chat_id=message.chat.id,
                text="Для начала вам необходимой авторизоваться. Для этого нажмите /login.",
            )


@bot.callback_query_handler(func=lambda call: call.data.split("#")[0] == "habit", state=HabitStatesGroup.habits)
def habits_callback(call: CallbackQuery):
    page = int(call.message.text.split("#")[1])
    bot.delete_message(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id
    )
    send_habit(message=call.message, page=page)


def send_habit(message: Message, page: int = 1) -> None:
    with bot.retrieve_data(user_id=message.from_user.id, chat_id=message.chat.id) as data:
        habits: list[HabitSchema] = data.get("habits", [])

    paginator = InlineKeyboardPaginator(
        page_count=len(habits),
        current_page=page,
        data_pattern="habit#{page}",
    )

    paginator.add_before(
        InlineKeyboardButton(text="Удалить привычку", callback_data=f"delete#{page}"),
        InlineKeyboardButton(text="Редактировать привычку", callback_data=f"update#{page}"),
    )
    paginator.add_after(
        InlineKeyboardButton(text="Создать новую привычку", callback_data=f"create#{page}"),
    )
    habit: HabitSchema = habits[page - 1]
    text = VIEW_MESSAGES["view"].format(
        title=habit.title,
        description=habit.description,
        this_count=habit.count_repeat,
        all_count=COUNT_REPEAT_HABIT,
    )
    bot.send_message(
        chat_id=message.chat.id,
        text=text,
        reply_markup=paginator.markup,
        parse_mode="Markdown",
    )


# def get_habit_str(habit: HabitSchema) -> str:
#     return f"""
#         **Заголовок**: {habit.title}
#         **Описание**: {habit.description}
#         **Повторений**: {habit.count_repeat} из {COUNT_REPEAT_HABIT} | Осталось: {COUNT_REPEAT_HABIT - habit.count_repeat}
#     """
