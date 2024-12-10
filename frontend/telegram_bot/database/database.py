import logging
from typing import Generator
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from .models import Base

from frontend.telegram_bot.config import get_database_url

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        # logging.FileHandler('frontend.log'),
        logging.StreamHandler(),
    ]
)

logger = logging.getLogger(__name__)

DATABASE_URL = get_database_url(sync=True)

logger.info(f"DATABASE_URL: {DATABASE_URL}")

engine = create_engine(url=DATABASE_URL)
Base.metadata.create_all(engine)

SessionLocal = sessionmaker(bind=engine)


@contextmanager
def get_session() -> Generator[Session, None, None]:
    with SessionLocal() as s:
        yield s
