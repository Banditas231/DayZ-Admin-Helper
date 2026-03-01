@echo off
cd /d "%~dp0"
python -m pip install requests colorama -q
python "%~dp0check_steam_bans.py" "%1"
pause
