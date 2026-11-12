# Floor 1: Hearthgate Plains (design, 2026-11-11)

Written for Jay. This is what Floor 1 is meant to be; the placeholder map in the game follows it. The hunting grounds and monsters are in `BESTIARY.md`; the exact coordinates are in `maps/floor1_plan.py` and `maps/layout_floor1.py`.

## The idea
A new climber starts in a small walled yard, picks a path, and walks into **Hearthgate**: one compact walled city where every service is a short walk from the temple. Around it lies a ring of safe starter fields, then a spread of hunting grounds that get harder and richer the farther you walk, ending in the Old Quarry and the Old Watchtower. To the north, the Pass and the labyrinth lead to the Axe-Lord and Floor 2.

**Small for 20, roomy for 500.** The city is 80 x 72 tiles and the walk from the temple to anything in town is about 30 steps. The land around it has about 1,000 monsters spread over twelve grounds at one monster per 30 tiles, with the same kind of monster in several grounds, so a crowd spreads out instead of queueing for one spawn. At 20 players the grounds feel empty; at 500 the monsters still last.

## Hearthgate (the walled city)
Gates face north, south, west and east. Streets run straight to the plaza.

| Area | What is there |
|---|---|
| North wall (shop row) | General Store (Merchant Wenna), Weaponsmith (Garrick), Armorer (Hesta), Quartermaster's Stores (Bryn, potions and arrows), Bank (Banker Tolliver), Hunters' Hall (Taskmaster Ren, Bounty Warden Cass, Hunter Brannoch) |
| Plaza | Fountain, the Monument (names of those who opened floors), Vesper the Info Broker, a signpost, Captain Dorrow at the north gate |
| West of the plaza | The Ascendancy: Ascendant Veyra promotes you at level 20 for 20,000 gold |
| East of the plaza | The Guild Hall: Guildwarden Sela |
| Centre | The temple (Priest Odran heals and sells blessings; offline training statues). Its door faces the plaza |
| Beside the temple | West: the depot and mailbox. East: the Housewright's Workshop (Orla: furniture kits) |
| South | Lantern Row: two streets of 14 small houses with an open avenue to the south gate |
| South-west corner | The old drain grate (a secret leads under the city to the Underkeep) |

## Housing: 52 houses on Floor 1
| Where | Houses | Notes |
|---|---|---|
| Lantern Row, inside the walls | 14 small | The best homes: safe zone, next to everything. Rent 1,500 |
| Wallside Cabins, outside the west and east gates | 20 small | Cheaper (rent 600), in the Guarded ring but not inside the walls |
| Fisher's Huts, on the river bank | 10 small | Cheapest (rent 500), a short walk from the bridge and Millcross |
| Millcross, across the river | 8 cottages | Rent 800, a quiet village |

Houses cost 1,000 gold per tile to buy (the engine's price), need level 20, and one per character. More districts come with each new floor's town.

## Millcross and the river
A village west of the river with the inn (Miller Agna, Innkeeper Bess) and eight cottages. The river runs north to south; the roads cross it by two bridges. Fisher Corwin lives by the huts on the east bank.

## The ladder (summary)
Twelve grounds plus the apex, in the order a climber meets them. Details in `BESTIARY.md`.

| Levels | Ground | Role |
|---|---|---|
| 1-4 | Ratwarren | experience |
| 3-7 | Toad Pond | experience |
| 5-10 | Sproutling Glade | experience |
| 7-12 | Waspgrass Fields | experience |
| 9-15 | Boar Meadow | experience |
| 11-16 | Burrow Hills | experience |
| 12-18 | Wolf Copse | experience |
| 14-19 | Reedmarsh | money |
| 14-20 | Thornsnap Hollow | experience |
| 17-24 | Shard Fields | experience |
| 19-27 | The Bandit Road | money |
| 23-30 | The Old Quarry | money |
| 28-40 | The Old Watchtower (apex) | experience and money |

The four starter grounds and the roads around the city are *Guarded* (players cannot attack each other). Everything beyond is *Open*. The Old Watchtower is *Contested*.

## Quests on Floor 1
**Story quests** (finish all six to earn the Floor 1 perk at the Registrar):
1. *Bread for the Road* (Miller Agna): 15 Bristle Boars.
2. *The Lost Patrol* (Captain Dorrow): 2 Bandit Captains.
3. *Millstone* (Miller Agna, after Bread): 20 Thornsnaps. Title: Millhand.
4. *Wasp Nest* (Captain Dorrow): 12 Meadow Wasps.
5. *Pelts for the Hall* (Hunter Brannoch): 20 Meadow Wolves.
6. *Quarry Watch* (Hunter Brannoch, after Pelts): 10 Ruin Archers. Title: Quarrywatch.

**Side quests** (good money, not needed for the perk): *Snapper Season* (Fisher Corwin), *Mole Hills* (Miller Agna), *The Alpha* (Brannoch), *Shard Hunt* (Brannoch). Hunting tasks from Taskmaster Ren stay as the daily money source.

## Services at a glance
- **Heal, bless:** Priest Odran (free healing below level 50).
- **Promotion:** Ascendant Veyra, level 20, 20,000 gold: Vanguard to Blade Warden, Ranger to Far Warden, Arcanist to High Arcanist, Mystic to Elder Mystic.
- **Spells:** nobody sells them; they unlock by level (`!spells` lists yours).
- **Where to hunt:** `!hunt`, or ask Wenna, Bryn, Bess, Brannoch, Corwin, Dorrow or Guide Pell. You also get a message when a level takes you past your ground.

## The Arrival Yard (tutorial)
New characters appear in a walled yard south-east of the city. Guide Pell greets them; a stone path leads east past a rat pen (Stop 1: fighting), a sign about skills, spells and the Journal (Stop 2), and into the Registrar's hall (Stop 3), where they choose a path and a difficulty and are sent to the temple. They also get a letter (`!guide`) with the story and first steps.
Still to build for the full tutorial (roadmap R11): gates that open only after a step is done, pop-up hints at levels 2, 5 and 10, and a walked-through test with a real new character.
