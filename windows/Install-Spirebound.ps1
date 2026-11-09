# Spirebound one-click setup for Windows (roadmap 1.5).
# Double-click Install-Spirebound.bat instead of running this directly.
#
# What it does (all free software, nothing is bought):
#   1. Installs MariaDB (database) and the Microsoft C++ runtime with winget, if missing.
#   2. Downloads the pinned Canary server, OTClient Redemption and the Tibia client files
#      (placeholder art, stays on this PC only, never uploaded to GitHub).
#   3. Builds a ready-to-run server in .local\server and a client in .local\client.
#   4. Creates the database and the local test account  jay / spirebound.
# Safe to run again: it skips what is already done and rebuilds the server from the repo.

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"   # makes downloads much faster
$Root = Split-Path -Parent $PSScriptRoot
$Local = Join-Path $Root ".local"
$Dl = Join-Path $Local "downloads"
New-Item -ItemType Directory -Force -Path $Dl | Out-Null

function Say($msg) { Write-Host ""; Write-Host "== $msg" -ForegroundColor Cyan }
function Read-EnvFile($path) {
    $h = @{}
    if (Test-Path $path) {
        foreach ($line in Get-Content $path) {
            $t = $line.Trim()
            if ($t -and -not $t.StartsWith("#") -and $t.Contains("=")) {
                $k, $v = $t.Split("=", 2); $h[$k.Trim()] = $v.Trim()
            }
        }
    }
    return $h
}
function Get-File($url, $name) {
    $dest = Join-Path $Dl $name
    if ((Test-Path $dest) -and ((Get-Item $dest).Length -gt 1000)) { return $dest }
    Write-Host "   downloading $name ..."
    Invoke-WebRequest -Uri $url -OutFile "$dest.part" -UseBasicParsing
    Move-Item -Force "$dest.part" $dest
    return $dest
}
function Expand-To($zip, $dest) {
    if (Test-Path $dest) { Remove-Item -Recurse -Force $dest }
    Expand-Archive -Path $zip -DestinationPath $dest -Force
}

$Pins = Read-EnvFile (Join-Path $Root "server\PINS.env")
$Tag = $Pins["CANARY_TAG"]
$OtcTag = $Pins["OTCLIENT_TAG"]

# ---------------------------------------------------------------- 1. prerequisites
Say "Checking MariaDB and the C++ runtime"
$LocalEnvPath = Join-Path $Root "server\local.env"
$LocalEnv = Read-EnvFile $LocalEnvPath
function Find-MariaDbBin {
    $dirs = Get-ChildItem "C:\Program Files" -Directory -Filter "MariaDB*" -ErrorAction SilentlyContinue | Sort-Object Name -Descending
    foreach ($d in $dirs) { if (Test-Path (Join-Path $d.FullName "bin\mysql.exe")) { return (Join-Path $d.FullName "bin") } }
    return $null
}
$MyBin = Find-MariaDbBin
if (-not $MyBin) {
    if (-not $LocalEnv["MYSQL_ROOT_PASS"]) { $LocalEnv["MYSQL_ROOT_PASS"] = [guid]::NewGuid().ToString("N").Substring(0, 16) }
    Write-Host "   installing MariaDB (a Windows prompt may ask for permission)..."
    winget install -e --id MariaDB.Server --accept-package-agreements --accept-source-agreements --silent `
        --override "/quiet SERVICENAME=MariaDB PORT=3306 PASSWORD=$($LocalEnv['MYSQL_ROOT_PASS'])"
    $MyBin = Find-MariaDbBin
    if (-not $MyBin) { throw "MariaDB did not install. Install it from mariadb.org, then run this again." }
} elseif (-not $LocalEnv["MYSQL_ROOT_PASS"]) {
    $LocalEnv["MYSQL_ROOT_PASS"] = Read-Host "MariaDB is already installed. Type its root password (leave empty if none)"
}
winget list --id Microsoft.VCRedist.2015+.x64 -e *> $null
if ($LASTEXITCODE -ne 0) {
    winget install -e --id Microsoft.VCRedist.2015+.x64 --accept-package-agreements --accept-source-agreements --silent | Out-Null
}
$svc = Get-Service -Name "MariaDB*" -ErrorAction SilentlyContinue | Select-Object -First 1
if ($svc -and $svc.Status -ne "Running") { Start-Service $svc.Name }

if (-not $LocalEnv["MYSQL_PASS"]) { $LocalEnv["MYSQL_PASS"] = [guid]::NewGuid().ToString("N").Substring(0, 16) }
if (-not $LocalEnv["MYSQL_USER"]) { $LocalEnv["MYSQL_USER"] = "spire" }
if (-not $LocalEnv["MYSQL_DATABASE"]) { $LocalEnv["MYSQL_DATABASE"] = "spirebound" }
if (-not $LocalEnv["MYSQL_HOST"]) { $LocalEnv["MYSQL_HOST"] = "127.0.0.1" }
# local.env is git-ignored: passwords never reach GitHub
($LocalEnv.GetEnumerator() | Sort-Object Name | ForEach-Object { "$($_.Name)=$($_.Value)" }) | Set-Content -Encoding ASCII $LocalEnvPath

# ---------------------------------------------------------------- 2. downloads
Say "Downloading Canary $Tag, OTClient $OtcTag and the client files (first run only, about 1 GB)"
$canaryExeZip = Get-File $Pins["CANARY_WINDOWS_ZIP"] "canary-$Tag-windows.zip"
$canarySrcZip = Get-File "https://github.com/opentibiabr/canary/archive/refs/tags/$Tag.zip" "canary-$Tag-source.zip"
$otcExeZip = Get-File $Pins["OTCLIENT_WINDOWS_ZIP"] "otclient-$OtcTag-windows.zip"
$otcSrcZip = Get-File "https://github.com/opentibiabr/otclient/archive/refs/tags/$OtcTag.zip" "otclient-$OtcTag-source.zip"
$assetsZip = Get-File $Pins["TIBIA_ASSETS_ZIP"] "tibia-assets-$($Pins['TIBIA_ASSETS_VERSION']).zip"

# ---------------------------------------------------------------- 3a. server
Say "Building the server in .local\server"
$tmp = Join-Path $Local "tmp"
Expand-To $canarySrcZip $tmp
$src = Get-ChildItem $tmp -Directory | Select-Object -First 1
$Srv = Join-Path $Local "server"
$keepKey = $null
if (Test-Path (Join-Path $Srv "key.pem")) { $keepKey = Get-Content -Raw (Join-Path $Srv "key.pem") }
if (Test-Path $Srv) { Remove-Item -Recurse -Force $Srv }
New-Item -ItemType Directory -Force -Path $Srv | Out-Null
Expand-Archive -Path $canaryExeZip -DestinationPath $Srv -Force
foreach ($n in @("data", "config.lua.dist", "schema.sql", "LICENSE")) { Copy-Item -Recurse (Join-Path $src.FullName $n) $Srv }
# Canary's core files name Tibia's vocations; rename them to ours (same rules as tools/build_server.py)
$renames = @(@("master sorcerer","high arcanist"), @("elder druid","elder mystic"), @("royal paladin","far warden"),
             @("elite knight","blade warden"), @("sorcerer","arcanist"), @("druid","mystic"), @("paladin","ranger"), @("knight","vanguard"))
function Rename-Vocations([string]$text, [string]$pattern) {
    return [regex]::Replace($text, $pattern, {
        param($m)
        $chunk = $m.Value
        foreach ($r in $renames) {
            $chunk = [regex]::Replace($chunk, $r[0], {
                param($mm)
                $new = $r[1]
                if ([char]::IsUpper($mm.Value[0])) { (Get-Culture).TextInfo.ToTitleCase($new) } else { $new }
            }, "IgnoreCase")
        }
        return $chunk
    })
}
$itemsXml = Join-Path $Srv "data\items\items.xml"
[IO.File]::WriteAllText($itemsXml, (Rename-Vocations ([IO.File]::ReadAllText($itemsXml)) 'key="vocation" value="[^"]*"'))
foreach ($f in Get-ChildItem (Join-Path $Srv "data\scripts\runes"), (Join-Path $Srv "data\scripts\weapons") -Recurse -Filter *.lua) {
    [IO.File]::WriteAllText($f.FullName, (Rename-Vocations ([IO.File]::ReadAllText($f.FullName)) 'vocation\([^)]*\)'))
}
# Tibia's spells are replaced by Spirebound's own
Remove-Item -Recurse -Force (Join-Path $Srv "data\scripts\spells") -ErrorAction SilentlyContinue
Copy-Item -Recurse (Join-Path $Root "server\data-spirebound") (Join-Path $Srv "data-spirebound")
Copy-Item -Recurse -Force (Join-Path $Root "server\core-overrides\*") (Join-Path $Srv "data")
$world = Join-Path $Srv "data-spirebound\world"
if (-not (Test-Path (Join-Path $world "spirebound.otbm"))) {
    # fallback only: Canary's sample map
    Copy-Item (Join-Path $src.FullName "data-canary\world\canary.otbm") (Join-Path $world "spirebound.otbm")
    foreach ($k in @("monster", "npc", "house", "zones")) { Copy-Item (Join-Path $world "spirebound-$k.xml") (Join-Path $world "canary-$k.xml") }
}
if ($keepKey) { Set-Content -NoNewline -Path (Join-Path $Srv "key.pem") -Value $keepKey }

# config.lua = Canary defaults + server\config-overrides.lua (same rules as tools/build_server.py)
$cfg = Get-Content -Raw (Join-Path $Srv "config.lua.dist")
foreach ($raw in Get-Content (Join-Path $Root "server\config-overrides.lua")) {
    $line = $raw.Trim()
    if (-not $line -or $line.StartsWith("--") -or -not $line.Contains("=")) { continue }
    $key, $val = $line.Split("=", 2); $key = $key.Trim(); $val = $val.Trim()
    foreach ($k in @("MYSQL_HOST", "MYSQL_USER", "MYSQL_PASS", "MYSQL_DATABASE")) { $val = $val.Replace("@$k@", $LocalEnv[$k]) }
    if ($key.StartsWith("+")) { $cfg += "`n$($key.Substring(1)) = $val`n"; continue }
    $rx = [regex]("(?m)^" + [regex]::Escape($key) + "\s*=.*$")
    if (-not $rx.IsMatch($cfg)) { throw "config override '$key' is not a Canary setting" }
    $cfg = $rx.Replace($cfg, "$key = $val", 1)
}
Set-Content -Encoding UTF8 -Path (Join-Path $Srv "config.lua") -Value $cfg
Remove-Item -Recurse -Force $tmp

# ---------------------------------------------------------------- 3b. client
Say "Building the client in .local\client"
$Cli = Join-Path $Local "client"
Expand-To $otcSrcZip $tmp
$osrc = Get-ChildItem $tmp -Directory | Select-Object -First 1
if (Test-Path $Cli) { Remove-Item -Recurse -Force $Cli }
New-Item -ItemType Directory -Force -Path $Cli | Out-Null
foreach ($n in @("data", "modules", "mods", "init.lua", "otclientrc.lua", "LICENSE")) {
    $p = Join-Path $osrc.FullName $n
    if (Test-Path $p) { Copy-Item -Recurse $p $Cli }
}
Expand-Archive -Path $otcExeZip -DestinationPath $Cli -Force
Remove-Item -Recurse -Force $tmp
# Spirebound client modules (floor indicator, sword-skill bar, cursors) arrive in roadmap task 1.20
if (Test-Path (Join-Path $Root "client\modules")) { Copy-Item -Recurse -Force (Join-Path $Root "client\modules\*") (Join-Path $Cli "modules") }

# Built-in bot (vBot): report cavebot use to the server, remove the external bot server and the floor spy, keep one config
$botCfg = Join-Path $Cli "mods\game_bot\default_configs"
if (Test-Path $botCfg) {
    Remove-Item -Recurse -Force (Join-Path $botCfg "cavebot_1.3") -ErrorAction SilentlyContinue
    $vbot = Join-Path $botCfg "vBot_4.8"
    Copy-Item -Force (Join-Path $Root "client\bot\spirebound_report.lua") (Join-Path $vbot "vBot\spirebound_report.lua")
    $loader = Join-Path $vbot "_Loader.lua"
    $lt = [IO.File]::ReadAllText($loader)
    $lt = $lt.Replace('  "BotServer",' + "`n", '').Replace('  "BotServer",' + "`r`n", '')
    $lt = $lt.Replace('  "spy_level",' + "`n", '').Replace('  "spy_level",' + "`r`n", '')
    $lt = $lt.Replace('  "cavebot_control_panel"', '  "cavebot_control_panel",' + "`n" + '  "spirebound_report"')
    [IO.File]::WriteAllText($loader, $lt)
}

# client files (placeholder Tibia art) into data\things\<protocol>
$things = Join-Path $Cli ("data\things\" + $Pins["CLIENT_PROTOCOL"])
Expand-To $assetsZip $tmp
$assets = Get-ChildItem $tmp -Recurse -Filter "catalog-content.json" | Select-Object -First 1
if (-not $assets) { throw "client files not found in the download" }
New-Item -ItemType Directory -Force -Path $things | Out-Null
Copy-Item -Recurse -Force (Join-Path $assets.DirectoryName "*") $things
Remove-Item -Recurse -Force $tmp

# point the client at this PC and turn off its own asset downloader
$init = Join-Path $Cli "init.lua"
$text = Get-Content -Raw $init
$serverLine = 'Servers_init = { ["127.0.0.1"] = { port = 7171, protocol = ' + $Pins['CLIENT_PROTOCOL'] + ', httpLogin = false } }'
$text = $text.Replace('g_app.setName("OTClient - Redemption");', $serverLine + "`r`n" + 'g_app.setName("Spirebound");')
$text = $text -replace "enabled = true,(\s*\r?\n\s*repository)", 'enabled = false,$1'
Set-Content -Encoding UTF8 -Path $init -Value $text

# ---------------------------------------------------------------- 4. database
Say "Setting up the database"
$mysql = Join-Path $MyBin "mysql.exe"
$rootArgs = @("-uroot", "-h127.0.0.1")
if ($LocalEnv["MYSQL_ROOT_PASS"]) { $rootArgs += "-p$($LocalEnv['MYSQL_ROOT_PASS'])" }
$db = $LocalEnv["MYSQL_DATABASE"]; $user = $LocalEnv["MYSQL_USER"]; $pass = $LocalEnv["MYSQL_PASS"]
& $mysql @rootArgs -e "CREATE DATABASE IF NOT EXISTS ``$db``; CREATE USER IF NOT EXISTS '$user'@'localhost' IDENTIFIED BY '$pass'; CREATE USER IF NOT EXISTS '$user'@'127.0.0.1' IDENTIFIED BY '$pass'; GRANT ALL ON ``$db``.* TO '$user'@'localhost'; GRANT ALL ON ``$db``.* TO '$user'@'127.0.0.1'; FLUSH PRIVILEGES;"
if ($LASTEXITCODE -ne 0) { throw "Could not log in to MariaDB as root. Check MYSQL_ROOT_PASS in server\local.env." }
$userArgs = @("-u$user", "-p$pass", "-h127.0.0.1", $db)
$has = & $mysql @userArgs -N -e "SHOW TABLES LIKE 'server_config'"
if (-not $has) { Get-Content -Raw (Join-Path $Srv "schema.sql") | & $mysql @userArgs }
Get-Content -Raw (Join-Path $Root "server\sql\dev_accounts.sql") | & $mysql @userArgs

Say "Done!"
Write-Host "   Start the game with Start-Spirebound.bat (in the windows folder)."
Write-Host "   Log in with account  jay  and password  spirebound"
Write-Host "   Characters: Jay (gamemaster) and Climber (new player)"
