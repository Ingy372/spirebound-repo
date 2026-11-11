@echo off
rem Builds just the game client on this PC (the server runs in WSL).
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0Install-Client.ps1"
echo.
pause
