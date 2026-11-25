# Lets players on your Tailscale network (friends, a Grok Bot) reach the Spirebound server on this PC (roadmap 9.1).
# Must run as administrator (Open-Friend-Access.bat asks). It does two things, both only for this PC's Tailscale
# address, so nothing is opened to the rest of the internet:
#   1. forwards the game's ports (8080 login, 7172 game, 8090 client download) from the Tailscale address to the server;
#   2. allows those ports through Windows Firewall, on the Tailscale address only.
# Undo with Close-Friend-Access.bat.
$ErrorActionPreference = "Stop"
$ts = "C:\Program Files\Tailscale\tailscale.exe"
$ip = (& $ts ip -4 2>$null | Select-Object -First 1)
if (-not $ip -or $ip -notmatch '^100\.') {
    Write-Host "Tailscale is not connected on this PC. Open Tailscale from the Start menu, sign in, then run this again." -ForegroundColor Red
    Read-Host "Press Enter to close"; exit 1
}
$ip = $ip.Trim()
$ports = 8080, 7172, 8090
foreach ($p in $ports) {
    netsh interface portproxy delete v4tov4 listenaddress=$ip listenport=$p 2>$null | Out-Null
    netsh interface portproxy add v4tov4 listenaddress=$ip listenport=$p connectaddress=127.0.0.1 connectport=$p | Out-Null
}
Get-NetFirewallRule -DisplayName "Spirebound over Tailscale" -ErrorAction SilentlyContinue | Remove-NetFirewallRule
New-NetFirewallRule -DisplayName "Spirebound over Tailscale" -Direction Inbound -Protocol TCP -LocalPort $ports -LocalAddress $ip -Action Allow | Out-Null
Write-Host "Done. Players on your Tailscale network can reach the server at $ip (ports 8080, 7172, 8090)." -ForegroundColor Green
Read-Host "Press Enter to close"
