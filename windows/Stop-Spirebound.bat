@echo off
rem Saves and stops the Spirebound server (in WSL) and closes the client.
taskkill /IM otclient.exe >nul 2>&1
wsl -d Ubuntu -u root -- bash -c "pkill -INT -x canary; sleep 8; pkill -x canary; pkill -f login_server.py; true"
echo Spirebound stopped. (The server saves the world as it shuts down.)
timeout /t 3 >nul
