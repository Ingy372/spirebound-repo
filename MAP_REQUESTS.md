# Map requests

Real maps that are needed. Every map below already has a **script-generated placeholder** so the game is playable without it. Jay can make these himself or hand this file to another agent/mapper.

Format rules for whoever makes them:
- Canary / Tibia 15.11 item ids, `.otbm` format.
- No CipSoft map pieces (no copying areas from the official map).
- Never put a sealed area directly above or below a walkable one (spells and holes can cross levels), and put each next-floor stair behind a real door (REVIEW.md 3.2, 5.3).
- Floor 1 must hold a launch-day crowd: about 1,500 monsters across 14+ camps from easy to hard, with caves under some camps (REVIEW.md 5.2). Keep bank, depot, supply shop and temple a few steps apart.
- Keep the listed points (temple, doors, boss room, stairs) at the listed positions, or update the points file in `maps/src/<map>/points.csv` so the scripts keep working.

| # | Map | Size | Must contain | Placeholder | Status |
|---|---|---|---|---|---|
| M1 | Floor 1 — Hearthgate Plains (placeholder: `docs/previews/floor1_z7.png`) | 400 × 400 | Hearthgate (temple, depot, bank, market, monument square, 24 houses, Arrival Yard), Millcross village (6 houses), 3 starter fields, 14 hunting camps, Old Watchtower apex spawn (3 layers + hidden Ram Pens), river with fishing spots, the Pass arena, 3-level labyrinth, boss room, stair to Floor 2. Layout notes: `docs/11_FLOORS_AND_MAPS.md` (Floor 1 section) | task 1.8 | needed |
| M2 | The Underkeep, Wings 1–6 (placeholder: under Hearthgate, z 8–10) | 70 × 50 (Wing 1), 40–60 wide (Wings 2–6) | Drain grate entrance, water channel, columns hall, daily chest room, sealed doors to Wing 2 | task 2.10 | needed |
| M3 | Floors 2–10 | 300 × 300 each | Town, camps, apex spawn, pass, labyrinth, boss room (DESIGN.md §3.1) | phases 4–5 | later |
| M4 | The Cobalt Labyrinth (Floor 10) | 3 levels, 80 × 80 | Blue-lit maze, huge double door, Azhrakkar's boss room (round, 30 × 30) | task 5.5 | later |

Placeholder notes: walls in the generated map use a single wall family with guessed orientation, and floor changes are blue portals instead of stairs. Both are fine for testing and go away with the real map.

## M5 — One new Underkeep wing per season (for season 2 onward)
Each season should add a fresh Underkeep wing below the existing ones, so veterans have something new under Hearthgate. Size like Wing 1 (about 70×30 tiles), one floor level, a mini-boss room at the far end, and a spot for the entrance portal next to the previous wing's exit. Any theme you like; the script-made placeholder works until you draw one. Not needed before the first season ends.
