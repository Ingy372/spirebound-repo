# Floor 1 review, plus items, drops and gear (2026-11-26)

Written for Jay. Review only: nothing in the game was changed. Every claim names the file it comes from; anything I could not check is marked **unverified**.

**How this was checked.** I read the design files (`DESIGN.md`, `FLOOR1.md`, `ECONOMY.md`, `BALANCE.md`, `ROADMAP.md`, the gear spec, today's playtest hand-off), then the real game files: all 49 Floor 1 monster files, the spawn file, the boss, gear, difficulty, cavebot, secrets, fishing, quest and shop scripts, and every Floor 1 shop's price list. I ran the repo's read-only checkers (names, danger limits, NPC text, materials, commands, town and wilds plans).

**What I did not do.** I did not start the server, run the 279 in-game tests, or play in the client (another session was tuning the Axe-Lord while I worked, and the rule was "no edits"). I did not render the map, so tile-level problems (a missing door, a dead end) are **unverified** beyond what the plan checkers say. I did not read every NPC's dialogue line by line, nor the spell, house, arena or siege code. Two of the checkers redrew preview pictures as a side effect (`docs/FLOOR1_WILDS_PLAN.png`, `docs/previews/hunt_reed_marsh_z7.png`); I put both back exactly as they were.

**One moving target.** Another session was tuning the Axe-Lord while I read. It committed its work near the end of my review (commit `fff7d60b`: "Axe-Lord tuned by measurement: five level-30s kill him in 2 min 23 s with no deaths; client checks of the playtest fixes"). The boss numbers below are from that commit (20,000 health). I did not review the rest of that commit, and `ROADMAP.md` was still being edited when I finished.

---

## 1. Plain-English summary

**Overall grade: C+.** Levels 1 to about 20 are a solid B: a complete, guided start, many different hunting grounds, working shops, quests and secrets, and an unusually careful test habit. The last third of the floor (levels 20 to 35, the labyrinth, the Axe-Lord) is a D for now, because it has never been finished by real play, and the boss was re-tuned twice today against test characters only. The gear system works mechanically but has real balance holes.

**Top 5 problems**

1. **Nobody has ever finished Floor 1 the real way.** The labyrinth has never been walked in a playtest, it holds only about 13 monsters on three levels, and the Axe-Lord was re-tuned twice today: first after wiping a test party of three, then measured against five level-30 test characters whose level and gear were set by command (a kill in 2 min 23 s, commit `fff7d60b`). No party has ever reached and beaten him by really playing, so the moment the whole game is built around (the boss dies, Floor 2 opens) is still unproven.
2. **The Vanguard's reward weapons are weaker than swords the Weaponsmith sells.** A fully upgraded, boss-awakened Hearthguard Sword hits like an attack-22.5 sword; the spike sword on sale for 8,000 gold is attack 24. The axe version is a trap (25% weaker than the mace for the same effort). The "rare drop" weapons promise bonuses (life leech, critical hits) that are not built at all. And there are signs in the code that the weapon damage bonus itself is skipped on most hits (finding B4-0), which needs a quick test.
3. **The harder modes can be gamed, and the two boss rooms are open PvP for brand-new players.** Hardcore has no downside before level 21 (free +25% experience). A Death Game character becomes close to unkillable by hunting next to a friend who is not in the party. And anyone of any level can attack anyone inside the Gate Hound's arena and the Axe-Lord's hall, which every climber must visit.
4. **The money and levelling numbers in the documents are not what the game does.** The game doubles every drop chance (loot rate 2), but the economy model does not, so real income is roughly 25 to 70% above `ECONOMY.md`. The engine also adds two experience bonuses the levelling model leaves out, so Floor 1 is probably much shorter than the 11 to 15 hours you asked for.
5. **The cavebot penalty depends on the client being honest.** The server cuts experience and loot only when the client says "my bot is on". A changed client that stays silent farms at full speed; the only server-side catch is "killed 5 monsters without moving for 10 minutes".

**Top 5 strengths**

1. **The first hour is whole.** Yard, the Old Granary, the Registrar, the Proving, the town: each step has a guide, a quest-log line and a hint, and today's fixes (autoloot on, coins to the bank, gear that cannot fall on the floor) removed the worst new-player traps.
2. **Lots of real hunting ground.** Fifteen walled grounds plus the apex, six party caves, about 1,270 monsters, each with its own habit and trick, and a checker that proves no area floods a player (0 areas break the limits).
3. **The floor unlock is carefully built.** It is recorded once, saved to disk at once, credits everyone who really fought (damage, healing, tanking), ignores test characters, and gets easier to finish for small groups.
4. **No shop loop makes free money.** No Floor 1 NPC buys anything for as much as another sells it. The donation shop is switched off and holds no power beyond the starter set you approved.
5. **Honest engineering habits.** Generated tables, a name checker with zero hits, 279 in-game tests, and a playtest-to-fix loop that found and closed real bugs the same day.

---

## 2. Readiness verdict

**Ready for you and a few friends to play levels 1 to about 20: yes, with a short to-do list. Ready for the full run to the Axe-Lord: no.**

What blocks a friends session, in order:

1. **Reset the tower.** Every login currently says Floor 2's Pass is the next goal, left over from a test kill. You type `/floor reset 2` then `/floor reset 1` with your GM character (hand-off file, "Needs Jay"). Two minutes.
2. **Confirm today's fixes in the real client** (roadmap PT1): a reward taken while overloaded, a purchase when overloaded, first kill puts gold in the bank, Dorrow's weapon in hand, the Proving lit. Commit `fff7d60b` says these client checks were done while I was writing; I did not review it, so treat this as "check the note in `PROGRESS.md`", not as verified by me.
3. **Answer Q78 and prove the Axe-Lord by real play** (roadmap N1). He is now tuned for five level-30s, measured with test characters given their level, gear and Stair Key by command. Until a party that levelled and geared for real kills him, tell friends the boss is "not proven yet".
4. **Walk the labyrinth once** with a real party. It has never been played.
5. **Walk the three newest grounds** (Bramble Run, Smugglers' Ridge, Fallen Bastion). The plan checker says no trail leads to their gates (finding A1-2).

Nothing in the list is large. Items 1 and 2 are enough for a first evening that stays below level 20.

---

## 3. Floor 1 findings by area (Part A)

Severity: **Critical** = breaks the game or its main promise. **High** = players will hit it and it hurts. **Medium** = worth fixing before a public launch. **Low** = polish.

### A1. Layout and map

What exists (`maps/floor1_plan.py`, `FLOOR1.md`, spawn file `server/data-spirebound/world/spirebound-monster.xml`):

| Area | State |
|---|---|
| Arrival Yard, Old Granary, Registrar's hall, the Proving | Built, walked by fresh characters today |
| Hearthgate (walled city, the Hearth, 30 houses, about 20 service NPCs) | Built; hand polish still open (roadmap N3) |
| Millcross village, river, two bridges, huts and cabins | Built |
| 15 hunting grounds (Ratwarren to Fallen Bastion) | Built; 12 playtested, 3 new ones not walked in the client |
| 6 party caves under the grounds | Built; the Smugglers' Cellar and Molework were played |
| Old Watchtower (apex) | Built; not playtested by a real party |
| The Pass (Gate Hound arena) | Built and played |
| Labyrinth, 3 levels | Built; **never playtested** |
| Axe-Lord's hall and a private copy | Built; fight tuned today against five test characters, not yet by a real run |
| The Underkeep, 6 wings | Built; Wing 1 open, the rest sealed by floor progress |

**A1-1. The labyrinth is nearly empty and untested (High).**
- *For players:* the last stretch before the boss is three big mazes with about four monsters each, the same Ruin Sentinels and Archers they just hunted in the Quarry. It will feel like a corridor, not a climax.
- *Detail:* three spawn groups only: 4 Ruin Sentinels (level 1), 4 Ruin Archers (level 2), 5 Ruin Sentinels (level 3), each maze about 43 by 31 tiles (`maps/layout_floor1.py` lines 890-892). The hand-off lists the labyrinth under "not tested" (it was skipped with a jump).
- *Fix:* about 12 monsters per level in mixed packs, one labyrinth-only monster or elite, and one full walk with a real party.

**A1-2. Three new grounds have no trail in the plan (Medium, unverified in the client).**
- *For players:* the Bramble Run, Smugglers' Ridge and the Fallen Bastion may have to be found by walking through open country.
- *Detail:* `python tools/wilds_plan_check.py` prints "NO TRAIL TO" for all three gates and "problems 3". Roadmap 10.4 still lists "walking the new grounds in the client" as not done.
- *Fix:* add the trails and signposts in `maps/floor1_plan.py`, rerun the checker, walk them.

**A1-3. Two of the three new grounds are mirror images of old ones (Low).**
- *For players:* Smugglers' Ridge is the Bandit Road flipped; the Fallen Bastion is Shard Fields flipped with sentinels. Veterans will notice.
- *Detail:* `maps/floor1_plan.py` lines 752-776 (`_flip(BANDITS...)`, `_flip(... SHARDS ...)`).
- *Fix:* give each its own centrepiece when Step 4 (launch-size Floor 1) continues.

**A1-4. Boar Meadow is the thinnest ground, and it is the Vanguard's own (Medium).**
- *For players:* the class with the hardest solo life gets 17 boars on its class ground (11 on the surface), and the first story quest asks for 15 of them. Two Vanguards there at once will fight over spawns.
- *Detail:* spawn file count; roadmap 10.4 and Q73 already name it the weak spot.
- *Fix:* answer Q73 (boars in pairs) or enlarge the meadow to about 30 boars.

**A1-5. Dead ends, missing doors, unfinished tiles: unverified.** I did not render the map. The automated checks that exist pass: `hunt_check.py` (every ground reachable and within its danger limit), `hearthgate_plan_check.py` (every town service 29 to 80 steps from the Hearthstone), and all 12 secrets and 15 chests have a real spot on the map (`lib/spirebound/world_points.lua`).

### A2. The expanding dungeon (the Underkeep)

**How it works** (`scripts/spirebound/underkeep.lua`, `lib/spirebound/floors.lua`): the way in is secret s1, the drain grate in Hearthgate's south-west corner. Wings 2 to 6 are each closed by a boulder standing where a teleport should be. Once a minute the game checks which floors are open and swaps boulder for teleport: Wing 2 when Floor 2 opens, Wing 3 at Floor 4, Wing 4 at Floor 6, Wing 5 at Floor 8, Wing 6 at Floor 10, with a server-wide announcement. This matches `DESIGN.md` 3.4 and it **is wired up**.

**A2-1. Wing 1 is small (High, against your "must-have").**
- *For players:* the growing dungeon you want as a Floor 1 highlight is, on day one, a few halls with about 18 monsters of two kinds and one daily strongbox. It is a pleasant secret, not yet a place to spend an evening.
- *Detail:* the whole Underkeep holds about 100 monsters across six wings: Black Crawler 9 and Mire Toad 9 in the first area, then 8 to 16 per later kind (spawn file, level 8 to 10 of the map). Which monster sits in which wing is **unverified** (I mapped it by position only).
- *Fix:* triple Wing 1 (about 50 monsters, three kinds, one mini-boss), and give it the "one more secret per wing" the design promises.

**A2-2. No wing holds a secret of its own (Medium).** `DESIGN.md` 3.4 says every wing hides at least one more secret (shop, boss, chest room, fishing pool). The Floor 1 secret list has 12 entries and none is inside a wing (`lib/spirebound/secrets.lua` lines 18-31).

**A2-3. The daily strongbox pays every character, not every account (Low).** 800 to 1,500 gold plus a 25% gem per character every 20 hours (`underkeep.lua` lines 6-22). With extra characters allowed, that is a small alt faucet. It also uses the plain "add item" call that drops things on the floor when a player is overloaded (the same class of bug as hand-off P1-1). *Fix:* once per account; use `SpireGive.reward`.

**A2-4. Can the wings be skipped? Unverified, probably not.** Each wing is a separate area reached only by its teleport. I did not test whether the Skystep spell (climb a level) or a rope spot crosses between wings. Worth one GM test per wing.

**A2-5. During the friends test only Wing 2 can ever open (by design).** `lib/spirebound/scope.lua` seals Floors 3 to 10, so Wings 3 to 6 stay shut. Fine, but say so to testers.

### A3. Monsters and spawns

Monsters have no level of their own; the "level" is the level band of the ground they live in. Experience shown is the base number; the game multiplies it by the stage (10x at levels 1-8, 4x at 9-20, 3x at 21-50) and by two engine bonuses (finding A3-1). "Returns after" is the respawn time written in the spawn file.

| Monster | Where | Levels | Health | Hardest normal hit | Other attacks | Base XP | Spawns (surface / below ground) | Returns after (s) |
|---|---|---|---|---|---|---|---|---|
| Pen Rat | Arrival Yard: Old Granary cellar (tutorial) | 1-2 | 12 | 3 | - | 1 | 0 / 15 | 15 |
| Bramblejaw | The Proving (one-person intro boss, cannot kill you) | 3 | 240 | 12 | - | 6 | by script | - |
| Field Rat | The Ratwarren | 1-4 | 20 | 8 | - | 6 | 10 / 134 | 22 |
| Hopper Toad | Toad Pond | 3-7 | 28 | 10 | slows you | 9 | 24 / 42 | 20, 22 |
| Sproutling | Sproutling Glade | 5-10 | 35 | 10 | earth 0-12 (range 4) | 13 | 13 / 66 | 22 |
| Meadow Wasp | Waspgrass Fields | 7-12 | 45 | 16 | - | 17 | 66 / 96 | 22 |
| Bristle Boar | Boar Meadow | 9-15 | 90 | 30 | physical 0-36 (range 4) | 28 | 11 / 6 | 20, 43 |
| Burrow Mole | Burrow Hills + Molework caves | 11-16 | 130 | 32 | - | 39 | 64 / 140 | 43, 80 |
| Meadow Wolf | Wolf Copse, Bramble Run, Alpha's Den | 12-20 | 85 | 25 | - | 36 | 37 / 60 | 20, 28, 80 |
| Reed Snapper | Reedmarsh | 14-19 | 150 | 38 | slows you | 39 | 20 / 0 | 20 |
| Thornsnap | Thornsnap Hollow + Rootcellar | 14-20 | 140 | 35 | slows you | 56 | 23 / 64 | 20, 80 |
| Field Shardling | Shard Fields + Grotto | 17-24 | 120 | 20 | energy 0-35 (range 4) | 58 | 24 / 78 | 20, 30, 80 |
| Road Bandit | Bandit Road, Smugglers' Ridge, Cellar | 19-27 | 160 | 45 | smoke bomb (drunk) | 50 | 18 / 24 | 28, 80 |
| Bandit Crossbowman | Smugglers' Cellar, bandit grounds | 19-27 | 190 | 15 | physical 0-60 (range 6) | 72 | 10 / 22 | 28, 60, 80 |
| Hedge Hexer | Smugglers' Cellar, bandit grounds | 19-27 | 170 | 10 | earth 0-55 (range 4) | 78 | 8 / 22 | 28, 60, 80 |
| Ruin Archer | Old Quarry, Fallen Bastion, labyrinth | 23-30 | 220 | 20 | physical 0-60 (range 6) | 83 | 22 / 20 | 30, 80, 90 |
| Ruin Sentinel | Old Quarry, Fallen Bastion, labyrinth | 23-30 | 300 | 70 | physical 0-55 | 96 | 26 / 22 | 30, 80, 90 |
| Stonehorn Ram | Old Watchtower (apex, Stair Key piece) | 28-40 | 900 | 120 | physical 0-150 (range 4) | 480 | 26 / 16 | 60, 75 |
| Grey Alpha | Elite: Wolf Copse / Bramble Run | 12-20 | 260 | 60 | - | 107 | 4 / 4 | 450 |
| Bandit Captain | Elite: Bandit Road / Smugglers' Ridge | 19-27 | 450 | 90 | physical 0-60 (range 4) | 201 | 6 / 4 | 450 |
| Old Bristleback | Elite: Boar Meadow | 9-15 | 600 | 60 | physical 0-80 (range 4) | 220 | 1 / 0 | 450 |
| Moonhowl | Elite: Wolf Copse | 14+ | 520 | 55 | physical 0-40 | 240 | 3 / 0 | 450 |
| Mossback Snapper | Elite: Reedmarsh | 14+ | 900 | 70 | slows you | 250 | 1 / 0 | 450 |
| Blackthorn | Elite: Thornsnap Hollow | 14+ | 840 | 65 | slows you | 330 | 1 / 0 | 450 |
| Prism Shardling | Elite: Shard Fields | 17+ | 720 | 40 | energy 0-80 (range 4) | 340 | 1 / 0 | 450 |
| Granite Warden | Elite: Old Quarry | 24+ | 1100 | 95 | physical 0-80 | 380 | 1 / 0 | 450 |
| Old Tusk | Hidden mini-boss (secret s2), woken by script | party | 1800 | 140 | physical 60-160 (range 4) | 900 | by script | - |
| Hollowfang | Hidden mini-boss, woken by script | party | 1500 | 110 | physical 50-140 (range 4) | 750 | by script | - |
| Briar Mother | Hidden mini-boss, woken by script | party | 2200 | 120 | - | 1000 | by script | - |
| Drowned Warden | Hidden mini-boss, woken by script | party | 3200 | 190 | - | 1500 | by script | - |
| Gate Hound | FIELD BOSS: the Pass (spawned by script) | party ~30 | 4000 | 180 | physical 80-160 | 2500 | by script | - |
| Axe-Lord of the Stair | FLOOR BOSS (spawned by script) | party 30-35 | 20000 | 160 | physical 80-170 | 8000 | by script | - |
| Black Crawler | Underkeep (level 8 of the map, first wings) | ~25-35 | 520 | 110 | - | 260 | 0 / 9 | 90 |
| Mire Toad | Underkeep (first wings) | ~25-35 | 420 | 70 | earth 30-90 (range 4) | 210 | 0 / 9 | 90 |
| Vault Rat | Underkeep (deeper wing) | Floor 2+ | 600 | 130 | - | 320 | 0 / 8 | 90 |
| Chain Ghoul | Underkeep (deeper wing) | Floor 2+ | 900 | 170 | physical 60-150 (range 3) | 470 | 0 / 16 | 90 |
| Drain Matron | Underkeep mini-boss | Floor 2+ | 9000 | 300 | earth 150-350 (range 5) | 4200 | 0 / 1 | 1800 |
| Iron Shade | Underkeep (deeper wing) | Floor 4+ | 1800 | 200 | energy 120-280 (range 5) | 950 | 0 / 16 | 90 |
| Trap Mimic | Underkeep (deeper wing) | Floor 4+ | 2200 | 320 | - | 1100 | 0 / 8 | 90 |
| Keep Warden | Underkeep (deeper wing) | Floor 6+ | 4200 | 480 | physical 250-500 (range 4) | 2300 | 0 / 16 | 90 |
| Deep Sentinel | Underkeep (deepest wings) | Floor 8+ | 8000 | 800 | physical 400-800 (range 4) | 4500 | 0 / 8 | 90 |
| Vault Wraith | Underkeep (deepest wings) | Floor 8+ | 6500 | 400 | energy 400-850 (range 5) | 3800 | 0 / 8 | 90 |
| Vault Warden | Underkeep boss | Floor 8+ | 60000 | 900 | physical 500-1000 | 30000 | 0 / 1 | 1800 |
| The Underkeeper | Underkeep final boss | Floor 10 | 180000 | 1600 | physical 900-1800; physical 600-1200 | 90000 | 0 / 1 | 1800 |

(Also in the folder, with no loot and no hunting role: Ember Sprite, Mirror Image, Wolf Companion, Patrolman Teodric and the Twin Fang Warden, all created by spells, quests or later-floor content.)

**A3-1. Levelling is faster than the plan says (High).**
- *For players:* you asked for Floor 1 to last 11 to 15 hours. The real game is likely well under that, and a party is faster still (today's party went from level 3 to 19 in 2 hours 45 minutes including town trips).
- *Detail:* the engine multiplies every kill's experience by a fresh-stamina bonus (1.5x for the first hours of play each day, on for everyone because `freePremium = true`) and a low-level bonus on top of the stage rate (Canary's `data/events/scripts/player.lua` lines 597-601, read from the pinned Canary package). `tools/gen_economy.py` `stage()` (lines 33-35) counts only the stage. The monster generator's own notes say the same ("the engine adds +50% below level 50 and +50% for fresh stamina", `tools/gen_monsters.py`, Pen Rat). The exact size of the low-level bonus at each level is **unverified**.
- *Fix:* put both bonuses into the model, measure solo with the autopilot (roadmap PT3), then lower the 9-20 stage if you still want 11 to 15 hours.

**A3-2. Is the difficulty right for new players? Mostly yes; the wall is at level 19+ (Medium).**
- Levels 1 to 18: safe to the point of being gentle. The party playtest had no deaths from level 3 to 21 and the healer was never needed (hand-off P3-17).
- Levels 19+: the Bandit Road is a "mixed" ground on paper but plays as a group ground. Four Road Bandits killed a level-21 Vanguard in about 20 seconds; the Bandit Captain hits a 260-health Mystic for 55 to 61. Two story steps send solo players there (The Lost Patrol, and Iron for the Stair 2 of 2, which is a piece of the Stair Key: 30 Road Bandits).
- *Fix:* either mark the Bandit Road "group" in the plan and the Journal, or thin its packs to pairs on the outer loops so a solo player can earn the 30 kills.

**A3-3. Vanguard solo (Medium).** By the project's own model the Vanguard earns the least experience on every ground (Ranger 1.3x, Arcanist and Mystic 1.2x faster kills; `tools/gen_economy.py` `CLASS_SPEED`), which is your intent ("hardest solo"). Three things make it harder than intended: its class ground is the smallest (A1-4), its reward weapons are under-powered (B4-1), and before today's fix it could not drink strong health potions. With B4-1 fixed I would call it fair. The Ranger is clearly the easiest, as designed. Mystic and Arcanist were fine in the playtest, though mage health (295 at level 30) makes every boss hit a near one-shot.

**A3-4. Burrow Hills pays about three times its neighbours for a party (High, already on the roadmap as PT3).** 138,000 to 143,000 experience an hour each at levels 16-19 against 47,000 to 56,000 in Wolf Copse. 204 moles, 140 of them underground, returning every 43 to 80 seconds, with a soft 32 melee hit. *Fix:* halve the underground mole count or lengthen their return time to about 120 seconds.

**A3-5. Elites are not special for shards (Low).** Flawless shards are meant to come from elites, but the Stonehorn Ram also drops them and there are 42 Rams (3.5% each). Details in B4.

### A4. The floor boss and the unlock

**The fight** (`scripts/spirebound/bosses_floor1.lua`, monster file): 20,000 health (working copy), armour 40, swings up to 160, a 3-tile cleave for 80-170, and every 6 seconds a marked tile under a random player for 110-200 that lands after 0.6 seconds. At 60% he calls two Ruin Sentinels (the design says captains). Below 25% he changes look and the marked hit becomes a 3-tile line at the furthest player for 160-260 with a 1-second warning. He heals to full if nobody hurts him for 60 seconds or the room is empty for 30. He hits 50% harder every 30 seconds after an enrage timer that shrinks with headcount (60 minutes alone, 12.8 minutes for five, 8 minutes for eight or more).

**The Gate Hound:** 4,000 health, swings up to 180, a howl ring every 20 seconds for 120-220, three wolves. Returns 30 minutes after each kill. Killed by a level-30 party of three in about a minute with no deaths: this one feels right.

**The unlock** (`lib/spirebound/floors.lua`): when the Axe-Lord dies, everyone who did at least 2% of the fight's total work (damage, healing a fighter, or half the damage soaked) within the last 90 seconds is credited, top 20. The first time, the game records it, saves immediately, removes the boulders to Floor 2, announces it, starts the house head start, grants titles and fireworks. A second kill cannot fire it again (`recordClear` returns false once `bossDeadAt` is set).

Loot: 100 gold coins, up to 40 platinum, 10 health and 10 mana potions, in one body. The real reward is the weapon awakening for every credited fighter, plus a Boss Sigil.

**A4-1. The boss has only ever been beaten by test characters (Critical for the milestone).** Covered in the summary. Today's measured kill (five level-30s, 2 min 23 s, no deaths, commit `fff7d60b`) used characters whose level, tier-3 gear and Stair Key were set by command (`tools/party_run.py` `axelord30`). It shows the numbers are in range for five; it does not show that a real party can earn the key, cross the labyrinth and win. Roadmap N1 is the fix; the floor should not be called done before it.

**A4-2. Anyone can attack anyone inside both boss rooms, at any level (High, a design conflict).**
- *For players:* the under-50 protection that covers all of Floor 1 switches off inside the Pass arena and the Axe-Lord's hall. One griefer can walk in during a fight and kill the healer. His first two kills of the day cost him only a short orange mark; the red skull comes at the third.
- *Detail:* `lib/spirebound/pvp.lua` line 154 exempts the "bossroom" zone from newbie protection, and line 161 from the level-range rule. The Pass arena is a "bossroom" zone on the surface (`world_points.lua` line 1574). This follows `DESIGN.md` 3.2 ("PvP is on inside boss rooms"), but it works against your top priority (protect new players from toxic players).
- *Fix (your call, see Open questions):* keep boss-room PvP for level 50+ only, so Floors 1 to 4 are safe and later floors keep the drama.

**A4-3. The Gate Hound is a queue at launch (Medium).** Every climber needs credit on a Gate Hound kill for the Stair Key. He returns every 30 minutes and at most 20 players are credited per kill: 40 players an hour. A strong group can also kill him in under a minute, before late arrivals earn their 2%. *Fix:* return time 10 minutes, and credit anyone who did at least 1% in the arena.

**A4-4. A guild can hold the boss hall (Medium).** The hall holds 20; extra arrivals are teleported out, last in first out. Twenty characters (three clients per PC are allowed) can fill it and keep rivals outside. PvP inside is the only counter, and A4-2 says that should not apply below 50. *Fix:* cap by party or guild (for example at most 10 from one guild), or open a second hall when the first is full.

**A4-5. Three ways the unlock could silently never fire (Medium).**
1. If every credited name starts with "Pilot " or "Spell ", the kill is treated as a test and ignored (`Floors.onlyTesters`, `floors.lua` lines 140-150). Real players can pick such names ("Spell Weaver"); nothing reserves them. *Fix:* recognise testers by their test account (as `/pilot` already does), not by name.
2. If a boss dies after its fight record was lost (for example after a GM reloads scripts), the death is ignored and the boss is never scheduled to come back until a restart (`bosses_floor1.lua` lines 222-227). *Fix:* rebuild the record on death and always schedule the return.
3. The hall stays sealed until day 3 of the season once a season start is set (`bosses.lua` `CALENDAR_FIRST_DAY`). Intended (Q13), but for a friends weekend make sure no start date is set or the hall will throw everyone out.

**A4-6. Only one player gets the boss's coins and potions (Low).** One body, opened by whoever did the most damage. *Fix:* pay each credited fighter directly (for example 10 platinum each) the way shards are paid.

**A4-7. The private hall skips the Stair Key (Low).** After the floor is cleared, `!private` at the top of the labyrinth takes a party of 1 to 5 in without checking the key (`bosses_floor1.lua` lines 305-360). Late climbers can be carried to the awakening. Decide if that is wanted.

**A4-8. After the first kill there is little reason to fight him again (Low).** The awakening is once per weapon. Repeat kills give experience, a sigil and one body of coins.

### A5. NPCs, quests and secrets

**NPCs** (39 Floor 1 files in `server/data-spirebound/npc/`, generated by `tools/gen_npcs.py`): Guide Pell (tutorial), Registrar Maelis (path and difficulty), Priest Odran (healing, blessings), Banker Tolliver and a branch banker, Trader Osric (buys loot), Broker Nell (market), Merchant Wenna, Weaponsmith Garrick (also upgrades, reforges and replaces gear), Armorer Hesta, Quartermaster Bryn, Alchemist Ivo, Fletcher Tamsin, Runewright Mael, Tailor Quill, Housewright Orla, Innkeepers Roan and Bess, Postmaster, two coachmen, Ascendant Veyra (promotion), Guildwarden Sela, Taskmaster Rhen, Bounty Warden Cass, Warden Ketta, Vesper the Info Broker, quest givers Captain Dorrow, Hunter Brannoch, Miller Agna, Fisher Corwin, Fence Marrow and Patrolman Teodric, and six background townsfolk. `python tools/check_npc_text.py` reports 0 problems. I did not read every line of dialogue: **partly unverified**.

**Quests** (`lib/spirebound/quests.lua`): 6 story quests, a 2-part gear line, a weapon-tempering quest, an escort, a lore hunt (six stones), a lever puzzle, a delivery with a moral choice, 4 side hunts, 8 class outfit-addon quests, and the automatic Stair Key. Gold from all one-time Floor 1 quests is about 17,000 per character, which is reasonable against 2,000 to 12,000 an hour of hunting. Today's fix makes party kills count for everyone nearby.

**Secrets and the Info Broker** (`lib/spirebound/secrets.lua`, `scripts/spirebound/secrets.lua`): 12 secrets, each with a real spot on the map. Finding one records it as yours and pays its own small reward. Vesper buys it once per world (small 1,500, medium 3,000, large 6,000 gold on Floor 1; 33,000 in total), after which it is public. Gold is once per account, a cavebot cannot trigger a secret, and a sale is saved at once. This is your design, and it works by the code.

**A5-1. The Stair Key sends solo players into group content (Medium).** See A3-2: 30 Road Bandits and a Gate Hound kill are mandatory.

**A5-2. Quest text and the map disagree in places (Low).** The Bandit Road is called "east" in four quests; it is north-east. Wolf Copse is "west of town" in two quests and "across the river beside Millcross" in a third. The Old Quarry is "north" in one and "north-east" in another (`quests.lua`; positions in `maps/floor1_plan.py` `CAMPS`). New players read these literally.

**A5-3. The Sealed Shrine's 1,000 gold is paid to every character (Low).** Every other secret's gold is once per account; this one calls `addMoney` directly (`scripts/spirebound/secrets.lua` lines 27-37). It also drops two Bandit Captains on a player who may be alone.

**A5-4. Secret item rewards can still fall on the floor (Low).** Secret rewards and the Underkeep gem use the plain `addItem` (same file, line 56), the bug class fixed elsewhere today.

**A5-5. A weapon tier can be had for free at the most expensive step (Low).** "Tempered in the Field" gives +1 tier whenever it is handed in. A player who waits until tier 4 skips the tier-5 cost (3 flawless shards and 6,000 gold). *Fix:* the temper only works below tier 2.

**A5-6. Nothing here breaks the economy.** No quest or secret reward is large against hourly income. The first-time ground chests are the biggest one-off: about 34,500 gold and 15 rough shards per character across the 15 chests (`lib/spirebound/chests.lua`), see B4-5.

### A6. Town and safety

- **Safe zone:** Hearthgate and Millcross are "town" zones on three map levels (ground and two upper storeys), so upstairs rooms are safe too (`world_points.lua` `WorldZones`).
- **Guarded ring:** the starter grounds and the roads around the city. An unjust kill there counts as three.
- **Everywhere else on Floor 1:** nobody below level 50 can attack or be attacked (`pvp.lua` line 154). Since Floor 1 is levels 1 to 40, **Floor 1 is effectively PvP-free**, except the two boss rooms (A4-2).
- **Protections that exist in code:** level-range rule, outnumbered shield, guild-farming sanctuary, bounties, weighted skulls, murderers thrown out of towns and boss rooms.
- **PvP cursors:** the colours are a client feature I did not test: **unverified**.

**A6-1. The "2 hours of play time protection" in `DESIGN.md` 6.4 was not found (Low).** I searched the three PvP script files (`lib/spirebound/pvp.lua`, `scripts/spirebound/pvp.lua`, `pvp_lock.lua`) for a play-time rule and found none, only the level-50 rule. It hardly matters on Floor 1 because of that rule, but the design promises both. **Unverified** beyond that search.

**A6-2. Test commands ship inside the live game files (Low).** `/pilot` (set level, give items, jump) is in the normal datapack and is locked only by the account's e-mail ending in `@localhost` (`scripts/spirebound/dev_pilot.lua` lines 35-43), relying on the sign-up page refusing such addresses. One lock is thin for commands this strong. *Fix:* load the dev scripts only when a "test server" switch is on.

### A7. Fishing and other side activities

**Fishing works by the code** (`scripts/actions/tools/fishing.lua`, `lib/spirebound/fishing.lua`): cast on water, 25 to 70% bite chance by skill, wait 2 to 6 seconds, click again within 3 seconds, lose one worm, get a catch. Seven fish (one night-only, one legendary announced server-wide), a sunken purse (5 platinum), a pearl, old boots. A fishing log, two titles, and a weekly derby.

**A7-1. The purse makes fishing a safe gold source that a macro can run (Medium, estimate).**
- *For players:* a level-1 character standing in complete safety earns, by my estimate, 1,500 to 4,000 gold an hour from sunken purses, more than hunting pays until about level 12. The "anti-bot" second click is the easiest thing in the world for a macro.
- *Detail:* purse weight 2 of about 108 (1.85% per catch) times 500 gold is about 9 gold a catch; there is no delay between failed casts in the script, so the rate is limited only by the 2 to 6 second bite wait. **Unverified in game.**
- *Fix:* purse 2 platinum instead of 5, a 2-second delay after any cast, and count fishing gold in `tools/balance.py`.

**A7-2. Night fish follow the server's real clock (Low).** Secrets were moved to the game's own day and night, fishing was not (`fishing.lua` line 14 uses `os.date`). The Moonscale Eel only bites between 20:00 and 05:00 real time on your PC.

**A7-3. Parts of the fishing design are not built (Medium, doc versus game).** Message bottles that start secrets, hidden fishing spots as secrets, cooking fish into small buffs, and rare cosmetics are in `DESIGN.md` 8.2 and not in the catch table. No NPC buys fish or the pearl, so apart from the purse a catch is only food.

**A7-4. Other side activities, by the code:** hunting tasks from Taskmaster Rhen (one a day each), a 7-day login streak (100 to 1,000 gold), daily chests in each ground, an hourly "lucky climber" gift, Beacons, the Tower Quiz, outfit addon quests, crafting at four town crafters. I did not test them in play: **unverified beyond reading**.

### A8. Difficulty modes on Floor 1

| | Normal | Hardcore | Death Game |
|---|---|---|---|
| Experience | normal | +25% | +50% |
| Loot | normal | +15% (an extra roll) | +30% |
| Death below level 50 | costs nothing: no experience, no items (free blessings at each login) | 1.5x loss, blessings only halve it, extra item drops | character retired for good if it was a real monster death |
| Moving down | - | to Normal any time, costs the bonus experience | to Hardcore or Normal any time, costs the bonus experience |

(`lib/spirebound/difficulty.lua`, `scripts/spirebound/difficulty_events.lua`, `npc/registrar.lua` lines 53-55.)

**A8-1. Hardcore is free power until level 21 (High).**
- *For players:* a Hardcore character gets +25% experience and +15% loot, and until level 21 a death costs it nothing at all, because the engine's built-in starter blessing protects everyone that young. The smart choice is always Hardcore, then step down before it bites.
- *Detail:* the engine's adventurer's blessing gives every blessing to characters up to level 21 (Canary `data/libs/systems/blessing.lua` lines 220-230); our loss hook never runs then (comment at `difficulty_events.lua` lines 100-102), and the Hardcore item roll is zero with five or more blessings (`difficulty.lua` lines 180-186).
- *Fix:* Hardcore and Death Game characters do not get the starter blessing; Hardcore's loss applies from level 8.

**A8-2. A Death Game character can be made nearly unkillable (High).**
- *For players:* the rule "another player can never end you" has two side doors. (1) If the monster that kills you also hit another player who is not in your party, guild or household in the last 30 seconds, the death "does not count". Two friends who hunt side by side without partying both become immortal. (2) Inside a boss room, where PvP is open, a friend outside your party who hits you for 15% of your health once a minute does the same.
- *Detail:* `lib/spirebound/deathgame.lua` `judge` (lines 47-77): the "dragged in" rule and the "outside player did real damage" rule. Both exist to stop griefers, and both can be invoked on purpose.
- *Fix:* a death is only saved if the outside player was hostile to you (attacked you without being attacked, or is skulled), and the "dragged in" rule does not apply when you had also attacked that monster.

**A8-3. Normal has no sting at all below level 50 (your call).** A death costs the walk back. That was a deliberate fix today (Q77) and it matches the Registrar's promise, but it sits oddly with "challenge, not calm". It also means Floor 1 has no gold sink from blessings.

**A8-4. Are the perks worth the risk?** Hardcore: clearly yes, too much so (A8-1). Death Game: +50% is generous, and with A8-2 the risk is avoidable; fix A8-2 and it becomes a real, fair gamble. The Hardcore and Death Game titles and outfit rewards start at level 50 and beyond, so nothing cosmetic is earned on Floor 1.

### A9. The first two hours, class by class

All classes share the first 25 minutes:
1. **Login, Arrival Yard (0-5 min).** Guide Pell, a letter, a stone path. Clear.
2. **Old Granary (5-10 min).** Three Pen Rats, take a cheese, a gate opens. Rebuilt today; walked by a fresh character.
3. **Registrar (10-15 min).** Pick a path and a difficulty. *Risk:* the difficulty choice is made with one sentence of information each, and Hardcore is the hidden best answer (A8-1).
4. **The Proving (15-25 min).** A solo fight with Bramblejaw that cannot kill you. Lit as of today.
5. **Hearthgate and the Ratwarren, Toad Pond, Sproutling Glade (25-60 min, levels 3-9).** Fast and safe. With the engine bonuses a new player is level 9 in well under an hour.

Then the classes part:

- **Vanguard.** Waspgrass at 7, Captain Dorrow's weapon at 10, Boar Meadow 9-15. *Where it hurts:* Boar Meadow is small (A1-4); the reward sword is weaker than a 160-gold longsword until tier 3 (B4-1) and nothing tells the player; money is tight at levels 7-9 (0 to 6 gold in the playtest before the autoloot fix). By hour two the Vanguard is around level 14-16 and behind the others.
- **Ranger.** Same route, faster kills. *Where it hurts:* arrows are a constant cost; a spear Ranger gets no barracks weapon at all (only bow or crossbow are offered), so spear players cannot grow Mastery (B4-3).
- **Arcanist.** Waspgrass is its class ground (swarms). *Where it hurts:* 5 health per level; the wand is fine. The playtest's low boss damage was the test client's fault, not the class.
- **Mystic.** Heals from the start, the safest levelling. Its class ground (Thornsnap Hollow) comes at 14.

**Where players get lost, stuck, bored or quit (all classes):**
- **Levels 9-13: the experience rate drops from 10x to 4x at level 9** with no word of warning. It will feel like the game broke. A one-line message at level 9 would help.
- **Level 19-23: the solo road ends.** The Bandit Road, the Stair Key and the bosses all need a group, and the game says so only inside quest text. A solo player has Shard Fields and Reedmarsh and then nothing new until 23.
- **Level 20: promotion costs 20,000 gold.** At that level a player has earned perhaps 10,000 to 15,000 in total (estimate), so the headline feature of level 20 is out of reach for several hours.
- **Level 28+: one ground.** The Old Watchtower is the only content for 28 to 40 and it is a six-player ground. Solo players stall at the Quarry.
- **The boss:** see A4-1.

---

## 4. Items and drop tables

### 4.1 Every Floor 1 monster's loot

"Listed chance" is what the monster file says. The server runs loot rate 2 (`server/config-overrides.lua`), and the engine applies it by doubling every chance (Canary `getLootRandom`, `data/libs/functions/functions.lua` lines 68-76), so "real chance" is what players see. Coin amounts are 1 to the maximum, evenly. Hearth Shards, Beacon Embers and the rare weapons are not in these lists; a script adds them (4.3).

| Monster | Item | Listed chance | Real chance (2x loot rate) | Amount | Kills per drop | An NPC pays | Flag |
|---|---|---|---|---|---|---|---|
| Pen Rat | cheese | 100.0% | 100.0% | 1 | every kill | 2 |  |
| Pen Rat | gold coin | 80.0% | 100.0% | 1-3 | every kill | coin |  |
| Bramblejaw | gold coin | 100.0% | 100.0% | 1-40 | every kill | coin |  |
| Bramblejaw | health potion | 100.0% | 100.0% | 1-2 | every kill | - |  |
| Field Rat | gold coin | 70.0% | 100.0% | 1-4 | every kill | coin |  |
| Field Rat | cheese | 30.0% | 60.0% | 1 | 2 | 2 | junk that doubles a rat's value; not in the money model at 2x |
| Field Rat | mutated rat tail | 15.0% | 30.0% | 1 | 3 | 8 |  |
| Hopper Toad | gold coin | 70.0% | 100.0% | 1-6 | every kill | coin |  |
| Hopper Toad | poisonous slime | 12.0% | 24.0% | 1 | 4 | 10 |  |
| Sproutling | gold coin | 75.0% | 100.0% | 1-7 | every kill | coin |  |
| Sproutling | meat | 20.0% | 40.0% | 1 | 2 | 2 |  |
| Sproutling | sling herb | 14.0% | 28.0% | 1 | 4 | 10 |  |
| Meadow Wasp | gold coin | 70.0% | 100.0% | 1-8 | every kill | coin |  |
| Meadow Wasp | meat | 25.0% | 50.0% | 1 | 2 | 2 |  |
| Meadow Wasp | honeycomb | 16.0% | 32.0% | 1 | 3 | 10 |  |
| Meadow Wasp | compound eye | 2.5% | 5.0% | 1 | 20 | 25 |  |
| Bristle Boar | gold coin | 85.0% | 100.0% | 1-15 | every kill | coin |  |
| Bristle Boar | meat | 40.0% | 80.0% | 1-2 | 1 | 2 | meat: heavy (13 oz), inns pay 2 |
| Bristle Boar | ham | 15.0% | 30.0% | 1 | 3 | 4 |  |
| Bristle Boar | badger fur | 12.0% | 24.0% | 1 | 4 | 10 |  |
| Burrow Mole | gold coin | 90.0% | 100.0% | 1-26 | every kill | coin |  |
| Burrow Mole | meat | 40.0% | 80.0% | 1-2 | 1 | 2 | meat: heavy (13 oz), inns pay 2 |
| Burrow Mole | health potion | 4.0% | 8.0% | 1 | 12 | - |  |
| Burrow Mole | iron ore | 12.0% | 24.0% | 1 | 4 | 12 |  |
| Meadow Wolf | gold coin | 70.0% | 100.0% | 1-10 | every kill | coin |  |
| Meadow Wolf | wolf paw | 10.0% | 20.0% | 1 | 5 | 12 |  |
| Meadow Wolf | meat | 30.0% | 60.0% | 1 | 2 | 2 |  |
| Reed Snapper | gold coin | 100.0% | 100.0% | 1-30 | every kill | coin |  |
| Reed Snapper | platinum coin | 1.5% | 3.0% | 1 | 33 | coin |  |
| Reed Snapper | ham | 20.0% | 40.0% | 1 | 2 | 4 |  |
| Reed Snapper | health potion | 8.0% | 16.0% | 1 | 6 | - |  |
| Reed Snapper | turtle shell | 10.0% | 20.0% | 1 | 5 | 12 |  |
| Reed Snapper | bunch of reed | 18.0% | 36.0% | 1 | 3 | 8 |  |
| Thornsnap | gold coin | 85.0% | 100.0% | 1-22 | every kill | coin |  |
| Thornsnap | health potion | 5.0% | 10.0% | 1 | 10 | - |  |
| Thornsnap | spider silk | 13.0% | 26.0% | 1 | 4 | 12 |  |
| Field Shardling | gold coin | 85.0% | 100.0% | 1-20 | every kill | coin |  |
| Field Shardling | mana potion | 6.0% | 12.0% | 1 | 8 | - |  |
| Field Shardling | small amethyst | 6.0% | 12.0% | 1 | 8 | 200 | 200 gold gem at 12%: adds ~24 gold a kill, most of this monster's value |
| Road Bandit | gold coin | 90.0% | 100.0% | 1-60 | every kill | coin |  |
| Road Bandit | platinum coin | 6.0% | 12.0% | 1 | 8 | coin |  |
| Road Bandit | short sword | 5.0% | 10.0% | 1 | 10 | 10 |  |
| Road Bandit | leather armor | 4.0% | 8.0% | 1 | 12 | 5 |  |
| Road Bandit | mace | 5.0% | 10.0% | 1 | 10 | 30 |  |
| Road Bandit | rope belt | 13.0% | 26.0% | 1 | 4 | 10 |  |
| Road Bandit | brown piece of cloth | 6.0% | 12.0% | 1 | 8 | 12 |  |
| Bandit Crossbowman | gold coin | 90.0% | 100.0% | 1-55 | every kill | coin |  |
| Bandit Crossbowman | platinum coin | 5.0% | 10.0% | 1 | 10 | coin |  |
| Bandit Crossbowman | bolt | 30.0% | 60.0% | 1-10 | 2 | - |  |
| Bandit Crossbowman | crossbow | 2.5% | 5.0% | 1 | 20 | 120 |  |
| Bandit Crossbowman | rope belt | 10.0% | 20.0% | 1 | 5 | 10 |  |
| Hedge Hexer | gold coin | 90.0% | 100.0% | 1-55 | every kill | coin |  |
| Hedge Hexer | platinum coin | 6.0% | 12.0% | 1 | 8 | coin |  |
| Hedge Hexer | strong health potion | 12.0% | 24.0% | 1 | 4 | - |  |
| Hedge Hexer | spider silk | 8.0% | 16.0% | 1 | 6 | 12 |  |
| Hedge Hexer | sling herb | 15.0% | 30.0% | 1 | 3 | 10 |  |
| Ruin Archer | gold coin | 100.0% | 100.0% | 1-75 | every kill | coin |  |
| Ruin Archer | platinum coin | 6.0% | 12.0% | 1 | 8 | coin |  |
| Ruin Archer | arrow | 30.0% | 60.0% | 1-15 | 2 | - |  |
| Ruin Archer | bow | 3.0% | 6.0% | 1 | 17 | 100 |  |
| Ruin Archer | rope belt | 8.0% | 16.0% | 1 | 6 | 10 |  |
| Ruin Sentinel | gold coin | 100.0% | 100.0% | 1-85 | every kill | coin |  |
| Ruin Sentinel | platinum coin | 6.0% | 12.0% | 1 | 8 | coin |  |
| Ruin Sentinel | chain helmet | 6.0% | 12.0% | 1 | 8 | 17 |  |
| Ruin Sentinel | axe | 5.0% | 10.0% | 1 | 10 | 7 |  |
| Ruin Sentinel | iron ore | 8.0% | 16.0% | 1 | 6 | 12 |  |
| Stonehorn Ram | gold coin | 100.0% | 100.0% | 1-100 | every kill | coin |  |
| Stonehorn Ram | platinum coin | 30.0% | 60.0% | 1-2 | 2 | coin |  |
| Stonehorn Ram | health potion | 20.0% | 40.0% | 1-3 | 2 | - |  |
| Stonehorn Ram | mana potion | 20.0% | 40.0% | 1-3 | 2 | - |  |
| Stonehorn Ram | iron ore | 10.0% | 20.0% | 1 | 5 | 12 |  |
| Grey Alpha | gold coin | 100.0% | 100.0% | 1-40 | every kill | coin |  |
| Grey Alpha | wolf paw | 50.0% | 100.0% | 1-2 | every kill | 12 |  |
| Grey Alpha | health potion | 8.0% | 16.0% | 1 | 6 | - |  |
| Grey Alpha | wolf tooth chain | 6.0% | 12.0% | 1 | 8 | 100 |  |
| Bandit Captain | gold coin | 100.0% | 100.0% | 1-80 | every kill | coin |  |
| Bandit Captain | platinum coin | 15.0% | 30.0% | 1 | 3 | coin |  |
| Bandit Captain | brass armor | 4.0% | 8.0% | 1 | 12 | 150 | same item the Armorer sells for 450; fine |
| Bandit Captain | chain helmet | 5.0% | 10.0% | 1 | 10 | 17 |  |
| Bandit Captain | health potion | 15.0% | 30.0% | 1-2 | 3 | - |  |
| Bandit Captain | white piece of cloth | 12.0% | 24.0% | 1 | 4 | 20 |  |
| Old Bristleback | gold coin | 100.0% | 100.0% | 1-60 | every kill | coin |  |
| Old Bristleback | platinum coin | 25.0% | 50.0% | 1 | 2 | coin |  |
| Old Bristleback | meat | 60.0% | 100.0% | 1-3 | every kill | 2 |  |
| Old Bristleback | badger fur | 50.0% | 100.0% | 1-2 | every kill | 10 |  |
| Old Bristleback | health potion | 30.0% | 60.0% | 1-2 | 2 | - |  |
| Moonhowl | gold coin | 100.0% | 100.0% | 1-50 | every kill | coin |  |
| Moonhowl | platinum coin | 25.0% | 50.0% | 1 | 2 | coin |  |
| Moonhowl | wolf paw | 60.0% | 100.0% | 1-3 | every kill | 12 |  |
| Moonhowl | health potion | 30.0% | 60.0% | 1-2 | 2 | - |  |
| Mossback Snapper | gold coin | 100.0% | 100.0% | 1-90 | every kill | coin |  |
| Mossback Snapper | platinum coin | 40.0% | 80.0% | 1-2 | 1 | coin |  |
| Mossback Snapper | ham | 50.0% | 100.0% | 1-2 | every kill | 4 |  |
| Mossback Snapper | turtle shell | 40.0% | 80.0% | 1-2 | 1 | 12 |  |
| Mossback Snapper | strong health potion | 25.0% | 50.0% | 1 | 2 | - |  |
| Blackthorn | gold coin | 100.0% | 100.0% | 1-80 | every kill | coin |  |
| Blackthorn | platinum coin | 30.0% | 60.0% | 1 | 2 | coin |  |
| Blackthorn | spider silk | 60.0% | 100.0% | 1-3 | every kill | 12 |  |
| Blackthorn | strong health potion | 25.0% | 50.0% | 1 | 2 | - |  |
| Prism Shardling | gold coin | 100.0% | 100.0% | 1-85 | every kill | coin |  |
| Prism Shardling | platinum coin | 40.0% | 80.0% | 1-2 | 1 | coin |  |
| Prism Shardling | mana potion | 30.0% | 60.0% | 1-2 | 2 | - |  |
| Prism Shardling | small amethyst | 30.0% | 60.0% | 1-2 | 2 | 200 | up to 2 gems 60% of the time |
| Granite Warden | gold coin | 100.0% | 100.0% | 1-95 | every kill | coin |  |
| Granite Warden | platinum coin | 40.0% | 80.0% | 1-2 | 1 | coin |  |
| Granite Warden | chain helmet | 20.0% | 40.0% | 1 | 2 | 17 |  |
| Granite Warden | iron ore | 40.0% | 80.0% | 1-2 | 1 | 12 |  |
| Granite Warden | strong health potion | 25.0% | 50.0% | 1 | 2 | - |  |
| Old Tusk | gold coin | 100.0% | 100.0% | 1-100 | every kill | coin |  |
| Old Tusk | platinum coin | 100.0% | 100.0% | 1-5 | every kill | coin |  |
| Old Tusk | ham | 100.0% | 100.0% | 1-5 | every kill | 4 |  |
| Old Tusk | strong health potion | 50.0% | 100.0% | 1-2 | every kill | - |  |
| Hollowfang | gold coin | 100.0% | 100.0% | 1-100 | every kill | coin |  |
| Hollowfang | platinum coin | 100.0% | 100.0% | 1-4 | every kill | coin |  |
| Hollowfang | wolf paw | 100.0% | 100.0% | 1-3 | every kill | 12 |  |
| Hollowfang | strong health potion | 40.0% | 80.0% | 1-2 | 1 | - |  |
| Briar Mother | gold coin | 100.0% | 100.0% | 1-100 | every kill | coin |  |
| Briar Mother | platinum coin | 100.0% | 100.0% | 1-6 | every kill | coin |  |
| Briar Mother | spider silk | 100.0% | 100.0% | 1-3 | every kill | 12 |  |
| Briar Mother | strong health potion | 50.0% | 100.0% | 1-2 | every kill | - |  |
| Drowned Warden | gold coin | 100.0% | 100.0% | 1-100 | every kill | coin |  |
| Drowned Warden | platinum coin | 100.0% | 100.0% | 1-10 | every kill | coin |  |
| Drowned Warden | chain helmet | 30.0% | 60.0% | 1 | 2 | 17 |  |
| Drowned Warden | great health potion | 50.0% | 100.0% | 1-2 | every kill | - |  |
| Gate Hound | gold coin | 100.0% | 100.0% | 1-100 | every kill | coin |  |
| Gate Hound | platinum coin | 100.0% | 100.0% | 1-10 | every kill | coin |  |
| Gate Hound | health potion | 100.0% | 100.0% | 1-5 | every kill | - |  |
| Axe-Lord of the Stair | gold coin | 100.0% | 100.0% | 1-100 | every kill | coin |  |
| Axe-Lord of the Stair | platinum coin | 100.0% | 100.0% | 1-40 | every kill | coin | one body, one looter: only the top damage dealer's bag gets this |
| Axe-Lord of the Stair | health potion | 100.0% | 100.0% | 1-10 | every kill | - |  |
| Axe-Lord of the Stair | mana potion | 100.0% | 100.0% | 1-10 | every kill | - |  |
| Black Crawler | gold coin | 100.0% | 100.0% | 1-70 | every kill | coin |  |
| Black Crawler | platinum coin | 10.0% | 20.0% | 1 | 5 | coin |  |
| Black Crawler | small sapphire | 2.0% | 4.0% | 1 | 25 | 250 |  |
| Mire Toad | gold coin | 100.0% | 100.0% | 1-60 | every kill | coin |  |
| Mire Toad | strong health potion | 8.0% | 16.0% | 1 | 6 | - |  |
| Mire Toad | small emerald | 2.0% | 4.0% | 1 | 25 | 250 |  |
| Vault Rat | gold coin | 100.0% | 100.0% | 1-80 | every kill | coin |  |
| Vault Rat | platinum coin | 20.0% | 40.0% | 1 | 2 | coin |  |
| Chain Ghoul | gold coin | 100.0% | 100.0% | 1-100 | every kill | coin |  |
| Chain Ghoul | platinum coin | 30.0% | 60.0% | 1-2 | 2 | coin |  |
| Chain Ghoul | plate armor | 1.5% | 3.0% | 1 | 33 | 400 |  |
| Drain Matron | gold coin | 100.0% | 100.0% | 1-100 | every kill | coin |  |
| Drain Matron | platinum coin | 100.0% | 100.0% | 1-15 | every kill | coin |  |
| Drain Matron | knight armor | 20.0% | 40.0% | 1 | 2 | 5000 | 5,000 gold item 40% of the time, every 30 min |
| Iron Shade | gold coin | 100.0% | 100.0% | 1-100 | every kill | coin |  |
| Iron Shade | platinum coin | 50.0% | 100.0% | 1-3 | every kill | coin |  |
| Iron Shade | crown armor | 1.2% | 2.4% | 1 | 42 | 12000 | 12,000 gold item at 2.4%: 16 spawns |
| Trap Mimic | gold coin | 100.0% | 100.0% | 1-100 | every kill | coin |  |
| Trap Mimic | platinum coin | 60.0% | 100.0% | 1-4 | every kill | coin |  |
| Trap Mimic | small diamond | 4.0% | 8.0% | 1 | 12 | 300 |  |
| Keep Warden | gold coin | 100.0% | 100.0% | 1-100 | every kill | coin |  |
| Keep Warden | platinum coin | 80.0% | 100.0% | 1-6 | every kill | coin |  |
| Keep Warden | golden legs | 1.5% | 3.0% | 1 | 33 | 30000 | 30,000 gold item at 3%: 16 spawns |
| Deep Sentinel | gold coin | 100.0% | 100.0% | 1-100 | every kill | coin |  |
| Deep Sentinel | platinum coin | 100.0% | 100.0% | 1-10 | every kill | coin |  |
| Deep Sentinel | golden armor | 1.5% | 3.0% | 1 | 33 | 20000 | 20,000 gold item from a monster with 8 spawns: deep-wing only |
| Vault Wraith | gold coin | 100.0% | 100.0% | 1-100 | every kill | coin |  |
| Vault Wraith | platinum coin | 100.0% | 100.0% | 1-8 | every kill | coin |  |
| Vault Wraith | royal helmet | 1.5% | 3.0% | 1 | 33 | 30000 | 30,000 gold item at 3% |
| Vault Warden | gold coin | 100.0% | 100.0% | 1-100 | every kill | coin |  |
| Vault Warden | platinum coin | 100.0% | 100.0% | 1-50 | every kill | coin |  |
| Vault Warden | magic plate armor | 8.0% | 16.0% | 1 | 6 | 90000 | 90,000 gold item at 16% |
| The Underkeeper | gold coin | 100.0% | 100.0% | 1-100 | every kill | coin |  |
| The Underkeeper | platinum coin | 100.0% | 100.0% | 1-100 | every kill | coin |  |
| The Underkeeper | magic plate armor | 30.0% | 60.0% | 1 | 2 | 90000 | 90,000 gold item at 60%: late-season only, but a huge faucet |

### 4.2 Gold per kill (real, at loot rate 2)

| Monster | Coins per kill | Loot sold to NPCs per kill | Total per kill |
|---|---|---|---|
| Pen Rat | 2.0 | 2.0 | 4.0 |
| Bramblejaw | 20.5 | 0.0 | 20.5 |
| Field Rat | 2.5 | 3.6 | 6.1 |
| Hopper Toad | 3.5 | 2.4 | 5.9 |
| Sproutling | 4.0 | 3.6 | 7.6 |
| Meadow Wasp | 4.5 | 5.5 | 9.9 |
| Bristle Boar | 8.0 | 6.0 | 14.0 |
| Burrow Mole | 13.5 | 5.3 | 18.8 |
| Meadow Wolf | 5.5 | 3.6 | 9.1 |
| Reed Snapper | 18.5 | 6.9 | 25.4 |
| Thornsnap | 11.5 | 3.1 | 14.6 |
| Field Shardling | 10.5 | 24.0 | 34.5 |
| Road Bandit | 42.5 | 8.4 | 50.9 |
| Bandit Crossbowman | 38.0 | 8.0 | 46.0 |
| Hedge Hexer | 40.0 | 4.9 | 44.9 |
| Ruin Archer | 50.0 | 7.6 | 57.6 |
| Ruin Sentinel | 55.0 | 4.7 | 59.7 |
| Stonehorn Ram | 140.5 | 2.4 | 142.9 |
| Grey Alpha | 20.5 | 30.0 | 50.5 |
| Bandit Captain | 70.5 | 18.5 | 89.0 |
| Old Bristleback | 80.5 | 19.0 | 99.5 |
| Moonhowl | 75.5 | 24.0 | 99.5 |
| Mossback Snapper | 165.5 | 20.4 | 185.9 |
| Blackthorn | 100.5 | 24.0 | 124.5 |
| Prism Shardling | 163.0 | 180.0 | 343.0 |
| Granite Warden | 168.0 | 21.2 | 189.2 |
| Old Tusk | 350.5 | 12.0 | 362.5 |
| Hollowfang | 300.5 | 24.0 | 324.5 |
| Briar Mother | 400.5 | 24.0 | 424.5 |
| Drowned Warden | 600.5 | 10.2 | 610.7 |
| Gate Hound | 600.5 | 0.0 | 600.5 |
| Axe-Lord of the Stair | 2100.5 | 0.0 | 2100.5 |
| Black Crawler | 55.5 | 10.0 | 65.5 |
| Mire Toad | 30.5 | 10.0 | 40.5 |
| Vault Rat | 80.5 | 0.0 | 80.5 |
| Chain Ghoul | 140.5 | 12.0 | 152.5 |
| Drain Matron | 850.5 | 2000.0 | 2850.5 |
| Iron Shade | 250.5 | 288.0 | 538.5 |
| Trap Mimic | 300.5 | 24.0 | 324.5 |
| Keep Warden | 400.5 | 900.0 | 1300.5 |
| Deep Sentinel | 600.5 | 600.0 | 1200.5 |
| Vault Wraith | 500.5 | 900.0 | 1400.5 |
| Vault Warden | 2600.5 | 14400.0 | 17000.5 |
| The Underkeeper | 5100.5 | 54000.0 | 59100.5 |

### 4.3 Drops added by script

| Drop | From | Chance per kill | Kills on average | Guaranteed by | Flag |
|---|---|---|---|---|---|
| rough Hearth Shard | every hunting-ground monster | 0.555% | 180 | 540 kills | Fine, but 15 come free from chests, so the drop hardly matters |
| cut Hearth Shard | harder grounds (wolves, snappers, thornsnaps, shardlings, bandits, ruin guards) and elites | 0.469% | 213 | 639 kills | Fine |
| flawless Hearth Shard | elites and the Stonehorn Ram | 3.52% | 28 | 85 kills | **Too easy from Rams:** 42 Rams returning every 60-75 s |
| Rare weapon (one of four, random class) | Bandit Captain, Grey Alpha, Ruin Sentinel, Stonehorn Ram | 3% | 33 for any, about 133 for your own class | none | **Too common and pointless:** see B4-2 |
| 3 cut Hearth Shards | Gate Hound, first credited kill only | 100% once | - | - | Fine |
| Weapon awakening | Axe-Lord, each credited fighter | 100% once | - | waits for you if you died | Fine |

(`lib/spirebound/gear_data.lua` `SHARD_CHANCE`, `DROP_CHANCE`, `dropFrom`; `scripts/spirebound/gear.lua` lines 14-45.) The loot rate, Hardcore's bonus and Beacons do not change these; the cavebot removes half of them.

### 4.4 Custom items

There are almost no new items in the game. Every weapon, armour piece and material is a stock Tibia item; Spirebound adds a name, a description and hidden values on top. The complete list of things that are ours:

**Weapons** (`lib/spirebound/gear_data.lua`; no level needed; only the named class gets the bonus; tier, familiarity and awakening stay on the item and it can be traded)

| Name (awakened name) | Class | Built on (attack) | How you get it | Bonus at tier 0 | Flag |
|---|---|---|---|---|---|
| Hearthguard Sword (Stairlord's Edge) | Vanguard | sword (14) | Dorrow, level 10 | +10% damage | Weaker than a shop longsword until tier 3 |
| Hearthguard Axe (Stairlord's Cleaver) | Vanguard | axe (12) | Dorrow, level 10 | +10% | **Trap:** 25% weaker than the Mace |
| Hearthguard Mace (Stairlord's Maul) | Vanguard | mace (16) | Dorrow, level 10 | +10% | The right choice, and nothing says so |
| Trailwarden Bow (Stair-Iron Longbow) | Ranger | bow | Dorrow, level 10 | +10% | Fine |
| Trailwarden Crossbow (Stair-Iron Crossbow) | Ranger | crossbow | Dorrow, level 10 | +10% | Range 5 against the bow's 6 |
| Wand of Hearth Sparks (Wand of the Long Stair) | Arcanist | wand of vortex | Dorrow, level 10 | +10% | Fine |
| Reedroot Rod (Rod of the Long Stair) | Mystic | snakebite rod | Dorrow, level 10 | +10% | Fine |
| Briarguard Sabre | Vanguard | sabre (12) | rare drop | +10%, "2% life leech" | **Perk not built; base weaker than the main sword** |
| Copsewood Bow | Ranger | bow | rare drop | +10%, "3% critical" | **Perk not built** |
| Wand of Ember Script | Arcanist | wand of vortex | rare drop | +10%, "2% mana leech" | **Perk not built** |
| Thornward Rod | Mystic | snakebite rod | rare drop | +10%, "4% healing" | **Perk not built** |

**Armour** (reward of Iron for the Stair 2 of 2)

| Name | Class | Built on | Armour at tier 0 / tier 5 | Flag |
|---|---|---|---|---|
| Hearthward Mail | Vanguard | brass armor (8) | 10 / 15 | Fine |
| Trailwarden Greaves | Ranger | brass legs (5) | 7 / 12 | Fine |
| Millward Mantle | Arcanist | leather armor (4) | 7 / 12 | Fine |
| Thornward Robe | Mystic | leather armor (4) | 7 / 12 | Fine |

**Donation-shop starter set** (shop is switched off): Climber's Sword / Bow / Wand / Rod (+8% damage, cannot be upgraded) and Climber's Mail / Greaves / Mantle / Robe (+1 armour).

**Renamed stock items** (`data/item_renames.json`; every one uses a base Tibia picture as a placeholder)

| Item id | Stock item underneath | Name players see | Note |
|---|---|---|---|
| 16124 | blue crystal splinter | rough Hearth Shard | Dropped by every monster on Floor 1's hunting grounds. |
| 16119 | blue crystal shard | cut Hearth Shard | Dropped on Floor 1's harder grounds: Wolf Copse, Reedmarsh, Thornsnap Hollow, Shard Fields, the Bandit Road, t |
| 16120 | violet crystal shard | flawless Hearth Shard | Dropped by Floor 1's elites (Grey Alpha, Bandit Captain), in the Old Watchtower and on group grounds. |
| 16122 | green crystal splinter | rough Highland Shard | Dropped by every monster on Floor 2's hunting grounds. |
| 16121 | green crystal shard | cut Highland Shard | Dropped on Floor 2's harder grounds and caves. |
| 16127 | green crystal fragment | flawless Highland Shard | Dropped by Floor 2's elites and on its group grounds. |
| 28650 | sealed scroll | Mastery Respec Scroll | Use it to choose your style again: your Mastery points stay. Sold only in the shop; one use. |
| 5805 | golden goblet | Chronicle Cup | Awarded for finishing a season's Spire Chronicle. It looks best on a shelf in your house. |
| 9636 | fiery heart | Beacon Ember | Light a fire bowl of a town's Beacon with it: +5% experience and loot for everyone on that floor for an hour.  |
| 13865 | dead crawler | broken stone guardian | Carved stone and a cracked spear, all that is left of a guardian of the old ruins. |
| 13866 | dead crawler | broken stone guardian | Carved stone and a cracked spear, all that is left of a guardian of the old ruins. |
| 13867 | dead crawler | broken stone guardian | Carved stone and a cracked spear, all that is left of a guardian of the old ruins. |
| 13868 | dead crawler | broken stone guardian | Carved stone and a cracked spear, all that is left of a guardian of the old ruins. |
| 12340 | dead midnight panther | fallen underkeeper | Old bones, a cage-helm and a cold lantern, tangled in the chain he dragged. |
| 12337 | dead midnight panther | fallen underkeeper | Old bones, a cage-helm and a cold lantern, tangled in the chain he dragged. |
| 12338 | dead midnight panther | fallen underkeeper | Old bones, a cage-helm and a cold lantern, tangled in the chain he dragged. |
| 12339 | dead midnight panther | fallen underkeeper | Old bones, a cage-helm and a cold lantern, tangled in the chain he dragged. |
| 10430 | dead terramite | faded vault wraith | An empty purple shroud beside the strongbox it guarded. |
| 10431 | dead terramite | faded vault wraith | An empty purple shroud beside the strongbox it guarded. |
| 10432 | dead terramite | faded vault wraith | An empty purple shroud beside the strongbox it guarded. |
| 10433 | dead terramite | faded vault wraith | An empty purple shroud beside the strongbox it guarded. |
| 9001 | dead nightstalker | slain gate hound | Three heads on the ground, each still in its spiked iron collar. |
| 9002 | dead nightstalker | slain gate hound | Three heads on the ground, each still in its spiked iron collar. |
| 9003 | dead nightstalker | slain gate hound | Three heads on the ground, each still in its spiked iron collar. |
| 9004 | dead nightstalker | slain gate hound | Three heads on the ground, each still in its spiked iron collar. |

**Everything else is a stock item under its stock name:** the shops sell "brass armor", "spike sword", "wand of vortex", "snakebite rod"; monsters drop "chain helmet", "plate armor", "crown armor", "golden armor", "magic plate armor", "royal helmet". The fish are stock fish items shown under our names only in the catch message. Prices for all of them are in 6.3.

**Flags for this section**
- **Placeholder art everywhere.** No item has its own sprite; shards are Tibia's crystal splinters and shards, the respec scroll is a "sealed scroll". Expected at this stage, but it is every item.
- **Stock names against your naming rule.** `CLAUDE.md` says no CipSoft names a player can see. `tools/check_names.py` passes with zero hits because item names are not on its list. Whether "magic plate armor" or "wand of vortex" counts is your decision (Open questions).
- **Bag view shows the stock name and picture.** A Hearthguard Sword in a backpack looks like "sword"; the real name shows only on Look (hand-off P2-8, left as is).

---

## 5. Gear progression and gear systems (Part B)

### 5.1 The path, class by class

All four classes follow the same steps: starter kit at the Registrar, shop gear with the first gold, the barracks weapon from Captain Dorrow at level 10, one free tier from "Tempered in the Field" at level 12, the class armour from Iron for the Stair (about level 19-23), tiers bought with shards and gold at Garrick, and the awakening from the Axe-Lord.

| Step | Vanguard | Ranger | Arcanist | Mystic |
|---|---|---|---|---|
| Start | path weapon from the kit, 5 potions of each kind, ham | same | same | same |
| Shop, levels 1-10 | longsword 160, brass shield 65, studded or brass armour 90-450 | bow 400, arrows 1 each | wand of vortex 500 | snakebite rod 500 |
| Level 10 | Hearthguard Sword, Axe or Mace | Trailwarden Bow or Crossbow | Wand of Hearth Sparks | Reedroot Rod |
| About level 20 | Hearthward Mail (armour 10) | Trailwarden Greaves (7) | Millward Mantle (7) | Thornward Robe (7) |
| Tiers 1-5 | +4% damage each; armour +1 each | same | same | same |
| Familiarity 0-10 | +1.5% each, from kills with it in hand | same | same | same |
| Awakening | +10% | same | same | same |
| Best possible on Floor 1 | +61% damage, armour 15 | +61%, armour 12 | +61%, armour 12 | +61%, armour 12 |

**Are there clear upgrades?** For Rangers, Arcanists and Mystics, yes: each step is plainly better than the last. For Vanguards, no (B4-1).

**Does one item make the rest pointless?** Yes, in two directions: the shop's spike sword makes the whole Vanguard weapon path pointless for damage, and the main barracks weapon makes the rare-drop weapon pointless for everyone.

**Does each class get a fair share of drops?** The scripted drops are even (the rare weapon picks a class at random; shards are classless). Ordinary loot leans to the Vanguard and Ranger: swords, maces, axes, helmets, brass armour, bows, crossbows, arrows and bolts drop; no wand, rod or robe drops anywhere on Floor 1. Mages get mana potions and gems to sell instead. Not unfair in gold, but mages never get the "I found a weapon" moment.

### 5.2 Gear systems that exist

**B4-0. The weapon damage bonus may not be reaching most hits at all (High, needs a 5-minute test).**
- *For players:* tiers, familiarity, the awakening, style passives and trophies are all meant to raise the damage you deal. There is strong evidence in the code that the raise is skipped for most hits, so players would pay shards and gold for a number on the item that changes little.
- *Detail:* the bonus is applied in one place, `SpireProgress.onDealt` (`lib/spirebound/progress.lua` lines 80-95), which begins "if the amount is zero or less, return it unchanged". But the engine hands damage to that hook as a negative number for most hits: the boss script says so in its own comment ("the engine hands most hits over as negative numbers and some spells as positive ones", `scripts/spirebound/bosses_floor1.lua` lines 145-147, a bug fixed there today), and the calling code says the same ("Damage can arrive as negative numbers here", `scripts/spirebound/spells.lua` line 1440). The floor-perk hook sits beside it and may share the problem. The only automated tests feed it +100 (`tests/test_progression.lua` lines 105-106). I could not run the game to confirm: **unverified in play**.
- *Fix:* work on the size of the hit and keep its sign, as the boss script now does; add a test that hits a real monster with and without a tier-5 weapon and compares the damage.

**B4-1. Vanguard reward weapons are out-damaged by shop swords (High).**
- *For players:* the weapon the game tells a Vanguard to hold, upgrade and awaken deals less damage than swords Garrick sells in the same room. Holding the better sword stops Mastery and familiarity from growing, so the player must choose between hitting hard now and growing later, and the game explains none of it.
- *Detail:* melee and sword-skill damage scale with the weapon's attack value (`scripts/spirebound/sword_skills.lua` line 30; the engine's own melee formula). The Spirebound bonus is a multiplier on top (`lib/spirebound/gear.lua` `power`, lines 53-63): Floor 1 gives 1.10 at tier 0, 1.30 at tier 5, times 1.15 at full familiarity, plus 0.10 awakened = 1.61 at the very most. On an attack-14 sword that is the same as attack 15.4 at tier 0 and 22.5 at the maximum. Garrick sells a longsword (attack 17) for 160 gold and a spike sword (attack 24, defence 21 against 12) for 8,000 (`npc/hearthgate_weaponsmith.lua`). The Axe (attack 12) is 25% behind the Mace (attack 16) for identical cost.
- *Fix:* give the three barracks weapons one attack value of their own, set on the item like the armour bonus already is (suggest attack 20, +1 per tier, defence 15), and take the spike sword out of Floor 1's shop.

**B4-2. Rare-drop weapons are common, and their special bonuses do not exist (High).**
- *For players:* about one "rare" weapon falls every 33 kills in the Quarry or the Watchtower. Its promised life leech, critical hit, mana leech or healing bonus does nothing. It is a second copy of the main weapon with zero familiarity, and for Vanguards a weaker base.
- *Detail:* `perk` and `perkValue` are written in `gear_data.lua` (lines 20-23) and copied in `gear.lua` line 11; a search of every script finds no other use. The 3% chance applies to Ruin Sentinels (48 spawns) and Stonehorn Rams (42 spawns) as well as elites (`gear_data.lua` `dropFrom`), with no pity counter and no class preference.
- *Fix:* build the four perks, drop only from the two elites and the Ram at 0.5%, and favour the looter's own class.

**B4-3. Spear Rangers have no barracks weapon (Medium).** `DESIGN.md` 5.2 gives Rangers bow, crossbow and spear, and the economy model has a "Ranger (spears)" row, but Dorrow offers only bow and crossbow (`gear_data.lua` lines 16-17). Mastery only grows while a class barracks weapon is held (`lib/spirebound/progress.lua` `countsPure`), so a spear Ranger never grows.

**B4-4. Tiers (works; balance fine).** Five tiers. Each costs 3 shards of a grade plus gold: 500, 1,000 (rough), 2,000, 3,500 (cut), 6,000 (flawless): 13,000 gold and 15 shards per item, weapon and armour separately. No failure chance, so no failure-rate abuse. Gold is taken first, then shards, after both were checked (`gear.lua` lines 236-272): no dupe found. Shards are counted anywhere in the bags.

**B4-5. Rough shards are handed out, not earned (Low).** Fifteen first-time chests give one rough shard each; a weapon needs six. The 180-kill drop rate is almost irrelevant. Fine if intended; otherwise drop the shard from half the chests.

**B4-6. Familiarity (works).** 0 to 10, from kills with the weapon in hand, stored on the item, +1.5% damage a level. Party kills share it. Reforging resets it. No exploit found. Pen Rats do not count.

**B4-7. Reforge (one bug, Low).** Garrick remakes a weapon into another family of the class for 1,000 gold, keeping tier and awakening. The fee is taken before the new weapon is created; if creation fails the code answers "You have no room" and keeps the gold (`gear.lua` lines 289-296). The "replace" path was given a refund today; this one was not. In practice creation almost never fails since today's Store Inbox fallback.

**B4-8. Awakening (works).** Once per weapon, to every credited fighter, held for fighters who died before the boss did. A fighter not carrying a Floor 1 weapon at the kill gets a message and nothing, but can earn it on any later credited kill (`gear.lua` lines 449-473). No exploit found.

**B4-9. Gear can be traded with everything on it, to any level (Medium, your call).** Tier, familiarity and awakening travel with the item, and there is no level requirement. A new level-1 Vanguard can be handed a maxed Stairlord's weapon (+61% damage against monsters). Good for a player market; also what gold sellers sell. The bonus applies only against monsters (`scripts/spirebound/spells.lua` line 1485), so it is not a PvP problem.

**B4-10. Style tree and Mastery (exists; not reviewed in depth).** Thirty levels of permanent passive bonuses with two locked choices (`gear_data.lua` `style`, `PASSIVES`, `STYLE_POINTS`). The first ten levels cost 22,857 points each, which is Floor 1 territory. Balance **unverified**. Respecs are sold only in the donation shop (your decision).

**B4-11. Systems that do not exist.** No rarity colours, no sets or set bonuses, no sockets, no durability or repairs (roadmap R10b lists repairs as a missing gold sink), no enchanting or imbuing (the engine's own systems are off). Crafting makes supplies and outfit pieces, not gear (by design since 2026-11-23). **Dual wielding (Twin Fang)** is a Floor 8 secret limited to three characters a season; a script and a warden monster exist, but nothing of it is reachable on Floor 1 and I did not review it.

---

## 6. Economy check

### 6.1 Gold per hour

The project's own table (`ECONOMY.md`) uses the listed drop chances. The game doubles them. The right-hand column redoes the sum with the real chances and the model's own kill speeds for a Vanguard, assuming the player sells every drop to Trader Osric.

| Ground | Levels | Kills an hour (model) | `ECONOMY.md` gold an hour | Real gold an hour (my estimate) | Difference |
|---|---|---|---|---|---|
| The Ratwarren | 1-4 | 300 | 1,065 | about 1,830 | +72% |
| Boar Meadow | 9-15 | 264 | 2,590 | about 3,700 | +43% |
| Burrow Hills | 11-16 | 232 | 3,367 | about 4,360 | +30% |
| Wolf Copse | 12-18 | 277 | 2,026 | about 2,520 | +24% |
| Reedmarsh | 14-19 | 232 | 4,747 | about 5,890 | +24% |
| Thornsnap Hollow | 14-20 | 252 | 2,795 | about 3,680 | +32% |
| Shard Fields | 17-24 | 277 | 5,795 | about 9,560 | +65% |
| The Bandit Road | 19-27 | 248 | 9,711 | about 12,620 | +30% |
| The Old Quarry | 23-30 | 233 | 10,000 | about 13,650 | +37% |
| Old Watchtower (each of six) | 28-40 | about 65 each | 6,157 | about 9,500 | +54% |

**E-1. The economy model ignores the loot rate (High).** `tools/gen_economy.py` `drop_value` (lines 88-102) multiplies listed chance by average amount and never by the loot rate. Every check that reads "All checks pass" (supplies under 60% of income, house affordability, task payouts) was run on numbers that are too low. Real incomes are comfortable, so nothing is broken for players, but houses and promotion arrive sooner than planned and the "money is tight early" feeling from the playtest came from autoloot being off, not from low drops. *Fix:* put the rate into the model, rerun, then decide whether to trim drops or keep the richer game.

### 6.2 Where gold comes from and where it goes

**Faucets (Floor 1):** monster coins and sold loot (table above); one-time quests (about 17,000 a character); secrets sold to Vesper (33,000 for the whole world, once a season) plus about 5,000 in find rewards; first-time chests (about 34,500 a character); daily chests (up to about 4,600 a day if you walk to all 15); login streak (100 to 1,000 a day); hunting tasks; the Underkeep strongbox (800 to 1,500 a day); the hourly lucky climber (up to 5,000); fishing purses (A7-1).

**Sinks (Floor 1):** potions (health 45-50, mana 50-56, strong 93-115), arrows and bolts (1 and 2 each), blank runes, promotion (20,000 once), gear tiers (13,000 per item, 26,000 for weapon and armour), reforge 1,000, lost weapon 2,000, crafting fees (50 to 2,000), houses (1,000 a tile, rent 500 to 2,800 a week), furniture kits (400 to 1,500), the 250,000 exercise dummy, temple scrolls (300), coach fares.

**E-2. Sinks are thin for a careful player (Medium).** By the model, supplies eat 10 to 45% of income. Blessings cost nothing below level 50 on Normal (they are free), there are no repairs, and death costs nothing. A level-30 player who has bought promotion and five tiers on two items has spent about 46,000 and has no further sink on Floor 1 except a house. Over a five-month season that is inflation risk, though most of it will show on later floors. *Fix:* build one of the missing sinks from roadmap R10b before public launch (repairs is the classic one).

**E-3. Daily rewards are per character and extra characters are allowed (Low).** Login streak, daily chests, the strongbox and tasks all pay each character. A player with five alts collects them five times. Small sums, but they add up across a season. *Fix:* make the login streak and strongbox once per account.

### 6.3 Shop prices against drop values, and loops

I compared every "buy" price with every "sell" price across all Floor 1 shops (the 39 Floor 1 NPC files). **No item can be bought from one NPC and sold to another, or the same one, for a profit.** Shops buy back at roughly a quarter to a third of their price (sword 85 buy, 25 sell; brass armour 450 and 150; bow 400 and 100). `tools/balance.py` also enforces this.

Crafting loops, checked from `ECONOMY.md`'s recipe table: every recipe turns materials plus a fee into goods worth more than the fee, as intended, and none of the outputs can be sold to an NPC for more than the fee plus the NPC value of the materials. Blank runes: 2 small amethysts (NPC value 400) plus 50 gold for 20 runes worth 200 in the shop: a loss, so no loop.

**E-4. High-value stock items have a guaranteed buyer (Low now, Medium later).** Trader Osric pays 90,000 for a magic plate armor, 30,000 for golden legs or a royal helmet, 20,000 for golden armor, 17,000 for a giant sword. On Floor 1 only the deep Underkeep drops these, and those wings open late. When they do, The Underkeeper (60% real chance of a 90,000 item every 30 minutes) is the biggest faucet in the game. Check it when Wing 6 is tuned.

**Dupe risks found:** none in the gear, bank, shop or secret code I read. Today's fixes closed the "paid and got nothing" shop bug, which was a gold sink by accident, not a dupe.

### 6.4 Donation shop

Switched off twice over (`SpireShop.ENABLED = false`, and off in the friends-test scope). The catalogue (`lib/spirebound/shop.lua`): eight furniture and decoration items, two outfits, one mount, Spire Manor, and two things that touch gameplay:
- **The starter set** (+8% damage, +1 armour, levels 1-15, cannot be upgraded). You approved this on 2026-11-23. It is real combat power for the first two hours, out-classed by the free weapon at tier 2 for mages and Rangers. For Vanguards it is built on the same attack-14 sword, so it has the same weakness as B4-1.
- **The Mastery Respec Scroll**, sold only here. Not power in itself, but it means a wrong permanent build choice can only be undone with money. That is the kind of thing players call pay-to-win. Your decision; flagged so it is a choice and not an accident.

Nothing else overlaps with combat. The catalogue test in the code fails the build if a shop item has attack, defence or armour.

### 6.5 Cavebot

- **Is the experience cut enforced on the server?** Yes: `scripts/spirebound/difficulty_events.lua` line 16 multiplies every gain by 0.45 while the bot is on and for 10 minutes after. Party members standing within 7 tiles of a botter get the same cut.
- **Is loot cut too?** Yes: `scripts/spirebound/cavebot.lua` lines 36-54 removes each item with a 50% chance and halves stacks, coins included. Shards and rare weapons sit in the same body and are cut the same way. Secrets, party caves and boss rooms refuse botters. Hunting tasks count every second kill.
- **CB-1. It all hangs on the client's word (High).** The server learns the bot is on from a message the client sends (`cavebot.lua` lines 4-27). A client that never sends it gets full experience and full loot. The one server-side check catches only a character that kills 5 monsters in 10 minutes without moving more than a tile; a walking bot is invisible to it. Long hunts are logged for staff, never punished automatically. This is acknowledged in `DESIGN.md` 12 (hacked clients are a ban matter), but you should know the cut is a rule for honest players, not a wall. *Fix later:* server-side route-repeat detection, as the design already lists.
- **CB-2. Does coin loot reach the bank before the cut? Unverified.** With `autoBank = true`, if the engine banks coins before the cut runs, botters would keep full coins. My reading of the engine's order is that the cut runs first, but it needs one check in the client (it is also part of roadmap PT1).
- **CB-3. The bot state is forgotten on a server restart (Low).** It lives in memory only; a restart clears the 10-minute linger.

### 6.6 Seasonal reset

What the wipe does (`server/data-spirebound/season_wipe.sql`, run offline by `tools/season_wipe.sh` after `/season end` archives every character):
- **Deleted:** every non-staff character, and with it every item, all gold in bags and bank, depots, skills and levels; house ownership and house contents; guilds; market offers and history; floor progress; public secrets; bounties; head starts.
- **Kept:** accounts, staff characters, account-wide rewards (titles, the fishing log, Chronicle seals), the Hall of Seasons, and the donation shop's coin balance and list of owned purchases, which live on the account (`lib/spirebound/shop.lua` lines 83-96).
- **Donation items:** outfits and mounts are handed back at every login because they are remembered on the account. **Furniture, decorations and the Spire Manor deed are ordinary items and a house, so they are wiped (S-1, High before the shop opens).** `DESIGN.md` 4 promises donation purchases carry over. *Fix:* at a new character's first login, re-deliver every owned shop item to the Store Inbox, and give the Manor's last owner first refusal.
- **Floor 1 gear and shards:** gone with the characters, as designed.
- There is a rehearsal mode that runs the wipe on a copy first. Good.

---

## 7. Recommended balance changes

| # | Change | From | To | Why |
|---|---|---|---|---|
| 1 | Barracks sword, axe and mace attack | 14 / 12 / 16 | 20 each, +1 per tier | B4-1: the reward weapon must beat the shop |
| 2 | Spike sword in Garrick's shop | 8,000 gold | removed from Floor 1 | B4-1 |
| 3 | Rare weapon drop chance | 3% from four monsters | 0.5% from Grey Alpha, Bandit Captain and the Ram; own class twice as likely | B4-2 |
| 4 | Rare weapon perks | not built | build them, or delete the lines | B4-2 |
| 5 | Flawless shard from Stonehorn Ram | 3.52% | 1% | 42 Rams make elites irrelevant |
| 6 | Temper quest | +1 tier at any tier | only below tier 2 | A5-5 |
| 7 | Hardcore and Death Game starter blessing | given until level 21 | not given | A8-1 |
| 8 | Death Game "saved" rules | any outside player | only a hostile one; no "dragged in" if you attacked the monster | A8-2 |
| 9 | Boss-room PvP | all levels | level 50 and above | A4-2 (your call) |
| 10 | Gate Hound return time | 30 minutes | 10 minutes | A4-3 |
| 11 | Gate Hound credit | 2% of the fight | 1% | A4-3 |
| 12 | Axe-Lord coins | one body | 10 platinum to each credited fighter | A4-6 |
| 13 | Labyrinth monsters | 4, 4 and 5 | about 12 per level, mixed packs | A1-1 |
| 14 | Underground Burrow Moles | 140, back in 80 s | 70, back in 120 s | A3-4 |
| 15 | Bristle Boars | 17 | about 30 (pairs) | A1-4 |
| 16 | Bandit Road outer loops | packs of 3-4 | pairs | A3-2, the Stair Key step |
| 17 | Sunken purse | 5 platinum, weight 2 | 2 platinum, weight 1 | A7-1 |
| 18 | Delay after a fishing cast | none | 2 seconds | A7-1 |
| 19 | Field Shardling small amethyst | 6% listed (12% real) | 3% listed | E-1: one gem is two thirds of its value |
| 20 | Field Rat cheese | 30% listed (60% real) | 15% listed | E-1 and bag clutter |
| 21 | Underkeep strongbox, login streak | per character | per account | E-3 |
| 22 | Experience stage, levels 9-20 | 4x | decide after measuring with the engine bonuses counted | A3-1 |
| 23 | Promotion price | 20,000 at level 20 | keep, but say "most climbers afford this around level 25", or 12,000 | A9 |
| 24 | Underkeep Wing 1 | about 18 monsters | about 50, three kinds, one mini-boss | A2-1 |

---

## 8. Prioritized action plan

Each line is written so it can be handed over as a task. S = under an hour or two, M = half a day to a day, L = several days.

1. **(S, Jay) Reset the tower's floor record** with `/floor reset 2` then `/floor reset 1`.
2. **(S) Confirm the client checks of today's fixes** (roadmap PT1; commit `fff7d60b` reports them done), and add one more: are a cavebot user's looted coins halved before they reach the bank?
3. **(M) Prove the Axe-Lord by real play** (roadmap N1) once Jay answers Q78: a party that levelled, geared and earned the Stair Key with no commands, through the labyrinth, in the real client.
4. **(M) Rebuild the labyrinth's spawns** (about 12 per level, mixed packs) and walk all three levels with a party in the client.
5. **(S) Test the weapon damage bonus** on a real monster with and without a tier-5 weapon (finding B4-0); if it is skipped for negative damage, fix `SpireProgress.onDealt` and the perk hook, and add the test to the boot run.
5b. **(M) Fix Vanguard weapons:** one attack value for the three barracks weapons set on the item and rising with tier; remove the spike sword from Floor 1's Weaponsmith; add a test that no Floor 1 shop weapon out-damages the barracks weapon of the same class at tier 0.
6. **(M) Rare weapons:** build the four perks (life leech, critical, mana leech, healing) or remove them; cut the drop to 0.5% from elites and the Ram; favour the looter's class.
7. **(S) Close the Hardcore loophole:** no starter blessing for Hardcore and Death Game characters; test a level-15 Hardcore death.
8. **(M) Close the Death Game loopholes:** only hostile outside damage saves a character; no "dragged in" save when the victim attacked the monster; tests for both.
9. **(S, Jay decides) Boss-room PvP below level 50:** if "off", change the two lines in `lib/spirebound/pvp.lua` and add a test.
10. **(M) Make the money and levelling models tell the truth:** loot rate in `tools/gen_economy.py`, stamina and low-level bonuses in the levelling ladder; regenerate `ECONOMY.md` and `BALANCE.md`; list what no longer passes.
11. **(M) Measure solo pace** with the autopilot after task 10 (roadmap PT3) and tune Burrow Hills and the 9-20 stage.
12. **(S) Unlock safety:** recognise test characters by account, not by name; a boss death with no fight record still schedules the return and logs loudly.
13. **(S) Gate Hound:** 10-minute return, 1% credit.
14. **(S) Trails to the three new grounds;** rerun `tools/wilds_plan_check.py` until "problems 0"; walk them.
15. **(S) Small money leaks:** Sealed Shrine gold once per account; strongbox and login streak once per account; temper only below tier 2; reforge refunds on failure; secret and strongbox items through `SpireGive.reward`.
16. **(S) Fishing:** purse 2 platinum, 2-second cast delay, night by the game's clock.
17. **(S) Quest directions** match the map (Bandit Road north-east, one wording for Wolf Copse and the Quarry); a message at level 9 about the slower rate; the Journal says which grounds and steps need a group.
18. **(M) Spear Rangers:** add a Trailwarden Spear, or remove spears from the Ranger's design.
19. **(L) Underkeep Wing 1 at three times the size,** with one secret inside each wing.
20. **(M) Boar Meadow and the Bandit Road's outer loops** (Q73; pairs).
21. **(M) Donation items survive a season:** re-deliver owned furniture and decorations at first login; Spire Manor first refusal. Before the shop opens.
22. **(M) Load dev commands only on a test server.**
23. **(L, later) Cavebot detection on the server** (route repeats), and one more gold sink (repairs).
24. **(L, later) Fishing's missing pieces:** message bottles, hidden spots, a buyer for fish.

---

## 9. Open questions for Jay

1. **PvP in boss rooms on Floors 1 to 4.** The design says PvP is on in every boss room; your top priority says protect new players. Under-50s can be attacked at the Gate Hound and the Axe-Lord today. My recommendation: boss-room PvP from level 50 only.
2. **How many players should the Axe-Lord need** (Q78, still open)? Everything about the end of Floor 1 waits on this.
3. **Should Floor 1 really take 11 to 15 hours?** With the engine's bonuses it is shorter. Do you want the bonuses kept (a faster, friendlier start) or the hours?
4. **Loot rate 2: keep the richer real game, or trim drops to match the documents?** Either is fine; the documents and the game must agree.
5. **Item names.** Shops and drops use Tibia's own names ("magic plate armor", "wand of vortex"). Does your "no CipSoft names a player can see" rule cover item names? If yes, that is a rename pass over a few hundred items.
6. **Is dying on Normal below level 50 meant to cost nothing** (Q77)? It removes all sting and one gold sink from Floor 1.
7. **Should upgraded gear be tradable to low levels?** A market is good; twinked level-1s and gold sellers are the price. A level requirement by tier is a middle road.
8. **Mastery respecs only in the donation shop.** Are you comfortable with players calling that pay-to-win? An in-game route at a steep gold price would remove the argument.
9. **The Vanguard's three weapons:** should sword, axe and mace be equal in power and differ only in their skills (my recommendation), or should they trade attack for defence the way Tibia's do?
10. **How big should Underkeep Wing 1 be at launch?** It is a "must-have" in your brief and currently the smallest content on the floor.
11. **Does a solo player have to be able to reach the Axe-Lord's door?** Today the Stair Key needs a group twice (30 Road Bandits, the Gate Hound). If solo players should at least reach the door, the bandit step needs a solo-friendly place to do it.
12. **Private boss hall without the Stair Key** after the floor is cleared: a welcome catch-up, or a skipped rite of passage?
