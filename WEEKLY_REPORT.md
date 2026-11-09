# Weekly report — week of 2026-11-08 (Phases 1–5 built, plus the season reset; ready for your playtest)

## What's new
- **Floor 1 is playable from start to finish (on the test server in my cloud workspace; not yet run on your PC).** You create a character, pick a vocation and difficulty, level on Floor 1, kill the Gate Hound to open the labyrinth, climb its 3 levels, kill the Axe-Lord, and the whole server gets the "Floor 1 cleared" announcement while the stair to Floor 2 opens.
- **Map:** a script-made Floor 1 (Hearthgate, Millcross, river, 3 starter fields, 6 hunting camps, the Old Watchtower apex spawn with a hidden cave, the Pass, the labyrinth, the boss room, the Floor 2 landing). Preview: `docs/previews/floor1_z7.png`. Placeholder art and walls.
- **People and monsters:** 7 NPCs in Hearthgate (Registrar, priest, banker, merchant, quartermaster, weaponsmith, armorer), 13 monsters + 2 bosses, 116 spawned at once.
- **Fighting:** 24 sword skills (combos) + 42 spells that unlock by level (utility and support included), party XP bonus, difficulty bonuses, Death Game rules.
- **Client:** floor name at the top, sword-skill bar at the bottom (Shift+1..6), SAO cursors, Hardcore/Death Game label.
- **Design updates from your answers:** seasons confirmed; cavebot built in at 45% XP with no marker; spells by level; no conjured ammo; research on top servers added (DESIGN.md §15).
- **Phase 2, also built overnight:** PvP zones (shown on screen), weighted skulls and murderer penalties, newbie protection to 50, the 70% level-range rule, the outnumbered shield, guild Sanctuary, the bounty board (Bounty Warden Cass), consent guild wars (Guildwarden Sela), 12 Floor 1 secrets + Vesper the Info Broker, fishing, the Underkeep's first wing, 3 story quests with quest-log steps + the Floor 1 perk, the cavebot rules (45% XP, reported by the client's built-in bot), autoloot with rare-drop alerts, daily hunting tasks (Taskmaster Ren), catch-up rules for new players.
- **Phase 3 (houses):** `!buyhouse` with a one-hour head start for the players who cleared a new floor; House Portal (3 changes ever), Summoning Circle for private boss rematches with Boss Sigils, Fortune Hall gambling (gold only, bank to bank), Open House, guild bank, recruiting board, World/Mundo/Trade/Help/LFG chat.
- **Phases 4–5 (all 10 launch floors, placeholder maps):** every floor has a town with 8 NPCs and 6 houses, camps, a lake, an apex spawn, the Pass and its field boss, a 3-level maze and the floor boss. Azhrakkar waits on Floor 10. 27 story quests, 108 secrets, 63 fish, 18 perks, 48 sword skills + 3 Twin Fang skills, 56 spells (Lost Arts after the Floor 5 and Floor 8 story quests), the Twin Fang trial on Floor 8, Underkeep Wings 2–6, world events, weekend bonuses, the Saturday Fishing Derby, offline training statues. 1,115 monsters and 76 NPCs in the world. Previews: `docs/previews/floor2_z7.png` … `floor10_z7.png`.
- **Season reset (Phase 8):** `/season end <number>` archives everyone to the Hall of Seasons, keeps account titles, wipes the rest. Don't run it on the real server until we decide a season is over.
- Every change passes the automatic boot test (server online, 0 errors, now 54 in-game checks).

## Playtest checklist (about 45 minutes)
1. **Install / update (10 min):** double-click `windows\Install-Spirebound.bat`, wait for **Done!**. Then `Start-Spirebound.bat`. Log in: `jay` / `spirebound`.
2. **New character (10 min):** pick **Climber**. In the temple say `hi` to **Registrar Maelis** → pick a vocation → pick a difficulty (try Normal). Check the floor name at the top of the screen and the skill bar at the bottom.
3. **Hunt (10 min):** leave town by any gate. Kill rats/toads in the fields. Try a sword skill with Shift+1 (or type its name). Reach level 8 and check you get "New spell" messages. Visit the shops (say `hi`, then `trade`).
4. **Boss run as a GM (10 min):** log in as **Jay** (gamemaster). Go north up the road to the Pass (walled arena) and kill the **Gate Hound**: the boulders north of the arena should vanish with an announcement. Go through the maze (blue portals take you up), kill the **Axe-Lord**, watch for the gold "Floor 1 has been cleared" message, and step on the portal behind him to reach Floor 2's landing. (Shortcut if a fight is too hard: say `/floor field 1` or `/floor clear 1`; `/floor reset 1` puts it back.)
5. **Higher floors as a GM (optional, 10 min):** as Jay, say `/floor clear 1` … `/floor clear 9`, then walk the stairs from each boss room to see Floors 2–10. Try `!buyhouse` facing a house door in Hearthgate, then `!openhouse`.
6. **Phase 2 extras, if you have time (optional):** say `hi` to Vesper, Bounty Warden Cass, Guildwarden Sela and Taskmaster Ren near the Monument; fish in the river (buy a rod and worms from Merchant Wenna, use the rod on water, use it again when "Something is biting!"); step on the drain grate in the south-west corner of town.
7. **Notes (5 min):** in `PLAYTEST.md` write what felt good, what felt bad, and any error text. Short is fine.

## Open questions (my recommendation is in use until you answer; details in QUESTIONS.md)
- **Q1 (please):** give Claude GitHub access to `spirebound-repo` or push from GitHub Desktop. All of tonight's work (about 25 commits) is only on your PC.
- **Q11:** keep the 10-minute cavebot linger? (recommend yes)
- **Q12:** features from the top-server research (recommend keep all; hunting tasks come back; no character bazaar).
- Q2 stray Dojo-game branch · Q5 FYI · Q6 Twin Fang 3/season · Q7 newer Tibia systems off · Q8 difficulty bonuses · Q9 PvP protection numbers.

## Art and map requests
- **Art batch 1** (`ART_REQUESTS.md`): 4 vocation outfits, 13 Floor 1 monsters, Gate Hound, Axe-Lord (two forms), NPCs. **Batch 2**: cursors, floor badge, skill frames. Prompts ready for Grok.
- **Art batches 3–4**: Floors 2–10 monsters and bosses, Twin Fang, house items.
- **Maps** (`MAP_REQUESTS.md`): real Floor 1 (M1), Underkeep Wing 1 (M2), M3–M4 for the higher floors. The generated placeholder works in the meantime.
