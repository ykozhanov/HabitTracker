from telebot.states import State, StatesGroup


class CommandsStatesGroup(StatesGroup):
    login = State()
    select_action = State()
    logout = State()


class UserStatesGroup(StatesGroup):
    waiting_login = State()
    waiting_login_register = State()
    waiting_email= State()
    waiting_password = State()
    waiting_password_register = State()
    waiting_repeat_password = State()
    register = State()


class HabitStatesGroup(StatesGroup):
    habits = State()


class HabitUpdateStatesGroup(StatesGroup):
    update_title = State()
    update_description = State()
    waiting_title = State()
    waiting_description = State()
    check_habit = State()
    back_or_again_update = State()
    back_or_again_create = State()


class HabitCreateStatesGroup(StatesGroup):
    update_title = State()
    update_description = State()
    waiting_title = State()
    waiting_description = State()
    check_habit = State()
    back_or_again_update = State()
    back_or_again_create = State()