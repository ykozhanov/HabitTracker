from telebot.states import State, StatesGroup


class UserStatesGroup(StatesGroup):  # type: ignore[misc]
    waiting_login = State()
    waiting_login_register = State()
    waiting_email = State()
    waiting_password = State()
    waiting_password_register = State()
    waiting_repeat_password = State()
    check_new_user = State()
    register = State()
