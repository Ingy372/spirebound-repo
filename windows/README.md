# Playing Spirebound on your PC

The game server runs inside **WSL** (the free Ubuntu that Windows keeps inside itself); the game client is a normal Windows program. Nothing is uploaded anywhere.

1. **Play:** double-click the **Play Spirebound** shortcut on the desktop (it runs `Start-Spirebound.bat`). It saves a backup, starts the server (a black window; leave it open), waits until the server is ready, then opens the client. The first start builds the server and the client and takes several minutes.
2. **Log in:** account `jay@localhost`, password `spirebound`. See `MORNING.md` for the list of test characters.
3. **Stop:** double-click **Stop Spirebound** (`Stop-Spirebound.bat`).

**Backups:** `Start-Spirebound.bat` saves a copy of your world into the `backups` folder before every start and keeps the newest 14. Double-click `Backup-Spirebound.bat` for one any time. To go back, stop the server and double-click `Restore-Spirebound.bat` (it saves the current state first). Do this before ending a season too.

How it fits together
- `tools/run_server_wsl.sh` (run by Start): copies the repo into WSL, builds the Linux server, makes sure the database and test accounts exist, starts the server and the local login service (`tools/login_server.py`, port 8080, which hands the character list to the client).
- `Install-Client.bat` builds only the client (Start does this by itself if the client is missing). The older `Install-Spirebound.bat` builds a fully native Windows server instead; it is not used right now.
- `tools/winui/*.ps1` are small helpers Claude uses to drive and screenshot the client for testing.

If something fails, copy the red text into `PLAYTEST.md` and Claude will fix it next session.
