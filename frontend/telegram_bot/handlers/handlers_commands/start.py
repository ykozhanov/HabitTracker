from telebot.types import BotCommand, Message, ReplyKeyboardRemove

from frontend.telegram_bot.bot import bot

from ..utils import get_user


@bot.message_handler(commands=["start"])  # type: ignore
def handle_start(message: Message) -> None:
    with bot.retrieve_data(
        user_id=message.from_user.id, chat_id=message.chat.id
    ) as data:
        get_user(data=data, user_id=message.from_user.id)

    bot.send_message(
        chat_id=message.chat.id,
        text="Добро пожаловать!\n\nИспользуйте /help для получения списка команд.",
        reply_markup=ReplyKeyboardRemove(),
    )

    bot.set_my_commands(
        [
            BotCommand(command="/start", description="Запустить бот"),
            BotCommand(
                command="/login",
                description="Войти в аккаунт HabitTracker или зарегистрироваться",
            ),
            BotCommand(command="/help", description="Показать список команд"),
            BotCommand(command="/logout", description="Выйти из аккаунта HabitTracker"),
        ]
    )
