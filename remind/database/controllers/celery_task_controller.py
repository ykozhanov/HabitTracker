from datetime import datetime

from sqlalchemy import update

from remind.database import get_session, CeleryTask


class CeleryTaskController:

    @staticmethod
    def add_new_celery_task(celery_task_id: str, user_id: int, habit_id: int) -> None:
        with get_session() as session:
            if not session.query(CeleryTask).filter(CeleryTask.habit_id == habit_id).scalar():
                new_celery_task = CeleryTask(habit_id=habit_id, celery_task_id=celery_task_id, user_id=user_id, last_time_send_celery_task=datetime.now())
                session.add(new_celery_task)
                session.commit()

    @staticmethod
    def get_celery_task_id(habit_id: int) -> str | None:
        with get_session() as session:
            return session.query(CeleryTask).filter(CeleryTask.habit_id == habit_id).scalar()

    @staticmethod
    def update_celery_task_id(new_celery_task_id: str, habit_id: int) -> None:
        with get_session() as session:
            update_sql = update(CeleryTask).where(CeleryTask.habit_id == habit_id).values(celery_task_id=new_celery_task_id, last_time_send_celery_task=datetime.now())
            session.execute(update_sql)
            session.commit()

    @staticmethod
    def get_last_time_send_celery_task(habit_id: int) -> datetime:
        with get_session() as session:
            return session.query(CeleryTask.last_time_send_celery_task).filter(CeleryTask.habit_id == habit_id).scalar()
