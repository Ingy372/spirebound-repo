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
