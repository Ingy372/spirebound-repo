# Spirebound client-only setup for Windows (the server runs in WSL).
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


Say "Downloading the client (first run only, about 600 MB)"
$otcExeZip = Get-File $Pins["OTCLIENT_WINDOWS_ZIP"] "otclient-$OtcTag-windows.zip"
$otcSrcZip = Get-File "https://github.com/opentibiabr/otclient/archive/refs/tags/$OtcTag.zip" "otclient-$OtcTag-source.zip"
$assetsZip = Get-File $Pins["TIBIA_ASSETS_ZIP"] "tibia-assets-$($Pins['TIBIA_ASSETS_VERSION']).zip"
$tmp = Join-Path $Local "tmp"
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
    Copy-Item -Force (Join-Path $Root "client\modules\game_spirebound\bot\spirebound_report.lua") (Join-Path $vbot "vBot\spirebound_report.lua")
    $loader = Join-Path $vbot "_Loader.lua"
    $lt = [IO.File]::ReadAllText($loader)
    $lt = $lt.Replace('  "BotServer",' + "`n", '').Replace('  "BotServer",' + "`r`n", '')
    $lt = $lt.Replace('  "spy_level",' + "`n", '').Replace('  "spy_level",' + "`r`n", '')
    # Q16 / roadmap R15: no automatic sword-skill or spell rotation, no combo helper, no script editor
    foreach ($m in @('"AttackBot", -- last of major modules', '"combo",', '"ingame_editor",', '"pushmax",')) {
        $lt = $lt.Replace('  ' + $m + "`n", '').Replace('  ' + $m + "`r`n", '')
    }
    if (-not $lt.Contains('"spirebound_report"')) {
        $lt = $lt.Replace('  "cavebot_control_panel"', '  "cavebot_control_panel",' + "`n" + '  "spirebound_report"')
    }
    # M5 (DESIGN.md 12): in a player fight the helpers only heal. Bookmarks around the healing and eating scripts tell
    # the guard (loaded last) which helper jobs may keep running; everything else pauses during the fight.
    Copy-Item -Force (Join-Path $Root "client\modules\game_spirebound\bot\spirebound_mark.lua") (Join-Path $vbot "vBot\spirebound_mark.lua")
    Copy-Item -Force (Join-Path $Root "client\modules\game_spirebound\bot\spirebound_pvp_guard.lua") (Join-Path $vbot "vBot\spirebound_pvp_guard.lua")
    # B1: this client hangs when a wrapping label sits in a hidden bot tab; the override drops the wrapping and the
    # cavebot editor's one wrapping label gets a fixed height (the client module does the same for older installs)
    Copy-Item -Force (Join-Path $Root "client\modules\game_spirebound\bot\spirebound_fixes.otui") (Join-Path $vbot "vBot\spirebound_fixes.otui")
    $ed = Join-Path $vbot "cavebot\editor.otui"
    if (Test-Path $ed) {
        $et = [IO.File]::ReadAllText($ed).Replace("`r`n", "`n")
        $et = $et.Replace("    text: Double click on action from action list to edit it`n    text-align: center`n    text-auto-resize: true`n    text-wrap: true`n", "    text: Double-click an action to edit it`n    text-align: center`n    height: 14`n")
        [IO.File]::WriteAllText($ed, $et)
    }
    if (-not $lt.Contains('"spirebound_pvp_guard"')) {
        $lt = $lt.Replace('  "HealBot",', '  "spirebound_mark",' + "`n" + '  "HealBot",')
        $lt = $lt.Replace('  "new_healer",', '  "new_healer",' + "`n" + '  "spirebound_mark",')
        $lt = $lt.Replace('  "eat_food",', '  "spirebound_mark",' + "`n" + '  "eat_food",' + "`n" + '  "spirebound_mark",')
        $lt = $lt.Replace('  "spirebound_report"', '  "spirebound_mark",' + "`n" + '  "spirebound_report",' + "`n" + '  "spirebound_pvp_guard"')
    }
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
$serverLine = 'Servers_init = { ["127.0.0.1"] = { port = 8080, protocol = ' + $Pins['CLIENT_PROTOCOL'] + ', httpLogin = true } }'
$text = $text.Replace('g_app.setName("OTClient - Redemption");', $serverLine + "`r`n" + 'g_app.setName("Spirebound");')
$text = $text -replace "enabled = true,(\s*\r?\n\s*repository)", 'enabled = false,$1'
Set-Content -Encoding UTF8 -Path $init -Value $text


Say "Client ready in .local\client"

# Start the client in English (skips the language picker on the first run)
$cfgDir = Join-Path $env:APPDATA "otcr\otclient"
$cfg = Join-Path $cfgDir "config.otml"
if (-not (Test-Path $cfg)) {
    New-Item -ItemType Directory -Force -Path $cfgDir | Out-Null
    Set-Content -Encoding ASCII -Path $cfg -Value "locale: en"
}
