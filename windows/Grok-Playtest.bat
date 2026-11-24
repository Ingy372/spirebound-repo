@echo off
rem Grok plays a brand-new character on your server and writes a playtest report (docs\playtests\).
rem Needs: the server running (Start-Spirebound.bat) and your xAI API key in server\local.env.
cd /d "%~dp0.."
findstr /b "XAI_API_KEY=xai-" server\local.env >nul 2>&1
if errorlevel 1 (
  echo Your xAI API key is not set yet.
  echo Open server\local.env in Notepad and replace "paste-your-key-here" with your key, then save.
  notepad server\local.env
  pause
  exit /b 1
)
python tools\grok_tester.py --fresh
echo.
echo Done. The report is in the docs\playtests folder (the newest grok_ file).
pause
