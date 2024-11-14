from datetime import datetime
from typing import Optional

from celery.result import AsyncResult

from remind.database import User
from remind.database.controllers import UserController, UserInfoTelegramController, CeleryTaskController
from remind.telegram_bot.celery_telegram import CeleryTelegramBotController
from remind.schemas import RemindHabitSchema
from .utils import get_habit_remind_time


class RemindTelegramController:

    def __init__(self, user_token: str, ):
        self._user_token = user_token

    def add_user(self, chat_id: int, user_id: int, bot_token: str) -> None:
        user_controller = UserController(user_token=self._user_token)
        new_user = user_controller.add_user()
        user_info_telegram_info = UserInfoTelegramController(user=new_user)
        user_info_telegram_info.add_user_info_telegram(chat_id_telegram=chat_id, user_id_telegram=user_id, bot_token=bot_token)

    def update_user_token(self, new_user_token: str) -> None:
        user_controller = UserController(user_token=self._user_token)
        user_controller.update_user_token(new_user_token=new_user_token)
    #
    # def _add_new_remind(self, habit: RemindHabitSchema) -> AsyncResult:
    #     user_controller = UserController(user_token=self._user_token)
    #     user: User = user_controller.get_user()
    #     user_info = user.user_info_telegram
    #     return CeleryTelegramBotController.add_new_remind.apply_async(
    #         kwargs={
    #         "bot_token": user_info.telegram_bot_token,
    #         "chat_id": user_info.chat_id_telegram,
    #         "user_id": user_info.user_id_telegram,
    #         "habit_dict": habit.model_dump(),
    #         },
    #         eta=get_habit_remind_time(habit.remind_time, ),
    #     )

    def add_habit(self, habit: RemindHabitSchema, update: Optional[bool] = False) -> None:
        if datetime.now() < get_habit_remind_time(habit.remind_time):
            user_controller = UserController(user_token=self._user_token)
            user: User = user_controller.get_user()
            user_info = user.user_info_telegram
            celery_task: AsyncResult = CeleryTelegramBotController.add_new_remind.apply_async(
                kwargs={
                    "bot_token": user_info.telegram_bot_token,
                    "chat_id": user_info.chat_id_telegram,
                    "user_id": user_info.user_id_telegram,
                    "habit_dict": habit.model_dump(),
                },
                eta=get_habit_remind_time(habit.remind_time, ),
            )
            if update:
                celery_task_database_controller = CeleryTaskController()
                celery_task_id = celery_task_database_controller.get_celery_task_id(habit_id=habit.id)
                CeleryTelegramBotController.revoke_task_by_id(celery_task_id=celery_task_id)
                celery_task_database_controller.update_celery_task_id(habit_id=habit.id, new_celery_task_id=celery_task.id)

    # def add_new_habit(self, habit: RemindHabitSchema) -> None:
    #     self._add_new_remind(habit=habit)
        # user_controller = UserController(user_token=self._user_token)
        # user: User = user_controller.get_user()
        # user_info = user.user_info_telegram
        # CeleryTelegramBotController.add_new_remind.apply_async(
        #     kwargs={
        #         "bot_token": user_info.telegram_bot_token,
        #         "chat_id": user_info.chat_id_telegram,
        #         "user_id": user_info.user_id_telegram,
        #         "habit_dict": habit.model_dump(),
        #     })
