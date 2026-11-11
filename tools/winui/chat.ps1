# Logs in with a character and says the given chat lines (e.g. "!shop"), then saves a screenshot.
param([string]$Shot = "chat.png", [string]$Lines = "!shop", [string]$Email = "jay@localhost", [string]$Pass = "spirebound", [int]$CharY = 320)
. "$PSScriptRoot\login.ps1" -Email $Email -Pass $Pass
Click 480 $CharY; Keys "{ENTER}"; Start-Sleep 8
Keys "{ESC}"; Start-Sleep 1
foreach ($l in $Lines.Split("|")) { Click 600 880; Keys $l; Keys "{ENTER}"; Start-Sleep 2 }
Click 360 764; Start-Sleep 1
if (GameProc) { Shot $Shot } else { "CLIENT CRASHED" }
