@echo off
setlocal

:: Get the directory where this script is located
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

:: Check if .venv exists
if not exist ".venv\Scripts\python.exe" (
    echo [VenEl_SwaMCP] Creating virtual environment... >&2
    python -m venv .venv
    if errorlevel 1 (
        echo [VenEl_SwaMCP] Failed to create virtual environment. Make sure python is installed. >&2
        exit /b 1
    )
    
    echo [VenEl_SwaMCP] Installing dependencies... >&2
    call ".venv\Scripts\activate.bat"
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [VenEl_SwaMCP] Failed to install dependencies. >&2
        exit /b 1
    )
) else (
    call ".venv\Scripts\activate.bat"
)

:: Run the server
echo [VenEl_SwaMCP] Starting server... >&2
python -m src.server
