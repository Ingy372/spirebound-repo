# Floor 1: Hearthgate Plains (design, 2026-11-11)

Written for Jay. This is what Floor 1 is meant to be; the placeholder map in the game follows it. The hunting grounds and monsters are in `BESTIARY.md`; the exact coordinates are in `maps/floor1_plan.py` and `maps/layout_floor1.py`.

## How to look at the map (for the builders)
- `python tools/maprender.py out.png x y w h [z] [scale]` draws any part of the map with the real sprites, exactly the way the client shows it. Output goes to `.local/scratch/` (never committed: it contains the base game's art).
- `python tools/spriteview.py sheet out.png 1270-1280 ...` draws labelled contact sheets of item ids; `find <word>` lists ids by name. Wall families, doors, windows, trees, props and carpets in `tools/mapgen.py` and `maps/scenery.py` were all picked by looking at their sprites.

## The idea
A new climber starts in a small walled yard, picks a path, and walks into **Hearthgate**: one compact walled city where every service is a short walk from the temple. Around it lies a ring of safe starter fields, then a spread of hunting grounds that get harder and richer the farther you walk, ending in the Old Quarry and the Old Watchtower. To the north, the Pass and the labyrinth lead to the Axe-Lord and Floor 2.

**Small for 20, roomy for 500.** The walk from the Hearthstone to anything in town is short. Since the wilds rebuild (2026-11-13, `FLOOR1_WILDS_PLAN.md`) every hunting ground is a walled place with one gate, a hub and four hunting loops: about 1,270 monsters at rest on the whole floor since the challenge pass (2026-11-25, "challenge, not calm"): about 260 on the surface, 85 on the hill levels and about 920 underground in the dens, cellars and party caves (counted from the server's spawn file, 2026-11-26). When a ground fills up, the crowd system adds extra groups.

## Hearthgate (the walled city)
Gates face north, south, west and east. Streets run straight to the plaza.

| Area | What is there |
|---|---|
| North wall (shop row) | General Store (Merchant Wenna), Weaponsmith (Garrick), Armorer (Hesta), Quartermaster's Stores (Bryn, potions and arrows), Bank (Banker Tolliver), Hunters' Hall (Taskmaster Rhen, Bounty Warden Cass, Hunter Brannoch) |
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

### How every hunting ground is built (2026-11-13)
- **One gate** off a road or trail, 3 tiles wide, with a signpost at the junction. Inside: a **hub** with a sign naming the ground and its loops, a fire and a bench. No monsters within 8 tiles of the gate.
- **Four loops** (north-west, north-east, south-west, south-east): a ring trail 2 tiles wide round a solid grove, pond, rock pile or camp. Monster groups stand at fixed spots on the ring (4 groups of 3 on a starter loop, 6 on the others). One loop feeds one player hunting flat out, or two sharing; a cavebot route is one lap.
- **Return times** follow Tibia's rule: few monsters, back after 2 to 3.5 minutes (elites 15). Standing still does not pay: walk the loop.
- **Caves** for parties of 2 to 4 under Burrow Hills (the Molework), Wolf Copse (the Alpha's Den), Thornsnap Hollow (the Rootcellar), Shard Fields (Shard Grotto), the Bandit Road (Smugglers' Cellar) and the Old Quarry (the Lower Works). The way down is a hole where the cross trails meet. No cavebot below.
- **Crowd system:** 5+ players in a ground switch on half its extra groups, 8+ all of them, 12+ on a starter ground makes them return three times as fast. `!hunt` says how busy your grounds are.
- **Levelling:** levels 1-8 at 10x, 9-20 at 4x, 21-50 at 3x; Floor 1 takes about 11 to 15 hours of real play (ECONOMY.md has the ladder).

## Quests on Floor 1
**The story: The First Climb** (roadmap FD1, 2026-11-27; design `docs/superpowers/specs/2026-11-27-floor1-depth-design.md` 4.1).
Why everyone climbs: at the top of the Spire waits the Summit Wish, one wish for whoever reaches it (Guide Pell, the `!guide`
letter). Archivist Maren at the Monument tells eight chapters that follow the First Climb, the company that went up before
Hearthgate was a town; chapter 8 gives the title Heir to the First Climb and the Floor 1 perk (Registrar Maelis, 'perk').
1. *The Missing Names* (level 4): read the Monument's scraped rows; find the supply mark on the old wall by the north gate.
2. *The Quartermaster's Trail* (8): three supply stones in the Ratwarren, Toad Pond and the Sproutling Glade.
3. *Bread for the Climb* (12): ask Miller Agna about the climb; the old flour bin in Thornsnap Hollow (three thornsnaps); the ledger.
4. *The One Who Turned Back* (15): Brother Tam's grave in Reedmarsh; take his pendant to the archive or lay Agna's wreath (two titles, the look line says which).
5. *The Pay Chest* (19): two pages of Ione's record from Bandit Captains.
6. *The Watch That Never Ended* (24): the standing order by the oath stones in the Old Quarry; the watch log in the Old Watchtower's keep.
7. *The Rearguard* (28): Aldric Vane's field desk at the foot of the labyrinth, opened with the Stair Key.
8. *The Last Page* (30): the Axe-Lord of the Stair (he was Aldric Vane).
Twelve records (nine from the chapters, three loose: the Millcross carriage stop, Wolf Copse, Reedmarsh's camp) are kept as
items and counted on the Discoveries page (Records). Townsfolk each say one line about the First Climb ('climb'), and disagree.
Objects are put down at start-up by `scripts/spirebound/first_climb.lua`; Maren and the Oathroom are in `maps/floor1_story.py`.

**The big quest: The Oathroom** (roadmap FD3). Four climbers of level 30 stand on the four oath stones on the Old Quarry's
south trail; one pulls the lever. 25 minutes, one team at a time, on level 10: the Captain's hall (hold a line for three
minutes of waves), the Scout's hall (two pairs, four levers in the carved order SUN, MOON, STAR, FLAME), the Keeper's hall
(a rune floor; the safe path is in the book on the lectern, new each run), the Healer's hall (the Oathkeeper heals from four
braziers; stand beside one to put it out). Four chests, one per character each season: a tier step on a Floor 1 weapon,
the Oathbound Pack, 10,000 gold, or the Oathkeeper's Mantle aura. The first team each season goes on the Monument.

**Jobs** (the old story quests, same pay; since FD1 they no longer gate the perk):
1. *Bread for the Road* (Miller Agna): 15 Bristle Boars.
2. *The Lost Patrol* (Captain Dorrow): 2 Bandit Captains.
3. *Millstone* (Miller Agna, after Bread): 20 Thornsnaps. Title: Millhand.
4. *Wasp Nest* (Captain Dorrow): 12 Meadow Wasps.
5. *Pelts for the Hall* (Hunter Brannoch): 20 Meadow Wolves.
6. *Quarry Watch* (Hunter Brannoch, after Pelts): 10 Ruin Archers. Title: Quarrywatch.

**Side quests** (good money, not needed for the perk): *Snapper Season* (Fisher Corwin), *Mole Hills* (Miller Agna), *The Alpha* (Brannoch), *Shard Hunt* (Brannoch). Hunting tasks from Taskmaster Rhen stay as the daily money source.

## Services at a glance
- **Heal, bless:** Priest Odran (free healing below level 50).
- **Promotion:** Ascendant Veyra, level 20, 20,000 gold: Vanguard to Blade Warden, Ranger to Far Warden, Arcanist to High Arcanist, Mystic to Elder Mystic.
- **Spells:** nobody sells them; they unlock by level (`!spells` lists yours).
- **Where to hunt:** `!hunt`, or ask Wenna, Bryn, Bess, Brannoch, Corwin, Dorrow or Guide Pell. You also get a message when a level takes you past your ground.

## The Arrival Yard (tutorial)
New characters appear in a walled yard south-east of the city. Guide Pell greets them; a stone path leads east past the Old Granary, whose cellar is full of rats (Stop 1: fighting), a sign about skills, spells and the Journal (Stop 2), and into the Registrar's hall (Stop 3), where they choose a path and a difficulty and are sent to the temple. They also get a letter (`!guide`) with the story and first steps.
Guide Pell also gives a first quest (*First Blood*: three rats in the granary cellar), and short hints appear at levels 2, 5, 8, 10 and 20.
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

## Hearthgate v4.1 (2026-11-27, Jay's changes to v4)
This changes v4 below where they differ. Jay: "make it more of an 8 sided wall", "brighten it up some", "make the depot (middle of town) a building. make it circular", "flip the floor plan ... the actual bank booths ... should be on the second floor".
- **A real eight-sided wall:** the corners are cut twice as deep (24 tiles instead of 12).
- **Green, not grey:** grass between the buildings, paved streets, a path from every door to its street, trees, bushes and flowers.
- **The Hearth is the round building in the middle of the plaza** (round wall, red round roof, an archway on each of the four avenues).
  - **Ground floor:** you appear on the Hearthstone in the middle (and Waycrystals bring you there). Round it: the Monument (the names of each floor's first boss clears), the Floor Beacon's four fire bowls, the Arena Champion's statue, the notice board, four free trading stalls, benches. Stairs up on the west and east sides.
  - **Second floor:** 16 depot lockers in booths facing the middle (two rows north, two south), the bank counter on the west (Banker Tolliver, Trader Osric), Broker Nell and Vesper at the east counter.
- **The big hall north of the plaza is now the Climbers' Temple:** the chapel (Priest Odran), a waiting hall, a trade hall, the Trading Gallery upstairs and the Hall of Climbers on top. Flower beds and the fountain in front of it.
- **Hearthgate Green's pond** is bigger, with a proper shore, water lilies, reeds, stones and a little wooden pier.
- **Homes: 29** (the deeper corners took some lots; new ones on Manor Lane and Garden Row by the manor). Spire Manor's grounds moved a little west.
- **Nine townsfolk** (three more: Porter Gimble at the Hearth, Lysa the Florist and Corwin the Minstrel).
- **Steps from the Hearthstone:** stairs to the depot and bank 13-14, shops 19 to 25, the temple's priest 35.

This replaces every Hearthgate description above, v3 included. Jay (2026-11-26) asked for a full redesign: function first, a loose nod to a big round starting plaza. The tile plan is `maps/hearthgate_plan.py`; the picture is `docs/HEARTHGATE_PLAN.png`.
- **Same size, place and four gates; the wall's corners are cut off,** so the city is eight-sided.
- **Hearth Plaza:** a round marble plaza, 33 tiles across, in the middle. You appear (and come back after dying) on the Hearthstone at its centre, in the open air. Round it: the Monument, the Arena Champion's statue, the Beacon's four fire bowls, the fountain, Vesper, the notice board, six free trading stalls, benches.
- **The Hearth** is the great hall on the plaza's north side, its wide archway facing the Hearthstone (more archways north, west and east). Just inside: the bank and exchange (Tolliver, Osric, Nell) on the left, a depot wing on the right; behind them a second depot wing and the chapel (Priest Odran). 20 lockers in booths downstairs, 10 more in the Trading Gallery upstairs; the Hall of Climbers tower on top.
- **Every shop is at the plaza's edge,** two shops to a building, where the avenues leave it: Weaponsmith and Armorer, General Store and Quartermaster (west); Runewright and Fletcher, Alchemist and Tailor (east); the inn, Housewright and Post Office (south).
- **Crown Quarter (north-east):** the Ascendancy and the Hunters' Hall on the street along the Hearth's east wall; the Guild Hall and the Training Yard on the East High Road.
- **Spire Manor (south-east)** stands in its own walled grounds with a forecourt, reached by Manor Walk through the public Spire Gardens.
- **Homes, 30 in five streets:** Northside (north, mid-size), Crown Row (north-east, the best homes, all with an upstairs), Greenside (garden houses round Hearthgate Green, north-west), Lantern Row (small cheap homes in tight lanes, south-west), Southgate Row (south, mid-size). Ten have an upstairs.
- **Kept where they were:** the Old Well Yard and the Underkeep grate (south-west corner), the guardhouse and Captain Dorrow at the north gate. The Coach Yard is now by the south gate.
- **Walking distances from the Hearthstone** (steps): bank 24, nearest locker 26, shops 19 to 25, Hunters' Hall 31, Guild Hall 35, Ascendancy 40, Training Yard 44, gates 46 to 56.

## Hearthgate v3 (2026-11-12, built from HEARTHGATE_PLAN.md; replaced by v4 above)
This replaced the earlier Hearthgate descriptions above. The full plan, with every coordinate, is `HEARTHGATE_PLAN.md`; the picture is `docs/HEARTHGATE_PLAN.png`.
- **The Hearth** stands where North Avenue and the East-West High Road cross, with four open archways. You spawn on the Hearthstone in the middle of a red carpet cross.
  - **Ground floor:** depot wings with 20 lockers in Tibia-style booths (10 more upstairs); the bank and exchange (Tolliver, Osric, Nell); the chapel (Priest Odran).
  - **Level 2:** the Trading Gallery.
  - **Level 3:** the Hall of Climbers, in a tower with its own roof.
- **The Hearth Ring** is a marble square around the hall. Its south side is the Hearth Square: fountain, Monument, six free trading stalls. The Alchemist, Fletcher and Runewright face it.
- **Four quarters:**
  - Garden Quarter: Hearthgate Green with a pond.
  - Crown Quarter: Ascendancy and Guild Hall on Crown Court, Hunters' Hall, Training Yard.
  - Lantern Quarter: Market Street shops, the inn, the Coach Yard, Old Well Yard with the Underkeep grate.
  - Manor Quarter: Spire Manor on the East High Road with its forecourt and the public Spire Gardens.
- **30 houses** in eight streets (Squareside, Crown Row, Northside, Greenside, Lantern Row North and South, Manor Walk, Southgate Row); every third house is smaller with a garden strip; 12 have an upstairs.

## Homes, varied (2026-11-26)
This replaces the housing counts above. Jay: "the housing options are boring and all the same. unique housing options with 1 grand mansion house that a player can buy for real money is what i was going for."
- **Hearthgate, inside the walls:** 30 houses in eight streets, each with one of six plans (one room, two rooms, one room and a back yard, living room and side bedroom, two rooms with two beds, a snug single room); eight have an upstairs. Rent follows floor space.
- **Wallside Cabins:** 16 homes outside the west and east gates: 12 small cabins and 4 double-size longhouses.
- **Fisher's Huts:** 8 homes on the river bank: 6 huts and 2 boathouses.
- **Millcross:** 8 cottages, no two alike.
- **Spire Manor:** the one grand house, four furnished floors, sold only in the Spire Shop (DESIGN.md 7.6).
