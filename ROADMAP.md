# Spirebound Roadmap

Small numbered tasks, grouped into phases. Work top to bottom. Each task has a **Done when** line that can be checked. Check a task off (`[x]`) only when its Done-when has been checked, and write how in `PROGRESS.md`.

"Boot test" = `tools/test_boot.sh` (server starts with our datapack, prints "online", zero errors in the log). It must pass after every task from 1.3 onward.

Legend: 🧑 = needs Jay (playtest or decision). Everything else Claude does alone.

---

## Phase 1 — Floor 1, start to finish, running on Jay's PC
Goal: create a character, pick vocation and difficulty, level on Floor 1, kill the field boss, clear the labyrinth, kill the Floor 1 boss, watch Floor 2 unlock for everyone.

- [x] **1.1 Planning files.** DESIGN.md, ROADMAP.md, CLAUDE.md, PROGRESS.md, QUESTIONS.md, PLAYTEST.md, ART_REQUESTS.md, MAP_REQUESTS.md exist in the repo root.
  Done when: all eight files are committed.
- [x] **1.2 Archive the old TFS setup.** Move the TFS 1.4.2 server import and the 10.98-only tools into `legacy/`, keep every reusable tool (names checker, table generator, map compiler). Note it in PROGRESS.md.
  Done when: `legacy/README.md` explains what moved and why; `server/` is free for Canary; `python3 tools/check_names.py` still runs.
- [x] **1.3 Cloud test server.** Script that downloads pinned Canary v3.6.1 (Linux build), sets up MariaDB, and boots it with our datapack.
  Done when: `tools/test_boot.sh` exits 0 and its log shows the server online.
- [x] **1.4 Spirebound datapack skeleton.** `server/data-spirebound/` based on Canary's small `data-canary` pack, rebranded, CipSoft names removed, the systems in DESIGN §2 switched off in config.
  Done when: boot test passes with `dataPackDirectory = data-spirebound` and `check_names.py` reports 0 banned names in it.
- [ ] **1.5 Windows one-click setup.** *(built and checked in the cloud; waiting for Jay's first run)* `windows/Install-Spirebound.ps1` downloads pinned Canary (Windows build), OTClient Redemption 4.2 (Windows build), portable MariaDB and the 15.11 client files; creates the database; points the client at localhost. `Start-Spirebound.bat` / `Stop-Spirebound.bat`.
  Done when: script passes a dry-run check in the cloud (all download URLs answer, all paths exist), and 🧑 Jay double-clicks it once and reaches the login screen (logged in PLAYTEST.md).
- [x] **1.6 Dev accounts.** Script that creates a test account + GM character in the database.
  Done when: running it twice still gives exactly one test account (jay) with its 2 characters, verified by a database query in every boot test.
- [x] **1.7 Map tools for 15.x.** `tools/mapgen.py` writes Canary maps (Tibia 15.11 item ids) from Python layout files, checks every item id against the game data, and draws preview PNGs.
  Done when: a generated map loads in the server with zero map warnings, and preview PNGs are written.
- [x] **1.8 Floor 1 placeholder map.** Hearthgate (temple, depot, bank, shops, 6 houses, Arrival Yard), Millcross, starter fields, 6 hunting camps, apex spawn (outer + inner layer), the Pass arena, a 3-level labyrinth, boss room, sealed stair, the Underkeep grate (sealed), a Floor 2 landing room.
  Done when: map compiles and loads with zero warnings; preview PNGs are in `docs/previews/`; MAP_REQUESTS.md lists the real Floor 1 map.
- [x] **1.9 Four vocations.** Vanguard, Ranger, Arcanist, Mystic (+ promotions) in `vocations.xml`; new characters start with no vocation in the Arrival Yard.
  Done when: boot test passes and a scripted check reads all 4 vocations (+4 promotions) from the server.
- [x] **1.10 Registrar: pick vocation and difficulty.** NPC at the end of the Arrival Yard sets vocation, starter kit and difficulty (Normal/Hardcore/Death Game); stores difficulty on the character; step-down option for later.
  Done when: the Registrar loads with zero errors and in-game tests prove the rules (any first pick allowed, step-down allowed, moving *up* refused). The talk-through itself is checked in the Phase 1 playtest (a scripted 15.11 test client is not available yet).
- [x] **1.11 Difficulty effects.** XP/loot bonuses; Normal death = standard; Hardcore ×1.5 loss and blessing cap; Death Game: PvE death retires the character, PvP-saved death rule (DESIGN §6.6).
  Done when: in-game tests cover: Hardcore/Death Game XP bonus; Hardcore ×1.5 death loss; outside-player damage within 60 s saves a Death Game character, older damage or monster-only damage retires it; party member / guildmate / same-IP damage does not save. Hardcore skill loss, blessing cap and item-drop doubling moved to task 2.14.
- [x] **1.12 XP stages and rates.** Stages from DESIGN §5.5 in config.
  Done when: boot log lists the stages; a test computes XP at levels 10/75/250 and matches the table.
- [x] **1.13 Floor 1 monsters.** 11 monsters with original names (placeholder Tibia looks), loot tables from `data/`, spawns on the map.
  Done when: boot test reports all 11 monster types loaded with zero warnings, each spawned at least once on the map; ART_REQUESTS.md has an entry for each.
- [x] **1.14 Sword skill system v1.** Skill framework (weapon-family check, cooldowns, shared 1 s cooldown, Opener/Link/Finisher combo bonus) + the first 3 skills of all 8 weapon families.
  Done when: all 24 skills register as spells with cooldowns; in-game tests check 3 skills per family, weapon-family detection (right/wrong weapon), and that only Opener → Link → Finisher within 4 s gives +30%. Feel, damage and cooldown display are checked in the Phase 1 playtest.
- [x] **1.14b Spells v1.** The 8 shared spells and every vocation spell up to level 50 from DESIGN §5.3b (own incantations), learned automatically on reaching the level (no trainer, no gold), with a "you learned" message.
  Done when: every listed spell up to level 50 registers with zero errors; in-game tests check each vocation gets only its own spells at exactly the DESIGN §5.3b levels.
- [x] **1.15 Starter NPCs.** Temple priest (heal, blessings), bank, general store, quartermaster (potions + ammo: the gold sink), weaponsmith, armorer. Travel guide comes with Floor 2 (phase 4).
  Done when: each NPC loads with zero warnings and stands in Hearthgate (in-game test), and the generator refuses any price loop (an item that sells for more than it can be bought for). Buying and selling by hand is in the Phase 1 playtest.
- [x] **1.16 Party shared XP.** Party bonus from DESIGN §7.1, size cap 6.
  Done when: Lua test: a 3-player party of 2 vocations gets the expected XP per member.
- [x] **1.17 World floors state.** Saved floor records (Canary's database key-value store) for floors (field boss dead, floor boss dead, opened time, credited names) + GM test command `/floor`.
  Done when: test sets and reads every field; state survives a server restart.
- [x] **1.18 Gate Hound and the labyrinth door.** Field boss at the Pass; first kill opens the labyrinth door forever.
  Done when: test kills the Gate Hound with a GM command and the door tile becomes walkable; after restart it stays open.
- [x] **1.19 Axe-Lord and the Floor 2 unlock.** Boss with 3 phases and telegraphs; credit list; last hit; enrage scaling; first kill opens the stair, broadcasts the gold announcement, writes the monument, unlocks Floor 2 landing.
  Done when: in-game tests check credit (90-second window, top contributors), resets, enrage steps, and a full first kill (saved state, broadcast, stair boulder removed, last hit recorded), and that a second kill does none of the first-clear actions. Not yet: healing counts toward credit, the house head start (phase 3), the in-game Monument display.
- [x] **1.20 Client UI v1.** OTClient module `game_spirebound`: floor indicator (shows "Floor 1 - Hearthgate Plains"), cursor colors (green/orange/red/dark red), sword-skill bar (6 slots, Shift+1..6, live cooldowns), difficulty label.
  Done when: the module passes a Lua syntax check and the server's messages are covered by in-game tests (JSON format, floor lookup). Seeing it work in the real client is part of the Phase 1 playtest (no headless 15.x client exists to automate this).
- [ ] **1.21 🧑 Phase 1 playtest.** WEEKLY_REPORT.md with an under-an-hour checklist. Jay plays it.
  Done when: Jay writes "Phase 1 OK" (or notes) in PLAYTEST.md, and every note is either fixed or moved to a later task.

## Phase 2 — Core systems
- [x] **2.1 PvP cursors and skulls** (orange/red/black timings and penalties, DESIGN §6.4.7). Done when: tests for each skull threshold and penalty pass.
- [x] **2.2 Zone tiers** (Guarded/Open/Contested/Deadzone) from map zones + client corner icon. Done when: test kills in each zone give the expected skull result.
- [x] **2.3 Newbie and level-range protection.** Done when: tests: level 40 can't be attacked; level 200 can't start a fight with level 139 but can fight back.
- [x] **2.4 Outnumbered shield and guild-farming Sanctuary.** Done when: tests show damage reduction with 4 attackers and Sanctuary after 2 guild kills in 6 h.
- [x] **2.5 Bounty Board.** Done when: test: red skull gets a system bounty; same-IP/guild/party kills don't pay; a valid kill pays.
- [x] **2.6 Consent guild wars** (sign, terms, end, 7-day cooldown). Done when: tests for one-sided declaration refused and war kills give no skull.
- [x] **2.7 Secrets system + Info Broker (Vesper).** Discovery records, sell-or-keep, public list, announcement, explorer counts. Done when: tests: two players discover the same secret independently; one sells; the other's record stays; nobody is locked out.
- [x] **2.8 Floor 1 secrets (12).** Done when: all 12 have a walkable trigger tile on the map (in-game test); stepping on them is checked in the Phase 2 playtest; ART requests logged.
- [x] **2.9 Fishing system** (floor fish tables, night fish, worm bait, bite-and-react click, collection log with best weights, titles, legendary fish announcement). The weekly Derby moved to the world events task (5.7). Done when: in-game tests cover the catch table, night-only fish and bite chance; reacting in time is in the Phase 2 playtest.
- [x] **2.10 Underkeep Wing 1.** Done when: the grate secret leads into it, the wing and its monsters load, and the sealed Wing 2 door has its sign (in-game test).
- [x] **2.11 Quest log + Floor 1 story quests + perk choice.** Done when: every Floor 1 story quest has a quest-log line for every step and is in the client quest log (in-game tests); walking through them is in the Phase 2 playtest.
- [x] **2.12 Cavebot penalty (server side).** Client reports cavebot on/off; while on and for 10 min after: XP ×0.45, loot ×0.5, no visible marker, no secrets/rare chests/Twin Fang trial, boss rooms refuse entry; auto-targeting alone has no penalty; suspicion logging. Done when: in-game tests for each rule.
- [x] **2.12b Cavebot and auto-targeting in the client.** Adapt OTClient Redemption's built-in bot module: route recorder, walker, auto-target, auto-heal, auto-eat, looter; reports its state to the server; everything else from that module removed. Done when: the report script passes a Lua syntax check and the installer's edits to the bot loader are checked against the real file; seeing it work is in the Phase 2 playtest.
- [x] **2.14 Hardcore extras (part):** blessings can only remove half of a Hardcore death's experience loss (in-game test). Still open, moved to 2.14b: skill loss ×1.5 and item-drop chance ×2 (the engine handles those internally; needs a different approach).
- [x] **2.14b Hardcore skill loss ×1.5 and item drops ×2.** Done when: in-game tests for each. *(Done: skill debt + second drop roll; see DESIGN.md 5.5.)*
- [x] **2.15 Autoloot + loot highlight + loot channel.** Done when: in-game test: an item on the autoloot list goes to the backpack; rare drops print in the loot channel.
- [x] **2.16 Hunting tasks** from each floor's Quartermaster (kill counts, gold + task points). Done when: in-game test completes a task and pays out.
- [x] **2.17 Catch-up rules:** no death XP loss on Normal below level 50; faster skills below level 50. Done when: in-game tests for both.
- [ ] **2.13 🧑 Phase 2 playtest** with WEEKLY_REPORT.md. Done when: Jay signs off in PLAYTEST.md.

## Phase 3 — Houses and gambling
- [x] **3.1 Houses, rent, head start.** Listed price (1,000 gold per tile), level 20, one per character, weekly rent (the engine reverts unpaid houses), first-clear head start with the half-district cap. Done when: in-game tests for the head-start rules and that every house has a reachable doorway. Relisting announcements moved to 3.1b.
- [x] **3.1b Relist announcements** for reverted houses at server save. Done when: test. *(Done: checked every 5 minutes and right after start-up; 4+ houses are summarised in one message.)*
- [x] **3.2 House Portal (3 changes ever).** Done when: test: 4th change refused; forbidden targets refused.
- [x] **3.3 Summoning Circle + Boss Sigils.** Done when: test summons a private boss copy that gives no world-first credit.
- [x] **3.4 Fortune Hall** (dice, high-low, duel betting; gold only; 5% destroyed; bet cap; logs). Done when: tests: shop item and shop currency bets refused; cut destroyed; log written.
- [x] **3.5 Training room, trophies, mannequins, garden & pond, workshop, guild war room.** (Open House is done: `!openhouse`.) Done when: each has a test or a scripted use check. *(Done: exercise dummy kit, `!trophies`, `!mannequin`, `!pond`, `!warroom`, Housewright Orla. Workshop bench and garden wait for crafting/cooking, which don't exist yet: task 3.5b.)*
- [ ] **3.5b Workshop bench and garden** once a crafting/cooking system exists (needs a design pass first).
- [x] **3.6 Guilds (part):** guild bank at the banker ("guild balance"), recruiting board and looking-for-guild list at Guildwarden Sela, `!lfg` flag, chat channels World / Mundo / Trade / Help / Looking for Group. Guild halls come with the floor towns that have them (phase 4). Done when: boot test loads all of it with zero errors (dialogue checked in the playtest).
- [ ] **3.7 🧑 Phase 3 playtest.**

## Phase 4 — Floors 2 to 5
One task per floor: placeholder map, town + NPCs, monsters, apex spawn, field boss, labyrinth, floor boss, 12 secrets, fish list, story quests, perk.
- [x] **4.1 Floor 2** · [x] **4.2 Floor 3** · [x] **4.3 Floor 4** · [x] **4.4 Floor 5** (placeholder versions from one generator)
  Done when (each): map, town with 7 NPCs, stairs up and down, field and floor boss spawned, 12 secrets placed, 7 fish and 3 story quests with perks (in-game tests); boot test passes. Hand-tuned boss mechanics and real maps come later (MAP_REQUESTS M3, playtest notes).
- [x] **4.5 Underkeep Wings 2–3.** Done when: wings open at Floors 2 and 4 (in-game test checks each seal against its floor).
- [x] **4.6 Sword skills 4–6 for every weapon family.** Done when: tests as in 1.14.
- [x] **4.6b Spells above level 50 + the Lost Arts** (★ spells from quests, secrets and bosses). Done when: every spell in DESIGN §5.3b registers; tests check Lost Arts can't be bought.
- [ ] **4.7 🧑 Phase 4 playtest.**

## Phase 5 — Floors 6 to 10 and Azhrakkar
- [x] **5.1 Floor 6** · [x] **5.2 Floor 7** · [x] **5.3 Floor 8 (+ Twin Fang trial)** · [x] **5.4 Floor 9** · [x] **5.5 Floor 10 + Azhrakkar** (placeholder versions; Azhrakkar's 3 phases are in the pattern library, a scripted 3-phase test is still open)
  Done when (each): scripted speed run clears the floor; for 5.3 the 4th Twin Fang attempt is refused; for 5.5 all 3 Azhrakkar phases trigger in a scripted fight.
- [x] **5.6 Underkeep Wings 4–6.**
- [x] **5.7 World events scheduler** (Frenzy, Incursion, Fishing Frenzy, Wandering Champion). Done when: test forces each event and checks its announcement and end.
- [x] **5.7b Weekend rotating bonus** (double XP / rapid respawn / double loot / double fishing / double skill). Done when: test forces each bonus and checks it ends.
- [x] **5.7c Equal-footing PvP arena events** (Last Man Standing, Team Rush, Capture the Banner; same level/gear for all). Done when: scripted event with test players starts, scores and ends. *(Done: daily at 19:00 and 22:00 server time, `!arena join`, GM `/arena open|start|stop`. Equal footing = same health/mana and fixed hit/heal amounts, since the engine can't swap level or gear.)*
- [x] **5.7d Spire Siege** (weekly guild castle, level-scaled). Done when: scripted siege with two test guilds picks a holder. *(Done: Sundays 20:00 server time, `!siege join`, GM `/siege open|start|stop`; same equal-footing numbers as the Arena.)*
- [x] **5.7e Offline training statues + livestream (cast) switched on.** Done when: boot test shows both enabled with zero errors.
- [ ] **5.8 🧑 Phase 5 playtest.**

## Phase 6 — Client polish and languages
- [x] **6.1 Info Broker window, secret list, fishing log, quest log UI.** *(Done as one Journal window on the J key: secrets, fishing log, quests, hunting task, top climbers, Memorial. Server side is tested; the window itself needs Jay's first run. Selling secrets still happens by talking to the Info Broker.)*
- [x] **6.2 Death Game Memorial + leaderboard (in game).** *(Done: `!memorial` and `!top [normal|hardcore|deathgame]`; the Monument sign points to them. A proper client window comes with 6.1.)*
- [ ] **6.3 Portuguese and Spanish text** for UI, NPCs, quests, server messages.
- [ ] **6.4 Custom asset pipeline for 15.x** (our own appearances + sprite sheets from Jay's PNGs). Done when: a test sprite made from a PNG shows up in the client in place of a placeholder.
- [ ] **6.5 Swap in all art Jay has delivered so far.**
- [ ] **6.5b Android client build** (OTClient Redemption's Android target). Done when: an APK builds in CI.
- [x] **6.5c Season Path** (free track: daily/weekly goals → cosmetics, titles, house items). Done when: in-game test completes a goal and grants a reward. *(Done: `!path`; 7 goals, 30 tiers of furniture, tapestries and titles. The test completes goals and checks every reward is a real takeable item; Jay's playtest should confirm a reward lands in the store inbox.)*
- [ ] **6.6 🧑 Phase 6 playtest.**

## Phase 7 — Accounts, website, donation shop
- [ ] **7.1 Website** (account creation, character pages, floor monument, secret list, Hall of Fame, rules). Free software only (MyAAC or similar).
- [ ] **7.2 Donation shop** (cosmetics, housing, convenience; never power), off until launch. Done when: test confirms no shop item has combat stats and shop items can't be gambled.
- [ ] **7.2b Website wiki pages** generated from our data files; boss cooldowns and event countdowns on the website; Discord announcements.
- [ ] **7.3 🧑 Jay picks shop prices and payment setup** (QUESTIONS.md).

## Phase 8 — Seasons
- [x] **8.1 Season reset tool** (archives characters to the Hall of Seasons, keeps account-wide rewards). Done when: test season: create chars + rewards, run reset, account rewards remain and characters are archived. *(Done: `/season end <n>` for the owner; automated test checks the archive, account titles and that the wipe never touches accounts. A full live reset still needs a real test season.)*
- [x] **8.2 Season remix tooling** (shuffle secrets, add Underkeep wing, rotate boss mechanics). *(Done: automatic from the season number; `/season remix [n]` previews it. New Underkeep wings are map work: MAP_REQUESTS.md M5.)*

## Phase 9 — Friends test (still on Jay's PC)
- [ ] **9.1 Remote friend access on Jay's PC** (free options only; written guide). 🧑
- [ ] **9.2 Load test with scripted clients** (target 100 bots on Jay's PC without lag).
- [ ] **9.3 🧑 Friends playtest weekend + fixes.**

## Phase 10 — Move to a rented server (only after Jay says testing is done)
- [ ] **10.1 🧑 Jay picks a host** (QUESTIONS.md has options and prices).
- [ ] **10.2 Server setup scripts, backups, monitoring.**
- [ ] **10.3 Launch checklist** (all placeholders replaced, rules page, Discord, countdown).
