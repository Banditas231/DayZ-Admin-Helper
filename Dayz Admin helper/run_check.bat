@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"
python -m pip install requests colorama -q
set "dropped=%~1"
if not "%~2"=="" set "dropped=!dropped! %~2"
if not "%~3"=="" set "dropped=!dropped! %~3"
if not "%~4"=="" set "dropped=!dropped! %~4"
if not "%~5"=="" set "dropped=!dropped! %~5"
if not "%~6"=="" set "dropped=!dropped! %~6"
if not "%~7"=="" set "dropped=!dropped! %~7"
if not "%~8"=="" set "dropped=!dropped! %~8"
if not "%~9"=="" set "dropped=!dropped! %~9"
python "%~dp0check_steam_bans.py" "!dropped!"
pause
