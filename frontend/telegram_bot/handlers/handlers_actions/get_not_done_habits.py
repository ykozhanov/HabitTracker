import logging

from telebot.types import Message, CallbackQuery, ReplyKeyboardRemove

from frontend.telegram_bot.bot import bot
from frontend.telegram_bot.bot.states import CommandsStatesGroup, HabitStatesGroup
from frontend.telegram_bot.api import HabitAPIController
from frontend.telegram_bot.schemas import HabitSchema
from frontend.telegram_bot.exceptions import AuthenticationError, HabitError
from ..utils import send_habits, get_user, update_token

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        # logging.FileHandler('frontend.log'),
        logging.StreamHandler(),
    ]
)

logger = logging.getLogger(__name__)


@bot.message_handler(func=lambda message: "📝" in message.text, state=CommandsStatesGroup.select_action)
def handler_get_not_done_habits(message: Message) -> None:
    logger.info("start handler_get_not_done_habits")
    with bot.retrieve_data(user_id=message.from_user.id, chat_id=message.chat.id) as data:
        logger.info(f"handler_get_not_done_habits data start: {data}\nuser_id: {message.from_user.id}\nchat_id: {message.chat.id}")
        user = get_user(data=data, user_id=message.from_user.id)

    logger.info(f"handler_get_not_done_habits user: {user}")
    if user:
            try:
                habit_api_controller = HabitAPIController(user=user)
                with bot.retrieve_data(user_id=message.from_user.id, chat_id=message.chat.id) as data:
                    data["habits"] = habit_api_controller.get_list_not_done_habits()
            except AuthenticationError:
                if update_token(user=user, chat_id=message.chat.id):
                    handler_get_not_done_habits(message=message)
                return
                        # data["habits"] = habit_api_controller.get_list_not_done_habits()
            with bot.retrieve_data(user_id=message.from_user.id, chat_id=message.chat.id) as data:
                habits: list[HabitSchema] = data.get("habits")
            logger.info(f"handler_get_not_done_habits data if user: {data}")
            if habits:
                logger.info("handler_get_not_done_habits yes")
                bot.set_state(
                    user_id=message.from_user.id,
                    state=HabitStatesGroup.habits,
                    chat_id=message.chat.id,
                )
                send_habits(message=message, user_id=message.from_user.id)
            else:
                logger.info("handler_get_not_done_habits no")
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


@bot.callback_query_handler(func=lambda call: call.data.split("#")[0] == "habit", state=HabitStatesGroup.habits)
def habits_callback(call: CallbackQuery) -> None:
    with bot.retrieve_data(user_id=call.from_user.id, chat_id=call.message.chat.id) as data:
        logger.info(f"habits_callback data: {data}\nuser_id: {call.from_user.id}\nchat_id: {call.message.chat.id}")
    page = int(call.data.split("#")[1])
    bot.delete_message(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
    )
    send_habits(message=call.message, page=page, user_id=call.from_user.id)
