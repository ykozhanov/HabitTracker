from datetime import datetime, timezone

from sqlalchemy import delete

from remind.database import CeleryTask, get_session


class CeleryTaskController:

    @staticmethod
    def add_new_celery_task(celery_task_id: str, user_id: int, habit_id: int) -> None:
        with get_session() as session:
            if (
                not session.query(CeleryTask)
                .filter(CeleryTask.habit_id == habit_id)
                .scalar()
            ):
                new_celery_task = CeleryTask(
                    habit_id=habit_id,
                    celery_task_id=celery_task_id,
                    user_id=user_id,
                    last_time_send_celery_task=datetime.now(tz=timezone.utc),
                )
                session.add(new_celery_task)
                session.commit()

    @staticmethod
    def get_celery_task_id(habit_id: int) -> str:
        with get_session() as session:
            celery_task_id: str = (
                session.query(CeleryTask.celery_task_id)
                .filter(CeleryTask.habit_id == habit_id)
                .scalar()
            )
            return celery_task_id

    @staticmethod
    def delete_celery_task(habit_id: int) -> None:
        with get_session() as session:
            delete_sql = delete(CeleryTask).where(CeleryTask.habit_id == habit_id)
            session.execute(delete_sql)
            session.commit()

    @staticmethod
    def get_last_time_send_celery_task(habit_id: int) -> datetime | None:
        with get_session() as session:
            last_time_send_celery_task: datetime = (
                session.query(CeleryTask.last_time_send_celery_task)
                .filter(CeleryTask.habit_id == habit_id)
                .scalar()
            )
            return last_time_send_celery_task
