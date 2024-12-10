from os import getenv
from typing import Optional

from dotenv import load_dotenv

load_dotenv()

POSTGRES_USER = getenv("POSTGRES_USER_BACKEND", "admin")
POSTGRES_PASSWORD = getenv("POSTGRES_PASSWORD_BACKEND", "admin")
POSTGRES_DB = getenv("POSTGRES_DB_BACKEND", "habit_tracker_default")

DATABASE_URL_DEFAULT = getenv(
    "DATABASE_URL_DEFAULT",
    "postgresql{SYNC}://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{HOST}:{PORT}/{POSTGRES_DB}",
)


def get_database_url(sync: Optional[bool] = False, host: Optional[str] = "db", port: Optional[int] = 5432) -> str:
    return DATABASE_URL_DEFAULT.format(
        SYNC="+psycopg2" if sync else "+asyncpg",
        POSTGRES_USER=POSTGRES_USER,
        POSTGRES_PASSWORD=POSTGRES_PASSWORD,
        HOST=host,
        PORT=port,
        POSTGRES_DB=POSTGRES_DB,
    )


JWT_PRIVATE_KEY = getenv("JWT_PRIVATE_KEY")
JWT_PUBLIC_KEY = getenv("JWT_PUBLIC_KEY")
JWT_ALGORITHM = "RS256"

ACCESS_TOKEN_EXPIRE_MINUTES = int(getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 15))
REFRESH_TOKEN_EXPIRE_DAYS = int(getenv("REFRESH_TOKEN_EXPIRE_DAYS", 30))
COUNT_REPEAT_HABIT = int(getenv("COUNT_REPEAT_HABIT", 21))

