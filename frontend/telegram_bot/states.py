from telebot.states import State, StatesGroup


class UserStatesGroup(StatesGroup):
    login = State()
    waiting_login = State()
    waiting_email= State()
    waiting_password = State()
    waiting_repeat_password = State()



class HabitStatesGroup(StatesGroup):
    waiting_title = State()
    waiting_description = State()
