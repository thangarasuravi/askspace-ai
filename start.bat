@echo off
title AskSpace AI Launcher
echo ===================================================
echo           Starting AskSpace AI Workspace
echo ===================================================
echo.
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found in .venv!
    echo Please run setup instructions in README.md first.
    pause
    exit /b 1
)

echo [INFO] Opening AskSpace AI in your browser...
start http://127.0.0.1:5000/

echo [INFO] Starting Flask Server on http://127.0.0.1:5000...
echo Press CTRL+C to stop the server anytime.
echo.
".venv\Scripts\python.exe" run.py
pause
