from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton


class GenKeyboards:

    def __init__(self):
        pass

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

    # @staticmethod
    # def habits_inline_(page: int) -> InlineKeyboardMarkup:
    #     buttons = [
    #         [
    #             InlineKeyboardButton(text="Удалить", callback_data=f"delete#{page}"),
    #             InlineKeyboardButton(text="Редактировать", callback_data=f"update#{page}"),
    #             InlineKeyboardButton(text="Выполнена", callback_data=f"completed#{page}"),
    #         ],
    #         [
    #             InlineKeyboardButton(text="Создать новую привычку", callback_data=f"create#{page}"),
    #         ],
    #     ]
    #     keyboard = InlineKeyboardMarkup()
    #     keyboard.add(*buttons)
    #     return keyboard