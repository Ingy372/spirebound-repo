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

### 2026-11-08 (overnight) — Task 1.14b: spells to level 50
- 42 spells live, unlocking automatically at their level with a "New spell" message: 8 shared (light, find a player, first aid, cleanse, climb up/down, food, haste, strong light) plus each vocation's own up to level 50 (Vanguard 7, Ranger 8, Arcanist 9, Mystic 10). Includes party buffs, damage-reduction stances, a taunt, dashes, blink, summons (Ember Sprite, Wolf Companion), rune conjuring (fire, strike, healing, paralysis runes) and no ammo conjuring.
- Tibia's own spells and incantations are removed from the server build, and Canary's weapon/rune files are rewritten to our vocation names, so Arcanists can use wands, Rangers bows, and so on (same step added to the Windows installer and checked to give identical results). Boot test: 25 in-game tests pass.

### 2026-11-08 (overnight) — Task 1.20: Spirebound client UI v1
- New client module `client/modules/game_spirebound` (installed automatically): floor name at the top of the screen, a Hardcore / Death Game label, a sword-skill bar at the bottom (the skills of the weapon in your hand; click or Shift+1..6; cooldowns count down; colours show Opener / Link / Finisher), and SAO cursors over players (green, orange, red, dark red). The server sends floor, difficulty, skills and cast cooldowns on a private channel. Boot test: 26 in-game tests pass.
- Not yet verified in the real client: that's in your Phase 1 playtest. Cursor images are simple placeholders.

### 2026-11-08 (overnight) — Tasks 2.1–2.4: PvP protections
- **Zones:** every tile is Town (safe), Guarded, Open, Contested, Deadzone or Boss room, from the map. The client shows the zone next to the floor name.
- **Skulls:** our own unjust-kill counter (the engine's is off): a kill near town counts triple, on someone 30+ levels lower counts double, on a Death Game character counts double, in Contested/Deadzone never counts. Red = 3 a day / 5 a week / 10 a month, lasts 7 days; black = 6 a day / 10 a week, 14 days. Murderers: double death penalty, thrown out of towns and boss rooms, no NPC service; black marks can't party. Town killers are hunted by the guards for 30 minutes.
- **Protections:** nobody under level 50 can attack or be attacked (except in boss rooms), and under-50s are kept out of Contested/Deadzone; you can't start a fight with someone under 70% of your level outside Contested/Deadzone/boss rooms (they can still fight back; murderers are never protected); 3+ attackers on one player = 10% less damage per extra attacker (max 40%); the same guild killing you twice in 6 hours = 30-minute Sanctuary from that guild. Boot test: 30 in-game tests pass.
- Gaps: the 2-hour new-character protection and "black skulls can't use teleport gates" are not built yet.

### 2026-11-08 (overnight) — Tasks 2.5, 2.6: bounties and guild wars
- **Bounty Warden Cass** (by the Monument): becoming a murderer fines you up to level × 1,000 gold from your bank, which becomes an automatic bounty; anyone can add gold ("bounty 5000 name"); killing the murderer pays the whole bounty, except to the same computer, guild, party or a recent party partner. "board" lists the top bounties.
- **Guildwarden Sela**: found a guild (level 30, 20,000 gold), offer a war ("war 7 0 GuildName" = 7 days, no kill limit), the other leader must "accept" (or "reject"). 10,000 gold from each side, 1–14 days, optional kill limit, no re-declaring on the same guild for 7 days. War kills never make anyone a murderer (Canary handles the war itself). Boot test: 33 in-game tests pass.

### 2026-11-08 (overnight) — Tasks 2.7, 2.8: secrets and Vesper the Info Broker
- 12 Floor 1 secrets on the map (old pack ideas): the Underkeep grate, Old Tusk (a secret boar mini-boss that spawns from his mud wallow every 30 min), Miller's Race, Inn Smith, North Crack (a shortcut to Millcross for those who found it), Firefly Hollow (night only), Sealed Shrine (wakes two bandit captains), Dye Well, Empty Camp (a diary with a boss hint), Well Vein, Coward Pup, Gate Balcony. Each pays a one-time reward to every finder.
- **Vesper** (by the Monument): "secrets" shows what you found, "sell <name>" pays 1,500 / 3,000 / 6,000 gold (small / medium / large on Floor 1) to your bank, makes it public with a server-wide announcement, and adds it to her "list" with directions. Keeping it private never stops anyone else from finding it. Explorer titles at 10 / 50 / 100 discoveries. Boot test: 35 in-game tests pass.

### 2026-11-08 (overnight) — Tasks 2.12, 2.12b: the built-in cavebot rules
- **Server:** when the client reports the cavebot is on, you get 45% XP and half the loot (each corpse item has a 50% chance to vanish; stacks are halved), secrets don't trigger, and boss rooms send you back to the temple. The cut lasts 10 more minutes after switching off (Q11). No visible marker. Auto-targeting alone costs nothing.
- **Client:** OTClient Redemption already ships a full bot (vBot: cavebot, target bot, healing, looting). The installer now adds a small Spirebound script that reports cavebot on/off to the server, removes vBot's connection to an outside bot server and its "see other floors" spy tool, and drops the older duplicate bot config. Boot test: 36 in-game tests pass.

### 2026-11-08 (overnight) — Tasks 2.9, 2.10: fishing and the Underkeep
- **Fishing:** use a fishing rod on water; when "Something is biting!" appears you have 3 seconds to use the rod again (unattended fishing catches nothing). Worms are the bait. Floor 1 has 7 fish (one only bites at night, one legendary with a server-wide announcement), plus treasure and junk. Your fishing log keeps counts and best weights; "Angler" titles. The weekly Derby comes with world events.
- **The Underkeep, Wing 1:** a cave under Hearthgate reached through the drain-grate secret: a water channel, a column hall, Mire Toads and Black Crawlers (tuned to Floor 2), a daily strongbox (gold + a chance at a gem), and a sealed door to Wing 2. Boot test: 38 in-game tests pass.

### 2026-11-08 (overnight) — Task 2.11: story quests, quest log, Floor 1 perk
- Three Floor 1 story quests (old pack names, simpler steps): **Bread for the Road** and **Millstone** from Miller Agna in Millcross, **The Lost Patrol** from Captain Dorrow at Hearthgate's north gate. Kill counters, "report" to collect gold (and the title Millhand). Each shows its next step in the client's Quest Log.
- Finish all three and Registrar Maelis offers the Floor 1 perk: **Thick Skin** (+5% max health) or **Light Step** (+10 speed). Earned only.
- Cleanup: removed four leftover Canary sample scripts (an example quest chest, a sample world board, an imbuement shrine) that referenced the old sample map. Boot test: 40 in-game tests pass.

### 2026-11-08 (overnight) — Tasks 2.14 (part), 2.15–2.17: Hardcore cap, autoloot, tasks, catch-up
- **Hardcore:** blessings can now only remove half of the experience a death costs (Tibia's own formula). Hardcore skill loss and item drops still open (2.14b).
- **Autoloot** switched on (loot goes straight to your loot containers, rarest first), and drops with a 2% chance or less are announced as "Rare drop!" to you and your party.
- **Taskmaster Ren** (Hearthgate): 7 daily hunting tasks (wolves, boars, bandits, shardlings, sentinels, rams, mire toads) paying gold and task points; one task at a time.
- **Catch-up for new players:** Normal characters under level 50 lose no experience when they die, and everyone under 50 trains skills twice as fast. Boot test: 42 in-game tests pass.

### 2026-11-08 (overnight) — Phase 3 started: houses that do things
- **Buying:** `!buyhouse` while facing a free house's doorway (1,000 gold per tile, level 20, one house each, weekly rent). When a floor is first cleared, its credited players get the new district for an hour (half the houses at most), then everyone.
- **House Portal:** `!portal set` where you want to go (only 3 times ever, never into boss rooms, Deadzones, secrets or near a floor boss), then `!portal` from inside your house.
- **Summoning Circle:** every credited boss kill gives a Boss Sigil; `!summon <boss>` in a house of 30+ tiles spawns a private copy (normal loot, never counts as a first clear).
- **Fortune Hall:** `!fortune license` (250,000 gold) turns your house into a gambling hall; visitors bet with `!dice <amount> high|low` against the owner's bank. Gold only (bank to bank, so shop items can't be bet), 100 to 1,000,000 per roll, the hall keeps 5% which is destroyed, every bet logged.
- **Open House:** `!openhouse` opens your house to everyone for 2 hours with an announcement. House management spells now use our own words ("house guests", "house doors", "house subowners", "house kick"). Boot test: 44 in-game tests pass.

### 2026-11-08 (overnight) — Task 3.6: guild tools and chat channels
- Guild bank at Banker Tolliver; Guildwarden Sela keeps a recruiting board ("recruit on" for leaders, "recruiting" to see who's hiring) and lists players looking for a guild (`!lfg` to flag yourself). New chat channels: World (English), Mundo (Portuguese/Spanish), Trade, Help, Looking for Group; the Canary channel with a Tibia town name is gone.
- Caught and fixed: a generator was deleting hand-written NPC files that share its file-name prefix; it now only rewrites its own files, and the town test checks all 12 Hearthgate NPCs. Boot test: 44 in-game tests pass.

### 2026-11-08 (overnight) — Phase 4: Floors 2–5 (placeholder versions)
- One generator now builds every floor from a single spec (`maps/floors.py`): **Highrest Highlands, Rootwell Fogwood, Lakehold, Ringhold** each have a town (temple, depot, priest, banker, quartermaster, merchant, an outfitter who buys that floor's gear, two quest givers, 6 houses), roads, 6 camps, a fishing lake, an apex spawn with a cave, the Pass with a field boss, a 3-level maze and the floor boss room. Stairs link every boss room to the next floor; each town has a portal back down. Previews: `docs/previews/floor2_z7.png` to `floor5_z7.png`.
- 90 new monsters for floors 2–10 from the roster (old pack names for 2–5, new for 6–10), with placeholder looks and floor gear in their loot.
- Bosses for floors 2–10 use a pattern library: stomp, root and spores, lance lines, rotating stances, charge lines, the "don't move" slam, the visor silence with Jay's aggro-bounce, the split, and Azhrakkar's three-phase ruin dance. First kills open the labyrinth/next floor, announce the clear, award titles, sigils and the house head start.
- Content for floors 2–10 generated: 27 story quests (in the quest log), 18 perk choices (any floor at the Registrar), 108 secrets (old pack names for 2–5), 63 fish. DESIGN.md table updated to the old pack's floor 3–5 bosses (my call). Boot test: 46 in-game tests pass, 570 monsters and 41 NPCs in the world.

### 2026-11-08 (overnight) — Phase 5: Floors 6–10 (placeholder versions)
- The same generator now builds **Emberreach, Glasswater Marsh, Frostspire, The Hollow Bazaar and The Cobalt Labyrinth**, so all 10 launch floors exist end to end: towns, camps, apex spawns, passes, labyrinths, boss rooms, stairs, 12 secrets and 7 fish each. Azhrakkar, the Cerulean Ruin waits at the top of Floor 10 with his three-phase fight (sweeps, burning blade + wardens, ruin dance with aggro bounce). Boot test: 46 in-game tests pass, 1,115 monsters and 76 NPCs.
- Still open in phase 5: the Twin Fang trial on Floor 8, world events, weekend bonuses, arena events, Spire Siege, offline training and livestream.

### 2026-11-08 (overnight) — Tasks 4.6, 4.6b: the rest of the sword skills and spells
- 24 more sword skills (now 6 per weapon family; the new ones unlock at levels 60, 100 and 150), e.g. Blade Tempest, Worldsplitter, Titan's Fall, Heartseeker, Ballista Shot, Skyfall Lance, Cataclysm Rite, Lifebloom Rite.
- 14 more spells: Bulwark Aura, Recovery, Iron Will, Eagle Eye, Sanctified Ground, Arcane Empower, plus the Lost Arts (Last Bastion, Unbroken Line, Hawk's Path, Volley of Dawn, Meteor Rain, Mirror Image, Wellspring, Winter's Breath), which only work after finishing every story quest on Floor 5 (first) and Floor 8 (second). Every vocation now has 19–22 spells. DESIGN.md says 2 Lost Arts per vocation (the table always listed 2). Boot test: 47 in-game tests pass.

### 2026-11-08 (overnight) — Tasks 5.7, 5.7b, 5.7e: world events, weekend bonuses, Derby, offline training, livestream
- **World events** every 3 hours on an open floor, announced 10 minutes ahead: Frenzy (extra apex monsters, +25% loot), Incursion (elite packs in the camps), Fishing Frenzy (rare fish ×3), Wandering Champion (a 6×-health elite roams). GM test command: `/event frenzy 1`.
- **Weekend bonus** every Saturday and Sunday, rotating weekly: double XP, double loot, double skill training, double fishing luck (announced at login).
- **Weekly Fishing Derby** Saturdays 20:00–21:00 server time: biggest single catch wins 50,000 gold and the "Derby Champion" title, with live leader announcements.
- **Offline training statues** (sword, axe, club, distance, magic) in every town temple; **livestream** ("!livestream on") stays on, with no XP bonus for streaming. Boot test: 50 in-game tests pass.

### 2026-11-08 (overnight) — Task 5.3: the Twin Fang
- Hidden stone circle in Floor 8's apex cave. A Vanguard with sword skill 80+ and 1,000 finished sword-skill combos (counted automatically) who steps on it faces the Twin Fang Warden; defeating it grants the Twin Fang, the title, and a server-wide announcement. Only 3 per season; after the third the trial seals.
- Effect: with a sword and an empty shield hand, every melee hit adds a 50% off-hand strike, and three exclusive skills unlock (Twin Fang Rush, Crossed Fangs, Fang Storm). The engine can't hold two weapons, so this is how the "second blade" works (DESIGN.md 5.6 updated, my call). The client's skill bar grew to 9 slots and only shows skills you can use. Boot test: 51 in-game tests pass.

### 2026-11-08 (overnight) — Tasks 4.5, 5.6: the Underkeep grows
- Wings 2–6 now exist under Hearthgate (levels 8–10), each behind a portal that stays a boulder until the tower reaches its floor: Wing 2 at Floor 2 (Vault Rats, Chain Ghouls, the Drain Matron), Wing 3 at Floor 4 (Trap Mimics, Iron Shades), Wing 4 at Floor 6 (Keep Wardens), Wing 5 at Floor 8 (the Vault Warden), Wing 6 at Floor 10 (Deep Sentinels, Vault Wraiths, The Underkeeper). Opening is announced server-wide. Boot test: 52 in-game tests pass.

### 2026-11-08 (overnight) — Task 8.1: season reset tool
- New owner command **/season** shows the season number; **/season end <number>** (everyone else logged out) archives every character to the Hall of Seasons (level, vocation, mode, titles, secrets found), copies titles to the account (Death Game characters also earn "Deathbound (Season N)"), then wipes characters, houses, guilds, the market and world progress. Accounts are kept. Restart the server afterwards.
- On login, every character gets the account's legacy titles, so a new season starts with them. Boot test: 54 in-game tests pass.

### 2026-11-08 (overnight) — Task 3.1b: houses back on the market
- When a house loses its owner (unpaid rent, deleted character), the server announces it: "Back on the market: <house> (<town>). Say !buyhouse at the door." Checked right after start-up and every 5 minutes; many at once are summarised in one line. Boot test: 55 in-game tests pass.

### 2026-11-08 (overnight) — Task 2.14b: the rest of the Hardcore death penalty
- **Skills:** a Hardcore death now costs 1.5× the normal skill and magic loss. The engine can't take skill progress away from a script, so the extra half becomes a "skill debt": your next training of that skill pays it off first (you get a message when it's cleared).
- **Items:** each equipped item gets a second 10% chance to fall into the corpse, which matches "doubled, blessings only remove half". An amulet of loss shatters on a Hardcore death and protects nothing. Not in arenas; red/black skulls already drop everything. DESIGN.md 5.5 explains it. Boot test: 56 in-game tests pass.

### 2026-11-08 (overnight) — Task 6.2: the Memorial and leaderboards
- **!memorial** lists every Death Game climber who fell this season (level, vocation, what killed them, date). **!top** shows the 20 highest climbers, marking Hardcore, Death Game and fallen characters; **!top normal / hardcore / deathgame** shows each mode's own board. The Monument sign in Hearthgate tells players about both. Boot test: 57 in-game tests pass.

### 2026-11-08 (overnight) — Task 6.5c: the Season Path
- A free reward track (say **!path**). Daily goals (300 monsters, 25 sword-skill combos, 5 fish: +10 each) and weekly goals (3,000 monsters, 3 bosses, 2 hunting tasks, 1 secret: +40 each). Every 100 points is a tier: 30 tiers of house furniture kits, tapestries, trophies and 6 titles. Cosmetic only, resets each season, and kills while the built-in cavebot is on don't count. About 8 weeks of steady play fills it (my call on the numbers). Boot test: 58 in-game tests pass.

### 2026-11-08 (overnight) — Task 5.7c: Arena events on equal footing
- A walled Arena under Floor 1 (reached only by event teleport). Sign-ups open daily at 19:00 and 22:00 server time (**!arena join**, level 20+, 4–20 fighters), rotating **Last Man Standing** (one life, last one wins), **Team Rush** (first team to 20 kills) and **Capture the Banner** (hold the centre square alone: a point every 5 seconds, first to 60). 10-minute limit.
- Equal footing (my call, engine limit): inside, everyone has 1,500 health and 1,000 mana, and every hit, spell and heal between fighters is a fixed amount, so level and gear don't matter. Nobody dies, nothing is lost, Death Game characters are safe. Winners get the "Arena Victor" title. GM test commands: `/arena open lms|rush|banner`, `/arena start`, `/arena stop`. Boot test: 61 in-game tests pass.

### 2026-11-08 (overnight) — Task 5.7d: Spire Siege
- A walled keep under Floor 1 with four guild gates and a throne room. Every Sunday sign-ups open at 19:45 server time (**!siege join**, guild members level 20+); at 20:00 every guild with 2+ fighters is teleported in. A guild scores a point every 5 seconds while only its members stand in the throne room; after 30 minutes the top guild holds the keep for a week (+5% experience and loot for its members, "Keeper of the Spire" title for its leader). Ties keep the old holder.
- Level-scaled the same way as the Arena: same health and mana, fixed hits and heals; downed fighters go back to their gate, nobody dies or loses anything. GM test commands: `/siege open`, `/siege start`, `/siege stop`. Boot test: 63 in-game tests pass.

### 2026-11-08 (overnight) — Task 8.2: season remix
- From season 2 on, each season automatically remixes the tower so veterans can't coast on old knowledge: field bosses and floor bosses swap mechanics among themselves (Azhrakkar keeps his ruin dance), and on every floor the big/medium/small rewards move between that floor's secrets (locations and hints stay; special secrets like the Underkeep keep their reward). Season 1 is exactly as designed. **/season remix** shows you what the next season will change.
- A new Underkeep wing per season is map work, added as MAP_REQUESTS.md M5. Boot test: 64 in-game tests pass.

### 2026-11-08 (overnight) — Task 3.5: house fixtures
- **Housewright Orla** (next to the Monument) sells furniture kits, tapestries and an **exercise dummy kit** (250,000 gold) for your own training room; kits are built by using them on your house floor. The Season Path's kit rewards build the same way (two rewards swapped for kits that actually build).
- **!trophies** in any house shows the owner's Trophy Hall (every boss beaten, first date, kill count). **!mannequin save/wear 1-3** stores outfits at home. **!pond stock** fills your house pond with every fish kind you've caught (visitors see it with **!pond**), and **!pond bait** gives worms once a day. **!warroom** in a guildmate's house shows your guild's wars.
- Not built: the workshop bench and garden need crafting/cooking, which the game doesn't have yet (new task 3.5b). Also fixed: the Monument sign text from the leaderboard task hadn't made it into the map file; it has now. Boot test: 65 in-game tests pass.

### 2026-11-10 (unattended) — Setup fixes, then Task 6.1: the Journal window
- Fixed two things that stopped the boot test on a fresh copy of the repo: the pinned-versions file `server/PINS.env` was being hidden from git, and the test helpers sometimes loaded after the tests that use them. The boot test now runs on Jay's PC through WSL (Ubuntu + MariaDB installed there; no compiler needed): `wsl -d Ubuntu -u root -- bash -c 'cd /root/sb && git pull && bash tools/test_boot.sh'`.
- **Journal** (press J, or !journal): one window with tabs for Secrets (names hidden until found, hints shown), Fishing log, Quests, Hunting task, Top climbers and the Memorial. The server answers each tab with plain text lines. Boot test: 67 in-game tests pass. Rough: the window itself is untested until it runs in the real client (no client available overnight).

### 2026-11-10 (unattended) — Task 6.3 (part): Portuguese and Spanish
- New command **!language en / pt / es** (remembered per character). Every server message is looked up in the player's language before it is sent; anything without a translation is simply sent in English, so nothing can break. 43 sentences and 25 patterns (fishing, arena, siege, house, PvP, Hardcore, Journal...) are translated, plus the Journal window and its tab labels in the client. Translations come from one list in `tools/gen_i18n.py` so Portuguese and Spanish can't drift apart; a test checks that.
- Not done (new task 6.3b): NPC dialogue, quest text, secret hints, item/monster names. Boot test: 70 in-game tests pass.

### 2026-11-10 (unattended) — Task 7.1 / 7.2b (part): the public website
- `python3 tools/gen_site.py` builds eight plain pages into `website/public/` (home, how to play, the tower with every floor's monsters, bosses and fish, vocations, difficulty, PvP rules, events, rules). They are generated from DESIGN rules and our data files so they can't drift; no scripts, no tracking, light and dark mode. Secrets are only counted, never named. The boot test now checks the site builds with no broken links.
- Still open: account creation, character pages and the Hall of Fame (need MyAAC and the database), boss cooldowns and event countdowns. The website is not hosted anywhere.

### 2026-11-10 (unattended) — Task 7.2: the donation shop (closed)
- **!shop** lists and sells cosmetics and house decorations for "Spire Coins" (account-wide). It is switched off with a "opens at launch" message until the launch flag is turned on. Outfits and mounts follow the account to every character. The owner can hand out test coins with /shopgrant.
- A test runs on every boot: every item must be a cosmetic kind, a real takeable item with zero attack, defense and armor, not a weapon or shield, and not gold. Prices and the 2 outfit / 1 mount looks are placeholders (Jay picks prices in 7.3; looks need art). Boot test: 71 in-game tests pass.

### 2026-11-10 (unattended) — Task 10.2 (part): backups on Jay's PC
- `windows/Backup-Spirebound.bat` saves the whole database as a zip in a `backups` folder (newest 14 kept); `Start-Spirebound.bat` now does it automatically before every start; `Restore-Spirebound.bat` puts back the newest copy (and saves the current state first as a safety net). Worth running before ending a season.
- Rough: the scripts passed a syntax check but have not run against a real Windows install (no MariaDB on the build machine). First real run is the test; if the backup fails the game still starts.

### 2026-11-10 (unattended) — stopping point
- Done tonight: setup fixes, 6.1 Journal, 6.3 (part) languages, 7.1/7.2b (part) static website, 7.2 closed shop, 10.2 (part) backups. WEEKLY_REPORT.md has a new top section with a 10-minute check list.
- **Pick up next:** (1) 6.3b translate NPC dialogue/quest text/hints (extend `tools/gen_i18n.py`; the translation hook in `lib/spirebound/i18n.lua` already covers `sendTextMessage` and text dialogs, NPC `say` is not hooked yet); (2) 6.4 custom sprite pipeline (see `tools/appearances.py`); (3) 6.5b Android build in CI; (4) 9.2 bot load test (needs a protocol 15.11 test client). Everything else left in ROADMAP.md needs Jay (playtests, host, prices, art) or a crafting design pass (3.5b).
- Test command on Jay's PC: `wsl -d Ubuntu -u root -- bash -c 'cd /root/sb && git pull && bash tools/test_boot.sh'` (a clone lives in WSL at /root/sb; MariaDB is installed there and may need `service mariadb start`).

### 2026-11-11 (unattended) — Playable Windows client (Part 1)
- **The game now runs on Jay's PC and was tested end to end.** Server + database run inside WSL (Ubuntu); the OTClient 4.2 Windows client is built by `windows/Install-Client.ps1` (pins from `server/PINS.env`, assets from the pinned opentibiabr-linked release). Windows reaches the WSL server on ports 8080 (login), 7172 (game) through WSL's localhost forwarding.
- **Why the old plan could not log in:** OTClient 4.2 uses an HTTP login for clients newer than 12.81 and Canary has no login web service of its own. New `tools/login_server.py` plays that role (checks the account in the database, returns the character list). Without it the client's first packet was rejected silently.
- **Desktop shortcuts** "Play Spirebound" (backup → start WSL server → wait until ports answer → open client) and "Stop Spirebound". `tools/run_server_wsl.sh` does the server side; backup/restore now use WSL's MariaDB (`tools/db_wsl.sh`) and were tested on a real install. New test characters (one per vocation + a Hardcore one, level 30) in `server/sql/dev_accounts.sql`, kits via `scripts/spirebound/dev_seed.lua`.
- **Bugs fixed on the way:** the cursor refresh in the client module crashed the Windows client (heap corruption), so it is off (cursors still change on skull updates); Portuguese/Spanish accents showed as garbage because the protocol carries Latin-1 (`SpireI18n.toLatin1`); Journal tabs overflowed the window; WSL's clock drifted (copied from Windows at start); `rsync --delete` kept wiping the server download cache.
- Proof: `screenshots/` (character in the temple, Journal window, Spanish message). Boot test: 71 in-game tests pass. `tools/winui/*.ps1` drive and screenshot the client for future testing. Read MORNING.md for the checklist.

### 2026-11-11 (unattended) — Part 2 and 3 summary
- 6.3b partly done (NPC speech hooked into translations; Registrar translated, checked live). 6.4, 6.5b, 9.2 not started: reasons in DECISIONS.md. Added `DECISIONS.md` (shop prices, crafting draft, hosting comparison, art priority).
- **Pick up next:** 6.3b other NPCs (`tools/i18n_npc.py`); put cursor art at 11x11; 6.4 sprite pipeline; a protocol-15.11 bot client for 9.2 (start from `tools/login_server.py`). Test commands: `tools/winui/enter.ps1`, `chat.ps1`, `journal.ps1` drive the real client.

### 2026-11-11 — Review (REVIEW.md) and the first blocker fixes from it
- **REVIEW.md** added: a full review of design, balance, bugs, maps, economy, security and roadmap, with a top-10 fix list and questions for Jay.
- **Fixed (REVIEW 3.1, 3.2, 3.3, 7.1):** the stair to the next floor now sits behind a wall, so nobody can walk around the boulder, and a new floor guard sends anyone found on a sealed floor back to Hearthgate; Skystep can no longer pass through floors and ceilings (it needs a real gap, and never lands in a boss room); red and black skulls now last 7 and 14 days (they lasted about 57 years); the login service no longer accepts database tricks in the name box, refuses repeated wrong passwords from one address (8 in 5 minutes), and keeps the database password off the command line. Map and previews regenerated.
- Boot test: online, 0 errors, 76 in-game checks pass (4 new). The login service was also tried live with good, wrong and malicious logins. Not yet tried with a real player: walking into the new wall, casting Skystep, and the floor guard teleport. Still open from the review's blocker list: the gamemaster test account is re-created at every start (7.3), the Death Game holes (3.4), and everything else in REVIEW.md section A.

### 2026-11-11 — Roadmap updated from REVIEW.md
- New **Phase R — Make it real** at the top of ROADMAP.md: 22 tasks from the review, in priority order (R1–R3 already fixed). No new features until it's done. Tasks the review found ticked too early (1.8, 2.12, 3.3, 3.4) now point to their R task.
- Added Q13–Q25 to QUESTIONS.md (the review's questions for Jay, each with my recommendation, assumed until answered). New tasks 7.4, 7.5, 8.3, 8.4, 10.4, 10.5; map rules added to MAP_REQUESTS.md; a stricter "when to tick a task" rule added to CLAUDE.md.

### 2026-11-11 — Jay's first playtest notes applied (PLAYTEST.md)
- Mage wand and rod now work from level 1 (the build patches the item file); base walking speed 110 → 170 for all vocations; new starter letter with lore and first steps (given by the Registrar, `!guide` re-reads it); `!spells` lists a vocation's spells and when each unlocks (spells are never sold); Hearthgate compacted (depot beside temple, shops at the temple door, monument closer). Boot test: 78 tests pass.
- **Not yet:** a real tutorial and quests (R11, R12), more compact real maps, and the level-8 gap before a first spell (consider a level-1 spell for mages).
