from telebot.types import CallbackQuery

from frontend.telegram_bot.api import HabitAPIController
from frontend.telegram_bot.bot import bot
from frontend.telegram_bot.bot.states import HabitStatesGroup
from frontend.telegram_bot.exceptions import AuthenticationError
from frontend.telegram_bot.schemas import HabitSchema

from ..utils import get_user, send_habits, update_token


@bot.callback_query_handler(func=lambda call: call.data.split("#")[0] == "remind")  # type: ignore
def check_habit_callback(call: CallbackQuery):
    with bot.retrieve_data(
        user_id=call.from_user.id, chat_id=call.message.chat.id
    ) as data:
        user = get_user(data=data, user_id=call.from_user.id)
    status = call.data.split("#")[1]
    habit_id = int(call.data.split("#")[2])
    if user:
        if status == "completed":
            habit_api_controller = HabitAPIController(user=user)
            habit_api_controller.complete_habit(habit_id=habit_id)
            bot.edit_message_text(
                text="Отлично!",
                chat_id=call.message.chat.id,
                message_id=call.message.id,
            )

        elif status == "uncompleted":
            bot.edit_message_text(
                text="Ждем новых свершений! 😊",
                chat_id=call.message.chat.id,
                message_id=call.message.id,
            )
    else:
        bot.send_message(
            chat_id=call.message.chat.id,
            text="Для начала вам необходимой авторизоваться. Для этого нажмите /login.",
        )


@bot.callback_query_handler(
    func=lambda call: call.data.split("#")[0] == "completed",
    state=HabitStatesGroup.habits,
)  # type: ignore
def check_habit_callback_from_list_not_done(call: CallbackQuery):
    with bot.retrieve_data(
        user_id=call.from_user.id, chat_id=call.message.chat.id
    ) as data:
        user = get_user(data=data, user_id=call.from_user.id)
        habits: list[HabitSchema] = data.get("habits")
    if habits is None:
        bot.send_message(
            chat_id=call.message.chat.id,
            text="Что-то пошло не так. Выбрать новое действие /help.",
        )
        return
    page = int(call.data.split("#")[1])
    if not (habit_id := habits[page - 1].id):
        bot.send_message(
            chat_id=call.message.chat.id,
            text="Что-то пошло не так. Выбрать новое действие /help.",
        )
        return
    if user:
        try:
            habit_api_controller = HabitAPIController(user=user)
            habit_api_controller.complete_habit(habit_id=habit_id)
            with bot.retrieve_data(
                user_id=call.from_user.id, chat_id=call.message.chat.id
            ) as data:
                data["habits"] = habit_api_controller.get_list_not_done_habits()
            send_habits(page=page, user_id=call.from_user.id, message=call.message)
        except AuthenticationError:
            if update_token(user=user, chat_id=call.message.chat.id):
                check_habit_callback_from_list_not_done(call=call)
            return
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.id)
    else:
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.id)
        bot.send_message(
            chat_id=call.message.chat.id,
            text="Для начала вам необходимой авторизоваться. Для этого нажмите /login.",
        )
