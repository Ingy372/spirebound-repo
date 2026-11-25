# Restarts the Spirebound server without opening the game client (for Claude's tests; Jay, 2026-11-24, CLAUDE.md 6a).
# Saves and stops the server, backs up the world, starts it again in the background and waits until it is online.
$ErrorActionPreference = "Continue"
$Root = Split-Path -Parent $PSScriptRoot
function PortOpen($port) {
    try { $c = New-Object Net.Sockets.TcpClient; $r = $c.BeginConnect("127.0.0.1", $port, $null, $null)
          $ok = $r.AsyncWaitHandle.WaitOne(1500) -and $c.Connected; $c.Close(); return $ok } catch { return $false }
}
function Ready { (PortOpen 8080) -and (PortOpen 7172) }

Write-Host "Stopping the server (it saves the world as it shuts down)..."
$wslStop = "/mnt/" + $Root.Substring(0,1).ToLower() + $Root.Substring(2).Replace("\", "/") + "/tools/stop_server_wsl.sh"
wsl.exe -d Ubuntu -u root -- bash -c "tr -d '\r' < $wslStop | bash"   # (Windows line endings would break bash)
if (Ready) { Start-Sleep 5 }
try { & (Join-Path $PSScriptRoot "Backup-Spirebound.ps1") } catch { Write-Host "(No backup this time: $($_.Exception.Message))" }
$wslRoot = "/mnt/" + $Root.Substring(0,1).ToLower() + $Root.Substring(2).Replace("\", "/")
Start-Process wsl.exe -WindowStyle Minimized -ArgumentList @("-d", "Ubuntu", "-u", "root", "--", "bash", "$wslRoot/tools/run_server_wsl.sh", "$wslRoot")
$t0 = Get-Date
while (-not (Ready)) {
    if (((Get-Date) - $t0).TotalSeconds -gt 600) { Write-Host "FAIL: the server did not come online in 10 minutes (.local\server.log)"; exit 1 }
    Start-Sleep 3
}
Start-Sleep 5
# the client's Spirebound modules and spell effects, as Start-Spirebound does
$Client = Join-Path $Root ".local\client\otclient.exe"
$Mods = Join-Path $Root "client\modules"
if ((Test-Path $Mods) -and (Test-Path $Client)) { Copy-Item -Recurse -Force (Join-Path $Mods "*") (Join-Path (Split-Path $Client) "modules") }
wsl.exe -d Ubuntu -u root -- python3 "$wslRoot/tools/install_effects.py" client "$wslRoot/.local/client"
Write-Host "Server online."
