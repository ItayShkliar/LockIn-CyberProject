@echo off
rem ------------------------------------------------------------
rem Install all Python dependencies required by the LockInProject
rem ------------------------------------------------------------

rem Exit on any error
setlocal EnableExtensions EnableDelayedExpansion

rem Resolve script directory (project root)
set "SCRIPT_DIR=%~dp0"

rem Optional: create a virtual environment
set "VENV_DIR=%SCRIPT_DIR%.venv"
if not exist "%VENV_DIR%" (
    echo Creating virtual environment at %VENV_DIR% ...
    python -m venv "%VENV_DIR%"
)

rem Activate the virtual environment
call "%VENV_DIR%\Scripts\activate.bat"

rem Upgrade pip to the latest version
echo Upgrading pip...
python -m pip install --upgrade pip

rem ------------------------------------------------------------
rem Core Python packages used throughout the codebase
rem ------------------------------------------------------------
rem Flask (web server)
rem PyQt5 (desktop UI)
rem requests (HTTP client)
rem psutil (system monitoring)
rem ------------------------------------------------------------

echo Installing required Python packages...
pip install Flask PyQt5 requests psutil

echo All dependencies installed successfully.

endlocal
