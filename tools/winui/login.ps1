# Restarts the client and logs in with the given account (automated testing helper).
param([string]$Email = "jay@localhost", [string]$Pass = "spirebound")
$root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Stop-Process -Name otclient -Force -ErrorAction SilentlyContinue; Start-Sleep 2
Start-Process "$root\.local\client\otclient.exe" -WorkingDirectory "$root\.local\client"
Start-Sleep 12
. "$PSScriptRoot\ui.ps1"
Focus; Start-Sleep 1
Click 720 390; Keys $Email; Click 720 413; Keys $Pass; Keys "{ENTER}"; Start-Sleep 4
