from os import getenv
from typing import Optional

from dotenv import load_dotenv

from .exceptions import EnvError

load_dotenv()

POSTGRES_USER = getenv("POSTGRES_USER_FRONTEND", "admin")
POSTGRES_PASSWORD = getenv("POSTGRES_PASSWORD_FRONTEND", "admin")
POSTGRES_DB = getenv("POSTGRES_DB_FRONTEND", "habit_tracker_default")

DATABASE_URL_DEFAULT = getenv(
    "DATABASE_URL_DEFAULT",
    "postgresql{SYNC}://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{HOST}:{PORT}/{POSTGRES_DB}",
)


def get_database_url(
    sync: Optional[bool] = False,
    host: Optional[str] = "db_frontend",
    port: Optional[int] = 5432,
) -> str:
    return DATABASE_URL_DEFAULT.format(
        SYNC="+psycopg2" if sync else "+asyncpg",
        POSTGRES_USER=POSTGRES_USER,
        POSTGRES_PASSWORD=POSTGRES_PASSWORD,
        HOST=host,
        PORT=port,
        POSTGRES_DB=POSTGRES_DB,
    )


BOT_TOKEN = getenv("BOT_TOKEN")
if BOT_TOKEN is None:
    raise EnvError("Проверьте переменную окружения: 'BOT_TOKEN'")

URL_BACKEND = getenv("URL_BACKEND", "http://localhost:8000/api")
COUNT_REPEAT_HABIT = int(getenv("COUNT_REPEAT_HABIT", 21))


VIEW_MESSAGES = {
    "view": "*Заголовок*: {title}\n*Описание*: {description}\n*Повторений*: {this_count} из {all_count} | Осталось: {diff}\n*Напоминание*: в {hour} часов {minute} минут",
    "check": "*Заголовок*: {title}\n*Описание*: {description}\n*Напоминание*: в {hour} часов {minute} минут",
    "user": "*Логин*: {username}\n*E-mail*: {email}",
}
