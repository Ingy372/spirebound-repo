"""Scenery helpers for the map builders: natural-looking groves, ponds, ground patches, props and carpets.
Item ids were chosen by looking at the sprites (tools/spriteview.py, tools/maprender.py)."""
import math

TREES_BROAD = [3617, 3619, 3625, 957]
TREES_FIR = [3614, 3682]
TREES_DEAD = [3623, 3624, 958]
BUSHES = [3681, 3699, 3700]
THORNS = [3703, 3704, 3705, 3706]
FLOWERS = [102, 6225, 6226, 6227, 6228, 6229, 6230, 3656]
FERNS = [3737, 3751, 3754]
STONES = [1780, 1781, 1782]                     # small single-tile stones
BOULDERS = [1783]                               # a big 2x2 rock: the map builder adds its other three pieces
GRASS_IDS = {4526, 4515, 4517, 4518, 4519, 4520, 4521, 4522, 106}


def noise(x, y, seed=0):
    """Smooth pseudo-random value in 0..1 (sum of a few sine waves): gives clumps instead of uniform sprinkling."""
    a = seed * 1.7
    v = (math.sin(x * 0.11 + a) + math.sin(y * 0.13 + a * 1.3) + math.sin((x + y) * 0.07 + a * 0.6) + math.sin((x - y) * 0.09 + a * 2.1))
    return (v + 4) / 8.0


def free(m, x, y, z):
    """A tile with plain walkable ground and nothing standing on it."""
    return (x, y, z) in m.ground and (x, y, z) not in m.items and m.ground[(x, y, z)] not in (4597, 4609, 4610)


def sprinkle(m, x0, y0, w, h, z, kinds, density, seed=0, lo=0.0, grass_only=True, on_dirt=False):
    """Place items from `kinds` at the given density, only where noise() >= lo (use lo ~0.55 for clumps).
    Never on roads and streets unless on_dirt=True (for dirt-covered hunting grounds)."""
    rng = m.rng
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            if not free(m, x, y, z):
                continue
            if grass_only and m.ground[(x, y, z)] not in GRASS_IDS and not (on_dirt and m.ground[(x, y, z)] == 103):
                continue
            if noise(x, y, seed) >= lo and rng.random() < density:
                m.put(x, y, z, rng.choice(kinds))


def patch(m, cx, cy, rx, ry, z, key, wobble=0.25):
    """An irregular ellipse of ground (dirt, mud, gravel, water...)."""
    rng = m.rng
    for y in range(cy - ry - 1, cy + ry + 2):
        for x in range(cx - rx - 1, cx + rx + 2):
            d = ((x - cx) / max(rx, 1)) ** 2 + ((y - cy) / max(ry, 1)) ** 2
            if d <= 1.0 + (rng.random() - 0.5) * wobble and (x, y, z) in m.ground:
                # paint under objects too (a grass square left under a rock looks unfinished); never under walls,
                # and water drowns whatever natural thing stood there
                its = [i for i, _a in m.items.get((x, y, z), [])]
                if _solid(its):
                    continue
                if its and key == "water":
                    m.clear_items(x, y, z)
                m.ground[(x, y, z)] = m.pick(key)


def _solid(ids):
    """Walls, furniture, signs and other placed things keep their ground; only natural things get painted under."""
    return any(i not in SCENERY for i in ids)


def pond(m, cx, cy, rx, ry, z, ring="mud"):
    patch(m, cx, cy, rx + 2, ry + 2, z, ring, wobble=0.5)
    patch(m, cx, cy, rx, ry, z, "water", wobble=0.3)


def carpet(m, x0, y0, w, h, z, iid=2576):
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            if (x, y, z) in m.ground and not m.blocked(x, y, z):
                m.items.setdefault((x, y, z), []).insert(0, (iid, b""))


def prop(m, x, y, z, iid):
    if (x, y, z) in m.ground:
        m.put(x, y, z, iid)


def replace(m, x, y, z, iid):
    m.clear_items(x, y, z)
    prop(m, x, y, z, iid)


def counter(m, x, y, w, z, vertical=False):
    """A shop counter: wooden counter pieces in a row (horizontal 2317/2318, vertical 2320/2321)."""
    a, b = (2320, 2321) if vertical else (2317, 2318)
    for i in range(w):
        prop(m, x + (0 if vertical else i), y + (i if vertical else 0), z, a if i % 2 == 0 else b)


def lamp(m, x, y, z):
    prop(m, x, y, z, 8659)


def bridge(m, x0, y0, w, h, z):
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            if (x, y, z) in m.ground:
                m.ground[(x, y, z)] = 408
                m.clear_items(x, y, z)


SCENERY = set(TREES_BROAD + TREES_FIR + TREES_DEAD + BUSHES + THORNS + FLOWERS + FERNS + STONES + BOULDERS + [1784, 1785, 1786, 2264, 2290, 3605, 7957, 1822])


def ruin(m, x0, y0, w, h, z, style="stone"):
    """A broken building: a wall ring with many pieces missing, rubble and a fallen pillar inside."""
    from mapgen import FAMILIES
    rng = m.rng
    m.fill(x0, y0, w, h, z, "pave")
    # the wall outline with whole stretches missing (breaks of 1-3 tiles, rubble lying in them); every piece left
    # standing is chosen from its neighbours, so each stretch ends cleanly instead of looking half-built
    ring = [(x, y0) for x in range(x0, x0 + w)] + [(x0 + w - 1, y) for y in range(y0 + 1, y0 + h)]
    ring += [(x, y0 + h - 1) for x in range(x0 + w - 2, x0 - 1, -1)] + [(x0, y) for y in range(y0 + h - 2, y0, -1)]
    keep, gap = [], 0
    for t in ring:
        if gap > 0:
            gap -= 1
            if rng.random() < 0.5:
                prop(m, t[0], t[1], z, 1822)
            continue
        if rng.random() < 0.18:
            gap = rng.randint(0, 2)
            prop(m, t[0], t[1], z, 1822)
            continue
        keep.append(t)
    m.autowall(keep, z, style)
    for _ in range(max(3, w * h // 14)):
        prop(m, x0 + rng.randint(1, w - 2), y0 + rng.randint(1, h - 2), z, rng.choice([1822, 1822, 1783, 2264, 2290, 3737]))


def standing_stones(m, cx, cy, z, n=8, radius=5):
    patch(m, cx, cy, radius + 2, radius + 2, z, "dirt", wobble=0.6)      # ground first, so no grass shows under a stone
    for i in range(n):
        a = 2 * math.pi * i / n
        prop(m, cx + int(round(radius * math.cos(a))), cy + int(round(radius * math.sin(a))), z, 2152 if i % 2 == 0 else 2263)
    prop(m, cx, cy, z, 1996)


def forest(m, x0, y0, w, h, z, keep=(), thresh=0.6, density=0.5, seed=7, cell=4):
    """Forest masses between the places people go. Trees only where noise() is high, never near roads, buildings, camps,
    NPCs or points of interest (a clear buffer of about 8 tiles)."""
    rng = m.rng
    blocked = set()
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            g = m.ground.get((x, y, z))
            items = m.items.get((x, y, z), [])
            if g is None or g not in GRASS_IDS or any(i not in SCENERY for i, _a in items):
                blocked.add((x // cell, y // cell))
    for px, py, pz in keep:
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                blocked.add((px // cell + dx, py // cell + dy))
    dilated = set()
    for cx, cy in blocked:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                dilated.add((cx + dx, cy + dy))
    kinds = TREES_FIR + TREES_BROAD + TREES_BROAD
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            if (x // cell, y // cell) in dilated or not free(m, x, y, z):
                continue
            if noise(x * 0.5, y * 0.5, seed) >= thresh and rng.random() < density:
                m.put(x, y, z, rng.choice(kinds))
