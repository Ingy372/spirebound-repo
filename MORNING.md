# Good morning, Jay

**Status: the game is playable on your PC.** The game window opens, you log in, and the Journal (press J) works. I tested all of this myself overnight with screenshots (in the `screenshots` folder).

## How to start
1. Double-click **Play Spirebound** on your desktop.
2. The first time, it builds the server and takes a few minutes. A black server window opens: **leave it open**. When the server is ready the game window opens by itself (the start also saves a backup first).
3. Log in (see the next section). The server window can stay minimised.
4. When you are done, double-click **Stop Spirebound** on your desktop.

If the game window never opens after about 10 minutes, look at the black server window for red text and tell me what it says.

## Logins (account for all characters)
- Account name: `jay@localhost` &nbsp; Password: `spirebound`
- Characters on that account: **Jay** (the gamemaster, level 2), **Climber** (brand-new, talk to Registrar Maelis), and ready-made level 30 testers: **Test Vanguard**, **Test Ranger**, **Test Arcanist**, **Test Mystic**, **Test Hardcore** (a Vanguard on Hardcore).
- These are on-this-PC test logins only. They live in `server\sql\dev_accounts.sql` (and the first-login kits in `server\data-spirebound\scripts\spirebound\dev_seed.lua`).
- The first time a Test character logs in, a "Customise Character" window pops up. Press Esc to close it.

## GM tricks (log in as **Jay**)
- `/floor clear 1` opens Floor 1's boss gate and stair; `/floor reset 1` puts it back (works for floors 1 to 10).
- `/goto Climber` teleports you to another player; `/i gold coin 1000` gives items; `/m rat` spawns a monster.
- Tip: for fighting tests use a Test character (level 30 with a weapon). Jay is only level 2.

## What to check (about 20 minutes)
1. **Journal.** Press **J**. A window called "Journal - Secrets" opens with six tabs along the top (Secrets, Fishing, Quests, Task, Top, Memorial). Click each one: each shows lines of text and none crashes the game. Press Esc to close. The top of the screen should say "Floor 1 - Hearthgate Plains [Safe zone]".
2. **Languages.** Click the chat bar at the bottom, type `!language pt` and press Enter. A message says "Idioma definido: Português (Brasil)." Press J: the tab names turn Portuguese (Segredos, Pesca, Missões...). Then `!language es` ("Idioma establecido: Español.") and `!language en` ("Language set to English."). Accents should look right (no strange characters).
3. **Shop.** Type `!shop`. You should see: "The shop opens when Spirebound launches. It sells cosmetics and house decorations only: never power." (The shop is closed on purpose until launch.)
4. **Backup and restore.**
   - Double-click `windows\Backup-Spirebound.bat`. A `.zip` file appears in the `backups` folder.
   - To test restore: log in as Test Vanguard and walk a few steps, **Stop Spirebound**, then double-click `windows\Restore-Spirebound.bat`. It says "Restored from ..." and saves a safety copy first. Start the game again: you are back where the backup was.
5. **Website (optional).** Open `website\public\index.html` in your browser.
6. **Fighting (optional).** Log in as Test Vanguard, leave town by any gate and hit rats with the left mouse button. Shift+1 to Shift+6 are the sword-skill buttons.

## Known rough spots
- The little coloured "cursor" markers over other players are switched off for now: updating them every second crashed the Windows client. They will still change when someone gets a skull. I will find a safe way next.
- The sword-skill bar and the NPC / quest / item text in Portuguese and Spanish are still unchecked or unfinished (see ROADMAP 6.3b).
- Everything runs on the free "Ubuntu" that Windows keeps inside itself (WSL). If Play Spirebound ever says it cannot find Ubuntu, tell me.

## If something breaks
Write what you saw in `PLAYTEST.md` (a screenshot path is plenty). Everything I did overnight is in `PROGRESS.md`.

## Also done overnight
- Registrar Maelis now speaks Portuguese and Spanish (say `!language pt`, then log in or talk to her).
- `DECISIONS.md` has my homework for you: shop prices, a crafting design, hosting options, art priority list. Just say yes/no.
- Not done: ROADMAP 6.4, 6.5b, 9.2 (reasons at the bottom of DECISIONS.md).
- The server's log is saved in `.local\server.log` if something looks wrong.
