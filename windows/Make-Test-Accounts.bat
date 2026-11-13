@echo off
rem DEV ONLY: puts back the local test account "jay" (GM character Jay plus test characters).
rem Start-Spirebound no longer does this by itself (roadmap R4). Start the server once first.
wsl.exe -d Ubuntu -u root -- bash /mnt/c/Users/Muth3/Desktop/spirebound-repo/tools/dev_accounts_wsl.sh
pause
