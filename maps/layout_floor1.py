"""Floor 1 layout (roadmap 1.8, redesigned 2026-11-11): Hearthgate Plains. DESIGN.md 3.1-3.5, 9.1-9.2.
Coordinates: Floor 1 occupies x 1000-1399, y 1000-1399, z 7 (labyrinth climbs to z 6, 5, boss room z 4;
the apex cave is z 8). Floor 2's landing is at x 2000+.
Camps and their monsters come from maps/floor1_plan.py (also read by tools/gen_bestiary.py).
Everything here is a playable stand-in; the real map is MAP_REQUESTS.md M1."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from floor1_plan import CAMPS, MILLCROSS, TOWN  # noqa: E402

X0, Y0, Z = 1000, 1000, 7
ID_PILLAR = 1273  # wall pole piece used as a column
SIZE = 400


def build(m):
    rng = m.rng
    claimed = []

    def claim(name, x, y, w, h):
        """Refuse overlapping buildings: a typo in a coordinate should fail the build, not hide a wall inside a house."""
        for n, a, b, c, d in claimed:
            if x < a + c and a < x + w and y < b + d and b < y + h:
                raise ValueError(f"{name} overlaps {n}")
        claimed.append((name, x, y, w, h))

    # ------------------------------------------------ the plain, river, border of trees
    m.fill(X0, Y0, SIZE, SIZE, Z, "grass")
    for y in range(Y0, Y0 + SIZE):
        for x in range(X0, X0 + SIZE):
            if x < X0 + 3 or y < Y0 + 3 or x >= X0 + SIZE - 3 or y >= Y0 + SIZE - 3:
                m.put(x, y, Z, m.pick("tree"))
    river_x = X0 + 120
    for y in range(Y0 + 3, Y0 + SIZE - 3):
        wobble = (y // 17) % 3 - 1
        m.fill(river_x + wobble, y, 5, 1, Z, "water")

    # ------------------------------------------------ hunting camps first (roads and towns are drawn over them)
    def camp(c):
        cx, cy, w, h = X0 + c["x"], Y0 + c["y"], c["w"], c["h"]
        key, density = c["decor"]
        m.scatter(cx, cy, w, h, Z, key, density)
        total = int(w * h / 30)  # about one monster per 30 tiles: room for 20 players, still monsters for 500
        placed = []
        for mon, size, share in c["mix"]:
            for _ in range(max(1, round(total * share / size))):
                for _try in range(60):
                    sx, sy = cx + rng.randint(4, w - 5), cy + rng.randint(4, h - 5)
                    if all(abs(sx - px) + abs(sy - py) >= 8 for px, py in placed):
                        break
                placed.append((sx, sy))
                for p in [(sx + a, sy + b, Z) for a in (-1, 0, 1) for b in (-1, 0, 1)]:
                    m.clear_items(*p)
                m.monsters.append((mon, (sx, sy, Z), 3, size, c["respawn"]))
        m.points["camp_" + c["id"]] = (cx + w // 2, cy + h // 2, Z)

    for c in CAMPS:
        camp(c)

    # ------------------------------------------------ Hearthgate: a compact walled city (80 x 72)
    # Plan (x across, y down):  shop row along the north wall, a plaza in front of the temple, depot and workshop
    # either side of the temple, two streets of houses to the south. Every service is within about 30 steps of the temple.
    tx, ty, tw, th = X0 + TOWN["x"], Y0 + TOWN["y"], TOWN["w"], TOWN["h"]
    m.fill(tx, ty, tw, th, Z, "cobble")
    gates = {(tx + tw // 2, ty), (tx + tw // 2 + 1, ty), (tx, ty + th // 2), (tx, ty + th // 2 + 1),
             (tx + tw - 1, ty + th // 2), (tx + tw - 1, ty + th // 2 + 1), (tx + tw // 2, ty + th - 1), (tx + tw // 2 + 1, ty + th - 1)}
    m.walls(tx, ty, tw, th, Z, gaps=gates)
    m.flag(tx + 1, ty + 1, tw - 2, th - 2, Z, 0x0001)  # whole town is a safe zone (DESIGN 6.2)
    gate_n = (tx + tw // 2, ty)

    # temple (centre, door to the north plaza)
    tpx, tpy = tx + 30, ty + 26
    claim("temple", tpx, tpy, 20, 14)
    m.building(tpx, tpy, 20, 14, Z, floor="marble", door_side="n")
    temple = (tpx + 10, tpy + 7, Z)
    m.put(tpx + 10, tpy + 3, Z, 3515)  # altar
    m.towns.append((1, "Hearthgate", temple))
    m.points["temple_hearthgate"] = temple
    m.npcs.append(("Priest Odran", (tpx + 14, tpy + 5, Z)))
    m.sign(tpx + 9, tpy + 12, Z, "Hearthgate Temple. Priest Odran heals the wounded and sells blessings.")
    # offline training statues (sword, axe, club, distance, magic): use one to log out and train slowly
    for i, sid in enumerate(range(16198, 16203)):
        m.put(tpx + 3 + i * 3, tpy + 1, Z, sid)
    m.sign(tpx + 17, tpy + 1, Z, "Offline training: use a statue to log out and train that skill slowly while you're away.")

    # plaza (x 18..61, y 14..25): fountain, monument, notice sign
    m.put(tx + 28, ty + 19, Z, 1922)
    m.put(tx + 52, ty + 19, Z, 1922)
    m.sign(tx + 52, ty + 22, Z, "The Monument. Names of those who opened the tower's floors are carved here. Say !top for the climbers, !memorial for the fallen.")
    m.points["monument"] = (tx + 52, ty + 20, Z)
    m.sign(tx + 40, ty + 14, Z, "Hearthgate. Shops to the north, the Ascendancy west, the Guild Hall east, the depot and workshop beside the temple, houses south. Say !guide for your first steps.")
    m.npcs.append(("Vesper", (tx + 57, ty + 22, Z)))
    m.npcs.append(("Captain Dorrow", (tx + 43, ty + 2, Z)))

    # shop row along the north wall (door south, sign in front). NPC stands 3 tiles inside.
    shops = [("General Store", 3, "Merchant Wenna"), ("Weaponsmith", 15, "Weaponsmith Garrick"), ("Armorer", 27, "Armorer Hesta"),
             ("Quartermaster's Stores", 45, "Quartermaster Bryn"), ("Bank", 57, "Banker Tolliver"), ("Hunters' Hall", 69, "Taskmaster Ren")]
    for name, rx, npc in shops:
        sx = tx + rx
        claim(name, sx, ty + 4, 10, 9)
        m.building(sx, ty + 4, 10, 9, Z, floor="wood", door_side="s")
        m.sign(sx + 5, ty + 13, Z, name)
        m.points["shop_" + name.lower().replace("'", "").replace(" ", "_")] = (sx + 5, ty + 8, Z)
        m.npcs.append((npc, (sx + 5, ty + 7, Z)))
    m.npcs.append(("Bounty Warden Cass", (tx + 71, ty + 9, Z)))   # inside the Hunters' Hall
    m.npcs.append(("Hunter Brannoch", (tx + 76, ty + 7, Z)))

    # the Ascendancy (promotion hall, west of the plaza) and the Guild Hall (east)
    claim("ascendancy", tx + 4, ty + 15, 14, 10)
    m.building(tx + 4, ty + 15, 14, 10, Z, floor="marble", door_side="e")
    m.sign(tx + 18, ty + 18, Z, "The Ascendancy. Climbers of level 20 and above may be promoted here.")
    m.npcs.append(("Ascendant Veyra", (tx + 10, ty + 19, Z)))
    claim("guildhall", tx + 62, ty + 15, 14, 10)
    m.building(tx + 62, ty + 15, 14, 10, Z, floor="wood", door_side="w")
    m.sign(tx + 61, ty + 18, Z, "Guild Hall. Found a guild, read the recruiting board.")
    m.npcs.append(("Guildwarden Sela", (tx + 69, ty + 19, Z)))

    # depot (west of the temple, door facing it) and the Housewright's workshop (east, door facing it)
    dx, dy = tx + 6, ty + 26
    claim("depot", dx, dy, 16, 10)
    m.building(dx, dy, 16, 10, Z, floor="wood", door_side="e")
    for i in range(4):
        m.depot(dx + 3 + i * 3, dy + 1, Z, 1)
    m.put(dx + 14, dy + 8, Z, 3501)  # mailbox
    m.sign(dx + 16, dy + 3, Z, "Hearthgate Depot")
    m.points["depot_hearthgate"] = (dx + 8, dy + 5, Z)
    claim("workshop", tx + 60, ty + 26, 16, 10)
    m.building(tx + 60, ty + 26, 16, 10, Z, floor="wood", door_side="w")
    m.sign(tx + 59, ty + 29, Z, "Housewright's Workshop: furniture kits and tapestries.")
    m.npcs.append(("Housewright Orla", (tx + 68, ty + 30, Z)))

    # houses (south): two streets of small houses with the main avenue (x 38..44) left open to the south gate
    hid = 1
    for row_y, side in ((46, "n"), (56, "s")):
        for hx_rel in (3, 12, 21, 30, 45, 54, 63):
            hx, hy = tx + hx_rel, ty + row_y
            claim(f"house {hid}", hx, hy, 8, 8)
            m.house_building(hid, f"Lantern Row {hid}", hx, hy, 8, 8, Z, town=1, rent=1500, door_side=side)
            hid += 1
    # Underkeep grate (sealed; it becomes a secret in task 2.10)
    grate = (tx + 6, ty + 67, Z)
    m.put(*grate, 435)
    m.sign(tx + 7, ty + 67, Z, "An old drain grate. Something echoes far below.")
    m.points["underkeep_grate"] = grate

    # ------------------------------------------------ housing outside the walls (cheaper, less safe)
    # Wallside Cabins: two clusters of ten small cabins beside the west and east roads. Fisher's Huts: ten on the river bank.
    for cluster, x_start in (("West", tx - 44), ("East", tx + tw + 5)):
        for row_y in (40, 49):
            for i in range(5):
                hx, hy = x_start + i * 8, ty + row_y
                claim(f"{cluster} cabin {hid}", hx, hy, 7, 6)
                m.house_building(hid, f"Wallside Cabin {hid}", hx, hy, 7, 6, Z, town=1, rent=600, door_side="n")
                hid += 1
        lane0 = x_start - 2
        m.road((lane0, ty + 39), (lane0 + 43, ty + 39), Z, width=2)
        m.road((lane0, ty + 48), (lane0 + 43, ty + 48), Z, width=2)
    fisher = []
    for col_x in (X0 + 134, X0 + 146):
        for j in range(5):
            hx, hy = col_x, Y0 + 192 + j * 8
            claim(f"fisher hut {hid}", hx, hy, 7, 6)
            m.house_building(hid, f"Fisher's Hut {hid}", hx, hy, 7, 6, Z, town=1, rent=500, door_side="w")
            fisher.append((hx, hy))
            hid += 1
    m.npcs.append(("Fisher Corwin", (X0 + 143, Y0 + 190, Z)))
    m.sign(X0 + 143, Y0 + 192, Z, "Fisher's Huts. Cheap homes on the river bank, outside the city walls.")

    # ------------------------------------------------ roads
    m.road((tx - 60, ty + th // 2), (tx + tw // 2, ty + th // 2), Z)        # west road (crosses the river: bridge)
    m.road((tx + tw // 2, ty + th // 2), (tx + tw + 60, ty + th // 2), Z)   # east road
    m.road((tx + tw // 2, Y0 + 90), (tx + tw // 2, ty), Z)                  # north road to the Pass
    m.road((tx + tw // 2, ty + th), (tx + tw // 2, Y0 + 372), Z)        # south road
    m.road((X0 + 60, Y0 + 220), (X0 + 130, Y0 + 220), Z)                    # Millcross to the river bank
    m.road((X0 + 130, Y0 + 220), (tx - 60, ty + th // 2), Z)                # river bank to the west road
    m.road((tx + tw // 2, Y0 + 205), (X0 + 280, Y0 + 205), Z)               # north road east to the Burrow Hills
    m.road((X0 + 280, Y0 + 205), (X0 + 280, Y0 + 150), Z)                   # ... and on to the quarry
    m.road((tx + tw + 60, ty + th // 2), (X0 + 345, ty + th // 2), Z)       # east road on towards the bandits and shards
    m.road((X0 + 345, ty + th // 2), (X0 + 345, Y0 + 232), Z)
    m.road((tx + tw // 2, Y0 + 368), (X0 + 175, Y0 + 368), Z)       # south road west to the Boar Meadow
    m.road((tx + tw // 2, Y0 + 368), (X0 + 345, Y0 + 368), Z)       # south road east to the Shard Fields
    m.road((X0 + 345, ty + th // 2), (X0 + 345, Y0 + 368), Z)
    m.road((X0 + 70, Y0 + 235), (X0 + 70, Y0 + 330), Z)                     # Millcross south to the Wolf Copse and Reedmarsh
    m.road((tx + tw // 2, Y0 + 110), (X0 + 160, Y0 + 110), Z)               # north road west to the Thornsnap Hollow
    m.road((X0 + 160, Y0 + 110), (X0 + 160, Y0 + 140), Z)

    # ------------------------------------------------ Millcross village (town 2 on floor 1)
    mx, my = X0 + MILLCROSS["x"], Y0 + MILLCROSS["y"]
    mw, mh = MILLCROSS["w"], MILLCROSS["h"]
    m.fill(mx, my, mw, mh, Z, "dirt")
    m.flag(mx, my, mw, mh, Z, 0x0001)
    m.building(mx + 18, my + 4, 14, 10, Z, floor="wood", door_side="s")  # inn
    m.sign(mx + 25, my + 15, Z, "Millcross Inn")
    m.npcs.append(("Miller Agna", (mx + 24, my + 9, Z)))
    m.npcs.append(("Innkeeper Bess", (mx + 28, my + 9, Z)))
    for row_y in (24, 34):
        for i in range(4):
            claim(f"cottage {hid}", mx + 3 + i * 15, my + row_y, 9, 8)
            m.house_building(hid, f"Millcross Cottage {hid}", mx + 3 + i * 15, my + row_y, 9, 8, Z, town=2, rent=800, door_side="n")
            hid += 1
    m.towns.append((2, "Millcross", (mx + 25, my + 18, Z)))

    # ------------------------------------------------ the Arrival Yard (town 50): where every new character starts
    yx, yy = X0 + 270, Y0 + 332
    m.fill(yx, yy, 40, 24, Z, "grass")
    m.fill(yx + 1, yy + 10, 38, 4, Z, "stonefloor")  # the path, west to east
    m.walls(yx, yy, 40, 24, Z)
    m.flag(yx + 1, yy + 9, 8, 6, Z, 0x0001)           # the arrival square is safe; the rat pen is not
    spawn = (yx + 4, yy + 11, Z)
    m.towns.append((50, "Arrival Yard", spawn))
    m.points["tutorial_spawn"] = spawn
    m.sign(yx + 3, yy + 9, Z, "Welcome to the Spirebound tower. Click the ground to walk. Follow the stone path east: each stop teaches one thing. Guide Pell will help.")
    m.npcs.append(("Guide Pell", (yx + 6, yy + 11, Z)))
    pen = (yx + 13, yy + 2, 11, 6)
    m.walls(pen[0], pen[1], pen[2], pen[3], Z, gaps={(pen[0] + 5, pen[1] + 5)})
    m.fill(pen[0] + 1, pen[1] + 1, pen[2] - 2, pen[3] - 2, Z, "dirt")
    m.clear_items(pen[0] + 5, pen[1] + 5, Z)
    m.fill(pen[0] + 5, pen[1] + 6, 1, 4, Z, "stonefloor")  # little path from the gap down to the main path
    m.monsters.append(("Field Rat", (pen[0] + 5, pen[1] + 3, Z), 3, 3, 15))
    m.points["tutorial_pen"] = (pen[0] + 5, pen[1] + 4, Z)
    m.sign(yx + 11, yy + 9, Z, "Stop 1: Fighting. Click a rat in the pen to attack it. Rats are weak. When it falls, open the body (right-click) and take what it carries.")
    m.sign(yx + 21, yy + 9, Z, "Stop 2: Sword skills and spells. The bar on the right holds your skills (Shift+1..6). Say !spells to see what you will learn. Press J for your Journal.")
    m.sign(yx + 27, yy + 9, Z, "Stop 3: The Registrar's hall is ahead. Choose your path and how hard you want to live. Then you are sent to Hearthgate.")
    m.building(yx + 29, yy + 7, 10, 10, Z, floor="marble", door_side="w")
    m.npcs.append(("Registrar Maelis", (yx + 34, yy + 12, Z)))
    m.points["tutorial_registrar"] = (yx + 34, yy + 12, Z)

    # ------------------------------------------------ apex spawn: the Old Watchtower (Contested from task 2.2)
    ax, ay = X0 + 30, Y0 + 30
    m.fill(ax, ay, 44, 44, Z, "stonefloor")
    m.walls(ax, ay, 44, 44, Z, gaps={(ax + 22, ay + 43), (ax + 23, ay + 43)})
    m.walls(ax + 12, ay + 12, 20, 20, Z, gaps={(ax + 22, ay + 31)})  # the packed inner room
    m.monsters.append(("Stonehorn Ram", (ax + 8, ay + 36, Z), 3, 3, 90))
    m.monsters.append(("Stonehorn Ram", (ax + 36, ay + 36, Z), 3, 3, 90))
    m.monsters.append(("Stonehorn Ram", (ax + 22, ay + 22, Z), 4, 8, 90))
    # semi-hidden rope spot to the cliff caves (z 8), a Deadzone later
    cx, cy, cz = ax, ay, 8
    m.fill(cx, cy, 44, 44, cz, "cavefloor")
    m.walls(cx, cy, 44, 44, cz)
    m.teleport((ax + 40, ay + 3, Z), (cx + 4, cy + 4, cz), "apex_rope_spot")
    m.teleport((cx + 3, cy + 3, cz), (ax + 39, ay + 4, Z), "apex_cave_exit")
    m.monsters.append(("Stonehorn Ram", (cx + 22, cy + 22, cz), 5, 9, 90))
    m.points["apex_watchtower"] = (ax + 22, ay + 40, Z)

    # ------------------------------------------------ the Pass (field boss arena) and the labyrinth
    px, py = gate_n[0] - 12, Y0 + 70
    m.fill(px, py, 24, 20, Z, "stonefloor")
    m.walls(px, py, 24, 20, Z, gaps={(px + 12, py + 19), (px + 13, py + 19), (px + 12, py), (px + 13, py)})
    m.points["gate_hound_spawn"] = (px + 12, py + 9, Z)  # spawned by script (it never returns once dead)
    m.points["pass_arena"] = (px + 12, py + 10, Z)
    # sealed until the Gate Hound dies once (scripts remove the boulders)
    for i, gx in enumerate((px + 12, px + 13)):
        m.put(gx, py, Z, 1772)
        m.points[f"gate_pass_{i + 1}"] = (gx, py, Z)
    # labyrinth level 1 (z 7) north of the Pass
    lx, ly = px - 10, Y0 + 12
    m.fill(px + 11, ly + 31, 4, py - (ly + 31), Z, "stonefloor")  # corridor from the Pass to the maze
    e1, x1 = m.maze(lx, ly, 14, 10, Z, seed=11)
    m.ground[(lx + 22, ly + 31, Z)] = 416; m.ground[(lx + 23, ly + 31, Z)] = 416
    for p in [(lx + 22, ly + 30, Z), (lx + 23, ly + 30, Z), (lx + 22, ly + 31, Z), (lx + 23, ly + 31, Z)]:
        m.clear_items(*p)
    # levels 2 and 3 (z 6, z 5) and the boss room (z 4) stacked above
    e2, x2 = m.maze(lx, ly, 14, 10, 6, seed=22)
    e3, x3 = m.maze(lx, ly, 14, 10, 5, seed=33)
    m.teleport(x1, (e2[0] + 1, e2[1], 6), "lab1_up")
    m.teleport(x2, (e3[0] + 1, e3[1], 5), "lab2_up")
    m.teleport(e2, (x1[0] + 1, x1[1], Z), "lab2_down")
    m.teleport(e3, (x2[0] + 1, x2[1], 6), "lab3_down")
    m.monsters.append(("Ruin Sentinel", (lx + 20, ly + 15, Z), 4, 4, 90))
    m.monsters.append(("Ruin Archer", (lx + 20, ly + 15, 6), 4, 4, 90))
    m.monsters.append(("Ruin Sentinel", (lx + 20, ly + 15, 5), 4, 5, 90))
    # boss room (z 4) with a back chamber holding the stair to floor 2
    bx, by, bz = lx + 6, ly + 2, 4
    m.fill(bx, by, 30, 24, bz, "stonefloor")
    m.walls(bx, by, 30, 24, bz)
    m.teleport(x3, (bx + 15, by + 21, bz), "lab3_up")
    m.teleport((bx + 15, by + 22, bz), (x3[0] + 1, x3[1], 5), "boss_room_exit")
    m.points["axe_lord_spawn"] = (bx + 15, by + 10, bz)  # spawned by script
    m.points["boss_room_floor1"] = (bx + 15, by + 12, bz)
    m.points["boss_room_floor1_nw"] = (bx + 1, by + 1, bz)
    m.points["boss_room_floor1_se"] = (bx + 28, by + 22, bz)
    m.sign(bx + 13, by + 21, bz, "Beyond this door the tower's protection ends.")
    # stair to floor 2 (sealed by a boulder until the first clear)
    m.put(bx + 15, by + 2, bz, 1772)
    m.points["gate_floor2"] = (bx + 15, by + 2, bz)
    # the stair sits in a walled back chamber: the boulder tile is the only way in (no walking around it)
    for wx in range(bx + 1, bx + 29):
        if wx != bx + 15:
            m.put(wx, by + 2, bz, 1271)  # horizontal brick wall (tools/mapgen.py ID["wall_h"])

    # stair to floor 2: linked to Floor 2's landing by tools/mapgen.py (link_floors)
    m.points["stair_floor2_src"] = (bx + 15, by + 1, bz)

    # ------------------------------------------------ PvP zone tiers (DESIGN.md 6.3). Default everywhere: Open.
    m.zone("open", X0, Y0, SIZE, SIZE)
    # guarded ring: the city, its cabins and roads, the four starter camps, the fisher huts and the Arrival Yard
    m.zone("guarded", tx - 60, ty - 12, tw + 120, th + 24, 7)
    for c in CAMPS:
        if c["zone"] == "guarded":
            m.zone("guarded", X0 + c["x"] - 6, Y0 + c["y"] - 6, c["w"] + 12, c["h"] + 12, 7)
    m.zone("guarded", tx + 10, Y0 + 195, 70, 55, 7)                  # the gate road up to the Waspgrass Fields
    m.zone("guarded", X0 + 128, Y0 + 186, 30, 50, 7)                 # the fisher huts
    m.zone("guarded", yx - 2, yy - 2, 44, 28, 7)                      # the Arrival Yard
    m.zone("guarded", mx - 20, my - 20, mw + 40, mh + 40, 7)         # around Millcross
    m.zone("contested", ax - 5, ay - 5, 54, 54, 7)                   # the Old Watchtower approach and outer layer
    m.zone("deadzone", ax + 12, ay + 12, 20, 20, 7)                  # the packed inner room
    m.zone("deadzone", cx, cy, 44, 44, 8)                            # the cliff caves below
    m.zone("bossroom", px, py, 24, 20, 7)                            # the Pass arena
    m.zone("bossroom", bx, by, 30, 24, 4)                            # the Axe-Lord's room
    m.zone("town", tx, ty, tw, th, 7)
    m.zone("town", mx, my, mw, mh, 7)

    # ------------------------------------------------ Floor 1 secrets (DESIGN.md 8.1). Trigger tiles only; no markers.
    def secret(sid, x, y, z=Z):
        if (x, y, z) not in m.ground:
            raise ValueError(f"secret {sid} has no ground at {(x, y, z)}")
        m.clear_items(x, y, z)  # trigger tiles must be walkable
        m.points["secret_" + sid] = (x, y, z)
    secret("s1", tx + 6, ty + 68)                       # beside the drain grate
    bm = m.points["camp_boar_meadow"]
    secret("s2", bm[0] + 18, bm[1] + 2)                 # mud wallow east of the boar meadow
    m.points["old_tusk_spawn"] = (bm[0] + 15, bm[1] + 4, Z)
    secret("s3", mx + 30, my + 8)                       # under the Millcross mill (inn back room)
    secret("s4", mx + 21, my + 6)                       # false pantry shelf in the inn
    secret("s5", X0 + 225, Y0 + 132)                    # cracked wall in the old quarry
    m.points["north_crack_exit"] = (mx + 25, my + 20, Z)
    secret("s6", mx + 44, my + 2)                       # hollow behind the Millcross well (night only)
    secret("s7", X0 + 352, Y0 + 186)                    # ruined shrine on the bandit road
    secret("s8", X0 + 330, Y0 + 330)                    # plates in the shard fields
    secret("s9", X0 + 44, Y0 + 300)                     # abandoned bedroll in the wolf copse
    secret("s10", X0 + 380, Y0 + 380)                   # ruined well in the south-east corner
    secret("s11", X0 + 160, Y0 + 170)                   # bramble ring in the thornsnap hollow
    secret("s12", X0 + 296, Y0 + 60)                    # broken stair of a ruined side tower near the Pass

    # ------------------------------------------------ The Underkeep, Wing 1 (DESIGN.md 3.4), under Hearthgate at z 8
    ux, uy, uz = tx, ty + 10, 8
    m.fill(ux, uy, 70, 50, uz, "cavefloor")
    m.walls(ux, uy, 70, 50, uz)
    # a water channel and column hall
    for y in range(uy + 3, uy + 47):
        m.ground[(ux + 20, y, uz)] = m.pick("water")
        m.ground[(ux + 21, y, uz)] = m.pick("water")
    for y in (uy + 15, uy + 16, uy + 30, uy + 31):  # crossings
        m.ground[(ux + 20, y, uz)] = 351
        m.ground[(ux + 21, y, uz)] = 351
    for cx_ in range(ux + 30, ux + 66, 6):
        for cy_ in range(uy + 6, uy + 46, 8):
            m.put(cx_, cy_, uz, ID_PILLAR)
    m.points["underkeep_entry"] = (ux + 4, uy + 4, uz)
    m.teleport((ux + 2, uy + 2, uz), (tx + 7, ty + 69, Z), "underkeep_exit")
    m.monsters.append(("Mire Toad", (ux + 10, uy + 25, uz), 4, 5, 90))
    m.monsters.append(("Mire Toad", (ux + 40, uy + 12, uz), 4, 4, 90))
    m.monsters.append(("Black Crawler", (ux + 45, uy + 30, uz), 4, 5, 90))
    m.monsters.append(("Black Crawler", (ux + 58, uy + 40, uz), 4, 4, 90))
    # daily chest room (scripted reward, task 2.10) and the sealed door to Wing 2
    m.points["underkeep_chest"] = (ux + 64, uy + 4, uz)
    m.walls(ux + 58, uy + 1, 11, 8, uz, gaps={(ux + 58, uy + 4)})
    m.put(ux + 64, uy + 4, uz, 3515)  # an old stone altar used as the daily strongbox (scripted)
    m.points["underkeep_wing2_door"] = (ux + 69, uy + 25, uz)
    m.sign(ux + 67, uy + 25, uz, "A black iron door. Sealed until the tower reaches Floor 2.")

    # ------------------------------------------------ Underkeep Wings 2-6 (DESIGN.md 3.4): one per two floors cleared
    # wing: (x, y, z, w, h, monsters, opens when floor N is open, boss)
    wings = [
        (2, ux + 70, uy + 5, uz, 60, 40, ["Vault Rat", "Chain Ghoul"], 2, "Drain Matron"),
        (3, ux, uy, 9, 60, 50, ["Trap Mimic", "Iron Shade"], 4, None),
        (4, ux - 55, uy + 5, 9, 50, 40, ["Keep Warden", "Iron Shade"], 6, None),
        (5, ux, uy, 10, 40, 40, ["Keep Warden", "Chain Ghoul"], 8, "Vault Warden"),
        (6, ux + 45, uy, 10, 45, 40, ["Deep Sentinel", "Vault Wraith"], 10, "The Underkeeper"),
    ]
    prev_exit = {2: (ux + 69, uy + 25, uz)}
    for wid, wx, wy, wz, ww, wh, mons, req, boss in wings:
        m.fill(wx, wy, ww, wh, wz, "cavefloor")
        m.walls(wx, wy, ww, wh, wz)
        for i, mon in enumerate(mons):
            for j in range(2):
                m.monsters.append((mon, (wx + 10 + j * (ww // 2), wy + 10 + i * (wh // 3), wz), 4, 4, 90))
        if boss:
            m.monsters.append((boss, (wx + ww - 8, wy + wh - 8, wz), 1, 1, 1800))
        entry = (wx + 3, wy + 3, wz)
        m.points[f"uk_wing{wid}_entry"] = entry
        m.points[f"uk_wing{wid}_req"] = (req, 0, 0)  # floor that opens it (read by scripts/spirebound/underkeep.lua)
        m.sign(wx + 4, wy + 1, wz, f"Underkeep, Wing {wid}.")
    # doors between wings: a portal guarded by a boulder until the wing opens
    links = [(2, (ux + 66, uy + 25, uz)), (3, (ux + 5, uy + 45, uz)), (4, (ux + 60, uy + 44, uz)),
             (5, (ux + 6, uy + 44, 9)), (6, (ux + 30, uy + 35, 10))]
    for wid, src in links:
        if src not in m.ground:
            continue
        m.clear_items(*src)
        e = m.points[f"uk_wing{wid}_entry"]
        m.teleport(src, (e[0] + 1, e[1] + 1, e[2]), f"uk_door{wid}")  # sealed by script until the wing opens
        m.points[f"uk_door{wid}_dest"] = (e[0] + 1, e[1] + 1, e[2])
        back = (e[0] - 1, e[1] - 1, e[2])
        m.teleport(back, (src[0] - 2, src[1], src[2]), f"uk_back{wid}")


    # ------------------------------------------------ The Arena (DESIGN.md 15, roadmap 5.7c): z 11, reached only by
    # event teleport. Engine PvP-zone flag (0x10): no skulls, no death loss. Two team starts and a banner tile.
    ax0, ay0, az = X0 + 10, Y0 + 10, 11
    m.fill(ax0, ay0, 40, 30, az, "gravel")
    m.walls(ax0, ay0, 40, 30, az)
    m.flag(ax0 + 1, ay0 + 1, 38, 28, az, 0x0010)
    for px_, py_ in ((ax0 + 12, ay0 + 9), (ax0 + 27, ay0 + 9), (ax0 + 12, ay0 + 20), (ax0 + 27, ay0 + 20)):
        m.put(px_, py_, az, ID_PILLAR)  # cover
    m.fill(ax0 + 18, ay0 + 13, 4, 4, az, "stonefloor")  # the banner square
    m.points["arena_a"] = (ax0 + 4, ay0 + 15, az)
    m.points["arena_b"] = (ax0 + 35, ay0 + 15, az)
    m.points["arena_center"] = (ax0 + 20, ay0 + 15, az)
    m.points["arena_nw"] = (ax0 + 1, ay0 + 1, az)
    m.points["arena_se"] = (ax0 + 38, ay0 + 28, az)
    m.zone("arena", ax0, ay0, 40, 30, az)

    # ------------------------------------------------ Spire Siege keep (DESIGN.md 15, roadmap 5.7d): z 11, event
    # teleport only. Courtyard with four guild gates and the throne room in the middle (PvP-zone flag).
    sx0, sy0, sz = X0 + 70, Y0 + 10, 11
    m.fill(sx0, sy0, 60, 50, sz, "gravel")
    m.walls(sx0, sy0, 60, 50, sz)
    m.flag(sx0 + 1, sy0 + 1, 58, 48, sz, 0x0010)
    kx, ky = sx0 + 22, sy0 + 17
    m.fill(kx, ky, 16, 16, sz, "marble")
    m.walls(kx, ky, 16, 16, sz, gaps={(kx + 8, ky), (kx + 8, ky + 15), (kx, ky + 8), (kx + 15, ky + 8)})
    m.points["siege_throne"] = (kx + 8, ky + 8, sz)
    m.points["siege_throne_nw"] = (kx + 1, ky + 1, sz)
    m.points["siege_throne_se"] = (kx + 14, ky + 14, sz)
    m.points["siege_gate_1"] = (sx0 + 4, sy0 + 4, sz)
    m.points["siege_gate_2"] = (sx0 + 55, sy0 + 4, sz)
    m.points["siege_gate_3"] = (sx0 + 4, sy0 + 45, sz)
    m.points["siege_gate_4"] = (sx0 + 55, sy0 + 45, sz)
    m.zone("siege", sx0, sy0, 60, 50, sz)
