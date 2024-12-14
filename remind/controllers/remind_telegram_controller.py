from datetime import datetime, timezone
from typing import Optional

from celery.result import AsyncResult

from remind.database import User, UserInfoTelegram
from remind.database.controllers import (
    CeleryTaskController,
    UserController,
    UserInfoTelegramController,
)
from remind.schemas import RemindHabitSchema
from remind.telegram_bot.celery_telegram import CeleryTelegramBotController

from .utils import get_habit_remind_time


class RemindTelegramController:

    def __init__(
        self,
        refresh_token: str,
    ):
        self._refresh_token = refresh_token

    def add_user(self, chat_id: int, user_id: int, bot_token: str) -> None:
        user_controller = UserController(refresh_token=self._refresh_token)
        new_user = user_controller.add_user()
        user_info_telegram_info = UserInfoTelegramController(user=new_user)
        user_info_telegram_info.add_user_info_telegram(
            chat_id_telegram=chat_id, user_id_telegram=user_id, bot_token=bot_token
        )

    def delete_user(self) -> None:
        user_controller = UserController(refresh_token=self._refresh_token)
        user_controller.delete_user()

    def update_refresh_token(self, new_refresh_token: str) -> None:
        user_controller = UserController(refresh_token=self._refresh_token)
        user_controller.update_refresh_token(new_refresh_token=new_refresh_token)

    def add_habit(
        self, habit: RemindHabitSchema, update: Optional[bool] = False
    ) -> None:
        remind_time: datetime | None = get_habit_remind_time(remind_time=habit.remind_time)  # type: ignore
        if remind_time and datetime.now(tz=timezone.utc) < remind_time:
            celery_task_database_controller = CeleryTaskController()
            if update:
                celery_task_id = celery_task_database_controller.get_celery_task_id(
                    habit_id=habit.id  # type: ignore
                )
                CeleryTelegramBotController.revoke_task_by_id(
                    celery_task_id=celery_task_id
                )
                celery_task_database_controller.delete_celery_task(habit_id=habit.id)  # type: ignore
            user_controller = UserController(refresh_token=self._refresh_token)
            user: User = user_controller.get_user()
            user_info: UserInfoTelegram = user.user_info_telegram
            celery_task: AsyncResult = (
                CeleryTelegramBotController.add_new_remind.apply_async(
                    kwargs={
                        "bot_token": user_info.telegram_bot_token,
                        "chat_id": user_info.chat_id_telegram,
                        "habit_dict": habit.model_dump(),
                    },
                    eta=remind_time,
                )
            )
            celery_task_database_controller.add_new_celery_task(
                celery_task_id=celery_task.id, user_id=user.id, habit_id=habit.id  # type: ignore
            )
