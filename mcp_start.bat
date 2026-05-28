@echo off
setlocal

:: Get the directory where this script is located
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

:: 1. Try Python (Source Method)
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [VenEl_SwaMCP] Python detected. Using source/.venv approach... >&2
    if not exist ".venv\Scripts\python.exe" (
        echo [VenEl_SwaMCP] Creating virtual environment... >&2
        python -m venv .venv
        call ".venv\Scripts\activate.bat"
        echo [VenEl_SwaMCP] Installing dependencies... >&2
        pip install -r requirements.txt
    ) else (
        call ".venv\Scripts\activate.bat"
    )
    echo [VenEl_SwaMCP] Starting server... >&2
    python -m src.server
    exit /b %errorlevel%
)

:: 2. Try Docker (Container Method)
docker --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [VenEl_SwaMCP] Python not found, but Docker detected. Running via Docker container... >&2
    :: Windows path formatting for Docker volumes can be tricky, using double slash for Windows paths
    docker run -i --rm -v //var/run/docker.sock:/var/run/docker.sock ghcr.io/venkateshellur/venel_swamcp:latest
    exit /b %errorlevel%
)

:: 3. Try Standalone Executable (Binary Method)
if exist "VenEl_SwaMCP-windows.exe" (
    echo [VenEl_SwaMCP] Neither Python nor Docker found. Running standalone executable... >&2
    VenEl_SwaMCP-windows.exe
    exit /b %errorlevel%
)

:: Failure
echo [VenEl_SwaMCP] ERROR: Could not start. Please install Python, Docker, or download the standalone executable into this folder. >&2
exit /b 1
