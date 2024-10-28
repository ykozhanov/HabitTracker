from telebot.types import Message, BotCommand

from .. import bot


@bot.message_handler(commands=["start"])
def handle_start(message: Message) -> None:
    bot.send_message(chat_id=message.chat.id, text="Добро пожаловать! Используйте /help для получения списка команд.")
    bot.set_my_commands([
        BotCommand(command="/start", description="Запустить бота"),
        BotCommand(command="/login", description="Войти в аккаунт HabitTracker или зарегистрироваться"),
        BotCommand(command="/help", description="Показать список команд"),
        BotCommand(command="/logout", description="Выйти из аккаунта HabitTracker"),
    ])
