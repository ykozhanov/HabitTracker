from telebot.types import CallbackQuery, Message, ReplyKeyboardRemove

from frontend.telegram_bot.api import HabitAPIController
from frontend.telegram_bot.bot import bot
from frontend.telegram_bot.bot.states import CommandsStatesGroup, HabitStatesGroup
from frontend.telegram_bot.exceptions import AuthenticationError
from frontend.telegram_bot.schemas import HabitSchema

from ..utils import get_user, send_habits, update_token


@bot.message_handler(
    func=lambda message: "📝" in message.text,
    state=[CommandsStatesGroup.select_action, HabitStatesGroup.habits],
)  # type: ignore
def handler_get_not_done_habits(message: Message) -> None:
    with bot.retrieve_data(
        user_id=message.from_user.id, chat_id=message.chat.id
    ) as data:
        user = get_user(data=data, user_id=message.from_user.id)
    if user:
        with bot.retrieve_data(
            user_id=message.from_user.id, chat_id=message.chat.id
        ) as data:
            try:
                habit_api_controller = HabitAPIController(user=user)
                data["habits"] = habit_api_controller.get_list_not_done_habits()
            except AuthenticationError:
                if update_token(user=user, chat_id=message.chat.id):
                    data["habits"] = habit_api_controller.get_list_not_done_habits()
                else:
                    return
        with bot.retrieve_data(
            user_id=message.from_user.id, chat_id=message.chat.id
        ) as data:
            habits: list[HabitSchema] = data.get("habits")
        if habits:
            bot.set_state(
                user_id=message.from_user.id,
                state=HabitStatesGroup.habits,
                chat_id=message.chat.id,
            )
            send_habits(message=message, user_id=message.from_user.id)
        else:
            bot.send_message(
                chat_id=message.chat.id,
                text="Привычек пока нет.\n\nВыбрать новое действие /help",
                reply_markup=ReplyKeyboardRemove(),
            )
            bot.set_state(
                user_id=message.from_user.id,
                state=CommandsStatesGroup.select_action,
                chat_id=message.chat.id,
            )
    else:
        bot.send_message(
            chat_id=message.chat.id,
            text="Для начала вам необходимой авторизоваться.\nДля этого нажмите /login.",
        )


@bot.callback_query_handler(
    func=lambda call: call.data.split("#")[0] == "habit", state=HabitStatesGroup.habits
)  # type: ignore
def habits_callback(call: CallbackQuery) -> None:
    page = int(call.data.split("#")[1])
    bot.delete_message(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
    )
    send_habits(message=call.message, page=page, user_id=call.from_user.id)
