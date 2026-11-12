"""Generic placeholder layout for floors 2-10 (roadmap phases 4-5). Content comes from maps/floors.py.
Each floor: a town (temple, depot, shops, houses, quest givers), roads, 6 hunting camps, a lake, an apex spawn with a
cave below (Contested/Deadzone), the Pass (field boss), a 3-level maze labyrinth (z 6, 5) and the boss room (z 4).
Named points are prefixed f<N>_ so scripts can find them. The real maps are MAP_REQUESTS.md M3."""

from floors import FLOORS, SIZE, origin

ID_PILLAR = 1296  # grey stone post (a free-standing column)
BIOME_KEYS = {"grass": "grass", "dried": "dried", "dirt": "dirt", "jungle": "jungle", "dirtfloor": "cavefloor",
              "sand": "sand", "cobble": "cobble", "gravel": "gravel", "stonefloor": "stonefloor", "rocksoil": "rocksoil",
              "earth": "earth", "swamp": "swamp", "mud": "mud", "wood": "wood", "snow": "snow", "blackmarble": "blackmarble"}


def build(m, n):
    spec = FLOORS[n]
    X0, Y0 = origin(n)
    Z = 7
    rng = m.rng
    base, accent, path = (BIOME_KEYS[k] for k in spec["biome"])
    P = f"f{n}_"
    town_id = n + 1

    # ground, accent patches, tree border
    m.fill(X0, Y0, SIZE, SIZE, Z, base)
    for _ in range(25):
        ax, ay = X0 + rng.randint(5, SIZE - 30), Y0 + rng.randint(5, SIZE - 30)
        m.fill(ax, ay, rng.randint(8, 25), rng.randint(8, 25), Z, accent)
    for y in range(Y0, Y0 + SIZE):
        for x in range(X0, X0 + SIZE):
            if x < X0 + 3 or y < Y0 + 3 or x >= X0 + SIZE - 3 or y >= Y0 + SIZE - 3:
                m.put(x, y, Z, m.pick("tree"))

    # town (south centre)
    tw, th = 90, 70
    tx, ty = X0 + (SIZE - tw) // 2, Y0 + SIZE - th - 20
    m.fill(tx, ty, tw, th, Z, "cobble")
    gates = {(tx + tw // 2, ty), (tx + tw // 2 + 1, ty), (tx, ty + th // 2), (tx, ty + th // 2 + 1),
             (tx + tw - 1, ty + th // 2), (tx + tw - 1, ty + th // 2 + 1)}
    m.walls(tx, ty, tw, th, Z, gaps=gates)
    m.flag(tx + 1, ty + 1, tw - 2, th - 2, Z, 0x0001)
    tpx, tpy = tx + 35, ty + 24
    m.building(tpx, tpy, 20, 12, Z, floor="marble", door_side="s")
    temple = (tpx + 10, tpy + 6, Z)
    m.put(tpx + 10, tpy + 2, Z, 3515)
    for i, sid in enumerate(range(16198, 16203)):
        m.put(tpx + 2 + i * 3, tpy + 1, Z, sid)
    m.towns.append((town_id, spec["town"], temple))
    m.points[P + "temple"] = temple
    m.points[f"floor{n}_landing"] = (temple[0], temple[1] + 2, Z)
    m.points[P + "down_src"] = (tpx + 3, tpy + 9, Z)  # portal back down (linked in tools/mapgen.py)
    m.sign(tpx + 4, tpy + 9, Z, f"Portal down to Floor {n - 1}.")
    m.npcs.append((f"Priest of {spec['town']}", (tpx + 15, tpy + 4, Z)))
    m.sign(tpx + 9, tpy + 10, Z, f"{spec['town']} Temple. Floor {n}: {spec['name']}.")
    dx, dy = tx + 6, ty + 6
    m.building(dx, dy, 16, 10, Z, floor="wood", door_side="s")
    for i in range(4):
        m.depot(dx + 3 + i * 3, dy + 1, Z, town_id)
    m.put(dx + 14, dy + 8, Z, 3501)
    m.npcs.append((f"Quartermaster of {spec['town']}", (dx + 3, dy + 6, Z)))
    for i, role in enumerate(["Banker", "Merchant", "Outfitter"]):
        sx = tx + 28 + i * 14
        m.building(sx, ty + 6, 12, 9, Z, floor="wood", door_side="s")
        m.sign(sx + 6, ty + 15, Z, f"{spec['town']} {role}")
        m.npcs.append((f"{role} of {spec['town']}", (sx + 6, ty + 10, Z)))
    m.npcs.append((f"Elder of {spec['town']}", (tx + 74, ty + 30, Z)))     # quest giver
    m.npcs.append((f"Scout of {spec['town']}", (tx + tw // 2 + 3, ty + 3, Z)))  # quest giver at the north gate
    hid0 = 100 * n
    for i in range(6):
        hx, hy = tx + 8 + (i % 3) * 24, ty + 44 + (i // 3) * 12
        m.house_building(hid0 + i, f"{spec['town']} House {i + 1}", hx, hy, 9, 8, Z, town=town_id, rent=2000 * n + 500 * i, door_side="n")

    # roads
    cx, cy = tx + tw // 2, ty + th // 2
    m.road((X0 + 20, cy), (cx, cy), Z, key=path)
    m.road((cx, cy), (X0 + SIZE - 20, cy), Z, key=path)
    m.road((cx, Y0 + 90), (cx, ty), Z, key=path)

    # a lake for fishing (east)
    lx, ly = X0 + SIZE - 70, Y0 + 120
    m.fill(lx, ly, 26, 14, Z, "water")
    m.points[P + "lake"] = (lx - 1, ly + 7, Z)

    # camps
    camps = [(X0 + 20, Y0 + 150), (X0 + 70, Y0 + 210), (X0 + SIZE - 80, Y0 + 200), (X0 + SIZE - 70, Y0 + 40),
             (X0 + 160, Y0 + 130), (X0 + 40, Y0 + 90)]
    for i, (sx, sy) in enumerate(camps):
        m.scatter(sx, sy, 40, 35, Z, "bush" if base != "snow" else "boulder", 0.04)
        mons = spec["camp"]
        for j in range(3):
            mon = mons[(i + j) % len(mons)]
            px, py = sx + rng.randint(5, 34), sy + rng.randint(5, 29)
            for a in (-1, 0, 1):
                for b in (-1, 0, 1):
                    m.clear_items(px + a, py + b, Z)
            m.monsters.append((mon, (px, py, Z), 3, 4, 60))
        if i in (1, 3):
            m.monsters.append((spec["elite"], (sx + 20, sy + 17, Z), 2, 1, 300))
        m.points[P + f"camp{i + 1}"] = (sx + 20, sy + 17, Z)

    # apex spawn (north-west) + cave below
    ax, ay = X0 + 20, Y0 + 20
    m.fill(ax, ay, 40, 40, Z, "stonefloor")
    m.walls(ax, ay, 40, 40, Z, gaps={(ax + 20, ay + 39), (ax + 21, ay + 39)})
    m.walls(ax + 10, ay + 10, 20, 20, Z, gaps={(ax + 20, ay + 29)})
    m.monsters.append((spec["apex"], (ax + 8, ay + 32, Z), 3, 3, 90))
    m.monsters.append((spec["apex"], (ax + 20, ay + 20, Z), 4, 7, 90))
    m.fill(ax, ay, 40, 40, 8, "cavefloor")
    m.walls(ax, ay, 40, 40, 8)
    m.teleport((ax + 36, ay + 3, Z), (ax + 4, ay + 4, 8), P + "apex_rope")
    m.teleport((ax + 3, ay + 3, 8), (ax + 35, ay + 4, Z), P + "apex_cave_exit")
    m.monsters.append((spec["apex"], (ax + 20, ay + 20, 8), 5, 8, 90))
    m.points[P + "apex"] = (ax + 20, ay + 36, Z)

    # the Pass + labyrinth + boss room (north centre)
    px, py = cx - 12, Y0 + 70
    m.fill(px, py, 24, 20, Z, "stonefloor")
    m.walls(px, py, 24, 20, Z, gaps={(px + 12, py + 19), (px + 13, py + 19), (px + 12, py), (px + 13, py)})
    m.points[P + "field_spawn"] = (px + 12, py + 9, Z)
    m.points[P + "pass_arena"] = (px + 12, py + 10, Z)
    for i, gx in enumerate((px + 12, px + 13)):
        m.put(gx, py, Z, 1772)
        m.points[P + f"gate_pass_{i + 1}"] = (gx, py, Z)
    labx, laby = px - 12, Y0 + 8
    e1, x1 = m.maze(labx, laby, 16, 11, Z, seed=100 + n)
    H = 11 * 3 + 1
    entry_col = (px + 12 - labx) // 3 * 3 + 1
    for yy in range(laby + H - 1, py):
        for xx in (labx + entry_col, labx + entry_col + 1):
            m.ground[(xx, yy, Z)] = 416
            m.clear_items(xx, yy, Z)
    for xx in range(min(labx + entry_col, px + 12), max(labx + entry_col + 2, px + 14)):
        m.ground[(xx, py - 1, Z)] = 416
        m.clear_items(xx, py - 1, Z)
    e2, x2 = m.maze(labx, laby, 16, 11, 6, seed=200 + n)
    e3, x3 = m.maze(labx, laby, 16, 11, 5, seed=300 + n)
    m.teleport(x1, (e2[0] + 1, e2[1], 6), P + "lab1_up")
    m.teleport(x2, (e3[0] + 1, e3[1], 5), P + "lab2_up")
    m.teleport(e2, (x1[0] + 1, x1[1], Z), P + "lab2_down")
    m.teleport(e3, (x2[0] + 1, x2[1], 6), P + "lab3_down")
    for zz in (Z, 6, 5):
        m.monsters.append((spec["labyrinth"], (labx + 24, laby + 16, zz), 5, 5, 90))
    bx, by, bz = labx + 9, laby + 2, 4
    m.fill(bx, by, 30, 24, bz, "stonefloor")
    m.walls(bx, by, 30, 24, bz)
    m.teleport(x3, (bx + 15, by + 21, bz), P + "lab3_up")
    m.teleport((bx + 15, by + 22, bz), (x3[0] + 1, x3[1], 5), P + "boss_exit")
    m.points[P + "boss_spawn"] = (bx + 15, by + 10, bz)
    m.points[P + "boss_nw"] = (bx + 1, by + 1, bz)
    m.points[P + "boss_se"] = (bx + 28, by + 22, bz)
    m.sign(bx + 13, by + 21, bz, "Beyond this door the tower's protection ends.")
    m.put(bx + 15, by + 2, bz, 1772)
    m.points[P + "gate_next"] = (bx + 15, by + 2, bz)
    # the stair sits in a walled back chamber: the boulder tile is the only way in (no walking around it)
    for wx in range(bx + 1, bx + 29):
        if wx != bx + 15:
            m.put(wx, by + 2, bz, 1271)  # horizontal brick wall (tools/mapgen.py ID["wall_h"])
    m.points[f"stair_floor{n + 1}_src"] = (bx + 15, by + 1, bz)

    # Floor 8: the hidden Twin Fang trial (DESIGN.md 5.6): a stone circle inside the apex cave
    if n == 8:
        tf = (ax + 30, ay + 30, 8)
        m.clear_items(*tf)
        m.points["twin_fang_trial"] = tf

    # secrets: 12 trigger tiles spread over the camps and wilds
    spots = [(X0 + 15 + (k * 23) % 260, Y0 + 100 + (k * 37) % 150) for k in range(40)]
    placed = 0
    for (sx, sy) in spots:
        if placed == 12:
            break
        p = (sx, sy, Z)
        if p in m.ground and m.ground[p] not in (4597, 4609) and not m.house.get(p) and not (tx <= sx < tx + tw and ty <= sy < ty + th):
            m.clear_items(*p)
            placed += 1
            m.points[P + f"secret_{placed}"] = p

    # zones
    m.zone("open", X0, Y0, SIZE, SIZE)
    m.zone("guarded", tx - 40, ty - 40, tw + 80, th + 60, Z)
    m.zone("contested", ax - 5, ay - 5, 50, 50, Z)
    m.zone("deadzone", ax + 10, ay + 10, 20, 20, Z)
    m.zone("deadzone", ax, ay, 40, 40, 8)
    m.zone("bossroom", px, py, 24, 20, Z)
    m.zone("bossroom", bx, by, 30, 24, bz)
    m.zone("town", tx, ty, tw, th, Z)
