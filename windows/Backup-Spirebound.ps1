# Saves a copy of the Spirebound database (characters, houses, guilds, market, world progress)
# into the "backups" folder next to the repo, and keeps the newest 14 copies.
# Run it any time with Backup-Spirebound.bat. Start-Spirebound.bat also runs it before each start.
# Restore with Restore-Spirebound.bat.
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
if (-not $LocalEnv["MYSQL_DATABASE"]) { throw "Spirebound is not installed yet (server\local.env is missing). Run Install-Spirebound.bat first." }

$dirs = Get-ChildItem "C:\Program Files" -Directory -Filter "MariaDB*" -ErrorAction SilentlyContinue | Sort-Object Name -Descending
$bin = $null
foreach ($d in $dirs) { if (Test-Path (Join-Path $d.FullName "bin\mariadb-dump.exe")) { $bin = Join-Path $d.FullName "bin\mariadb-dump.exe"; break }
                         if (Test-Path (Join-Path $d.FullName "bin\mysqldump.exe")) { $bin = Join-Path $d.FullName "bin\mysqldump.exe"; break } }
if (-not $bin) { throw "Could not find MariaDB's dump tool. Is MariaDB installed?" }

$out = Join-Path $Root "backups"
New-Item -ItemType Directory -Force -Path $out | Out-Null
$stamp = Get-Date -Format "yyyy-MM-dd_HH-mm"
$file = Join-Path $out "spirebound_$stamp.sql"

& $bin "-u$($LocalEnv['MYSQL_USER'])" "-p$($LocalEnv['MYSQL_PASS'])" -h127.0.0.1 --single-transaction --routines "--result-file=$file" $LocalEnv["MYSQL_DATABASE"]
if ($LASTEXITCODE -ne 0 -or -not (Test-Path $file) -or (Get-Item $file).Length -lt 1000) {
    throw "The backup did not work. Is the server's database running? (Start-Spirebound.bat starts it.)"
}
Compress-Archive -Path $file -DestinationPath "$file.zip" -Force
Remove-Item $file
Write-Host "Backup saved: $file.zip"

# keep the newest 14
Get-ChildItem $out -Filter "spirebound_*.sql.zip" | Sort-Object Name -Descending | Select-Object -Skip 14 | Remove-Item -Force
