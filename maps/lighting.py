"""Night lighting for Floor 1 (Jay, 2026-11-27): "all pathways (roads) and everything in the city should be well lit and
visible even at night. ... we had a 'lower class or poor' section of the city. its fine if its not lit as well as the
rest of the city. put some torches in dungeons, and make some completely dark. players have light spells, torches, and
sources of light to illuminate the areas they want to see better in."

What this does (run by tools/mapgen.py once Floor 1 is built, before Map.finish):
  * Every road and street tile must lie within a few tiles of a light. Where one does not, a lit lamp post goes on the
    verge beside it (the free tile that covers the most dark road), never on the road, never in a building, never next
    to a door, never in a gap between two solid things (it would close the way), never next to another lamp.
  * Hearthgate's streets and plaza: a light within 3 tiles of every tile (bright).
  * Lantern Row, the poor quarter in the south-west (cheap houses, tight lanes, the Old Well Yard): within 6 (dim,
    pools of light with darker gaps between).
  * Floor 1's roads, village lanes and gate trails outside the walled hunting grounds: within 4. Not the hunting grounds
    themselves (the challenge stays), and not the stretch of the Millcross road whose lanterns the Town Works lights (a
    lamp post there would spoil that deed).
  * Dungeons (Claude's call, Jay can veto): the starter and early caves, boss halls, story rooms and the Underkeep keep
    their wall torches; the deeper caves in DARK are pitch black (no torch, lamp or fire basin at all). Their hub signs
    say so, so nobody walks in without a light by surprise.
"""
from __future__ import annotations

import hearthgate_plan as HP
import scenery as S

LAMP_POST = 8660
WALL_LAMP_H, WALL_LAMP_V = 2910, 2908                # lit wall lamps (on a horizontal / vertical wall piece)
# brightness of the lights our builders place (read from appearances.dat: street lamp 7, wall lamps and torch bearers 6,
# coal basin 8, campfire). Fixed here so the map comes out the same with or without the client files.
LIGHT = {8660: 7, 2910: 6, 2908: 6, 2941: 6, 2931: 6, 2113: 8, 2117: 7, 1996: 7}
DARK_ONLY = {2910, 2908, 2941, 2931, 2113, 2117}    # what a dark level must not have (decorative lights only)
LAMP_UNLIT = 8659                                  # the Road Lanterns deed (maps/floor1_features.py)

REACH_TOWN, REACH_POOR, REACH_ROAD = 3, 6, 4

# hunting grounds whose lower levels are pitch dark (the deeper ones, levels 17-30): bring a light
DARK = {
    "shard_fields": "Shard Grotto",
    "old_quarry": "The Lower Works",
    "fallen_bastion": "The Bastion Cellars",
}
DARK_SIGN = "Below is pitch dark: no torches. Bring a light."


def _door_ids():
    from mapgen import FAMILIES
    out = {v for f in FAMILIES.values() for k, v in f.items() if k.startswith("door") and v}
    try:
        from mapgen import OPEN_DOOR
        out |= {v for v in OPEN_DOOR.values() if isinstance(v, int)}
    except ImportError:
        pass
    return out


def _lights(m, z):
    return {(x, y) for (x, y, zz), items in m.items.items() if zz == z and any(i in LIGHT for i, _a in items)}


def light_paths(m, tiles, z, reach, banned=frozenset(), doors=frozenset()):
    """Put lamp posts beside the path tiles (a set of (x, y)) so each lies within `reach` tiles of a light. Returns the
    number of lamps placed."""
    lights = _lights(m, z)
    tiles = set(tiles)
    inb = set()                                           # inside a building (walls included): never
    for bd in m.buildings:
        if bd["z"] <= z <= bd.get("top", bd["z"]):
            bx, by, bw, bh = bd["rect"]
            inb |= {(x, y) for x in range(bx, bx + bw) for y in range(by, by + bh)}
    banned = set(banned) | inb

    def lit(t):
        return any(max(abs(t[0] - a), abs(t[1] - b)) <= reach for a, b in near(t, reach))

    grid = {}

    def add(p):
        lights.add(p)
        grid.setdefault((p[0] // 16, p[1] // 16), []).append(p)

    for p in list(lights):
        grid.setdefault((p[0] // 16, p[1] // 16), []).append(p)

    def near(t, r):
        for gx in range((t[0] - r) // 16, (t[0] + r) // 16 + 1):
            for gy in range((t[1] - r) // 16, (t[1] + r) // 16 + 1):
                yield from grid.get((gx, gy), ())

    def blocked(x, y):
        return (x, y, z) not in m.ground or bool(m.items.get((x, y, z))) or (x, y) in lights

    def ok(x, y):
        if (x, y) in tiles or (x, y) in banned or not S.free(m, x, y, z):
            return False
        if not any((x + a, y + b) in tiles for a in (-1, 0, 1) for b in (-1, 0, 1)):
            return False                                  # only on the verge, right beside the path
        for a in (-1, 0, 1):
            for b in (-1, 0, 1):
                q = (x + a, y + b, z)
                if (q[0], q[1]) in lights or any(i in doors for i, _a in m.items.get(q, [])):
                    return False
        if (blocked(x, y - 1) and blocked(x, y + 1)) or (blocked(x - 1, y) and blocked(x + 1, y)):
            return False                                  # a gap between two solid things: a lamp would close it
        return True

    placed = 0
    for t in sorted(tiles, key=lambda p: (p[1], p[0])):
        if lit(t):
            continue
        best, score = None, 0
        for a in range(-reach, reach + 1):
            for b in range(-reach, reach + 1):
                x, y = t[0] + a, t[1] + b
                if not ok(x, y):
                    continue
                s = sum(1 for u in range(-reach, reach + 1) for v in range(-reach, reach + 1)
                        if (x + u, y + v) in tiles and not lit((x + u, y + v)))
                s = s * 100 - (abs(a) + abs(b))           # cover the most dark road; ties: the spot nearest the gap
                if best is None or s > score:
                    best, score = (x, y), s
        if best:
            m.put(best[0], best[1], z, LAMP_POST)
            add(best)
            placed += 1
    # where no post fits (a street squeezed between buildings): a lamp on a wall that faces the street. Seen from
    # outside only on a south wall (street below it) or an east wall (street right of it), and only on a plain piece
    # (never a window, corner or door), as the house door lamps do (maps/hearthgate_dress.py)
    from mapgen import FAMILIES
    plain_h = {f["h"] for f in FAMILIES.values()}
    plain_v = {f["v"] for f in FAMILIES.values()}
    for t in sorted(tiles, key=lambda p: (p[1], p[0])):
        if lit(t):
            continue
        best = None
        for r in range(1, reach + 1):
            for a in range(-r, r + 1):
                for (x, y, kind, face) in ((t[0] + a, t[1] - r, "h", (0, 1)), (t[0] - r, t[1] + a, "v", (1, 0))):
                    have = [i for i, _a in m.items.get((x, y, z), [])]
                    if not have or have[-1] not in (plain_h if kind == "h" else plain_v) or (x, y) in lights:
                        continue
                    if (x + face[0], y + face[1]) not in tiles and not S.free(m, x + face[0], y + face[1], z):
                        continue
                    if any(max(abs(x - u), abs(y - v)) < 3 for u, v in near((x, y), 3)):
                        continue
                    best = (x, y, kind)
                    break
                if best:
                    break
            if best:
                break
        if best:
            m.put(best[0], best[1], z, WALL_LAMP_H if best[2] == "h" else WALL_LAMP_V)
            add(best[:2])
            placed += 1
    left = sorted(t for t in tiles if not lit(t))
    m.dark_left = getattr(m, "dark_left", []) + [(x, y, z) for (x, y) in left]
    return placed


def light_town(m, tx, ty, Z):
    """Hearthgate's streets and plaza bright, Lantern Row dim."""
    inside, _w = HP.hearth_tiles()
    streets = {(x, y) for (r, _g) in HP.STREETS.values() for x in range(r[0], r[0] + r[2]) for y in range(r[1], r[1] + r[3])}
    plaza = {(x, y) for x in range(HP.W) for y in range(HP.H) if HP.in_plaza(x, y) and (x, y) not in inside}
    paths = streets | plaza
    poor = {(x, y) for (x, y) in paths if poor_quarter(x, y)}
    hall = {(tx + x, ty + y) for (x, y) in inside}
    doors = _door_ids()
    n_main = light_paths(m, {(tx + x, ty + y) for (x, y) in paths - poor}, Z, REACH_TOWN, banned=hall, doors=doors)
    n_poor = light_paths(m, {(tx + x, ty + y) for (x, y) in poor}, Z, REACH_POOR, banned=hall, doors=doors)
    return n_main, n_poor


def poor_quarter(x, y):
    """Lantern Row and the Old Well Yard (town coordinates): the south-west corner inside the wall."""
    return 1 <= x <= 30 and 51 <= y <= 80


def light_roads(m, bounds, town_rect, z_top=7):
    """Floor 1's roads and trails at the surface, outside the town and the walled hunting grounds."""
    x0, y0, w, h = bounds
    tx, ty, tw, th = town_rect
    grounds = set()
    for L in getattr(m, "wilds", []):
        if L["c"].get("floor", 1) == 1:
            grounds |= L["rect"]
    doors = _door_ids()
    total = 0
    for z in sorted({t[2] for t in m.road_tiles if t[2] <= z_top}):
        deed = [(x, y) for (x, y, zz), items in m.items.items() if zz == z and any(i == LAMP_UNLIT for i, _a in items)]
        tiles = {(x, y) for (x, y, zz) in m.road_tiles if zz == z
                 and x0 <= x < x0 + w and y0 <= y < y0 + h
                 and not (tx <= x < tx + tw and ty <= y < ty + th)
                 and (x, y) not in grounds
                 and not any(max(abs(x - a), abs(y - b)) <= 8 for a, b in deed)}
        total += light_paths(m, tiles, z, REACH_ROAD, banned=grounds, doors=doors)
    return total


def darken(m):
    """The DARK grounds' lower levels: no decorative light at all. Returns the number of lights taken out."""
    n = 0
    for L in getattr(m, "wilds", []):
        if L["id"] not in DARK:
            continue
        for z, cells in L["levels"].items():
            if z <= 7:
                continue
            xs = [t[0] for t in L["boxes"][z]]
            ys = [t[1] for t in L["boxes"][z]]
            for x in range(min(xs) - 1, max(xs) + 2):
                for y in range(min(ys) - 1, max(ys) + 2):
                    items = m.items.get((x, y, z))
                    if items and any(i in DARK_ONLY for i, _a in items):
                        m.items[(x, y, z)] = [(i, a) for i, a in items if i not in DARK_ONLY]
                        n += 1
    return n


def check(m):
    """Problems for the walk test: a light left in a dark level."""
    out = []
    for L in getattr(m, "wilds", []):
        if L["id"] in DARK:
            for z in L["levels"]:
                if z > 7:
                    for (x, y) in L["levels"][z]:
                        if any(i in DARK_ONLY for i, _a in m.items.get((x, y, z), [])):
                            out.append(f"lighting: a light in the dark level {DARK[L['id']]} at {x},{y},{z}")
    return out


def build(m, bounds, town, Z=7):
    """Floor 1's night lighting. bounds = (x0, y0, w, h) of the floor, town = (tx, ty) of Hearthgate's corner."""
    tx, ty = town
    dark = darken(m)
    from floor1_features import _hub_line
    for L in getattr(m, "wilds", []):
        if L["id"] in DARK and any(z > 7 for z in L["levels"]):
            _hub_line(m, L, DARK_SIGN)
    n_main, n_poor = light_town(m, tx, ty, Z)
    n_road = light_roads(m, bounds, (tx, ty, HP.W, HP.H))
    print(f"lighting: {n_main} lamp posts in Hearthgate, {n_poor} in Lantern Row, {n_road} along the roads; "
          f"{dark} lights taken out of the dark caves; {len(getattr(m, 'dark_left', []))} path tiles left unlit")
