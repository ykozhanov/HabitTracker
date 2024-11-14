from telebot.types import CallbackQuery, ReplyKeyboardRemove

from frontend.telegram_bot.bot import bot
from frontend.telegram_bot.bot.states import HabitStatesGroup, CommandsStatesGroup
from frontend.telegram_bot.api import HabitAPIController
from frontend.telegram_bot.exceptions import TimeOutError, LoginError, HabitError
from frontend.telegram_bot.schemas import HabitSchema
from ..utils import send_habit, get_user


@bot.callback_query_handler(func=lambda call: call.data.split("#")[0] == "delete", state=HabitStatesGroup.habits)
def delete_habit_callback(call: CallbackQuery):
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
                habit_api_controller.delete_habit(habit_id=habit_id)
                # bot.delete_message(
                #     chat_id=call.message.chat.id,
                #     message_id=call.message.message_id
                # )
                del data["habits"]
                data["habits"] = habit_api_controller.get_list_not_done_habits()
                if len(data["habits"]) > 0:
                    send_habit(message=call.message, page=page - 1, user_id=call.from_user.id)
                else:
                    bot.send_message(
                        chat_id=call.message.chat.id,
                        text="Привычек пока нет.\nВыбрать новое действие /help",
                        reply_markup=ReplyKeyboardRemove(),
                    )
                    bot.set_state(
                        user_id=call.message.from_user.id,
                        state=CommandsStatesGroup.select_action,
                        chat_id=call.message.chat.id,
                    )
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
