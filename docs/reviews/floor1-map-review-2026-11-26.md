# Floor 1 map review (2026-11-26)

Written for Jay. Review only: I changed nothing on the map. Fixes are with the session "Floor 1 fixes (Opus)".

**How I looked.** I drew the map with the project's own renderer (`tools/maprender.py`, the real sprites, the same picture the client shows) and looked at every picture: the whole floor in one view, Hearthgate in four close-up quarters plus the roof view, the Arrival Yard, the surface in nine sections, the Pass and the way to the labyrinth close up, the party-cave level, the Underkeep's three levels, one party cave close up, Burrow Hills with its hill level drawn, and the Axe-Lord's hall with its private copy. The pictures are in `.local/scratch/rv/` on your PC (not in the repo, because they contain the base game's art).

**What I did not do.** I did not walk it in the client. Most surface pictures were at about a third of full size, so a single wrong tile (one missing wall piece, one blocked doorway) could still be hiding; the automated checks cover those better than my eyes (`tools/hunt_check.py` reports every ground reachable and within its danger limit). I did not look closely at labyrinth levels 2 and 3, the other five party caves, or the hill levels of grounds other than Burrow Hills. NPCs and monsters are not drawn by the renderer.

---

## 1. Plain-English summary

**Grade: B for being correct and tidy, D+ for looking hand-made. Overall C.**

The map is clean. Walls and corners are right everywhere I looked, buildings have roofs, big objects are whole, nothing is dumped on roads or in doorways, shorelines are smooth, and the town is easy to read. That is real work and it shows.

But it looks like what it is: a generator's output. The floor is a square lawn with rectangles placed on it. Every hunting ground is a box. Most roads are ruler-straight with right-angle corners. Houses are identical empty squares in rows. The Underkeep, which you named a must-have, is six huge bare rectangular rooms. A Tibia veteran will see "auto-generated" within a minute of leaving town.

And there is one real hole: **the Gate Hound can be walked around.**

**Top problems**

1. **The Pass does not seal the labyrinth (High, a real bug).** The Gate Hound's arena is a walled box in an open meadow. The paved way from its sealed north gate to the labyrinth has no walls, so anyone can walk round the arena on the grass and into the maze. The "labyrinth is open!" moment is meaningless.
2. **The Underkeep is six big empty rooms (High).** No corridors, cells, side rooms or stairs. Wing 1 is a single hall about 70 by 50 tiles with a grid of pillars and one water channel; the other five wings are bare rectangles with a few pillars.
3. **Everything is a rectangle on a lawn (Medium).** Hunting grounds have hard square outlines; the rocky grounds are flat grey slabs with straight edges against the grass; neighbours sit a tile or two apart like floor tiles.
4. **Homes and public rooms are empty boxes (Medium).** About 80 houses, cabins, huts and cottages are the same bare square with a door: no beds, no inner walls, no furniture. The Hunters' Hall, Guild Hall, Spire Manor, the inns and the Registrar's hall are large rooms with almost nothing in them.
5. **Roads are straight lines, and a few go nowhere (Medium).** The design says winding roads; outside the three main roads they are straight with square corners, and two simply stop in the grass.

**What is good**

1. Walls, corners, doors and roofs are consistent across every building I saw.
2. Hearthgate's layout is clear: the Hearth in the middle, four gates, streets that lead somewhere, a market with stalls and a notice board.
3. Burrow Hills with its hill level, and Toad Pond with its ponds and jetties, look like places. They show what the other grounds could be.
4. The Axe-Lord's hall has presence: black marble, a red runner, two rows of pillars, braziers.
5. No half objects, no clutter on paths, clean shorelines, quiet gates. The map quality rules in `CLAUDE.md` are being followed.

---

## 2. Findings

Severity as in the main review. Positions are map coordinates (x, y, level); level 7 is the surface.

### M1. The Gate Hound's seal can be walked around (High)
- *For players:* the tower's first big moment is "the Gate Hound has fallen, the labyrinth is open to all". In fact the labyrinth is open from the first minute to anyone who walks past the arena. The Axe-Lord's own door is still locked by the Stair Key, so the floor boss is safe, but the labyrinth's monsters and the announcement are not.
- *Detail:* the arena is a 24 by 20 walled box at about (1220-1243, 1070-1089, 7) with the sealing boulders in its north gap. From there a strip of paving runs north to the maze's entrance at about (1232, 1043). The strip is floor only, no walls, and the maze's south entrance is an open gap (`maps/layout_floor1.py`, the "corridor from the Pass to the maze" line). No script guards the maze; only the boulders are removed when the Hound dies.
- *Fix:* wall both sides of the corridor so the only way in is through the arena; check the other floors' generated Passes for the same gap; add an automatic check that no walkable path reaches the maze while the boulders stand.

### M2. The Underkeep is six bare halls (High)
- *For players:* the growing secret dungeon under the city should feel old, dark and cramped. It is a warehouse: you step in and see the whole wing.
- *Detail:* level 8 holds two rooms of about 70 by 50 and 58 by 40 tiles; levels 9 and 10 hold two more each, 30 to 40 tiles a side. Decoration is a pillar grid in Wing 1, a water channel, a tiny strongbox room, and scattered bones and braziers. `FLOOR1.md` describes "pale stone halls with lamps, a storeroom by the entrance, a column hall", which is more than what is there.
- *Fix:* rebuild each wing as real dungeon: corridors two or three tiles wide, guard rooms, cells, a collapsed section, a flooded section, locked side rooms, at least one loop and one dead end with a reward, and the secret the design promises in every wing. Wing 1 first.

### M3. Hunting grounds are boxes (Medium)
- *For players:* from outside, every ground is a square hedge, a square tree wall or a square of boulders. Inside they are fine to hunt. It is the outline that says "generated".
- *Detail:* all 15 grounds are axis-aligned rectangles 38 to 84 tiles wide. The four rocky grounds (Burrow Hills, Old Quarry, Shard Fields, Fallen Bastion) are grey slabs with ruler-straight edges on the lawn; the Old Quarry and Burrow Hills are separated by a strip of grass a few tiles wide. Reedmarsh's ponds are cut off square at the ground's border, with loose 2 by 2 squares of water at the corners and a bright stair-stepped fringe.
- *Fix:* let each ground's outline wander (push the wall in and out by several tiles, round the corners), blend rock into grass with a ragged band of gravel and boulders, and give Reedmarsh a natural shore.

### M4. Roads are straight with square corners (Medium)
- *Detail:* the north, south and east roads out of Hearthgate wind nicely. The rest do not: the Old Watchtower road, the Reedmarsh road, the Bramble Run road, and the road to Smugglers' Ridge, which runs dead straight down the east edge of the map for about 170 tiles. `FLOOR1.md` promises "winding dirt roads".
- *Fix:* run every road through the same winding routine the main roads use; move the east road off the map edge.

### M5. Roads that stop in the grass (Medium)
- *Detail, approximate positions:* (a) the road coming south on the west side ends in open lawn at about (1075, 1193), some 15 tiles short of Millcross; (b) the east branch of the south-gate road ends at about (1300, 1368), short of the ruined well it seems to aim for.
- *Fix:* connect each to something, or end it at a landmark (a ruin, a signpost, a camp fire).

### M6. One river crossing looks like a dirt dam (Medium, check close up)
- *Detail:* the southern crossing at about (1115, 1262) is a proper wooden bridge. The crossing on the Millcross road at about (1125, 1219) appears in the render as the brown road running straight across the water. At my zoom I cannot be certain it is not a low bridge. `FLOOR1.md` says both are wooden bridges.
- *Fix:* render it at full size; if it is dirt, build the bridge.

### M7. Every home is the same empty box (Medium)
- *For players:* house hunting is choosing between identical squares. Nothing says "this one is the nice one".
- *Detail:* 30 houses in Hearthgate, 20 Wallside Cabins in two blocks of ten, 10 Fisher's Huts, 8 Millcross cottages: all a bare wooden floor about 7 by 6 inside four walls, in straight rows. No beds, no inner walls, no fireplace, no furniture. The Fisher's Huts stand in a 2 by 5 grid on bare grass with no path to them. Already known as Q69 for Hearthgate; it applies everywhere.
- *Fix:* five or six house plans (one room, two rooms, L-shape, with a yard, with a loft), each with a bed and a few fixtures, mixed along each street; paths and a jetty for the huts.

### M8. Public buildings are large empty rooms (Medium)
- *Detail:* Hunters' Hall (about 16 by 12 inside): one carpet strip, two small statues, a ladder. Guild Hall: a blue carpet and a short counter. Spire Manor, the showcase house you sell: one marble hall with a fountain, four pillars and two benches. The Lantern & Lark: a counter and five tables in a room that would hold twenty. The Registrar's hall, where every player makes their two biggest choices: a marble room with a red carpet and nothing else.
- *Fix:* furnish each for what it is (trophies and a map table in the Hunters' Hall, a desk and banners for the Registrar, rooms and a kitchen for the inn, real rooms for the Manor).

### M9. Millcross has no mill (Medium, not seen)
- *Detail:* quests come from "Miller Agna", a secret is "under the Millcross mill", and the design promises windmills. I saw eight cottages, an inn and a wheat field, and no mill building. It may be too small to spot at my zoom.
- *Fix:* check; if missing, build a windmill by the field.

### M10. The Arrival Yard is a walled lawn (Medium)
- *For players:* this is the first screen of the game. It is a long white-walled rectangle of grass with a path, the Old Granary, four plain cross-walls and a small marble room.
- *Detail:* roadmap P7 has dressed it (pillars, hedges, flower beds) and it is tidy, but there is no sight of the tower, no height, no crowd. The yard also stands in open country south-east of the city as a blank white box seen from outside.
- *Fix:* your call how much; at least give the outside a reason to look as it does.

### M11. Large empty lawns (Low)
- *Detail:* the south-east corner (roughly 120 by 60 tiles), the south-west, the far west and the north-west hold grass, a few bushes and nothing to find. The map is 400 by 400 and perhaps a third of it is this.
- *Fix:* as Step 4 of the roadmap adds ground for levels 17 to 30, put it here; meanwhile scatter small landmarks (a shrine, a camp, a wreck, a standing stone) so wandering is rewarded.

### M12. The labyrinth is an open-air maze in a field (Low)
- *Detail:* level 1 of the labyrinth is on the surface: a 43 by 31 block of grey walls in a meadow. Nothing marks it as the foot of a tower.
- *Fix:* with M1's walls, add a gatehouse or tower base so it reads as the entrance to the Spire's stair.

### M13. The Old Watchtower is a box inside a box (Low)
- *Detail:* a square stone wall round a lawn with scattered rubble, and inside it a square walled dirt yard about 22 by 20. No tower.
- *Fix:* a round or broken tower base, collapsed wall sections, a real courtyard.

### M14. Party caves all share one shape (Low)
- *Detail:* on the cave level each cave is a ring corridor three to five tiles wide running round a solid block, with one or two cross tunnels. The Alpha's Den, seen close up, is exactly that.
- *Fix:* vary them: a big central chamber, branching dead ends, a narrow choke point, an underground pool.

### M15. Small things (Low)
- The centre of Hearthgate Green is a diamond of brown mound tiles that reads as a mistake where a pond or statue is expected.
- A dense strip of trees is pressed against the outside of the city's west wall.
- Smugglers' Ridge and the Fallen Bastion are mirror images of the Bandit Road and Shard Fields (already in the main review).
- The city wall's gates are plain gaps: no gatehouse or towers.
- The plateau on top of Burrow Hills has blocky stair-step edges.

### M16. Correction to the main review: the three new grounds do have trails
The plan checker says "NO TRAIL TO" the Bramble Run, Smugglers' Ridge and the Fallen Bastion. The drawn map shows a road from each gate to the road network. The checker is reading something out of date; the map is fine.

---

## 3. Suggested order of work

1. **M1** the Pass (small, a real bug).
2. **M2** Underkeep Wing 1 rebuilt as a real dungeon (large; the other wings can wait for their floors).
3. **M5, M6, M9** dead-end roads, the river crossing, the mill (small).
4. **M7, M8** house plans and public interiors (medium; pairs with roadmap N3 and Q69).
5. **M3, M4** softer outlines and winding roads for every ground (medium to large; best done in the generator so Floors 2 to 10 inherit it).
6. **M10 to M15** as polish, or left for the Cowork finishing pass you planned.

## 4. Questions for Jay

1. **How hand-made should Floor 1 look before friends see it?** Items M3, M4, M7 and M8 are the difference between "tidy generated map" and "a world". They are also the kind of thing the Cowork polish pass was meant for.
2. **The Underkeep:** is a real dungeon rebuild of Wing 1 worth doing before the friends test, given it is a secret most testers will not find?
3. **Empty land:** fill it with more hunting ground (helps launch-day crowding) or shrink the map so the floor feels fuller?
