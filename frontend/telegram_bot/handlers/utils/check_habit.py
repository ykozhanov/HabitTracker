from telebot.types import CallbackQuery

from frontend.telegram_bot.bot import bot
from frontend.telegram_bot.states import HabitStatesGroup
from frontend.telegram_bot.database import UserSession
from frontend.telegram_bot.controllers import HabitAPIController
from frontend.telegram_bot.keyboards import GenKeyboards


@bot.callback_query_handler(state=HabitStatesGroup.check)
def check_habit_callback(call: CallbackQuery):
    with bot.retrieve_data(user_id=call.from_user.id, chat_id=call.message.chat.id) as data:
        user: UserSession = data["login"].get("user", None)
    status = call.data.split("#")[0]
    habit_id = int(call.data.split("#")[1])

    if user:
        if status == "completed":
            habit_api_controller = HabitAPIController(user=user)
            habit_api_controller.complete_habit(habit_id=habit_id)
            bot.edit_message_text(
                text="Отлично!",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
            )

        elif status == "uncompleted":
            bot.edit_message_text(
                text="Ждем новых свершений 😊",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
            )
        else:
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                text="Что-то пошло не так, повторите пожалуйста ответ.",
                reply_markup=GenKeyboards.check_habit(habit_id=habit_id),
                message_id=call.message.message_id,
            )
    else:
        bot.send_message(
            chat_id=call.message.chat.id,
            text="Для начала вам необходимой авторизоваться. Для этого нажмите /login.",
        )
