# Spirebound — full review

Written 2026-11-11. Nothing in the game or the design files was changed; this file is the only thing added.

## How to read this

- Every point says **what** is wrong or missing, **why it matters to players**, **how serious** it is, and **what to do**.
- Seriousness: **Blocker** (fix before anyone outside your house plays), **Important** (fix before a public launch, or it will cost you players), **Nice-to-have**.
- File references look like `path/file.lua:123` (file and line number) so the build agent can go straight to the spot.
- **Checked** means I confirmed it by reading the engine's own source code (Canary v3.6.1) or by building the map in memory and looking at the tiles. **Likely** means the code reads that way but it needs a live test. **Unsure** means exactly that.

## The short version

1. **The idea is strong and the foundations are tidy, but nobody has played it yet.** `PLAYTEST.md` is empty. Nine phases and about 80 commits were built on top of zero human play sessions. Every "feel" question (is combat fun, are bosses fair, is the first hour good) is still open.
2. **A lot of what is ticked off in `ROADMAP.md` is a thin first version, not the designed feature.** Floors 2–10 are one template stamped nine times; 16 of the 18 perk choices do nothing; "story quests" are 27 copies of "kill 30 of these"; the tutorial yard does not exist; repeatable boss fights, healer credit and the 20-player cap are not built.
3. **There are several real, checked bugs in the headline systems**: anyone can walk around the boulder to the next floor without killing the boss; a level-12 spell lets players pass through floors and ceilings; red and black skulls never expire; a party member or guildmate can permanently delete a Death Game character; the Fortune Hall destroys no gold; the login service can be broken into with one crafted password field.
4. **The balance numbers in `data/` are for the old October game, not this one.** The "economy check" that is supposed to protect you checks a game with 5 floors, level 70 and a currency called "col". The real game has no economy check at all, and its gold income explodes on high floors.

None of this is unusual for a project at this stage, and almost all of it is fixable. The order to fix it in is at the end (section A).

---

## 1. Vision and fun

### 1.1 Nobody has played it — Blocker (for everything else)
- **What:** `PLAYTEST.md:16` says "no playtests yet". Roadmap tasks 1.21, 2.13, 3.7, 4.7, 5.8 and 6.6 (all the "Jay plays it" steps) are unticked, but phases 2 to 8 were built anyway.
- **Why it matters:** the automated tests prove the rules run; they cannot tell you whether hitting a boar is fun. If sword skills feel bad, everything built on top is wasted effort.
- **Do:** stop adding features. Jay plays the first hour (new character → Registrar → level 15 → a secret → a death). Then the build agent fixes what he writes down. Repeat for the Floor 1 boss run with two or three friends on voice chat.

### 1.2 The first hour — Important
- **What:** DESIGN §5.1 promises an "Arrival Yard" with a guided path under 10 minutes that teaches movement, combat, looting and the skill bar. It is not on the map (`maps/layout_floor1.py` has no Arrival Yard; the Registrar simply stands in the temple, line 39). Roadmap 1.8 lists it as done. A new character can also walk out of town without ever picking a vocation or difficulty (`npc/registrar.lua:61`).
- **Why it matters:** your own research (DESIGN §15) lists "bad first 2 hours" as a top reason players quit. Today a new player gets: a temple, an NPC, a field of rats, and chat commands like `!journal`, `!path`, `!buyhouse` that nothing in the game tells them about.
- **Do:** build the yard for real: a walled path where each gate opens after one small step (kill a rat, loot it, use a sword skill, drink a potion), ending at the Registrar. Give the first three levels a pop-up hint each. Block the town gates until a vocation is chosen.

### 1.3 The first week — Important
- **What:** every floor after the first is the same square: town at the bottom, six bushes-and-monsters camps, a lake on the right, the apex fort top-left, the Pass and a small maze at the top (`maps/layout_floor.py`; compare `docs/previews/floor2_z7.png` to `floor10_z7.png`). Each floor has 8 monster types that differ only in size of numbers (`tools/gen_monsters.py:262-306`), and each camp is a random mix of the same five monsters, so there is no "easy camp, hard camp" ladder inside a floor.
- **Why it matters:** by Floor 3 a player has seen everything the game will show them for the next 300 levels. The feeling of "what's up there?" is the whole point of a tower.
- **Do:** this is expected of placeholders, but treat it as the real work still ahead, not a finished phase. Before a friends test, hand-tune **Floor 1 and Floor 2 only** (different layouts, monsters with one distinct trick each, a camp ladder from easy to hard). Leave 3–10 locked.

### 1.4 The first month — Important
- **What:** nothing stops the tower being finished in the first one or two weeks. Floors are "level targets, not doors" (DESIGN §3.1), boss health does not grow with the number of attackers, and the 20-player limit is not enforced (see 3.9). Azhrakkar has roughly 830,000 health (`tools/gen_monsters.py:267,305`); twenty mid-level players can burn that in a couple of minutes. A season is planned to last about five months (DESIGN §4), with 15 more floors promised during it.
- **Why it matters:** the shared tower is pillar #1. Once Floor 10 falls, the server's one story is over and what is left is a normal grind. The promise of "25 floors by season end" means a new floor about every nine days from a team of one agent and an owner who has not yet made the art for Floor 1.
- **Do:** (a) put a **calendar gate** on each floor boss (for example: Floor 2's boss room unseals no earlier than day 3, then one floor every 5–7 days). This turns every unlock into an event people log in for, and is how most seasonal servers pace content. (b) Drop the "25 floors" promise; say "10 floors, more if the season goes well".

### 1.5 Where players will get stuck or quit
- **Launch-day crowding (Important):** Floor 1 has about 215 monsters in total including the Underkeep, and each later floor has 107 (I counted from the map builder). A hundred players arriving on day one will find nothing alive. See 5.2.
- **Chat commands for everything (Important):** houses, portals, gambling, the shop, the Season Path, arena sign-up, language and the Journal all run on typed `!commands`. Players under 25 will not type commands. Each needs a clickable route (an NPC, a sign, or a client button) before public launch.
- **Death Game permadeath from lag (Important):** see 3.4.
- **Solo players at the boss wall (Nice-to-have):** a solo player cannot open a floor and cannot join the top guild's kill. The design's answer (repeat kills from a portal for parties of 1–5) is not built (3.9).

### 1.6 What successful servers do that this one doesn't (yet)
- A **website with account creation, highscores and a countdown** before anything else is public. Yours is static pages only (roadmap 7.1).
- **A staffed first week**: game masters online, a bug-report channel, hotfixes within hours.
- **An open beta that is wiped** before the real launch, announced as such.
- **Clear daily goals** visible on screen from minute one (your Season Path exists but hides behind `!path`).
- **Far more hunting room per player** at launch, or faster respawn when the server is busy.

---

## 2. Player progression

### 2.1 No new abilities for most of the game — Important
- **What:** sword skills unlock at levels 1, 1, 1, 60, 100, 150 (`lib/spirebound/sword_skills.lua:29-85`). The last level-unlocked spell is at level 80 for Vanguards, 70 for Rangers, 60 for Arcanists and **50 for Mystics** (`lib/spirebound/spells.lua:10-67`). The two "Lost Arts" come at 100 and 150. Floors 6 to 10 (levels 160 to 400) add nothing new to press.
- **Why it matters:** more than half the climb has no "ding, new toy" moment. That is the classic dead-level problem.
- **Do:** spread unlocks to at least level 300 (one meaningful thing every 20–30 levels), or add skill upgrades (rank II/III versions) as boss and quest rewards on Floors 6–10.

### 2.2 Gear stops halfway up the tower — Important
- **What:** there is no Spirebound gear. Monsters drop ordinary base-game items by ID (`tools/gen_monsters.py:257-259`). Melee weapons top out around Floor 5–7; **mages and rangers get no weapon upgrade after Floor 5**, and nothing at all for rangers beyond the shop bow and crossbow (`tools/gen_npcs.py`, weaponsmith rows). "Azhrakkar's Greatsword, the strongest sword in season 1" (DESIGN §9.3) does not exist. The old design's gear tables (`data/weapons.csv`, `data/armor.csv`) are for five classes that were replaced.
- **Why it matters:** "get stronger" is one fifth of your core loop, and "the best gear comes only from playing" is pillar 5. Right now there is no best gear.
- **Do:** design one gear ladder per vocation per floor (10 floors × 4 vocations × weapon + armour set), with each floor boss dropping that floor's best piece. Generate it from a table, the same way monsters are.

### 2.3 Perks: 16 of 18 do nothing — Important (it is also a bug)
- **What:** floors 2–10 offer perk choices such as "+10% maximum mana" or "+5% damage to bosses" (`lib/spirebound/floor_content.lua:8,27,46…`). Only the two Floor 1 perks are actually applied (`lib/spirebound/quests.lua:101-115`). Picking any other perk stores the choice and gives nothing.
- **Why it matters:** players will notice, and "the perk is fake" is the kind of thing that ends up in a server review.
- **Do:** implement each perk or remove the offer until it works. Add a test per perk that checks the number really changes.

### 2.4 Quests are kill counters — Important
- **What:** all 27 quests on floors 2–10 are "kill 30 X", "kill 30 Y", "kill 3 elites", with the same dialogue (`lib/spirebound/floor_content.lua`, e.g. lines 5-7 and 157-159). They pay gold only.
- **Why it matters:** DESIGN §8.3 calls these story quests, and two Lost Art spells and all perks hang off them. Pillar 6 ("plain to learn, every quest says what to do next") is met; "worth doing" is not.
- **Do:** one hand-written quest line per floor with a small story and a non-gold reward (a gear piece, a cosmetic, a shortcut). Keep kill quests as the daily tasks they already resemble.

### 2.5 Twin Fang is a power prize for the fastest guild — Important (your call)
- **What:** three players per season get +50% damage on every melee hit and three stronger exclusive skills (`lib/spirebound/sword_skills.lua:87-93`). It also works with a two-handed sword, because the check is only "one hand is empty" (`scripts/spirebound/twin_fang.lua:79-81`). The 1,000-combo requirement counts combos even when they hit nothing useful (`scripts/spirebound/sword_skills.lua:89-91`), so it is about three hours of hitting rats. "Defeat it alone" is not enforced: friends can kill the Warden for you (`twin_fang.lua:50-58`).
- **Why it matters:** DESIGN §5.6 says "a distinct style, not a must-have". As built it is the strongest melee build on the server, handed to whichever three Vanguards reach Floor 8 first, in a game whose top priority is protecting weaker players.
- **Do:** keep the rarity and the spectacle, cut the raw power: off-hand strike at 20–25%, one-handed swords only, combos must damage a monster near your level, and the trial room only lets one player in.

### 2.6 Rangers pay for every shot; everyone else attacks for free — Important
- **What:** sword skills cost no mana for anyone (`scripts/spirebound/sword_skills.lua:120`), including the mages' area attacks. Rangers alone buy ammunition, which DESIGN §5.3b calls the main everyday gold sink.
- **Why it matters:** one vocation carries the sink meant for all four. Rangers will be the poor class; mages get free area damage with no supply cost.
- **Do:** either give mage sword skills a mana cost, or make ammo cheap and move the sink somewhere everyone pays (repairs, travel, blessings).

### 2.7 Difficulty modes: Death Game is the safest way to level — Important
- **What:** a Death Game character earns +50% experience and can step down to Normal at any time in town, keeping every level (`lib/spirebound/difficulty.lua:90-100`). So the best strategy is: pick Death Game, hunt easy monsters, step down before anything risky.
- A second hole: every Death Game character, even one that never left town or already died, gets the account-wide title "Deathbound (Season N)" at season end (`lib/spirebound/season.lua:48-49`). The level-50 title and the level-100/200/300 outfit from DESIGN §5.4 are not built.
- **Why it matters:** Death Game is the feature people will tell their friends about. Its rewards should mean "I risked it".
- **Do:** stepping down costs the bonus (for example, lose the experience above what a Normal character would have earned, or drop a fixed share of levels). Award Deathbound only to characters that reached level 50 alive in that mode.

### 2.8 The numbers in `data/` describe a different game — Important
- **What:** `data/*.csv` and `data/economy_check.md` were last changed on 5 October (the old design): five floors, levels to 70, a currency called "col", classes called cleaver, shade and slinger. `tools/gen_tables.py` still produces them, and the only automatic check on GitHub (`.github/workflows/design-tables.yml`) only checks those files. The live game's numbers are typed straight into `tools/gen_monsters.py`, `tools/gen_npcs.py` and `tools/gen_floor_content.py`. The public website's Floor 1 monster list also reads the old file (`tools/gen_site.py:143`).
- **Why it matters:** DESIGN §10 promises "an economy check that fails loudly if prices make no sense". For the real game, that safety net does not exist, and `CLAUDE.md`'s rule about `data/` tables is not being followed.
- **Do:** rebuild `gen_tables.py` around the real 10-floor game (experience per hour, gold per hour, supply cost, time to each level band, time to afford a house) and make the monster and NPC generators read from it. Delete or archive the old tables.

### 2.9 Rough pacing estimate — Unsure, needs play data
- From the generator's formulas I estimate roughly 350–400 hours of solo hunting to reach level 350, with about 150 of those hours on Floor 9 alone (the 3× stage from 301 meets monsters that barely give more). Floors 1–3 fly by in about 10 hours. This is back-of-envelope arithmetic, not a measurement. The proper fix is 2.8.

### 2.10 Pay-to-win check — see 6.3
The shop itself sells no power (and a test enforces it, which is good). The hole is resale: see section 6.

---

## 3. Systems and game logic: bugs, exploits, loopholes

### 3.1 Anyone can walk around the boulder to the next floor — Blocker (Checked)
- **What:** the stair to the next floor is a live portal with a single boulder on the tile in front of it, in an open room (`maps/layout_floor1.py:187-191`, `maps/layout_floor.py:151-153`). The tiles left and right of the boulder are empty floor. I built the map in memory and confirmed it for every floor. No script checks that a floor is open when someone arrives.
- **Why it matters:** a player who reaches a boss room can step past the boss onto Floor 2, 3, 4… without anyone killing anything. The core rule of the game is skippable.
- **Do:** put the stair in a walled back chamber whose only entrance is the boulder tile, **and** add a server check: stepping onto a floor that is not open sends you back. Add a test that tries to walk there.

### 3.2 Skystep lets players pass through floors and ceilings — Blocker (Checked in code, needs a live test)
- **What:** Skystep (level 12, all vocations) only checks that the destination tile exists (`scripts/spirebound/spells.lua:143-160`). It does not check that there is a gap to climb through. The labyrinth's three levels and the boss room are stacked directly on top of each other (`maps/layout_floor1.py:165-176`), the Underkeep sits directly under Hearthgate, and Underkeep Wings 3, 5 and 6 sit under Wings 1 and 3 (`maps/layout_floor1.py:228-262`).
- **Why it matters:** three casts take you from the maze entrance to the boss room, skipping all three mazes. From the town street you can drop into the Underkeep without finding its secret, and from there into wings that are supposed to be sealed until Floors 4, 8 and 10.
- **Do:** copy the standard rule (you can only go up if the tile above you is empty, and only go down if the tile in front has no floor), block the spell in labyrinths and boss rooms, and stop stacking sealed areas above walkable ones in the real maps.

### 3.3 Red and black skulls never expire — Blocker (Checked)
- **What:** the script sets the skull timer to "now + 7 days" as a calendar time (`scripts/spirebound/pvp.lua:150,154`), but the engine expects the number of seconds remaining. The result is a skull that lasts about 57 years.
- **Why it matters:** one bad evening makes a character a permanent outlaw: locked out of towns, shops and boss rooms forever, losing everything on every death.
- **Do:** pass `7 * 86400` and `14 * 86400`. Add a test that reads the remaining time back. Note the engine only counts skull time down while the player is online; decide if that is what you want.

### 3.4 Death Game: ways to lose a character unfairly, and ways to never lose one — Blocker
- **Party members, guildmates and people on the same internet address can delete you (Checked).** Damage from them is deliberately ignored when deciding whether a death was "PvP" (`lib/spirebound/difficulty.lua:59-73`), and the engine lets party members and guildmates hurt each other. So if one of them lands the killing blow, the character is deleted. "Same address" includes housemates, internet cafés, and many mobile and South American connections where thousands share one address. This breaks DESIGN §6.6: "a Death Game character is only deleted by PvE".
- **A friend outside your party can make you immortal.** Any damage from an outside player in the last 60 seconds turns a death into a Hardcore-style penalty (`scripts/spirebound/difficulty_events.lua:59-72,76-93`). A friend on a second account taps you once a minute while you fight a boss. Boss rooms allow PvP at any level, so this works from level 1.
- **Protected low-levels can kill you with monsters.** A character under level 50 cannot be attacked (`lib/spirebound/pvp.lua:35`) but can drag a train of monsters onto a Death Game player. That death is PvE and permanent.
- **Lag, crashes and disconnects.** Nothing protects a Death Game character when the server stalls or the player's connection drops. Also, a "retired" flag lives in the server's memory cache, which is only written to disk at the hourly save (see 7.2). **Likely:** if the server crashes within the hour, a dead Death Game character comes back to life.
- **A retired character still holds things.** It keeps its name, its house, its guild leadership and its market offers, and still fills a character slot (`lib/spirebound/difficulty.lua:106-114`).
- **Do:** (1) a death is PvP if a player dealt the killing blow or most of the recent damage, whoever they are; drop the party/guild/address exceptions for the *deletion* decision and handle "friend tagging" by requiring real damage (say 15% of your health in the window) rather than any hit. (2) Monsters recently pulled by another player do not count as PvE for 30 seconds. (3) Write a public "unfair death" policy and give game masters a restore command. (4) On retirement, free the house, pass on guild leadership, cancel market offers, and save immediately.

### 3.5 Hardcore item-drop code is called with the wrong arguments — Important (Checked)
- **What:** the function expects (mode, blessings, amulet, skull, arena) but is called with (mode, skull, arena) (`scripts/spirebound/difficulty_events.lua:184` vs `lib/spirebound/difficulty.lua:163`). Blessings never reduce the extra drop chance, and when a red- or black-skulled Hardcore character dies the script hits an error.
- **Do:** fix the call; add a test that goes through the real death event rather than only the pure function.

### 3.6 PvP rules that can be turned against their purpose — Important
- **Only the last hit counts.** Unjust kills, the guild Sanctuary and bounty payouts all look only at whoever landed the final blow (`scripts/spirebound/pvp.lua:88,108,123`). A gang lets a throwaway character finish every kill: nobody important gets a skull and the Sanctuary never triggers.
- **Outnumbered shield as armour.** The shield counts every player who hit you in 10 seconds (`pvp.lua:65-78`). A team has its own spare characters tap their tank for 1 damage and he takes 40% less from the real enemy.
- **Protected healers.** A character under level 50, or under 70% of the attacker's level, cannot be attacked but can heal a player-killer all day.
- **Bounty "recent party partner" rule is not connected.** The rule exists (`lib/spirebound/bounty_war.lua:22`) but the game never supplies the data, so a murderer's friend leaves the party, kills him and collects the bounty, including his own fine.
- **Town guards.** A murderer who logs in inside a town, or respawns there, has 30 seconds and then loses a quarter of his health every second (`pvp.lua:178`). If he has a remembered "last safe spot" he is instead teleported back to it, which after a death is a free trip back to where he died (`pvp.lua:184-185`). The Outlaw Camp that DESIGN §6.4 promises as the place for red players to shop does not exist.
- **Not built yet (already noted in PROGRESS.md):** the 2-hour protection for new characters, and black skulls being barred from teleport gates.
- **Do:** count everyone who did meaningful damage for unjust kills, Sanctuary and bounties; only count outsiders who did real damage for the outnumbered shield; healing a skulled player removes your protection for a few minutes; build a respawn point outside town for murderers.

### 3.7 Houses — Important
- **Fortune Hall destroys no gold (Checked).** The winner is paid 1.9× the bet out of the host's bank (`scripts/spirebound/houses.lua:182-186`, `lib/spirebound/houses.lua:75-79`). The missing 5% simply stays with the host. DESIGN §7.5 says it is destroyed as a gold sink, and roadmap 3.4 says a test proves it; the test only checks the arithmetic. It is a 5% edge for house owners, not a sink.
- **Hosts cannot protect themselves.** Any visitor can bet up to 1,000,000 gold per roll against the host's whole bank whenever the host is online. There is no host-set limit, no pause, and no delay between rolls.
- **Open House wipes your guest list and may get you robbed (Likely).** `!openhouse` replaces the guest list with "everyone" and two hours later sets it to empty (`houses.lua:207,214`), so the owner's real guest list is lost. If the server restarts during the two hours the house stays open forever. The engine's default lets invited guests move items, and "everyone" is invited. There is also no cooldown, so one house owner can spam server-wide announcements.
- **The Summoning Circle almost certainly does not work (Likely).** The boss is created inside the house (`houses.lua:103`), and houses are safe zones where the engine refuses all attacks. The sigil is spent, the boss cannot be fought and never leaves. Even where it could be fought, the summoned copy has none of its special attacks, because those only run for bosses created by the boss system (`scripts/spirebound/bosses_floor1.lua:155-159`).
- **House Portal skips the labyrinth.** It refuses boss rooms and anything within 20 tiles of one *on the same level* (`houses.lua:18-25`). The top of the maze is on a different level, so it is allowed, as are apex spawns.
- **There are 63 houses on the whole server**, six per town. With one house per character and most house features locked behind owning one, "houses do things" will be true for about 63 people.
- **Do:** actually destroy the cut; let hosts set a table limit and open/close the table; make Open House add and later remove a single "everyone" entry and restore on restart; move the Summoning Circle to a small private arena reached from the house; ban portal targets inside labyrinths and Contested zones; plan for 10× the houses, or add rentable rooms.

### 3.8 The built-in cavebot penalty is on the honour system — Important
- **What:** the server learns that the cavebot is on only because a small script in the client says so (`scripts/spirebound/cavebot.lua:11-25`). The client ships the full vBot toolkit with its script editor; the installer only removes two pieces (`windows/Install-Client.ps1:71-81`). Deleting one line turns the penalty off. The "pattern logging" that roadmap 2.12 lists as done is not in the code.
- **Loopholes even for honest clients:** auto-targeting is free and auto-heal is free, so standing in a busy spawn with both on is unpunished botting. vBot's attack helper can fire perfect sword-skill combos automatically, which makes combos a setting rather than a skill. A second character that follows a botting one in a party gets its share of experience at full rate. Hunting tasks pay full gold to cavebot users (`scripts/spirebound/tasks.lua:2-24`).
- **Why it matters:** if half the server bots at 100%, the honest half leaves. And "captivating sword skills" stop mattering if a script presses them.
- **Do:** decide the real rule (see owner questions). Then enforce on the server: movement and kill patterns, not a client flag. Strip the script editor and the attack helper from the shipped client, or accept and price them in.

### 3.9 Bosses and floor unlocks — Important
- **One shared boss on a 30-minute timer, PvP on.** After the first kill each floor boss simply reappears in the same open room every 30 minutes (`lib/spirebound/bosses.lua:11`, `bosses_floor1.lua:206-211`). The designed version (a private portal for parties of 1–5, once per character per 20 hours, DESIGN §3.2.6) is not built. The strongest guild will camp every boss and nobody else will ever get a kill.
- **Healers and tanks get no credit.** Only damage counts (`bosses_floor1.lua:139-149`). A Mystic who healed the whole fight gets no title, no sigil and no house head start. PROGRESS.md admits this; it should be fixed before any real boss race.
- **One point of damage earns full credit.** Any hit in the last 90 seconds counts (`lib/spirebound/bosses.lua:29-38`), so spare characters can be carried to world-first titles and house head starts.
- **Enrage timer exploit.** The timer is set from the most players seen in the *first 60 seconds* (`bosses_floor1.lua:170-171`). Start the fight alone (60-minute timer), then bring in nineteen friends.
- **No 20-player limit, and boss health does not scale.** See 1.4.
- **Offline at the kill, lose your reward.** Titles and sigils are only given to players online at that instant (`bosses_floor1.lua:116-128`).
- **Reaction time.** Big hits land 0.6 seconds after the warning (`lib/spirebound/bosses.lua:8`). With normal internet delay to Miami from South America or Europe that leaves about a third of a second, in a game where a hit can delete a character. My view: 1.0–1.2 seconds for the lethal ones. Your taste call.
- **Do:** build the private repeat-kill portal with a per-character lockout; credit healing and damage taken; require a minimum share for credit; recompute the enrage timer whenever the headcount rises; enforce the room cap; store rewards for offline players.

### 3.10 Secrets — Important
- **Running across a secret can miss it.** Triggers are checked twice a second by looking at where each player is standing (`scripts/spirebound/secrets.lua:107-122`). A fast character crosses a tile in less than that. DESIGN §8.1 says "touches or passes".
- **Rewards are per character, so new characters farm them.** Each finder gets the gold reward once (300 to 14,000+ per secret depending on floor, `tools/gen_floor_content.py:160`). Make a character, run the route, bank the gold, delete, repeat.
- **Selling is a one-time race for the whole server.** Once sold, a secret is public forever with directions. From season 2 the locations are the same (only reward sizes shuffle, `lib/spirebound/remix.lua`), so veterans will sell all 120 in the first hours. "Exploration pays" becomes "exploration paid the first person".
- **"Night only" uses the real clock** (20:00–05:00 server time, `lib/spirebound/secrets.lua:57-59`), which is the middle of the working day or the middle of the night for whole continents. Use the game's own day/night cycle.
- **Floors 6–10 secrets all have the same hint**: "Somewhere on Floor N, off the beaten path" (`floor_content.lua:96-172`).
- **Do:** trigger on stepping onto the tile; make the gold reward once per account; move secret locations each season; add a few secrets that rotate weekly.

### 3.11 Season rollover — Blocker before the first real reset (Likely)
- **What:** `/season end` deletes rows straight from the database while the server is still running (`scripts/spirebound/season.lua:44-58`, `lib/spirebound/season.lua:58-71`). But the server keeps its own copy of the floor records, public secrets, Twin Fang holders, house owners and guilds in memory and writes them back when it saves or shuts down. I checked that the engine's key-value store works this way.
- **Why it matters:** after the restart, the "new" season may begin with floors already open, secrets already sold and houses owned by characters that no longer exist. Items lying inside houses are also not wiped. PROGRESS.md itself says a full reset has never been run.
- **Also missing:** the fishing log is supposed to carry over (DESIGN §4) and does not; no automatic backup is taken first.
- **Do:** make the reset an offline tool: stop the server, back up, run the wipe, start. Rehearse it on a copy of a real database long before season 1 ends.

### 3.12 Smaller confirmed problems — Nice-to-have unless noted
- **Hunting tasks exist only for Floor 1** (`lib/spirebound/tasks.lua:5-11`), pay 2,000–9,000 gold each (far more than Floor 1 hunting), can be farmed daily by high-level characters in minutes, and "task points" cannot be spent on anything. *(Important for the economy.)*
- **Season Path is per character** (lost on a Death Game death), takes about 8 of the season's 21 weeks to finish, and its rewards are the same furniture the cash shop sells (see 6.2).
- **Fishing Derby winner must be online at the final second** to be paid (`scripts/spirebound/events.lua:150-153`). The "struggle" click is one more press of the same button, which a script does trivially.
- **Weekend bonus:** four of the five designed bonuses exist; "rapid respawn" is missing (`lib/spirebound/events.lua:11-16`).
- **"Two clients per computer"** (DESIGN §12) is actually "two characters per account" (`server/config-overrides.lua:41`). Nothing limits accounts per person.
- **Underkeep strongbox** and secret rewards are per character and therefore farmable with new characters.
- **Several small memory leaks**: per-player tables that are never cleared at logout (`pvp.lua:3-5`, `client_link.lua:2`, `secrets.lua:107`). Harmless for a friends test; clean up before running for weeks.

---

## 4. Content gaps for a launch-ready game

| Area | State today | Seriousness | Recommendation |
|---|---|---|---|
| Tutorial / onboarding | Designed, not built (1.2) | Important | Build the Arrival Yard; in-game hints; a "how do I…" Help tab in the Journal |
| Account creation | None. Accounts are made by a database script | **Blocker for friends test** | Simplest safe option first (a small sign-up page), full website later |
| Quests | 30 kill counters (2.4) | Important | One real quest line per floor |
| NPC variety | 76 NPCs, 7 identical roles per town | Nice-to-have | A few characters with personality per town; they are cheap to write |
| Gear | None of its own (2.2) | Important | Gear ladder |
| Crafting | Draft in `DECISIONS.md` §2, not approved | Nice-to-have | The draft is sensible and small. I would say yes, after gear exists |
| Gold sinks | Few and flat (6.1) | Important | See section 6 |
| Social | Guilds, LFG, chat channels exist. No friends-list features beyond the engine's, no mentor mode (DESIGN §6.5), no guild halls | Nice-to-have | Mentor mode is worth building; it serves your anti-bullying pillar |
| Events | World events, arena, siege built; all untested by humans | Nice-to-have for now | Switch arena and siege **off** for the friends test; too few players |
| Anti-bot / anti-cheat | A client flag (3.8). No speed-hack, multi-client or pattern detection | Important | Server-side pattern logging; a report command |
| Moderation tools | None of your own: no report command, no mute, no chat filter, no ban reasons, no audit log of GM actions, no staff roles defined | **Important** (it is your pillar #2) | `!report`, a GM action log, a written punishment ladder, a chat filter for slurs in three languages |
| Website / wiki | Static pages, not hosted; Floor 1 data from the old tables | Important before public | MyAAC or similar; fix the data source |
| Accessibility | Cursor colours are green/orange/red only (colour-blind players cannot tell them apart); no text-size option; boss warnings are a red smoke effect only | Nice-to-have | Add a shape or icon to each cursor state; add a sound to boss warnings |
| Localization | Server messages and one NPC translated; 75 NPCs, quests, 120 hints, items and monsters still English | Nice-to-have | Machine translation has not been checked by a native speaker. Find one Brazilian and one Spanish-speaking friend to read it before launch |
| Rules and policies | Rules page exists. No privacy policy, terms, refund policy, or age statement | **Blocker before taking money** | See 6.4 |

---

## 5. Map layout

I looked at `docs/previews/*.png`, `maps/layout_floor1.py`, `maps/layout_floor.py`, and built the map in memory to count things.

### 5.1 What works
- The shape of a floor is right: town in the south, hunting fields around it, danger increasing as you go north, boss at the far end. Travel times are sensible: about a minute from Hearthgate to the nearer camps and under three minutes to the Pass or the apex fort at low level.
- Starter fields hug the town walls and sit inside the Guarded zone. Good for new players.
- The apex spawn is far from town and has layers. Good for the Contested-zone fights you want.

### 5.2 Not enough monsters for a launch — Blocker for public launch, fine for friends
- **What:** Floor 1 is 400×400 tiles with about 215 monsters including the Underkeep; each later floor is 300×300 with 107. Most of every map is empty grass.
- **Why it matters:** on launch day everyone is on Floor 1. With normal respawn times, a hundred players get less than one kill a minute each.
- **Do (real maps, M1):** aim for at least 1,500 monsters on Floor 1 across 14+ camps of different difficulty, caves under the camps, and respawn that speeds up when the floor is busy (the engine has a setting for this). `MAP_REQUESTS.md` M1 already asks for 14 camps; add the monster count.

### 5.3 Stacked levels create exploits — Blocker
See 3.1 and 3.2. The real maps should never put a sealed area directly above or below a walkable one, and the next floor's stair should be behind a real door.

### 5.4 The labyrinth is not a labyrinth yet — Important
- **What:** three small random mazes (about 30×20 tiles each) with one monster pack per level, joined by blue portals.
- **Why it matters:** DESIGN §3.1 treats the labyrinth as the climb before the boss. Today it is a two-minute walk, or zero with Skystep.
- **Do:** hand-designed labyrinths with a theme per floor, branching paths, a mid-point safe room, and a shortcut that opens once you have cleared it.

### 5.5 Other notes for whoever draws the real maps — Nice-to-have
- Every floor has the same layout; vary where the town, the Pass and the apex sit.
- Floor 1's Guarded zone is one big rectangle that also covers the bandit road east of town; shape zones to the terrain.
- Give each town a visible landmark for the features that are currently invisible: a Bounty Board, a guild board, a Fortune Hall street, a signposted portal plaza.
- Put the bank, depot and supply shop within a few steps of each other and of the temple. Resupply trips are the most repeated walk in the game.
- Towns need a second level and far more houses (3.7), plus guild halls.
- The Arena and Siege keep are hidden under Floor 1 and reached only by teleport. Fine.
- `maps/README.md` and `maps/src/` describe the old text-map pipeline, which the game no longer uses. Update or remove so a mapper is not misled.

---

## 6. Economy and monetization

### 6.1 Gold floods in on high floors and has nowhere to go — Important
- **What:** on Floor 10 an ordinary monster drops coins plus a 1–3% chance at gear that the town Outfitter buys for 20,000 gold (`tools/gen_floor_content.py:85`, `tools/gen_monsters.py:282-285`). My rough estimate is several hundred thousand gold per hour for one player. Against that, the dearest potion is 225 gold, weekly rent tops out near 22,500, and five blessings cost about 100,000.
- **Why it matters:** by mid-season gold is worthless, player-to-player prices run away, and new players can never catch up. On Floor 1 the opposite is true: hunting pays a few hundred gold an hour while one daily task pays up to 9,000.
- **Do:** this is what the rebuilt economy check (2.8) is for. Specific levers: Outfitter prices that scale gently (not with floor squared); percentage-based sinks that grow with wealth (market tax, repair costs, blessing cost by level with no cap, portal travel fees, house upkeep by size); potions that scale with floor. Sinks DESIGN §10 lists but that do not exist yet: travel fees, repair costs, skull fines as a true sink (today the fine becomes a bounty that a friend can collect), the Fortune Hall cut (3.7).

### 6.2 The shop as it stands would sell almost nothing — Important
- **What:** the shop has 11 items. Seven of the eight furniture and decoration items are also free Season Path rewards (`lib/spirebound/season_path.lua:17-29`) and several are sold for gold by the Housewright (`tools/gen_npcs.py`, housewright rows). That leaves two outfits and one mount, all using stand-in looks.
- **Do:** the shop needs its own exclusive, good-looking things: 8–12 outfits, a few mounts, name effects, house themes. That is an art job before it is a pricing job.

### 6.3 "Never pay-to-win" has one real hole — Important (your call)
- **What:** DESIGN §11 lets shop items be sold to other players for gold. Gold buys gear from other players, blessings, houses and supplies. So money → cosmetics → gold → power, in two steps.
- **Why it matters:** players will say it out loud on day one. Many servers accept this trade-off because it lets non-payers earn cosmetics; it is a fair choice, but it is not "never".
- **Do:** pick one: (a) shop items cannot be traded (pure, simple); (b) shop items can be traded, but the best gear on each floor is bound to the character that earned it (keeps the promise where it matters most); (c) accept it and reword the promise.

### 6.4 Prices and pack sizes (`DECISIONS.md` §1)
- The four packs ($5 / $10 / $25 / $50) and roughly one cent per coin are normal for this kind of server. Outfits at 600 coins ($6) and mounts at 800 ($8) are in the usual range.
- **Convenience items need a second look:** "extra depot space" is storage power in a game with capacity limits, and "extra character slot" matters more than it looks when retired Death Game characters keep their slot (3.4). I would make retired characters free their slot and sell depot space for gold instead.
- **House moving service** only makes sense if houses are plentiful.

### 6.5 Legal and payment risks — Blocker before taking any money (I am not a lawyer)
- **Gambling.** The Fortune Hall is gold-only, which is the right instinct. But if shop items can be resold for gold (6.3), gold has a real-money price, and a gold casino starts to look like a real-money casino to a payment company or a regulator. Several countries also treat this strictly where minors are involved. Safest: if 6.3 stays as is, remove or heavily cap the Fortune Hall; if the Fortune Hall stays, make shop items untradeable.
- **Payment companies** can freeze accounts for games that use someone else's intellectual property or that involve gambling. Before applying to Stripe or PayPal: all CipSoft art gone, no SAO wording anywhere public, written refund and chargeback policy.
- **Calling it a "donation"** does not change what it is legally; it is a sale of virtual goods. You may owe sales tax or VAT depending on where buyers are.
- **Privacy.** A worldwide player base means European and Brazilian privacy law applies to the accounts you store (emails, addresses, IP logs). You need a privacy policy, a way to delete an account, and an age statement.
- **No purchase record.** Shop purchases are written only to the server's text log (`scripts/spirebound/shop.lua:49`). You need a permanent record per purchase to answer disputes.

---

## 7. Technical and operations

### 7.1 The login service is not safe to expose — Blocker before any friend connects (Checked)
- **What:** `tools/login_server.py` says "development only" at the top, and it is. The function meant to make names safe for the database does nothing: it replaces a quote mark with a quote mark (line 37). A crafted name in the login box can run any database command, including resetting passwords or deleting everything. It also listens to the whole network (line 96), sends the password back to the client in plain text as the "session key" (line 48), has no limit on login attempts, and puts the database password on the command line (line 29).
- **Do:** before roadmap 9.1: use proper parameterised database queries, add attempt limits, and put it behind encryption (HTTPS). Better: replace it with the login part of a maintained website package.

### 7.2 Game state is saved once an hour — Important (Checked how the store works; impact Likely)
- **What:** nearly everything Spirebound adds (difficulty choice, Death Game retirement, floor clears, secrets, bounties, shop coins, titles) lives in the engine's key-value store, which keeps changes in memory and writes them at the server save. The save interval is the engine default: one hour.
- **Why it matters:** a crash can roll back a floor clear the whole server just celebrated, or give back shop coins that were already spent on an item the player keeps.
- **Do:** force a save right after the important moments (floor clear, retirement, shop purchase, secret sale), and shorten the save interval.

### 7.3 A god account with a public password is re-created at every start — Blocker before any friend connects
- **What:** the start script loads `server/sql/dev_accounts.sql` every time (`tools/run_server_wsl.sh`, near the end), which resets the `jay` account to the password printed in `MORNING.md` and gives it full gamemaster rights. The file itself warns never to run it on a public server, but the start script does it unconditionally.
- **Do:** make the dev accounts a separate, deliberate step that the public/friends start script never runs.

### 7.4 Passwords and accounts — Important
- Passwords are stored with an old, fast scrambling method (SHA-1, no salt). If the database ever leaks, most passwords can be recovered. The engine supports stronger options through a proper website package.
- Two-factor login is promised in DESIGN §15 and not planned in the roadmap.

### 7.5 Tests and automation — Important
- **Good:** 71 in-game checks run on every boot test, and the habit of "pure rule first, then wiring" is the right one.
- **Gap 1:** the tests mostly check the pure rules, not the wiring. Every Checked bug above (skull time, Hardcore drops, Fortune Hall cut, stair bypass, Summoning Circle) sits in the wiring and passed the tests.
- **Gap 2:** nothing runs automatically on GitHub except the check on the obsolete tables (`.github/workflows/design-tables.yml`). DESIGN §2 says GitHub runs the boot test; it does not.
- **Gap 3:** there is no scripted player, so nothing can walk through a door, fight a monster or click a window. The agent started one (`tools/winui/`); it is worth finishing, since it is also the base for the load test.
- **Do:** add a boot-test job on GitHub; add one end-to-end test per headline rule (try to reach Floor 2 without a kill; die as each difficulty; wait out a skull).

### 7.6 Performance at a few hundred players — Unsure, needs the load test
- Five separate timers each walk the whole player list every half second to two seconds, and each looks up the player's zone by scanning a list of 84 rectangles (`scripts/spirebound/pvp.lua:165-197`, `client_link.lua:19-41`, `secrets.lua:107-122`, `cavebot.lua:57-69`). At 300 players that is a few thousand small checks per second: probably fine, but it scales badly and it is easy to fix (one timer, zone looked up by map grid).
- The engine itself handles thousands of players on other servers. The real unknown is your scripts under load, which is what roadmap 9.2 is for. Do not skip it.

### 7.7 Hosting, backups, updates — Important before public
- The hosting comparison in `DECISIONS.md` §3 is reasonable. Game servers attract attacks, so pick on attack protection first and price second. Prices there are "as found on the day"; check them live.
- Backups exist for your PC. For a public server: automatic backups every few hours, copied **off** the server, and a restore that has actually been tried.
- There is no written update routine (announce → save → back up → update → check → reopen) and no way to roll back a bad update other than restoring the database. Write the one-page routine before launch.
- **Friends test from your PC:** the plan is to let friends connect to your home computer. That shows them your home internet address. Use a free tunnel or VPN-style tool so they never see it, and fix 7.1 and 7.3 first.

---

## 8. Risks: names, IP, takedowns

### 8.1 The game cannot go public on CipSoft's art, and replacing it is far bigger than the art list — Blocker for public launch
- **What:** every picture in the game today is from the official Tibia client. `ART_REQUESTS.md` covers outfits, monsters, bosses and UI (about 150 pieces). A Tibia-style game also needs every floor tile, wall, tree, door, item, spell effect and projectile: thousands of sprites. The tool to load custom art (roadmap 6.4) has not been started.
- **Why it matters:** this is the single biggest piece of unplanned work between today and a public launch, and it is the thing CipSoft acts on.
- **Do:** get the pipeline working with one sprite now, to learn what it costs. Then decide the route: a full custom set, or a licensed/open sprite pack as the base with your own monsters and bosses on top.

### 8.2 CipSoft names are visible everywhere on items — Important
- **What:** the name checker has 53 entries and only looks for SAO names and a handful of Tibia place names (`tools/banned_names.txt`). Every item in the game still carries its Tibia name: "wand of vortex", "snakebite rod", "amulet of loss", "magic plate armor", and the generators type these in directly (`tools/gen_npcs.py`, `tools/gen_floor_content.py:61-62`). Blessings also use Tibia's names (PROGRESS.md notes this).
- **Do:** rename items along with the gear ladder (2.2) and extend the checker to scan item names.

### 8.3 Friends testing means handing out CipSoft files — Important
- **What:** each tester needs the client plus Tibia's art files. Your installer downloads them from a third party's copy on GitHub (`server/PINS.env`, last lines).
- **Why it matters:** a private test among friends is low risk. A public download link is not.
- **Do:** keep the test invite-only, never post the installer publicly, and do not open to strangers until 8.1 is done.

### 8.4 The SAO resemblance — Important (I am not a lawyer)
- Names are original, which is good. But ideas in combination are still recognisable: a floating tower of floors, a death game, an information broker, a unique dual-wield skill for one swordsman, coloured player cursors, and a giant blue fiend with a huge sword at the end of a labyrinth. `DESIGN.md` itself names the SAO boss that inspired Azhrakkar (§9.3) and calls Hearthgate "our echo of SAO's starting city" (§3.3).
- Game ideas are generally free to use; names, art and marketing are where trouble starts. **Do:** never use the name or abbreviation in anything public (website, Discord, server lists, the README if the repo is ever made public); make Azhrakkar's look clearly your own (not blue, not goat-headed, different weapon would be safest); keep "inspired by" as a private note.

### 8.5 Smaller items
- `screenshots/*.png` in the repo show CipSoft art. Harmless while the repo is private; remove before it is ever made public.
- The game server engine is under a licence (GPL) that asks you to share your changes to *it* if you distribute it. You only run it, and your own scripts are separate, so this is fine today. The client is under a permissive licence.
- Server lists and communities ban servers that copy other servers' work or that sell power. You are clean on both counts so far.

---

## 9. Roadmap

### 9.1 Is the order right?
The first plan was right (Floor 1 end to end, then playtest). What actually happened is that phases 2 to 8 were built before the Phase 1 playtest. The result is wide and shallow. **The roadmap now needs a "make it real" phase before any "add more" phase.**

### 9.2 What I would cut or switch off before a friends test
- Floors 3–10 (keep them in the repo, seal them).
- Arena events and Spire Siege (need dozens of players).
- The shop, the Season Path, the website wiki, livestream.
- Android client (6.5b) and the remaining translations (6.3b).
- Season reset and remix (not needed for months).
- Twin Fang (Floor 8 is sealed anyway).

### 9.3 What to add or move earlier
1. **Jay's solo playtest of the first hour** — now.
2. **Fix the Blockers in sections 3 and 7** (list in A below).
3. **Account creation and a safe login** (moved up from phase 7).
4. **The Arrival Yard tutorial.**
5. **Rebuilt balance tables for the real game** (2.8).
6. **Floors 1 and 2 made real**: hand-tuned monsters, a gear ladder for those two floors, one proper quest line each, the private repeat-boss portal, healer credit.
7. **Moderation basics**: report command, GM log, rules shown in game.
8. **A scripted test player and the load test** (9.2).
9. **Art pipeline proof with one sprite** (6.4), because it decides the whole launch date.
10. Then the friends weekend (9.3), with a wipe afterwards.

### 9.4 A process note
`ROADMAP.md` ticks tasks whose "Done when" was quietly narrowed (for example 1.8 lists an Arrival Yard that is not there; 2.12 lists pattern logging that is not there; 3.3 and 3.4 are ticked on tests that do not exercise the real thing). I would add a rule to `CLAUDE.md`: a task is only ticked when a test goes through the real game path, and anything cut from a task is written as a new open task, not a note.

---

## A. Top 10 fixes, in order

1. **Play it.** Jay's first-hour session and a three-person Floor 1 boss run. Freeze new features until the notes are handled. (1.1)
2. **Close the floor-skipping holes:** wall in the stair, add the "is this floor open?" check, fix Skystep. (3.1, 3.2)
3. **Lock the front door before any friend connects:** fix the login service, stop re-creating the god account, add account creation. (7.1, 7.3)
4. **Make Death Game trustworthy:** no deletion by party, guild or same-address players; no friend-tag immortality; no monster-train kills by protected characters; a restore policy; step-down has a cost. (3.4, 2.7)
5. **Fix skulls that never expire and the last-hit-only PvP rules.** (3.3, 3.6)
6. **Finish the boss system:** private repeat kills with a lockout, healer and tank credit, minimum share for credit, enrage and headcount fixes, room cap, and a calendar gate per floor. (3.9, 1.4)
7. **Rebuild the balance tables and economy check for the real game,** then fix the gold curve, the Fortune Hall cut, task payouts and missing sinks. (2.8, 6.1, 3.7)
8. **Give players things to earn:** a gear ladder, abilities past level 150, working perks, one real quest line per floor (Floors 1–2 first). (2.1–2.4)
9. **Decide and enforce the bot rules on the server side.** (3.8)
10. **Prove the art pipeline and size the art job; plan Floor 1 for a launch-day crowd.** (8.1, 5.2)

Also before the first season ends, not before: rehearse the season reset on a copy (3.11).

## B. Questions only Jay can answer

1. **Pacing:** are you happy to put a calendar gate on floor bosses (one new floor every 5–7 days) so the tower lasts the season? (1.4)
2. **Pay-to-win line:** shop items untradeable, or tradeable with the best gear bound to its owner, or leave it and soften the promise? (6.3)
3. **Fortune Hall:** keep it, cap it, or drop it, given the legal link to the shop? (6.5)
4. **Bots:** is automatic sword-skill rotation allowed? Is standing still with auto-target and auto-heal "botting"? Should a follower character get full experience from a botting one? (3.8)
5. **Death Game:** what should stepping down cost? What is your rule when someone dies to lag or a server crash: restore, or "the tower is cruel"? (2.7, 3.4)
6. **Twin Fang:** real power for three players, or a spectacular style with a small edge? (2.5)
7. **Boss warnings:** 0.6 seconds as designed, or about a second for hits that can kill? You will know after one fight. (3.9)
8. **Houses:** many more houses, or keep them rare and move the house features (portal, summoning, gambling) somewhere everyone can rent? (3.7)
9. **Art:** will you make thousands of tiles and items with Grok, or start from an open sprite pack and make only the monsters, bosses and outfits yourself? (8.1)
10. **Scope of the first test:** are you comfortable sealing Floors 3–10 and testing only Floors 1–2 with friends? (9.2)
11. **Staff:** who moderates at launch besides you, and in which languages? (section 4)
12. **Azhrakkar's look:** how far from the original are you willing to move him? (8.4)
13. **Money:** are you prepared to register a business, write refund and privacy policies, and handle tax before the shop opens? If not, launch without a shop. (6.5)

## C. What is genuinely great here — protect these

- **The shared tower.** One world, one race, floors opened by players for everyone, names on a monument. It gives a private server something most lack: a story. Everything else should serve it.
- **Anti-bullying as a design pillar, with real rules behind it.** Level-range protection, zone tiers with a Guarded ring around towns, bully multipliers, consent-only guild wars, the guild Sanctuary, bounties. The details need fixing; the intent and the layering are better thought through than on most live servers.
- **Death Game where only the tower can kill you.** A permadeath mode that player-killers cannot grief is a rare, clever idea. It is worth the effort to make it airtight.
- **Difficulty chosen in the world, at an NPC, as a moment** rather than a website dropdown.
- **Secrets you can sell or keep.** The Info Broker gives explorers a real decision and creates server-wide gossip. Keep it; make it renew.
- **Never pay-to-win, enforced by a test.** The shop check that fails the build if an item has combat stats is exactly the right habit. One loophole to close.
- **Every heavy hit is telegraphed.** Fair bosses are the difference between "hard" and "cheap", especially with permadeath.
- **The cavebot stance.** Building it in and making manual play clearly better is an honest answer to a problem every server has. It needs enforcement, not a rethink.
- **Generators and tables instead of hand-edited files.** Monsters, NPCs, floors, translations and the website all come from one source each. That is why a rebalance will take hours, not weeks.
- **Pure rules separated from wiring, with tests.** The structure is right; the tests just need to reach further.
- **Plain-English paperwork.** `DESIGN.md` marks whose decision each line is. `QUESTIONS.md` always carries a recommendation. `PROGRESS.md` admits what is rough. A non-programmer can actually steer this project, which is rare.
- **Seasons with account-wide keepsakes.** The reasoning in DESIGN §4 is sound and matches your goal of keeping the level gap small.

---

*Things I could not check: how any of it feels to play; whether the client windows work beyond the screenshots; live behaviour of the Summoning Circle, Open House item rules and the season reset (marked Likely above); real performance under load; and anything legal, where you should ask a professional before taking money.*
