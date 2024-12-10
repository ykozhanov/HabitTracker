from telebot.states import State, StatesGroup


class HabitStatesGroup(StatesGroup):
    habits = State()


class HabitUpdateStatesGroup(StatesGroup):
    update_title = State()
    update_description = State()
    update_remind_time = State()
    waiting_title = State()
    waiting_description = State()
    waiting_remind_time_hour = State()
    waiting_remind_time_minute = State()
    check_habit = State()
    back_or_again_update = State()
    back_or_again_create = State()


class HabitCreateStatesGroup(StatesGroup):
    waiting_title = State()
    waiting_description = State()
    waiting_remind_time_hour = State()
    waiting_remind_time_minute = State()
    check_habit = State()
    back_or_again_update = State()
    back_or_again_create = State()