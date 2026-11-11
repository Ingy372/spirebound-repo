@echo off
rem Saves a copy of the Spirebound database into the backups folder.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0Backup-Spirebound.ps1"
pause
