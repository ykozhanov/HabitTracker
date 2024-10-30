from datetime import time

import telebot
from celery import Celery
from celery.schedules import crontab

from backend import HabitSchema, get_session, HabitTrackerTelegram, User
from frontend.telegram_bot import HabitStatesGroup, GenKeyboards, BOT_TOKEN

from utils import get_execution_time
from database import CeleryDatabaseController

celery = Celery(
    main="celery_telegram_bot_controller",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
)


class CeleryTelegramBotController:
    with get_session() as s:
        _session = s

    @staticmethod
    @celery.task
    def send_reminder_telegram_bot(chat_id: int, user_id: int, habit: HabitSchema):
        bot = telebot.TeleBot(BOT_TOKEN)
        bot.send_message(
            chat_id=chat_id,
            text=f"Просто напомним вам про привычку {habit.title!r} 👉👈",
            reply_markup=GenKeyboards.check_habit(habit_id=habit.id),
        )
        bot.set_state(
            user_id=user_id,
            state=HabitStatesGroup.check,
            chat_id=chat_id,
        )

    @staticmethod
    def revoke_task_by_id(celery_task_id: str):
        celery.control.revoke(celery_task_id, terminate=True)  # terminate=True завершает задачу, если она уже выполняется

    @celery.task
    async def send_all_remind(self):
        users: list[User] = CeleryDatabaseController.get_all_user()
        for i_user in users:
            for i_habit in i_user.habits:
                habit_tracker: HabitTrackerTelegram = i_habit.habit_tracker_telegram
                remind_time: time = habit_tracker.remind_time
                execution_time = get_execution_time(hour=remind_time.hour, minute=remind_time.minute)
                new_celery_task = CeleryTelegramBotController.send_reminder_telegram_bot.apply_async(
                    {"chat_id": habit_tracker.chat_id, "habit": i_habit, "user_id": habit_tracker.user_id},
                    eta=execution_time)
                CeleryDatabaseController.add_new_habit_celery(habit_id=i_habit.id, celery_task_id=new_celery_task.id)


celery.conf.beat_schedule = {
    'send-notification-every-day': {
        'task': 'celery_telegram_bot_controller.CeleryTelegramBotController.send_all_remind',
        'schedule': crontab(hour="23", minute="50"),
    },
}
