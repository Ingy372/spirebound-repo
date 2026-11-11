# Logs in (see login.ps1) and enters the game with the first character in the list; saves a screenshot.
param([string]$Shot = "enter.png", [int]$CharY = 320)
. "$PSScriptRoot\login.ps1"
Click 480 $CharY; Keys "{ENTER}"; Start-Sleep 10
if (GameProc) { Shot $Shot } else { "CLIENT CRASHED" }
