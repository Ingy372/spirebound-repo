@echo off
rem Saves and stops the Spirebound server and closes the client.
taskkill /IM otclient.exe >nul 2>&1
taskkill /IM canary.exe >nul 2>&1
echo Spirebound stopped. (The server saves the world as it shuts down.)
timeout /t 3 >nul
