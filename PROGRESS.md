# Progress log

Newest at the bottom. 2–3 lines per finished task, plain English.

---

### 2026-11-08 — Session 1: new plan, repo cleanup
- **Repo fix:** your PC's copy of the repo was linked to your *Dojo-game* GitHub repo instead of *spirebound-repo*. Re-linked it to spirebound-repo and brought in the one newer commit that was only on GitHub. (Stray branch in Dojo-game: see QUESTIONS.md Q2.)
- **Kept, not deleted:** the October design pack (`docs/`, `data/`, `tools/`) and the phase-0 TFS server work. The old `CLAUDE.md` is replaced by the new one; the old `STATUS.md`, `CHANGELOG.md` and `OWNER_INPUT.md` (your player-experience answers, which DESIGN.md still draws on) moved into `docs/` with "_2026-10" in their names. Work now happens on the `main` branch (the phase-0 branch was merged in).
- **Task 1.1 done:** wrote DESIGN.md (game bible from your brief, gaps marked "Claude's call"), ROADMAP.md (10 phases, Phase 1 = character creation → Floor 1 boss → Floor 2 unlocks), CLAUDE.md (your working rules), QUESTIONS.md (9 questions, each with a recommendation already assumed), PLAYTEST.md, ART_REQUESTS.md (first batch with Grok prompts), MAP_REQUESTS.md.
- **Research:** Canary v3.6.1 (protocol 15.11) and OTClient Redemption 4.2 both publish ready-made Windows builds, so your PC never needs a compiler. Cyntara's bot rules summarized in DESIGN.md §12.

### 2026-11-08 — Task 1.2: old TFS setup archived
- Moved the TFS 1.4.2 server, its config scripts, the 10.98 art pipeline, the old test client and old CI into `legacy/tfs-1.4.2/` (nothing deleted; `legacy/README.md` lists every item and why).
- Kept in use: name checker (now also scans DESIGN.md, ART_REQUESTS.md and the new datapack), table generator, map writer and map compiler. Name check: 0 banned names.

### 2026-11-08 — Tasks 1.3, 1.4, 1.12: the Canary server boots with our datapack
- `tools/build_server.py` downloads the pinned Canary v3.6.1 and assembles a server from it plus our own files; `tools/test_boot.sh` starts it, runs in-game tests and fails on any error. Result: **server online, 0 errors, 1 in-game test passed** (cloud test box).
- New datapack `server/data-spirebound/` (from Canary's small sample pack, all CipSoft-named monsters/NPCs/quests stripped). Prey, hunting tasks, Wheel of Destiny, Forge monsters and boosted boss are switched off; newbie protection set to level 50; 2 characters online per account.
- XP stages from DESIGN.md 5.5 are live (25x early down to 2x at 401+), checked by an in-game test. The world map is still Canary's sample map as a stand-in until task 1.8.

### 2026-11-08 — Tasks 1.9, 1.10, 1.11: vocations, the Registrar, difficulty modes
- Four vocations live: Vanguard, Ranger, Arcanist, Mystic, promoting to Blade Warden, Far Warden, High Arcanist, Elder Mystic (Canary's extra Monk vocation removed).
- New NPC **Registrar Maelis** (Arrival Yard): pick a vocation (with starter kit) and Normal / Hardcore / Death Game; later, "step down" to an easier mode (never up).
- Difficulty effects: +25%/+50% XP, +15%/+30% loot, Hardcore death costs ×1.5 XP. Death Game: killed by monsters = character retired to the Memorial with a server announcement; if an outside player hit you in the last 60 s it counts as PvP and you survive (party, guild or same-IP hits don't count). Boot test: online, 0 errors, 5 in-game tests pass. Hardcore extras (skills, blessing cap, item drops) queued as task 2.14.

### 2026-11-08 — Tasks 1.16, 1.17: party bonus and the tower's memory
- Parties: each member gets (XP × (1 + 30% per extra member + 10% per extra vocation)) ÷ members; parties cap at 6; level range 1.5× (Canary's setting already matched).
- World floor records: field boss / floor boss / first-clear credit / last hit are saved for the whole server and survive restarts (checked across two boots). Credit keeps the top 20; boss enrage = 60 min solo, 16 min for 4, 8 min for 8 or more. GM test command `/floor` shows, opens, clears or resets floors. Boot test: online, 0 errors, 9 in-game tests pass.

### 2026-11-08 — Task 1.14: sword skills v1
- 24 sword skills live (3 for each of the 8 weapon families: sword, axe, club, bow, crossbow, spear, wand, rod). Each needs the right weapon in hand, has its own cooldown plus a 1-second shared cooldown, and is tagged Opener / Link / Finisher.
- Combo: Opener → Link → Finisher within 4 seconds each = Finisher hits 30% harder and shouts "COMBO!". For now cast by typing the skill's name (e.g. `arc slash`); the hotbar comes with the client work (task 1.20). Boot test: online, 0 errors, 13 in-game tests pass.

### 2026-11-08 — Tasks 1.5 (built), 1.6: one-click Windows setup and test accounts
- New `windows/` folder: **Install-Spirebound.bat** (installs free MariaDB + C++ runtime with winget, downloads Canary, OTClient and the placeholder Tibia art, builds everything into the hidden `.local` folder, creates the database), **Start-Spirebound.bat**, **Stop-Spirebound.bat**, and a plain-English README.
- Checked in the cloud: every download link answers, the script parses, its server config comes out byte-for-byte identical to the tested Linux build, and its client edits (connect to this PC, protocol 15.11) apply correctly. It has not run on Windows yet: that's your first playtest step.
- Test account **jay / spirebound** with characters **Jay** (gamemaster) and **Climber** (new player); created on every install/boot, checked by the boot test.

### 2026-11-08 — End of session 1
- Wrote WEEKLY_REPORT.md (install test checklist for Jay). All commits are on Jay's PC on the `main` branch; **not pushed to GitHub** (no upload access from this session; QUESTIONS.md Q1).
- Next session: task 1.7 (map tools for 15.x item ids), then 1.8 (Floor 1 placeholder map), 1.13, 1.15, 1.18, 1.19, 1.20.

### 2026-11-08 — Jay's answers applied: seasons, cavebot, more spells
- Seasons confirmed (DESIGN.md §4, QUESTIONS Q3 answered).
- Bots (DESIGN.md §12 rewritten): cavebot and auto-targeting are built into our client. Cavebot on = 30% XP, 50% loot, visible gear icon, no secrets/boss rooms, penalty lingers 10 min; auto-targeting alone is free. Numbers are my call, open for veto as Q10. New roadmap tasks 2.12 (server penalty) and 2.12b (client cavebot from OTClient's built-in bot module).
- Spells (new DESIGN.md §5.3b): about 20 per vocation (8 shared + 12 own) covering attack, healing, support and utility; 3 per vocation are "Lost Arts" earned only from quests, secrets and bosses. New roadmap tasks 1.14b (spells to level 50 + trainers) and 4.6b (the rest).

### 2026-11-08 — More of Jay's answers applied
- Cavebot: 45% XP (was 30%), no visible marker, other rules confirmed. The 10-minute linger is explained and waiting on Jay (QUESTIONS Q11).
- Spells now unlock automatically by level, no gold. Ammo can't be conjured: Ranger's 3 conjure spells became Keen Sight, Tracker's Mark and Disengage. Ammo + potions are the gold burn.

### 2026-11-08 — Research: what top servers share
- Looked at RubinOT, Aurera Global, Cyleria, Baiak-Ilusion, Gunzodus (otservlist snapshot, 2026-11-08). Report: `docs/RESEARCH_TOP_SERVERS_2026-11.md`.
- Added DESIGN.md §15 with what we adopt (autoloot, weekend bonuses, guild castle "Spire Siege", equal-footing arena events, offline training, livestream, hunting tasks, Season Path, catch-up rules, Android client, website wiki) and our answer to the top reasons players quit. New roadmap tasks 2.15–2.17, 5.7b–e, 6.5b–c, 7.2b. Summary question Q12.

### 2026-11-08 (overnight) — Tasks 1.7, 1.8, 1.13, 1.18, 1.19: Floor 1 is playable end to end
- **Map:** new map generator (`tools/mapgen.py`) and a Floor 1 placeholder (`maps/layout_floor1.py`): Hearthgate with temple, depot, 4 shops, 6 houses, monument, drain grate; Millcross village with 3 cottages; a river; 3 starter fields and 6 hunting camps; the Old Watchtower apex spawn with a rope spot to a cave; the Pass arena; a 3-level maze labyrinth; the boss room; and a Floor 2 landing. Previews in `docs/previews/`. 116 monsters spawn.
- **Monsters:** 13 Floor 1 monsters + 2 bosses generated from one table (`tools/gen_monsters.py`), placeholder Tibia looks.
- **Bosses:** the Gate Hound (howls in a telegraphed ring, summons wolves) seals the Pass until its first death, then never returns. The Axe-Lord has 3 phases (marked tiles, guards at 60%, long blade and 3-tile line at 25%), resets if left alone, enrages by headcount, credits the top 20 recent damage dealers, awards titles, opens the stair to Floor 2 with a server-wide announcement, and respawns every 30 minutes for repeat kills. Boot test: online, 0 errors, 20 in-game tests pass (tests now only run on test boots, never on your playing server).
- Old 10.98 map tools and the test town moved to `legacy/`.

### 2026-11-08 (overnight) — Task 1.15: Hearthgate's shopkeepers
- Six NPCs from one table (`tools/gen_npcs.py`): Priest Odran (free healing under level 50 or when badly hurt; blessings for gold), Banker Tolliver (balance/deposit/withdraw/transfer), Merchant Wenna (rope, shovel, food, fishing gear), Quartermaster Bryn (potions and ammunition: the main gold burn), Weaponsmith Garrick (starter weapons for all 8 weapon types), Armorer Hesta (leather to brass). The generator blocks buy-low/sell-high loops. Boot test: 21 in-game tests pass.
- Known gap: blessing names still use Canary's built-in (Tibia) names; renamed when the blessings get their own design.
