# Puts back a saved copy of the Spirebound database. Stop the server first (Stop Spirebound).
# Usage: Restore-Spirebound.bat            -> restores the newest backup
#        Restore-Spirebound.bat <file.zip> -> restores that one
# The current state is saved first as a safety copy.
param([string]$File = "")
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$wslRoot = "/mnt/" + $Root.Substring(0,1).ToLower() + $Root.Substring(2).Replace("\", "/")
$wslFile = ""
if ($File) { $wslFile = "/mnt/" + $File.Substring(0,1).ToLower() + $File.Substring(2).Replace("\", "/") }
& wsl.exe -d Ubuntu -u root -- bash "$wslRoot/tools/db_wsl.sh" restore "$wslRoot" "$wslFile"
if ($LASTEXITCODE -ne 0) { throw "The restore did not work (see the message above)." }
