from datetime import datetime, time, timezone
from typing import Optional

from telebot.apihelper import ApiTelegramException
from telebot.types import InlineKeyboardButton, Message
from telegram_bot_pagination import InlineKeyboardPaginator

from frontend.telegram_bot.bot import bot
from frontend.telegram_bot.bot.states import CommandsStatesGroup, HabitStatesGroup
from frontend.telegram_bot.config import COUNT_REPEAT_HABIT, VIEW_MESSAGES
from frontend.telegram_bot.schemas import HabitSchema


def paginator_create(
    habits: list[HabitSchema], page: int, done_today: Optional[bool] = False
) -> InlineKeyboardPaginator:
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
        button_before.append(
            InlineKeyboardButton(text="Выполнена", callback_data=f"completed#{page}")
        )

    paginator.add_before(*button_before)
    paginator.add_after(
        InlineKeyboardButton(
            text="Создать новую привычку", callback_data=f"create#{page}"
        ),
    )
    return paginator


def text_habit_create(habit: HabitSchema) -> str:
    return VIEW_MESSAGES["view"].format(
        title=habit.title,
        description=habit.description,
        this_count=habit.count_repeat,
        all_count=COUNT_REPEAT_HABIT,
        diff=(
            COUNT_REPEAT_HABIT - habit.count_repeat
            if habit.count_repeat
            else COUNT_REPEAT_HABIT - 0
        ),
        hour=habit.remind_time.hour if isinstance(habit.remind_time, time) else 0,
        minute=habit.remind_time.minute if isinstance(habit.remind_time, time) else 0,
    )


def send_habits(message: Message, user_id: int, page: int = 1) -> None:
    with bot.retrieve_data(user_id=user_id, chat_id=message.chat.id) as data:
        habits: list[HabitSchema] = data.get("habits")
    habit: HabitSchema = habits[page - 1]
    text = text_habit_create(habit=habit)
    bot.set_state(
        user_id=user_id,
        state=HabitStatesGroup.habits,
        chat_id=message.chat.id,
    )
    done_today = (
        isinstance(habit.last_time_check, datetime)
        and habit.last_time_check.date() == datetime.now(tz=timezone.utc).date()
    )
    paginator = paginator_create(habits=habits, page=page, done_today=done_today)
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
            text="Что-то пошло не так.\n\nВернуться к действиями /help",
        )
