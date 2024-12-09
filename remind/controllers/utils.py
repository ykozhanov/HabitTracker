from datetime import time, datetime, timezone


def get_habit_remind_time(remind_time: time) -> datetime | None:
    now = datetime.now(tz=timezone.utc)
    replace_time = now.replace(hour=remind_time.hour, minute=remind_time.minute)
    return now.replace(hour=remind_time.hour, minute=remind_time.minute) if now < replace_time else None

