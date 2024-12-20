from telebot.types import CallbackQuery, ReplyKeyboardRemove

from frontend.telegram_bot.api import HabitAPIController
from frontend.telegram_bot.bot import bot
from frontend.telegram_bot.bot.states import CommandsStatesGroup, HabitStatesGroup
from frontend.telegram_bot.exceptions import AuthenticationError
from frontend.telegram_bot.schemas import HabitSchema

from ..utils import get_user, send_habits, update_token


@bot.callback_query_handler(
    func=lambda call: call.data.split("#")[0] == "delete", state=HabitStatesGroup.habits
)  # type: ignore
def delete_habit_callback(call: CallbackQuery):
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
    habit_id = habits[page - 1].id
    if not habit_id:
        bot.send_message(
            chat_id=call.message.chat.id,
            text="Что-то пошло не так. Выбрать новое действие /help.",
        )
        return
    if user:
        try:
            habit_api_controller = HabitAPIController(user=user)
            habit_api_controller.delete_habit(habit_id=habit_id)
            with bot.retrieve_data(
                user_id=call.from_user.id, chat_id=call.message.chat.id
            ) as data:
                data["habits"] = habit_api_controller.get_list_not_done_habits()
        except AuthenticationError:
            if update_token(user=user, chat_id=call.message.chat.id):
                delete_habit_callback(call=call)
            return
        bot.delete_message(
            chat_id=call.message.chat.id, message_id=call.message.message_id
        )
        if len(data.get("habits")) > 0:
            send_habits(page=page - 1, user_id=call.from_user.id, message=call.message)
        else:
            bot.send_message(
                chat_id=call.message.chat.id,
                text="Привычек пока нет.\nВыбрать новое действие /help",
                reply_markup=ReplyKeyboardRemove(),
            )
            bot.set_state(
                user_id=call.message.from_user.id,
                state=CommandsStatesGroup.select_action,
                chat_id=call.message.chat.id,
            )
    else:
        bot.send_message(
            chat_id=call.message.chat.id,
            text="Для начала вам необходимой авторизоваться. Для этого нажмите /login.",
        )
