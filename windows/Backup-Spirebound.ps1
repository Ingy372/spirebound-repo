# Saves a copy of the Spirebound database (characters, houses, guilds, market, world progress)
# into the "backups" folder next to the repo, and keeps the newest 14 copies.
# The database lives inside WSL (Ubuntu), so this just asks WSL to do the work (tools/db_wsl.sh).
# Run it any time with Backup-Spirebound.bat. Start-Spirebound.bat also runs it before each start.
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$wslRoot = "/mnt/" + $Root.Substring(0,1).ToLower() + $Root.Substring(2).Replace("\", "/")
& wsl.exe -d Ubuntu -u root -- bash "$wslRoot/tools/db_wsl.sh" backup "$wslRoot"
if ($LASTEXITCODE -ne 0) { throw "The backup did not work (see the message above)." }
