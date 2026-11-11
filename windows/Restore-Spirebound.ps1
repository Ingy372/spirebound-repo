# Puts back a saved copy of the Spirebound database. Stop the server first (Stop-Spirebound.bat).
# Usage: Restore-Spirebound.bat            -> restores the newest backup
#        Restore-Spirebound.bat <file.zip> -> restores that one
param([string]$File = "")
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot

function Read-EnvFile($path) {
    $h = @{}
    if (Test-Path $path) {
        foreach ($line in Get-Content $path) {
            $line = $line.Trim()
            if ($line -and -not $line.StartsWith("#") -and $line.Contains("=")) {
                $k, $v = $line.Split("=", 2); $h[$k.Trim()] = $v.Trim()
            }
        }
    }
    return $h
}

$LocalEnv = Read-EnvFile (Join-Path $Root "server\local.env")
if (-not $LocalEnv["MYSQL_DATABASE"]) { throw "Spirebound is not installed yet." }
if (Get-Process -Name canary -ErrorAction SilentlyContinue) { throw "The server is still running. Double-click Stop-Spirebound.bat first." }

if (-not $File) {
    $latest = Get-ChildItem (Join-Path $Root "backups") -Filter "spirebound_*.sql.zip" -ErrorAction SilentlyContinue | Sort-Object Name -Descending | Select-Object -First 1
    if (-not $latest) { throw "There are no backups yet." }
    $File = $latest.FullName
}
if (-not (Test-Path $File)) { throw "Cannot find $File" }

$dirs = Get-ChildItem "C:\Program Files" -Directory -Filter "MariaDB*" -ErrorAction SilentlyContinue | Sort-Object Name -Descending
$mysql = $null
foreach ($d in $dirs) { if (Test-Path (Join-Path $d.FullName "bin\mysql.exe")) { $mysql = Join-Path $d.FullName "bin\mysql.exe"; break } }
if (-not $mysql) { throw "Could not find MariaDB." }

# make a safety copy of what is there now, in case this was a mistake
& (Join-Path $PSScriptRoot "Backup-Spirebound.ps1")

$tmp = Join-Path $env:TEMP ("spirebound_restore_" + [guid]::NewGuid().ToString("N"))
Expand-Archive -Path $File -DestinationPath $tmp -Force
$sql = Get-ChildItem $tmp -Filter "*.sql" | Select-Object -First 1
$args = @("-u$($LocalEnv['MYSQL_USER'])", "-p$($LocalEnv['MYSQL_PASS'])", "-h127.0.0.1", $LocalEnv["MYSQL_DATABASE"])
Get-Content -Raw $sql.FullName | & $mysql @args
if ($LASTEXITCODE -ne 0) { throw "The restore failed. Your previous data was saved just now in the backups folder." }
Remove-Item -Recurse -Force $tmp
Write-Host "Restored from $File"
