from os import getenv
from typing import Optional

from dotenv import load_dotenv

load_dotenv()

POSTGRES_USER = getenv("POSTGRES_USER", "admin")
POSTGRES_PASSWORD = getenv("POSTGRES_PASSWORD", "admin")
POSTGRES_DB = getenv("POSTGRES_DB", "habit_tracker_default")

DATABASE_URL_DEFAULT = getenv(
    "DATABASE_URL_DEFAULT",
    "postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{HOST}:5432/{POSTGRES_DB}",
)


def get_database_url(host: Optional[str] = "db") -> str:
    return DATABASE_URL_DEFAULT.format(
        POSTGRES_USER=POSTGRES_USER,
        POSTGRES_PASSWORD=POSTGRES_PASSWORD,
        HOST=host,
        POSTGRES_DB=POSTGRES_DB,
    )


JWT_SECRET_KEY = getenv("JWT_SECRET_KEY", "JWT_SECRET_KEY")
JWT_ALGORITHM = getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 15))
REFRESH_TOKEN_EXPIRE_DAYS = int(getenv("REFRESH_TOKEN_EXPIRE_DAYS", 30))

COUNT_REPEAT_HABIT = int(getenv("COUNT_REPEAT_HABIT", 21))