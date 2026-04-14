@echo off
echo Starting XXBot Host...
echo.

cd /d "%~dp0"

python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found. Please install Python and add it to PATH.
    pause
    exit /b 1
)

echo Starting main.py...
echo.

python main.py

echo.
echo XXBot Host has exited.
pause