@echo off
title LockIn Installation Script
echo ==========================================
echo   LockIn - Installing Dependencies
echo ==========================================
echo.
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    pause
    exit /b
)

echo [1/2] Updating pip...
python -m pip install --upgrade pip

echo [2/2] Installing requirements from requirements.txt...
pip install -r requirements.txt

echo.
echo ==========================================
echo   Installation Complete!
echo ==========================================
pause
