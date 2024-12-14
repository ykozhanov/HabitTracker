from telebot import custom_filters

import frontend.telegram_bot.handlers  # noqa: F401

from .bot import bot

if __name__ == "__main__":
    bot.add_custom_filter(custom_filters.StateFilter(bot))
    bot.polling(none_stop=True)
