# Takes the Spirebound website off the public internet again (undoes Open-Public-Website). Roadmap 7.1b.
$ts = "C:\Program Files\Tailscale\tailscale.exe"
& $ts funnel reset
Write-Host "The website is no longer public. Friends on your Tailscale network can still reach it." -ForegroundColor Green
Read-Host "Press Enter to close"
