@echo off
rem Ends the season for real (roadmap 8.3): run this AFTER saying /season end <number> in game (that archives everyone and
rem shuts the server down). This backs up the database, wipes characters, houses, guilds, the market and world
rem progress, and starts the server for the new season. Accounts and account rewards are kept.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0Season-Reset.ps1"
pause
