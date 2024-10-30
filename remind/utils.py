from datetime import datetime, timedelta


def get_execution_time(hour: int, minute: int) -> datetime:
    now = datetime.now()
    tomorrow = now + timedelta(days=1)
    return tomorrow.replace(hour=hour, minute=minute)
