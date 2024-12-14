from datetime import datetime, time, timezone

import pytz


def get_habit_remind_time(remind_time: time) -> datetime | None:
    moscow_timezone = pytz.timezone("Europe/Moscow")
    now = datetime.now(tz=moscow_timezone)
    replace_time = now.replace(
        hour=remind_time.hour, minute=remind_time.minute, second=0, microsecond=0
    )
    return replace_time.astimezone(tz=timezone.utc) if now < replace_time else None
