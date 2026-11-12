"""Dressing for dungeons, caves and arenas: natural caves, wall lamps, and decorations placed so they never block a
spawn, a teleport, a door or a corridor. Item rules were counted in Canary's hand-made map (2026-11-11)."""
import math

# Cave walls ("dirt wall"): the piece depends on which side the cave floor is.
CAVE_STRAIGHT = {"S": 5637, "N": 5631, "E": 5636, "W": 5630}
CAVE_INNER = {frozenset("ES"): 5648, frozenset("NW"): 5646, frozenset("NE"): 5650, frozenset("SW"): 5649}
CAVE_OUTER = {"SE": 5632, "SW": 5633, "NE": 5635, "NW": 5634}
CAVE_ROCK = 101                       # the dark earth under cave walls
DIRT_FLOOR = [351, 352, 353, 354, 355]

# hung on walls (north and west walls of a room are the ones you see from inside)
LAMP_H, LAMP_V = 2910, 2908           # lit wall lamps
CHAINS_H, CHAINS_V = 5483, 5482
TORCH_H, TORCH_V = 2941, 2931         # torch bearers fixed to a wall

# walkable clutter (never blocks anything)
BONES = [3114, 3132, 3115, 3116, 5018]
COBWEBS = [2699, 2700, 2701]
DEBRIS = [6475, 6482]
# solid decoration (only in open space)
PILLAR = 2152
PILLARS = [2152, 2263]
COAL_BASIN = 2113
STALAGMITES = [388, 389, 392, 393]
CRYSTALS = [7812, 7808]
RUBBLE = [5866, 5708]
THRONE = 2357

D8 = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]


def keep_clear(m, z, spawn_r=2):
    """Tiles that decoration must leave alone: named points, teleports, signs and the 3x3 around monster spawns."""
    out = set()
    for x, y, pz in m.points.values():
        if pz == z:
            out |= {(x + dx, y + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)}
    for _n, (x, y, pz), *_r in m.monsters:
        if pz == z:
            out |= {(x + dx, y + dy) for dx in range(-spawn_r, spawn_r + 1) for dy in range(-spawn_r, spawn_r + 1)}
    return out


def floor_free(m, x, y, z):
    p = (x, y, z)
    return p in m.ground and not m.items.get(p) and m.ground[p] not in (4597, 4609, 4610, CAVE_ROCK)


def open_space(m, x, y, z):
    """Free tile with free tiles all around: a solid thing here can never close a path."""
    return floor_free(m, x, y, z) and all(floor_free(m, x + dx, y + dy, z) for dx, dy in D8)


def scatter(m, x0, y0, w, h, z, kinds, n, solid=False, avoid=(), tries=40):
    rng = m.rng
    avoid = set(avoid)
    placed = 0
    for _ in range(n * tries):
        if placed >= n:
            break
        x, y = rng.randint(x0, x0 + w - 1), rng.randint(y0, y0 + h - 1)
        if (x, y) in avoid:
            continue
        if (open_space(m, x, y, z) if solid else floor_free(m, x, y, z)):
            m.put(x, y, z, rng.choice(kinds))
            placed += 1
    return placed


def hang(m, x0, y0, w, h, z, every=5, h_item=LAMP_H, v_item=LAMP_V, offset=2):
    """Hang lamps (or chains, torches) on the north and west walls of a room, every few tiles."""
    from mapgen import FAMILIES
    hs = {f["h"] for f in FAMILIES.values()}
    vs = {f["v"] for f in FAMILIES.values()}
    for x in range(x0 + offset, x0 + w - 1, every):
        if any(i in hs for i, _a in m.items.get((x, y0, z), [])):
            m.put(x, y0, z, h_item)
    for y in range(y0 + offset, y0 + h - 1, every):
        if any(i in vs for i, _a in m.items.get((x0, y, z), [])):
            m.put(x0, y, z, v_item)


def hang_maze(m, x0, y0, w, h, z, share=0.08, h_item=LAMP_H, v_item=LAMP_V):
    """Lamps on maze walls that face a corridor (a horizontal piece with floor south of it, a vertical one with floor
    east of it)."""
    from mapgen import FAMILIES
    hs = {f["h"] for f in FAMILIES.values()}
    vs = {f["v"] for f in FAMILIES.values()}
    rng = m.rng
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            ids = [i for i, _a in m.items.get((x, y, z), [])]
            if not ids or rng.random() > share:
                continue
            if ids[-1] in hs and floor_free(m, x, y + 1, z):
                m.put(x, y, z, h_item)
            elif ids[-1] in vs and floor_free(m, x + 1, y, z):
                m.put(x, y, z, v_item)


def blob(x0, y0, w, h, must, rng, fill=0.55, seed=0):
    """An organic cave shape inside the rectangle (one tile margin for the walls), always containing the `must` tiles
    and every tile connected to them; unconnected pockets are dropped."""
    def noise(x, y):
        a = seed * 1.3
        return (math.sin(x * 0.23 + a) + math.sin(y * 0.19 + a * 1.7) + math.sin((x + y) * 0.13 + a * 0.4)
                + math.sin((x - y) * 0.17 + a * 2.3)) / 4.0
    cx, cy = x0 + w / 2.0, y0 + h / 2.0
    cells = set()
    for y in range(y0 + 1, y0 + h - 1):
        for x in range(x0 + 1, x0 + w - 1):
            d = ((x - cx) / (w / 2.0)) ** 2 + ((y - cy) / (h / 2.0)) ** 2
            if noise(x, y) * 0.6 + (1.0 - d) * 1.1 > 1.0 - fill:
                cells.add((x, y))
    # carve a winding tunnel from each must tile to the middle so everything joins up
    for mx, my in must:
        x, y = mx, my
        while abs(x - int(cx)) + abs(y - int(cy)) > 1:
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if x0 < x + dx < x0 + w - 1 and y0 < y + dy < y0 + h - 1:
                        cells.add((x + dx, y + dy))
            if rng.random() < 0.6:
                x += (1 if cx > x else -1) if abs(cx - x) > 1 else 0
            else:
                y += (1 if cy > y else -1) if abs(cy - y) > 1 else 0
            if abs(cx - x) <= 1 and abs(cy - y) <= 1:
                break
    # keep only what is connected to the first must tile
    start = must[0]
    seen, stack = {start}, [start]
    while stack:
        x, y = stack.pop()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            q = (x + dx, y + dy)
            if q in cells and q not in seen:
                seen.add(q)
                stack.append(q)
    return seen


def cave(m, cells, z):
    """Lay a natural cave: dirt floor on `cells`, a ring of dirt-wall pieces around it chosen by where the floor is."""
    rng = m.rng
    cells = set(cells)
    for x, y in cells:
        m.ground[(x, y, z)] = rng.choice(DIRT_FLOOR)
        m.clear_items(x, y, z)
    ring = {(x + dx, y + dy) for x, y in cells for dx, dy in D8} - cells
    for x, y in ring:
        m.ground[(x, y, z)] = CAVE_ROCK
        m.clear_items(x, y, z)
        orth = {d for d, (dx, dy) in (("N", (0, -1)), ("E", (1, 0)), ("S", (0, 1)), ("W", (-1, 0))) if (x + dx, y + dy) in cells}
        if len(orth) == 1:
            piece = CAVE_STRAIGHT[next(iter(orth))]
        elif len(orth) == 2 and frozenset(orth) in CAVE_INNER:
            piece = CAVE_INNER[frozenset(orth)]
        elif not orth:
            diag = [d for d, (dx, dy) in (("NW", (-1, -1)), ("NE", (1, -1)), ("SE", (1, 1)), ("SW", (-1, 1))) if (x + dx, y + dy) in cells]
            piece = CAVE_OUTER[diag[0]] if diag else None
        else:                             # floor on opposite or three sides (a thin rock spur): a straight piece
            piece = CAVE_STRAIGHT["S" if "S" in orth else "N" if "N" in orth else "E"]
        if piece:
            m.put(x, y, z, piece)


def flagstones(m, x0, y0, w, h, z, ground_id):
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            if (x, y, z) in m.ground:
                m.ground[(x, y, z)] = ground_id


def carpet_path(m, x0, y0, w, h, z, iid=2576, avoid=()):
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            if (x, y) not in avoid and (x, y, z) in m.ground and not any(
                    i not in (iid,) for i, _a in m.items.get((x, y, z), [])):
                m.items.setdefault((x, y, z), []).insert(0, (iid, b""))
