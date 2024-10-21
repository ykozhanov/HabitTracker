from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

class GenKeyboards:

    def __init__(self):
        pass

    @classmethod
    def login_keyboard(cls) -> InlineKeyboardMarkup:
        buttons = [
            InlineKeyboardButton(text="Да ✅", callback_data="yes"),
            InlineKeyboardButton(text="Нет 🚫", callback_data="no"),
        ]
        keyboard = InlineKeyboardMarkup()
        keyboard.add(*buttons)
        return keyboard