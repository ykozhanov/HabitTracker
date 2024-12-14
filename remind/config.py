from os import getenv
from typing import Optional

from dotenv import load_dotenv

load_dotenv()

POSTGRES_USER = getenv("POSTGRES_USER_REMIND", "admin")
POSTGRES_PASSWORD = getenv("POSTGRES_PASSWORD_REMIND", "admin")
POSTGRES_DB = getenv("POSTGRES_DB_REMIND", "remind_default")

DATABASE_URL_DEFAULT = getenv(
    "DATABASE_URL_DEFAULT",
    "postgresql{SYNC}://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{HOST}:{PORT}/{POSTGRES_DB}",
)


def get_database_url(
    sync: Optional[bool] = False,
    host: Optional[str] = "db_remind",
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


URL_BACKEND = getenv("URL_BACKEND", "http://backend:8000/api")
