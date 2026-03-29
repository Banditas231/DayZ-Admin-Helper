@echo off
title DayZ Mod Update Checker
cd /d "%~dp0"
where python >nul 2>&1
if errorlevel 1 (
  echo Python was not found in PATH. Install Python 3 from https://www.python.org/downloads/
  echo Enable "Add python.exe to PATH" during setup.
  pause
  exit /b 1
)
python check_and_update_mods.py
pause
