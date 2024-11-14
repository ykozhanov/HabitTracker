from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


class GenRemindKeyboards:

    def __init__(self):
        pass

    @staticmethod
    def check_habit(habit_id: int) -> InlineKeyboardMarkup:
        buttons = [
            InlineKeyboardButton(text="Уже выполнил", callback_data=f"completed#{habit_id}"),
            InlineKeyboardButton(text="Еще не выполнил", callback_data=f"uncompleted#{habit_id}"),
        ]
        keyboard = InlineKeyboardMarkup()
        keyboard.add(*buttons)
        return keyboard
