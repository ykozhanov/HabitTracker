from typing import Any
from datetime import time, datetime, timedelta

import telebot
import requests
from celery import Celery
from celery.schedules import crontab

from .states import RemindStatesGroup
from .keyboards import GenRemindKeyboards
from remind.schemas import RemindHabitSchema
from remind.database.controllers import CeleryTaskController, UserController
from remind.database.models import User
from remind.config import URL_BACKEND

celery = Celery(
    main="celery_telegram_bot_controller",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0",
)


def get_execution_time(habit: RemindHabitSchema) -> datetime:
    now = datetime.now()
    if not habit.last_time_check and habit.remind_time > now.time():
        return now.replace(hour=habit.remind_time.hour, minute=habit.remind_time.minute)
    if habit.last_time_check.date() >= now.date():
        tomorrow = now + timedelta(days=1)
        return tomorrow.replace(hour=habit.remind_time.hour, minute=habit.remind_time.minute)
    return now.replace(hour=habit.remind_time.hour, minute=habit.remind_time.minute)


class CeleryTelegramBotController:

    @staticmethod
    @celery.task
    def add_new_remind(bot_token: str, chat_id: int, user_id: int, habit_dict: dict[str, Any]):
        habit = RemindHabitSchema.model_validate(habit_dict)
        bot = telebot.TeleBot(bot_token)
        bot.send_message(
            chat_id=chat_id,
            text=f"Просто напомним вам про привычку {habit.title!r} 👉👈",
            reply_markup=GenRemindKeyboards.check_habit(habit_id=habit.id),
        )
        bot.set_state(
            user_id=user_id,
            state=RemindStatesGroup.check,
            chat_id=chat_id,
        )

    @staticmethod
    def revoke_task_by_id(celery_task_id: str):
        celery.control.revoke(celery_task_id, terminate=True)  # terminate=True завершает задачу, если она уже выполняется


urls = {
    "habits": "/habits/",
}


@celery.task
def send_all_remind():
    celery_task_controller = CeleryTaskController()
    users: list[User] = UserController.get_all_users()
    url = URL_BACKEND + urls["habits"]
    for i_user in users:
        user_info = i_user.user_info_telegram
        headers = {
            "Authorization": f"Bearer {i_user.user_token}",
        }
        response = requests.get(url=url, headers=headers, timeout=60)
        habits: list[RemindHabitSchema] = [RemindHabitSchema.model_validate(habit) for habit in response.json()]
        for habit in habits:
            execution_time = get_execution_time(habit=habit)
            celery_task = CeleryTelegramBotController.add_new_remind.apply_async(
                kwargs={
                    "bot_token": user_info.telegram_bot_token,
                    "chat_id": user_info.chat_id_telegram,
                    "user_id": user_info.user_id_telegram,
                    "habit": habit,
                },
                eta=execution_time,
            )
            last_time_send_celery_task = celery_task_controller.get_last_time_send_celery_task(habit_id=habit.id)
            if last_time_send_celery_task and datetime.now() > last_time_send_celery_task:
                CeleryTelegramBotController.revoke_task_by_id(celery_task_controller.get_celery_task_id(habit_id=habit.id))
                celery_task_controller.add_new_celery_task(celery_task_id=celery_task.id, user_id=i_user.id, habit_id=habit.id)


    celery.conf.beat_schedule = {
        'send-notification-every-day': {
            'task': 'send_all_remind',
            'schedule': crontab(hour="23", minute="30"),
        },
    }
