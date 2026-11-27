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
- [ ] **G6 Rerun with Grok on a calm PC**: items 5-8 of the session 1 report (invisible attackers, dropped clicks and chat), and `!hunt` refused in town (could not reproduce from the code). Done when: a Grok report with no lag caveat, on the current client package, including a Ranger and a Vanguard past the cheese gate.
- [ ] **1.5 Windows one-click setup.** *(built and checked in the cloud; waiting for Jay's first run)* Done when: 🧑 Jay double-clicks it once and reaches the login screen (logged in PLAYTEST.md).

## Step 3 — The milestone: a real party clears Floor 1 🧑
The moment the whole game is built around has never been played. **Nothing new until this passes.**
- [ ] **N1 The full run** (new, 2026-11-25): a party of real characters (Jay plus Grok testers or friends; several Pilots in one party as the rehearsal) goes yard → Registrar → the grounds → Stair Key → Gate Hound → labyrinth → Axe-Lord, in the real client with no GM shortcuts, and Floor 2 opens with the announcement, the Monument names and the head-start window. Done when: it happens, and every note from it is fixed or filed.
- [ ] **R0 / 1.21 🧑 Jay plays the first hour and signs off Phase 1**: new character → Registrar → level 15 → a secret → a death, then N1. Done when: Jay writes "Phase 1 OK" (or notes) in PLAYTEST.md, and every note is fixed or moved to a task.

- [~] **PT3 Measure the solo pace and Burrow Hills** (party playtest P3-15/16 and P2-10): a party made 138-143k experience an hour in Burrow Hills (3x Wolf Copse), level 3 to 19 in 2h45m, and early money was tight (0-6 gold at levels 7-9). Measure solo with the autopilot after the PT1 fixes (autoloot, meat, coins to bank), then tune Burrow Hills' density/respawn or mole experience in the generators, and early income if still short. Done when: solo pace and Burrow Hills are within `tools/balance.py`'s targets, or Jay accepts the numbers. *(2026-11-26: Burrow Hills measured solo: ~155k experience an hour, 445 kills an hour, so it keeps its old 215 s respawn (not 10.4's faster one). Left: rerun `python tools/autopilot.py burrow_solo14` after the next restart and check it is near the model (~230 kills an hour); a full solo levelling timing; early money after the autoloot/meat/bank fixes.)*

## Step 4 — Floor 1 big enough for a launch evening
The calm rebuild left the level 9-24 solo grounds with 7 to 16 monsters each (about 10-15 solo players in all). At a season launch everyone is in that band at once. Calm stays; the answer is more room.
- [ ] **N8 Quieter kill counting** (found by 9.2): seven scripts count kills with the engine's old kill event, which writes 7-8 warning lines to the server log on every kill (about 150,000 lines an hour at 100 players, copied into a Windows file on Jay's PC). Move them to death events. Done when: a kill writes no warning, every kill-counting test still passes, and `python3 tools/loadtest.py ramp --tee <file on /mnt/c>` shows no extra lag at 100 bots.
- [~] **10.4 Launch-size Floor 1** *(2026-11-26, from N2: monsters come back faster (40% of the wait, at least 40 s), and three new grounds: the Bramble Run (14-20), Smugglers' Ridge (19-26), the Fallen Bastion (23-30); walk test, danger limits and economy pass. Then denser mid grounds (as far as the danger limits allow) and two more boars. Measured (N2 reruns): about 110 at once at 200+ kills an hour, about 50 in levels 9-30 (was 30 and 9). Left: about 40 more, mostly levels 17-30 (more ground there; Thornsnap Hollow, the Bandit Road, the Old Quarry, Smugglers' Ridge and the Bastion are still under 200 with 4 hunters), Boar Meadow (Q73), and walking the new grounds in the client after the next restart.)* (moved up from Phase 10) [REVIEW 5.2]: enlarge the grounds and add grounds and levels until N2's floor total reaches the target (Claude's call: 150 at once across levels 1-35, to be checked against Jay's launch hopes), every one still passing the calm rules. Real map work (MAP_REQUESTS M1). Done when: N2 rerun meets the target and the new areas are walked in the client.

## Step 5 — Floor 2 is a real place
**PAUSED (Jay, 2026-11-26: "didnt realize you were working on floor 2+ content. were still getting floor 1 finished and ready.").** Don't work on Floors 2 and up until Jay says so. What was done before the pause is in PROGRESS.md (2026-11-26 afternoon) and stays in the game; the client walk `r13b_floors23` was stopped part way and never finished.
Winning Floor 1 must not lead to a placeholder.
- [~] **R13b Floor 2 hand-tuned** *(2026-11-26: built (`maps/floor2_plan.py`): eight walled grounds on an easy-to-hard ladder, rendered, walk test passes. Left: the client walk `r13b_floors23` passing at each ground's level.)* (cut from R13, 2026-11-13): its own layout and an easy-to-hard ladder of grounds. Done when: rendered, walk test passes, walked in the client.
- [~] **S6 The floor recipe for Floors 2 to 10** *(2026-11-26: Floors 2, 3 and 4 have their plans and twists; `balance.py --check` enforces the recipe on every planned floor; rule written in CLAUDE.md. Left: Floors 5 to 10.)* (takes over H12: the calm rules become a rule for every floor, in `CLAUDE.md` and the generator): each floor's grounds get types and habits by the recipe, plus the floor's own twist, in `maps/floors.py`. Floor 2 first, then Floor 3.
- [~] **R10c House prices per floor** *(2026-11-25: built and checked on every floor. Still to do: a real !buyhouse on a higher floor in the client)*.
- [ ] **J5b Economy for the next floors:** materials, recipes and burn-rate check per floor (Floor 2 first; what "recipes" means waits on Q57).

## Step 6 — Hearthgate and the arrival look hand-made
- [~] **P7 The first hour shows the tower** *(2026-11-25: the yard has the Spire's sealed door and a first-clears stone; race line at login and lit lamps done. 2026-11-26: the yard dressed as the tower's forecourt (paved, a row of pillars), hedges, trees in every stage, flower beds by the path, a runner to the Registrar; seen in the client. Left: tutorial gates for cursors, the Journal and skills.)* Done when: rendered, and a fresh autopilot character walks it with every gate passed.
- [~] **N3 Hearthgate hand polish** *(2026-11-26: market parasols, goods and a cart, flower pots round the Hearth, a well, a covered wagon, a notice board with live news (seen in the client), carpets as runners, a second storey on five shops so the roofs vary. Left: the houses' shapes (Q69) and Jay's look.)* (new; Q47, FLOOR1_REVIEW F1-50): the Hearth Square stops being an empty marble slab (stalls, trees, carts, a notice board with live news), varied building shapes, the streets dressed. Done when: rendered, Jay says it looks like a town.
- [~] **6.5c Outfit addons as quest rewards** *(2026-11-26: all 16 addon drawings approved and installed; eight quests built, two per class, from Captain Dorrow, Hunter Brannoch, Vesper and Fisher Corwin (say "outfit"); `python3 tools/loadtest.py addon` walks one character per class through both quests with the real NPCs and kill events and checks the addons: PASS. Left: after the next live restart, see an earned addon on a character in the client (Q71 covers the quest choices).)* (Jay, 2026-11-25: "tibia has the base outfit, addon 1 and addon 2... it'll give us more content for quests"). Pipeline and install are ready (art/OUTFIT_RULES.md A1-A7). Done when: each class outfit has two addons Jay approved, each unlocked by its own quest, and a test character earns one through the real quest and sees it in the client.

## Step 7 — Know the real size of the art job
Art, not code, sets the launch date: only 13 monsters are ours.

## Step 8 — Accounts, then the friends test
- [~] **7.1b The website on a secure public address** *(2026-11-26: ready but off: `windows\Open-Public-Website.bat` puts the website (only) on a free https:// `.ts.net` address through Tailscale Funnel; steps in windows/README.md. Waiting on Jay's go (Q70).)* (split from 7.1, 2026-11-25): the site, sign-up and make-another-character pages are served by the login service on port 8080 without HTTPS. Friends over Tailscale are already encrypted; a public launch needs a real web address with HTTPS (free certificate) in front of it. Done when: a player off Jay's network opens the site over https:// and signs up.
- [~] **10.5 Stronger passwords and two-step login** [REVIEW 7.4], through the website package. *(2026-11-25: built in the login service: passwords stored as slow salted hashes (old ones upgrade at the next login), the commonest passwords and ones containing your own names refused, optional two-step login with an authenticator app plus six backup codes, and a change-password form, all on the new Account security page (/security). Checked against the real database with a test copy of the login service: no code, wrong code, right code, backup code, switching off. To tick: after the next restart, Jay switches it on with his phone and logs in once with the game client, which asks for the code (about 2 minutes).)*
- [~] **9.1 Remote friend access on Jay's PC** 🧑 *(2026-11-24: built over Tailscale and checked with the shared client package. To tick: a player connects from another machine. 2026-11-25: the Windows path for friends is built: a one-line PowerShell installer (desktop shortcut, updates when run again), a download page on port 8090 and a ready-to-send invite in .local/friend_invite.txt; the installer was tested on this PC with a stand-in package (install, update, server unreachable).)*
- [ ] **9.3 🧑 Friends playtest weekend + fixes** (invite-only, Floors 1-2, wiped afterwards).

---

## Later — after the friends test (not ordered yet)
Kept so nothing is lost. Several wait on Jay's answers to Q54-Q61 (the review's cuts).

**Money monsters (Jay, 2026-11-25)**
- [ ] **N6 The "money monsters"** (new; Jay: "monsters that vets will look forward to running into once in the game. Bosses, the fire boar, and a few others that haven't been made yet"; the fire boar is our red-crested Bristle Boar, already made): make the art for the rest of the list in ART_REQUESTS.md Batch 11 (the bosses first), and give each a website showcase render (a larger, sharp render from the Blender model, never a stretched sprite) for the banner. Possibly rename the Bristle Boar to something like Frenzied Boar (Q63). Done when: every boss on the list walks across the website banner.

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
