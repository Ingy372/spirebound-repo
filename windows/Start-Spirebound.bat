@echo off
rem Starts the Spirebound server and opens the game client.
set ROOT=%~dp0..
if not exist "%ROOT%\.local\server\canary.exe" (
  echo Spirebound is not installed yet. Double-click Install-Spirebound.bat first.
  pause
  exit /b 1
)
powershell -NoProfile -Command "Get-Service -Name 'MariaDB*' -ErrorAction SilentlyContinue | Where-Object Status -ne Running | Start-Service"
echo Saving a backup of your world first...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0Backup-Spirebound.ps1" 2>nul || echo (No backup this time. The game will still start.)
echo Starting the Spirebound server (a black window will stay open while it runs)...
start "Spirebound Server" /D "%ROOT%\.local\server" "%ROOT%\.local\server\canary.exe"
echo Waiting for the server to come online...
timeout /t 15 /nobreak >nul
start "" /D "%ROOT%\.local\client" "%ROOT%\.local\client\otclient.exe"
echo Log in with account: jay   password: spirebound
