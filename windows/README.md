# Playing Spirebound on your PC

1. **Install (once):** double-click `Install-Spirebound.bat`. It downloads about 1 GB the first time and may ask Windows for permission to install MariaDB (the free database the server uses). When it says **Done!**, close the window.
2. **Play:** double-click `Start-Spirebound.bat`. A black server window opens (leave it open), then the game client.
3. **Log in:** account `jay`, password `spirebound`. Characters: **Jay** (gamemaster tools) and **Climber** (a brand-new character: talk to the Registrar).
4. **Stop:** double-click `Stop-Spirebound.bat`, or close the black server window.

After Claude pushes new work, run `Install-Spirebound.bat` again to rebuild (it skips the downloads).

Notes
- Everything installed lives in the hidden `.local` folder inside the repo, plus MariaDB under Program Files. Nothing is uploaded anywhere.
- The Tibia art in `.local\client` is a placeholder for testing on this PC only. Your Grok art replaces it before any public launch.
- Passwords for the local database are in `server\local.env` (never uploaded to GitHub).
- If something fails, copy the red text into `PLAYTEST.md` and Claude will fix it next session.
