# Spirebound Roadmap

Small numbered tasks, grouped into phases. Work top to bottom. Each task has a **Done when** line that can be checked. Check a task off (`[x]`) only when its Done-when has been checked, and write how in `PROGRESS.md`.

"Boot test" = `tools/test_boot.sh` (server starts with our datapack, prints "online", zero errors in the log). It must pass after every task from 1.3 onward.

Legend: 🧑 = needs Jay (playtest or decision). Everything else Claude does alone.

---

## Phase R — Make it real (from REVIEW.md, 2026-11-11). Do this before anything else.
The review found that phases 2–8 were built wide and thin before anyone played Phase 1. **No new features until this phase is done.** Section numbers in brackets point into `REVIEW.md`. Order = priority.

Already fixed the same day:
- [x] **R1 Floor-skipping holes** [3.1, 3.2]: next-floor stair walled in behind the boulder, floor guard sends anyone on a sealed floor back to Hearthgate, Skystep needs a real gap and never lands in a boss room. *(Walking into it in the real client is still part of R0.)*
- [x] **R2 Skull timers** [3.3]: red 7 days, black 14 days (they lasted ~57 years).
- [x] **R3 Login service, first pass** [7.1]: no database tricks in the login box, wrong-password limit. Rest is in R4.

Open:
- [ ] **R0 🧑 Jay plays the first hour** (same as 1.21): new character → Registrar → level 15 → a secret → a death. Then a 3-person Floor 1 boss run. Every note becomes a fix or a task.
- [x] **R4 Lock the front door** [7.1, 7.3, §4]: the start script stops re-creating the GM test account (separate dev-only step); login service uses random session tokens, not the password, and only listens locally until the friend tunnel exists; a simple account sign-up page (moved up from 7.1). Done when: tests show the GM account is not touched by a normal start and a session key is never the password.
- [x] **R5 Death Game made trustworthy** [3.4, 2.7]: a character is deleted only by a death that was really PvE (the killing blow or most recent damage from monsters, whoever the players are); "friend tagging" needs real damage (~15% of health) to save you; monsters dragged in by another player in the last 30 s don't count as PvE; retirement frees house, guild leadership, market offers and the character slot, and saves at once; GM restore command + written "unfair death" policy; stepping down costs the bonus (Q14); Deathbound title only for characters that reached level 50 alive. Done when: an in-game test for each rule that goes through the real death event.
- [x] **R6 Hardcore death fix** [3.5]: the item-drop call has the wrong arguments (blessings ignored, error on skulled deaths). Done when: a test dies through the real death event.
- [x] **R7 Fair PvP credit** [3.6]: unjust kills, Sanctuary and bounties count everyone who did meaningful damage (not only the last hit); outnumbered shield counts only outsiders who did real damage; healing a skulled player drops your protection for a few minutes; bounty "recent party partner" rule actually wired; murderers respawn outside town (Outlaw Camp).
- [x] **R8 Save at the big moments** [7.2]: force a save after floor clears, Death Game retirement, shop purchases and secret sales; shorter save interval.
- [x] **R9 Finish the boss system** [3.9, 1.4]: private repeat-kill portal for parties of 1–5 with a per-character 20 h lockout; healing and damage taken count for credit; minimum share for credit; enrage timer recomputed when more players arrive; 20-player room cap; rewards kept for players offline at the kill; calendar gate per floor (Q13); warning time for lethal hits (Q19).
- [x] **R10 Real balance tables and economy check** [2.8, 6.1, 3.7, 3.12]: rebuild `tools/gen_tables.py` for the real 10-floor game (XP/h, gold/h, supply cost, time per level band, time to afford a house); monster/NPC/floor generators read from it; the economy check runs on GitHub; archive the old October tables. Then fix: high-floor gold flood, Fortune Hall cut really destroyed + host table limit, hunting tasks per floor with sane payouts and something to spend task points on, missing sinks (travel fees, repairs). Done when: the check fails loudly on a bad price and passes on the real game.
- [ ] **R10b Missing gold sinks** (cut from R10, 2026-11-13): item repairs need a durability system that doesn't exist yet (design first), and travel between floor towns is free. Done when: a repair or travel fee exists in game with an in-game test, and `tools/balance.py` counts it.
- [ ] **R10c House prices per floor** (found by R10): the engine charges 1,000 gold a tile everywhere, so from Floor 3 up a house costs under 4 hours of hunting. Done when: `!buyhouse` (a core override) charges by floor and `tools/balance.py` checks every floor's houses.
- [x] **R11 Arrival Yard tutorial** [1.2] (promised in 1.8, never on the map): walled path, each gate opens after one small step (kill, loot, sword skill, potion), ends at the Registrar; town gates closed until a vocation is chosen; hint pop-ups for the first levels; a "How do I…" tab in the Journal.
- [x] **R12 Things to earn on Floors 1–2** [2.1–2.4, 8.2]: a Spirebound gear ladder per vocation (boss drops the floor's best piece) generated from a table, with original item names and the name checker extended to items; every perk works or is removed (test per perk); one hand-written quest line per floor with a non-gold reward; a plan for unlocks past level 150.
- [x] **R13 Scope for the friends test** [1.3, 9.2 of review]: Floors 1–2 hand-tuned (different layouts, monsters with one trick each, easy→hard camp ladder); Floors 3–10 sealed; arena, siege, shop and Season Path switched off for the test (Q22).
- [ ] **R13b Floor 2 hand-tuned** (cut from R13, 2026-11-13): Floor 2's map is still the shared placeholder generator; give it its own layout (walled grounds with loops, as Floor 1) and an easy-to-hard camp ladder. Done when: rendered, walk test passes, walked in the client.
- [x] **R14 Moderation basics** [§4]: `!report`, mute, GM action log, chat filter (en/pt/es), rules shown in game, written punishment ladder.
- [x] **R15 Bots enforced on the server** [3.8] (after Q16): pattern logging that 2.12 promised; strip the vBot script editor/attack helper from the shipped client or accept them; task gold and follower XP rules.
- [x] **R16 House fixes** [3.7]: Open House keeps the real guest list and survives restarts, with a cooldown; Summoning Circle moved to a small private arena (it can't work inside a safe house); House Portal can't target labyrinths or Contested zones.
- [x] **R17 Secret fixes** [3.10]: trigger on stepping on the tile, gold reward once per account, "night" uses the game's day/night, real hints for Floors 6–10.
- [ ] **R18 Tests that reach the real game** [7.5]: boot test runs on GitHub; end-to-end tests per headline rule (reach Floor 2 without a kill, die as each difficulty, wait out a skull, Fortune Hall cut).
- [ ] **R19 Clickable routes for chat commands** [1.5]: every `!command` players need also has an NPC, sign or client button.
- [ ] **R20 Small fixes** [3.12]: memory leaks at logout, Derby pays offline winners, rapid-respawn weekend bonus, faster respawn when a floor is busy.
- [ ] **R21 Twin Fang rebalance** [2.5] (after Q18): one-handed swords only, combos must hit a real monster, solo trial room, smaller off-hand bonus.
- [ ] **R22 Prove the art pipeline** = task 6.4, moved up [8.1]: one custom sprite in the client, then an estimate of the full art job.

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
  Done when: map compiles and loads with zero warnings; preview PNGs are in `docs/previews/`; MAP_REQUESTS.md lists the real Floor 1 map. *(Review: the Arrival Yard was never put on the map. Now task R11.)*
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
- [x] **2.12 Cavebot penalty (server side).** Client reports cavebot on/off; while on and for 10 min after: XP ×0.45, loot ×0.5, no visible marker, no secrets/rare chests/Twin Fang trial, boss rooms refuse entry; auto-targeting alone has no penalty; suspicion logging. Done when: in-game tests for each rule. *(Review: suspicion logging was never built, and the penalty trusts the client. Now task R15.)*
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
- [x] **3.3 Summoning Circle + Boss Sigils.** Done when: test summons a private boss copy that gives no world-first credit. *(Review: the boss probably can't be fought inside a safe house, and it has no special attacks. Now task R16.)*
- [x] **3.4 Fortune Hall** (dice, high-low, duel betting; gold only; 5% destroyed; bet cap; logs). Done when: tests: shop item and shop currency bets refused; cut destroyed; log written. *(Review: the 5% stays with the host instead of being destroyed. Now task R10.)*
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
- [ ] **6.3 Portuguese and Spanish text** for UI, NPCs, quests, server messages. *(Partly done: `!language en|pt|es`, 43 sentences + 25 patterns of server messages, the Journal and its client labels. Still English: NPC talk, quest text, item and monster names, secret hints. Next: 6.3b.)*
- [ ] **6.3b Translate NPC dialogue, quest text and secret hints** into pt and es (extend `tools/gen_i18n.py`). *(Part done 2026-11-11: NPC speech is hooked into the language system and the Registrar is fully translated, verified in the real client. Still English: the other 75 NPCs, quest text, the 120 secret hints, item/monster names. Add rows to `tools/i18n_npc.py`.)*
- [ ] **6.4 Custom asset pipeline for 15.x** (our own appearances + sprite sheets from Jay's PNGs). Done when: a test sprite made from a PNG shows up in the client in place of a placeholder.
- [ ] **6.5 Swap in all art Jay has delivered so far.**
- [ ] **6.5b Android client build** *(on hold until after the friends test, per REVIEW 9.2; 6.3b translations likewise)* (OTClient Redemption's Android target). Done when: an APK builds in CI.
- [x] **6.5c Season Path** (free track: daily/weekly goals → cosmetics, titles, house items). Done when: in-game test completes a goal and grants a reward. *(Done: `!path`; 7 goals, 30 tiers of furniture, tapestries and titles. The test completes goals and checks every reward is a real takeable item; Jay's playtest should confirm a reward lands in the store inbox.)*
- [ ] **6.6 🧑 Phase 6 playtest.**

## Phase 7 — Accounts, website, donation shop
- [ ] **7.1 Website** (account creation, character pages, floor monument, secret list, Hall of Fame, rules). Free software only (MyAAC or similar). *(Part done: static pages — home, how to play, the tower, vocations, difficulty, PvP rules, events, rules — built by `tools/gen_site.py` into `website/public/`. Still to do: account creation, character pages, Hall of Fame (need MyAAC + the database).)*
- [x] **7.2 Donation shop** (cosmetics, housing, convenience; never power), off until launch. Done when: test confirms no shop item has combat stats and shop items can't be gambled. *(Done, closed: `!shop` is off until launch (SpireShop.ENABLED). 11 placeholder items (furniture, statues, tapestries, 2 outfits, 1 mount) with placeholder prices; a test fails the build if any item has attack, defense or armor or is gold. Payment hookup is 7.3.)*
- [ ] **7.2b Website wiki pages** generated from our data files; boss cooldowns and event countdowns on the website; Discord announcements. *(Part done: floors, fish and secret counts generated from our data. Still to do: boss cooldowns, event countdowns, Discord announcements.)*
- [ ] **7.3 🧑 Jay picks shop prices and payment setup** (QUESTIONS.md).
- [ ] **7.4 Shop worth buying from** [REVIEW 6.2, 6.4]: 8–12 shop-only outfits, a few mounts, name effects, house themes (nothing the Season Path or Housewright already gives); depot space sold for gold instead; a permanent purchase record per sale.
- [ ] **7.5 🧑 Before taking any money** [REVIEW 6.5]: privacy policy, terms, refund policy, age statement, account deletion, all CipSoft art gone, the trade/gambling question settled (Q15, Q17). Ask a professional about tax and law.

## Phase 8 — Seasons
- [x] **8.1 Season reset tool** (archives characters to the Hall of Seasons, keeps account-wide rewards). Done when: test season: create chars + rewards, run reset, account rewards remain and characters are archived. *(Done: `/season end <n>` for the owner; automated test checks the archive, account titles and that the wipe never touches accounts. A full live reset still needs a real test season.)*
- [ ] **8.3 Season reset as an offline tool** [REVIEW 3.11]: stop server → automatic backup → wipe → start (today's `/season end` deletes rows while the server still holds them in memory); fishing log carries over; rehearsed on a copy of a real database. Needed before season 1 ends, not before.
- [ ] **8.4 Secrets move each season, plus a few weekly rotating secrets** [REVIEW 3.10].
- [x] **8.2 Season remix tooling** (shuffle secrets, add Underkeep wing, rotate boss mechanics). *(Done: automatic from the season number; `/season remix [n]` previews it. New Underkeep wings are map work: MAP_REQUESTS.md M5.)*

## Phase 9 — Friends test (still on Jay's PC)
*Starts only after Phase R. Friends test is invite-only (REVIEW 8.3) and wiped afterwards.*
- [ ] **9.1 Remote friend access on Jay's PC** (free options only; written guide; a tunnel so friends never see Jay's home address [REVIEW 7.7]). 🧑
- [ ] **9.2 Load test with scripted clients** (target 100 bots on Jay's PC without lag).
- [ ] **9.3 🧑 Friends playtest weekend + fixes.**

## Phase 10 — Move to a rented server (only after Jay says testing is done)
- [ ] **10.1 🧑 Jay picks a host** (QUESTIONS.md has options and prices).
- [ ] **10.2 Server setup scripts, backups, monitoring.** *(Part done for Jay's PC and tested on 2026-11-11: Backup-Spirebound.bat, Restore-Spirebound.bat, automatic backup at each start (the database lives in WSL). Rented-server scripts and monitoring wait for 10.1.)*
- [ ] **10.3 Launch checklist** (all placeholders replaced, rules page, Discord, countdown; open beta that gets wiped; staffed first week; written update/rollback routine; backups copied off the server every few hours [REVIEW 1.6, 7.7]).
- [ ] **10.4 Launch-size Floor 1** [REVIEW 5.2]: ~1,500 monsters across 14+ camps of rising difficulty, caves, busier-floor respawn. Real map work (MAP_REQUESTS M1).
- [ ] **10.5 Stronger passwords and two-step login** [REVIEW 7.4], through the website package.

## Floor 1 build (2026-11-11, from Jay's instructions)
- [x] **F1.1 Floor 1 map redesign.** Compact walled Hearthgate with 14 inner houses, 20 wallside cabins, 10 fisher huts, Millcross with 8 cottages, twelve hunting grounds laid out as a level ladder, roads between them, the Arrival Yard. Done when: map builds and loads, every ground's monsters exist, every camp is on the map (in-game tests). *(Placeholder look; real map is MAP_REQUESTS M1.)*
- [x] **F1.2 Floor 1 NPCs and quests.** Promotion at level 20 (Ascendant Veyra), Hunters' Hall (Brannoch, Taskmaster, Bounty Warden), Innkeeper Bess, Fisher Corwin, Guide Pell; six story quests and four side quests with a quest-log entry each. Done when: all NPCs stand in town and every quest has log lines and a real target (in-game tests).
- [x] **F1.3 BESTIARY.md and the hunting ladder logic.** `maps/floor1_plan.py` -> map + BESTIARY.md + `!hunt` and NPC advice. Done when: tests check each level 1-40 has a ground and the advice names it.
- [x] **F1.4 Tutorial (first version).** New characters start in the Arrival Yard with a guide, signs and a rat pen; a letter, `!guide`, `!hunt` and level-up advice. Added since: a tutorial quest from Guide Pell (First Blood: three rats) and hints at levels 2, 5, 8, 10 and 20. Still open: stop gates that need a step done, and a walked-through playtest in the real client. (R11)

## Jay's direction list (2026-11-11)
- [x] **J1 Expand Hearthgate, no wasted space.** 112x96, ten shops, Market Square, Trade Hall, inn, training yard, carriage station, 22 houses. Done when: map builds with no overlapping buildings and every named place loads (in-game tests).
- [x] **J2 Second top-server research pass.** `docs/RESEARCH_TOP_SERVERS_2026-11b.md`.
- [x] **J3 Spire Manor, the shop-only showcase house.** Four levels, stairs, trophy gallery, rooftop garden; only the shop hands it out. Done when: in-game test walks its stairs and checks the shop-only rule.
- [x] **J4 Newcomer playthrough and fixes.** Played a fresh character in the real client; fixed:
  - silent quest offers (the client crashed on keywords in brackets);
  - the Arrival Yard showing Open PvP;
  - the first fight barehanded;
  - tutorial rats that could kill a level 1, and rats escaping the pen;
  - confusing login lines;
  - Pell's wrong attack advice and missing plural keywords;
  - no way to heal in the yard.
  Done when: in-game tests cover the quest talk, the yard zone and the pen gap.
- [~] **J5 Economy.** `tools/gen_economy.py` writes ECONOMY.md (burn rates per hunting ground and vocation) and fails the build if a vocation loses money where it should hunt. Floor 1 monsters drop trade materials; crafters (Fletcher, Alchemist, Runewright, Tailor) turn them into things no shop sells. Done so far: model, materials, recipes, tests. Still open: the same for Floors 2-10 (J5b) and a playtest of crafting in the client (J5c).
- [ ] **J5b Economy for Floors 2-10:** materials, recipes and burn-rate check per floor.
- [ ] **J5c Crafting playtest in the client:** buy materials on the market, craft at each crafter.
- [ ] **J6 Client defaults for newcomers:** Battle List open by default, and make sure the first chat line after switching tabs is never lost (seen twice in the playthrough). Alt+click attack does nothing in our client: either fix it or stop mentioning it.
- [x] **J7 Boosted creature of the day.** One Floor 1 hunting-ground monster a day: +50% experience and an extra loot roll, named at login (Canary's own version can't pick our monsters). Done when: in-game test checks every pick is a real monster with no repeats for 13 days.
- [x] **J8 Temple scroll.** Runewright Mael sells it (300 gold, used up): back to your home temple when not in a fight; never from a boss room, Deadzone, the Arena or the Siege. Done when: in-game test finds the item and the seller. *(Still to check by hand in the client: J5c-style playtest.)*
- [ ] **J9 Ten-minute mini events** between the big ones (snowball fight, quiz, last man standing at fixed gear).
- [ ] **J10 Forge for Floor 3 and up** (waiting on Q27).
- [x] **J11 The Hearth, Hearthgate's home hall** (Jay, 2026-11-12). It brings temple, depot, bank and market together across three levels:
  - **Level 1:** the spawn and respawn point, 18 lockers, Trader Osric (junk buyer), Banker Tolliver, and Broker Nell.
  - **Level 2:** the trading gallery, with 16 more lockers and trade tables.
  - **Level 3:** the Hall of Climbers.
  Also added: an account vault shared by all characters on an account, and a branch bank on the north wall. Done when: in-game test checks that the respawn point is in the Hearth, all stairs work both ways, the NPCs are loaded and the vault arithmetic holds; Osric's trade window was checked in the client.
- [x] **J12 Hearthgate v3, built from the plan** (Jay, 2026-11-12). The Hearth at the centre, four quarters, 30 houses, Spire Manor moved to the East High Road, Spire Gardens, Hearthgate Green, Old Well Yard. Done when: map builds with no overlaps, in-game tests check the archways, a locker near the Hearthstone, 30 street houses, all stairs; walked in the client.

## Floor 1 wilds rebuild (plan ready 2026-11-12: `FLOOR1_WILDS_PLAN.md`, picture `docs/FLOOR1_WILDS_PLAN.png`)
Jay: "monster spawn areas are currently messy and need to have more of a dedicated area where a few players at a time will be able to bot or farm." Follow the plan exactly; one commit per task; details and "done when" are in its Part 9.
- [x] **W0 Find out how the engine respawns** (three questions in Part 7).
- [x] **W1 Put the new ground table into `maps/floor1_plan.py`** (nothing on the map changes yet).
- [x] **W2 Builder pieces:** wall ring, loop, fixed groups, named points, the walk test.
- [x] **W3 Pilot: Boar Meadow** with Old Tusk's wallow.
- [x] **W4 The four starter grounds.**
- [x] **W5 Burrow Hills, Wolf Copse, Reedmarsh, Thornsnap Hollow.**
- [x] **W6 Shard Fields, the Bandit Road, the Old Quarry, the Old Watchtower's groups.**
- [x] **W7 Roads, trails, signposts, zones, secrets, forest pass.**
- [x] **W8 The six caves.**
- [x] **W9 Experience stages and the ladder** (Q30: Jay said yes, Floor 1 should last 11-15 hours).
- [x] **W10 The crowd system and the `!hunt` line** (Q31: yes; cavebot refused in caves, Q32: yes).
- [x] **W11 Regenerate documents and pictures; playtest list for Jay.**
- [ ] **W12 Walk every rebuilt ground in the real client** (cut from W3-W8 on 2026-11-13: the client could not be driven this session). Done when: each ground's gate, hub signs, four loops and cave walked by Jay or by Claude in the client, and one party-sized fight in a cave, notes fixed. (Done so far: Boar Meadow, Toad Pond's hub, the Molework down and up.)
