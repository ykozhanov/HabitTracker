from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton


class GenKeyboards:

    def __init__(self):
        pass

    @classmethod
    def yes_or_no_inline(cls) -> InlineKeyboardMarkup:
        buttons = [
            InlineKeyboardButton(text="Да ✅", callback_data="yes"),
            InlineKeyboardButton(text="Нет 🚫", callback_data="no"),
        ]
        keyboard = InlineKeyboardMarkup()
        keyboard.add(*buttons)
        return keyboard

    @classmethod
    def select_action_reply(cls) -> ReplyKeyboardMarkup:
        buttons = [
            KeyboardButton(text="Выйти из профиля 🔄"),
            KeyboardButton(text="Список привычек 📝"),
            KeyboardButton(text="Создать новую привычку ➕"),
        ]
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(*buttons)
        return keyboard

    @classmethod
    def check_habit(cls, habit_id) -> InlineKeyboardMarkup:
        buttons = [
            InlineKeyboardButton(text="Уже выполнил", callback_data=f"completed#{habit_id}"),
            InlineKeyboardButton(text="Еще не выполнил", callback_data=f"uncompleted#{habit_id}"),
        ]
        keyboard = InlineKeyboardMarkup()
        keyboard.add(*buttons)
        return keyboard
