import logging
from typing import Optional
from datetime import datetime, timezone

from telebot.apihelper import ApiTelegramException
from telebot.types import InlineKeyboardButton, Message
from telegram_bot_pagination import InlineKeyboardPaginator

from frontend.telegram_bot.bot import bot
from frontend.telegram_bot.schemas import HabitSchema
from frontend.telegram_bot.config import VIEW_MESSAGES, COUNT_REPEAT_HABIT
from frontend.telegram_bot.bot.states import HabitStatesGroup, CommandsStatesGroup

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        # logging.FileHandler('frontend.log'),
        logging.StreamHandler(),
    ]
)

logger = logging.getLogger(__name__)


def paginator_create(habits: list[HabitSchema], page: int, done_today: Optional[bool] = False) -> InlineKeyboardPaginator:
    paginator = InlineKeyboardPaginator(
        page_count=len(habits),
        current_page=page,
        data_pattern="habit#{page}",
    )
    button_before = [
        InlineKeyboardButton(text="Удалить", callback_data=f"delete#{page}"),
        InlineKeyboardButton(text="Редактировать", callback_data=f"update#{page}"),
    ]
    if not done_today:
        button_before.append(InlineKeyboardButton(text="Выполнена", callback_data=f"completed#{page}"))

    paginator.add_before(*button_before)
    paginator.add_after(
        InlineKeyboardButton(text="Создать новую привычку", callback_data=f"create#{page}"),
    )
    return paginator


def text_habit_create(habit: HabitSchema) -> str:
    return VIEW_MESSAGES["view"].format(
        title=habit.title,
        description=habit.description,
        this_count=habit.count_repeat,
        all_count=COUNT_REPEAT_HABIT,
        diff=COUNT_REPEAT_HABIT - habit.count_repeat,
        hour=habit.remind_time.hour,
        minute=habit.remind_time.minute,
    )

def send_habits(message: Message, user_id, page: int = 1) -> None:
    with bot.retrieve_data(user_id=user_id, chat_id=message.chat.id) as data:
        logger.info(f"send_habit - data: {data}\nuser_id: {user_id}\nchat_id: {message.chat.id}")
        habits: list[HabitSchema] = data.get("habits")

    # logger.info(f"send_habit habits: {habits}")
    # logger.info(f"send_habit page: {page}")

    habit: HabitSchema = habits[page - 1]
    text = text_habit_create(habit=habit)
    bot.set_state(
        user_id=user_id,
        state=HabitStatesGroup.habits,
        chat_id=message.chat.id,
    )
    done_today = isinstance(habit.last_time_check, datetime) and habit.last_time_check.date() == datetime.now(tz=timezone.utc).date()
    paginator = paginator_create(habits=habits, page=page, done_today=done_today)
    # logger.info(f"send_habit - habit: {habit}")
    try:
        bot.send_message(
            chat_id=message.chat.id,
            text=text,
            reply_markup=paginator.markup,
            parse_mode="Markdown",
        )
    except ApiTelegramException:
        bot.set_state(
            user_id=user_id,
            state=CommandsStatesGroup.select_action,
            chat_id=message.chat.id,
        )
        bot.send_message(
            chat_id=message.chat.id,
            text="Что-то пошло не так.\n\nВернуться к действиями /help"
        )
