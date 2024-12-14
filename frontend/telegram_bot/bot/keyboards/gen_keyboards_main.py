from telebot.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)


class GenKeyboards:

    @staticmethod
    def yes_or_no_inline() -> InlineKeyboardMarkup:
        buttons = [
            InlineKeyboardButton(text="Да ✅", callback_data="yes"),
            InlineKeyboardButton(text="Нет 🚫", callback_data="no"),
        ]
        keyboard = InlineKeyboardMarkup()
        keyboard.add(*buttons)
        return keyboard

    @staticmethod
    def select_action_reply() -> ReplyKeyboardMarkup:
        buttons = [
            KeyboardButton(text="Выйти из профиля 🔄"),
            KeyboardButton(text="Список привычек 📝"),
            KeyboardButton(text="Создать новую ➕"),
        ]
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(*buttons)
        return keyboard
