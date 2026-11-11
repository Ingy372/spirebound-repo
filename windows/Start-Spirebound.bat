@echo off
rem Starts the Spirebound server (in WSL), waits until it is ready, then opens the game client.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0Start-Spirebound.ps1"
