from telebot.states import State, StatesGroup


class RemindStatesGroup(StatesGroup):
    check = State()
