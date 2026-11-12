# Floor 1 outside the walls: progression, hunting grounds and spawns (plan, 2026-11-12)

Jay asked for this on 2026-11-12: *"look at player progression, the map design of everything outside the city, monster spawn areas are currently messy and need to have more of a dedicated area where a few players at a time will be able to bot or farm. maybe there should be an algorithm where the monster spawn increases or decreases with players active? check how tibia decides upon its spawn sizes. set up the map and instructions for a less expensive model to do all the work."*

**This is a plan only. Nothing in the game has changed.** The picture is `docs/FLOOR1_WILDS_PLAN.png`; `python tools/wilds_plan_check.py` redraws it and checks that nothing overlaps (it must print `problems 0`).

Part 1 is for Jay. Parts 2 to 9 are the build instructions.

---

## Part 1. For Jay: what I found and what I propose

### What is wrong today
1. **Floor 1 is over in about an hour.** With experience at 25 times normal, the numbers in `ECONOMY.md` put a new character at level 35 after roughly 1 hour 15 minutes of hunting. The Ratwarren lasts about one minute and Boar Meadow about five. Twelve hunting grounds were built for a floor that players leave before they have seen three of them.
2. **The hunting grounds are rectangles of lawn.** Each one is a box on flat grass with monsters dropped at random spots. There are no paths, no edges and nothing that says "this spot is yours". Three roads run straight through the middle of a ground (Waspgrass, the Old Quarry and Sproutling Glade), so monsters stand on the road.
3. **There are far too many monsters, coming back far too fast.** Boar Meadow has 90 boars that each return after 55 seconds. That is enough for about 22 players hunting flat out, in one field. Nobody ever has to move, share or pick a spot. Standing still between two groups is as good as walking, which is the laziest possible bot.
4. **The ladder has dips.** By the model, Shard Fields (levels 17 to 24) gives less experience per hour than Wolf Copse (levels 12 to 18), and Burrow Hills gives less than Boar Meadow. A climber who follows the guide slows down.
5. **The Old Watchtower has no road to it.**

### How Tibia does it (what I checked)
- **Every spawn is small and fixed.** A hunting spot in Tibia is a handful of monsters at set places, and each monster comes back a few *minutes* after it dies. The number of monsters divided by that wait decides how many players a spot can feed. That is why Tibia players talk about "a respawn" as a place one player or one team owns for an hour.
- **Monsters do not come back while someone is standing on top of the spot.** Community answers put the limit at about 7 squares, so a player has to keep walking a circuit. That circuit is what a cavebot records.
- **Respawn gets faster as more players are online.** Community answers say the fastest rate is reached at 800 players online, and that since 2013 a quiet world is treated as if it had 500. There is also a system where two areas of the map get doubled respawn for a while.
- **Our engine has none of that built in, as far as I could see.** It has one global "spawn rate" setting, fixed at start-up. The first build task checks this properly.

### What I propose
1. **Slow the early levels so Floor 1 lasts about 11 to 15 hours** (about a day and a half on the cavebot). The first eight levels stay quick. This is question Q30 below; I have assumed yes.
2. **Rebuild each hunting ground as an enclosed place with four hunting loops.** A loop is a ring-shaped trail around a pond, a grove or a rock pile, with monster groups at fixed spots along it. One loop feeds one player hunting flat out, or two sharing. A cavebot route is simply one lap. Each ground has one gate off the road with a small clearing to meet in, and signs naming the loops.
3. **Six of the harder grounds get a cave underneath** with bigger, denser groups, meant for a party of two to four.
4. **Size every spawn the Tibia way:** few monsters, coming back after two to three and a half minutes, sized so one loop is one player's worth.
5. **Add a crowd system, as you suggested.** Each ground counts the players inside it. When it is over-full, extra monster groups switch on at set spots along the loops; when the crowd leaves, they switch off again. The four starter grounds can grow to four times their normal size for launch day. The harder grounds only grow by half, so good spots stay worth competing for.
6. **Move roads out of the grounds, add a road to the Old Watchtower, and smooth the ladder** so every step is better than the last.

### What it means in numbers
| | Today | Planned |
|---|---|---|
| Time to level 35 (hunting by hand) | about 1 h 15 min | about 11 h by the model, nearer 15 h in real play |
| Hunting grounds | 12 open boxes | the same 12, each a walled-off place with 4 loops |
| Monsters on Floor 1 at rest | about 1,000 | about 1,000 (fewer per ground above, about 190 more in caves) |
| Monsters when the floor is packed | about 1,000 | about 1,500 |
| Players one ground feeds | about 20, all on top of each other | 4 to 8 at rest, 12 to 16 when packed, plus a party in the cave |

### Questions for you (also in QUESTIONS.md; I assume my recommendation until you answer)
- **Q30. Slow the early levels?** Recommendation: yes. Levels 1 to 8 at 10 times, 9 to 20 at 4 times, 21 to 50 at 3 times.
- **Q31. Crowd system as described?** Recommendation: yes.
- **Q32. No cavebot inside the caves?** Recommendation: yes. Loops are for solo players and bots; caves are for teams at the keyboard.

---

## Part 2. Rules for the builder (read first)

1. Follow every rule in `CLAUDE.md`, above all the map quality rules. Render every ground with `tools/maprender.py` and walk it in the client before committing.
2. **Do not touch:** Hearthgate, Millcross, the Arrival Yard, the Fisher's Huts, the Wallside Cabins, the Pass, the labyrinth, the Axe-Lord's hall, the Underkeep, the Arena, the Siege keep, or the inside of the Old Watchtower.
3. **Keep every name and id:** the camp ids in `maps/floor1_plan.py` (`starter_west`, `boar_meadow`...), the point names made from them (`camp_<id>`), monster names, quest names and secret ids. Tests, quests and the hunting guide use them.
4. All coordinates here are Floor 1 tiles (0 to 399). The builder adds 1000 to both, as `maps/layout_floor1.py` already does. Surface is z 7; caves are z 8.
5. The plan table lives in `maps/floor1_plan.py`. Put the new numbers there, so `tools/gen_bestiary.py` and the `!hunt` guide follow automatically. `tools/wilds_plan_check.py` holds the same rectangles; keep the two in step, and run it before each commit.
6. One task = one commit, with the boot test, in the order of Part 9. If a rule here cannot be met, write why in `QUESTIONS.md`, choose the nearest thing that works, and carry on.

---

## Part 3. Progression

### 3.1 Experience stages (replaces the first row of DESIGN.md 5.5; Q30)
| Level | Now | Planned |
|---|---|---|
| 1 to 8 | 25x | 10x |
| 9 to 20 | 25x | 4x |
| 21 to 50 | 25x | 3x |
| 51 and up | unchanged for now | to be checked the same way when Floor 2 is planned (roadmap R10) |

### 3.2 The ladder: experience per hour must rise at every step
"Base experience per hour" is before the stage multiplier, for a Vanguard at the middle level of the ground, by the model in `tools/gen_economy.py`. Change each monster's experience value in `tools/gen_monsters.py` until its ground is within 10% of the target. Do not change health or damage in this pass.

| Step | Ground | Levels | Role | Base experience per hour now | Target |
|---|---|---|---|---|---|
| 1 | The Ratwarren | 1-4 | experience | 1,800 | 1,800 |
| 2 | Toad Pond | 3-7 | experience | 2,430 | 2,500 |
| 3 | Sproutling Glade | 5-10 | experience | 3,375 | 3,500 |
| 4 | Waspgrass Fields | 7-12 | experience | 6,000 | 5,000 |
| 5 | Boar Meadow | 9-15 | experience | 10,570 | 7,500 |
| 6 | Burrow Hills | 11-16 | experience | 10,350 | 9,000 |
| 7 | Wolf Copse | 12-18 | experience | 16,440 | 11,000 |
| 8 | Reedmarsh | 14-19 | money | 12,770 | 9,000 |
| 9 | Thornsnap Hollow | 14-20 | experience | 14,200 | 13,000 |
| 10 | Shard Fields | 17-24 | experience | 15,230 | 16,000 |
| 11 | The Bandit Road | 19-27 | money | 22,525 | 14,500 |
| 12 | The Old Quarry | 23-30 | money | 26,300 | 19,000 |
| 13 | The Old Watchtower | 28-40 | both | not modelled | 26,000 outside, 32,000 inner room and cave |

- Money grounds give about three quarters of the experience of the experience ground at the same level, and at least one and a half times its gold per hour. Check the gold column of `ECONOMY.md` after the change and raise coin drops on Reed Snappers, Road Bandits and the Quarry monsters if needed.
- Caves (Part 5.4) need no monster changes: bigger groups, closer together, already give about a quarter more per hour.

### 3.3 The timeline this gives (by the model; real play is about 40% slower, the cavebot a little over twice as slow)
| Level reached | Hours played | Where the climber is |
|---|---|---|
| 6 | 0.1 | Ratwarren, Toad Pond |
| 9 | 0.2 | Sproutling Glade. Stage drops from 10x to 4x here |
| 11 | 0.5 | Waspgrass Fields |
| 14 | 1.1 | Boar Meadow. First step outside the Guarded ring |
| 18 | 2.1 | Burrow Hills, Wolf Copse, Reedmarsh |
| 21 | 3.0 | Thornsnap Hollow. Promotion becomes possible at 20; the 20,000 gold arrives around level 25 |
| 25 | 4.8 | Shard Fields, the Bandit Road, the Gate Hound with a group |
| 30 | 7.7 | The Old Quarry, the labyrinth |
| 35 | 10.7 | The Old Watchtower, the Axe-Lord |
| 40 | 14.7 | The Old Watchtower's inner room and cave |

Done when: `tools/gen_economy.py` prints this ladder with every target met, an in-game test reads the three new stages, and `DESIGN.md` 5.5, `ECONOMY.md` and `BESTIARY.md` are regenerated or updated. Quote Jay's answer to Q30 in `PROGRESS.md` if he has given one.

---

## Part 4. The map outside the walls

### 4.1 Where everything goes
Look at `docs/FLOOR1_WILDS_PLAN.png`. The four starter grounds hug the city (Guarded). The eight harder grounds sit one road-walk further out (Open). The Old Watchtower stays in the far north-west (Contested).

| Id | Ground | x, y | Width x height | Gate side | Size | Zone | Cave below |
|---|---|---|---|---|---|---|---|
| starter_west | The Ratwarren | 134, 242 | 38 x 40 | south | small | guarded | none |
| starter_east | Toad Pond | 296, 242 | 38 x 40 | south | small | guarded | none |
| starter_south | Sproutling Glade | 190, 338 | 38 x 40 | north | small | guarded | none |
| wasp_fields | Waspgrass Fields | 184, 194 | 44 x 34 | east | small | guarded | none |
| boar_meadow | Boar Meadow | 140, 338 | 39 x 57 | north | tall | open | none (Old Tusk's wallow instead) |
| burrow_hills | Burrow Hills | 240, 188 | 60 x 40 | west | standard | open | The Molework |
| wolf_copse | Wolf Copse | 28, 262 | 60 x 40 | east | standard | open | The Alpha's Den |
| reed_marsh | Reedmarsh | 44, 322 | 52 x 48 | north | standard | open | none |
| thornsnap_hollow | Thornsnap Hollow | 158, 132 | 60 x 40 | east | standard | open | The Rootcellar |
| shard_fields | Shard Fields | 340, 300 | 52 x 48 | north | standard | open | Shard Grotto |
| bandit_road | The Bandit Road | 328, 172 | 52 x 48 | south | standard | open | Smugglers' Cellar |
| old_quarry | The Old Quarry | 240, 124 | 60 x 40 | west | standard | open | The Lower Works |

The Old Watchtower stays at 30, 30 (44 x 44).

### 4.2 Roads and trails
Roads are 3 wide (`Map.road`, as now); trails are 2 wide. **No road or trail may pass through a ground**; each ends at a gate. Remove every road in today's `# roads` block that is not listed here.

| Road | From, through, to |
|---|---|
| Pass Road | north gate (232, 235) to the Pass (232, 92) |
| South Road | south gate (232, 332) to (232, 368) |
| Mill Road | west gate (175, 285) to the river bank (118, 285) |
| River Path | (118, 285) to (130, 220) |
| Millcross Road | (130, 220) to Millcross (99, 220), over the bridge |
| East Road | east gate (288, 285) to East Cross (338, 285) |
| Shrine Path | (232, 368) to the toppled shrine (300, 368) |

| Trail | From, through, to |
|---|---|
| Ratwarren gate | Mill Road (153, 284) to (153, 282) |
| Toad Pond gate | East Road (315, 284) to (315, 282) |
| Glade trail | South Road (231, 335) to (209, 335) to (209, 337) |
| Wasp gate | Pass Road (230, 211) to (228, 211) |
| Cabin Lane | west cabins (152, 313) to (159, 326) to Boar Meadow (159, 337) |
| Burrow trail | Pass Road (234, 208) to (239, 208) |
| Quarry trail | Pass Road (234, 144) to (239, 144) |
| Thornsnap trail | Pass Road (230, 152) to (218, 152) |
| Bandit Track | East Cross (338, 285) to (338, 240) to (354, 224) to (354, 220) |
| Shard Track | East Cross (338, 285) to (338, 292) to (366, 296) to (366, 299) |
| Copse Road | Millcross south gate (70, 239) to (92, 250) to (92, 310) to (70, 318) to Reedmarsh (70, 321) |
| Copse gate | Copse Road (92, 282) to Wolf Copse (88, 282) |
| Watch Road | Millcross north side (76, 194) to (76, 110) to (52, 84) to the Old Watchtower gate (52, 80) |

Put a signpost at every junction naming what lies each way and its level range (for example "Burrow Hills, levels 11-16"). Move the eastern standing stones from (305, 240) to (356, 262), because Toad Pond now sits there.

### 4.3 Secrets and named spots that sit inside a ground
Every secret must end on a walkable tile inside its ground. If the old spot is no longer walkable, move it by the smallest step that works, keep its id, and list the move in `PROGRESS.md`.

| Point | Was | Now |
|---|---|---|
| secret_s2, old_tusk_spawn | old Boar Meadow | Old Tusk's wallow in the new Boar Meadow (Part 6) |
| secret_s5 | (225, 132) in the old Quarry | a spot on a trail in the new Old Quarry |
| secret_s7 (352, 186), secret_s9 (44, 300), secret_s11 (160, 170) | | still inside Bandit Road, Wolf Copse and Thornsnap Hollow; make sure they stay walkable |
| secret_s8, s10, s12, s3, s4, s6 | | untouched |

### 4.4 Zones
- Guarded: the same city ring as today, plus each Guarded ground's rectangle grown by 6 tiles, plus the gate road to Waspgrass, the Fisher's Huts, the Arrival Yard and Millcross.
- Open everywhere else, the caves included. The Old Watchtower stays Contested, with its inner room and cave Deadzone.

---

## Part 5. How one hunting ground is built

Every ground uses the same skeleton, dressed differently (Part 6). The skeleton is what makes it tidy; the dressing is what makes it look hand-made.

### 5.1 The pieces
```
 +------------------------------+     W = wall of the ground (thicket, rock or water), 2 tiles thick
 | W W W W W W W W W W W W W W W|     H = hub: the clearing inside the gate
 | W  loop NW   +   loop NE   W |     + = the cross trail between the loops
 | W            +             W |     each loop = a ring trail around a solid core
 | W + + + + + + + + + + + +  W |
 | W  loop SW   +   loop SE   W |
 | W            +             W |
 | W H H H H H H H H H H H H  W |
 | W W W W W W  gate  W W W W W |
 +------------------------------+
```
| Piece | Small ground | Standard ground | Tall ground (Boar Meadow) |
|---|---|---|---|
| One loop's box | 18 x 16 | 24 x 18 | 18 x 24 |
| Cross trail between loops | 2 wide | 3 wide | 3 wide |
| Hub strip on the gate side | 6 deep | 8 deep | 6 deep |
| Gate | 3 wide, in the middle of the gate side | same | same |
| Monster groups per loop | 4 | 6 | 6 |
| Extra (crowd) group spots per loop | 4 | 3 | 3 |

### 5.2 Building rules
1. **Outer wall.** The outermost 2 tiles of the rectangle are solid, with no gap anywhere except the gate. Use what Part 6 names for that ground. Nothing natural outside the ground within 1 tile of the wall is needed; the forest pass may grow up to it.
2. **Hub.** Clear ground the full width of the gate side. A sign beside the gate reads "<Name>. Levels X to Y. Four loops: north-west, north-east, south-west, south-east." Add one fire or lamp and one bench-like prop. **No monster group within 8 tiles of the gate.**
3. **Loops.** In each loop's box: a ring-shaped trail 2 tiles wide, 3 tiles in from the box edge, around a solid core that nobody can walk through. Paint the trail with the ground patch named in Part 6. Each loop opens onto the cross trail or the hub through one mouth 3 tiles wide, with a small sign naming the loop.
4. **Make it look grown, not drawn.** Cut every corner of the ring diagonally. Shift each loop's box by up to 2 tiles from the grid. Let the core bulge or pinch by 1 tile here and there, but keep the trail at least 2 wide everywhere. Scatter low, walk-over dressing (flowers, pebbles, bones) on the trail edges only.
5. **Between loops.** Whatever is left between two loops' trails is filled solid with the wall material, so a monster or a player goes round by the cross trail.
6. **Monster groups.** Put the groups on the ring at even spacing, at least 9 tiles apart (11 in small loops), never in a mouth. Each group is one spawn area of radius 2 holding the monsters listed in Part 6. Clear a 3 x 3 patch for each. These positions are written into the plan file, not rolled at random on each build.
7. **Crowd spots.** Mark the extra group spots halfway between the normal groups. They get no monsters in the spawn file; write them out as named points for the crowd system (Part 7): `crowd_<ground id>_<loop>_<n>`.
8. **Named points.** `camp_<id>` = the middle of the hub. `loop_<id>_<nw|ne|sw|se>` = each loop's mouth. `den_<id>` = the cave entrance.
9. **A check that fails the build.** Add a walk test to the map builder (plain flood fill over walkable tiles, before the file is written). It must prove for every ground: the gate is reachable from the Hearthstone; every group spot and crowd spot is reachable from the gate; each loop's trail is a closed ring; and nothing walkable crosses the outer wall except the gate.

### 5.3 How many monsters and how fast they return (the Tibia rule)
A loop should feed one player hunting flat out, with a little spare:

**respawn seconds = 2,770 x (monsters in the loop) / (kills per hour of one player there)**

Kills per hour comes from `ECONOMY.md`. With today's figures:

| Ground | Monsters per loop | Kills per hour | Respawn (seconds) |
|---|---|---|---|
| Ratwarren, Toad Pond, Sproutling Glade, Waspgrass | 12 (4 groups of 3) | 300 | 110 |
| Boar Meadow | 18 (6 groups of 3) | 264 | 190 |
| Burrow Hills | 18 | 230 | 215 |
| Wolf Copse | 18 | 265 | 190 |
| Reedmarsh | 18 | 232 | 215 |
| Thornsnap Hollow | 18 | 254 | 195 |
| Shard Fields | 18 | 277 | 180 |
| The Bandit Road | 18 | 237 | 210 |
| The Old Quarry | 18 | 229 | 220 |
| Any cave | 32 (8 groups of 4) | about 550 for a party of three | 160 |

Elites (Grey Alpha, Bandit Captain) return after 15 minutes. Recompute the table if the monster experience pass (Part 3.2) changes kills per hour.

### 5.4 Caves
- A natural cave at z 8, about 36 x 26, wholly under its own ground, made with `dungeon.cave` and `dungeon.blob`. The Smugglers' Cellar and the Lower Works are built dungeons with a wall family instead.
- The way down is in the middle of the ground, where the cross trails meet: `Map.stairs` placed at z 8, which makes the hole on the surface. Put a warning sign beside it: "<Cave name>. For a party. Levels X and up."
- Inside: an entry chamber with no monsters, then a ring of chambers so a party can circle. Eight groups of four, at least 7 tiles apart. Decorate with `maps/dungeon.py` and `keep_clear`.
- Before carving, check that no tile at z 8 within 6 tiles is already used (the Underkeep is under the city, and its wings may reach further). If there is a clash, move the cave inside its ground's rectangle; if it still clashes, stop and write it in `QUESTIONS.md`.
- The crowd system does not run in caves. The cavebot is refused there, as in boss rooms (Q32).

---

## Part 6. The twelve grounds, one by one

"Wall" is the outer wall and the filling between loops. "Core" is the solid middle of each loop. "Trail" is the ground patch on the ring. Use the scenery lists already in `maps/scenery.py`; check with the walk test that the wall really blocks.

| Ground | Wall | Core of each loop | Trail | Groups (each loop) | Landmark and notes |
|---|---|---|---|---|---|
| The Ratwarren | thick bushes and broadleaf trees | dirt mounds ringed with stones | dirt | 4 x 3 Field Rats | A broken cart in the hub. The first sign a new player reads: keep it friendly |
| Toad Pond | broadleaf trees and ferns | **a pond** in every loop, each a different shape | grass with mud at the water's edge | 3 x 3 Hopper Toads, 1 x 3 Field Rats | Players walk round four ponds. Fishing works here |
| Sproutling Glade | dense ferns and young trees | fern-and-bush groves | grass | 3 x 3 Sproutlings, 1 x 3 Hopper Toads | A ring of mushrooms in the hub |
| Waspgrass Fields | hedges of bushes | flower beds packed solid with a tree in the middle | grass, heavy with flowers at the edges | 4 x 3 Meadow Wasps | Captain Dorrow's quest ground: 48 wasps is plenty for "12 wasps" |
| Boar Meadow | oaks (broadleaf), dense | oak groves; one mud wallow visible in each | dirt | 6 x 3 Bristle Boars | **Old Tusk's wallow:** the south-east core is hollow, a 7 x 7 mud clearing reached by a gap 1 tile wide. `old_tusk_spawn` and `secret_s2` go inside |
| Burrow Hills | boulders (2 x 2 rocks) and stones | bare dirt hills crowded with boulders | dirt | 6 x 3 Burrow Moles | The cave mouth looks like a giant burrow: dirt patch, bones |
| Wolf Copse | dark firs, very dense | fir thickets | grass with ferns | 5 x 3 Meadow Wolves, and 1 group of 1 Grey Alpha with 2 Meadow Wolves | Dim and closed-in. The Alpha's Den has 2 Grey Alphas among its groups |
| Reedmarsh | **water**, with a rim of reeds and dead trees | open pools | mud; where a trail crosses water use bridge pieces (`scenery.bridge`) | 6 x 3 Reed Snappers | The money ground: no cave. Fishing works on every pool |
| Thornsnap Hollow | thorn bushes | thorn thickets with a dead tree in the middle | dirt | 5 x 3 Thornsnaps, 1 x 3 Bristle Boars | `secret_s11` at (160, 170) must stay on a trail |
| Shard Fields | boulders and stones on gravel | gravel mounds with boulder clusters | gravel | 6 x 3 Field Shardlings | Shard Grotto below: use the crystal props from `maps/dungeon.py` |
| The Bandit Road | broadleaf trees and bushes, with broken stone wall pieces drawn by `Map.autowall` | **a bandit camp** in every core: a fenced-off heap of carts, barrels, crates and a fire that cannot be walked into | dirt | 5 x 3 Road Bandits, and 1 group of 1 Bandit Captain with 2 Road Bandits | Smugglers' Cellar below: a built cellar (stone wall family), 2 Bandit Captains among its groups. `secret_s7` stays walkable |
| The Old Quarry | boulders and rubble | cut-stone piles: rubble, broken pillars, boulders | gravel | 4 groups of Ruin Sentinel + Ruin Archer + Field Shardling, 2 groups of Ruin Sentinel + 2 Ruin Archers | The Lower Works below: a built mine (stone wall family), same mix in groups of four. `secret_s5` moves onto a trail here |

**The Old Watchtower.** Leave the walls, the inner room and the cave as they are. Replace its four big spawn areas with fixed groups under the same rules: 6 groups of 3 Stonehorn Rams round the courtyard (respawn 150), 4 groups of 4 in the inner room (respawn 120), 8 groups of 4 in the cave (respawn 120). Add the Watch Road to its gate.

**The land between the grounds.** Keep the scattered trees, the forest pass, the lake, the ponds and the ruins. After the grounds are in, run the forest pass again so woods fill the space between grounds and roads, with no trees within 3 tiles of a road, trail or gate.

---

## Part 7. The crowd system (more players, more monsters)

**First, find out what the engine really does** (task W0 in Part 9). On a test map or with the GM character:
1. Kill a group and stand next to its spot. Do the monsters return while you stand there, or only after you step away? How far away?
2. Kill a group with respawn 110 and time its return from 20 tiles away. Is it 110 seconds, or 110 plus up to a minute?
3. Read the engine's spawn code for the pinned version (Canary 3.6.1, `spawn_monster.cpp`) and note whether it already changes speed with the number of players online.

Write the three answers in `PROGRESS.md`. If monsters return on top of a standing player, nothing in this plan changes: the long respawn times already make walking the loop better than standing still. If the engine already speeds up with players online, switch that off or account for it, so the two systems do not stack.

**Then build the system** as a script in `server/data-spirebound/scripts/spirebound/`, with its rules in a `lib/spirebound` file so they can be tested.

- Every 30 seconds, count the players standing inside each ground's rectangle at z 7. Staff characters do not count. Players on the cavebot do.
- Each ground has **seats** = its number of loops (4).
- Each ground is in one of four states:

| State | When | What is switched on |
|---|---|---|
| Quiet | fewer than 5 players | nothing extra |
| Busy | 5 to 7 players | half of the ground's crowd spots (the odd-numbered ones) |
| Packed | 8 or more | all crowd spots |
| Rush (Guarded grounds only) | 12 or more | all crowd spots, and crowd monsters return three times as fast |

- A crowd spot that is switched on holds the same group as its loop's normal groups, made by the script, and brings it back after the ground's respawn time once the whole group is dead. It never spawns a group while a player is within 7 tiles of the spot.
- A ground steps **up** as soon as the count is reached, and steps **down** only after the count has stayed below the line for 5 minutes. When it steps down, living crowd monsters stay until killed; they simply do not return.
- Crowd monsters are ordinary monsters: same experience, same loot.
- After a restart every ground begins Quiet.
- `!hunt` and the hunting-guide NPCs add one line per ground for the player's level: "Boar Meadow: busy (6 players, extra boars are out)".

Sizes this gives: a starter ground holds 48 monsters when quiet, 96 when packed, and in a rush feeds about four times its quiet number of players. A standard ground holds 72, then 108.

Done when these in-game tests pass through the real script: a ground with 4 test players is Quiet; with 5 it switches on half its crowd spots and monsters really appear there; with 8 all of them; a Guarded ground with 12 is in Rush and an Open ground is not; no group appears within 7 tiles of a player; five minutes after the players leave, the spots stop refilling.

---

## Part 8. What must be true at the end

1. `python tools/wilds_plan_check.py` prints `problems 0`, and the built map passes the walk test in Part 5.2.
2. Every ground matches its row in Parts 4 and 6, and has been rendered and walked in the client: gate, hub signs, all four loops, the cave.
3. No monster spawn stands on a road, a trail outside a ground, or within 8 tiles of a gate.
4. Monster counts on Floor 1 (surface and caves, without crowd spots) are within 5% of: starters 48 each, standard grounds 72 each, caves 32 each, Old Watchtower 66.
5. `BESTIARY.md`, `ECONOMY.md`, `FLOOR1.md`, `docs/FLOOR1_PLAN.png` and the `!hunt` text are regenerated and agree with the map.
6. All existing in-game tests still pass, plus the new ones named in Parts 3, 5 and 7.
7. A new character, played by hand in the client from the Arrival Yard, reaches each of the first five grounds by following signs only.

---

## Part 9. Build order (one commit each)

| Task | What | Done when |
|---|---|---|
| W0 | Find out how the engine respawns (Part 7, the three questions) | Answers in `PROGRESS.md` |
| W1 | Put the new ground table, loop sizes, group lists and respawn times into `maps/floor1_plan.py`; keep `tools/wilds_plan_check.py` in step | The check prints `problems 0`; nothing on the map has changed yet |
| W2 | Add the builder pieces: solid wall ring, loop with core and mouth, fixed group placement, named points, and the walk test (Part 5.2) | A scratch ground builds and passes the walk test |
| W3 | Pilot: rebuild **Boar Meadow** completely, with Old Tusk's wallow | Rendered, walked in the client, boot test passes |
| W4 | The four starter grounds | Same |
| W5 | Burrow Hills, Wolf Copse, Reedmarsh, Thornsnap Hollow | Same |
| W6 | Shard Fields, the Bandit Road, the Old Quarry, and the Old Watchtower's groups | Same |
| W7 | Roads, trails, signposts, zones, secrets, the standing stones, the forest pass (Part 4) | Part 8 points 3 and 7 |
| W8 | The six caves (Part 5.4) | Each walked in the client with a party-sized fight |
| W9 | Experience stages and the ladder (Part 3) | Part 3's "done when" |
| W10 | The crowd system and the `!hunt` line (Part 7) | Part 7's tests |
| W11 | Regenerate the documents and pictures; add a playtest list for Jay to `WEEKLY_REPORT.md` | Part 8 point 5 |

Floors 2 to 10 are not part of this job. When Floor 1 is approved, the same skeleton (gate, hub, four loops, a cave, the respawn rule, the crowd system) becomes a rule for every floor.

---

## Sources for the Tibia research
- TibiaQA, "how does the block spawn system work": https://www.tibiaqa.com/34343/how-does-the-block-spawn-system-work
- TibiaQA, "how many areas can have improved respawn": https://tibiaqa.com/23442/how-many-areas-can-have-improved-respawn
- TibiaWiki, "Spawn" (pointed to by the answers above; I could not read its text directly): https://tibia.fandom.com/wiki/Spawn
- Tibiantis, "Spawn info" (a private server's own rule, for comparison only): https://tibiantis.info/library/map
- OTLand threads on changing spawn rate by players online (community changes, not engine features): https://otland.net/threads/spawnrate-players-online.243835/

These are community answers, not official figures. The plan copies the ideas (small fixed spawns, minutes-long respawn, faster when crowded), not the exact numbers.
