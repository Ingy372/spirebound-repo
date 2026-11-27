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
MONUMENT = 2028                 # Tibia's "monument", drawn with ours in the client (tools/install_effects.py)
BENCH, LAMP_POST, TREE = 2370, 8660, 3619
POTS = (316, 321)


LILIES = (3669, 3670, 3671, 3672)
REED = 3688


def garden_pond(m, R, Z, c, rx, ry, pier, rng):
    """A town pond (Jay, 2026-11-27: the old one "looks funny and needs some detail work"): a smooth oval of water on
    the grass, no mud ring, so Map.edge_grounds draws a proper shoreline; lilies on the water, reeds and stones on the
    shore, and a short wooden pier."""
    cx, cy = c
    water = []
    for y in range(cy - ry - 1, cy + ry + 2):
        for x in range(cx - rx - 1, cx + rx + 2):
            if ((x - cx) / (rx + 0.5)) ** 2 + ((y - cy) / (ry + 0.5)) ** 2 <= 1.0:
                p = R(x, y) + (Z,)
                m.clear_items(*p)
                m.ground[p] = m.pick("water")
                water.append((x, y))
    if pier:
        S.bridge(m, *R(pier[0], pier[1]), pier[2], pier[3], Z)
    ws = set(water)
    inner = [(x, y) for (x, y) in water if all((x + a, y + b) in ws for a in (-1, 0, 1) for b in (-1, 0, 1))
             and m.ground[R(x, y) + (Z,)] != 408]
    for (x, y) in rng.sample(inner, min(len(inner), max(2, len(inner) // 4))):
        m.put(*R(x, y), Z, rng.choice(LILIES))
    shore = sorted({(x + a, y + b) for (x, y) in water for a in (-1, 0, 1) for b in (-1, 0, 1)} - ws)
    rng.shuffle(shore)
    for k, (x, y) in enumerate(shore[:max(4, len(shore) // 5)]):
        p = R(x, y) + (Z,)
        if m.ground.get(p) in S.GRASS_IDS and not m.items.get(p) and not (pier and abs(x - pier[0]) <= 1):
            m.put(*p, REED if k % 3 else rng.choice(S.STONES))


HEARTH_WALL = "stone"            # the Hearth's round wall, both levels


def hearth_roof(m, R, rz, tiles, style="red"):
    """A roof on level rz over a round hall (Map.roof does rectangles): roof ground on every tile, edge pieces on the
    empty tiles round it, picked by which sides the roof is on (the same rules as Map.roof)."""
    from mapgen import ROOFS
    r = ROOFS[style]
    world = {R(x, y) for (x, y) in tiles}
    for (x, y) in world:
        if (x, y, rz) not in m.ground:
            m.ground[(x, y, rz)] = r["g"]
            m.flags[(x, y, rz)] = m.flags.get((x, y, rz + 2), 0)
    around = {(x + a, y + b) for (x, y) in world for a in (-1, 0, 1) for b in (-1, 0, 1)} - world
    for (x, y) in around:
        if (x, y, rz) in m.ground:
            continue
        n, s_, e, w_ = (x, y - 1) in world, (x, y + 1) in world, (x + 1, y) in world, (x - 1, y) in world
        key = ("N" if n else "S" if s_ else "") + ("E" if e else "W" if w_ else "")
        if len(key) == 2:
            key = key[0]
        if not key:
            key = ("N" if (x, y - 1) in world or (x - 1, y - 1) in world or (x + 1, y - 1) in world else "S") + \
                  ("W" if (x - 1, y - 1) in world or (x - 1, y + 1) in world else "E")
        m.put(x, y, rz, r[key])


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
    # v4.1 (Jay: "the town is grey, brighten it up some"): grass between the buildings, paved streets and plaza
    W, H = P.W, P.H
    for y in range(H):
        for x in range(W):
            p = (tx + x, ty + y, Z)
            m.clear_items(*p)
            m.ground[p] = m.pick("grass")
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
                m.ground[(tx + x, ty + y, Z)] = FLAGSTONE if d2 > (P.HEARTH_R - 0.5) ** 2 else MARBLE

    # ---------------------------------------------------------------- the Hearth: the round hall at the plaza's centre
    # (Jay, 2026-11-27: "make the depot (middle of town) a building. make it circular as you can to hold the shape that
    # is currently there. this will be the main hub of the city", then "flip the floor plan. i think the actual bank
    # booths ... should be on the second floor"). Ground floor: the Hearthstone, the Monument, the Floor Beacon, the
    # Arena Champion and the stalls. Second floor: the depot lockers and the bank.
    hx_, hy_ = P.HEARTHSTONE
    hall, ring = P.hearth_tiles()
    claim("the hearth", *R(*P.HEARTH_COURT[:2]), *P.HEARTH_COURT[2:])
    for (x, y) in hall:                    # the wall stands on the plaza's paving, so no pale floor pokes out past it
        m.ground[(tx + x, ty + y, Z)] = FLAGSTONE if (x, y) in ring and not P.hearth_arch(x, y) else MARBLE
    # grey stone, not the low white marble: from above the white pieces read as pale floor slabs, so the ring looked
    # like messy ground (Jay, 2026-11-27: "the ground tiles need to be cleaned up around all of the depot area")
    m.autowall([R(x, y) for (x, y) in ring if not P.hearth_arch(x, y)], Z, HEARTH_WALL)
    for a in range(-2, 4):                                       # the Hearthstone: black marble framed in flagstone,
        for b in range(-2, 3):                                   # the braziers on the frame's corners
            edge = a in (-2, 3) or b in (-2, 2)
            m.ground[(tx + hx_ + a, ty + hy_ + b, Z)] = FLAGSTONE if edge else BLACK_MARBLE
    temple = R(hx_, hy_) + (Z,)
    m.towns.append((1, "Hearthgate", temple))
    m.points["temple_hearthgate"] = temple
    m.points["hearth_waypoint"] = R(*P.WAYPOINT) + (Z,)              # where a Floor 1 Waycrystal brings you
    for (px, py) in P.HEARTH_BRAZIERS:                            # four braziers round the Hearthstone: the hearth fire
        S.prop(m, *R(px, py), Z, DG.COAL_BASIN)
    for name, (sx, sy, sz) in P.HEARTH_STAIRS.items():
        m.stairs(*R(sx, sy), sz, floor="marble", name=name)
    mx, my = P.MONUMENT                                          # the Monument: the names of every floor's first clears
    S.prop(m, *R(mx, my), Z, MONUMENT)   # our own object (art/models/monument.py; Jay: "deserves to be its own custom object")
    for px in (mx - 2, mx + 3):
        S.prop(m, *R(px, my), Z, MARBLE_PILLAR)
    m.sign(*R(mx + 1, my), Z, "The Monument. The names of those who cleared each floor's boss are carved here. "
           "Use the statue to read them. Say !top for the climbers, !memorial for the fallen.")
    m.points["monument"] = R(mx, my + 1) + (Z,)
    for i, (bx_, by_) in enumerate(P.BEACON_BOWLS):       # the Floor Beacon (scripts/spirebound/beacons.lua)
        S.prop(m, *R(bx_, by_), Z, 30964)                 # empty fire bowl (lit: 30965)
        m.points[f"beacon_1_{i + 1}"] = R(bx_, by_) + (Z,)
    m.sign(*R(63, 44), Z, "The Floor Beacon. Bring a Beacon Ember to a fire bowl: each fire gives everyone hunting on "
           "this floor +5% experience and loot for an hour. Say !beacon to see what burns.")
    ax, ay = P.ARENA_STATUE                               # the Arena MVP's statue (scripts/spirebound/arena.lua names it)
    S.prop(m, *R(ax, ay), Z, 2025)
    m.points["arena_mvp_statue"] = R(ax, ay) + (Z,)
    m.sign(*R(ax + 1, ay), Z, "The Arena Champion. The best fighter of the last arena event stands here until the next "
           "one. Say !arena for the schedule.")
    m.put(*R(*P.NOTICE_BOARD), Z, 2597)                    # the notice board (live news, scripts/spirebound/monument.lua)
    m.points["hearth_notice_board"] = R(*P.NOTICE_BOARD) + (Z,)
    for k, (sx_, sy_) in enumerate(P.STALLS):             # free trading stalls
        S.counter(m, *R(sx_, sy_), 3, Z)
        S.prop(m, *R(sx_ + 1, sy_ - 1 if sy_ < 49 else sy_ + 1), Z, (2519, 116, 2523, 117)[k])
    for (px, py) in ((52, 46), (61, 46), (52, 52), (61, 52)):                           # benches round the Hearthstone
        S.prop(m, *R(px, py), Z, BENCH)
    for (px, py) in ((50, 57), (63, 57), (51, 43), (61, 39), (49, 61), (60, 61)):       # pillars and plants
        if free(px, py):
            S.prop(m, *R(px, py), Z, MARBLE_PILLAR if py in (57, 61) else POTS[px % 2])
    m.sign(*R(57, 46), Z, "The Hearth. Upstairs on both sides: your depot lockers (shared by every depot in the tower; "
           "open the market from any of them) and the bank. Stalls here are free: stand behind one and trade.")
    m.sign(*R(57, 52), Z, "Hearthgate. Shops face the plaza where the avenues leave the Hearth: arms and stores west, "
           "runes, arrows, potions and cloth east, the inn, housewright and post south. The Climbers' Temple north, "
           "the Crown Quarter north-east, Spire Manor south-east. Say !guide for your first steps.")
    # the second floor: the same round wall, a floor over it (one tile in from top and left, as storeys are), the
    # lockers and the bank; then a round roof
    up = {(x, y) for (x, y) in hall if (x - 1, y) in hall and (x, y - 1) in hall}
    for (x, y) in up:
        p = (tx + x, ty + y, Z - 1)
        if m.ground.get(p) is None:
            m.ground[p] = MARBLE
        m.flag(tx + x, ty + y, 1, 1, Z - 1, 0x0001)
    walls6 = ring | set(P.HEARTH_INNER_WALLS)                 # the round wall and the walls behind lockers and counters
    for (x, y) in walls6:
        m.ground.setdefault((tx + x, ty + y, Z - 1), MARBLE)
        m.clear_items(tx + x, ty + y, Z - 1)
    m.autowall([R(x, y) for (x, y) in walls6], Z - 1, HEARTH_WALL)
    for a in range(-2, 4):                                       # the same framed square over the Hearthstone
        for b in range(-2, 3):
            edge = a in (-2, 3) or b in (-2, 2)
            m.ground[(tx + hx_ + a, ty + hy_ + b, Z - 1)] = FLAGSTONE if edge else BLACK_MARBLE
    for (px, py) in P.HEARTH_BRAZIERS:
        S.prop(m, *R(px, py), Z - 1, DG.COAL_BASIN)
    # sixteen lockers facing the middle (Jay, 2026-11-12: "just use what tibia uses for their dp's")
    for bx, by, face in P.DEPOT_ROWS:
        m.depot_booths(*R(bx, by), 4, Z - 1, 1, face=face)
    m.points["depot_hearthgate"] = R(*P.HEARTH_POINTS["depot_hearthgate"]) + (Z - 1,)
    # the counters on the sides: the bank west, Broker Nell and Vesper east
    for (kx, ky, kn) in P.HEARTH_COUNTERS:
        S.counter(m, *R(kx, ky), kn, Z - 1, vertical=True)
    for npc, pos in P.BANK_NPCS.items():
        m.npcs.append((npc, R(*pos) + (Z - 1,)))
    m.npcs.append(("Vesper", R(*P.VESPER) + (Z - 1,)))
    for k in ("hearth_bank", "hearth_trader", "trade_hall", "shop_bank"):
        m.points[k] = R(*P.HEARTH_POINTS[k]) + (Z - 1,)
    m.sign(*R(48, 50), Z - 1, "Bank and Exchange. Banker Tolliver keeps your gold and your account vault; Trader Osric "
           "buys your loot.")
    m.sign(*R(65, 50), Z - 1, "Broker Nell explains the market. Vesper has work for climbers who ask.")
    m.sign(*R(57, 46), Z - 1, "The Hearth, depot floor. Your lockers are shared by every depot in the tower; open the "
           "market from any of them. Stairs down on both sides.")
    for (px, py) in ((50, 49), (63, 49)):                       # plants beside the middle
        S.prop(m, *R(px, py), Z - 1, POTS[px % 2])
    hearth_roof(m, R, Z - 2, up)

    # ---------------------------------------------------------------- the Climbers' Temple (plan: TEMPLE)
    x0, y0, hw, hh = P.TEMPLE
    claim("the temple", *R(x0, y0), hw, hh)
    m.building(*R(x0, y0), hw, hh, Z, floor="marble", door_side=None, style="white", doors=False,
               extra_gaps=[R(*a) for a in P.TEMPLE_ARCHES])
    m.storey(*R(x0, y0), hw, hh, Z - 1, floor="wood", style="white")           # the Trading Gallery
    m.storey(*R(*P.TEMPLE_TOWER[:2]), *P.TEMPLE_TOWER[2:], Z - 2, floor="marble", style="white")   # the Hall of Climbers
    paint(45, 13, 10, 8, WOOD)                                                    # the waiting hall (north-west)
    paint(45, 23, 10, 7, WOOD)                                                    # the trade hall (south-west)
    for a in P.TEMPLE_ARCHES:
        m.ground[(tx + a[0], ty + a[1], Z)] = MARBLE
    S.carpet(m, *R(56, 12), 2, 19, Z, 2576)                                       # the red cross of carpet
    S.carpet(m, *R(45, 22), 24, 1, Z, 2576)
    for px, py in ((54, 20), (59, 20), (54, 24), (59, 24)):
        S.prop(m, *R(px, py), Z, MARBLE_PILLAR)
    for px, py in ((54, 29), (59, 29), (54, 13), (59, 13)):
        S.prop(m, *R(px, py), Z, DG.COAL_BASIN)
    # the chapel (north-east)
    m.put(*R(65, 13), Z, 3515)                                                    # the altar
    S.carpet(m, *R(64, 14), 3, 6, Z, 2576)
    m.npcs.append(("Priest Odran", R(*P.PRIEST) + (Z,)))
    m.points["hearth_chapel"] = R(P.PRIEST[0], P.PRIEST[1] + 1) + (Z,)
    for px, py in ((61, 15), (67, 15), (67, 18)):
        S.prop(m, *R(px, py), Z, BENCH)
    # the waiting hall (north-west): find a party before you climb
    S.prop(m, *R(48, 14), Z, HERO_STATUE)
    S.prop(m, *R(52, 14), Z, ANGEL_STATUE)
    for px, py in ((47, 19), (51, 19)):
        S.prop(m, *R(px, py), Z, BENCH)
    for px, py in ((46, 13), (53, 19)):
        S.prop(m, *R(px, py), Z, POTS[px % 2])
    # the trade hall (south-west): tables to deal face to face
    for py in (24, 27):
        S.counter(m, *R(47, py), 6, Z)
    for px, py in ((46, 29), (53, 29)):
        S.prop(m, *R(px, py), Z, POTS[px % 2])
    # the south-east hall: benches by the stairs
    for px, py in ((61, 25), (64, 25)):
        S.prop(m, *R(px, py), Z, BENCH)
    S.prop(m, *R(66, 24), Z, ANGEL_STATUE)
    m.sign(*R(60, 21), Z, "The Climbers' Temple. Priest Odran in the chapel; the Trading Gallery upstairs; the Hall of "
           "Climbers at the top.")
    DG.hang(m, *R(x0, y0), hw, hh, Z, every=5, offset=3)
    # level 2: the Trading Gallery
    for px, py in ((46, 16), (60, 16), (46, 26), (60, 26)):
        S.counter(m, *R(px, py), 8, Z - 1)                                        # trade tables: stand either side and deal
    for px, py in ((48, 28), (64, 28)):
        S.prop(m, *R(px, py), Z - 1, BENCH)
    m.sign(*R(56, 15), Z - 1, "The Trading Gallery. Meet, haggle, and trade face to face.")
    DG.hang(m, *R(x0, y0), hw, hh, Z - 1, every=5, offset=4)
    # level 3: the Hall of Climbers
    S.prop(m, *R(52, 20), Z - 2, HERO_STATUE)
    S.prop(m, *R(61, 20), Z - 2, ANGEL_STATUE)
    S.prop(m, *R(51, 26), Z - 2, MARBLE_PILLAR)
    S.prop(m, *R(57, 26), Z - 2, MARBLE_PILLAR)
    S.carpet(m, *R(53, 22), 8, 3, Z - 2, 2576)
    m.sign(*R(56, 19), Z - 2, "The Hall of Climbers. Look for a party here before you climb. Say !top for the climbers.")
    DG.hang(m, *R(*P.TEMPLE_TOWER[:2]), *P.TEMPLE_TOWER[2:], Z - 2, every=4, offset=3)
    for name, (sx, sy, sz) in P.TEMPLE_STAIRS.items():
        m.stairs(*R(sx, sy), sz, floor="wood" if sz == Z else "marble", name=name)
    m.roof(*R(*P.TEMPLE_TOWER[:2]), *P.TEMPLE_TOWER[2:], Z - 2, "red")           # the tower's own roof
    gx_, gy_, gw_, gh_ = P.TEMPLE_GARDEN                                          # flower beds before the temple
    for y in range(gy_, gy_ + gh_):
        for x in range(gx_, gx_ + gw_):
            if not (54 <= x <= 59) and not P.in_plaza(x, y):
                m.ground[(tx + x, ty + y, Z)] = 4526
                if (x + y) % 2 == 0 and y == gy_ + 1:
                    S.prop(m, *R(x, y), Z, rng.choice(S.FLOWERS))
    paint(55, 31, 4, 3, MARBLE)

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
    dx_, dy_ = P.MANOR_AT[0] + 11, P.MANOR_AT[1]          # the manor's front door
    paint(dx_ - 1, gy0 + 1, 3, dy_ - gy0 - 1, MARBLE)     # the forecourt: gate to door
    paint(dx_ - 6, gy0 + 1, 13, 1, MARBLE)
    lamps([(dx_ - 5, gy0 + 2), (dx_ + 5, gy0 + 2)])
    for px in (dx_ - 3, dx_ + 3):
        S.prop(m, *R(px, gy0 + 2), Z, POTS[px % 2])
    for px, py in ((gx0 + 2, gy0 + 1), (gx0 + gw0 - 3, gy0 + 1)):   # a tree each side of the forecourt
        S.prop(m, *R(px, py), Z, rng.choice(S.TREES_BROAD[:3]))
    sgx, sgy, sgw, sgh = P.SPIRE_GARDENS                 # a public garden beside the way to the manor's gate
    paint(sgx, sgy, sgw, sgh, 4526)
    paint(*P.STREETS["Manor Walk"][0], MARBLE)
    garden_pond(m, R, Z, (100, 56), 3, 2, None, rng)
    for px, py in ((89, 53), (90, 59), (95, 53), (107, 59), (94, 59), (107, 53)):
        if free(px, py):
            S.prop(m, *R(px, py), Z, TREE)
    for px, py in ((92, 56), (100, 53), (100, 59)):
        if free(px, py):
            S.prop(m, *R(px, py), Z, BENCH)
    S.sprinkle(m, *R(sgx, sgy), sgw, sgh, Z, S.FLOWERS, 0.1, seed=62)
    m.sign(*R(87, 51), Z, "Spire Gardens. Manor Walk leads to the gate of Spire Manor.")

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
    m.sign(*R(gr[0] + 2, gr[1]), Z, "An old drain grate. Something echoes far below. Climbers say only the seasoned come back up.")
    m.points["underkeep_grate"] = grate

    gx1, gy1, gw1, gh1 = P.GREEN                         # Hearthgate Green: a park with a pond
    paint(gx1, gy1, gw1, gh1, 4526)
    for r in P.GREEN_PATHS:
        paint(*r, COBBLE)
    pd = P.POND
    garden_pond(m, R, Z, pd["c"], pd["rx"], pd["ry"], pd["pier"], rng)
    for px, py in ((22, 22), (26, 22), (19, 28), (29, 25)):            # benches looking at the pond
        S.prop(m, *R(px, py), Z, BENCH)
    for px, py in ((14, 16), (15, 19), (20, 16), (24, 17), (28, 16), (14, 25), (14, 32), (20, 33), (29, 33)):
        S.prop(m, *R(px, py), Z, rng.choice(S.TREES_BROAD[:3]))
    S.sprinkle(m, *R(gx1, gy1), gw1, 6, Z, S.FLOWERS, 0.10, seed=63)
    S.sprinkle(m, *R(gx1, 22), 4, 13, Z, S.FLOWERS, 0.10, seed=65)
    lamps([(18, 20), (18, 22), (12, 21), (16, 34)])
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

    # ---------------------------------------------------------------- round the Hearth: the fountain, benches, lamps
    m.put(*R(*P.FOUNTAIN), Z, 1922)                       # the fountain, in the temple garden
    for (px, py) in ((42, 43), (42, 55), (71, 43), (71, 55)):                           # benches by the shop doors
        if free(px, py):
            S.prop(m, *R(px, py), Z, BENCH)
    rim = []                                               # lamps round the plaza's rim, clear of the avenues
    import math
    for i in range(16):
        ang = (i + 0.5) * math.pi / 8
        px, py = int(round(cx + 15.4 * math.cos(ang))), int(round(cy + 15.4 * math.sin(ang)))
        if on_path(px, py) or not free(px, py) or (px, py) in hall:
            continue
        rim.append((px, py))
    lamps(rim)

    # ---------------------------------------------------------------- street lamps along the avenues and high roads
    lamps([(54, 3), (59, 8), (54, 9), (54, 70), (59, 80), (54, 90), (59, 92),
           (4, 47), (14, 47), (26, 47), (39, 51), (74, 47), (83, 51), (97, 47), (108, 51),
           (41, 12), (72, 12), (16, 12), (95, 12), (30, 58), (15, 80), (30, 80), (59, 74), (69, 82), (98, 61)])
    import hearthgate_dress                               # the open cobble, the gates and the doors dressed
    hearthgate_dress.dress(m, tx, ty, W, H, Z, rng, streets=streets | {(x, y) for x in range(55, 59) for y in range(33, 67)},
                           campfires=((15, 28), (105, 44)), inside=P.inside_wall)
    m.rng = main_rng
    return hid
