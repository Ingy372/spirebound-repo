@echo off
rem Lets players on your Tailscale network download the game client from this PC (port 8090), for as long as this
rem window stays open. Builds the package first. Needs Open-Friend-Access.bat to have been run once.
cd /d "%~dp0.."
python tools\make_friend_client.py || (pause & exit /b 1)
echo.
echo Sharing the client. Leave this window open while your tester installs; close it when they are done.
python -m http.server 8090 --bind 127.0.0.1 --directory .local\friend
