from telebot.types import CallbackQuery

from remind.telegram_bot import RemindStatesGroup, GenRemindKeyboards

from frontend.telegram_bot.bot import bot
from frontend.telegram_bot.bot.states import HabitStatesGroup
from frontend.telegram_bot.api import HabitAPIController
from frontend.telegram_bot.schemas import HabitSchema
from frontend.telegram_bot.exceptions import LoginError, HabitError, TimeOutError
from ..utils import send_habit, get_user


@bot.callback_query_handler(state=RemindStatesGroup.check)
def check_habit_callback(call: CallbackQuery):
    with bot.retrieve_data(user_id=call.from_user.id, chat_id=call.message.chat.id) as data:
        user = get_user(data=data, user_id=call.from_user.id)
    status = call.data.split("#")[0]
    habit_id = int(call.data.split("#")[1])

    bot.delete_message(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
    )

    if user:
        if status == "completed":
            habit_api_controller = HabitAPIController(user=user)
            habit_api_controller.complete_habit(habit_id=habit_id)
            bot.edit_message_text(
                text="Отлично!",
                chat_id=call.message.chat.id,
                message_id=call.message.id,
            )

        elif status == "uncompleted":
            bot.edit_message_text(
                text="Ждем новых свершений 😊",
                chat_id=call.message.chat.id,
                message_id=call.message.id,
            )
        else:
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                text="Что-то пошло не так, повторите пожалуйста ответ.",
                reply_markup=GenRemindKeyboards.check_habit(habit_id=habit_id),
                message_id=call.message.id,
            )
    else:
        bot.send_message(
            chat_id=call.message.chat.id,
            text="Для начала вам необходимой авторизоваться. Для этого нажмите /login.",
        )


# from telebot.types import CallbackQuery
#
# from frontend.telegram_bot.handlers.handlers_actions.get_not_done_habits import send_habit
# from frontend.telegram_bot.bot import bot
# from frontend.telegram_bot.states import HabitStatesGroup
# from frontend.telegram_bot.database import UserSession
# from frontend.telegram_bot.api import HabitAPIController
# from frontend.telegram_bot.exceptions import TimeOutError, LoginError, HabitError
# from frontend.telegram_bot.schemas import HabitSchema


@bot.callback_query_handler(func=lambda call: call.data.split("#")[0] == "completed", state=HabitStatesGroup.habits)
def check_habit_callback_from_list_not_done(call: CallbackQuery):
    with bot.retrieve_data(user_id=call.from_user.id, chat_id=call.message.chat.id) as data:
        user = get_user(data=data, user_id=call.from_user.id)
        habits: list[HabitSchema] = data.get("habits", [])

        page = int(call.data.split("#")[1])
        habit_id = habits[page - 1].id

        bot.delete_message(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
        )

        if user:
            habit_api_controller = HabitAPIController(user=user)
            try:
                habit_api_controller.complete_habit(habit_id=habit_id)
                # bot.delete_message(
                #     chat_id=call.message.chat.id,
                #     message_id=call.message.message_id
                # )
                data["habits"] = habit_api_controller.get_list_not_done_habits()
                send_habit(message=call.message, page=page, user_id=call.from_user.id)
            except (HabitError, TimeOutError) as exc:
                bot.send_message(
                    chat_id=call.message.chat.id,
                    text=f"Что-то пошло не так. {exc.detail}",
                )
            except LoginError:
                bot.send_message(
                    chat_id=call.message.chat.id,
                    text=f"Ошибка аутентификации, попробуйте войти снова /login.",
                )
            except Exception as exc:
                bot.send_message(
                    chat_id=call.message.chat.id,
                    text=f"Ошибка:\n\n{exc if exc else "Что-то пошло не так."}\n\nВернуться в меню действий /help",
                )
        else:
            bot.send_message(
                chat_id=call.message.chat.id,
                text="Для начала вам необходимой авторизоваться. Для этого нажмите /login.",
            )
