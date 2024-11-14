from telebot.states import State, StatesGroup


class CommandsStatesGroup(StatesGroup):
    login = State()
    select_action = State()
    logout = State()
