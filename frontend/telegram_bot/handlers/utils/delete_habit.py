from telebot.types import CallbackQuery

from frontend.telegram_bot.handlers.actions.get_all_habits import send_habit
from frontend.telegram_bot.bot import bot
from frontend.telegram_bot.states import HabitStatesGroup
from frontend.telegram_bot.database import UserSession
from frontend.telegram_bot.controllers import HabitAPIController
from frontend.telegram_bot.exceptions import TimeOutError, LoginError, HabitError
from frontend.telegram_bot.schemas import HabitSchema


@bot.callback_query_handler(func=lambda call: call.data.split("#")[0] == "delete", state=HabitStatesGroup.habits)
def delete_habit_callback(call: CallbackQuery):
    with bot.retrieve_data(user_id=call.from_user.id, chat_id=call.message.chat.id) as data:
        user: UserSession = data["login"].get("user", None)
        habits: list[HabitSchema] = data.get("habits", [])

        page = int(call.message.text.split("#")[1])
        habit_id = habits[page - 1].id

        if user:
            habit_api_controller = HabitAPIController(user=user)
            try:
                habit_api_controller.delete_habit(habit_id=habit_id)
                bot.delete_message(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id
                )
                data["habits"] = habit_api_controller.get_list_habits()
                send_habit(message=call.message, page=page - 1)
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
                    text=f"Что-то пошло не так. {exc}",
                )
        else:
            bot.send_message(
                chat_id=call.message.chat.id,
                text="Для начала вам необходимой авторизоваться. Для этого нажмите /login.",
            )
