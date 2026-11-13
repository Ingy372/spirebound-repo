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

### 2026-11-11 — Floor 1 redesigned: map, NPCs, quests, bestiary, tutorial start (Jay's instructions)
- **Map:** compact walled Hearthgate (shops at the north wall, plaza, temple, depot and workshop beside it, two house streets), 52 houses on the floor (14 inside, 20 wallside cabins and 10 fisher huts outside the walls, 8 in Millcross), 12 hunting grounds as a ladder (plan in `maps/floor1_plan.py`), about 1,000 monsters, the Arrival Yard. Three new monsters (Meadow Wasp, Burrow Mole, Reed Snapper); wolves now give 50 experience.
- **NPCs and quests:** promotion at level 20 for 20,000 gold (Ascendant Veyra), Hunters' Hall (Hunter Brannoch, Taskmaster Ren, Bounty Warden Cass), Innkeeper Bess, Fisher Corwin, Guide Pell. Six story quests (they unlock the perk) and four side quests (they don't).
- **Progression logic:** `BESTIARY.md` and `!hunt` come from one plan; shop NPCs and quest givers answer "hunt"; level-ups tell you when to move on; new characters start in the Arrival Yard. Boot test: 82 in-game tests pass, 0 errors. Not yet seen in the real client.

- Tutorial additions the same day: Guide Pell's quest *First Blood* (3 rats), level hints at 2/5/8/10/20, the new quest in the quest log. Boot test: 82 in-game tests, 0 errors.

### 2026-11-11 — Claude is the mapper: Floor 1 look-and-feel pass (Jay: "you are going to take over as the mapper/architect")
- Built two tools so the map can be designed by eye: `tools/spriteview.py` (decodes the client's sprite sheets and appearances file; contact sheets of item ids) and `tools/maprender.py` (draws the real map with the real sprites). First pieces of roadmap 6.4. Outputs stay in `.local/scratch/` (CipSoft art, never committed).
- Rebuilt how the map looks: six wall families with windows, doors and closed corners; furnished shops and halls; a stone city wall with pillars; a marble plaza with statues, lamps, trees and stalls; a winding river with bridges; winding roads; forests, lakes, ruins and standing stones; a distinct look for each of the twelve hunting grounds. Fixed a bug where the old east-west road ran through the temple.
- Boot test: 82 in-game tests, 0 errors, 0 map warnings. `CLAUDE.md` map rule updated: Claude builds the real maps; Cowork polishes later. Not yet seen in the real client.

### 2026-11-11 — Fixed missing walls on the cabins; Floor 1 plan picture (from Jay's screenshot)
- Cause of the holes: the little lane roads beside the Wallside Cabins were drawn after the cabins and erased their north walls and doors. Roads now never erase walls or doors, and every house now has a visible open door in its doorway.
- Added `docs/FLOOR1_PLAN.png` (made by `tools/plan_image.py`): the labelled Floor 1 plan, hunting grounds by level range. Boot test: 82 in-game tests, 0 errors.

### 2026-11-11 — Corners and walls fixed everywhere, checked in the real client (Jay: "focus on the corners of everything")
- Learned the real rules by counting how Canary's hand-made map builds walls: which piece goes on each corner (top-left post, bottom-right L piece), which ground goes under each wall, and each wall family's own open door. The wall builder now follows them, and a new "auto-wall" picks every piece from its neighbours (used by the labyrinth).
- Fixed on the way: brick corner used the wrong piece; floor triangles past corners; city wall now pale stone with gates as wide as the avenues; fallen-looking gate pillars removed; standing stones that sat inside the city; Hunters' Hall pressed against the city wall; a ruin dropped on the Arrival Yard; Millcross back-row cottages had no path; bushes and trees on streets, in doorways, in the Pass and in the labyrinth corridors.
- Checked in the client by logging in with Jay's GM character and teleporting around. Boot test: 82 in-game tests, 0 errors.

### 2026-11-11 — No more half-made objects; map rules made permanent (Jay: "make sure this rule applies to all map creation in the future")
- Big objects are several pieces on neighbouring tiles. `tools/learn_object_parts.py` learned 412 such pieces from Canary's hand-made map (`tools/object_parts.json`); the map builder now completes every object or removes it if it cannot fit. Fixed: the plaza fountain and benches, the Millcross fountain, two-piece furniture, and about 600 quarter-boulders around the world (now whole 2x2 rocks, fewer of them).
- Ruins now break cleanly with rubble in the gaps; grass squares no longer show under rocks and stones; a ring of standing stones moved out of the Reedmarsh pools. Map rules written into CLAUDE.md for every future map. Boot test: 82 in-game tests, 0 errors.

### 2026-11-11 — Roofs, upstairs rooms, stairs and ladders (Jay: "add the stairs and roofs")
- Learned from Canary's hand-made map how roofs sit (one level up, lined up with the wall tops, edge pieces around them), how stairs pair with the stair tile above, and how ladders pair with trapdoors. The map builder now roofs every surface building automatically and has builders for upstairs rooms, stairs and ladders; the map renderer can draw upper levels.
- Added upstairs to the Guild Hall, Millcross Inn, Hunters' Hall (ladder) and four corner houses on Lantern Row (part of the house, higher rent). Town safe zone now covers upstairs. New in-game tests: a character walks up and down real stairs, the ladder and trapdoor work, upstairs rooms belong to their house, the temple has a roof. Walked the Guild Hall stairs and the Hunters' Hall ladder in the client. Boot test: 86 in-game tests, 0 errors.

### 2026-11-11 — Soft ground edges and shorelines (Jay: "do edges next")
- `tools/learn_ground_edges.py` learned the two edge sets real maps use (grass edges over dirt and sand; shoreline pieces on land next to water, 12 pieces each) into `tools/ground_edges.json`. The map builder now smooths coastlines and edges every place where grass meets roads, dirt, mud, gravel, sand or paving, and where land meets water, on every floor.
- Checked by render and in the client (river shore and road edges). Boot test: 86 in-game tests, 0 errors.

### 2026-11-11 — Floor 1 finished: the Pass, labyrinth, boss hall, watchtower, cave, Underkeep, Arena and Siege keep dressed (Jay: "finish Floor 1")
- New `maps/dungeon.py`: natural caves (cave walls learned from Canary's map), wall lamps/torches/chains on the right walls, and decoration that can never block spawns, teleports, doors or corridors. Every special area on Floor 1 now has its own look (see FLOOR1.md).
- New in-game test: every landing, start and entrance stays walkable. Checked the boss hall and the cave in the client. Boot test: 87 in-game tests, 0 errors.

### 2026-11-11 — Hearthgate expanded and re-planned; second top-server research pass (Jay's direction list, steps 1-2)
- Hearthgate grew from 80x72 to 112x96 with every block used. The layout:
  - ten shops along the north wall: five new (Fletcher, Alchemist, Runewright, Tailor, Post Office) plus the five old;
  - the Market Square, with free stalls for player trading;
  - the temple between the depot and a new Trade Hall (west) and the workshop and Hunters' Hall (east);
  - a high road gate to gate;
  - the inn (rooms upstairs), a Training Yard (the offline statues moved here), a plot for Spire Manor, and a Carriage Station (Coachman Ferro to Millcross, Coachwoman Dara back);
  - 22 houses (was 14).
  Camps, cabins, the Arrival Yard and the standing stones moved to fit around the bigger walls.
- `docs/RESEARCH_TOP_SERVERS_2026-11b.md`: who is biggest now (RubinOT, Best-Baiak, Streamy, Miracle, Ezodus) and the patterns in minigames, travel, PvP, gear, houses and premium, with what we have and what we are missing. Boot test: 87 in-game tests, 0 errors.

### 2026-11-11 — Spire Manor, the shop-only showcase house (Jay's direction list, step 3)
- Four levels at the south end of Hearthgate's avenue:
  - **The Grand Hall:** an indoor fountain, display counters along both walls, statues and trophies.
  - **The Trophy Gallery:** two long display rows, bookcases, weapon and armour racks.
  - **The private quarters:** a bedroom and a study.
  - **A rooftop garden:** fountain, benches, trees, a telescope and a balustrade.
  Stairs join every level. It is house 99 and 1 of 1 on the server.
- Only the shop can hand it out: a new "house" kind in the catalog, and !buyhouse refuses it. Price and resale are in Q26 (assumed: placeholder 5,000 coins, not resellable).
- Fixed: big objects inside houses (beds, fountains) were being removed, and an upstairs floor could cover the stair hole from below. New test covers the manor's four levels, its stairs and the shop-only rule. Boot test: 88 in-game tests, 0 errors.

### 2026-11-12 — Newcomer playthrough, the holes it found, and the economy (Jay's direction list, steps 4-5)
- Played a fresh character in your client from the Arrival Yard. Found and fixed:
  - Guide Pell's quest offer never showed: the client crashes drawing keywords inside brackets.
  - The yard showed Open PvP: a variable got overwritten.
  - The first fight was barehanded; new characters now get a practice club.
  - Three tutorial rats killed the character at level 1; there are now weak Pen Rats, and they can't leave the pen.
  - Canary's "joker tokens" and empty "boosted boss" login lines are gone.
  - Pell's attack advice and his plural keywords were wrong.
  - There was no healing before town; Pell now heals below level 10.
- Economy: Floor 1 monsters drop trade materials, and seven crafting recipes turn them into things no shop sells. `tools/gen_economy.py` writes ECONOMY.md with burn rates for each of the 12 hunting grounds and 4 vocations, and fails the build if a vocation loses money. It caught moles too poor for arrow-using rangers, which are now fixed. Boot test: 91 in-game tests, 0 errors.

### 2026-11-12 — Boosted creature of the day (roadmap J7)
- Each day one Floor 1 hunting-ground monster gives +50% experience and an extra loot roll; the login message names it. Canary's own version picked nothing because our monsters aren't in the official bestiary (that is why the login line used to be blank). Boot test: 92 in-game tests, 0 errors.

### 2026-11-12 — Temple teleport scroll (roadmap J8)
- Runewright Mael sells a temple teleport scroll (300 gold, used up) that takes you home when you're not in a fight. It never works from a boss room, Deadzone, the Arena or the Siege. A small gold sink, and common on popular servers. Boot test: 93 in-game tests, 0 errors.

### 2026-11-12 — The Hearth: Hearthgate's home hall (Jay: a "temple" or "home" area ... 2-3 levels ... a junk buyer ... a banker)
- The temple, depot, Trade Hall and workshop are replaced by one three-level hall in the middle of town, as the big servers do:
  - **Level 1:** the temple nave, where you spawn and respawn; the depot (18 lockers, mailboxes); and the bank and exchange (Banker Tolliver, Trader Osric, Broker Nell).
  - **Level 2:** a trading gallery with 16 more lockers and trade tables.
  - **Level 3:** the Hall of Climbers.
  The workshop moved into the old depot building.
- Trader Osric buys every item monsters drop (53 kinds, near standard Tibia prices). The account vault keeps gold for every character on an account. Banker Ansel runs a branch on the north wall. Checked in the client; boot test: 94 in-game tests, 0 errors. Questions Q28 (the vault) and Q29 (Osric's prices).

### 2026-11-12 — Hearthgate v3 built from the plan (Jay: "review the plan and execute it")
- Rebuilt the whole town block from `HEARTHGATE_PLAN.md`:
  - **The Hearth:** a compact three-level hall at the crossing of the two main roads, with four open archways and a tower.
  - **The Ring and Hearth Square:** the Ring is a marble square around the hall; the Hearth Square, with its fountain, Monument and six stalls, is its south side.
  - **Shops and public buildings:** all moved to the new layout.
  - **Spire Manor:** moved to the East High Road, with a forecourt and public Spire Gardens.
  - **Houses and parks:** 30 houses in eight streets, plus Hearthgate Green, Old Well Yard and a pocket garden.
- Two small tool changes: roofs can now wrap round a tower, and `building()` accepts an explicit doorway and extra open archways. Walked the Hearth, the gate and the manor in the client. Boot test: 95 in-game tests, 0 errors.

### 2026-11-12: Hearth depots rebuilt as booths (Jay: "banks should be booths... just use what tibia uses for their dp's")
- Copied the real Tibia depot booth from Canary's hand-made map: each locker stands on a counter, and wooden railings two tiles deep split the row into one-person booths. Players can drop items on the counters to trade across them. New map tool `depot_booths()`, so every future depot uses the same pattern.
- The Hearth now has 26 lockers in booths on the ground floor (a wall row plus a back-to-back island in each wing) and 10 in booths in the gallery. The west stairs moved to the wing's south-west corner. Opened a locker from a booth in the real client; boot test 95 in-game tests, 0 errors.
- Booth fix from Jay's look: the back row's dividers were only one tile deep, so a player could be pushed out. Now every divider is two railings deep (back row turned to face the north row across a 3-tile walkway: 20 lockers downstairs, 10 upstairs). Added the red depot switch tile in front of every locker: step on it and it lights up and says what your depot and stash hold (checked in the client). A new in-game test checks every booth has the switch and two-deep dividers.

### 2026-11-12: Plan for Floor 1 outside the walls (plan only, nothing built)
- Jay: "look at player progression, the map design of everything outside the city, monster spawn areas are currently messy ... set up the map and instructions for a less expensive model to do all the work." Wrote `FLOOR1_WILDS_PLAN.md` with the picture `docs/FLOOR1_WILDS_PLAN.png` and the checker `tools/wilds_plan_check.py` (prints problems 0).
- Findings: Floor 1 is out-levelled in about 1 h 15 min at 25x; grounds are boxes of lawn with roads through three of them; one field holds enough boars for 22 players. Plan: slower early stages (Q30), each ground rebuilt as a walled place with four hunting loops, six caves for parties, Tibia-style small spawns with minutes-long respawn, and a crowd system that adds monsters when a ground is over-full (Q31). Tasks W0-W11 added to the roadmap.
- Jay answered Q30-Q32 (2026-11-12): yes to all three. Q30 in his words: "yes slow it down to what you recommend. it should last about 11-15 hours. this will give a great sense of FOMO on launch day and on season resets." The plan and roadmap now treat them as decided.

### 2026-11-13: How the engine brings monsters back (wilds plan W0)
Read the engine's spawn code for our pinned version (Canary 3.6.1, `spawn_monster.cpp`). The three answers:
1. **Standing on the spot does not stop a respawn for our monsters.** Our monsters are all marked "not blockable", so they come back on top of a player after a 4-second sparkle. (A "blockable" monster would wait while any player is within about one screen, and its timer would restart each time.) As the plan says, this changes nothing: the long return times already make walking the loop better than standing still.
2. **The real wait is about twice the number in the spawn file.** The engine only notices a death at its next check, and checks once per respawn time, so a group with "110 seconds" really returns after about 220 seconds (between 1x and 2x). From now on the plan's respawn times are the real waits, and the map builder writes half of them into the spawn file.
3. **The engine does not speed up with players online.** There is one fixed "spawn rate" setting (ours is 1) and a doubling for Canary's own boosted creature, nothing else. So the crowd system (W10) will not stack with anything.

### 2026-11-13: The new hunting-ground table (wilds plan W1)
- `maps/floor1_plan.py` now holds the plan's table for all twelve grounds: new place and size, gate side, loop size, what the walls, cores and trails are made of, the monster groups on each loop, the real respawn wait, and the six caves with their groups. The Old Watchtower's fixed groups are there too.
- The plan checker now reads that same table instead of its own copy, so the two can never drift apart (problems 0). The bestiary and economy pages were regenerated from it; the map itself is unchanged until W3.

### 2026-11-13: The hunting-ground builder (wilds plan W2)
- New map tool `maps/wilds.py` builds any hunting ground from its row in the plan: the 2-tile outer wall with a 3-wide gate, the hub with its sign, fire and bench, four loops (a 2-wide ring trail round a solid core, corners cut, a few bulges so it looks grown), the cross trails, the monster groups at fixed spots on each ring, the crowd spots and the named points. Each group can now mix monsters (for example a Grey Alpha with two wolves) with its own return time.
- Rock walls now use Tibia's real mountain ground with rock faces round it, learned from Canary's hand-made map. The walk test runs every time the map is built and stops the build if a gate can't be reached from the Hearthstone, a spot can't be reached from the gate, a loop isn't a closed ring, or the outer wall has a hole. `python maps/wilds.py` builds all twelve grounds on blank land: all pass.

### 2026-11-13: Boar Meadow rebuilt, the pattern for every ground (wilds plan W3)
- Boar Meadow is now a walled oak wood south-west of town (39 x 57): one gate on the north side reached by the new Cabin Lane from the west cabins, a dirt hub with a sign, a fire and a bench, and four ring-shaped trails round oak groves, each with six groups of three boars (72 in all, back after about 3 minutes). The south-east grove is hollow: Old Tusk's wallow, a mud clearing reached through a one-tile gap; Old Tusk and secret s2 moved into it. The old south road branch that ran into the meadow is gone.
- Rendered and checked; the walk test passes; new in-game tests check the gate, loop mouths, crowd spots, that the engine really spawned 72 monsters inside, and the wallow. Boot test: 98 in-game tests, 0 errors. Walking it in the client is now task W12 (the client could not be driven this session). Also fixed: the Watchtower entrance point could get a rubble pile on it.

### 2026-11-13: The four starter grounds rebuilt (wilds plan W4)
- The Ratwarren (bushes, thicket mounds), Toad Pond (a pond inside every loop), Sproutling Glade (fern groves) and Waspgrass Fields (hedges round flower beds) are now walled places with a gate, a hub and four loops, 48 monsters each, back after about 2 minutes. Each gate has a short trail from the nearest road. The eastern standing stones moved to (356, 262) to make room for Toad Pond.
- Fixed while looking at the renders: Toad Pond's ponds had dried up (the water was trimmed too far), and grass trails now carry more flowers so the loops can be seen. Walk test passes for all five rebuilt grounds; boot test 98 in-game tests, 0 errors.

### 2026-11-13: Burrow Hills, Wolf Copse, Reedmarsh and Thornsnap Hollow rebuilt (wilds plan W5)
- Burrow Hills: rock walls and rocky hills (real mountain ground). Wolf Copse: dark fir thickets, one Grey Alpha pack per loop. Reedmarsh: deep-swamp walls with reeds and dead trees, a pool inside every loop. Thornsnap Hollow: thorn walls, a dead tree in each thicket. 72 monsters each, about 3 to 3.5 minutes to return; elites 15 minutes.
- Roads: the old roads that ran through Burrow Hills, the Old Quarry, Wolf Copse and Thornsnap Hollow are gone; new gate trails from the Pass Road, and the new Copse Road from Millcross down past Wolf Copse to the Reedmarsh gate. Secrets moved onto trails by the smallest step: s9 from (44, 300) to (44, 297) in Wolf Copse, s11 from (160, 170) to (165, 166) in Thornsnap Hollow.
- Client check (W3-W4 grounds): walked Boar Meadow's hub and north-west loop (boars stand on the trail in threes, zone reads Open PvP), Old Tusk's wallow, and Toad Pond's hub (Guarded, sign in place). Walk test passes for 9 grounds; boot test 98 in-game tests, 0 errors.

### 2026-11-13: Shard Fields, the Bandit Road, the Old Quarry and the Watchtower's groups (wilds plan W6)
- Shard Fields: rock walls and gravel trails round boulder mounds. The Bandit Road: a wood with broken stone walls, a fenced camp of carts, crates and barrels with a fire in every loop, one Bandit Captain pack per loop. The Old Quarry: rock and rubble, gravel trails, mixed sentinel and archer groups. 72 monsters each.
- The East Road now ends at East Cross (338, 285); from there the Bandit Track runs north and the Shard Track south. The old roads that ran down x 345 through Shard Fields are gone; the road south of town now ends at the toppled shrine. Secret s7 moved one tile (352, 186) to (353, 186); s5 now sits on the far side of the Quarry's north-east loop at (297, 137).
- The Old Watchtower keeps its walls but now has fixed groups: six of 3 rams round the courtyard, four of 4 in the inner room, eight of 4 in the cave (66 in all). New in-game test counts them. Walk test passes for all 12 grounds; boot test 99 in-game tests, 0 errors.

### 2026-11-13: Roads, signposts and the forest between the grounds (wilds plan W7)
- New Watch Road from Millcross's north side to the Old Watchtower's gate (it had no road). Signposts at ten junctions name what lies each way with its level range (for example "West: Waspgrass Fields, levels 7-12. East: Burrow Hills, levels 11-16."). The old camp drawing code is gone: every ground now comes from the plan.
- One change from the plan: Cabin Lane leaves the west cabins at their east end (172, 304) instead of (152, 313), because there is no gap between the cabins there.
- The map build now also fails if a monster group stands on a road or within 8 tiles of a gate (plan Part 8.3); two Boar Meadow groups were too close and moved. Forests fill the land between grounds and stay off roads. Zones: starter grounds Guarded, the rest Open up to their walls, the Watchtower Contested. Boot test 99 in-game tests, 0 errors. Still to check by hand: a new character finding the first five grounds by the signs (playtest list).

### 2026-11-13: Six party caves under the harder grounds (wilds plan W8)
- The Molework (Burrow Hills), the Alpha's Den (Wolf Copse), the Rootcellar (Thornsnap Hollow) and Shard Grotto (Shard Fields) are natural caves; the Smugglers' Cellar (Bandit Road) and the Lower Works (Old Quarry) are built with stone walls. Each is about 36 x 26 under its ground: an entry chamber with no monsters, then a ring of eight chambers round it, one group of four in each (32 monsters, back after about 2.5 minutes; two Grey Alphas in the Den and two Bandit Captains in the Cellar).
- The way down is a stone-rimmed hole where the ground's cross trails meet, with a sign: "<cave>. For a party. Levels X and up. Bots are refused below." The Molework's mouth is dug out like a giant burrow. The build checks nothing else is dug nearby at that depth and that every chamber can be reached from the stairs.
- Walked down into the Molework and back up in your client. New in-game test checks all six caves' stairs both ways and their 32 monsters. Boot test 100 in-game tests, 0 errors. A party fight in a cave is on the W12 list. The cavebot refusal comes with W10.

### 2026-11-13: Slower early levels and a ladder that always climbs (wilds plan W9)
- Jay's answer to Q30: "yes slow it down to what you recommend. it should last about 11-15 hours. this will give a great sense of FOMO on launch day and on season resets." Experience stages are now 10x for levels 1-8, 4x for 9-20 and 3x for 21-50 (was 25x); DESIGN.md 5.5 updated.
- Monster experience retuned so every ground meets the plan's target within 10% and each experience ground beats the one before (for example boars 40 to 28, wolves 50 to 36, bandits 70 to 50). Road Bandits and the Quarry's sentinels and archers carry more coins (and a little platinum), so both money grounds now pay over 1.5 times the gold of Shard Fields.
- By the model: level 14 after 0.8 hours, 25 after 3.9, 35 after 9.4, 40 after 13.5 hours of hand hunting (real play about 40% slower, so roughly 13 to 19 hours). `tools/gen_economy.py` now prints this ladder in ECONOMY.md and fails if a target is missed or the ladder dips. The in-game stage test reads the three new stages. Boot test 100 in-game tests, 0 errors.

### 2026-11-13: The crowd system and the busy line in !hunt (wilds plan W10)
- Jay's idea, Q31 "yes": every 30 seconds each hunting ground counts the players inside (staff don't count, cavebot users do). Fewer than 5: Quiet. 5 to 7: Busy, half its extra groups come out. 8 or more: Packed, all of them. 12 or more on a starter ground: Rush, and extra groups come back three times as fast. A ground steps up at once and only steps down after 5 minutes below the line; then the extra monsters left alive stay, but don't come back. No extra group ever appears within 7 tiles of a player. A starter ground goes from 48 monsters to 96; a harder one from 72 to 108.
- `!hunt` now adds a line such as "Boar Meadow: busy (6 players, extra monsters are out)" for the grounds it recommends. Q32 "yes": a player with the cavebot on is sent back up the stairs from any of the six caves.
- Five new in-game tests drive the real crowd update (it really puts the monsters on the map): 4 players quiet, 5 busy with half the spots, 8 all spots, 12 a Rush only on a Guarded ground, nothing beside a player, and no refilling five minutes after everyone leaves. Boot test 105 in-game tests, 0 errors.

### 2026-11-13: Wilds rebuild finished: documents, pictures and the report (wilds plan W11)
- Regenerated BESTIARY.md, ECONOMY.md, the `!hunt` guide, `docs/FLOOR1_PLAN.png` and `docs/FLOOR1_WILDS_PLAN.png` (plan check: problems 0). FLOOR1.md now explains how every ground is built. Monster counts match the plan: 48 per starter ground, 72 per harder ground, 32 per cave, 66 in the Old Watchtower (in-game tests count them).
- WEEKLY_REPORT.md has a 50-minute playtest list for the new wilds. New question Q33 (does the look suit you?); Q30-Q32 moved to Answered.

### 2026-11-13: The front door is locked (roadmap R4)
- Logging in now hands the client a random one-day token instead of sending the password back; the database keeps only the token's fingerprint, and the game server accepts tokens only. The login service listens on this PC only until the friend tunnel exists.
- Starting the server no longer resets the GM test account. That is now a separate dev-only step (`windows\Make-Test-Accounts.bat`); a brand-new database still gets it once so the PC has a way in.
- New sign-up page at http://localhost:8080/signup (name, e-mail, password twice, at most three accounts an hour from one address).
- Checked: the login service's self-test proves the token is never the password and only its hash is stored; the boot test fails if a normal start touches the test accounts or the server takes passwords. Logged in through your client with a real token. Boot test 105 in-game tests, 0 errors.

### 2026-11-13: Death Game deaths are now fair (roadmap R5)
- A Death Game character is retired only by a real PvE death. Another player's damage saves you only if it was real (at least 15% of your health in the last minute), so a one-hit "tag" no longer makes you immortal. A player's killing blow never deletes you, and a friend can't save you by landing the last hit. A monster that hit another outside player in the last 30 seconds counts as dragged in: not PvE.
- Retiring now frees the house, hands guild leadership to the next member (or closes the guild), removes market offers, frees the character slot and saves at once. GMs can `/restore <name>` after a server crash or server lag; the policy is on the website rules. Stepping down costs the extra experience the harder path gave (Q14, my recommendation assumed). Deathbound needs level 50 alive on the Death Game.
- Six new in-game tests drive the same rule code the real death event calls, and run the retirement clean-up and restore on the real database and houses. Boot test 111 in-game tests, 0 errors.

### 2026-11-13: Hardcore death drop fixed (roadmap R6)
- The extra Hardcore item drop passed its values in the wrong order, so blessings were ignored and a skulled Hardcore death raised an error. Each value is now passed in its right place: no blessings gives the full 10% extra chance per item, each blessing removes a fifth, red and black skulls get no extra roll (they already drop everything).
- New in-game test runs the real death handler with real items and a real corpse: items really fall in with no blessings, none with five, no error on a red skull, nothing for Normal. Boot test 112 in-game tests, 0 errors.

### 2026-11-13: Fair PvP credit (roadmap R7)
- Kills now credit everyone who did real damage (at least 10% of the victim's health in the last minute), not only the last hit: each can get the unjust kill and the skull, each of their guilds counts toward Sanctuary, and a bounty is split among them by damage. The "partied together in the last 24 hours" bounty rule now really works: joining a party records partners.
- The outnumbered shield counts only outside attackers who did real damage. Healing a skulled player costs your own protection for 5 minutes. Murderers who die wake in the new Outlaw Camp (a palisade far west with a track to the Watch Road), not in town. DESIGN.md 6.4 has the numbers.
- Five new in-game tests use the same damage records the real fight events write. Boot test 117 in-game tests, 0 errors.

### 2026-11-13: Saving at the big moments (roadmap R8)
- The whole server now saves at once after a field boss's first kill, a floor clear, a Death Game retirement, a shop purchase and a secret sale, so a crash can't undo them. Moments a few seconds apart share one save.
- Found that Canary's own "save interval" only runs once a day at the global save time; the server now also saves quietly every 10 minutes. New in-game test goes through the real floor-state calls and counts the saves. Boot test 118 in-game tests, 0 errors.

### 2026-11-13: The boss system finished (roadmap R9)
- Credit: healing the fighters and soaking the boss's hits now count (soaking at half), and you need at least 2% of the fight's total to be credited, so a token hit earns nothing. Titles for players who were offline at the kill wait for their next login. The enrage timer now follows the most players present at any time, and a boss room holds 20 at most (late arrivals are sent back out).
- Q19 (assumed): marked hits that can kill (250 or more) wait 1.0 s, the rest 0.6 s. Q13 (assumed): each floor's boss hall unseals on its day of the season (Floor 1 on day 3, then every 6 days), once a season is started with `/calendar start`; until then nothing is sealed.
- Private repeat kills: after Floor 1 is cleared, a party leader with 1 to 5 players says `!private` at the top of the labyrinth to fight the Axe-Lord in a new private hall, once per character every 20 hours, with no world-first actions. Six new in-game tests; boot test 124 in-game tests, 0 errors. A real boss fight in the client is still part of R0.

### 2026-11-13: Real balance tables for all ten floors (roadmap R10)
- New `tools/balance.py` holds one target row per floor (hours to climb its levels, coins per hour) and models experience, gold, supplies and house prices for all ten floors. The monster generator now reads it: Floors 2-10 monsters get their experience and coin drops from those targets. Before, Floor 3 took 7 hours and Floors 7-10 took 100 to 275 hours each; now the climb rises gently from 14 to 45 hours per floor (about 260 hours in all by the model).
- The check fails the build on a bad number (a price loop, a gold flood or drought, supplies eating more than 60% of the coins, an overpaid task) and runs on GitHub; `--selftest` proves it fails on a bad price. Floor 1's tasks paid up to ten times their kills' coins: now about 250-450 gold, and every floor 2-10 has four tasks. Task points buy things at last (`!taskshop`: a temple scroll, strong potions, an hour of +20% experience, a title).
- The Fortune Hall's 5% is now really destroyed (before, the host kept it) and each hall takes at most 500,000 gold of bets an hour. The October tables moved to `legacy/october_tables/`; the website now reads the real data. Not done, now new tasks: repairs and floor travel fees (R10b), and house prices per floor (R10c). Boot test 126 in-game tests, 0 errors.

### 2026-11-13: The Arrival Yard tutorial (roadmap R11)
- The yard is wider and the stone path now runs through four fence gates. Each opens once the new character has done one thing: beaten a rat in the pen, looted it, said `!spells` (sword skills themselves need a vocation, which only the Registrar gives, so this gate teaches what is coming instead of asking for a cast), and drunk the health potion every new character now gets. A closed gate steps you back with a hint. The Registrar's hall is at the end; nobody without a vocation can leave the yard.
- The Journal (J) has a new "How do I..." page answering thirteen common questions (attack, loot, heal, where to hunt, sword skills, spells, gold, selling, tasks, getting home, secrets, PvP protection, floors). Hints at levels 2, 5, 8, 10 and 20 were already in place.
- Checked in your client as the fresh character Climber: walking into the first gate before beating a rat sends you back with "Beat a rat in the pen first...". Three new in-game tests. Boot test 129 in-game tests, 0 errors. (Note: your client needs the updated Journal module to show the new page.)

### 2026-11-13: Things to earn on Floors 1-2 (roadmap R12)
- **Gear ladder:** for each of the four paths, three pieces per floor on Floors 1 and 2, each with its own name and a small bonus (for example the Vanguard's Briarguard Sabre, Hearthward Mail and Stairlord's Cleaver): a rare drop from the harder monsters, a quest piece, and the boss piece, which the Axe-Lord or the Crowned Aurochs drops for its top fighter. One table in `tools/gen_gear.py`; the name checker reads every name.
- **Quest lines with a real reward:** "Iron for the Stair" (Hunter Brannoch, Floor 1) and "The Hornbreaker's Due" (Scout of Highrest, Floor 2), two steps each, ending in your path's quest piece.
- **Every perk works:** before, only the two Floor 1 perks did anything. Now all twenty do; four that promised things the engine can't do were reworded (Fog Sense is now a 5% dodge, Iron Will -8% physical damage, Marsh Walker +15 speed, Haggler +8% coins). A test checks each perk's numbers. The plan for unlocks past level 150 is in `docs/PLAN_PAST_150.md`. Boot test 133 in-game tests, 0 errors.

### 2026-11-13: Scope for the friends test (roadmap R13)
- Q22 (assumed yes): the server now runs in "friends test" scope. Floors 3-10 stay sealed even if Floor 2's boss falls, and the Arena, the Spire Siege, the shop and the Season Path are off. You can switch with `/scope test` or `/scope launch`.
- Floor 2's five camp monsters now each have one trick: the Horned Grazer charges, the Ridge Cat pounces, the Dust Strider kicks sand from range, the Hill Cutthroat has a war cry that hurts everyone near, the Blight Wasp spits blight. Floor 1's ladder already runs easy to hard (W9).
- Cut, now task R13b: Floor 2 still uses the shared placeholder map; it needs its own hand-built layout like Floor 1's. Two new in-game tests. Boot test 135 in-game tests, 0 errors.

### 2026-11-13: Moderation basics (roadmap R14)
- Players can `!report <name>, <what happened>`; online gamemasters see it at once and `/reports` lists them. GMs can `/mute <name>, <minutes>` and `/unmute`. Every GM action (mute, restore, calendar, scope) goes into a log you can read with `/gmlog`.
- Public chat (World, Mundo, Trade, Help, Looking for Group) blocks the worst words in English, Portuguese and Spanish, including digits swapped for letters. `!rules` shows the rules in game, new characters are pointed to them on first login, and the punishment ladder (warning, mutes, character ban, account ban, permanent) is written in `docs/RULES.md` and on the website rules page.
- Two new in-game tests. Boot test 137 in-game tests, 0 errors. Who moderates, in which languages, is still Q23.

### 2026-11-13: Bot rules enforced on the server (roadmap R15)
- Q16 (assumed): the server no longer only trusts the client's "cavebot on" report. Killing 5 or more monsters in 10 minutes without moving more than a tile now counts as botting (auto-target and auto-heal on one spot), with the usual 45% experience and half loot, until you walk again. A party member within 7 tiles of a botting member gets the same 45% experience. While botting, only every second kill counts for a hunting task. Hunts of 6 hours without a 15-minute break, and 10 minutes on one spot, are written to the server log for staff (no automatic bans).
- The client installer now removes vBot's attack helper (automatic spell and skill rotation), its combo helper, push helper and script editor; I made the same change to your installed client. New in-game test. Boot test 138 in-game tests, 0 errors.

### 2026-11-13: House fixes (roadmap R16)
- Open House now saves the owner's real guest list and puts it back when the two hours are up, even across a restart (a minute-by-minute check reads the saved record), and each house can open once a day.
- The Summoning Circle no longer drops the boss into the house (fights can't happen in a safe house): it opens onto a new small private arena, one summoned boss at a time, with a light to walk home to Hearthgate.
- The House Portal can no longer be set inside a labyrinth or on Contested ground. Three new in-game tests. Boot test 141 in-game tests, 0 errors.

### 2026-11-13: Secret fixes (roadmap R17)
- A secret now triggers the moment you step on its tile (before, a twice-a-second check could miss a fast walker). Its gold is paid once per account: a second character finding it gets the discovery but not the gold again. "Only at night" secrets follow the game's own night, the one you see in the client, not the server's clock.
- The 60 secrets on Floors 6-10 had the same "somewhere on Floor N" hint; each kind now has its own clue in that floor's words (for example "Someone hid supplies where the marsh meets the woods, far from Reedhaven's walls."). Two new in-game tests. Boot test 143 in-game tests, 0 errors.

### 2026-11-13: Tests that reach the real game (roadmap R18, part)
- New GitHub workflow (`.github/workflows/boot.yml`) runs the full boot test on every push: it builds the pinned server, starts it on a fresh database and runs every in-game test. I can't read GitHub's results from your PC, so R18 stays marked "partly done" until a run is confirmed green (look under the repository's Actions tab: "boot test").
- New end-to-end tests: nobody reaches Floor 2 before the Axe-Lord's first kill (and the boulder still seals the stair), dying costs what DESIGN.md says on each difficulty, a red skull wears off, the Fortune Hall destroys its cut. Boot test 147 in-game tests, 0 errors.

### 2026-11-13: Every chat command one click away (roadmap R19)
- The Journal (J, or the new Journal button on the top bar) has a Commands tab: a button for each of the 24 player commands (`!hunt`, `!spells`, `!taskshop`, `!private`, `!openhouse`...). Commands that need more words (`!report`, `!summon`, `!dice`, `!fortune`) are put in the chat line for you to finish. The Journal window is wider so all eight tabs fit.
- A new check (`tools/check_commands.py`, part of the boot test) fails if anyone adds a player command without a button. Checked in your client after a restart: the Commands tab shows every button and clicking `!hunt` sends it. Your installed client now has the updated module.

### 2026-11-13: Small fixes (roadmap R20)
- Memory: scripts that keep a note per player (combo chains, PvP damage, quest offers, bot watch, Second Wind...) now forget it when the player logs out, so the server no longer grows with every login.
- The Fishing Derby pays a winner who logged off before the end: the 50,000 gold goes straight to the bank and the title waits for the next login.
- The "Rapid Respawn" weekend bonus was promised but missing; it is now one of the five weekend bonuses: every hunting ground counts as packed (all extra groups out) and they come back twice as fast. "Faster respawn when a floor is busy" is the crowd system (W10). Three new in-game tests; boot test 150 in-game tests, 0 errors.

### 2026-11-13: Twin Fang rebalance (roadmap R21)
- Q18 (assumed "style with a small edge"): the off-hand strike is now 22% of the hit (was 50%, the strongest build in the game), only with a one-handed sword and a free hand. Sword-skill combos count toward the trial only when they hit a real monster (not a summon or a training dummy). The trial on Floor 8 is fought alone: anyone else who walks in during a fight is sent home.
- New in-game test, including that the game itself knows which swords are two-handed. Boot test 151 in-game tests, 0 errors.

### 2026-11-13: Playtest fix, the yard's loot gate
- Jay's playtest: after killing several rats a gate stayed shut. The kill had counted; the stuck gate was the loot gate, because Pen Rats often had nothing to take and autoloot didn't count. Pen Rats now always drop a cheese, and carrying it (picked up by hand or by autoloot) opens the gate. Boot test 151 in-game tests, 0 errors.

### 2026-11-13: Early attack spells for Rangers and Vanguards (Jay's playtest)
- Jay: "there are no combat or attack spells in the beginning... so the players have something to attack with besides basic attacks once reaching level 8." Mages already had one at 8; now Rangers get Piercing Shot (level 8, one target) and Scatter Shot (16, a spread in front), and Vanguards get Heavy Strike (8, melee range) and Whirlwind (16, everything around you). Their damage grows with the distance or melee skill instead of magic level. DESIGN.md 5.3b updated; new in-game test; boot test 152 in-game tests, 0 errors.
