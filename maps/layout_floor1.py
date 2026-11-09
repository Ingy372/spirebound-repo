"""Floor 1 placeholder layout (roadmap 1.8): Hearthgate Plains. DESIGN.md 3.1-3.5, 9.1-9.2.
Coordinates: Floor 1 occupies x 1000-1399, y 1000-1399, z 7 (labyrinth climbs to z 6, 5, boss room z 4;
the apex cave is z 8). Floor 2's landing is at x 2000+.
Everything here is a playable stand-in; the real map is MAP_REQUESTS.md M1."""

X0, Y0, Z = 1000, 1000, 7
ID_PILLAR = 1273  # wall pole piece used as a column
SIZE = 400


def build(m):
    rng = m.rng
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

    # ------------------------------------------------ Hearthgate (town 1)
    tx, ty, tw, th = X0 + 190, Y0 + 250, 90, 80
    m.fill(tx, ty, tw, th, Z, "cobble")
    gates = {(tx + tw // 2, ty), (tx + tw // 2 + 1, ty), (tx, ty + th // 2), (tx, ty + th // 2 + 1),
             (tx + tw - 1, ty + th // 2), (tx + tw - 1, ty + th // 2 + 1), (tx + tw // 2, ty + th - 1), (tx + tw // 2 + 1, ty + th - 1)}
    m.walls(tx, ty, tw, th, Z, gaps=gates)
    m.flag(tx + 1, ty + 1, tw - 2, th - 2, Z, 0x0001)  # whole town is a safe zone (DESIGN 6.2)

    # temple (centre)
    tpx, tpy = tx + 35, ty + 30
    m.building(tpx, tpy, 20, 14, Z, floor="marble", door_side="s")
    temple = (tpx + 10, tpy + 7, Z)
    m.put(tpx + 10, tpy + 3, Z, 3515)  # altar
    m.towns.append((1, "Hearthgate", temple))
    m.points["temple_hearthgate"] = temple
    m.npcs.append(("Registrar Maelis", (tpx + 6, tpy + 5, Z)))
    m.npcs.append(("Priest Odran", (tpx + 14, tpy + 5, Z)))
    m.sign(tpx + 9, tpy + 12, Z, "Hearthgate Temple. New climbers: speak to Registrar Maelis (say hi).")
    # offline training statues (sword, axe, club, distance, magic): use one to log out and train slowly
    for i, sid in enumerate(range(16198, 16203)):
        m.put(tpx + 3 + i * 3, tpy + 1, Z, sid)
    m.sign(tpx + 17, tpy + 1, Z, "Offline training: use a statue to log out and train that skill slowly while you're away.")

    # depot
    dx, dy = tx + 8, ty + 8
    m.building(dx, dy, 16, 10, Z, floor="wood", door_side="s")
    for i in range(4):
        m.depot(dx + 3 + i * 3, dy + 1, Z, 1)
    m.put(dx + 14, dy + 8, Z, 3501)  # mailbox
    m.sign(dx + 7, dy + 10, Z, "Hearthgate Depot")
    m.points["depot_hearthgate"] = (dx + 8, dy + 5, Z)
    m.npcs.append(("Quartermaster Bryn", (dx + 3, dy + 6, Z)))

    # shops row (NPCs arrive in task 1.15)
    for i, name in enumerate(["General Store", "Weaponsmith", "Armorer", "Bank"]):
        sx = tx + 30 + i * 13
        m.building(sx, ty + 8, 11, 9, Z, floor="wood", door_side="s")
        m.sign(sx + 5, ty + 17, Z, name)
        m.points["shop_" + name.lower().replace(" ", "_")] = (sx + 5, ty + 12, Z)
        npc = {"General Store": "Merchant Wenna", "Weaponsmith": "Weaponsmith Garrick", "Armorer": "Armorer Hesta", "Bank": "Banker Tolliver"}[name]
        m.npcs.append((npc, (sx + 5, ty + 11, Z)))

    # houses (south streets)
    hid = 1
    for row in range(2):
        for col in range(3):
            hx, hy = tx + 10 + col * 24, ty + 52 + row * 13
            m.house_building(hid, f"Lantern Row {hid}", hx, hy, 9, 8, Z, town=1, rent=1000 + 250 * hid, door_side="n")
            hid += 1

    # monument square + fountain
    m.put(tx + 70, ty + 36, Z, 1922)
    m.sign(tx + 70, ty + 39, Z, "The Monument. Names of those who opened the tower's floors are carved here. Say !top for the climbers, !memorial for the fallen.")
    m.points["monument"] = (tx + 70, ty + 37, Z)
    m.npcs.append(("Housewright Orla", (tx + 74, ty + 41, Z)))  # furniture kits, exercise dummy (DESIGN 7.5)
    m.npcs.append(("Bounty Warden Cass", (tx + 66, ty + 42, Z)))
    m.npcs.append(("Guildwarden Sela", (tx + 74, ty + 42, Z)))
    m.npcs.append(("Vesper", (tx + 78, ty + 36, Z)))
    m.npcs.append(("Taskmaster Ren", (tx + 62, ty + 36, Z)))

    # Underkeep grate (sealed; it becomes a secret in task 2.10)
    m.put(tx + 6, ty + 70, Z, 435)
    m.sign(tx + 7, ty + 70, Z, "An old drain grate. Something echoes far below.")
    m.points["underkeep_grate"] = (tx + 6, ty + 70, Z)

    # ------------------------------------------------ roads
    gate_n = (tx + tw // 2, ty)
    m.npcs.append(("Captain Dorrow", (gate_n[0] + 3, ty + 3, Z)))
    m.road((tx - 60, ty + th // 2), (tx + tw // 2, ty + th // 2), Z)        # west road (crosses the river: bridge)
    m.road((tx + tw // 2, ty + th // 2), (tx + tw + 60, ty + th // 2), Z)   # east road
    m.road((tx + tw // 2, Y0 + 90), (tx + tw // 2, ty), Z)                  # north road to the Pass
    m.road((tx + tw // 2, ty + th), (tx + tw // 2, ty + th + 50), Z)        # south road
    m.road((X0 + 60, Y0 + 220), (tx - 60, ty + th // 2), Z)                 # to Millcross

    # ------------------------------------------------ Millcross village (town 2 on floor 1)
    mx, my = X0 + 35, Y0 + 195
    m.fill(mx, my, 50, 40, Z, "dirt")
    m.flag(mx, my, 50, 40, Z, 0x0001)
    m.building(mx + 18, my + 4, 14, 10, Z, floor="wood", door_side="s")  # inn
    m.sign(mx + 25, my + 15, Z, "Millcross Inn")
    m.npcs.append(("Miller Agna", (mx + 24, my + 9, Z)))
    for i in range(3):
        m.house_building(hid, f"Millcross Cottage {i + 1}", mx + 3 + i * 16, my + 24, 9, 8, Z, town=2, rent=800, door_side="n")
        hid += 1
    m.towns.append((2, "Millcross", (mx + 25, my + 18, Z)))

    # ------------------------------------------------ starter fields (Guarded) and hunting camps
    def camp(name, cx, cy, w, h, monsters, decor="bush", density=0.04):
        m.scatter(cx, cy, w, h, Z, decor, density)
        for mon, count in monsters:
            sx = cx + rng.randint(4, w - 5)
            sy = cy + rng.randint(4, h - 5)
            for p in [(sx + a, sy + b, Z) for a in (-1, 0, 1) for b in (-1, 0, 1)]:
                m.clear_items(*p)
            m.monsters.append((mon, (sx, sy, Z), 3, count, 60))
        m.points["camp_" + name] = (cx + w // 2, cy + h // 2, Z)

    camp("starter_west", tx - 58, ty + 5, 45, 30, [("Field Rat", 4), ("Hopper Toad", 3), ("Field Rat", 4)], "flowers", 0.03)
    camp("starter_south", tx + 20, ty + th + 8, 50, 35, [("Sproutling", 4), ("Field Rat", 3), ("Hopper Toad", 4)], "flowers", 0.03)
    camp("starter_east", tx + tw + 8, ty + 5, 50, 30, [("Hopper Toad", 4), ("Sproutling", 4), ("Field Rat", 3)], "flowers", 0.03)
    camp("boar_meadow", X0 + 150, Y0 + 330, 40, 40, [("Bristle Boar", 4), ("Bristle Boar", 3)])
    camp("wolf_copse", X0 + 40, Y0 + 270, 40, 40, [("Meadow Wolf", 4), ("Meadow Wolf", 3), ("Grey Alpha", 1)], "tree", 0.08)
    camp("shard_fields", X0 + 320, Y0 + 300, 40, 40, [("Field Shardling", 4), ("Field Shardling", 3)], "boulder", 0.03)
    camp("bandit_road", X0 + 330, Y0 + 180, 40, 40, [("Road Bandit", 4), ("Road Bandit", 3), ("Bandit Captain", 1)])
    camp("thornsnap_hollow", X0 + 140, Y0 + 140, 40, 40, [("Thornsnap", 4), ("Bristle Boar", 3)], "bush", 0.08)
    camp("old_quarry", X0 + 220, Y0 + 130, 40, 35, [("Ruin Sentinel", 3), ("Ruin Archer", 3), ("Field Shardling", 2)], "boulder", 0.05)

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

    # stair to floor 2: linked to Floor 2's landing by tools/mapgen.py (link_floors)
    m.points["stair_floor2_src"] = (bx + 15, by + 1, bz)

    # ------------------------------------------------ PvP zone tiers (DESIGN.md 6.3). Default everywhere: Open.
    m.zone("open", X0, Y0, SIZE, SIZE)
    m.zone("guarded", tx - 60, ty - 40, tw + 120, th + 90, 7)       # roads and fields around Hearthgate + starter fields
    m.zone("guarded", mx - 20, my - 20, 90, 80, 7)                   # around Millcross
    m.zone("contested", ax - 5, ay - 5, 54, 54, 7)                   # the Old Watchtower approach and outer layer
    m.zone("deadzone", ax + 12, ay + 12, 20, 20, 7)                  # the packed inner room
    m.zone("deadzone", cx, cy, 44, 44, 8)                            # the cliff caves below
    m.zone("bossroom", px, py, 24, 20, 7)                            # the Pass arena
    m.zone("bossroom", bx, by, 30, 24, 4)                            # the Axe-Lord's room
    m.zone("town", tx, ty, tw, th, 7)
    m.zone("town", mx, my, 50, 40, 7)

    # ------------------------------------------------ Floor 1 secrets (DESIGN.md 8.1). Trigger tiles only; no markers.
    def secret(sid, x, y, z=Z):
        if (x, y, z) not in m.ground:
            raise ValueError(f"secret {sid} has no ground at {(x, y, z)}")
        m.clear_items(x, y, z)  # trigger tiles must be walkable
        m.points["secret_" + sid] = (x, y, z)
    secret("s1", tx + 6, ty + 71)                       # beside the drain grate
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
    m.teleport((ux + 2, uy + 2, uz), (tx + 7, ty + 72, Z), "underkeep_exit")
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
