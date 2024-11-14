from telebot import custom_filters

from .bot import bot
import frontend.telegram_bot.handlers

if __name__ == "__main__":
    bot.add_custom_filter(custom_filters.StateFilter(bot))
    bot.polling(none_stop=True)
