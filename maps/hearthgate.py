"""Hearthgate v4 (docs/design/hearthgate_v4_plan.md): builds the walled city from the tile plan in maps/hearthgate_plan.py.

Jay, 2026-11-26: "full redesign of the towns layout" ... "im worried about it being fun and functional." A loose nod
to a big round starting plaza; names and shapes are our own.

An eight-sided wall, a great round plaza with the Hearthstone in the open air at its centre, the Hearth (depot, bank,
chapel, gallery, tower) on the plaza's north side, every shop at an avenue's mouth facing the plaza, the Crown Quarter
north-east, Spire Manor in walled grounds south-east, and three kinds of neighbourhood. Called from
maps/layout_floor1.py; uses its own random numbers, so changing the town never shifts the scenery of the rest of the map.
"""
import random

import scenery as S
import dungeon as DG
import hearthgate_plan as P

MARBLE, FLAGSTONE, BLACK_MARBLE, WOOD, COBBLE, DIRT = 409, 416, 410, 408, 870, 103
MARBLE_PILLAR, HERO_STATUE, ANGEL_STATUE = 2153, 2027, 2031
BENCH, LAMP_POST, TREE = 2370, 8660, 3619
POTS = (316, 321)


def build(m, tx, ty, Z, claim, hid=1):
    """Lays the whole town with its top-left corner at (tx, ty). Returns the next free house id."""
    rng = random.Random(2611)                 # the town's own random numbers (m.pick and the helpers use m.rng too)
    main_rng, m.rng = m.rng, rng

    def R(x, y):
        return tx + x, ty + y

    def paint(x, y, w, h, gid):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                m.ground[(tx + xx, ty + yy, Z)] = gid

    def free(x, y, z=Z):
        p = (tx + x, ty + y, z)
        return p in m.ground and not m.items.get(p)

    def lamps(points):
        for px, py in points:
            if free(px, py):
                S.lamp(m, *R(px, py), Z)

    streets = {(x, y) for (r, _g) in P.STREETS.values() for x in range(r[0], r[0] + r[2]) for y in range(r[1], r[1] + r[3])}

    def on_path(x, y):
        """Streets, the avenues' lines across the plaza and the Hearthstone's own square stay clear."""
        return ((x, y) in streets or (55 <= x <= 58 and 33 <= y <= 66) or (40 <= x <= 73 and 48 <= y <= 50))

    # ---------------------------------------------------------------- ground, the eight-sided wall, the safe zone
    W, H = P.W, P.H
    for y in range(H):
        for x in range(W):
            p = (tx + x, ty + y, Z)
            m.clear_items(*p)
            m.ground[p] = COBBLE if P.inside_wall(x, y) else m.pick("grass")
    wall = P.wall_tiles()
    gates = {t for ts in P.GATES.values() for t in ts}
    m.autowall([R(x, y) for (x, y) in wall if (x, y) not in gates], Z, "pale")
    for y in range(H):
        for x in range(W):
            if P.inside_wall(x, y) and (x, y) not in wall:
                m.flag(tx + x, ty + y, 1, 1, Z, 0x0001)          # the whole town is a safe zone (DESIGN 6.2)
    for (x, y) in gates:
        m.flag(tx + x, ty + y, 1, 1, Z, 0x0001)
    for _n, (r, gid) in P.STREETS.items():
        paint(*r, gid)

    # ---------------------------------------------------------------- Hearth Plaza
    cx, cy = P.PLAZA_C
    for y in range(30, 68):
        for x in range(38, 76):
            d2 = (x - cx) ** 2 + (y - cy) ** 2
            if d2 <= P.PLAZA_R ** 2:
                m.ground[(tx + x, ty + y, Z)] = FLAGSTONE if d2 > (P.PLAZA_R - 1.3) ** 2 else MARBLE
    hx_, hy_ = P.HEARTHSTONE
    for a in (-1, 0, 1):                                         # the Hearthstone: a black marble square
        for b in (-1, 0, 1):
            m.ground[(tx + hx_ + a, ty + hy_ + b, Z)] = BLACK_MARBLE
    for a, b in ((-3, 0), (3, 0), (0, -3), (0, 3), (-2, -2), (2, -2), (-2, 2), (2, 2)):   # a ring of flagstone round it
        m.ground[(tx + hx_ + a, ty + hy_ + b, Z)] = FLAGSTONE
    temple = R(hx_, hy_) + (Z,)
    m.towns.append((1, "Hearthgate", temple))
    m.points["temple_hearthgate"] = temple

    # ---------------------------------------------------------------- the Hearth (plan: HEARTH)
    x0, y0, hw, hh = P.HEARTH
    claim("the hearth", *R(x0, y0), hw, hh)
    m.building(*R(x0, y0), hw, hh, Z, floor="marble", door_side=None, style="white", doors=False,
               extra_gaps=[R(*a) for a in P.HEARTH_ARCHES])
    m.storey(*R(x0, y0), hw, hh, Z - 1, floor="wood", style="white")           # the Trading Gallery
    m.storey(*R(*P.HEARTH_TOWER[:2]), *P.HEARTH_TOWER[2:], Z - 2, floor="marble", style="white")   # the Hall of Climbers
    paint(43, 13, 12, 9, WOOD)                                                    # north-west depot wing
    paint(59, 25, 12, 9, WOOD)                                                    # south-east depot wing
    paint(43, 25, 12, 9, BLACK_MARBLE)                                            # the bank
    for a in P.HEARTH_ARCHES:
        m.ground[(tx + a[0], ty + a[1], Z)] = MARBLE
    S.carpet(m, *R(56, 12), 2, 23, Z, 2576)                                       # the red cross of carpet
    S.carpet(m, *R(43, 23), 28, 1, Z, 2576)
    for px, py in ((54, 21), (59, 21), (54, 25), (59, 25)):
        S.prop(m, *R(px, py), Z, MARBLE_PILLAR)
    for px, py in ((54, 33), (59, 33), (54, 13), (59, 13)):
        S.prop(m, *R(px, py), Z, DG.COAL_BASIN)
    # depot (Jay, 2026-11-12: "just use what tibia uses for their dp's"): two wings of ten booths, two-deep dividers
    for bx, by, face in P.DEPOT_BOOTHS:
        m.depot_booths(*R(bx, by), 5, Z, 1, face=face)
    m.put(*R(59, 31), Z, 3501)
    m.put(*R(54, 15), Z, 3501)
    m.sign(*R(59, 27), Z, "Depot. Your lockers are shared by every depot in the tower. Open the market from any locker. "
           "More booths in the north-west wing and upstairs.")
    m.points["depot_hearthgate"] = R(*P.HEARTH_POINTS["depot_hearthgate"]) + (Z,)
    # the bank and exchange, just inside the front archway: one counter, three keepers behind it
    bx, by, bn = P.BANK_COUNTER
    S.counter(m, *R(bx, by), bn, Z, vertical=True)
    for npc, pos in P.BANK_NPCS.items():
        m.npcs.append((npc, R(*pos) + (Z,)))
    for py, pid in ((26, 2472), (28, 2480), (30, 2472), (32, 2480)):
        S.prop(m, *R(44, py), Z, pid)
    S.carpet(m, *R(46, 27), 3, 5, Z, 5572)
    m.sign(*R(54, 27), Z, "Bank and Exchange. Banker Tolliver keeps your gold and your account vault; Trader Osric buys "
           "your loot; Broker Nell explains the market.")
    for k in ("hearth_bank", "hearth_trader", "trade_hall", "shop_bank"):
        m.points[k] = R(*P.HEARTH_POINTS[k]) + (Z,)
    # the chapel
    m.put(*R(65, 13), Z, 3515)                                                    # the altar
    S.carpet(m, *R(64, 14), 3, 6, Z, 2576)
    m.npcs.append(("Priest Odran", R(*P.PRIEST) + (Z,)))
    for px, py in ((61, 15), (68, 15), (68, 18)):
        S.prop(m, *R(px, py), Z, BENCH)
    m.sign(*R(60, 21), Z, "The Hearth. Temple, depot, bank and market under one roof. The trading gallery is upstairs.")
    DG.hang(m, *R(x0, y0), hw, hh, Z, every=5, offset=3)
    # level 2: the Trading Gallery
    for bx, by, face in P.GALLERY_BOOTHS:
        m.depot_booths(*R(bx, by), 5, Z - 1, 1, face=face)
    for px, py in ((45, 17), (61, 17), (45, 29), (61, 29)):
        S.counter(m, *R(px, py), 8, Z - 1)                                        # trade tables: stand either side and deal
    for px, py in ((48, 32), (64, 32)):
        S.prop(m, *R(px, py), Z - 1, BENCH)
    m.sign(*R(56, 15), Z - 1, "The Trading Gallery. Meet, haggle, and trade face to face. Lockers along the north wall.")
    DG.hang(m, *R(x0, y0), hw, hh, Z - 1, every=5, offset=4)
    # level 3: the Hall of Climbers
    S.prop(m, *R(52, 20), Z - 2, HERO_STATUE)
    S.prop(m, *R(61, 20), Z - 2, ANGEL_STATUE)
    S.prop(m, *R(51, 26), Z - 2, MARBLE_PILLAR)
    S.prop(m, *R(57, 26), Z - 2, MARBLE_PILLAR)
    S.carpet(m, *R(53, 22), 8, 3, Z - 2, 2576)
    m.sign(*R(56, 19), Z - 2, "The Hall of Climbers. Look for a party here before you climb. Say !top for the climbers.")
    DG.hang(m, *R(*P.HEARTH_TOWER[:2]), *P.HEARTH_TOWER[2:], Z - 2, every=4, offset=3)
    for name, (sx, sy, sz) in P.HEARTH_STAIRS.items():
        m.stairs(*R(sx, sy), sz, floor="wood" if sz == Z else "marble", name=name)
    m.roof(*R(*P.HEARTH_TOWER[:2]), *P.HEARTH_TOWER[2:], Z - 2, "red")           # the tower's own roof

    # ---------------------------------------------------------------- shops: two rooms in each building, doors on the plaza
    PROPS = {"general": (2519, 2523, 116, 117), "weapons": (3458, 116, 118, 2472), "armor": (2429, 2429, 2480, 2472),
             "fletcher": (2519, 116, 2523, 116), "alchemist": (2472, 2472, 2480, 2472), "runes": (2480, 2480, 2472, 2480),
             "tailor": (2429, 2429, 2480, 2429), "post": (2523, 3501, 3501, 2523), "plain": (2519, 2523, 116, 2429)}

    def shop_room(name, npc, kind, room, door, side):
        rx, ry, rw, rh = room
        dx, dy = door
        step = {"e": -1, "w": 1}[side]                    # into the room
        kx = dx + 4 * step
        m.npcs.append((npc, R(kx, dy) + (Z,)))
        m.points["shop_" + name.lower().replace("'", "").replace(" ", "_")] = R(dx + 2 * step, dy) + (Z,)
        if kind != "post":
            S.counter(m, *R(dx + 3 * step, ry), rh, Z, vertical=True)
        back = rx if side == "e" else rx + rw - 1
        spots = [(back, yy) for yy in range(ry, ry + rh) if yy != dy][:2] + [(back - step, ry), (back - step, ry + rh - 1)]
        for (px, py), pid in zip(spots, PROPS[kind]):
            if free(px, py) and (px, py) != (kx, dy):
                S.prop(m, *R(px, py), Z, pid)
        m.sign(*R(dx + step, dy - 1 if free(dx + step, dy - 1) else dy + 1), Z, name)    # just inside the door

    for blk in P.SHOP_BLOCKS:
        bx0, by0, bw, bh = blk["rect"]
        doors = [r[4] for r in blk["rooms"]]
        claim(blk["rooms"][0][0], *R(bx0, by0), bw, bh)
        side = blk["rooms"][0][5]
        m.building(*R(bx0, by0), bw, bh, Z, floor="wood", door_side=side, style=blk["style"], doors=True,
                   door=R(*doors[0]), extra_gaps=[R(*d) for d in doors[1:]])
        for d in doors[1:]:
            m.ground[(tx + d[0], ty + d[1], Z)] = WOOD
            if side == "w":
                m.ground[(tx + d[0], ty + d[1] - 1, Z)] = WOOD
        axis, at = blk["split"]
        if axis == "y":
            m.autowall([R(x, at) for x in range(bx0 + 1, bx0 + bw - 1)], Z, blk["style"])
        if blk["tall"]:                                    # a second storey on some, so the roofs vary in height
            m.storey(*R(bx0, by0), bw, bh, Z - 1, floor="wood", style=blk["style"])
        for room in blk["rooms"]:
            shop_room(*room)

    # the inn, with rooms upstairs
    ix, iy, iw, ih = P.INN["rect"]
    claim("inn", *R(ix, iy), iw, ih)
    m.building(*R(ix, iy), iw, ih, Z, floor="wood", door_side="e", style=P.INN["style"], doors=True, door=R(*P.INN["door"]))
    S.counter(m, *R(49, 66), 4, Z, vertical=True)                                  # the bar
    m.npcs.append(("Innkeeper Roan", R(47, 67) + (Z,)))
    S.prop(m, *R(44, 66), Z, 2519)
    S.prop(m, *R(44, 67), Z, 2523)
    S.prop(m, *R(44, 68), Z, 2523)
    for px, py in ((45, 72), (49, 72), (45, 75), (49, 75)):                         # tables and stools
        S.prop(m, *R(px, py), Z, 2322)
        S.prop(m, *R(px + 1, py), Z, 2358)
    m.sign(*R(52, 66), Z, "The Lantern & Lark. Food, drink, and rooms upstairs. Innkeeper Roan.")
    m.storey(*R(ix, iy), iw, ih, Z - 1, floor="wood", style=P.INN["style"])
    m.stairs(*R(52, 75), Z, name="hearthgate_inn")
    m.autowall([R(48, y) for y in range(66, 77) if y not in (70, 71, 72)], Z - 1, P.INN["style"])
    for px, py, pid in ((44, 66, 2487), (46, 66, 2487), (44, 74, 2487), (46, 74, 2322), (50, 66, 2487), (52, 68, 2322)):
        S.prop(m, *R(px, py), Z - 1, pid)

    # the guardhouse beside the north gate: Captain Dorrow stands outside
    g = P.GUARDHOUSE
    claim("guardhouse", *R(*g["rect"][:2]), *g["rect"][2:])
    m.building(*R(*g["rect"][:2]), *g["rect"][2:], Z, floor="wood", door_side="w", style="stone", doors=True, door=R(*g["door"]))
    for px, py, pid in ((62, 3, 2487), (64, 3, 2487), (66, 3, 2322), (67, 3, 2358), (67, 7, 2472), (62, 8, 2472)):
        S.prop(m, *R(px, py), Z, pid)
    m.sign(*R(61, 4), Z, "Guardhouse. Captain Dorrow keeps the north gate.")
    m.npcs.append(("Captain Dorrow", R(*g["captain"]) + (Z,)))

    # ---------------------------------------------------------------- the Crown Quarter
    a = P.ASCENDANCY
    claim("ascendancy", *R(*a["rect"][:2]), *a["rect"][2:])
    m.building(*R(*a["rect"][:2]), *a["rect"][2:], Z, floor="marble", door_side="w", style="sand", doors=True, door=R(*a["door"]))
    S.carpet(m, *R(75, 26), 3, 1, Z, 2576)
    for px, py in ((76, 23), (83, 23), (76, 29), (83, 29)):
        S.prop(m, *R(px, py), Z, MARBLE_PILLAR)
    S.prop(m, *R(84, 26), Z, ANGEL_STATUE)
    m.sign(*R(75, 24), Z, "The Ascendancy. Climbers of level 20 and above may be promoted here.")
    m.npcs.append(("Ascendant Veyra", R(*a["npc"]) + (Z,)))
    hh_ = P.HUNTERS_HALL
    hx, hy, hw2, hh2 = hh_["rect"]
    claim("Hunters' Hall", *R(hx, hy), hw2, hh2)
    m.building(*R(hx, hy), hw2, hh2, Z, floor="wood", door_side="w", style="stone", doors=True, door=R(*hh_["door"]))
    m.points["shop_hunters_hall"] = R(77, 35) + (Z,)
    S.carpet(m, *R(75, 35), 6, 1, Z, 2576)
    S.prop(m, *R(75, 37), Z, 2033)
    S.prop(m, *R(84, 37), Z, 2030)
    S.prop(m, *R(80, 32), Z, 2322)
    S.prop(m, *R(81, 32), Z, 2358)
    m.sign(*R(75, 33), Z, "Hunters' Hall. Hunting tasks, bounties and the trophy loft.")
    m.npcs.append(("Taskmaster Rhen", R(78, 33) + (Z,)))
    m.npcs.append(("Bounty Warden Cass", R(82, 34) + (Z,)))
    m.npcs.append(("Hunter Brannoch", R(84, 35) + (Z,)))
    m.storey(*R(hx, hy), hw2, hh2, Z - 1, floor="wood", style="stone")
    m.ladder(*R(*hh_["ladder"]), Z, name="hunters_hall")
    for px, py, pid in ((76, 32, 2519), (77, 32, 2523), (76, 36, 2472), (81, 36, 2429), (79, 34, 2322)):
        S.prop(m, *R(px, py), Z - 1, pid)
    gh = P.GUILD_HALL
    gx, gy, gw, gh2 = gh["rect"]
    claim("guildhall", *R(gx, gy), gw, gh2)
    m.building(*R(gx, gy), gw, gh2, Z, floor="wood", door_side="s", style="timber", doors=True, door=R(*gh["door"]))
    S.carpet(m, *R(86, 42), 6, 3, Z, 5572)
    S.counter(m, *R(91, 41), 3, Z)
    S.prop(m, *R(85, 40), Z, 2322)
    S.prop(m, *R(86, 40), Z, 2358)
    m.sign(*R(89, 46), Z, "Guild Hall. Found a guild, read the recruiting board; Banker Ansel keeps the guild bank.")
    m.npcs.append(("Guildwarden Sela", R(88, 43) + (Z,)))
    m.npcs.append(("Banker Ansel", R(92, 40) + (Z,)))
    m.storey(*R(gx, gy), gw, gh2, Z - 1, floor="wood", style="timber")
    m.stairs(*R(*gh["stairs"]), Z, name="guild_hall")
    S.carpet(m, *R(86, 42), 7, 3, Z - 1, 5572)
    for px in (86, 88, 90, 92):
        S.prop(m, *R(px, 43), Z - 1, 2322)
        S.prop(m, *R(px, 44), Z - 1, 2358)
    ty_ = P.TRAINING_YARD
    yx, yy, yw, yh = ty_["rect"]
    claim("training yard", *R(yx, yy), yw, yh)
    paint(yx, yy, yw, yh, DIRT)
    m.walls(*R(yx, yy), yw, yh, Z, gaps={R(*t) for t in ty_["gaps"]}, style="timber")
    for i, sid in enumerate(range(16198, 16203)):        # offline training statues: log out and train that skill slowly
        m.put(*R(yx + 1 + i * 2, yy + 2), Z, sid)
    m.sign(*R(yx + 9, yy + 5), Z, "Training Yard. Use a statue to log out and train that skill slowly while you're away.")
    for px in (2, 5, 8):                                  # practice posts
        S.prop(m, *R(yx + px, yy + 7), Z, 2263)
    m.points["training_yard"] = R(*ty_["point"]) + (Z,)

    # ---------------------------------------------------------------- Spire Manor in its walled grounds, Spire Gardens
    gx0, gy0, gw0, gh0 = P.MANOR_GROUNDS["rect"]
    claim("manor grounds", *R(gx0, gy0), gw0, gh0)
    for y in range(gy0, gy0 + gh0):
        for x in range(gx0, gx0 + gw0):
            m.ground[(tx + x, ty + y, Z)] = m.pick("grass")
    m.walls(*R(gx0, gy0), gw0, gh0, Z, gaps={R(*t) for t in P.MANOR_GROUNDS["gate"]}, style="white")
    for t in P.MANOR_GROUNDS["gate"]:
        m.ground[(tx + t[0], ty + t[1], Z)] = MARBLE
    import manor                                         # the whole house is one movable piece (maps/manor.py)
    mx0, my0 = R(*P.MANOR_AT)
    manor.build(m, mx0, my0, Z)
    paint(93, 64, 3, 3, MARBLE)                          # the forecourt: gate to door
    paint(88, 64, 13, 2, MARBLE)
    lamps([(89, 64), (99, 64)])
    for px, py in ((91, 65), (97, 65)):
        S.prop(m, *R(px, py), Z, POTS[px % 2])
    for px, py in ((81, 64), (106, 64), (81, 83), (106, 83), (81, 74), (106, 74)):   # the grounds: trees and flowers round the house
        S.prop(m, *R(px, py), Z, rng.choice(S.TREES_BROAD[:3]))
    for y in range(gy0 + 1, gy0 + gh0 - 1):
        for x in range(gx0 + 1, gx0 + gw0 - 1):
            if (x <= 82 or x >= 105 or y >= 83) and free(x, y) and m.ground[(tx + x, ty + y, Z)] in S.GRASS_IDS \
                    and (x + 2 * y) % 5 == 0:
                S.prop(m, *R(x, y), Z, rng.choice(S.FLOWERS))
    sgx, sgy, sgw, sgh = P.SPIRE_GARDENS                 # a public garden on the way to the manor's gate
    paint(sgx, sgy, sgw, sgh, 4526)
    paint(93, 51, 3, 12, MARBLE)                         # Manor Walk
    S.pond(m, *R(101, 56), 3, 2, Z, ring="mud")
    for px, py in ((86, 53), (90, 59), (98, 53), (107, 59), (88, 56), (106, 53)):
        if free(px, py):
            S.prop(m, *R(px, py), Z, TREE)
    for px, py in ((92, 55), (96, 57), (101, 59)):
        if free(px, py):
            S.prop(m, *R(px, py), Z, BENCH)
    S.sprinkle(m, *R(sgx, sgy), sgw, sgh, Z, S.FLOWERS, 0.1, seed=62)
    m.sign(*R(92, 52), Z, "Spire Gardens. Manor Walk leads to the gate of Spire Manor.")

    # ---------------------------------------------------------------- yards and green places
    c = P.COACH_YARD
    cx0, cy0, cw, ch = c["rect"]
    claim("coach yard", *R(cx0, cy0), cw, ch)
    paint(cx0, cy0, cw, ch, DIRT)
    m.walls(*R(cx0, cy0), cw, ch, Z, gaps={R(*c["gap"])}, style="timber")
    m.sign(*R(61, 85), Z, "Carriage Station. Coachman Ferro drives to Millcross and back.")
    m.npcs.append(("Coachman Ferro", R(*c["ferro"]) + (Z,)))
    m.points["carriage_hearthgate"] = R(*c["carriage"]) + (Z,)
    for px, py, pid in ((61, 83, 2519), (68, 83, 2523), (61, 91, 2472), (67, 91, 2519)):
        S.prop(m, *R(px, py), Z, pid)
    for px in (63, 66):
        S.prop(m, *R(px, 90), Z, 2264)                   # hitching posts
    m.put(*R(67, 85), Z, 7906)                           # the covered wagon (two tiles)

    ox, oy, ow, oh = P.OLD_WELL                          # Old Well Yard: overgrown, with the Underkeep grate
    paint(ox, oy, ow, oh, 4526)
    for px, py in ((ox, oy), (ox + ow - 1, oy), (ox, oy + oh - 1), (ox + ow - 1, oy + oh - 1)):
        S.prop(m, *R(px, py), Z, 2264)
    gr = P.GRATE
    keep = {(gr[0] + a, gr[1] + b) for a in (-1, 0, 1, 2) for b in (0, 1, 2)}
    S.sprinkle(m, *R(ox, oy), ow, oh, Z, S.BUSHES + S.FERNS, 0.3, seed=64)
    for (px, py) in keep:
        m.clear_items(*R(px, py), Z)
    grate = R(*gr) + (Z,)                                # Underkeep grate (the Underkeep's exit lands at (5, 68))
    m.put(*grate, 435)
    m.sign(*R(gr[0] + 2, gr[1]), Z, "An old drain grate. Something echoes far below.")
    m.points["underkeep_grate"] = grate

    gx1, gy1, gw1, gh1 = P.GREEN                         # Hearthgate Green: a park with a pond
    paint(gx1, gy1, gw1, gh1, 4526)
    paint(gx1, 23, gw1, 1, COBBLE)
    paint(20, gy1, 1, gh1, COBBLE)
    S.pond(m, *R(25, 29), 2, 2, Z, ring="mud")
    for px, py in ((17, 21), (23, 21), (17, 26), (22, 31), (15, 30), (27, 18)):
        S.prop(m, *R(px, py), Z, BENCH)
    for px, py in ((14, 15), (16, 17), (13, 19), (13, 27), (18, 31), (14, 32), (28, 15), (24, 15)):
        S.prop(m, *R(px, py), Z, rng.choice(S.TREES_BROAD[:3]))
    S.sprinkle(m, *R(gx1, gy1), gw1, gh1, Z, S.FLOWERS, 0.06, seed=63)
    lamps([(19, 12), (21, 34), (12, 22), (29, 24)])
    px0, py0, pw, ph = P.POCKET_GARDEN
    paint(px0, py0, pw, ph, 4526)
    S.prop(m, *R(50, 87), Z, BENCH)
    S.prop(m, *R(52, 85), Z, TREE)
    S.prop(m, *R(52, 90), Z, TREE)

    # ---------------------------------------------------------------- 30 houses (maps/house_plans.py: no two neighbours alike)
    import house_plans as HP
    for street, rent, lots in P.HOUSES:
        for k, (lx, ly, lw, lh, side, storeys, style) in enumerate(lots):
            hx0, hy0 = R(lx, ly)
            claim(f"house {hid}", hx0, hy0, lw, lh)
            fx, fy, fw, fh, plan = HP.footprint(hid, hx0, hy0, lw, lh, side, allow_shrink=storeys == 1)
            m.house_building(hid, f"{street} {k + 1}", fx, fy, fw, fh, Z, town=1, rent=HP.rent_for(rent, fw, fh, plan, storeys),
                             door_side=side, style=style, floor="marble" if style == "white" else "wood", storeys=storeys)
            HP.fit(m, hid, fx, fy, fw, fh, Z, side, style, plan, storeys)
            if (fw, fh) != (lw, lh):
                HP.yard(m, (hx0, hy0, lw, lh), (fx, fy, fw, fh), Z, S, rng)
            hid += 1

    # ---------------------------------------------------------------- the plaza: Monument, Vesper, Beacon, stalls, benches
    mx, my = P.MONUMENT
    S.prop(m, *R(mx, my), Z, HERO_STATUE)
    m.sign(*R(mx + 1, my), Z, "The Monument. Names of those who opened the tower's floors are carved here. Say !top for the "
           "climbers, !memorial for the fallen.")
    m.points["monument"] = R(mx, my + 1) + (Z,)
    ax, ay = P.ARENA_STATUE                               # the Arena MVP's statue (scripts/spirebound/arena.lua names it)
    S.prop(m, *R(ax, ay), Z, 2025)
    m.points["arena_mvp_statue"] = R(ax, ay) + (Z,)
    m.sign(*R(ax + 1, ay), Z, "The Arena Champion. The best fighter of the last arena event stands here until the next one. "
           "Say !arena for the schedule.")
    for i, (bx_, by_) in enumerate(P.BEACON_BOWLS):       # the Floor Beacon (scripts/spirebound/beacons.lua)
        S.prop(m, *R(bx_, by_), Z, 30964)                 # empty fire bowl (lit: 30965)
        m.points[f"beacon_1_{i + 1}"] = R(bx_, by_) + (Z,)
    m.sign(*R(65, 44), Z, "The Floor Beacon. Bring a Beacon Ember to a fire bowl: each fire gives everyone hunting on this "
           "floor +5% experience and loot for an hour. Say !beacon to see what burns.")
    m.npcs.append(("Vesper", R(*P.VESPER) + (Z,)))
    m.put(*R(*P.FOUNTAIN), Z, 1922)                       # the fountain
    for k, (sx_, sy_) in enumerate(P.STALLS):             # free trading stalls
        S.counter(m, *R(sx_, sy_), 3, Z)
        S.prop(m, *R(sx_ + 1, sy_ - 1 if sy_ < 49 else sy_ + 1), Z, (2519, 116, 2523, 117, 2519, 116)[k])
    for (px, py) in ((52, 41), (61, 41), (47, 49 - 3), (66, 52), (52, 57), (61, 57)):     # benches looking at the Hearthstone
        if free(px, py) and not on_path(px, py):
            S.prop(m, *R(px, py), Z, BENCH)
    for (px, py) in ((45, 38), (68, 38), (45, 60), (68, 60)):                           # a tree in a bed at four corners
        for a in (0, 1):
            for b in (0, 1):
                m.ground[(tx + px + a, ty + py + b, Z)] = 4526
        S.prop(m, *R(px, py), Z, TREE)
        S.prop(m, *R(px + 1, py + 1), Z, rng.choice(S.FLOWERS))
    m.sign(*R(53, 52), Z, "Hearthgate. The Hearth (depot, bank, temple) is the great hall north. Shops face this plaza "
           "where the avenues leave it: arms and stores west, runes, arrows, potions and cloth east, the inn, housewright "
           "and post south. Crown Quarter north-east, Spire Manor south-east. Say !guide for your first steps.")
    m.sign(*R(60, 46), Z, "Hearth Plaza. Stalls are free: stand behind one and trade with other climbers. "
           "For lasting offers use the market at any depot locker.")
    m.put(*R(*P.NOTICE_BOARD), Z, 2597)                    # the notice board (live news, scripts/spirebound/monument.lua)
    m.points["hearth_notice_board"] = R(*P.NOTICE_BOARD) + (Z,)
    rim = []                                               # lamps round the plaza's rim, clear of the avenues
    import math
    for i in range(16):
        ang = (i + 0.5) * math.pi / 8
        px, py = int(round(cx + 15.2 * math.cos(ang))), int(round(cy + 15.2 * math.sin(ang)))
        if py <= 35 or on_path(px, py) or not free(px, py):
            continue
        rim.append((px, py))
    lamps(rim)

    # ---------------------------------------------------------------- street lamps along the avenues and high roads
    lamps([(54, 3), (59, 8), (54, 9), (54, 70), (59, 80), (54, 90), (59, 92),
           (4, 47), (14, 47), (26, 47), (39, 51), (74, 47), (84, 51), (97, 47), (108, 51),
           (39, 12), (74, 12), (9, 12), (20, 12), (96, 12), (30, 58), (11, 80), (30, 80), (59, 74)])
    import hearthgate_dress                               # the open cobble, the gates and the doors dressed
    hearthgate_dress.dress(m, tx, ty, W, H, Z, rng, streets=streets | {(x, y) for x in range(55, 59) for y in range(33, 67)})
    m.rng = main_rng
    return hid
