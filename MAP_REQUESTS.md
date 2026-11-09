# Map requests

Real maps that are needed. Every map below already has a **script-generated placeholder** so the game is playable without it. Jay can make these himself or hand this file to another agent/mapper.

Format rules for whoever makes them:
- Canary / Tibia 15.11 item ids, `.otbm` format.
- No CipSoft map pieces (no copying areas from the official map).
- Keep the listed points (temple, doors, boss room, stairs) at the listed positions, or update the points file in `maps/src/<map>/points.csv` so the scripts keep working.

| # | Map | Size | Must contain | Placeholder | Status |
|---|---|---|---|---|---|
| M1 | Floor 1 — Hearthgate Plains | 400 × 400 | Hearthgate (temple, depot, bank, market, monument square, 24 houses, Arrival Yard), Millcross village (6 houses), 3 starter fields, 14 hunting camps, Old Watchtower apex spawn (3 layers + hidden Ram Pens), river with fishing spots, the Pass arena, 3-level labyrinth, boss room, stair to Floor 2. Layout notes: `docs/11_FLOORS_AND_MAPS.md` (Floor 1 section) | task 1.8 | needed |
| M2 | The Underkeep, Wing 1 | 70 × 50 | Drain grate entrance, water channel, columns hall, daily chest room, sealed doors to Wing 2 | task 2.10 | needed |
| M3 | Floors 2–10 | 300 × 300 each | Town, camps, apex spawn, pass, labyrinth, boss room (DESIGN.md §3.1) | phases 4–5 | later |
| M4 | The Cobalt Labyrinth (Floor 10) | 3 levels, 80 × 80 | Blue-lit maze, huge double door, Azhrakkar's boss room (round, 30 × 30) | task 5.5 | later |
