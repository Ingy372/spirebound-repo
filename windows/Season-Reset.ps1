# Season reset, offline (roadmap 8.3). See Season-Reset.bat.
$Root = Split-Path -Parent $PSScriptRoot
$wslRoot = "/mnt/" + $Root.Substring(0,1).ToLower() + $Root.Substring(2).Replace("\", "/")
Write-Host "This WIPES every character, house, guild and the market for a new season. Accounts are kept."
Write-Host "First say /season end <number> in the game. A backup is made before anything is wiped."
$answer = Read-Host "Type WIPE to go ahead"
if ($answer -ne "WIPE") { Write-Host "Nothing was changed."; exit 0 }
wsl.exe -d Ubuntu -u root -- bash -c "tr -d '\r' < $wslRoot/tools/stop_server_wsl.sh | bash"
Start-Sleep 5
wsl.exe -d Ubuntu -u root -- bash -c "tr -d '\r' < $wslRoot/tools/season_wipe.sh > /tmp/season_wipe.sh; bash /tmp/season_wipe.sh wipe $wslRoot"
if ($LASTEXITCODE -ne 0) { Write-Host "The wipe did not run (see above). Nothing else was changed."; exit 1 }
& (Join-Path $PSScriptRoot "Restart-Server.ps1")
Write-Host "The new season has begun."
