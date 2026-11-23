# Spirebound Roadmap

Small numbered tasks, grouped into phases. Work top to bottom. Each task has a **Done when** line that can be checked. Check a task off (`[x]`) only when its Done-when has been checked, and write how in `PROGRESS.md`.

"Boot test" = `tools/test_boot.sh` (server starts with our datapack, prints "online", zero errors in the log). It must pass after every task from 1.3 onward.

Legend: 🧑 = needs Jay (playtest or decision). Everything else Claude does alone.

Finished tasks live in `ROADMAP_DONE.md` (move each task there when it is ticked).

---

## Jay's playtest, 2026-11-23 ("floor 1 is boring"). Do this first.
- [ ] **P1 Gear and weapon progression** (design `docs/superpowers/specs/2026-11-23-gear-progression-design.md`, waiting for Jay's OK; the build plan comes after). Done when: a new character can follow the "Next upgrade" window from level 1 to the Floor 1 boss, tested in the real game.
- [ ] **P1b Style path abilities (8, stage 2)**: one signature ability per path (Bulwark, Reaver, Marksman, Trapper, Emberwright, Stormbinder, Lifebinder, Wildcaller), learned when the path's Mastery reaches 10 (`style = 2` rows in `lib/spirebound/spells.lua`). Reached around Floors 4-5, so after the alpha. Done when: each casts in the client with a level 120 tester.
- [ ] **P1c Style final abilities (16, stage 3)**: one per final style, learned at final Mastery 10 (`style = 3`). Reached around Floor 8. Done when: each casts in the client with a level 280 tester.
- [ ] **P2 Quests you can find**: every Floor 1 quest giver marked (map marks, a sign or board in Hearthgate, the window from P1). Done when: autopilot or Claude reaches every Floor 1 quest giver from the temple using only in-game directions.
- [ ] **P3 Hearthgate feels alive**: more NPCs with things to say or do, townsfolk that walk, lights, fires, fountains, ambient effects. Done when: rendered, checked in the client, and listed in the playtest checklist for Jay.
- [ ] **P4 Toad Pond too small, levelling slow and dull**: grow Toad Pond (and check the other rebuilt grounds the same way) and re-check XP per hour levels 1-15 in `tools/gen_economy.py`. Done when: the walk test and economy check pass and autopilot hunts it.
- [ ] **P5 Remove stock materials we don't use** ("venomous slime" and similar from leftover Tibia files); every material's description says where it drops. Done when: a script finds no material without a source and the boot test passes.

## Phase R — Make it real (from REVIEW.md, 2026-11-11). Do this before anything else.
The review found that phases 2–8 were built wide and thin before anyone played Phase 1. **No new features until this phase is done.** Section numbers in brackets point into `REVIEW.md`. Order = priority.
- [ ] **R0 🧑 Jay plays the first hour** (same as 1.21): new character → Registrar → level 15 → a secret → a death. Then a 3-person Floor 1 boss run. Every note becomes a fix or a task.
- [ ] **R10b Missing gold sinks** (cut from R10, 2026-11-13): item repairs need a durability system that doesn't exist yet (design first), and travel between floor towns is free. Done when: a repair or travel fee exists in game with an in-game test, and `tools/balance.py` counts it.
- [ ] **R10c House prices per floor** (found by R10): the engine charges 1,000 gold a tile everywhere, so from Floor 3 up a house costs under 4 hours of hunting. Done when: `!buyhouse` (a core override) charges by floor and `tools/balance.py` checks every floor's houses.
- [ ] **R13b Floor 2 hand-tuned** (cut from R13, 2026-11-13): Floor 2's map is still the shared placeholder generator; give it its own layout (walled grounds with loops, as Floor 1) and an easy-to-hard camp ladder. Done when: rendered, walk test passes, walked in the client.
- [~] **R18 Tests that reach the real game** *(2026-11-13: end-to-end tests added and passing; the GitHub boot workflow is written but its first run is not checked yet)* [7.5]: boot test runs on GitHub; end-to-end tests per headline rule (reach Floor 2 without a kill, die as each difficulty, wait out a skull, Fortune Hall cut).
- [ ] **R22 Prove the art pipeline** = task 6.4, moved up [8.1]: one custom sprite in the client, then an estimate of the full art job.

## Phase 1 — Floor 1, start to finish, running on Jay's PC
Goal: create a character, pick vocation and difficulty, level on Floor 1, kill the field boss, clear the labyrinth, kill the Floor 1 boss, watch Floor 2 unlock for everyone.
- [ ] **1.5 Windows one-click setup.** *(built and checked in the cloud; waiting for Jay's first run)* `windows/Install-Spirebound.ps1` downloads pinned Canary (Windows build), OTClient Redemption 4.2 (Windows build), portable MariaDB and the 15.11 client files; creates the database; points the client at localhost. `Start-Spirebound.bat` / `Stop-Spirebound.bat`.
  Done when: script passes a dry-run check in the cloud (all download URLs answer, all paths exist), and 🧑 Jay double-clicks it once and reaches the login screen (logged in PLAYTEST.md).
- [ ] **1.21 🧑 Phase 1 playtest.** WEEKLY_REPORT.md with an under-an-hour checklist. Jay plays it.
  Done when: Jay writes "Phase 1 OK" (or notes) in PLAYTEST.md, and every note is either fixed or moved to a later task.

## Phase 2 — Core systems
- [ ] **2.13 🧑 Phase 2 playtest** with WEEKLY_REPORT.md. Done when: Jay signs off in PLAYTEST.md.

## Phase 3 — Houses and gambling
- [ ] **3.5b Workshop bench and garden** once a crafting/cooking system exists (needs a design pass first).
- [ ] **3.7 🧑 Phase 3 playtest.**

## Phase 4 — Floors 2 to 5
One task per floor: placeholder map, town + NPCs, monsters, apex spawn, field boss, labyrinth, floor boss, 12 secrets, fish list, story quests, perk.
- [ ] **4.7 🧑 Phase 4 playtest.**

## Phase 5 — Floors 6 to 10 and Azhrakkar
- [ ] **5.8 🧑 Phase 5 playtest.**

## Phase 6 — Client polish and languages
- [ ] **6.3 Portuguese and Spanish text** for UI, NPCs, quests, server messages. *(Partly done: `!language en|pt|es`, 43 sentences + 25 patterns of server messages, the Journal and its client labels. Still English: NPC talk, quest text, item and monster names, secret hints. Next: 6.3b.)*
- [ ] **6.3b Translate NPC dialogue, quest text and secret hints** into pt and es (extend `tools/gen_i18n.py`). *(Part done 2026-11-11: NPC speech is hooked into the language system and the Registrar is fully translated, verified in the real client. Still English: the other 75 NPCs, quest text, the 120 secret hints, item/monster names. Add rows to `tools/i18n_npc.py`.)*
- [ ] **6.4 Custom asset pipeline for 15.x** (our own appearances + sprite sheets from Jay's PNGs). Done when: a test sprite made from a PNG shows up in the client in place of a placeholder.
- [ ] **6.5 Swap in all art Jay has delivered so far.**
- [ ] **6.5b Android client build** *(on hold until after the friends test, per REVIEW 9.2; 6.3b translations likewise)* (OTClient Redemption's Android target). Done when: an APK builds in CI.
- [ ] **6.6 🧑 Phase 6 playtest.**

## Phase 7 — Accounts, website, donation shop
- [ ] **7.1 Website** (account creation, **character creation** (Jay, 2026-11-14: "players will create characters via the website. they will sign up there, login, and create their character from the website"; the sign-up page in `tools/login_server.py` is a stopgap that makes the first character with the account), character pages, floor monument, secret list, Hall of Fame, rules). Free software only (MyAAC or similar). *(Part done: static pages — home, how to play, the tower, vocations, difficulty, PvP rules, events, rules — built by `tools/gen_site.py` into `website/public/`. Still to do: account creation, character pages, Hall of Fame (need MyAAC + the database).)*
- [ ] **7.2b Website wiki pages** generated from our data files; boss cooldowns and event countdowns on the website; Discord announcements. *(Part done: floors, fish and secret counts generated from our data. Still to do: boss cooldowns, event countdowns, Discord announcements.)*
- [ ] **7.3 🧑 Jay picks shop prices and payment setup** (QUESTIONS.md).
- [ ] **7.4 Shop worth buying from** [REVIEW 6.2, 6.4]: 8–12 shop-only outfits, a few mounts, name effects, house themes (nothing the Season Path or Housewright already gives); depot space sold for gold instead; a permanent purchase record per sale.
- [ ] **7.5 🧑 Before taking any money** [REVIEW 6.5]: privacy policy, terms, refund policy, age statement, account deletion, all CipSoft art gone, the trade/gambling question settled (Q15, Q17). Ask a professional about tax and law.

## Phase 8 — Seasons
- [ ] **8.3 Season reset as an offline tool** [REVIEW 3.11]: stop server → automatic backup → wipe → start (today's `/season end` deletes rows while the server still holds them in memory); fishing log carries over; rehearsed on a copy of a real database. Needed before season 1 ends, not before.
- [ ] **8.4 Secrets move each season, plus a few weekly rotating secrets** [REVIEW 3.10].

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

## Jay's direction list (2026-11-11)
- [~] **J5 Economy.** `tools/gen_economy.py` writes ECONOMY.md (burn rates per hunting ground and vocation) and fails the build if a vocation loses money where it should hunt. Floor 1 monsters drop trade materials; crafters (Fletcher, Alchemist, Runewright, Tailor) turn them into things no shop sells. Done so far: model, materials, recipes, tests. Still open: the same for Floors 2-10 (J5b) and a playtest of crafting in the client (J5c).
- [ ] **J5b Economy for Floors 2-10:** materials, recipes and burn-rate check per floor.
- [ ] **J5c Crafting playtest in the client:** buy materials on the market, craft at each crafter.
- [ ] **J6 Client defaults for newcomers:** Battle List open by default, and make sure the first chat line after switching tabs is never lost (seen twice in the playthrough). Alt+click attack does nothing in our client: either fix it or stop mentioning it.
- [ ] **J15b Fire runes burn vines too**: the engine's own fire runes (fire bomb, great fireball) don't burn Vinewalls yet; only our fire spells do.
- [ ] **J15c Wild PvP verdict**: after a few weeks of the weekly event, ask the players; if they love it, give it a zone (Deadzone).
- [ ] **J14b Dawnpiercer light arrow**: a projectile of our own (the effect pipeline makes effects only; projectiles need 8 directions).
- [ ] **J13d Client action bar defaults**: a new character's action bar starts with three Tibia incantations (the client's stock defaults); start it empty or with the character's first spells instead.
- [ ] **J13c Spirebound names for the rune items** (fire, strike, healing, paralysis runes still use the engine's item names; Q36).
- [ ] **J9 Ten-minute mini events** between the big ones (snowball fight, quiz, last man standing at fixed gear).
- [ ] **J10 Forge for Floor 3 and up** (waiting on Q27).

## Floor 1 wilds rebuild (plan ready 2026-11-12: `FLOOR1_WILDS_PLAN.md`, picture `docs/FLOOR1_WILDS_PLAN.png`)
Jay: "monster spawn areas are currently messy and need to have more of a dedicated area where a few players at a time will be able to bot or farm." Follow the plan exactly; one commit per task; details and "done when" are in its Part 9.
- [ ] **W12 (replaced by H13 below)** Walk every rebuilt ground in the real client (cut from W3-W8 on 2026-11-13: the client could not be driven this session). Done when: each ground's gate, hub signs, four loops and cave walked by Jay or by Claude in the client, and one party-sized fight in a cave, notes fixed. (Done so far: Boar Meadow, Toad Pond's hub, the Molework down and up.)

## Floor 1 hunting grounds, third pass (plan ready 2026-11-14: `FLOOR1_HUNTING_PLAN.md`). Do this next.
Jay: "im feeling overhelmed when i walk into a zone with nonstop monsters flooding to me. i think the zones need to bigger... utilize multi height levels as well. layer the monsters throughout the spawn more like real tibia does." Follow the plan exactly; one commit per task; details and "done when" are in its Part 9. Never relax a limit in its Part 3 to make a ground pass.
- [~] **H0 Measure how monsters notice players** (range, walls, changing level, wandering) and check which weekend bonus was on during Jay's test. *(2026-11-14: weekend bonus checked (none / Double Experience); the engine's view range is 11 tiles each way; the in-client measurement is still open because client control was declined this session.)*
- [ ] **H2 New ground table and moved roads** in `maps/floor1_plan.py` (nothing on the map changes yet).
- [ ] **HB Pilot Ranger's bow**: the test ranger's bow and arrows sit in the backpack, so it fights with its fists; equip them (the test kit) so ranger runs mean something. Done when: an autopilot run with Pilot Ranger kills with arrows.
- [ ] **S1b Class-aware economy model**: `tools/gen_economy.py` models what each class earns at each ground (area spells on swarms, keeping distance from slow monsters, healing through long fights) and what a group of 3-4 earns per person; `balance.py --check` then checks the reward targets per ground type (training 100%, class 120% for its class, mixed 110%, group 150%, large group 175%).
- [ ] **S4 Group grounds (3 to 4 players) and the large-group ground (4 to 8, the Old Watchtower)**: mixed packs with a front-liner, a ranged one and a caster; party size 8 in the game too (`party_rules.lua` still says 6); a test with several Pilot characters in one party.
- [ ] **S5 Packs stay together and follow their leader in the game** (a pack that splits up is just three singles); test on the Meadow Wolf and Grey Alpha.
- [ ] **S6 The floor recipe for Floors 2 to 10**: each floor's grounds get types and habits by the recipe, plus the floor's own twist, in `maps/floors.py`; the generator and checker obey them. (Takes over H12.)
- [ ] **H7 Boar Meadow, Wolf Copse, Reedmarsh, Thornsnap Hollow.** *(After S1 and S2; built with habits and ground types.)*
- [ ] **H8 Shard Fields, the Bandit Road, the Old Quarry, the Old Watchtower's groups.** *(After S1 and S2; the group parts are S4.)*
- [ ] **H9 Roads, trails, signposts, zones on every level, secrets, forest pass.**
- [ ] **H10 Crowd pockets, the weekend-bonus change, cavebot rule, respawn times and the economy re-check.**
- [ ] **H11 In-game tests on the real map** (monsters in range at each route's start, middle and end; monsters let go when you change level); regenerate documents and pictures.
- [ ] **H12 The calm rules become a rule for every floor** (`CLAUDE.md`, and the Floors 2 to 10 generator obeys them). R13b (Floor 2) builds on this.
- [ ] **H13 Walk every ground and level in the real client**; playtest list for Jay.
