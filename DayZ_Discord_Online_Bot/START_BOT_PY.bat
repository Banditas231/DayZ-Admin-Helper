@echo off
setlocal
title DayZ Discord Online Bot

cd /d "%~dp0"

echo ==========================================
echo  DayZ Discord Online Bot
echo ==========================================
echo.

where python >nul 2>&1
if errorlevel 1 (
  echo [ERROR] Python not found in PATH.
  echo Install Python 3 and enable "Add Python to PATH".
  echo.
  pause
  exit /b 1
)

if not exist "requirements.txt" (
  echo [ERROR] requirements.txt not found
  pause
  exit /b 1
)

if not exist "OnlineBot_Config.json" (
  if exist "OnlineBot_Config.example.json" (
    echo [INFO] Creating OnlineBot_Config.json from example...
    copy /Y "OnlineBot_Config.example.json" "OnlineBot_Config.json" >nul
    echo [INFO] Edit OnlineBot_Config.json and .env before running.
  ) else (
    echo [ERROR] OnlineBot_Config.json not found
    pause
    exit /b 1
  )
)

if not exist ".env" (
  if exist ".env.example" (
    echo [INFO] Copy .env.example to .env and add your DISCORD_TOKEN.
  )
)

if not exist ".venv" (
  echo [INFO] Creating virtual environment .venv ...
  python -m venv .venv
  if errorlevel 1 (
    echo [ERROR] Failed to create .venv
    pause
    exit /b 1
  )
)

echo [INFO] Removing wrong package "a2s" if present...
call ".venv\Scripts\pip.exe" uninstall -y a2s >nul 2>&1

echo [INFO] Installing packages...
call ".venv\Scripts\pip.exe" install -r requirements.txt
if errorlevel 1 (
  echo [ERROR] pip install failed.
  pause
  exit /b 1
)

echo [INFO] Starting bot...
echo.
call ".venv\Scripts\python.exe" "bot.py"

echo.
echo [INFO] Bot stopped. Press any key to close.
pause >nul
