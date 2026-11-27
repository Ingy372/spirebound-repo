"""House plans (Jay, 2026-11-26: "currently the housing options are boring and all the same. unique housing options
... is what i was going for").

Every ordinary house used to be the same bare square. Now each lot picks one of the plans below, so neighbours differ
in size, rooms, beds and rent. A plan only uses furniture the engine keeps on a house tile (beds, bookcases, dressers,
cushioned chairs, benches): it throws away anything it counts as movable (tables, chests, pots), because a house's
movable things belong to its owner. Players bring the rest.

Use:  x0, y0, w, h, plan = footprint(hid, x0, y0, w, h, door_side)     before m.house_building(...)
      fit(m, hid, x0, y0, w, h, z, door_side, style, plan, storeys)   after it
      rent_for(base, w, h, plan, storeys)
"""
BED, BOOKCASE_N, BOOKCASE_W, DRESSER, BENCH = 2487, 2437, 2438, 2427, 2370
CHAIR_S, CHAIR_E, CHAIR_N, CHAIR_W = 2362, 2363, 2364, 2365

# key, how much shorter than the lot (a yard is left behind the house), inner wall, beds, what the sign calls it
PLANS = [
    dict(key="one-room", shrink=0, wall=None, beds=1, label="one room"),
    dict(key="two-room", shrink=0, wall="across", beds=1, label="two rooms"),
    dict(key="yard", shrink=2, wall=None, beds=1, label="one room and a back yard"),
    dict(key="side-bedroom", shrink=0, wall="along", beds=1, label="a living room and a side bedroom"),
    dict(key="twin", shrink=0, wall="across", beds=2, label="two rooms, two beds"),
    dict(key="snug", shrink=1, wall=None, beds=1, label="a snug single room"),
]


def pick(hid):
    """Neighbouring house numbers never get the same plan."""
    return PLANS[(hid * 2 + hid // 3) % len(PLANS)]


def footprint(hid, x0, y0, w, h, door_side, allow_shrink=True):
    """The house's real rectangle inside its lot: some plans are shorter and leave a yard behind (the door stays on
    the street side)."""
    plan = pick(hid)
    s = plan["shrink"] if allow_shrink else 0
    if s and door_side == "n":
        h -= s
    elif s and door_side == "s":
        y0, h = y0 + s, h - s
    elif s and door_side == "w":
        w -= s
    elif s and door_side == "e":
        x0, w = x0 + s, w - s
    return x0, y0, w, h, plan


def rent_for(base, w, h, plan, storeys=1, standard=36):
    """Rent follows floor space (a standard town house is 6 x 6 inside), plus a little for a second bed."""
    area = (w - 2) * (h - 2) * storeys
    rent = base * area / (standard * storeys) * (1.1 if plan["beds"] > 1 else 1.0) * (1.0 if storeys == 1 else 1.0)
    return max(100, int(round(rent / 50.0)) * 50)


def fit(m, hid, x0, y0, w, h, z, door_side, style, plan, storeys=1):
    """Inner wall, bed(s) and a few fixed pieces. Works for a door on any side: (a, b) is a spot `a` tiles along the
    door wall and `b` tiles deep into the house."""
    ix0, iy0, iw, ih = x0 + 1, y0 + 1, w - 2, h - 2
    A, B = (iw, ih) if door_side in ("n", "s") else (ih, iw)

    def at(a, b):
        if door_side == "n":
            return ix0 + a, iy0 + b
        if door_side == "s":
            return ix0 + a, iy0 + ih - 1 - b
        if door_side == "w":
            return ix0 + b, iy0 + a
        return ix0 + iw - 1 - b, iy0 + a

    door_a = (w // 2 if door_side in ("n", "s") else h // 2) - 1
    used = {at(door_a, 0), at(door_a, 1)}
    if storeys > 1:                                           # the stairs stand in the back right corner (mapgen)
        sx, sy = x0 + w - 2, (y0 + h - 3 if door_side == "n" else y0 + 2)
        used |= {(sx + dx, sy + dy) for dx in (-1, 0) for dy in (-1, 0, 1)}
    wall = plan["wall"]
    if storeys > 1:                                           # two-storey houses: the upstairs is the second room
        wall = None
    gap = None
    if A * B < 30:                                            # a cabin is too small to divide
        wall = None
    if wall == "across" and B >= 5:
        b = B // 2
        gap_a = 1 if door_a > 2 else A - 2
        tiles = [at(a, b) for a in range(A) if a != gap_a and at(a, b) not in used]
        m.autowall(tiles, z, style)
        gap = at(gap_a, b)
        used |= set(tiles) | {gap, at(gap_a, b - 1), at(gap_a, b + 1)}
    elif wall == "along" and A >= 6:
        a = A - 3
        gap_b = B - 2
        tiles = [at(a, b) for b in range(1, B) if b != gap_b]
        m.autowall(tiles, z, style)
        used |= set(tiles) | {at(a, gap_b), at(a - 1, gap_b), at(a + 1, gap_b)}
    else:
        wall = None

    def put(x, y, zz, iid, tall=False):
        spots = [(x, y)] + ([(x, y + 1)] if tall else [])
        if zz == z and any(s in used for s in spots):
            return False
        if any((sx_, sy_, zz) not in m.ground or m.items.get((sx_, sy_, zz)) for sx_, sy_ in spots):
            return False
        m.put(x, y, zz, iid)
        if zz == z:
            used.update(spots)
        return True

    # beds: a bed is two tiles, head to the north. They stand at the back of the house (upstairs if there is one);
    # in a side-bedroom plan the first bed stands in the side room.
    bz = z - 1 if storeys > 1 else z
    left = {"n": (ix0, iy0 + ih - 2), "s": (ix0, iy0), "w": (ix0 + iw - 1, iy0), "e": (ix0, iy0)}[door_side]
    right = {"n": (ix0 + iw - 1, iy0 + ih - 2), "s": (ix0 + iw - 1, iy0), "w": (ix0 + iw - 1, iy0 + ih - 2), "e": (ix0, iy0 + ih - 2)}[door_side]
    order = [right, left] if (wall == "along" and storeys == 1) else [left, right]
    if storeys > 1:
        order = [left, (left[0] + 2, left[1])]
    placed = 0
    for bx, by in order:
        if placed < plan["beds"] and put(bx, by, bz, BED, tall=True):
            placed += 1
    # a bookcase on the north wall, a dresser beside the bed, a bench or chairs in the front room
    for bx in (ix0 + 1, ix0 + iw - 2, ix0, ix0 + iw - 1):
        if put(bx, iy0, z, BOOKCASE_N if hid % 2 else DRESSER):
            break
    for cx, cy, cid in ((ix0 + iw - 1, iy0 + ih // 2, CHAIR_W), (ix0, iy0 + ih // 2, CHAIR_E)):
        if (hid + cx) % 3 and put(cx, cy, z, cid):
            break
    if iw * ih >= 30:
        for bx, by in (at(A - 2, 1), at(1, 1), at(A - 2, 2)):
            if put(bx, by, z, BENCH):
                break
    return placed


def yard(m, lot, house, z, S, rng):
    """The strip a shorter house leaves inside its lot becomes a little garden."""
    lx, ly, lw, lh = lot
    hx, hy, hw, hh = house
    for yy in range(ly, ly + lh):
        for xx in range(lx, lx + lw):
            if not (hx <= xx < hx + hw and hy <= yy < hy + hh):
                m.ground[(xx, yy, z)] = m.pick("grass")
                m.clear_items(xx, yy, z)
                if (xx + yy) % 3 == 0:
                    S.prop(m, xx, yy, z, rng.choice(S.FLOWERS + S.BUSHES))
