# Puts the Spirebound website (sign-up, make another character, account security) on a public https:// address,
# using Tailscale Funnel (free; Tailscale gives the address and its certificate). Roadmap 7.1b.
# ONLY the website (port 8080 on this PC) goes public. The game port stays on your Tailscale network.
# Undo with Close-Public-Website.bat.
# The first time, Tailscale may print a link asking you to allow Funnel for your account: open it, click allow, run this again.
$ErrorActionPreference = "Stop"
$ts = "C:\Program Files\Tailscale\tailscale.exe"
if (-not (Test-Path $ts)) { Write-Host "Tailscale is not installed on this PC." -ForegroundColor Red; Read-Host "Press Enter to close"; exit 1 }
& $ts funnel --bg http://127.0.0.1:8080
Write-Host ""
Write-Host "Your public address is the https:// line above. Send that to players; they sign up there." -ForegroundColor Green
& $ts funnel status
Read-Host "Press Enter to close"
