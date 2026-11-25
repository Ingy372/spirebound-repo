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

## Accounts (2026-11-13)
- **Make an account:** while the server is running, open http://localhost:8080/signup in a browser on this PC.
- **Test accounts:** starting the server no longer resets the test account "jay". If you ever need it back, double-click `Make-Test-Accounts.bat` (local testing only; its password is public).

## A Grok play tester (optional, costs a little per run)
Grok can play a brand-new character on your server and write a playtest report, like a first-time player would.
1. Sign in at console.x.ai (your X account works). This is xAI's developer site; your Grok subscription does **not**
   include it. Add some credits under Billing and set a spending limit there.
2. Create an API key (it starts with `xai-`).
3. Double-click `windows\Grok-Playtest.bat`. The first time, it opens `server\local.env` in Notepad: replace
   `paste-your-key-here` with your key and save. (That file never goes to GitHub.)
4. Start the server (`Start-Spirebound.bat`), then double-click `Grok-Playtest.bat` again. A game window opens and
   Grok plays for up to 40 minutes (60 moves). Don't use the game window while it plays.
5. The report lands in `docs\playtests\` (the newest `grok_` file). Tell Claude it's there.

## Friends and a Grok Bot over Tailscale (roadmap 9.1)
Players on your private Tailscale network can join your server; nobody else on the internet can, and your home
address is never shown. The same steps work for a friend (on Windows they use the normal client package) and for a
Grok Bot (its cloud computer runs Linux; the setup script installs the client with Wine).

**Once:**
1. Open Tailscale from the Start menu on this PC and make sure it says *Connected*.
2. Restart the server (Stop-Spirebound, then Start-Spirebound).
3. Double-click `windows\Open-Friend-Access.bat` and click *Yes* on the administrator prompt. It shows your
   Tailscale address (starts with 100.). It only opens the game's ports, and only on that address.
4. In the Tailscale admin console (login.tailscale.com) under **Access controls**, keep the bot away from your other
   devices: add `"tag:grokbot": ["autogroup:admin"]` to `"tagOwners"`, make sure the general rule is for
   `"autogroup:member"` (not `"*"`), and add the rule
   `{"action": "accept", "src": ["tag:grokbot"], "dst": ["YOUR-100-ADDRESS:8080,7172,8090"]}`.
5. Under **Settings > Keys**, generate an auth key: *Ephemeral* on, *Reusable* off, tag `tag:grokbot`.

**Each time a tester installs:**
1. Double-click `windows\Share-Client.bat` and leave its window open (it builds the client package and shares it on
   your Tailscale address). Close it when they've installed.
2. For a Grok Bot: open `.local\grok_bot_brief.txt` (Share-Client writes it), replace `PASTE-THE-TAILSCALE-KEY-HERE`
   with the key from step 5, and paste the whole text to your Grok Bot. Its account is `grokbot` (password in the
   brief); its character is "Grok Tester".
3. When the bot sends its report, save it in `docs\playtests\` or paste it to Claude.

To shut it again: `windows\Close-Friend-Access.bat`.
