# Floor 1 hunting grounds, third pass: bigger, layered, on several levels (plan, 2026-11-14)

Jay, 2026-11-14: *"im still not satisfied with the hunting field. it is a major step up from the first pass, but still not complete. im feeling overhelmed when i walk into a zone with nonstop monsters flooding to me. i think the zones need to bigger... utilize multi height levels as well. layer the monsters throughout the spawn more like real tibia does... certain areas are fine but the whole spawn shouldn't be a massive swarm."*

**Changed 2026-11-16 (Jay): the group sizes and the head-count limits in Parts 3 and 5 are replaced by Part 10 (habits, ground types, danger budget; `DESIGN.md` 9.4). The layouts, levels and positions in this plan stay.**

**This is a plan only. Nothing in the game has changed.** It replaces Parts 4.1, 5 and 6 of `FLOOR1_WILDS_PLAN.md` (the four-loop skeleton). Everything else in that plan stays: the experience stages, the ladder, the respawn rule, the roads idea, the crowd system (with the changes in Part 7 here).

Part 1 is for Jay. Parts 2 to 9 are the build instructions for the next model.

---

## Part 1. For Jay: why it swarms, and what changes

### Why it feels like a flood (measured on today's map)
1. **A whole loop fits on one screen.** Each hunting loop is a ring about 18 tiles by 12. Your screen shows 15 by 11. So all 18 monsters of a loop are within about one screen of you the moment you step in.
2. **Monsters do not need to see you.** I read the engine's code: a monster picks you as a target as soon as you are in its range on the same level, walls or not. It only needs a clear line to *hit* you. So the rock in the middle of a loop hides nothing: the whole loop wakes up and walks round to you from both sides.
3. **Every group is three.** There are no single monsters and no pairs anywhere. Real Tibia's early hunting grounds are mostly ones and twos.
4. **The trails are 2 tiles wide.** There is nowhere to step back to and nowhere without monsters.
5. **It is three to four times denser than Tibia.** Measured on the map (H1): one monster for every 13 to 15 tiles you can walk on. Wherever you stand, on average 12 monsters can come at you, up to 26; the gate clearing itself has 4 to 6. Tibia's early caves are nearer one for every 40 to 60.
6. **Not the weekend bonus.** Friday 13 November had no bonus and Saturday 14 is Double Experience. "Rapid Respawn" (which fills every crowd spot) was not on.

### What real Tibia and good servers do
- **Ones and twos near the entrance, bigger groups deeper in.** The far end and the lower levels are where it gets busy. You choose how deep to go.
- **Long quiet stretches.** Corridors and empty clearings between groups, so a fight ends before the next begins.
- **Levels stack.** A cave or hill has several levels joined by ramps, stairs and holes. Each level is its own fight: monsters never notice someone on another level, so stairs are also the way out when it goes wrong.
- **A few packed rooms, clearly dead ends.** The "swarm" exists, but as a room you decide to enter, usually for a team.
- A mapper on OTLand put it simply: for a slow, Tibia-like server you need "wider areas of a map" with sparse monsters.

### What I propose
1. **Each ground gets about twice the land, and two to four levels.** Hills and ridges you climb, tunnels and hollows you go down into. About four to five times today's walking room in total.
2. **The same number of monsters, spread out.** So experience per hour and the Floor 1 timetable barely move. Fewer monsters per screen, not fewer monsters.
3. **Three bands in every ground: calm, middle, deep.** Calm (by the gate) is singles and pairs. Middle is pairs and the odd three. Deep (far end, upper or lower level) is threes. A sign marks each step.
4. **A hard limit on how many monsters can come at you at once**, checked by a tool on every build: 3 in the calm band, 4 in the middle, 6 deep. Only marked dead-end "nests" and the party caves go higher, and you never have to enter those.
5. **Room to fight.** Paths 3 to 5 wide, a clearing at every group, and rest spots with no monsters in range.
6. **Still four hunting routes per ground** (one player each, a lap for the cavebot), but they are winding circuits through the land, no longer four identical rings.
7. **Extra crowd monsters go into side pockets**, not between the normal groups, and a weekend bonus no longer fills a ground for a player who is alone.

### In numbers
| | Today | Planned |
|---|---|---|
| Land per standard ground | 60 x 40 | about 84 x 60, plus 1 to 3 more levels |
| Walking room per monster (surface) | about 6 tiles | 45 or more |
| Monsters that can reach you at once, by the gate | up to 18 | 3 at most |
| Group sizes | all threes | singles, pairs, threes; fours and fives only in nests and party caves |
| Monsters on Floor 1 | about 1,000 + caves | the same |
| Levels used | surface, plus 6 party caves | every ground has at least 2 levels; 9 of 12 have 3 or more |

### Questions (in `QUESTIONS.md`; I have assumed my recommendation)
- **Q37.** Cavebot allowed on the new solo cave and hill levels, still refused in the party caves? Recommendation: yes.
- **Q38.** Which areas felt fine to you? I have assumed the party caves and the Old Watchtower's inner room should stay packed, and everything else calms down.
- **Q39.** Test two pilot grounds first (the Ratwarren and Burrow Hills) before the other ten are rebuilt? Recommendation: yes, but the builder keeps going while you test.

---

## Part 2. Rules for the builder (read first)

1. Follow every rule in `CLAUDE.md`, above all the map quality rules, and Part 2 of `FLOOR1_WILDS_PLAN.md` (do-not-touch list, keep every id and name, coordinates are Floor 1 tiles with 1000 added by the builder).
2. **Levels:** surface is z 7. "Up" is z 6 (and z 5 where a ground says so). "Down" is z 8, "deep" is z 9. Smaller z is higher.
3. The plan table stays in `maps/floor1_plan.py`; the builder is `maps/wilds.py`. Replace the loop skeleton; do not keep both.
4. One task = one commit, boot test passing, in the order of Part 9. If a rule cannot be met, write why in `QUESTIONS.md`, choose the nearest thing that passes the checker, and carry on.
5. **Never relax a limit in Part 3 to make a ground pass.** Make the ground bigger, move a route to another level, or split a group instead.
6. Tick a task only when its check goes through the real map and the real server (CLAUDE.md, "Ticking tasks").

### Engine facts this plan relies on (Canary 3.6.1; H0 confirms them in game)
| Fact | Source | Used for |
|---|---|---|
| A monster only targets a creature on its own level (`isTarget`: different z returns false) | `monster.cpp`, read 2026-11-14 | levels are separate fights; stairs are exits |
| Line of sight is checked to attack, not to pick a target | `monster.cpp` (`canUseAttack` uses `isSightClear`; `onCreatureFound` does not) | walls do not hide players, so spacing is by distance only |
| A monster that leaves its spawn range is sent home (`deSpawnRange = 2` levels, `deSpawnRadius = 50` tiles in config) | `config.lua.dist`, `onThink` | groups cannot be dragged across a ground |
| How far a monster notices a player (the number `NOTICE`) | The engine lets a creature see 11 tiles each way (`MAP_MAX_VIEW_PORT_X/Y = 11` in `map_const.hpp`); the monster's own check may be smaller and was not readable. H0 confirms in the client | every limit in Part 3. Use 10 (`tools/hunt_check.py`) until measured |
| Monsters return on top of a player; the real wait is about twice the spawn-file number | W0, `PROGRESS.md` 2026-11-13 | unchanged |

---

## Part 3. The calm rules (the checker enforces every one)

**Pull** of a tile = the number of monsters whose home spot is on the same level and within `NOTICE` tiles of it (the larger of the x and y distance; no walls considered). It is the most monsters that can come at a player standing there.

### 3.1 Bands
Every walkable tile of a ground belongs to one band. Bands are set by walking distance from the gate, level by level.

| Band | Where | Pull limit | Group sizes allowed | Share of the ground's monsters |
|---|---|---|---|---|
| Approach | the hub, the first 12 steps in from the gate, 8 steps round every stair or ramp landing | 0 | none | 0 |
| Calm | the nearer part of the surface | 3 (2 in the Ratwarren) | 1 and 2 | 30 to 40% |
| Middle | the rest of the surface, the first other level | 4 | 1, 2, and at most one 3 in any 20 x 20 area | 35 to 45% |
| Deep | the far end, the furthest level | 6 | 2 and 3 | 20 to 30% |
| Nest | a dead-end room in the deep band, at most one per route, entered through a neck 2 or 3 wide, with a warning sign and bones outside | 8 | one group of 4 or 5 | counted in Deep |
| Party cave | the deepest level of the seven grounds that have one | 8 | 4 | separate (32 per cave, as today) |

### 3.2 Whole-ground limits
1. **Breathing room:** on every level at least 25% of walkable tiles have pull 0 (party caves excluded). *(2026-11-14: a second rule, "60% at pull 2 or less", was dropped while building the Ratwarren: the band limits already cap crowding, and that rule worked against layering.)*
2. **A rest spot within 20 steps:** from every walkable tile, a pull-0 tile can be reached in 20 steps or fewer.
3. **Spacing between group homes:** at least `NOTICE + 3` in the calm band, `NOTICE + 1` in the middle, `NOTICE - 1` deep, 12 in party caves.
4. **Density** (walkable tiles per monster, per level): surface 45 or more (50 in the four starter grounds); up and down levels 35; deep 25; party cave 20.
5. **Room to fight:** route paths are at least 3 wide everywhere, 4 or 5 for most of their length. Every group stands in a clearing with at least 40 walkable tiles inside 4 steps of its home. No path narrower than 3 for more than 6 tiles except a nest's neck.
6. **Depth means danger:** along each route, a group's size never drops by more than 1 as you go deeper, and the ground's "soft" monster (Part 5) appears only in the calm band.
7. **Crowd spots** (Part 7) are counted too: with every crowd spot switched on, each band's pull limit may be exceeded by 2 at most.

### 3.3 The checker (`tools/hunt_check.py`, task H1)
- Reads the built map (after `Map.finish`), the monster groups, the crowd spots and the band of each tile.
- Prints one line per ground and level: walkable tiles, monsters, density, highest pull per band, share at pull 0 and at 2 or less, worst distance to a rest spot, closest pair of groups, and `OK` or the broken rules.
- Writes a heat-map picture per ground and level to `docs/previews/hunt_<id>_z<z>.png`: pull 0 white, 1-2 green, 3-4 yellow, 5-6 orange, 7+ red, group homes as dots, routes as lines.
- Exit code 1 if any rule breaks. From H3 on it runs inside the map build and the boot test.

---

## Part 4. Where the grounds go (all checked: nothing overlaps, nothing in the river)

| Id | Ground | Levels | x, y | Width x height | Gate (side, at) | Was |
|---|---|---|---|---|---|---|
| starter_west | The Ratwarren | 1-4 | 134, 242 | 38 x 40 | south, (153, 282) | same land; grows downward |
| starter_east | Toad Pond | 3-7 | 294, 230 | 58 x 52 | south, (323, 282) | 38 x 40 |
| starter_south | Sproutling Glade | 5-10 | 184, 338 | 44 x 56 | north, (206, 338) | 38 x 40 |
| wasp_fields | Waspgrass Fields | 7-12 | 160, 180 | 68 x 50 | east, (228, 205) | 44 x 34 |
| boar_meadow | Boar Meadow | 9-15 | 140, 338 | 39 x 57 | north, (159, 338) | same land; grows up and down |
| burrow_hills | Burrow Hills | 11-16 | 240, 170 | 84 x 58 | west, (240, 199) | 60 x 40 |
| wolf_copse | Wolf Copse | 12-18 | 8, 254 | 80 x 60 | east, (88, 284) | 60 x 40 |
| reed_marsh | Reedmarsh | 14-19 | 10, 324 | 86 x 68 | north, (53, 324) | 52 x 48 |
| thornsnap_hollow | Thornsnap Hollow | 14-20 | 142, 104 | 84 x 64 | east, (226, 136) | 60 x 40 |
| shard_fields | Shard Fields | 17-24 | 342, 300 | 54 x 92 | north, (369, 300) | 52 x 48 |
| bandit_road | The Bandit Road | 19-27 | 332, 146 | 60 x 76 | south, (362, 222) | 52 x 48 |
| old_quarry | The Old Quarry | 23-30 | 240, 98 | 64 x 62 | west, (240, 129) | 60 x 40 |

The Old Watchtower keeps its walls and place (Part 5).

**Levels below ground may be larger than the surface rectangle** by up to 8 tiles a side, if the existing clash check passes (nothing else dug within 6 tiles at that depth; the Underkeep is under Hearthgate at z 8 to 10). The Ratwarren's lower level may use x 126 to 170, y 236 to 290.

### Roads and trails that move
Roads never pass through a ground and end at its gate, as before. Proposed lines; adjust by the smallest step that makes `tools/wilds_plan_check.py` print `problems 0`.

| Road or trail | New line |
|---|---|
| East Road | east gate (288, 285) to the new East Cross (356, 285) |
| Toad Pond gate | East Road (323, 284) to (323, 282) |
| Bandit Track | East Cross (356, 285) to (356, 240) to (362, 226) to (362, 222) |
| Shard Track | East Cross (356, 285) to (369, 292) to (369, 299) |
| Glade trail | South Road (231, 335) to (206, 335) to (206, 337) |
| Wasp gate | Pass Road (230, 205) to (228, 205) |
| Burrow trail | Pass Road (234, 199) to (239, 199) |
| Quarry trail | Pass Road (234, 129) to (239, 129) |
| Thornsnap trail | Pass Road (230, 136) to (226, 136) |
| Copse Road | Millcross south gate (70, 239) to (94, 246) to (94, 316) to (53, 320) to Reedmarsh (53, 323) |
| Copse gate | Copse Road (94, 284) to Wolf Copse (88, 284) |
| Standing stones (east) | move to (378, 262) |

Unchanged: Pass Road, South Road, Mill Road, River Path, Millcross Road, Shrine Path, Ratwarren gate, Cabin Lane, Watch Road. Remove the size rule from `tools/wilds_plan_check.py` (it expects the old loop sizes) and redraw `docs/FLOOR1_WILDS_PLAN.png` with one outline per level.

Secrets keep their ids and must end on a walkable tile inside their ground (s2 in Old Tusk's wallow, s5 in the Old Quarry, s7 Bandit Road, s9 Wolf Copse, s11 Thornsnap Hollow); list any move in `PROGRESS.md`. Guarded zones: each starter ground's rectangle grown by 6, **on every level it has**. Everything else Open, on every level.

---

## Part 5. The grounds, one by one

Every ground keeps **four routes** of the same size as today's loops (12 monsters each in the four starter grounds, 18 each elsewhere) and its respawn time from `maps/floor1_plan.py`, so totals do not change: 48 per starter ground, 72 per standard ground, 32 per party cave. A route is a closed circuit, so one lap is a cavebot route.

A route's groups, in order from its start:
- **12-monster route:** 6 singles, 3 pairs (9 groups). In the Ratwarren's lowest route: 4 singles, 2 pairs, 1 nest of 4.
- **18-monster route:** calm band 4 singles + 2 pairs; middle 2 singles + 3 pairs; deep 2 threes, or 1 three + a nest. Adjust between routes so the ground meets the shares in 3.1.

"Soft" = the easier monster used for some calm-band singles, so the low end of the level range has something to hunt by the gate.

| Ground | Surface (z 7) | Up (z 6) | Down (z 8) | Deep (z 9) | Soft monster | Look |
|---|---|---|---|---|---|---|
| The Ratwarren | **The Yard:** route A, singles only | none | **The Warren:** routes B, C, D in earth tunnels with wide chambers; D ends in the Nest (4 rats) | none | none | Bushes and mounds above; `dungeon.cave` below. Two ways down (a burrow by the hub, another at the far end) |
| Toad Pond | routes A, B, C round four ponds of different shapes, with small islands reached by `scenery.bridge` | none | **The Sunken Grotto:** route D, a wet cave under the largest pond | none | Field Rat | Fishing on every pond |
| Sproutling Glade | routes A, B, C through fern groves and mushroom rings | none | **The Root Hollow:** route D, under a great tree in the middle | none | Hopper Toad | The tree is the landmark; stairs down between its roots |
| Waspgrass Fields | routes A, B, C through flower meadows cut by hedges | **Hive Knoll:** route D on a flat-topped hill in the middle, one nest (the hive) | none | none | none | First ground with a climb. Captain Dorrow's quest wasps are in the calm band |
| Boar Meadow | route A, a ring round the foot of the ridge | **Oak Ridge:** route B along a wooded ridge down the middle | **The Wallows:** routes C, D in wide mud tunnels; Old Tusk's wallow is a dead-end chamber off D (`old_tusk_spawn`, `secret_s2`) | none | none | The land is narrow, so it stacks three levels |
| Burrow Hills | routes A, B among boulder hills | **The Crown:** route C on a plateau | **The Molework:** route D, solo tunnels | **The Deep Molework:** party cave | Bristle Boar | Giant burrow mouth with bones |
| Wolf Copse | routes A, B, C through dense firs with clearings | **Howling Rock:** route D on a crag; the Grey Alpha's pack is its nest | **The Alpha's Den:** party cave | none | Bristle Boar | Dim, closed in. One Grey Alpha on the surface in the deep band, one on the Rock |
| Reedmarsh | routes A, B, C, D across mud islands joined by bridges; the furthest islands are the deep band | a stilt lookout by the hub and one mid-marsh (no monsters: rest spots, fishing) | none | none | Hopper Toad | The money ground: flat but the widest. Water is the wall |
| Thornsnap Hollow | routes A, B on the rim of the hollow | none | **The Rootcellar:** routes C, D, solo root tunnels | **The Lower Rootcellar:** party cave | Bristle Boar | `secret_s11` stays on a path |
| Shard Fields | routes A, B on gravel flats | **The Terraces:** route C on a first terrace (z 6), route D on the summit (z 5) | **Shard Grotto:** party cave | none | Burrow Mole | Three stepped levels; crystals from `maps/dungeon.py` |
| The Bandit Road | routes A, B: an old road with ambush clearings and fenced camps | **The Lookouts:** route C on the upper floors and walkways of three ruined buildings (`Map.storey`, `Map.stairs`) | **Smugglers' Cellar:** route D, solo, built with the stone wall family | **The Vault:** party cave, the 2 Bandit Captains | Meadow Wolf | One Bandit Captain per surface route, in the deep band. `secret_s7` stays walkable |
| The Old Quarry | route A round the rim | **The Scaffolds:** route B on cut-stone terraces | **The Lower Works:** routes C, D, solo, built mine | **The Flooded Level:** party cave | Field Shardling (singles only) | Mixed groups: a pair is Sentinel + Archer; a three adds a Shardling. `secret_s5` on a path |

**The Old Watchtower.** Keep the walls, inner room and cave. Courtyard: the same 18 rams as 4 singles, 4 pairs and 2 threes under the middle-band rules. The inner room and the cave stay packed under the party-cave rules (these are the areas meant to be hard).

**Party caves** keep 8 groups of 4, but grow from 36 x 26 to about 56 x 40 so the chambers are 12 or more apart, with an empty entry chamber.

---

## Part 6. How a ground is built (replaces the loop skeleton)

### 6.1 A ground is drawn from a list, not rolled
In `maps/floor1_plan.py` each ground gets, per level, a hand-written list:
- **clearings:** name, x, y (inside the ground's box), radius 3 to 6, band, and what stands there: a group, a crowd spot, a rest spot, a nest, a landing, or nothing;
- **paths:** from clearing, to clearing, width 3 to 5;
- **routes:** the ordered clearings of each circuit (A to D);
- **links:** ramp, stairs or ladder between two levels, with both ends.

The builder then: fills the box with the ground's wall material; carves each clearing as an uneven blob (`dungeon.blob`, seeded by the ground id so every build is the same); carves each path with a slight wiggle; paints the path ground; places groups, signs and dressing; and runs the walk test and the checker.

### 6.2 Drawing rules
1. **Start from the gate:** hub, then a trunk path that winds to the far end. Routes hang off the trunk as circuits. Circuits may share a junction clearing (pull 0) but not a path.
2. **Nothing straight for more than 10 tiles; no two clearings the same size in a row; no grid.** Compare the render with the old four-ring picture: if it still looks like rings in boxes, redraw.
3. **Rest spots** are real places: a campfire, a fallen log, a shrine stone. At least one per route.
4. **Level links:** at least two between any pair of joined levels, at opposite ends, so nobody is cornered. Landings are approach band (no group within 8 steps, either end).
5. **Outer wall** 2 tiles thick, one gate, as today. The walk test still proves the gate is the only way in on the surface and that every level is reachable from it.
6. **Signs:** at the gate (name, levels, "calm near the gate, harder the deeper you go"), at each route start (its name and band), outside every nest ("A nest. Not alone."), at every way down to a party cave.
7. **Named points:** keep `camp_<id>`, `gate_<id>`, `ground_<id>_nw/se`, `den_<id>` (now the party cave's entrance), `crowd_<id>_<route>_<n>`, and `loop_<id>_<a|b|c|d>` for each route's start. The old `loop_<id>_<nw|ne|sw|se>` names go; update every test, the crowd data and the `!hunt` text that uses them.

### 6.3 New builder pieces (task H3)
| Piece | What it does | Notes |
|---|---|---|
| `Map.hill(cells, z)` | A raised level: solid mountain ground under the cells at the level below, walkable ground on top at z | Rock faces come from `Map.edge_grounds`. Keep hills 3 or more tiles from the outer wall |
| `Map.ramp(x, y, z, facing)` | An outdoor slope between two levels | Find the ramp items the way `tools/learn_object_parts.py` learns objects: from Canary's hand-made map and the item list's floor-change flag. If no good ramp is found, use `Map.stairs` (stone) and say so in `PROGRESS.md` |
| `wilds.level(m, c, z)` | Carves one level of a ground from its clearings and paths | Natural levels use `dungeon.cave`; built ones (Bandit Road, Old Quarry) a wall family |
| `wilds.bands(L)` | Gives every walkable tile its band from walking distance and the plan | Read by the checker |
| Group placement | One spawn area per group, radius 1 for singles, 2 otherwise, members on free tiles round the home | As `wilds.group` today |

Render outdoor upper levels with the `top` argument of `tools/maprender.py`, and every lower level on its own.

---

## Part 7. Crowd system and respawn changes

1. **Crowd spots move into side pockets:** small dead-end clearings off a route, 3 to 4 per route as today, each holding one pair (starter grounds: one single). They obey rule 3.2.7.
2. **Head count is per ground across all its levels** except the party cave.
3. **Rapid Respawn weekend:** stop forcing every ground to "packed". The weekend bonus halves the wait for monsters only; crowd spots switch on only from the real head count.
4. States, thresholds and the 5-minute step-down stay as they are.
5. Respawn times: recompute with the rule in `FLOOR1_WILDS_PLAN.md` 5.3 after H10 re-measures kills per hour (more walking means slightly fewer kills; expect waits 10 to 15% shorter). The ladder targets in its Part 3.2 must still be met within 10%.
6. Cavebot: refused in party caves only (Q37 assumed yes); allowed on every other level with the usual penalty.

---

## Part 8. What must be true at the end

1. `python tools/hunt_check.py` passes for every ground and level, and the heat maps are committed.
2. `python tools/wilds_plan_check.py` prints `problems 0`; the walk test passes on every level.
3. Monster counts are within 5% of: starter grounds 48, standard grounds 72, party caves 32, Old Watchtower 66.
4. An in-game test, on the real spawned map, stands a test player at each route's start, middle and far end and counts the monsters within `NOTICE`: never above the band's limit; and at the gate: zero.
5. An in-game test walks a test player from a group to another level and checks the monsters let go.
6. Every ground has been rendered level by level and walked in the client by a GM character; one new low-level character has hunted the Ratwarren and Toad Pond by hand without dying to a pile-up.
7. `BESTIARY.md`, `ECONOMY.md`, `FLOOR1.md`, the plan pictures, the taskmaster's list and the `!hunt` text agree with the map.
8. The calm rules are written into `CLAUDE.md`'s map quality rules so Floors 2 to 10 follow them.

---

## Part 9. Build order (one commit each)

| Task | What | Done when |
|---|---|---|
| H0 | Measure in game: how far a monster notices a player (across and down), that walls do not matter, that monsters let go when the player changes level, how far they wander. Check which weekend bonus was on for Jay's test on 2026-11-13/14 | Answers in `PROGRESS.md`; `NOTICE` set in one place |
| H1 | Write `tools/hunt_check.py` and run it on today's map | It prints today's numbers (expected to fail) and writes heat maps; numbers quoted in `PROGRESS.md` |
| H2 | New ground table in `maps/floor1_plan.py` (Part 4), moved roads, plan picture | `wilds_plan_check.py` prints `problems 0`; map unchanged |
| H3 | Builder pieces (Part 6.3) | A scratch ground with a hill and a lower level builds, passes the walk test and the checker |
| H4 | Pilot 1: **The Ratwarren** (Yard + Warren) | Checker OK, rendered, walked in the client, boot test. Add to `PLAYTEST.md` checklist for Jay |
| H5 | Pilot 2: **Burrow Hills** (all four levels) | Same |
| H6 | Toad Pond, Sproutling Glade, Waspgrass Fields | Same, each |
| H7 | Boar Meadow, Wolf Copse, Reedmarsh, Thornsnap Hollow | Same, each |
| H8 | Shard Fields, the Bandit Road, the Old Quarry, the Old Watchtower's groups | Same, each |
| H9 | Roads, trails, signposts, zones on every level, secrets, standing stones, forest pass | Part 8 point 2; a new character reaches the first five grounds by signs alone |
| H10 | Crowd pockets, the weekend-bonus change, the cavebot rule, respawn times and the economy re-check (Part 7) | Crowd tests updated and passing; `tools/gen_economy.py` meets the ladder |
| H11 | In-game tests of Part 8 points 4 and 5; regenerate documents, pictures, taskmaster list, `!hunt` | Boot test passes with the new tests |
| H12 | Write the calm rules into `CLAUDE.md`; make the Floors 2 to 10 generator (`maps/layout_floor.py`) obey them, checked by `hunt_check.py` | Checker passes on all ten floors |
| H13 | Walk every ground and level in the real client (replaces W12); playtest list for Jay in `WEEKLY_REPORT.md` | Notes fixed or turned into tasks |

If Jay's notes on the pilots (H4, H5) arrive, apply them before continuing with the next ground.

---

## Part 10. Spawn habits and ground types on Floor 1 (2026-11-16; replaces the group sizes in Parts 3 and 5)

The rules are in `DESIGN.md` 9.4. This part applies them to Floor 1. Everything here is Claude's call and Jay can veto any line.

### 10.1 Habits

| Monster | Habit | Weight | In practice |
|---|---|---|---|
| Field Rat | Swarm | 0.4 | clumps of 5 to 8 in the Warren; ones and twos in the Yard |
| Hopper Toad | Pair | 1 | twos by the water, a single here and there |
| Sproutling | Colony | 0.7 | a few on the paths, thick round the great tree's roots |
| Meadow Wasp | Colony | 0.5 | scouts in the meadows, a cloud at the hive |
| Burrow Mole | Colony | 1 | singles on the hills, thick in the Molework |
| Bristle Boar | Loner | 1.8 | always alone, far apart |
| Meadow Wolf | Pack | 1 (Grey Alpha 2) | 3 to 5 together; the larger packs have a Grey Alpha |
| Field Shardling | Pair | 1 | twos among the crystals |
| Thornsnap | Sentry | 1.3 | rooted in place at bends and doorways |
| Road Bandit | Sentry | 1 (Captain 2.5) | guards at camps and ambush spots; a Captain leads a camp |
| Ruin Sentinel, Ruin Archer | Sentry | 1.3, 1 | a Sentinel in front with Archers behind |
| Stonehorn Ram | Pack | 2 | a herd; the apex spawn |

Reedmarsh's monster gets its habit when H7 reaches it. Weights are first guesses; S1 sets them from each monster's real numbers in `tools/balance.py`.

### 10.2 Ground types

| Ground | Type | Why |
|---|---|---|
| The Ratwarren, Toad Pond, Sproutling Glade | Training | the three first grounds; any class, solo |
| Boar Meadow | Class: Vanguard | loners that charge you, tunnels in the Wallows |
| Reedmarsh | Class: Ranger | open islands, water as the wall, room to keep your distance |
| Waspgrass Fields | Class: Arcanist | clouds of weak wasps |
| Thornsnap Hollow | Class: Mystic | rooted monsters that poison; long fights where staying power wins |
| Burrow Hills, Wolf Copse, Shard Fields | Mixed | two habits each; fine solo, better as a pair |
| The party caves, the Bandit Road's Vault, the Old Quarry's Lower Works and Flooded Level | Group (3 to 4) | mixed packs: a front-liner, a ranged one, a caster |
| The Old Watchtower's inner room and cave | Large group (4 to 8) | the apex spawn; Jay already wanted it hard |

### 10.3 Danger budget (weight that may come at one player at once)

| Type | Gate | Outer part | Middle | Deep | Nest or den |
|---|---|---|---|---|---|
| Training | 0 | 2 | 3 | 4 | 6 |
| Class, mixed | 0 | 3 | 4 | 6 | 8 |
| Group | 0 | 6 | 9 | 12 | 14 |
| Large group | 0 | 10 | 16 | 22 | 26 |

Breathing room, rest spots and room to fight (3.2) stay as they are for training, class and mixed grounds. Group and large-group grounds only need a quiet gate and a quiet room between packs. Never raise a budget to make a ground pass; change the ground.

### 10.4 The five grounds already rebuilt

Their maps stay. Their monsters are regrouped by habit (task S3): the Ratwarren's lower level in swarms, Waspgrass as a colony round the hive, Burrow Hills as a colony with loner boars on top, Toad Pond in pairs, the Glade as a colony round the great tree. Totals per ground may change; the economy generator is rerun after.

---

## Sources
- Engine: `opentibiabr/canary` v3.6.1, `src/creatures/monsters/monster.cpp` and `config.lua.dist` (read 2026-11-14).
- OTLand, low-rate servers need wide areas with sparse monsters: https://otland.net/posts/2774595
- OTLand, a custom lair built with "a lot of open space, but also some narrow passages": https://otland.net/threads/10-98-custom-magma-dragon-lair.291840/latest
- OTLand, "map layout discussion": https://otland.net/threads/map-layout-discussion.291569/
- OTLand, keep spawn areas small with few monsters each: https://otland.net/threads/tfs-1-4-2-spawn-issue.293361/
- Tibiantis, "Spawn info" (home squares, monsters per home): https://tibiantis.info/library/map
- TibiaVip, how CipSoft plans and re-checks hunting grounds: https://tibiavip.app/home/news?id=6507
- TibiaQA, how respawn scales in quiet areas: https://www.tibiaqa.com/39442/how-does-creature-respawn-actually-scale-semi-abandoned-hunting-areas

The picture of real Tibia in Part 1 (ones and twos by the entrance, harder and denser on lower levels, stacked cave levels) and the density figure (one monster per 40 to 60 tiles in early caves) come from my own knowledge of its classic low-level caves, not from a published number; the searches found no written rule. The limits in Part 3 are this plan's own.
