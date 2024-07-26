from data.loader import bot
import handler


def start_bot():
    bot.infinity_polling(timeout=False)

if __name__ == '__main__':
    start_bot()