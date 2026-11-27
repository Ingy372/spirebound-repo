"""N3 (FLOOR1_REVIEW.md F1-50, Q47), redone for Hearthgate v4 (2026-11-27): the town dressed so it looks lived in.

Runs after the town's buildings, streets, plaza and green places are in place (maps/hearthgate.py). It only ever adds
things on open ground, so it can't block a door, a lane or an avenue:
  * the open cobble: a few things (a tree, barrels, crates, a cart, a bench, flower pots) only where a 5 x 5 patch of bare
    cobble surrounds the spot and never on a street, spaced at least 7 tiles apart;
  * a campfire with a bench on Hearthgate Green and in the Training Yard;
  * a lamp beside the front doors that face south or east;
  * braziers either side of the four town gates (roadmap P3b).
v4.1 (Jay, 2026-11-27: "the town is grey, brighten it up some"): the ground between buildings is grass, so this also
  * paves a path from every door that faces grass to the nearest street (`door_paths`);
  * plants trees, bushes and flowers on the grass (`greenery`): a tree only where a 3 x 3 patch of bare grass surrounds
    it (it can never close a gap between houses), nothing within a tile of a wall or two tiles of a door.
"""
import scenery as S

COBBLE = 870
CART = 5543
BRAZIER = 2113          # coal basin (lit)
CRATES = [2519, 117, 118, 2472]
BARRELS = [2523, 116]
POTS = [316, 321, 324, 329]
TREE = 3619
CAMPFIRE = 1996
PILLAR = 1296            # grey stone post


def _bare(m, x, y, z, r):
    """Every tile within r of (x, y) is plain cobble with nothing on it."""
    for a in range(-r, r + 1):
        for b in range(-r, r + 1):
            p = (x + a, y + b, z)
            if m.ground.get(p) != COBBLE or m.items.get(p):
                return False
    return True


def dress(m, tx, ty, tw, th, z, rng, streets=(), campfires=((15, 25), (105, 44)), inside=None):
    """streets: town-relative tiles that must stay clear (lanes are cobble too). inside(x, y): town-relative, True
    within the city wall."""
    def R(x, y):
        return tx + x, ty + y

    def free(x, y):
        p = R(x, y) + (z,)
        return p in m.ground and not m.items.get(p)

    keep = {R(x, y) for (x, y) in streets}
    doors = door_paths(m, tx, ty, tw, th, z)
    # ---- the open cobble: a few things in the bare places, never in a lane
    kinds = [TREE, TREE, BARRELS, CRATES, POTS, CART, "bench"]
    placed = []
    spots = sorted((x, y) for x in range(tx + 3, tx + tw - 3) for y in range(ty + 3, ty + th - 3))
    rng.shuffle(spots)
    for (x, y) in spots:
        if len(placed) >= 26:
            break
        if (x, y) in keep or (x + 1, y) in keep:
            continue
        if any(max(abs(x - px), abs(y - py)) < 7 for px, py in placed):
            continue
        if not _bare(m, x, y, z, 2):
            continue
        k = kinds[len(placed) % len(kinds)]
        if k == "bench":
            m.put(x, y, z, 2370)
        elif isinstance(k, list):
            m.put(x, y, z, rng.choice(k))
            if k is not POTS and _bare(m, x + 1, y, z, 0):
                m.put(x + 1, y, z, rng.choice(k))          # barrels and crates come in twos
        else:
            m.put(x, y, z, k)
        placed.append((x, y))

    # ---- campfires (P3b): one on Hearthgate Green, one in the Training Yard, each with a bench beside it
    for (x, y) in campfires:
        spot = next(((x + a, y + b) for a in range(-2, 3) for b in range(-2, 3)
                     if free(x + a, y + b) and free(x + a + 1, y + b)), None)
        if spot:
            S.prop(m, *R(*spot), z, CAMPFIRE)
            S.prop(m, *R(spot[0] + 1, spot[1]), z, 2370)

    door_lamps(m, tx, ty, tw, th, z)
    greenery(m, tx, ty, tw, th, z, rng, keep, doors, inside)

    # ---- braziers at the four gates (P3b), just inside the wall either side of each gap
    mid_x, mid_y = tw // 2, th // 2
    for (x, y) in ((mid_x - 3, 1), (mid_x + 4, 1), (mid_x - 3, th - 2), (mid_x + 4, th - 2),
                   (1, mid_y - 2), (1, mid_y + 4), (tw - 2, mid_y - 2), (tw - 2, mid_y + 4)):
        if free(x, y):
            S.prop(m, *R(x, y), z, BRAZIER)
    return placed


def _door_ids():
    from mapgen import FAMILIES
    return {i for f in FAMILIES.values() for k, i in f.items() if i and k.startswith("door")}


def door_paths(m, tx, ty, tw, th, z, reach=10):
    """A cobble path from every door that opens onto grass, straight out to the nearest paving (a street, the plaza, a
    yard). When nothing paved lies within `reach` tiles, only the two tiles in front of the door are paved. Returns the
    door tiles (world coordinates)."""
    dids = _door_ids()
    doors = [(x, y) for (x, y, zz), its in m.items.items()
             if zz == z and tx <= x < tx + tw and ty <= y < ty + th and any(i in dids for i, _a in its)]
    for (x, y) in doors:
        for (a, b) in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            first = (x + a, y + b, z)
            if m.ground.get(first) not in S.GRASS_IDS or m.items.get(first):
                continue
            run = []
            for k in range(1, reach + 1):
                q = (x + a * k, y + b * k, z)
                if q not in m.ground or m.items.get(q):
                    break
                if m.ground[q] not in S.GRASS_IDS:
                    run.append(None)                       # reached paving
                    break
                run.append(q)
            if run and run[-1] is None:
                run = run[:-1]
            else:
                run = run[:2]
            for q in run:
                m.ground[q] = COBBLE
    return doors


def greenery(m, tx, ty, tw, th, z, rng, keep, doors, inside):
    """Trees, bushes and flowers on the town's grass (see the module notes for the rules)."""
    natural = S.SCENERY | set(POTS)

    def grass_free(p):
        return m.ground.get(p) in S.GRASS_IDS and not m.items.get(p) and (p[0], p[1]) not in keep

    def clear_round(x, y, r):
        """No wall, furniture or sign within r tiles (natural things are fine)."""
        for a in range(-r, r + 1):
            for b in range(-r, r + 1):
                its = m.items.get((x + a, y + b, z))
                if its and any(i not in natural for i, _a in its):
                    return False
                if (x + a, y + b, z) not in m.ground:
                    return False
        return True

    near_door = {(x + a, y + b) for (x, y) in doors for a in range(-2, 3) for b in range(-2, 3)}
    trees = [(x, y) for (x, y, zz), its in m.items.items() if zz == z and tx <= x < tx + tw and ty <= y < ty + th
             and any(i in S.TREES_BROAD or i == TREE for i, _a in its)]
    spots = [(x, y) for x in range(tx + 2, tx + tw - 2) for y in range(ty + 2, ty + th - 2)
             if (inside is None or inside(x - tx, y - ty)) and (x, y) not in near_door]
    rng.shuffle(spots)
    n_tree = n_bush = n_flower = 0
    for (x, y) in spots:
        p = (x, y, z)
        if not grass_free(p) or not clear_round(x, y, 1):
            continue
        if inside is not None and not all(inside(x - tx + a, y - ty + b) for a in (-2, 0, 2) for b in (-2, 0, 2)):
            continue                                       # keep clear of the city wall
        open3 = all(grass_free((x + a, y + b, z)) for a in (-1, 0, 1) for b in (-1, 0, 1))
        roll = rng.random()
        if open3 and n_tree < 90 and all(max(abs(x - u), abs(y - v)) >= 5 for (u, v) in trees):
            m.put(x, y, z, rng.choice(S.TREES_BROAD[:3]))
            trees.append((x, y))
            n_tree += 1
        elif open3 and roll < 0.03 and n_bush < 40:
            m.put(x, y, z, rng.choice(S.BUSHES))
            n_bush += 1
        elif roll < 0.09:
            m.put(x, y, z, rng.choice(S.FLOWERS))
            n_flower += 1
    return n_tree, n_bush, n_flower


def door_lamps(m, tx, ty, tw, th, z):
    """P3b: a lit lamp on the outside wall beside each front door that faces south or east (a lamp hung on a south or
    east wall shows outside; on a north or west wall it would hang inside, see maps/dungeon.py `hang`). At night the
    streets glow round every doorway. Lamps go only on plain wall pieces, never on a window, corner or door."""
    from mapgen import FAMILIES
    lamp_h, lamp_v = 2910, 2908
    plain_h = {f["h"] for f in FAMILIES.values()}
    plain_v = {f["v"] for f in FAMILIES.values()}
    walls = {i for f in FAMILIES.values() for k, i in f.items() if i and not k.startswith("door")}
    n = 0
    for b in m.buildings:
        x0, y0, w, h = b["rect"]
        if b["z"] != z or not (tx <= x0 and x0 + w <= tx + tw and ty <= y0 and y0 + h <= ty + th):
            continue
        ids = lambda x, y: [i for i, _a in m.items.get((x, y, z), [])]        # noqa: E731
        south = [(x, y0 + h - 1) for x in range(x0 + 1, x0 + w - 1)]
        east = [(x0 + w - 1, y) for y in range(y0 + 1, y0 + h - 1)]
        for row, plain, lamp, step in ((south, plain_h, lamp_h, (1, 0)), (east, plain_v, lamp_v, (0, 1))):
            for (x, y) in row:
                if any(i in walls for i in ids(x, y)) or (x, y, z) not in m.ground:
                    continue                                   # a wall piece, not the doorway
                for d in (-2, 2):
                    q = (x + d * step[0], y + d * step[1])
                    have = ids(*q)
                    if have and have[-1] in plain and lamp not in have:
                        m.put(q[0], q[1], z, lamp)
                        n += 1
    return n


def dress_yard(m, yx, yy, yw, yh, z):
    """P7 (FLOOR1_REVIEW.md F1-01, Q47): the Arrival Yard reads as the foot of the tower, not a fenced field. Only adds
    things on free grass away from the path, the gates and the pen; its own random numbers (the rest of the map's
    scenery must not shift). The gates, fences, signs and points stay exactly where maps/layout_floor1.py put them."""
    import random
    rng = random.Random(4711)

    def grass_free(x, y):
        p = (x, y, z)
        return p in m.ground and m.ground[p] in S.GRASS_IDS and not m.items.get(p)

    # the Spire's forecourt: paved behind the sealed door's wall, a colonnade of pillars along the yard's north wall
    for x in range(yx + 1, yx + 12):
        for y in (yy + 1, yy + 2):
            m.clear_items(x, y, z)
            m.ground[(x, y, z)] = 416                  # flagstone
        if (x - yx) % 2 == 0:
            m.put(x, yy + 1, z, PILLAR)
    # hedges along the inside of the north and south walls, broken here and there
    def by_granary(x, y):                              # nothing natural within a tile of the Old Granary (x 13..24, y 2..8)
        return yx + 12 <= x <= yx + 25 and yy + 1 <= y <= yy + 9

    for x in range(yx + 12, yx + yw - 15):
        for y in (yy + 1, yy + yh - 2):
            if grass_free(x, y) and rng.random() < 0.7 and not by_granary(x, y):
                m.put(x, y, z, rng.choice(S.BUSHES))
    # a tree in the corners of each stage (between the fences), clear of the path rows (y 9..14)
    stages = [(yx + 1, yx + 25), (yx + 27, yx + 31), (yx + 33, yx + 37), (yx + 39, yx + 43), (yx + 45, yx + 49)]
    for (a, b) in stages:
        for x in (a + 1, b - 1):
            for y in (yy + 3, yy + yh - 4):
                if b - a >= 4 and grass_free(x, y):
                    m.put(x, y, z, rng.choice(S.TREES_BROAD[:3]))
    # flower beds beside the path, two tiles off it
    for x in range(yx + 2, yx + 50):
        for y in (yy + 7, yy + 16):
            if grass_free(x, y) and rng.random() < 0.35 and not by_granary(x, y):
                m.put(x, y, z, rng.choice(S.FLOWERS))

