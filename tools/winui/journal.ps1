param([string]$Shot = "journal.png", [string]$Email = "jay@localhost", [string]$Pass = "spirebound", [int]$CharY = 320)
. "$PSScriptRoot\login.ps1" -Email $Email -Pass $Pass
Click 480 $CharY; Keys "{ENTER}"; Start-Sleep 8
Keys "{ESC}"; Start-Sleep 1; Keys "j"; Start-Sleep 3
if (GameProc) { Shot $Shot } else { "CLIENT CRASHED" }
