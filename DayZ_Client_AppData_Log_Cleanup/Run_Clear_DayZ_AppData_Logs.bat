@echo off
chcp 65001 >nul
title DayZ AppData Log Cleanup
cd /d "%~dp0"

echo.
echo 1^) Preview only ^(nothing deleted^) — press A and Enter
echo 2^) Delete all found log/RPT/mdmp/adm files — press any other key and Enter
echo.
set /p CHOICE="Choice: "

if /i "%CHOICE%"=="A" (
  powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0clear_dayz_appdata_logs.ps1" -DryRun
) else (
  powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0clear_dayz_appdata_logs.ps1"
)

echo.
pause
