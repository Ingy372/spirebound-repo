@echo off
rem Opens the Spirebound server to your Tailscale network only (asks for administrator rights).
powershell -NoProfile -Command "Start-Process powershell -Verb RunAs -ArgumentList '-NoProfile -ExecutionPolicy Bypass -File \"%~dp0Open-Friend-Access.ps1\"'"
