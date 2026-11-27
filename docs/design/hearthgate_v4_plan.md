# Hearthgate, a new layout (plan, 2026-11-26)

Written for Jay. Picture: `docs/HEARTHGATE_V4_PLAN.png`. Nothing is built yet.

Jay, 2026-11-26: *"full redesign of the towns layout. if you feel the layout scores a solid A, then dont worry about a redesign."* And earlier the same day: *"i wanted the town to have somewhat of a resemblance to sword art onlines town of beginnings. but at the same time dont want anything having restrictions on it to hold to that hope."*

## My score for today's layout: B

What works: it is tidy, every service exists, the Hearth is in the middle, four gates, clear streets.

Why it is not an A:
1. **Walks are long.** From the Hearthstone it is 29 steps to the nearest shop door, 39 to 50 to the weapon, armour and general shops, 62 to the Ascendancy and 80 to the Guild Hall (`tools/hearthgate_plan_check.py`). A player restocks dozens of times; this is the number that matters most.
2. **The middle is a building, not a place.** You appear inside the Hearth hall. The square outside it is a strip on one side. There is nowhere the whole server naturally stands together, which is the one thing the Town of Beginnings is remembered for.
3. **No districts.** Shops, halls and homes are spread through one even grid of same-size blocks, so nothing tells you where you are.
4. **Homes hold the best ground.** Houses line the square while the shops sit against the far north wall.
5. **Spire Manor has no grounds.** The one house sold for real money is a box on a street.

## The new layout

Same footprint (112 by 96 tiles), same four gates, same place on the map, so nothing outside the walls moves.

- **An eight-sided wall.** The corners are cut off, so the city reads as round from the road, with a tower at each of the eight corners and a gatehouse at each gate.
- **Hearth Plaza, a great round square in the very middle** (about 34 tiles across). You appear on the Hearthstone in the open air at its centre. Round it: the Monument, Vesper, the Beacon's four fire bowls, the notice board, benches and the free trading stalls. This is the Town of Beginnings nod: one huge round plaza where everyone starts, returns and gathers. Names, shapes and buildings stay our own.
- **The Hearth becomes the great hall on the plaza's north side,** its doors facing the Hearthstone: depot wings, chapel, bank and traders inside, as now, about 12 steps from where you appear.
- **Every shop faces the plaza.** Six shop buildings stand round the ring: weapons and armour, general store and potions, runes and fletcher, alchemist and tailor, the inn, the housewright and post. Target: every shop door within 25 steps of the Hearthstone (today 29 to 50).
- **Four avenues** run from the plaza to the four gates. The first thing a new player sees in each direction is a gate.
- **Crown Quarter (north-east):** Ascendancy, Guild Hall, Hunters' Hall and Training Yard together. Target: all within 45 steps (today up to 80).
- **Spire Manor (south-east):** the manor inside its own walled grounds, with a gate on the avenue, a garden and a forecourt. It is the largest thing in town after the Hearth, and visible from the plaza.
- **Three neighbourhoods, each with its own kind of home** (the new house plans in `maps/house_plans.py`):
  - *Lantern Row* (south-west): small, cheap homes in tight lanes.
  - *Greenside* (north-west): garden houses round Hearthgate Green.
  - *Northside and Southgate Row:* mid-size homes, some with an upstairs.
- **Kept:** the Old Well Yard with the Underkeep grate in the south-west corner, the Coach Yard by the south gate, 30 houses inside the walls.

## What it costs

This is a rebuild of Hearthgate's part of the map, about a day of work: the layout, the dressing, the tests that know where things are, and a walk in the client. Everything outside the walls stays. Characters standing in town are put back on the Hearthstone. It should happen while nobody is using the map for something else (the Underkeep rebuild is using it now).

## Done when

- The plan check reports every shop door within 25 steps of the Hearthstone and the Crown Quarter within 45.
- Rendered and looked at, every changed area, by the map quality rules.
- Boot test passes; the manor, depot, bank, shop and housing tests pass on the new spots.
- A fresh test character walks Hearthstone to each service in the client.

---

## The tile plan (built 2026-11-27)

The exact numbers live in `maps/hearthgate_plan.py`, which both the builder (`maps/hearthgate.py`) and the checker (`tools/hearthgate_plan_check.py`) read, so this table and the map cannot drift apart. Coordinates are town-relative: x 0..111 west to east, y 0..95 north to south. Rectangles are x, y, width, height, walls included. Picture: `docs/HEARTHGATE_PLAN.png`.

**Wall and plaza.** The wall's corners are cut 12 tiles (an octagon, a staircase of wall pieces on the diagonals). Gates unchanged: north and south x 55–58, west and east y 48–50. Hearth Plaza is a circle 33 tiles across centred on (56.5, 49), marble with a flagstone rim; the Hearthstone is (56, 49), a black marble square, the same tile as before (so `temple_hearthgate` did not move).

| Place | Rectangle | Door(s) | Inside |
|---|---|---|---|
| The Hearth | 42, 12, 30, 23 | open archways: south x 55–58 (faces the Hearthstone), north x 56–57, west and east y 22–24 | bank (south-west, by the front), depot wing (south-east, 10 lockers), depot wing (north-west, 10 lockers), chapel (north-east); gallery on level 2 (10 more lockers, trade tables); the Hall of Climbers tower on level 3 (49, 18, 16, 11) |
| Weaponsmith / Armorer | 31, 38, 10, 10 | (40, 40), (40, 45) east | two rooms, inner wall at y 42 |
| General Store / Quartermaster | 31, 51, 10, 10 | (40, 53), (40, 58) east | inner wall at y 56 |
| Runewright / Fletcher | 73, 39, 10, 9 | (73, 41), (73, 45) west | inner wall at y 43 |
| Alchemist / Tailor | 73, 51, 10, 10 | (73, 53), (73, 58) west | inner wall at y 56 |
| Housewright / Post Office | 60, 65, 11, 10 | (60, 67), (60, 71) west | inner wall at y 69 |
| The Lantern & Lark (inn) | 43, 65, 11, 13 | (53, 67) east | bar, tables, rooms upstairs |
| Guardhouse | 60, 2, 9, 8 | (60, 6) west | Captain Dorrow outside |
| Ascendancy | 74, 22, 12, 9 | (74, 26) west | Crown Quarter |
| Hunters' Hall | 74, 31, 14, 8 | (74, 35) west | trophy loft by ladder |
| Guild Hall | 84, 39, 13, 9 | (90, 47) south | meeting room upstairs |
| Training Yard | 98, 37, 11, 11 | gap (99–100, 47) | fenced, no roof |
| Spire Manor grounds | 80, 63, 28, 22 | gate (93–95, 63) | the manor at (83, 67), door (94, 67); forecourt, trees, flowers |
| Spire Gardens | 84, 52, 26, 9 | open | public garden; Manor Walk (x 93–95) from the East High Road to the gate |
| Coach Yard | 60, 82, 10, 11 | gap (60, 87) | by the south gate |
| Old Well Yard | 2, 62, 9, 9 | open | Underkeep grate kept at (5, 66) |
| Hearthgate Green | 12, 13, 18, 21 | open | pond, benches, trees |

**Streets.** North Avenue 55, 1, 4, 11; South Avenue 55, 65, 4, 30 (marble). West High Road 1, 48, 40, 3; East High Road 73, 48, 38, 3 (flagstone). Lanes (cobble): North Lane 3, 10, 106, 2; Hearth West Street 40, 12, 2, 26; Hearth East Street 72, 12, 2, 27; Crown Lane 86, 20, 23, 3; Green Lane 10, 12, 2, 36; Lantern Lane 2, 59, 26, 2; Lantern Close 11, 68, 17, 3; Lantern Cut 27, 51, 3, 30; Southgate Lane 10, 81, 45, 3; Coach Lane 59, 75, 20, 3.

**Plaza.** Monument (49, 42), Arena Champion (49, 56), Beacon bowls (62–68, 42), fountain (64, 56), Vesper (59, 53), notice board (53, 45), six free stalls, benches facing the Hearthstone, a tree in a bed at four corners, lamps round the rim.

**30 houses** (lots; `maps/house_plans.py` gives each its own plan):

| Street | Lots (x, y) | Size | Door | Kind |
|---|---|---|---|---|
| Northside | (14,2) (23,2) (32,2) (41,2) (70,2) (79,2) (88,2) | 8 x 8 | south, onto North Lane | mid-size, two with an upstairs |
| Crown Row | (74,12) (83,12) (92,12) (101,12); (89,23) (98,23) | 8 x 8 | south / north, onto Crown Lane | the best homes, all two storeys |
| Greenside | (2,13) (2,22) (2,31) (32,13) (32,22) (13,37) | 8 x 8 | facing the Green | garden houses |
| Lantern Row | (3,52) (11,52) (19,52) (12,61) (20,61) (12,71) (20,71) | 7 x 7 | north | small, cheap, tight lanes |
| Southgate Row | (13,84) (22,84) (31,84) (40,84) | 8 x 8 | north, onto Southgate Lane | mid-size, two with an upstairs |

**Measured walks** (steps from the Hearthstone, no diagonals, on the built map; `python tools/hearthgate_plan_check.py --walk`): nearest locker 26, bank 24, Trader Osric 22, priest 34; shop doors 19 to 25 (goal 25, was 29 to 50); Ascendancy 40, Hunters' Hall 31, Guild Hall 35, Training Yard 44 (goal 45, was up to 80); gates 46 to 56.
