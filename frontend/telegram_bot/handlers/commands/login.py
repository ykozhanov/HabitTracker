from telebot.types import Message, CallbackQuery

from .. import GenKeyboards, UserStatesGroup, CommandsStatesGroup, bot, UserAPIController


@bot.message_handler(commands=["login"])
def handle_login(message: Message) -> None:
    username = message.from_user.username
    bot.send_message(
        chat_id=message.chat.id,
        text="Добро пожаловать, {username}!/nВы уже зарегистрированы в приложении HabitTracker?"
        .format(username=username),
        reply_markup=GenKeyboards.yes_or_no_inline(),
    )
    bot.set_state(
        user_id=message.from_user.id,
        state=CommandsStatesGroup.login,
        chat_id=message.chat.id,
    )


@bot.callback_query_handler(state=CommandsStatesGroup.login)
def handle_login(call: CallbackQuery) -> None:
    if call.data == "yes" or call.data == "no":
        text = "Отлично! Введите ваш логин:" if call.data == "yes" else "Давайте зарегистрируемся! Введите username:"
        state = UserStatesGroup.waiting_login if call.data == "yes" else UserStatesGroup.waiting_login_register
        bot.send_message(chat_id=call.message.chat.id, text=text)
        bot.set_state(
            user_id=call.from_user.id,
            state=state,
            chat_id=call.message.chat.id,
        )
    else:
        bot.send_message(
            chat_id=call.message.chat.id,
            text="Извините, я вас не совсем понял. Подскажите пожалуйста, вы уже зарегистрированы в приложении HabitTracker?",
            reply_markup=GenKeyboards.yes_or_no_inline(),
        )


@bot.message_handler(state=[UserStatesGroup.waiting_login, UserStatesGroup.waiting_login_register])
def handle_waiting_login(message: Message) -> None:
    with bot.retrieve_data(user_id=message.from_user.id, chat_id=message.chat.id) as data:
        data["login"]["username"] = message.text
    state_now = bot.get_state(user_id=message.from_user.id, chat_id=message.chat.id)

    state = UserStatesGroup.waiting_password if state_now == UserStatesGroup.waiting_login else UserStatesGroup.waiting_password_register
    bot.send_message(chat_id=message.chat.id, text="Введите пароль:")
    bot.set_state(
        user_id=message.from_user.id,
        state=state,
        chat_id=message.chat.id,
    )


@bot.message_handler(state=[UserStatesGroup.waiting_password, UserStatesGroup.waiting_password_register])
def handle_waiting_password(message: Message) -> None:
    with bot.retrieve_data(user_id=message.from_user.id, chat_id=message.chat.id) as data:
        data["login"]["password"] = message.text
    state_now = bot.get_state(user_id=message.from_user.id, chat_id=message.chat.id)

    if state_now == UserStatesGroup.waiting_password:
        with bot.retrieve_data(user_id=message.from_user.id, chat_id=message.chat.id) as data:
            username = data["login"].pop("username")
            password = data["login"].pop("password")
            api_controller = UserAPIController(username=username, password=password)
            user = api_controller.login()
            data["login"]["user"] = user
        bot.send_message(
            chat_id=message.chat.id,
            text=f"Отлично! Вы успешно вошли как {username!r}.\nЧто хотите сделать?",
            reply_markup=GenKeyboards.select_action_reply(),
        )
        bot.set_state(
            user_id=message.from_user.id,
            state=CommandsStatesGroup.select_action,
            chat_id=message.chat.id,
        )
    else:
        bot.send_message(chat_id=message.chat.id, text="Повторите пароль:")
        bot.set_state(
            user_id=message.from_user.id,
            state=UserStatesGroup.waiting_password_register,
            chat_id=message.chat.id,
        )


@bot.message_handler(state=UserStatesGroup.waiting_password_register)
def handle_waiting_password_register(message: Message) -> None:
    with bot.retrieve_data(user_id=message.from_user.id, chat_id=message.chat.id) as data:
        check_password = message.text == data["login"]["password"]

    if check_password:
        with bot.retrieve_data(user_id=message.from_user.id, chat_id=message.chat.id) as data:
            username = data["login"].pop("username")
            password = data["login"].pop("password")
            api_controller = UserAPIController(username=username, password=password)
            user = api_controller.login(register=True)
            data["login"]["user"] = user
        bot.send_message(
            chat_id=message.chat.id,
            text=f"Отлично! Вы успешно зарегистрировались и вошли как {username!r}.\nЧто хотите сделать?",
            reply_markup=GenKeyboards.select_action_reply(),
        )
        bot.set_state(
            user_id=message.from_user.id,
            state=CommandsStatesGroup.select_action,
            chat_id=message.chat.id,
        )
    else:
        bot.send_message(chat_id=message.chat.id, text="Неверный пароль. Повторите еще раз:")
