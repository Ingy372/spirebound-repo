"""N3 (FLOOR1_REVIEW.md F1-50, Q47): Hearthgate dressed so it looks lived in, not generated.

Runs after the town's buildings, streets and green places are in place (maps/layout_floor1.py). It only ever adds
things on open ground, so it can't block a door, a lane or an avenue:
  * the Hearth Square: flower pots along the Ring, crates, barrels and a cart by the market stalls, and the notice board
    (live news, scripts/spirebound/monument.lua);
  * the open cobble: a few things (a tree, barrels, crates, a cart, a bench, flower pots) only where a 5 x 5 patch of bare
    cobble surrounds the spot, so lanes of four tiles or less stay clear, spaced at least 7 tiles apart;
  * braziers either side of the four town gates (roadmap P3b).
"""
import scenery as S

COBBLE = 870
NOTICE_BOARD = 2597
CART = 5543
BRAZIER = 2113          # coal basin (lit)
CRATES = [2519, 117, 118, 2472]
BARRELS = [2523, 116]
POTS = [316, 321, 324, 329]
TREE = 3619
PARASOLS = [625, 626, 627]


def _bare(m, x, y, z, r):
    """Every tile within r of (x, y) is plain cobble with nothing on it."""
    for a in range(-r, r + 1):
        for b in range(-r, r + 1):
            p = (x + a, y + b, z)
            if m.ground.get(p) != COBBLE or m.items.get(p):
                return False
    return True


def dress(m, tx, ty, tw, th, z, rng):
    def R(x, y):
        return tx + x, ty + y

    def free(x, y):
        p = R(x, y) + (z,)
        return p in m.ground and not m.items.get(p)

    # ---- the Hearth Square (Ring: x 38..75, y 33..70; the Hearth hall: x 42..71, y 38..60)
    for y in range(40, 59, 4):                    # flower pots down both sides of the Ring, clear of the side arches
        if 47 <= y <= 51:
            continue
        for x in (39, 74):
            if free(x, y):
                S.prop(m, *R(x, y), z, rng.choice(POTS))
    for x in range(44, 70, 5):                    # and along the north side, clear of the North Avenue
        if 54 <= x <= 59:
            continue
        if free(x, 35):
            S.prop(m, *R(x, 35), z, rng.choice(POTS))
    # the market corner: goods stacked beside the stalls, a trader's cart
    for (x, y), pid in (((37, 68), CRATES[0]), ((37, 67), BARRELS[0]), ((48, 69), CRATES[1]), ((65, 68), BARRELS[1]),
                        ((70, 64), CRATES[2]), ((76, 64), BARRELS[0])):
        if free(x, y):
            S.prop(m, *R(x, y), z, pid)
    if free(43, 66):
        S.prop(m, *R(43, 66), z, CART)
    for (x, y) in ((41, 69), (48, 69), (69, 69), (42, 63), (70, 63), (75, 63)):    # a parasol beside each stall
        if free(x, y):
            S.prop(m, *R(x, y), z, PARASOLS[(x + y) % len(PARASOLS)])
    if free(46, 35) and free(47, 35):              # the old draw well on the north side of the square (2 tiles)
        m.put(*R(47, 35), z, 1930)
    cx_, cy_ = R(2, 52)                            # the Coach Yard gets its covered wagon (2 tiles)
    if all((cx_ + a, cy_ + 2, z) in m.ground and not m.items.get((cx_ + a, cy_ + 2, z)) for a in (5, 6)):
        m.put(cx_ + 6, cy_ + 2, z, 7906)
    # the notice board, beside the town sign in front of the Hearth
    nb = (62, 63)
    if not free(*nb):
        raise ValueError(f"the notice board's spot {nb} is taken")
    m.put(*R(*nb), z, NOTICE_BOARD)
    m.points["hearth_notice_board"] = R(*nb) + (z,)

    # ---- the open cobble: a few things in the bare places, never in a lane
    kinds = [TREE, TREE, BARRELS, CRATES, POTS, CART, "bench"]
    placed = []
    spots = sorted((x, y) for x in range(tx + 3, tx + tw - 3) for y in range(ty + 3, ty + th - 3))
    rng_spots = spots[:]
    rng.shuffle(rng_spots)
    for (x, y) in rng_spots:
        if len(placed) >= 22:
            break
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

    # ---- braziers at the four gates (P3b), just inside the wall either side of each gap
    mid_x, mid_y = tw // 2, th // 2
    for (x, y) in ((mid_x - 3, 1), (mid_x + 4, 1), (mid_x - 3, th - 2), (mid_x + 4, th - 2),
                   (1, mid_y - 2), (1, mid_y + 4), (tw - 2, mid_y - 2), (tw - 2, mid_y + 4)):
        if free(x, y):
            S.prop(m, *R(x, y), z, BRAZIER)
    return placed
