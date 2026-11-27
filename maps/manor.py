"""Spire Manor: the one grand house in Hearthgate, sold only in the Spire Shop (Jay, 2026-11-11: "pay to obtain only
... at least 3 levels high"; 2026-11-26: "it needs to feel premium, and also have features that players would want to
pay for, but not be totally game breaking").

One movable piece: build(m, x0, y0, z) lays the whole house with its top-left wall corner at (x0, y0), door in the
middle of the north wall, 22 x 16 tiles, four levels. Nothing here gives power: what the owner gets is space, comfort
and convenience (lib/spirebound/manor.lua has the rules).

  level 1  entrance hall with a red runner; dining hall (west); steward's office with a private depot, mailbox and
           the stair (east); the great hall with a fountain across the whole south side
  level 2  trophy and mannequin gallery (north); library (south-west); training hall with dummies (south-east)
  level 3  master suite (west); lounge (north-east); two guest rooms (south-east)
  level 4  roof garden: pond, benches, telescope, and the Waystone
"""
import scenery as S
import dungeon as DG

W, H, HOUSE_ID = 22, 16, 99      # house 99: clear of every other floor's numbers
MARBLE_PILLAR, HERO_STATUE, ANGEL_STATUE = 2153, 2027, 2031
FOUNTAIN, BENCH, TELESCOPE, TREE, CRYSTAL = 1922, 2370, 3488, 3619, 1841
TABLE, ROUND_TABLE, BIG_TABLE = 2315, 2316, 2314
CHAIR_S, CHAIR_E, CHAIR_N, CHAIR_W = 2362, 2363, 2364, 2365          # the purple cushioned chairs
BED, DRESSER, DRAWER, WARDROBE, MIRROR, CLOCK = 2487, 2427, 2431, 2441, 2630, 2445
BOOKCASE_N, BOOKCASE_W, CHEST, TREASURE = 2437, 2438, 2472, 2478
TAPESTRY_RED, TAPESTRY_BLUE, TAPESTRY_PURPLE, PICTURE = 2654, 2657, 2642, 2640
TROPHY_WALL, WEAPON_RACK, ARMOUR_RACK = 2670, 6110, 6112
DUMMIES = (28559, 28561, 28563)
MAILBOX, POT_A, POT_B, BARREL = 3501, 316, 321, 2523
BLACK_MARBLE, FLAGSTONE = 410, 416
FIXTURE_AID = 59900            # scripts/spirebound/manor.lua: nobody can move an item that carries it
FIXTURES = {TABLE, ROUND_TABLE, BIG_TABLE, 872, POT_A, POT_B, CLOCK, DRAWER, WEAPON_RACK, ARMOUR_RACK, BARREL, TREASURE,
            CHEST, WARDROBE, *DUMMIES, *S.FLOWERS}


def _wall(m, x0, y0, z, tiles):
    m.autowall([(x0 + x, y0 + y) for x, y in tiles], z, "white")


def build(m, x0, y0, z):
    """Returns the door's position. Sets the house, its sign and the points scripts and tests use."""
    P = lambda x, y, zz, iid: S.prop(m, x0 + x, y0 + y, zz, iid)      # noqa: E731

    # ------------------------------------------------------------------ level 1
    m.building(x0, y0, W, H, z, floor="marble", door_side="n", style="white", doors=True)
    m.buildings[-1]["roof"] = None                       # the roof is the garden terrace instead
    for yy in range(1, H - 1):
        for xx in range(1, W - 1):
            if xx in (1, W - 2) or yy in (1, H - 2):
                m.ground[(x0 + xx, y0 + yy, z)] = BLACK_MARBLE          # a black marble border round the house
    _wall(m, x0, y0, z, [(7, y) for y in range(1, 7) if y not in (3, 4)])          # dining hall | entrance hall
    _wall(m, x0, y0, z, [(14, y) for y in range(1, 7) if y not in (3, 4)])         # entrance hall | steward's office
    _wall(m, x0, y0, z, [(x, 7) for x in range(1, 8) if x not in (3, 4)])          # dining hall / great hall
    _wall(m, x0, y0, z, [(x, 7) for x in range(14, 21) if x not in (17, 18)])      # office / great hall
    S.carpet(m, x0 + 10, y0 + 1, 2, 11, z)                                          # the runner, door to fountain
    for px, py in ((8, 1), (13, 1), (8, 6), (13, 6)):
        P(px, py, z, MARBLE_PILLAR)
    P(9, 2, z, HERO_STATUE)
    P(12, 2, z, ANGEL_STATUE)
    P(9, 5, z, POT_A)
    P(12, 5, z, POT_B)
    # dining hall: one long table, six cushioned chairs, a sideboard
    for ty in (2, 3, 4, 5):
        P(3, ty, z, TABLE)
        P(4, ty, z, TABLE)
    for ty in (2, 4, 5):
        P(2, ty, z, CHAIR_E)
        P(5, ty, z, CHAIR_W)
    P(1, 1, z, DRESSER)
    P(5, 1, z, CLOCK)
    P(1, 6, z, BARREL)
    P(2, 6, z, BARREL)
    # steward's office: a private depot (two lockers), the mailbox, a desk; the stair stands in its north-east corner
    m.depot(x0 + 15, y0 + 1, z, 1)
    m.depot(x0 + 16, y0 + 1, z, 1)
    m.put(x0 + 17, y0 + 1, z, MAILBOX)
    P(16, 5, z, TABLE)
    P(17, 5, z, TABLE)
    P(16, 6, z, CHAIR_N)
    P(15, 6, z, TREASURE)
    m.points["manor_steward"] = (x0 + 16, y0 + 4, z)
    m.points["manor_housekeeper"] = (x0 + 3, y0 + 9, z)
    m.npcs.append(("Steward Aldous", (x0 + 16, y0 + 4, z)))
    m.npcs.append(("Housekeeper Mirelle", (x0 + 3, y0 + 9, z)))
    # the great hall: fountain, pillars, benches along the south wall, statues, flowers
    m.put(x0 + 10, y0 + 12, z, FOUNTAIN)
    for px, py in ((4, 9), (17, 9), (4, 13), (17, 13), (8, 9), (13, 9)):
        P(px, py, z, MARBLE_PILLAR)
    for px in (6, 14):
        P(px, 14, z, BENCH)
    for px, py in ((2, 14), (19, 14), (2, 8), (19, 8)):
        P(px, py, z, POT_A if px == 2 else POT_B)
    P(7, 11, z, ROUND_TABLE)
    P(6, 11, z, CHAIR_E)
    P(8, 11, z, CHAIR_W)
    P(14, 11, z, ROUND_TABLE)
    P(13, 11, z, CHAIR_E)
    P(15, 11, z, CHAIR_W)
    DG.hang(m, x0, y0, W, H, z, every=3, h_item=TAPESTRY_RED, v_item=DG.LAMP_V, offset=2)
    m.stairs(x0 + 20, y0 + 3, z, floor="wood", name="spire_manor_1")

    # ------------------------------------------------------------------ level 2: gallery, library, training hall
    z2 = z - 1
    m.storey(x0, y0, W, H, z2, floor="wood", style="white")
    _wall(m, x0, y0, z2, [(x, 7) for x in range(1, 21) if x not in (5, 6, 15, 16)])
    _wall(m, x0, y0, z2, [(10, y) for y in range(8, 15)])
    S.carpet(m, x0 + 3, y0 + 3, 15, 2, z2)                                          # the gallery's runner
    for px in (4, 7, 10, 13, 16):                                                   # display stands down the gallery
        P(px, 5, z2, 872)
    for px in (5, 8, 11, 14):
        P(px, 2, z2, ARMOUR_RACK if px in (5, 14) else WEAPON_RACK)
    DG.hang(m, x0, y0, W, H, z2, every=3, h_item=TROPHY_WALL, v_item=DG.LAMP_V, offset=3)
    m.points["manor_gallery"] = (x0 + 10, y0 + 4, z2)
    # library (south-west): bookcases round the walls, a reading table
    for px in (1, 3, 7, 9):
        P(px, 8, z2, BOOKCASE_N)
    for py in (10, 12, 14):
        P(1, py, z2, BOOKCASE_W)
    P(5, 11, z2, BIG_TABLE)
    P(4, 11, z2, CHAIR_E)
    P(7, 12, z2, CHAIR_W)
    P(8, 14, z2, CLOCK)
    S.carpet(m, x0 + 3, y0 + 10, 5, 4, z2)
    # training hall (south-east): three exercise dummies on a bare floor, a weapon rack, a bench
    for px, iid in zip((13, 16, 19), DUMMIES):
        m.put(x0 + px, y0 + 9, z2, iid)
    P(12, 14, z2, BENCH)
    P(19, 14, z2, CHEST)
    m.points["manor_training"] = (x0 + 16, y0 + 11, z2)
    m.stairs(x0 + 1, y0 + 3, z2, floor="wood", name="spire_manor_2")

    # ------------------------------------------------------------------ level 3: master suite, lounge, guest rooms
    z3 = z - 2
    m.storey(x0, y0, W, H, z3, floor="wood", style="white")
    _wall(m, x0, y0, z3, [(10, y) for y in range(1, 15) if y not in (7, 8)])        # master suite | the east side
    _wall(m, x0, y0, z3, [(x, 7) for x in range(11, 21) if x not in (12, 13, 18)])  # lounge / guest rooms
    _wall(m, x0, y0, z3, [(16, y) for y in range(8, 15)])                           # guest room | guest room
    # master suite: bed on a carpet, wardrobe, dresser, mirror, a sitting corner, a strongbox
    P(2, 9, z3, BED)                                      # (off the carpet: a bed is two pieces and needs bare floor)
    S.carpet(m, x0 + 4, y0 + 9, 5, 4, z3)
    P(3, 9, z3, DRAWER)
    P(2, 13, z3, WARDROBE)
    P(8, 13, z3, DRESSER)
    P(2, 0, z3, MIRROR)
    P(4, 13, z3, TREASURE)
    P(6, 5, z3, ROUND_TABLE)
    P(5, 5, z3, CHAIR_E)
    P(7, 5, z3, CHAIR_W)
    P(8, 1, z3, BOOKCASE_N)
    P(4, 1, z3, CLOCK)
    # lounge: the stair to the roof stands in its north-east corner
    P(13, 3, z3, BIG_TABLE)
    P(12, 3, z3, CHAIR_E)
    P(15, 4, z3, CHAIR_W)
    P(13, 5, z3, CHAIR_N)
    P(11, 1, z3, BOOKCASE_N)
    S.carpet(m, x0 + 12, y0 + 2, 5, 4, z3)
    # two guest rooms, a bed and a chest of drawers each
    for gx in (12, 18):
        P(gx, 10, z3, BED)
        P(gx + 1, 13, z3, DRAWER)
    P(14, 9, z3, POT_A)
    P(20, 9, z3, POT_B)
    DG.hang(m, x0, y0, W, H, z3, every=4, h_item=TAPESTRY_BLUE, v_item=DG.LAMP_V, offset=3)
    m.points["manor_suite"] = (x0 + 5, y0 + 7, z3)
    m.stairs(x0 + 20, y0 + 3, z3, floor="wood", name="spire_manor_3")

    # ------------------------------------------------------------------ level 4: the roof garden (open to the sky)
    tz = z - 3
    for yy in range(y0 + 1, y0 + H):
        for xx in range(x0 + 1, x0 + W):
            if (xx, yy, tz) not in m.ground:
                lawn = x0 + 3 <= xx <= x0 + W - 3 and y0 + 3 <= yy <= y0 + H - 3
                m.ground[(xx, yy, tz)] = m.pick("grass") if lawn else FLAGSTONE
    for xx in range(x0 + 1, x0 + W):                     # a limestone balustrade round the edge
        for yy in (y0 + 1, y0 + H - 1):
            if (xx, yy) != (x0 + 20, y0 + 2):
                m.put(xx, yy, tz, 9273)
    for yy in range(y0 + 2, y0 + H - 1):
        for xx in (x0 + 1, x0 + W - 1):
            m.put(xx, yy, tz, 9272)
    for px in range(5, 10):                               # the owner's fish pond (!pond): the map builder adds its shore
        for py in range(9, 12):
            if (px, py) not in ((5, 9), (9, 9), (5, 11), (9, 11)):
                m.ground[(x0 + px, y0 + py, tz)] = m.pick("water")
    m.put(x0 + 14, y0 + 10, tz, FOUNTAIN)
    for px, py in ((5, 5), (16, 5), (11, 13)):
        P(px, py, tz, BENCH)
    for px, py in ((4, 4), (17, 4), (4, 12), (17, 12)):
        P(px, py, tz, TREE)
    S.sprinkle(m, x0 + 3, y0 + 3, W - 5, H - 5, tz, S.FLOWERS, 0.10, seed=99)
    P(18, 13, tz, TELESCOPE)
    for px, py in ((10, 5), (11, 5), (10, 6), (11, 6)):   # the Waystone on a flagstone dais
        m.ground[(x0 + px, y0 + py, tz)] = FLAGSTONE
        m.clear_items(x0 + px, y0 + py, tz)
    m.put(x0 + 10, y0 + 5, tz, CRYSTAL)
    m.points["manor_waystone"] = (x0 + 10, y0 + 6, tz)
    m.flag(x0 + 1, y0 + 1, W - 1, H - 1, tz, 0x0001)

    # ------------------------------------------------------------------ the house itself
    tiles = []
    for zz in (z, z2, z3, tz):
        for yy in range(y0 + 1, y0 + H):
            for xx in range(x0 + 1, x0 + W):
                if (xx, yy, zz) in m.ground and not (zz == z and (xx == x0 + W - 1 or yy == y0 + H - 1)):
                    m.house[(xx, yy, zz)] = HOUSE_ID
                    tiles.append((xx, yy, zz))
    # Furniture the engine counts as "movable" is thrown away when it stands on a house tile (a house's movable things
    # belong to its owner and live in the database). So each such piece stands on a tile that is inside the building
    # but not part of the house, and carries an action id that scripts/spirebound/manor.lua refuses to let anyone move:
    # the manor's furniture is a fixture, it can never be carried off, sold or duplicated.
    import struct
    lock = bytes([4]) + struct.pack("<H", FIXTURE_AID)                  # OTBM_ATTR_ACTION_ID
    for pos in list(tiles):
        its = m.items.get(pos)
        if its and any(i in FIXTURES for i, _a in its):
            m.items[pos] = [(i, lock if i in FIXTURES else a_) for i, a_ in its]
            m.house.pop(pos, None)
            tiles.remove(pos)
    m.manor_roof = (x0, y0, W + 1, H + 1, tz)                           # the layout marks it as town ground (a safe zone)
    door = (x0 + W // 2, y0)
    m.house[(door[0], door[1], z)] = HOUSE_ID
    m.houses[HOUSE_ID] = {"name": "Spire Manor", "town": 1, "rent": 0, "entry": (door[0], door[1] - 1, z), "size": len(tiles) + 1}
    m.points["spire_manor_plot"] = (x0, y0, z)
    m.points["spire_manor"] = (x0 + 10, y0 + 4, z)
    m.sign(x0 + 9, y0 - 1, z, "Spire Manor. Four floors: a great hall, a private depot and steward, a gallery, a library, "
           "a training hall, guest rooms and a roof garden with its Waystone. Its deed is sold in the Spire Shop (!shop).")
    return door
