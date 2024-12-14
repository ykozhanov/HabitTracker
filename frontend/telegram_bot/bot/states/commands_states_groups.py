from telebot.states import State, StatesGroup


class CommandsStatesGroup(StatesGroup):  # type: ignore[misc]
    login = State()
    select_action = State()
    logout = State()
