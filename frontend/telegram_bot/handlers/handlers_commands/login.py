import re

from telebot.types import CallbackQuery, Message

from frontend.telegram_bot.api import UserAPIController
from frontend.telegram_bot.bot import bot
from frontend.telegram_bot.bot.keyboards import GenKeyboards
from frontend.telegram_bot.bot.states import CommandsStatesGroup, UserStatesGroup
from frontend.telegram_bot.config import BOT_TOKEN, VIEW_MESSAGES
from frontend.telegram_bot.database import UserController
from frontend.telegram_bot.exceptions import AuthenticationError
from remind import RemindTelegramController

from ..utils import get_user


@bot.message_handler(commands=["login"])  # type: ignore
def handle_login(message: Message) -> None:
    # logger.debug(f"username: {username}")
    with bot.retrieve_data(
        user_id=message.from_user.id, chat_id=message.chat.id
    ) as data:
        user = get_user(data=data, user_id=message.from_user.id)

    if not user:
        bot.send_message(
            chat_id=message.chat.id,
            text=f"Добро пожаловать, {message.from_user.username}!\n\nВы уже зарегистрированы в приложении HabitTracker?",
            reply_markup=GenKeyboards.yes_or_no_inline(),
        )
    else:
        bot.send_message(
            chat_id=message.chat.id,
            text="Для начала вам нужно выйти.\n\nНажмите /logout.",
        )
    bot.set_state(
        user_id=message.from_user.id,
        state=CommandsStatesGroup.login,
        chat_id=message.chat.id,
    )


@bot.callback_query_handler(state=CommandsStatesGroup.login)  # type: ignore
def handle_callback_login(call: CallbackQuery) -> None:
    bot.delete_message(
        chat_id=call.message.chat.id,
        message_id=call.message.id,
    )

    if call.data == "yes" or call.data == "no":
        text = (
            "Введите ваш логин:"
            if call.data == "yes"
            else "Давайте зарегистрируемся!\nВведите логин:"
        )
        state = (
            UserStatesGroup.waiting_login
            if call.data == "yes"
            else UserStatesGroup.waiting_login_register
        )
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


@bot.message_handler(
    state=[UserStatesGroup.waiting_login, UserStatesGroup.waiting_login_register]
)  # type: ignore
def handle_waiting_login(message: Message) -> None:
    with bot.retrieve_data(
        user_id=message.from_user.id, chat_id=message.chat.id
    ) as data:
        data["login"] = {}
        data["login"]["username"] = message.text
    state_now = bot.get_state(user_id=message.from_user.id, chat_id=message.chat.id)
    state = (
        UserStatesGroup.waiting_password
        if state_now == "UserStatesGroup:waiting_login"
        else UserStatesGroup.waiting_password_register
    )
    bot.send_message(chat_id=message.chat.id, text="Введите пароль:")
    bot.set_state(
        user_id=message.from_user.id,
        state=state,
        chat_id=message.chat.id,
    )


@bot.message_handler(
    state=[UserStatesGroup.waiting_password, UserStatesGroup.waiting_password_register]
)  # type: ignore
def handle_waiting_password(message: Message) -> None:
    with bot.retrieve_data(
        user_id=message.from_user.id, chat_id=message.chat.id
    ) as data:
        data["login"]["password"] = message.text
    state_now = bot.get_state(user_id=message.from_user.id, chat_id=message.chat.id)
    if state_now == "UserStatesGroup:waiting_password":
        with bot.retrieve_data(
            user_id=message.from_user.id, chat_id=message.chat.id
        ) as data:
            username = data["login"].pop("username", None)
            password = data["login"].pop("password", None)
        try:
            user_data = UserAPIController.login(username=username, password=password)
            user_controller = UserController(user_id=message.from_user.id)
            user_info = user_controller.get_user()
            if user_info:
                user = user_controller.update(
                    access_token=user_data.access_token,
                    refresh_token=user_data.refresh_token,
                )
                remind_telegram_controller = RemindTelegramController(
                    refresh_token=user_info.refresh_token
                )
                remind_telegram_controller.update_refresh_token(
                    new_refresh_token=user.refresh_token
                )
            else:
                user = user_controller.add_new_user(
                    access_token=user_data.access_token,
                    refresh_token=user_data.refresh_token,  # type: ignore
                )
                remind_telegram_controller = RemindTelegramController(
                    refresh_token=user.refresh_token
                )
                remind_telegram_controller.add_user(
                    chat_id=message.chat.id,
                    user_id=message.from_user.id,
                    bot_token=BOT_TOKEN,  # type: ignore
                )
            data["login"]["user"] = user
            bot.send_message(
                chat_id=message.chat.id,
                text=f"Отлично!\n\nВы успешно вошли как {username!r}.\n\nЧто хотите сделать?",
                reply_markup=GenKeyboards.select_action_reply(),
            )
        except AuthenticationError:
            bot.send_message(
                chat_id=message.chat.id,
                text="Ошибка входа!\nПопробуйте войти снова, для этого нажмите /login",
            )
        except Exception:
            bot.send_message(
                chat_id=message.chat.id,
                text="Что-то пошло не так.\nПопробуйте войти снова, для этого нажмите /login",
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
            state=UserStatesGroup.waiting_repeat_password,
            chat_id=message.chat.id,
        )


@bot.message_handler(state=UserStatesGroup.waiting_repeat_password)  # type: ignore
def handle_waiting_repeat_password(message: Message) -> None:
    with bot.retrieve_data(
        user_id=message.from_user.id, chat_id=message.chat.id
    ) as data:
        check_password = message.text == data["login"]["password"]
    if check_password:
        bot.send_message(
            chat_id=message.chat.id, text="Введите вашу электронную почту:"
        )
        bot.set_state(
            user_id=message.from_user.id,
            state=UserStatesGroup.waiting_email,
            chat_id=message.chat.id,
        )
    else:
        bot.send_message(
            chat_id=message.chat.id, text="Пароли не совпадают. Повторите еще раз:"
        )


@bot.message_handler(state=UserStatesGroup.waiting_email)  # type: ignore
def handle_waiting_email(message: Message) -> None:
    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if re.match(email_pattern, message.text):
        with bot.retrieve_data(
            user_id=message.from_user.id, chat_id=message.chat.id
        ) as data:
            data["login"]["email"] = message.text
            username = data["login"].get("username")
            email = data["login"].get("email")
        text = VIEW_MESSAGES["user"].format(username=username, email=email)
        bot.send_message(
            chat_id=message.chat.id,
            text=f"Вы зарегистрируетесь со следующими данными:\n\n{text}\n\nВсё верно?",
            parse_mode="Markdown",
            reply_markup=GenKeyboards.yes_or_no_inline(),
        )
        bot.set_state(
            user_id=message.from_user.id,
            state=UserStatesGroup.check_new_user,
            chat_id=message.chat.id,
        )
    else:
        bot.send_message(
            chat_id=message.chat.id, text="Некорректный email. Повторите еще раз:"
        )


@bot.callback_query_handler(state=UserStatesGroup.check_new_user)  # type: ignore
def handle_callback_check_new_user(call: CallbackQuery) -> None:
    if call.data == "yes" or call.data == "no":
        if call.data == "yes":
            with bot.retrieve_data(
                user_id=call.from_user.id, chat_id=call.message.chat.id
            ) as data:
                username = data["login"].pop("username")
                password = data["login"].pop("password")
                email = data["login"].pop("email")
            try:
                user_data = UserAPIController.login(
                    username=username, password=password, email=email
                )
                user_controller = UserController(user_id=call.from_user.id)
                user = user_controller.add_new_user(
                    access_token=user_data.access_token,
                    refresh_token=user_data.refresh_token,  # type: ignore
                )
                data["login"]["user"] = user
                remind_telegram_controller = RemindTelegramController(
                    refresh_token=user.refresh_token
                )
                remind_telegram_controller.add_user(
                    chat_id=call.message.chat.id,
                    user_id=call.from_user.id,
                    bot_token=BOT_TOKEN,  # type: ignore
                )
                bot.delete_message(
                    chat_id=call.message.chat.id, message_id=call.message.id
                )
                bot.send_message(
                    chat_id=call.message.chat.id,
                    text=f"Отлично!\n\nВы успешно зарегистрировались и вошли как {username!r}.\n\nЧто хотите сделать? ⏬",
                    reply_markup=GenKeyboards.select_action_reply(),
                )
            except AuthenticationError:
                bot.send_message(
                    chat_id=call.message.chat.id,
                    text="Ошибка входа!\nПопробуйте войти снова, для этого нажмите /login",
                )
        else:
            bot.send_message(
                chat_id=call.message.chat.id,
                text="Для повторной регистрации нажмите /login.",
            )
        bot.set_state(
            user_id=call.from_user.id,
            state=CommandsStatesGroup.select_action,
            chat_id=call.message.chat.id,
        )
    else:
        bot.send_message(
            chat_id=call.message.chat.id,
            text="Извините, я вас не совсем понял. Подскажите пожалуйста, вы подтверждаете введенные данные?",
            reply_markup=GenKeyboards.yes_or_no_inline(),
        )
