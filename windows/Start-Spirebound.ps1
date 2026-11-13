# Starts the Spirebound game server (inside WSL), waits until it is ready, then opens the game client.
# Run through "Play Spirebound" (the desktop shortcut) or Start-Spirebound.bat.
$ErrorActionPreference = "Continue"
$Root = Split-Path -Parent $PSScriptRoot
$Client = Join-Path $Root ".local\client\otclient.exe"

function Say($m) { Write-Host $m -ForegroundColor Cyan }
function PortOpen($port) {
    try { $c = New-Object Net.Sockets.TcpClient; $r = $c.BeginConnect("127.0.0.1", $port, $null, $null)
          $ok = $r.AsyncWaitHandle.WaitOne(1500) -and $c.Connected; $c.Close(); return $ok } catch { return $false }
}
function Ready { (PortOpen 8080) -and (PortOpen 7172) }

if (-not (Test-Path $Client)) {
    Say "The game client is not installed yet. Running the client setup first (about 600 MB, one time)..."
    & (Join-Path $PSScriptRoot "Install-Client.ps1")
    if (-not (Test-Path $Client)) { Write-Host "Client setup failed. Tell Claude what the red text above says." -ForegroundColor Red; Read-Host "Press Enter to close"; exit 1 }
}

if (Ready) {
    Say "The server is already running."
} else {
    Say "Saving a backup of your world first..."
    try { & (Join-Path $PSScriptRoot "Backup-Spirebound.ps1") } catch { Write-Host "(No backup this time: $($_.Exception.Message) The game will still start.)" -ForegroundColor Yellow }
    $wslRoot = "/mnt/" + $Root.Substring(0,1).ToLower() + $Root.Substring(2).Replace("\", "/")
    Say "Starting the server (a black window will stay open while you play - leave it open)..."
    Start-Process wsl.exe -ArgumentList @("-d", "Ubuntu", "-u", "root", "--", "bash", "$wslRoot/tools/run_server_wsl.sh", "$wslRoot")
    Say "Waiting for the server to come online (the first start takes a few minutes)..."
    $t0 = Get-Date
    while (-not (Ready)) {
        if (((Get-Date) - $t0).TotalSeconds -gt 600) { Write-Host "The server did not come online in 10 minutes. Look at the black server window for red text." -ForegroundColor Red; Read-Host "Press Enter to close"; exit 1 }
        Start-Sleep 3
    }
    Start-Sleep 5   # let the server finish loading its scripts
}
# Spirebound's own client windows (Journal, task window, skill bar) change often: copy the latest every start
$Mods = Join-Path $Root "client\modules"
if (Test-Path $Mods) { Copy-Item -Recurse -Force (Join-Path $Mods "*") (Join-Path (Split-Path $Client) "modules") }
Say "Opening the game..."
Start-Process $Client -WorkingDirectory (Split-Path $Client)
Write-Host ""
Write-Host "Log in with account:  jay@localhost   password:  spirebound   (see TEST_LOGINS in MORNING.md)" -ForegroundColor Green
Start-Sleep 6
