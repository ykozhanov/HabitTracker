from os import getenv

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = getenv("BOT_TOKEN", None)
URL_FOR_FRONTEND = getenv("URL_FOR_FRONTEND=", "http://localhost:8000/api")
COUNT_REPEAT_HABIT = int(getenv("COUNT_REPEAT_HABIT", 21))

VIEW_MESSAGES = {
    "view": """
        **Заголовок**: {title}
        **Описание**: {description}
        **Повторений**: {this_count} из {all_count} | Осталось: {this_count - all_count}
        **Напоминание**: в {hour} часов {minute} минут
    """,
    "check": """
        **Заголовок**: {title}
        **Описание**: {description}
        **Напоминание**: в {hour} часов {minute} минут
        """
}