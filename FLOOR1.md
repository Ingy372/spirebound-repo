# Floor 1: Hearthgate Plains (design, 2026-11-11)

Written for Jay. This is what Floor 1 is meant to be; the placeholder map in the game follows it. The hunting grounds and monsters are in `BESTIARY.md`; the exact coordinates are in `maps/floor1_plan.py` and `maps/layout_floor1.py`.

## How to look at the map (for the builders)
- `python tools/maprender.py out.png x y w h [z] [scale]` draws any part of the map with the real sprites, exactly the way the client shows it. Output goes to `.local/scratch/` (never committed: it contains the base game's art).
- `python tools/spriteview.py sheet out.png 1270-1280 ...` draws labelled contact sheets of item ids; `find <word>` lists ids by name. Wall families, doors, windows, trees, props and carpets in `tools/mapgen.py` and `maps/scenery.py` were all picked by looking at their sprites.

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
Guide Pell also gives a first quest (*First Blood*: three rats in the pen), and short hints appear at levels 2, 5, 8, 10 and 20.
Still to build for the full tutorial (roadmap R11): gates that open only after a step is done, and a walked-through test with a real new character in the client.

## Look and feel (2026-11-11 pass)
- **Buildings** come in wall families (brick, grey stone, timber and plaster, sandstone, white stone, pale stone), with windows, open doors in the public buildings, a post on every outside corner, and furnished interiors: shop counters, barrels, crates, anvils, wardrobes, carpets, marble pillars, tables and chairs.
- **The city wall** is grey stone with a vine-covered pillar on each corner and a pillar either side of every gate. The plaza is cream marble inside a flagstone border, with fountain, statues, trees, benches, market stalls and lamp posts. Streets are cobble with a cream stripe down the two avenues.
- **The land** has a winding river with muddy banks and wooden bridges, winding dirt roads, forest masses between the places people go (never within about eight tiles of a road, building or hunting ground), three ponds and a lake, ruins (a watchtower by the lake, a farmhouse, a toppled shrine), two rings of standing stones, and a fenced wheat field north of Millcross.
- **Each hunting ground has its own look:** dirt mounds (Ratwarren), a pond (Toad Pond), ferns and bushes (Sproutling Glade), a flower meadow (Waspgrass), oak groves and mud wallows (Boar Meadow), bare dirt and boulders (Burrow Hills), dark fir forest (Wolf Copse), a thorn thicket (Thornsnap Hollow), pools and mud (Reedmarsh), grey gravel and boulders (Shard Fields), a ruined camp with carts and fires (Bandit Road), rubble and broken pillars (Old Quarry).
- **Still to do:** roofs are not possible with these tools (the game draws roofs as a separate floor), the Pass, labyrinth and Axe-Lord's room are plain stone boxes, the camps want more landmark set pieces, and the river banks need proper shore tiles. Cowork's finishing polish should start there.

## Wall rules (2026-11-11, learned from Canary's hand-made map)
- Corners: top-left = the small post, top-right = horizontal piece, bottom-left = vertical piece, bottom-right = the L-shaped corner piece. `Map.autowall` applies the same rule to any shape (the labyrinth uses it).
- Ground: the top row and left column of a building's walls stand on the outside ground; the bottom row and right column on the floor. Doorways always show the floor.
- Doors: each wall family has its own open door (brick 5099/5108, stone 6253/6255, sandstone 1655/1657, pale stone archway 1482/1484, white 1673/1670, timber 1649/1647).
- Nothing natural (trees, bushes, rocks) within one tile of a building or two tiles in front of its door.

## Roofs, upstairs, stairs and ladders (2026-11-11)
- Every building on the surface has a roof (red clay over white walls, dark shingle over brick and stone, straw over timber and sandstone). The game hides it when you walk inside. Roof shape and edge pieces follow Canary's hand-made map.
- Upstairs: the Guild Hall meeting room (stairs), the Millcross Inn guest rooms (stairs), the Hunters' Hall trophy loft (ladder and trapdoor), and four two-storey Lantern Row houses on the street corners (rent 2,800 instead of 1,500; the upstairs belongs to the house).
- Upstairs rooms in Hearthgate and Millcross count as town (safe zone).

## Ground edges (2026-11-11)
- Grass now spills softly over the edges of roads, dirt, mud, gravel, sand and paving, and every shore of the river, lake and ponds has a proper shoreline. The coastline is tidied first so there are no one-tile islands or puddles. Both edge sets were learned from Canary's hand-made map.

## Dungeons and special areas (2026-11-11)
- **The Pass:** a dirt fighting pit inside a flagstone ring, four pillars, braziers at both gates, torches on the walls, old bones.
- **The labyrinth:** stone walls with lamps along the corridors, cobwebs and bones; a different floor on each level (stone, stone tile, black marble).
- **The Axe-Lord's hall:** black marble, a red runner from the door to the sealed stair, two rows of pillars, braziers, a throne, chains on the back wall.
- **The Old Watchtower:** an overgrown courtyard with broken masonry around a paved keep with braziers and wall torches; the rope spot hides behind rubble. Its cave below is now a natural cave (rock walls, stalagmites, crystals, bones).
- **The Underkeep:** pale stone halls with lamps, a storeroom by the entrance, braziers in the column hall, cobwebs and bones; the strongbox room has a carpet. Wings 2-6 get pillars, braziers and clutter.
- **The Arena:** a sand floor with flagstone ends, red and blue team pads, braziers and torches. **The Siege keep:** a grassy courtyard with paved roads from the four gates to a white keep with a red cross carpet and a throne.

## Hearthgate, redesigned (2026-11-11, Jay: "i want the town expanded ... dont waste much space")
112 x 96 tiles. North to south:
- **North wall:** ten shops. West of the avenue: General Store, Weaponsmith, Armorer, Fletcher, Alchemist. East: Runewright, Quartermaster, Tailor, Bank, Post Office.
- **Market Square:** fountain, Monument, benches, eight free trading stalls. The Ascendancy is west of it, the Guild Hall (meeting room upstairs) east.
- **Temple block:** depot and Trade Hall (Broker Nell, market lockers) | temple | Housewright's workshop and Hunters' Hall (trophy loft by ladder).
- **High road:** west gate to east gate.
- **South of the high road:** the Lantern & Lark inn (rooms upstairs), the Training Yard (offline training statues, practice posts), Spire Manor (the showcase house) closing the avenue, and the Carriage Station.
- **South wall:** two streets of houses, 22 in all (8 with an upstairs).

## The Hearth (2026-11-12)
Hearthgate's home hall, replacing the old temple, depot and Trade Hall. It is 62 x 16 tiles across three levels, with its door facing the Market Square.
- **Level 1:** the temple nave in the middle (the spawn and respawn point, the altar, Priest Odran). The depot wing is to the west (18 lockers, 2 mailboxes); the bank and exchange to the east (Banker Tolliver and the account vault, Trader Osric who buys loot, Broker Nell for the market).
- **Level 2:** the trading gallery, with 16 lockers and six long trade tables.
- **Level 3:** the Hall of Climbers, with statues and a meeting carpet for finding a party.

## Hearthgate v3 (2026-11-12, built from HEARTHGATE_PLAN.md)
This replaces the earlier Hearthgate descriptions above. The full plan, with every coordinate, is `HEARTHGATE_PLAN.md`; the picture is `docs/HEARTHGATE_PLAN.png`.
- **The Hearth** stands where North Avenue and the East-West High Road cross, with four open archways. You spawn on the Hearthstone in the middle of a red carpet cross.
  - **Ground floor:** depot wings with 22 lockers; the bank and exchange (Tolliver, Osric, Nell); the chapel (Priest Odran).
  - **Level 2:** the Trading Gallery.
  - **Level 3:** the Hall of Climbers, in a tower with its own roof.
- **The Hearth Ring** is a marble square around the hall. Its south side is the Hearth Square: fountain, Monument, six free trading stalls. The Alchemist, Fletcher and Runewright face it.
- **Four quarters:**
  - Garden Quarter: Hearthgate Green with a pond.
  - Crown Quarter: Ascendancy and Guild Hall on Crown Court, Hunters' Hall, Training Yard.
  - Lantern Quarter: Market Street shops, the inn, the Coach Yard, Old Well Yard with the Underkeep grate.
  - Manor Quarter: Spire Manor on the East High Road with its forecourt and the public Spire Gardens.
- **30 houses** in eight streets (Squareside, Crown Row, Northside, Greenside, Lantern Row North and South, Manor Walk, Southgate Row); every third house is smaller with a garden strip; 12 have an upstairs.
