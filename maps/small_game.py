"""Small game on Floor 1's empty lawns (Jay, 2026-11-26, Q94: "fill in the empty land with small game monsters to help
it feel less empty"; DESIGN.md 3.4b).

Harmless creatures that run from you (tools/gen_monsters.py: Meadow Hare, Dapple Fawn, Thistle Hen, Acorn Squirrel),
in ones and twos, spread over every open stretch of grass that is far from the towns, the roads, the hunting grounds
and their gates, and from every other spawn. Same spots every build (no randomness that depends on other code).
"""
from floor1_plan import spawn_time

KINDS = [("Meadow Hare", 2), ("Dapple Fawn", 1), ("Thistle Hen", 2), ("Acorn Squirrel", 1)]
SPOTS = 40                 # how many places get a creature or two
GAP = 16                   # tiles between two small-game places
AWAY_GROUND = 10           # from any walled ground, town or village
AWAY_SPAWN = 12            # from any other monster spawn (and so from every gate's quiet zone)
AWAY_ROAD = 3
RESPAWN = 90


def place(m, x0, y0, size, z, blocked_rects):
    roads = getattr(m, "road_tiles", set())
    road_xy = {(x, y) for x, y, zz in roads if zz == z}
    spawns = [(p[0], p[1]) for _n, p, *_r in m.monsters if p[2] == z]
    points = [(p[0], p[1]) for p in m.points.values() if p[2] == z]

    def far_from_rects(x, y):
        return all(not (rx - AWAY_GROUND <= x < rx + rw + AWAY_GROUND and ry - AWAY_GROUND <= y < ry + rh + AWAY_GROUND)
                   for rx, ry, rw, rh in blocked_rects)

    from mapgen import ID
    grass = set(ID["grass"])
    cands = []
    for y in range(y0 + 8, y0 + size - 8, 2):
        for x in range(x0 + 8, x0 + size - 8, 2):
            g = m.ground.get((x, y, z))
            if g is None or m.items.get((x, y, z)) or g not in grass:
                continue
            if not far_from_rects(x, y):
                continue
            if any((x + a, y + b) in road_xy for a in range(-AWAY_ROAD, AWAY_ROAD + 1) for b in range(-AWAY_ROAD, AWAY_ROAD + 1)):
                continue
            if any(max(abs(x - a), abs(y - b)) < AWAY_SPAWN for a, b in spawns + points):
                continue
            # room for the creatures to stand: the 3 x 3 round the spot is open ground
            if not all((x + a, y + b, z) in m.ground and not m.items.get((x + a, y + b, z)) for a in (-1, 0, 1) for b in (-1, 0, 1)):
                continue
            cands.append((x, y))
    picked = []
    far = spawns[:]
    while len(picked) < SPOTS and cands:
        best = max(cands, key=lambda t: (min([max(abs(t[0] - p[0]), abs(t[1] - p[1])) for p in far] or [999]), t))
        if far and min(max(abs(best[0] - p[0]), abs(best[1] - p[1])) for p in far) < GAP:
            break
        picked.append(best)
        far.append(best)
        cands.remove(best)
    for i, (x, y) in enumerate(picked):
        name, most = KINDS[i % len(KINDS)]
        n = 1 + (i // len(KINDS)) % most
        kids = [(name, dx, 0, spawn_time(RESPAWN)) for dx in range(n)]
        m.monsters.append((kids, (x, y, z), 3, n, spawn_time(RESPAWN)))
    m.small_game = picked
    return picked
