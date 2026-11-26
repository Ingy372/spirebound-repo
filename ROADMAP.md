# Spirebound Roadmap

One ordered list (rewritten 2026-11-25 after the project review; Jay: "Yes, rewrite it"). Work top to bottom. Each task has a **Done when** line that can be checked. Check a task off (`[x]`) only when its Done-when has been checked, and write how in `PROGRESS.md`.

"Boot test" = `tools/test_boot.sh` (server starts with our datapack, prints "online", zero errors in the log). It must pass after every task.

Legend: 🧑 = needs Jay (playtest or decision). `[~]` = partly done. Everything else Claude does alone.

Finished tasks live in `ROADMAP_DONE.md` (move each task there when it is ticked).

**The one rule (review, 2026-11-25): nothing new gets built until Step 3 passes.** No new systems, events, abilities or floors. New playtest notes are the only thing that jumps the queue, and they go into Step 1. Ideas that come up meanwhile go in "Later" at the bottom.

---

## Step 1 — The first hour works for a brand-new player
Every real tester has hit a blocker in the first 30 minutes. Fix what is left, on fresh characters at the level a new player really has.
- [ ] **G10b Hands-on keyboard check** (cut from G10 and J6, 2026-11-25: the autopilot can't press keys): Ctrl+1-6 fire the weapon skills with chat on and off; Shift+1-6 fire them only with chat off and otherwise type normally; Enter after clicking a skill button goes to chat, not the skill; the first line typed after switching chat tabs is sent. Done when: checked by Jay or a Grok run on the current client.
- [ ] **G12b The last two clean-ups, seen** (cut from G12): the character list shows the new level and path after a logout (the client now asks the login service again), and the six townsfolk talk about once every 3 minutes each (was about once a minute). Done when: both seen in the client.
- [ ] **G6 Rerun with Grok on a calm PC**: items 5-8 of the session 1 report (invisible attackers, dropped clicks and chat), and `!hunt` refused in town (could not reproduce from the code). Done when: a Grok report with no lag caveat, on the current client package, including a Ranger and a Vanguard past the cheese gate.
- [ ] **1.5 Windows one-click setup.** *(built and checked in the cloud; waiting for Jay's first run)* Done when: 🧑 Jay double-clicks it once and reaches the login screen (logged in PLAYTEST.md).

## Step 2 — Finish Floor 1's last third (levels 19 to 35)
The end of the floor, right before the boss, is its weakest part: two grounds still swarm at the gate and the group hunting isn't built.
- [ ] **H8 The Bandit Road and the Old Quarry rebuilt** *(Shard Fields rebuilt 2026-11-23 and walked in the client 2026-11-24. These two need ruined buildings and a built mine, which the designed-ground builder can't make yet; a Pilot died at Bandit Road's gate. Checker today: pull 19.5 and 22.1 against 6, no quiet tiles.)* Done when: both pass `tools/hunt_check.py` on every level, have their elite and chest, and a Pilot of the right level walks in and survives, in the client.
- [ ] **S4 Group grounds (3 to 4 players) and the large-group ground (4 to 8, the Old Watchtower)**: mixed packs with a front-liner, a ranged one and a caster; party size 8 in the game too (`party_rules.lua` still says 6); a test with several Pilot characters in one party.
- [~] **S5 Packs stay together and follow their leader in the game** *(2026-11-25: built; in-game test. To tick: watch a pack in the client)*; test on the Meadow Wolf and Grey Alpha.
- [~] **P6 Monsters that fight differently** *(2026-11-25: seen in the client: thieving rats, the wolf's howl, a sproutling mending a friend, the sentinel's shield. Still to see on screen: the boar's charge, the mole's burrow, the snapper's drag, the bandit's smoke.)* (FLOOR1_REVIEW.md F1-10, F1-11). Done when: each behaviour is seen in the autopilot log or a screenshot, and `tools/balance.py --check` passes.
- [ ] **P9b Escort or rescue quest** (cut from P9, 2026-11-25): "find the Lost Patrol's survivor in the Bandit Vault and walk him home". Needs H8 and an NPC that follows the player. Done when: autopilot walks the survivor home.
- [ ] **H9 Roads, trails, signposts, zones on every level, secrets, forest pass.** *(Check first what the ground rebuilds already covered; H2, the old "new ground table and moved roads" task, is folded in here.)*
- [ ] **H10 Crowd pockets, the weekend-bonus change, cavebot rule, respawn times and the economy re-check.**
- [ ] **S1b Class-aware economy model**: `tools/gen_economy.py` models what each class earns at each ground and what a group of 3-4 earns per person; `balance.py --check` then checks the reward targets per ground type (training 100%, class 120%, mixed 110%, group 150%, large group 175%).
- [~] **H0 Measure how monsters notice players** in the client (range, walls, changing level, wandering). *(2026-11-14: weekend bonus checked; the engine's view range is 11 tiles each way; the in-client measurement is still open.)*
- [ ] **H11 In-game tests on the real map** (monsters in range at each route's start, middle and end; monsters let go when you change level); regenerate documents and pictures (FLOOR1.md still says "about 1,000 monsters").
- [ ] **H13 Walk every ground and level in the real client** (takes over W12: each ground's gate, hub signs, routes and cave, and one party-sized fight in a cave); playtest list for Jay.

## Step 3 — The milestone: a real party clears Floor 1 🧑
The moment the whole game is built around has never been played. **Nothing new until this passes.**
- [~] **P1 Gear and weapon progression** *(2026-11-24: Dorrow's weapon, Garrick's upgrade to tier 1 and the Upgrade tab work in the client. Still to check: the temper quest, the Gate Hound's shards and the Axe-Lord's awakening, which need a party.)* Done when: a new character can follow the "Next upgrade" window from level 1 to the Floor 1 boss, tested in the real game.
- [ ] **N1 The full run** (new, 2026-11-25): a party of real characters (Jay plus Grok testers or friends; several Pilots in one party as the rehearsal) goes yard → Registrar → the grounds → Stair Key → Gate Hound → labyrinth → Axe-Lord, in the real client with no GM shortcuts, and Floor 2 opens with the announcement, the Monument names and the head-start window. Done when: it happens, and every note from it is fixed or filed.
- [ ] **R0 / 1.21 🧑 Jay plays the first hour and signs off Phase 1**: new character → Registrar → level 15 → a secret → a death, then N1. Done when: Jay writes "Phase 1 OK" (or notes) in PLAYTEST.md, and every note is fixed or moved to a task.
- [~] **R18 Tests that reach the real game** *(2026-11-13: end-to-end tests added and passing; the GitHub boot workflow is written but its first run is not checked yet)*: boot test runs on GitHub; end-to-end tests per headline rule.

## Step 4 — Floor 1 big enough for a launch evening
The calm rebuild left the level 9-24 solo grounds with 7 to 16 monsters each (about 10-15 solo players in all). At a season launch everyone is in that band at once. Calm stays; the answer is more room.
- [ ] **N2 Measure how many players Floor 1 feeds** (new; uses 9.2): scripted clients hunting each ground, counting kills per player per hour as the ground fills, with the crowd system on. Done when: a table per ground of "players before each gets under 200 kills an hour", and a floor total.
- [ ] **9.2 Load test with scripted clients** (target 100 bots on Jay's PC without lag).
- [ ] **10.4 Launch-size Floor 1** (moved up from Phase 10) [REVIEW 5.2]: enlarge the grounds and add grounds and levels until N2's floor total reaches the target (Claude's call: 150 at once across levels 1-35, to be checked against Jay's launch hopes), every one still passing the calm rules. Real map work (MAP_REQUESTS M1). Done when: N2 rerun meets the target and the new areas are walked in the client.

## Step 5 — Floor 2 is a real place
Winning Floor 1 must not lead to a placeholder.
- [ ] **R13b Floor 2 hand-tuned** (cut from R13, 2026-11-13): its own layout and an easy-to-hard ladder of grounds. Done when: rendered, walk test passes, walked in the client.
- [ ] **S6 The floor recipe for Floors 2 to 10** (takes over H12: the calm rules become a rule for every floor, in `CLAUDE.md` and the generator): each floor's grounds get types and habits by the recipe, plus the floor's own twist, in `maps/floors.py`. Floor 2 first, then Floor 3.
- [~] **R10c House prices per floor** *(2026-11-25: built and checked on every floor. Still to do: a real !buyhouse on a higher floor in the client)*.
- [ ] **J5b Economy for the next floors:** materials, recipes and burn-rate check per floor (Floor 2 first; what "recipes" means waits on Q57).

## Step 6 — Hearthgate and the arrival look hand-made
- [~] **P7 The first hour shows the tower** *(2026-11-25: the yard has the Spire's sealed door and a first-clears stone; race line at login and lit lamps done. Left: the bigger yard rebuild (Q47) and tutorial gates for cursors, the Journal and skills.)* Done when: rendered, and a fresh autopilot character walks it with every gate passed.
- [ ] **N3 Hearthgate hand polish** (new; Q47, FLOOR1_REVIEW F1-50): the Hearth Square stops being an empty marble slab (stalls, trees, carts, a notice board with live news), varied building shapes, the streets dressed. Done when: rendered, Jay says it looks like a town.
- [ ] **P3b Fires and more lights in Hearthgate** (cut from P3): a few campfires, braziers at the gates, lit windows. Done when: rendered and seen in the client at night.
- [~] **6.5 Swap in all art Jay has approved so far.** *(2026-11-25: the 13 approved monsters are in the game. Still to do: NPCs and player outfits (need their own look numbers: ART_REQUESTS.md))*

## Step 7 — Know the real size of the art job
Art, not code, sets the launch date: only 13 monsters are ours.

## Step 8 — Accounts, then the friends test
- [ ] **7.1 Website** (account creation, **character creation** (Jay, 2026-11-14: "players will create characters via the website"), character pages, floor monument, secret list, Hall of Fame, rules). Free software only (MyAAC or similar). *(Part done: static pages built by `tools/gen_site.py`. Still to do: account creation, character pages, Hall of Fame.)*
- [ ] **10.5 Stronger passwords and two-step login** [REVIEW 7.4], through the website package.
- [~] **9.1 Remote friend access on Jay's PC** 🧑 *(2026-11-24: built over Tailscale and checked with the shared client package. To tick: a player connects from another machine. Still to do: a Windows install path for friends that uses the same package.)*
- [ ] **9.3 🧑 Friends playtest weekend + fixes** (invite-only, Floors 1-2, wiped afterwards).

---

## Later — after the friends test (not ordered yet)
Kept so nothing is lost. Several wait on Jay's answers to Q54-Q61 (the review's cuts).

**Floors and seasons**
- [ ] **4.7 🧑 Phase 4 playtest** (Floors 2 to 5). **5.8 🧑 Phase 5 playtest** (Floors 6 to 10 and Azhrakkar). *(How many floors open at launch: Q54.)*
- [ ] **8.4 Secrets move each season, plus a few weekly rotating secrets** [REVIEW 3.10].
- [ ] **J10 Forge for Floor 3 and up** (waiting on Q27).

**Systems waiting on a decision**
- [ ] **N5 One Journal page for daily and weekly rewards** (new; Q58): fold the overlapping reward loops into three or four, shown in one place.
- [ ] **3.5b Workshop bench and garden** (needs a crafting/cooking design; Q57 may cut it).
- [~] **J5 Economy** / **J5c Crafting playtest in the client** (Q57).
- [~] **J9 Ten-minute mini events** *(the Tower Quiz is built. Still to do: snowball fight, last man standing)* (Q59: events wait for players).
- [ ] **J15c Wild PvP verdict**: after a few weeks of the weekly event, ask the players.
- [ ] **R10b Missing gold sinks** (cut from R10): item repairs (design first) and travel fees between floor towns. Done when: one exists in game with a test, and `tools/balance.py` counts it.
- [ ] **2.13 🧑 Phase 2 playtest** (core systems). **3.7 🧑 Phase 3 playtest** (houses and gambling; Q56).

**Small spell and item jobs**
- [ ] **J15b Fire runes burn vines too.** **J14b Dawnpiercer light arrow** (a projectile of our own). **J13c Spirebound names for the rune items** (Q36).

**Client and languages** (on hold until the text stops changing)
- [ ] **6.3 / 6.3b Portuguese and Spanish**: server messages and the Registrar are done; the other 75 NPCs, quest text, secret hints, item and monster names are not.
- [ ] **6.5b Android client build.** **6.6 🧑 Phase 6 playtest.**

**Website, shop and money**
- [ ] **M2 Clean Count and Exile Ledger** (needs 7.1). **P12b Leaderboards on the website** (needs 7.1). **7.2b Website wiki pages**, boss cooldowns, event countdowns, Discord announcements.
- [ ] **7.3 🧑 Jay picks shop prices and payment setup.** **7.4 Shop worth buying from** [REVIEW 6.2, 6.4]. **7.5 🧑 Before taking any money** [REVIEW 6.5]: policies, all CipSoft art gone, the trade/gambling question settled (Q15, Q17).

**Going public** (only after Jay says testing is done)
- [ ] **10.1 🧑 Jay picks a host.** **10.2 Server setup scripts, backups, monitoring** *(done for Jay's PC)*. **10.3 Launch checklist** (placeholders replaced, rules page, Discord, countdown, open beta that gets wiped, staffed first week, update/rollback routine, off-server backups).
