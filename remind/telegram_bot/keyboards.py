from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup


class GenRemindKeyboards:

    @staticmethod
    def check_habit(habit_id: int) -> InlineKeyboardMarkup:
        buttons = [
            InlineKeyboardButton(
                text="Да", callback_data=f"remind#completed#{habit_id}"
            ),
            InlineKeyboardButton(
                text="Еще нет", callback_data=f"remind#uncompleted#{habit_id}"
            ),
        ]
        keyboard = InlineKeyboardMarkup()
        keyboard.add(*buttons)
        return keyboard
