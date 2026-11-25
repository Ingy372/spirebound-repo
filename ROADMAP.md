# Spirebound Roadmap

Small numbered tasks, grouped into phases. Work top to bottom. Each task has a **Done when** line that can be checked. Check a task off (`[x]`) only when its Done-when has been checked, and write how in `PROGRESS.md`.

"Boot test" = `tools/test_boot.sh` (server starts with our datapack, prints "online", zero errors in the log). It must pass after every task from 1.3 onward.

Legend: 🧑 = needs Jay (playtest or decision). Everything else Claude does alone.

Finished tasks live in `ROADMAP_DONE.md` (move each task there when it is ticked).

---

## Grok's playtest, 2026-11-24 (first-time Mystic, never killed anything as a Mystic). Do this first.
Reports: `docs/playtests/2026-11-24-grok-session1.md` and `...-session2.md`. Fixes: see PLAYTEST.md.
- [~] **G5 Client clean-up for newcomers**: the login field says "email" but wants the account name; hide the bot panel and the Store button; Ctrl+O for Options; the login title font is unreadable. *(2026-11-24: done: the login says "Account:" and the window "Spirebound"; the empty Store button is hidden. Left alone on purpose: the bot panel (DESIGN.md 11 builds bot helpers into our client; Q51) and Ctrl+O (it opens the chat channel list, as in Tibia). Still to do: the unreadable login title font (needs a look at the login screen).)* Done when: checked in the client with screenshots.
- [ ] **G7 Slower yard levels** (Q52, Grok session 2): Pen Rats and Pell's reward tuned so a new character leaves the yard at level 2-3. Done when: the autopilot's yard run ends at level 2-3.
- [ ] **G6 Rerun with Grok on a calm PC**: items 5-8 of the report (invisible attackers, dropped clicks and chat), and `!hunt` refused in town (could not reproduce from the code). Done when: a Grok report with no lag caveat, including a Ranger (Grok Fourth) and a Vanguard past the cheese gate (session 2 could not).

## Claude's playtest, 2026-11-25 (fresh Ranger, `docs/playtests/2026-11-25-claude-ranger.md`). Do this first.

- [ ] **C4 Check the hit-message spacing in the Server Log**: the client now drops the engine's extra space ("your  attack" -> "your attack", `client/modules/game_console/console.lua`); C1-C3 were checked in the client, this one only in code. Done when: a screenshot of the Server Log after a few hits shows single spaces.

## Grok's playtest, 2026-11-25 (session 3: all four paths on fresh characters). Do this first.
Report: `docs/playtests/2026-11-25-grok-session3.md` (handoff `...-session3-handoff.md`). Fixed the same day: see PLAYTEST.md. Left:
- [ ] **G8 A door on the Registrar**: the stone path ends at a red roof with no visible door (Grok found the way in only by clicking the minimap). Done when: a visible door faces the path, the path-end sign points to it, checked in a render and in the client.
- [ ] **G9 Walk every `!hunt` route**: the Sproutling Glade route ("south gate, then about 30 steps west") ended at a river for a Ranger and in forest for a Vanguard; Toad Pond east of town wasn't found in 18 minutes. Done when: an autopilot route walks each `!hunt` direction from the temple on foot (no jumps) and arrives, with a signpost at each turn.
- [ ] **G10 Retest the client-side items on the current client**: Pell's quest in the Quest Tracker (shown on 2 of 4 characters, no count per kill), the minimap "!" on quest givers (never seen), the clipped "ourfold Rene" skill name, the sticky Quickdraw crosshair, Enter firing Quickdraw, Shift+1-3 opening chat. Grok's client was older than the 09:46 package. Done when: each is checked with the autopilot on the current package and fixed where still broken.
- [ ] **G11 Vesper with her quest taken**: a second "hi" got her secrets-broker line and "Good bye", and her long bubble overlapped itself. Done when: with the quest active she reports the stones found so far, her lines are split short, checked in the client.
- [ ] **G12 Small clean-ups from session 3**: the death message says when the young-adventurer blessing kept your experience; temple townsfolk talk less often; the character list shows the current level and path after logout (engine or login-service cache); check that hits land on Bristle Boars (Grok saw its health bar stay full). Done when: each checked in the client.

## Jay's playtest, 2026-11-23 ("floor 1 is boring"). Do this first.
- [~] **P1 Gear and weapon progression** (design `docs/superpowers/specs/2026-11-23-gear-progression-design.md`, plan `docs/superpowers/plans/2026-11-23-gear-progression.md`). *(2026-11-24: in the client, Dorrow's weapon, Garrick's upgrade to tier 1 and the Upgrade tab all work (`floor1_gear_path`). Still to check in the client: the temper quest, the Gate Hound's shards and the Axe-Lord's awakening, which need a party-strength test.)* Done when: a new character can follow the "Next upgrade" window from level 1 to the Floor 1 boss, tested in the real game.
- [~] **P6 Monsters that fight differently** *(2026-11-25: seen in the client: thieving rats, the wolf's howl, a sproutling mending a friend, the sentinel's shield (p6_tricks). Still to see on screen: the boar's charge, the mole's burrow, the snapper's drag, the bandit's smoke. The last four built: thieving field rats, wolves that howl for the pack, sproutlings that mend each other, the sentinel's shield wall; in-game tests. To tick: the p6_tricks autopilot run after the restart)* *(2026-11-24: 10 behaviours, the shardling burst and 5 elites built; to tick: see them in the client; still to do: the coin-stealing rat, the wolf's call, sproutling heals, the sentinel's shield wall)* (FLOOR1_REVIEW.md F1-10, F1-11): one signature behaviour for each of the 13 regular Floor 1 monsters (poison, charge, call for help, burrow, drag, slow, steal, field, smoke, shield wall, burst/split, heal friends) and one rare named elite per ground, in `tools/gen_monsters.py`. Done when: each behaviour is seen in the autopilot log or a screenshot, and `tools/balance.py --check` passes.
- [~] **P7 The first hour shows the tower** *(2026-11-25: the yard now has the Spire's sealed door in a stone wall and a first-clears stone that names who opened each floor (in-game test). The rest of Q47 (a bigger rebuild) stays with P7)* *(2026-11-24: race line at login and lit lamps done; the yard rebuild waits on Q47)* (F1-01, F1-03, F1-04, F1-05): arrival at the foot of the Spire with the sealed Floor 2 gate and a first-clears plaque; the floor race in the login message and Journal; Pell's quest listed as soon as offered; tutorial gates for cursors, the Journal and sword skills. Done when: rendered, and a fresh autopilot character walks it with every gate passed.
- [~] **P8 A spell before level 8** *(2026-11-24: built, first attack at level 1, heal at 4, in-game test; to tick: cast with a level 2 Pilot in the client)* (F1-02): each class gets an attack spell at level 1 and a utility by level 4. Done when: the spell tests cast them with a level 2 Pilot of each class.
- [ ] **P3b Fires and more lights in Hearthgate** (cut from P3, 2026-11-25): a few campfires, braziers at the gates, lit windows. Done when: rendered and seen in the client at night.
- [ ] **P9b Escort or rescue quest** (cut from P9, 2026-11-25): "find the Lost Patrol's survivor in the Bandit Vault and walk him home". Needs the Bandit Road rebuild (H8) and an NPC that follows the player. Done when: autopilot walks the survivor home.
- [ ] **P12b Leaderboards on the website** (cut from P12, 2026-11-25): top climbers, first clears and Death Game survivors on the website. Needs 7.1 (the website reading the database). Done when: the page shows the same list as the Monument.

## Grok's market research picks (Jay's answers, 2026-11-25). After the playtest fixes above.
Research summary: `docs/RESEARCH_GROK_MARKET_2026-11-25.md`. Design: DESIGN.md 3.6 (beacons), 4 (Chronicle), 12 (count and ledger), 15 (Spire Pressure).
- [ ] **M2 Clean Count and Exile Ledger** (R2, as Jay changed it: no limits on extra characters): the website shows characters online and real people online; cheating bans are listed publicly with their reason and cover the person's other accounts. Needs 7.1 for the website pages. Done when: the count page matches the server's own count, and a test ban shows on the ledger and blocks a second account.

## Phase R — Make it real (from REVIEW.md, 2026-11-11). Do this before anything else.
The review found that phases 2–8 were built wide and thin before anyone played Phase 1. **No new features until this phase is done.** Section numbers in brackets point into `REVIEW.md`. Order = priority.
- [ ] **R0 🧑 Jay plays the first hour** (same as 1.21): new character → Registrar → level 15 → a secret → a death. Then a 3-person Floor 1 boss run. Every note becomes a fix or a task.
- [ ] **R10b Missing gold sinks** (cut from R10, 2026-11-13): item repairs need a durability system that doesn't exist yet (design first), and travel between floor towns is free. Done when: a repair or travel fee exists in game with an in-game test, and `tools/balance.py` counts it.
- [~] **R10c House prices per floor** *(2026-11-25: built: tools/balance.py prices houses per floor (about 8 hours of that floor's hunting; Floor 1 unchanged), !buyhouse charges it, every floor checked; in-game test of the price rule. Still to do: a real !buyhouse on a higher floor in the client)* (found by R10): the engine charges 1,000 gold a tile everywhere, so from Floor 3 up a house costs under 4 hours of hunting. Done when: `!buyhouse` (a core override) charges by floor and `tools/balance.py` checks every floor's houses.
- [ ] **R13b Floor 2 hand-tuned** (cut from R13, 2026-11-13): Floor 2's map is still the shared placeholder generator; give it its own layout (walled grounds with loops, as Floor 1) and an easy-to-hard camp ladder. Done when: rendered, walk test passes, walked in the client.
- [~] **R18 Tests that reach the real game** *(2026-11-13: end-to-end tests added and passing; the GitHub boot workflow is written but its first run is not checked yet)* [7.5]: boot test runs on GitHub; end-to-end tests per headline rule (reach Floor 2 without a kill, die as each difficulty, wait out a skull, Fortune Hall cut).

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
- [~] **6.5 Swap in all art Jay has delivered so far.** *(2026-11-25: the 13 approved monsters are in the game (seen in the client). Still to do: NPCs and player outfits (need their own look numbers: ART_REQUESTS.md))*
- [ ] **6.5b Android client build** *(on hold until after the friends test, per REVIEW 9.2; 6.3b translations likewise)* (OTClient Redemption's Android target). Done when: an APK builds in CI.
- [ ] **6.6 🧑 Phase 6 playtest.**

## Phase 7 — Accounts, website, donation shop
- [ ] **7.1 Website** (account creation, **character creation** (Jay, 2026-11-14: "players will create characters via the website. they will sign up there, login, and create their character from the website"; the sign-up page in `tools/login_server.py` is a stopgap that makes the first character with the account), character pages, floor monument, secret list, Hall of Fame, rules). Free software only (MyAAC or similar). *(Part done: static pages — home, how to play, the tower, vocations, difficulty, PvP rules, events, rules — built by `tools/gen_site.py` into `website/public/`. Still to do: account creation, character pages, Hall of Fame (need MyAAC + the database).)*
- [ ] **7.2b Website wiki pages** generated from our data files; boss cooldowns and event countdowns on the website; Discord announcements. *(Part done: floors, fish and secret counts generated from our data. Still to do: boss cooldowns, event countdowns, Discord announcements.)*
- [ ] **7.3 🧑 Jay picks shop prices and payment setup** (QUESTIONS.md).
- [ ] **7.4 Shop worth buying from** [REVIEW 6.2, 6.4]: 8–12 shop-only outfits, a few mounts, name effects, house themes (nothing the Season Path or Housewright already gives); depot space sold for gold instead; a permanent purchase record per sale.
- [ ] **7.5 🧑 Before taking any money** [REVIEW 6.5]: privacy policy, terms, refund policy, age statement, account deletion, all CipSoft art gone, the trade/gambling question settled (Q15, Q17). Ask a professional about tax and law.

## Phase 8 — Seasons
- [ ] **8.4 Secrets move each season, plus a few weekly rotating secrets** [REVIEW 3.10].

## Phase 9 — Friends test (still on Jay's PC)
*Starts only after Phase R. Friends test is invite-only (REVIEW 8.3) and wiped afterwards.*
- [~] **9.1 Remote friend access on Jay's PC** (free options only; written guide; a tunnel so friends never see Jay's home address [REVIEW 7.7]). 🧑 *(2026-11-24: built over Tailscale: `Open-Friend-Access.bat` (ports 8080/7172/8090, Tailscale address only), the login service hands Tailscale clients the Tailscale address, `Share-Client.bat` + `tools/make_friend_client.py` package the client, a Linux/Wine `setup.sh` and a brief for a Grok Bot; guide in windows/README.md. Checked 2026-11-24: the shared client package logged in as Grok Tester through the Tailscale address. To tick: a player connects from another machine. Still to do: a Windows install path for friends that uses the same package.)*
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
- [ ] **J13c Spirebound names for the rune items** (fire, strike, healing, paralysis runes still use the engine's item names; Q36).
- [~] **J9 Ten-minute mini events** *(2026-11-25: the Tower Quiz is built (every 3 hours, halfway between world events; !answer). Still to do: snowball fight, last man standing)* between the big ones (snowball fight, quiz, last man standing at fixed gear).
- [ ] **J10 Forge for Floor 3 and up** (waiting on Q27).

## Floor 1 wilds rebuild (plan ready 2026-11-12: `FLOOR1_WILDS_PLAN.md`, picture `docs/FLOOR1_WILDS_PLAN.png`)
Jay: "monster spawn areas are currently messy and need to have more of a dedicated area where a few players at a time will be able to bot or farm." Follow the plan exactly; one commit per task; details and "done when" are in its Part 9.
- [ ] **W12 (replaced by H13 below)** Walk every rebuilt ground in the real client (cut from W3-W8 on 2026-11-13: the client could not be driven this session). Done when: each ground's gate, hub signs, four loops and cave walked by Jay or by Claude in the client, and one party-sized fight in a cave, notes fixed. (Done so far: Boar Meadow, Toad Pond's hub, the Molework down and up.)

## Floor 1 hunting grounds, third pass (plan ready 2026-11-14: `FLOOR1_HUNTING_PLAN.md`). Do this next.
Jay: "im feeling overhelmed when i walk into a zone with nonstop monsters flooding to me. i think the zones need to bigger... utilize multi height levels as well. layer the monsters throughout the spawn more like real tibia does." Follow the plan exactly; one commit per task; details and "done when" are in its Part 9. Never relax a limit in its Part 3 to make a ground pass.
- [~] **H0 Measure how monsters notice players** (range, walls, changing level, wandering) and check which weekend bonus was on during Jay's test. *(2026-11-14: weekend bonus checked (none / Double Experience); the engine's view range is 11 tiles each way; the in-client measurement is still open because client control was declined this session.)*
- [ ] **H2 New ground table and moved roads** in `maps/floor1_plan.py` (nothing on the map changes yet).
- [ ] **S1b Class-aware economy model**: `tools/gen_economy.py` models what each class earns at each ground (area spells on swarms, keeping distance from slow monsters, healing through long fights) and what a group of 3-4 earns per person; `balance.py --check` then checks the reward targets per ground type (training 100%, class 120% for its class, mixed 110%, group 150%, large group 175%).
- [ ] **S4 Group grounds (3 to 4 players) and the large-group ground (4 to 8, the Old Watchtower)**: mixed packs with a front-liner, a ranged one and a caster; party size 8 in the game too (`party_rules.lua` still says 6); a test with several Pilot characters in one party.
- [~] **S5 Packs stay together and follow their leader in the game** *(2026-11-25: built: idle wolves drift back to their alpha (or the eldest wolf) and a pack joins its member's fight; in-game test. To tick: watch a pack in the client)* (a pack that splits up is just three singles); test on the Meadow Wolf and Grey Alpha.
- [ ] **S6 The floor recipe for Floors 2 to 10**: each floor's grounds get types and habits by the recipe, plus the floor's own twist, in `maps/floors.py`; the generator and checker obey them. (Takes over H12.)
- [ ] **H8 Shard Fields, the Bandit Road, the Old Quarry, the Old Watchtower's groups.** *(After S1 and S2; the group parts are S4.)* *(Shard Fields rebuilt 2026-11-23 and walked in the client 2026-11-24. Still to do: Bandit Road and Old Quarry (they need ruined buildings and a built mine, which the designed-ground builder can't make yet; a Pilot died at Bandit Road's gate), the Watchtower's groups.)*
- [ ] **H9 Roads, trails, signposts, zones on every level, secrets, forest pass.**
- [ ] **H10 Crowd pockets, the weekend-bonus change, cavebot rule, respawn times and the economy re-check.**
- [ ] **H11 In-game tests on the real map** (monsters in range at each route's start, middle and end; monsters let go when you change level); regenerate documents and pictures.
- [ ] **H12 The calm rules become a rule for every floor** (`CLAUDE.md`, and the Floors 2 to 10 generator obeys them). R13b (Floor 2) builds on this.
- [ ] **H13 Walk every ground and level in the real client**; playtest list for Jay.
