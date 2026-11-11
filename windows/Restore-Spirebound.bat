@echo off
rem Puts back the newest saved copy (or the zip file you drop on this icon). Stop the server first.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0Restore-Spirebound.ps1" %*
pause
