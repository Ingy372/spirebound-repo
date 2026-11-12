# Hearthgate v3: the build plan

**Status:** plan only. Nothing in the game has been changed. This file is the brief for the model that builds it.
**Picture:** `docs/HEARTHGATE_PLAN.png` (drawn by `python tools/hearthgate_plan_check.py`, which also checks the plan for overlaps).
**Asked for by Jay (2026-11-12):** *"it does not feel like a premium tight home/town layout ... make the layout of the temple and then town as functional as possible ... i want it to feel like it was hand crafted by a person."*

---

## 1. For Jay: what changes and why

**What is wrong with the town today**
- The Hearth is a long thin slab (62 tiles wide). You spawn at one end of a corridor, and the bank is 20 steps one way and the lockers 20 steps the other.
- The Hearth sits beside the main roads, not on them. Nothing in town points at it.
- Every shop is the same box in one row along the north wall, far from where players respawn.
- The houses are identical boxes in two rows. There are no gardens, lanes or corners, so it reads as a spreadsheet.
- Spire Manor blocks the south avenue and has no setting of its own.

**The new idea in one sentence:** the Hearth stands at the exact centre of town, where the two main roads cross. All four gates lead straight to one of its four doors, and everything a player needs between hunts is within about 25 steps of the spawn point.

**What you will notice when you walk it**
- **The Hearth** is a compact hall with a tower. You wake on the Hearthstone in the middle. Lockers are 6 steps away, the loot buyer 7, the banker 10, the priest 7.
- **The Hearth Ring** is a marble square all the way round it. The three supply shops (potions, arrows, runes) face it, as do the inn, the Hunters' Hall and four of the best houses. The south side widens into the Hearth Square, with the fountain, the Monument and the trading stalls.
- **Four quarters, each with its own character:**

| Quarter | Where | What is in it |
|---|---|---|
| Garden Quarter | north-west | Hearthgate Green (a park with a pond), quiet houses |
| Crown Quarter | north-east | Ascendancy and Guild Hall on Crown Court, Crown Row houses, the Hunters' Hall and Training Yard |
| Lantern Quarter | south-west | Market Street shops, the inn, the Coach Yard by the west gate, Lantern Row houses |
| Manor Quarter | south-east | Spire Manor on the High Road with its own forecourt and public gardens, Southgate Row houses |

- **30 houses** (22 today), in eight small streets, in several sizes, with gardens. Eight of them have an upstairs.
- **The town walls, the gates and everything outside town stay exactly where they are.**

**Walking distances from the spawn point (steps)**

| To | Steps |
|---|---|
| Nearest locker | 6 |
| Trader Osric (sells loot) | 7 |
| Priest Odran | 7 |
| Banker Tolliver | 10 |
| Alchemist (potions) | 21 |
| Fletcher (arrows) | 22 |
| Runewright (runes, scrolls) | 23 |
| Inn, Hunters' Hall | 29 |
| Spire Manor | 36 |
| Weaponsmith, Armorer | about 40 |
| North or south gate | under 50 |
| East or west gate | 56 |

---

## 2. For the builder: ground rules

1. Read `CLAUDE.md` first, especially **Map quality rules**. They all apply.
2. Only the Hearthgate block of `maps/layout_floor1.py` is rebuilt: from the comment `# ---- Hearthgate: the walled city` down to the Underkeep grate lines. Use the helper `R(x, y)`, which turns the plan's coordinates into map coordinates.
3. **Do not change:** `TOWN` in `maps/floor1_plan.py` (112 x 96), the four gates, the city wall, the roads outside town, the camps, the cabins, Millcross, the Arrival Yard, the Underkeep (level 8).
4. **Coordinates in this file are town-relative:** x 0..111 west to east, y 0..95 north to south. The wall is the outer ring (x 0 and 111, y 0 and 95). Rectangles are written `x, y, w, h` and include their walls.
5. Keep every `claim(...)` call. If two buildings overlap, the build must fail.
6. Run `python tools/hearthgate_plan_check.py` if you change any rectangle. It must print `problems 0`.
7. Keep these map point names, because scripts and tests use them: `temple_hearthgate`, `depot_hearthgate`, `trade_hall`, `hearth_bank`, `hearth_trader`, `monument`, `training_yard`, `carriage_hearthgate`, `spire_manor`, `spire_manor_plot`, `underkeep_grate`, every `shop_<name>`, `stairs_guild_hall`, `stairs_hearthgate_inn`, `ladder_hunters_hall`, `stairs_hearth_west`, `stairs_hearth_east`, `stairs_hearth_hall`, `stairs_spire_manor_1..3`. The old `shop_bank` point should now equal `hearth_bank`.

### Gates (unchanged)
| Gate | Tiles |
|---|---|
| North | x 55–58, y 0 |
| South | x 55–58, y 95 |
| West | x 0, y 48–50 |
| East | x 111, y 48–50 |

---

## 3. Streets and paving

Fill the whole town with cobble (870) first, then paint these on top. Ground ids: marble 409, flagstone 416, cobble 870, dirt 103, black marble 410, wood 408.

| Street | Rectangle (x, y, w, h) | Ground | Notes |
|---|---|---|---|
| North Avenue | 55, 1, 4, 31 | marble | north gate to the Ring |
| South Avenue | 55, 72, 4, 23 | marble | Ring to the south gate |
| West High Road ("Market Street") | 1, 48, 36, 3 | flagstone | west gate to the Ring |
| East High Road | 77, 48, 34, 3 | flagstone | Ring to the east gate |
| Hearth Ring and Hearth Square | 37, 32, 40, 40 | marble, with a 1-tile flagstone border on its outer edge | the Hearth stands in the middle of it |
| Mill Lane | 1, 10, 43, 3 | cobble | in front of the Northside houses |
| Avenue lanes | 38, 11, 17, 2 and 59, 11, 16, 2 | cobble | join Mill Lane and Crown Court to the avenue |
| Crown Court | 71, 13, 39, 8 | flagstone | a small square: statue, two trees, benches |
| Green Walk | 1, 35, 25, 3 | cobble | between the Green and the Market Street shops |
| Coach Lane | 11, 51, 3, 30 | cobble | High Road south to Lantern Lane |
| Lantern Lane | 1, 80, 54, 3 and 59, 80, 51, 3 | cobble | the houses' street, crossing the avenue |
| Manor Walk | 77, 69, 33, 3 | cobble | behind the manor |

Everything not listed and not a building stays cobble, except the places section 9 turns into gardens.

---

## 4. The Hearth (the centre of everything)

**Shell:** `42, 38, 30, 23`, white walls, three levels. Interior is x 43..70, y 39..59.

**Four open archways, no door leaves** (the Hearth never closes). Use `m.walls(..., gaps=...)` with `doors=False`:
- north: (56,38), (57,38)
- south: (56,60), (57,60)
- west: (42,48), (42,49), (42,50)
- east: (71,48), (71,49), (71,50)

The avenue and the High Road therefore run straight through the hall and cross at its centre.

### Level 1 (z 7)
The cross of the two aisles divides the floor into four rooms. They are divided by pillars and counters, never by walls, so the hall stays open.

| Part | Tiles | Floor | Contents |
|---|---|---|---|
| North–south aisle | x 55..58, y 39..59 | marble, red carpet (2576) on x 56..57 | |
| East–west aisle | x 43..70, y 48..50 | marble, red carpet on y 49 | |
| **The Hearthstone** (spawn and respawn) | (56,49) | carpet crossing | `temple_hearthgate` and town 1's temple position. Keep this tile and its eight neighbours empty. |
| Colonnade | pillars (2153) at (54,47), (59,47), (54,51), (59,51), (54,43), (59,43), (54,55), (59,55) | | |
| Braziers | coal basins (2113) at (54,39), (59,39), (54,59), (59,59) | | beside the north and south arches |
| **Depot, west** | x 43..54, y 39..47 | wood | Tibia-style depot booths (built 2026-11-12 at Jay's request): five booths on the north wall (lockers x 44..52, y 39), and a back-to-back island of 4 + 4 booths (lockers x 46..52 at y 45 and y 46). Each locker stands on a counter, with wooden railings between booths. Mailbox (3501) at (43,44); stairs up at (43,47). The east wing mirrors it (lockers x 61..69). |
| **Depot, east** | x 59..70, y 39..47 | wood | mirror: north wall x 61, 63, 65, 67, 69; east wall (70,41), (70,43); aisle row y 46 at x 62, 64, 66, 68. Mailbox at (70,45). |
| **Bank and Exchange** | x 43..54, y 51..59 | black marble | counter (`S.counter`) along y 53 from x 44 to 53. Behind it at y 55: **Trader Osric** (52,55), **Banker Tolliver** (48,55), **Broker Nell** (44,55). Chests (2472, 2480) on the south wall at x 44, 47, 50, 53. Sign at (43,52). |
| **Chapel** | x 59..70, y 51..59 | marble | altar (3515) at (65,58); carpet x 64..66, y 53..57; **Priest Odran** at (61,54); benches (2370) at (61,57) and (67,57). |

That makes 26 lockers on this level (10 more in booths in the gallery upstairs). Points: `depot_hearthgate` (49,42), `hearth_bank` (48,52), `hearth_trader` (52,52), `trade_hall` (50,52).

**Stairs up to the gallery:** `m.stairs` at (44,45) named `hearth_west`, and at (69,52) named `hearth_east`.

### Level 2 (z 6): the Trading Gallery
`m.storey(42, 38, 30, 23, Z - 1, floor="wood", style="white")`.
- Lockers on the north wall (y 39) at x 44, 47, 50, 53, 60, 63, 66, 69.
- Four trade tables (`S.counter`, 8 long) starting at (45,43), (61,43), (45,55), (61,55).
- Benches at (48,58), (64,58). Sign at (56,41): "The Trading Gallery. Meet, haggle, and trade face to face."
- Wall lamps with `DG.hang(..., every=5)`.
- Stairs up to the tower: `m.stairs` at (62,52) on this level, named `hearth_hall`.
- *Optional, do it last and only if it renders cleanly:* an atrium. Remove the floor at x 55..58, y 47..51 so the gallery looks down on the Hearthstone, with limestone railings (9273 on the north and south edges, 9272 on the west and east edges, as on the manor roof).

### Level 3 (z 5): the Hall of Climbers, a tower
The top level is smaller than the hall, so the building steps up to a tower.
- `m.storey(49, 44, 16, 11, Z - 2, floor="marble", style="white")` (interior x 50..63, y 45..53).
- Hero statue at (52,46), angel statue at (61,46), pillars at (51,52), (60,52), carpet x 53..60, y 48..50.
- Sign at (56,45): "The Hall of Climbers. Look for a party here before you climb."

### Roofs
The hall's roof surrounds the tower, and the tower has its own. This needs one small tool change (section 10, item 1).
- Hall: automatic, red clay, one level above the gallery.
- Tower: `m.roof(49, 44, 16, 11, Z - 2, "red")`.

### The Ring and the Hearth Square
- Trees (3619) at the Ring's corners: (38,33), (75,33), (38,70), (75,70).
- Lamps (`S.lamp`) at (41,36), (72,36), (41,62), (72,62), and beside every archway.
- **Hearth Square** is the wide south side, y 61..71:
  - fountain (1922, the builder completes it) at (48,65), with benches at (45,63), (51,63), (45,68), (51,68);
  - the Monument: hero statue at (65,65), its sign at (65,67), point `monument` (65,66);
  - **Vesper** at (60,66);
  - six trading stalls: counters 3 long on y 69 starting at x 39, 44, 49, 62, 67, 72, each with one crate or barrel behind it on y 68;
  - sign at (57,62) with the town directory, rewritten for this layout.

---

## 5. Shops and public buildings

`Door` is the doorway tile. Every shop gets its sign beside the door, a counter between the door and the keeper, and the props it has today (the `props` table in the current code).

| Building | Rectangle | Walls | Door | Who | Notes |
|---|---|---|---|---|---|
| Alchemist | 41, 23, 13, 9 | sandstone | (52,31) south | Alchemist Ivo | faces the Ring |
| Fletcher | 60, 23, 13, 9 | timber | (61,31) south | Fletcher Tamsin | faces the Ring |
| Runewright | 26, 37, 11, 10 | stone | (36,45) east | Runewright Mael | faces the Ring |
| Inn "The Lantern & Lark" | 24, 52, 13, 15 | timber | (36,59) east | Innkeeper Roan | upstairs rooms; stairs `hearthgate_inn` |
| Hunters' Hall | 77, 33, 18, 14 | stone | (77,40) west | Taskmaster Ren, Bounty Warden Cass, Hunter Brannoch | trophy loft; ladder `hunters_hall` |
| Quartermaster's Stores | 44, 2, 10, 9 | brick | (53,6) east | Quartermaster Bryn | last stop before the north gate |
| Guardhouse | 60, 2, 10, 9 | stone | (60,6) west | Captain Dorrow stands outside at (59,8) | racks, a table, two beds |
| Post Office | 44, 13, 10, 9 | sandstone | (53,17) east | Postmaster Hobb | two mailboxes inside |
| Tailor | 60, 13, 10, 9 | timber | (60,17) west | Tailor Quill | |
| General Store | 3, 38, 10, 9 | brick | (8,46) south | Merchant Wenna | Market Street |
| Weaponsmith | 14, 38, 10, 9 | brick | (19,46) south | Weaponsmith Garrick | Market Street |
| Armorer | 14, 52, 9, 9 | brick | (18,52) north | Armorer Hesta | Market Street |
| Housewright's Workshop | 14, 62, 9, 9 | stone | (14,66) west | Housewright Orla | on Coach Lane |
| Ascendancy | 75, 2, 15, 11 | sandstone | (82,12) south | Ascendant Veyra | faces Crown Court |
| Guild Hall | 93, 2, 15, 11 | timber | (100,12) south | Guildwarden Sela, Banker Ansel (a guild bank desk) | meeting room upstairs; stairs `guild_hall` |
| Coach Yard | 2, 52, 9, 9 | timber fence (`m.walls`, no roof, dirt ground) | gap at (6,52) | Coachman Ferro at (6,56) | hitching posts, barrels; point `carriage_hearthgate` (6,55) |
| Training Yard | 96, 33, 13, 14 | timber fence, no roof, dirt ground | gaps at (102,46), (103,46) | | offline statues 16198–16202 at y 35, x 98, 100, 102, 104, 106; practice posts; point `training_yard` (102,39) |

The north-wall bank is gone. Banker Tolliver is in the Hearth and Banker Ansel is in the Guild Hall.

---

## 6. Spire Manor

- Keep the building exactly as it is (22 x 16, four levels, house 99, shop-only). **Only its origin moves:** from `R(46, 53)` to `R(78, 53)`. Its door, at (89,53), then faces the East High Road.
- **Forecourt**, x 84..94, y 51..52: marble paving, lamps at (86,51) and (92,51), flower pots either side of the door.
- **Spire Gardens**, `101, 53, 9, 16`: a public garden beside the manor. Grass, a small pond (`S.pond`, about 2 x 2) in the middle, four trees, two benches, flowers, and one cobble path from the High Road. No walls.
- The manor's sign stays beside its door.

---

## 7. Houses: 30, in eight streets

Each lot below is 8 x 8. Use `m.house_building`. **Do not build 30 identical boxes** (see the size rule under the table).

| Street | Lots (x, y) | Door side | Storeys | Rent | Walls |
|---|---|---|---|---|---|
| Squareside (on the Hearth Square) | (38,72), (47,72), (59,72), (68,72) | north | 2 | 4,000 | white, white, sandstone, white |
| Crown Row (on Crown Court) | (75,21), (84,21), (93,21), (102,21) | north | 2 | 3,200 | sandstone, timber, sandstone, timber |
| Northside (Mill Lane) | (2,2), (11,2), (20,2), (29,2) | south | 1 | 1,500 | timber, brick, timber, sandstone |
| Greenside (beside the park) | (2,14), (2,24) | east | 1 | 1,800 | timber, timber |
| Lantern Row North | (2,72), (15,72), (24,72) | south | 1 | 1,500 | brick, timber, sandstone |
| Lantern Row South | (3,83), (12,83), (21,83), (30,83), (39,83) | north | 1 | 1,300 | timber, sandstone, brick, timber, sandstone |
| Manor Walk | (77,72), (86,72), (95,72) | south | 1 | 1,800 | sandstone, white, timber |
| Southgate Row | (62,83), (71,83), (80,83), (89,83), (98,83) | north | 1 | 1,300 | brick, timber, sandstone, timber, brick |

**Size rule (this is what makes it look hand-built):** in every street, make one house in three smaller than its lot (7 x 8 or 8 x 7), and turn the spare strip into a garden: grass, one tree or two bushes, flowers. Never put the same wall style on two neighbours. Name houses by street ("Squareside 1", "Crown Row 3"...).

Behind Crown Row (y 29..32, x 75..109), make a strip of back gardens: grass, trees, flower beds.

---

## 8. Green places

| Place | Rectangle | What goes there |
|---|---|---|
| Hearthgate Green | 12, 14, 25, 21 | Grass. A pond in the middle (`S.pond` at (24,24), about 5 x 3). A cobble path from each side to a ring path round the pond. Six benches facing the water, eight trees in two loose groups, flower beds, lamps at the four entrances. |
| Old Well Yard | 2, 62, 9, 9 | Overgrown grass and bushes with a broken wall piece or two. The Underkeep grate at (5,66), its sign at (7,66), secret `s1` at (6,67). The Underkeep exit teleport must arrive at (5,68). |
| Pocket garden | 48, 83, 6, 8 | Grass, a bench, two trees. |
| Spire Gardens | see section 6 | |

---

## 9. Detailing rules: how to make it feel hand-crafted

1. **Ground tells you where you are.** Marble means the Hearth Ring and the avenue. Flagstone is the High Road and Crown Court. Cobble is every lane. Dirt is the yards. Grass is the gardens.
2. **No bare walls on main streets.** Every building face on the Ring, the avenue or the High Road has something in front of it: a sign, a lamp, a crate and barrel, a flower pot, or a bench. Vary the mix so that no two neighbours match.
3. **Lamps:** at every street corner, and about every 8 tiles along the avenue and the High Road, on alternating sides.
4. **Trees stand only on grass**, or singly at the four Ring corners. Never put a tree on a street.
5. **Break the symmetry a little on purpose.** The east and west sides of the town already differ. Do not mirror the prop placement either.
6. **Every interior is furnished for its job** (counter, shelves or racks, a rug, something personal on a table), and nothing blocks the path from the door to the keeper.
7. **Keep it walkable.** Every lane is at least 2 tiles wide, and nothing stands within 2 tiles in front of a door. The Hearthstone and the archways stay clear.
8. **No new item ids by guesswork.** Check any new piece with `python tools/spriteview.py` before using it, and prefer the ids already in `maps/layout_floor1.py`, `maps/scenery.py` and `maps/dungeon.py`.

---

## 10. Tool changes the build needs

1. **`Map.roof` in `tools/mapgen.py`:** today it gives up if anything already stands at roof level. Change it to skip only the tiles that already have ground, and still lay the rest. That lets the Hearth's roof wrap round its tower. Check that the other buildings' roofs look the same afterwards.
2. **`Map.building` with several doorways:** the Hearth has four archways. Build it with `m.fill` and `m.walls(gaps=...)` directly (as the city wall does), then add it to `m.buildings` by hand so it gets its roof: `m.buildings.append(dict(rect=(x, y, 30, 23), z=Z, style="white", top=Z, roof="red"))` before the `m.storey` calls.
3. **Fenced yards** (Coach Yard, Training Yard): use `m.walls` only, not `m.building`, so they get no roof. The Training Yard is already built this way.

No other tool changes are needed.

---

## 11. Build order

1. Tool change 1, then rebuild and render the town to confirm nothing else changed.
2. Streets and paving (section 3).
3. The Hearth, all three levels, its stairs and roofs (section 4). Render each level, and the outside with `python tools/maprender.py out.png 1210 1266 46 40 7 1 4`.
4. The Ring, the Hearth Square, and the three Ring shops.
5. The rest of the shops and public buildings (section 5).
6. Spire Manor's move, forecourt and gardens (section 6).
7. Houses street by street (section 7), then the green places (section 8).
8. The detailing pass (section 9).
9. Update the tests that name old places, `FLOOR1.md`, `ROADMAP.md`, `PROGRESS.md`, and `docs/FLOOR1_PLAN.png` (`python tools/plan_image.py`).

Commit after each numbered step.

---

## 12. Done when

- `python tools/hearthgate_plan_check.py` prints `problems 0`, and `python tools/mapgen.py` builds with no overlap error.
- `tools/test_boot.sh` passes with no errors. The Hearth test in `test_npc_talk.lua` and the manor and stairs tests in `test_upstairs.lua` are updated for the new places, and still check the real map.
- New in-game checks exist for:
  - the Hearthstone being the town temple position and a safe tile;
  - a locker within 6 steps of it;
  - all four archways being walkable;
  - all three Hearth staircases working both ways;
  - 30 houses plus Spire Manor on the map.
- Renders of every quarter have been looked at, corners and edges included, with and without roofs.
- In the real client (Jay's GM character, `/pos`), these have been walked: spawn to locker to Trader Osric to the Alchemist to the north gate; all three Hearth levels; the manor's four floors; one house in each street.
- No shop, NPC or named point from section 2 is missing.
