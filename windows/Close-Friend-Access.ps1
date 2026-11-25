# Undoes Open-Friend-Access: removes the port forwards and the firewall rule. Run as administrator.
foreach ($p in 8080, 7172, 8090) {
    netsh interface portproxy show v4tov4 | Select-String "\s$p\s" | ForEach-Object {
        $addr = ($_.Line -split '\s+')[0]
        netsh interface portproxy delete v4tov4 listenaddress=$addr listenport=$p | Out-Null
    }
}
Get-NetFirewallRule -DisplayName "Spirebound over Tailscale" -ErrorAction SilentlyContinue | Remove-NetFirewallRule
Write-Host "Friend access closed." -ForegroundColor Green
Read-Host "Press Enter to close"
