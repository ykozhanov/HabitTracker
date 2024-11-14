import logging

from telebot.types import Message, CallbackQuery, ReplyKeyboardRemove

from frontend.telegram_bot.bot import bot
from frontend.telegram_bot.bot.states import CommandsStatesGroup, HabitStatesGroup
from frontend.telegram_bot.api import HabitAPIController
from frontend.telegram_bot.schemas import HabitSchema
from frontend.telegram_bot.exceptions import LoginError, HabitError
from ..utils import send_habit, get_user, update_token

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
        logger.info(f"handler_get_not_done_habits data: {data}")
        user = get_user(data=data, user_id=message.from_user.id)

    logger.info(f"handler_get_not_done_habits user: {user}")
    if user:
        try:
            habit_api_controller = HabitAPIController(user=user)
            with bot.retrieve_data(user_id=message.from_user.id, chat_id=message.chat.id) as data:
                data["habits"] = habit_api_controller.get_list_not_done_habits()
                habits: list[HabitSchema] = data.get("habits", None)
            # logger.info(f"habits: {habits}")
            if habits:
                # bot.set_state(
                #     user_id=message.from_user.id,
                #     state=HabitStatesGroup.habits,
                #     chat_id=message.chat.id,
                # )
                send_habit(message=message, user_id=message.from_user.id)
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
        except LoginError:
            logger.info("LoginError")
            update_token(user=user, chat_id=message.chat.id)
        except HabitError as exc:
            logger.info("HabitError")
            # detail = str(exc.detail).replace("_", "\\_").replace("*", "\\*") if exc.detail else "Что-то пошло не так."
            bot.send_message(
                chat_id=message.chat.id,
                text=f"Ошибка:\n\n{exc.detail if exc.detail else "Что-то пошло не так."}\n\nВернуться в меню действий /help",
                # parse_mode="Markdown",
            )
        # except Exception as exc:
        #     logger.info("Exception")
        #     # detail = str(exc).replace("_", "\\_").replace("*", "\\*") if exc else "Что-то пошло не так."
        #     bot.send_message(
        #         chat_id=message.chat.id,
        #         text=f"Ошибка:\n\n{exc if exc else "Что-то пошло не так."}.\n\nВернуться в меню действий /help",
        #         # parse_mode="Markdown",
        #     )
    else:
        bot.send_message(
            chat_id=message.chat.id,
            text="Для начала вам необходимой авторизоваться.\nДля этого нажмите /login.",
        )


@bot.callback_query_handler(func=lambda call: call.data.split("#")[0] == "habit", state=HabitStatesGroup.habits)
def habits_callback(call: CallbackQuery) -> None:
    # logger.info(f"habits_callback text: {call.message.text}")
    page = int(call.data.split("#")[1])
    bot.delete_message(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
    )
    send_habit(message=call.message, page=page, user_id=call.from_user.id)
