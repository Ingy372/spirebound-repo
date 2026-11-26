"""Designed hunting grounds (FLOOR1_HUNTING_PLAN.md Part 6).

A designed ground is drawn from a hand-written list in maps/floor1_plan.py (DESIGNS): clearings and paths on several
levels joined by stairs. Monsters stand in the clearings, spread out and layered calm (near the gate) -> middle -> deep,
so a player meets a few at a time. The surface keeps the walled ground of maps/wilds.py (outer wall, one gate); lower
levels are natural caves. tools/hunt_check.py measures how many monsters can reach a player on every tile.

Level kinds: the surface (z 7); a hill top above it (z 6: a raised plateau on mountain ground, reached by ramps,
Map.hill / Map.ramp); caves below (z 8, 9); and at most one party cave (a level marked party=True: groups of four, the
cavebot rule, the den_<id> points and tools/hunt_check.py's party limits).
Built places (H8, 2026-11-25): a lower level marked built=True is dug as a stone-walled cellar or mine (stone floor,
Map.autowall stone walls, wall torches, rubble and pillars) instead of a natural cave; the surface may list ruins
[(x, y, w, h, gaps)]: roofless broken stone buildings (outline by Map.autowall, gaps = doorways, some stretches fallen),
each standing in a clearing that is widened to fit it.

build(m, c) paints it; check(m) is its walk test (gate -> every level -> every group and crowd spot).
"""
import random

import dungeon as DG
import wilds as WI
from floor1_plan import CAVE_RESPAWN, DESIGNS, den_level
from mapgen import RAMPS

X0, Y0, Z = WI.X0, WI.Y0, WI.Z
D4, D8 = WI.D4, WI.D8
HOLE = 385                       # outdoors the way down is a stone-rimmed hole


def _blobby(cx, cy, r, rng):
    """A clearing: a disc of radius r with a slightly ragged edge."""
    out = set()
    for x in range(cx - r - 1, cx + r + 2):
        for y in range(cy - r - 1, cy + r + 2):
            dist = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
            if dist <= r - 0.5 or (dist <= r + 0.8 and rng.random() < 0.55):
                out.add((x, y))
    return out


def _gate(c, d):
    """The 3-wide, 2-deep gap in the outer wall, and the tile just inside it, for a gate on any side."""
    ox, oy = X0 + c["x"], Y0 + c["y"]
    gx, gy = ox + d["gate"][0], oy + d["gate"][1]
    side = c["gate"]
    if side == "s":
        return {(gx + a, oy + c["h"] - 1 - b) for a in (-1, 0, 1) for b in (0, 1)}, (gx, oy + c["h"] - 2)
    if side == "n":
        return {(gx + a, oy + b) for a in (-1, 0, 1) for b in (0, 1)}, (gx, oy + 1)
    if side == "w":
        return {(ox + b, gy + a) for a in (-1, 0, 1) for b in (0, 1)}, (ox + 1, gy)
    return {(ox + c["w"] - 1 - b, gy + a) for a in (-1, 0, 1) for b in (0, 1)}, (ox + c["w"] - 2, gy)


def _ramp_tiles(d, ox, oy, z_low):
    """For each ramp up from level z_low: (ramp tiles, foot tiles, approach tiles, hill landing tiles), world coords."""
    out = []
    for link in d["links"]:
        if link[0] != "ramp" or link[3] != z_low:
            continue
        _k, x, y, _z, facing = link
        fdy = RAMPS[facing][2]
        wx, wy = ox + x, oy + y
        ramp = {(wx, wy), (wx + 1, wy)}
        foot = {(wx, wy + fdy), (wx + 1, wy + fdy)}
        approach = {(wx + i, wy + fdy * k) for i in (0, 1) for k in range(1, 9)}
        landing = {(wx, wy - fdy), (wx + 1, wy - fdy)}
        out.append((ramp, foot, approach, landing))
    return out


def _carve(c, d, z, lv, rng, below=None):
    """The open tiles of one level, and its named clearing centres (world coordinates). `below`: the open tiles of the
    surface, for a hill level (its top keeps clear of them, so the rock faces of the valleys stand under its rim)."""
    ox, oy = X0 + c["x"], Y0 + c["y"]
    bx, by, bw, bh = lv["box"]
    box = {(ox + bx + u, oy + by + v) for u in range(bw) for v in range(bh)}
    if z == Z:                                       # nothing open within the 2-tile outer wall
        inner = {(ox + u, oy + v) for u in range(2, c["w"] - 2) for v in range(2, c["h"] - 2)}
    else:                                            # one tile of rock round the edge of the level's box
        inner = {(ox + bx + u, oy + by + v) for u in range(1, bw - 1) for v in range(1, bh - 1)}
    named, cells = {}, set()
    for (name, x, y, r, band, route, content) in lv["clearings"]:
        wx, wy = ox + x, oy + y
        named[name] = (wx, wy)
        if content == "hub":
            cells |= {(wx + a, wy + b) for a in range(-r, r + 1) for b in range(-r + 1, r + 1)}
        else:
            cells |= _blobby(wx, wy, r, rng)
    for a, b, w in lv["paths"]:
        cells |= WI._tunnel(named[a], named[b], rng, width=w)
    for (rx, ry, rw, rh, _gaps) in lv.get("ruins", []):   # a ruin and one tile of open ground round it
        cells |= {(ox + rx + u, oy + ry + v) for u in range(-1, rw + 1) for v in range(-1, rh + 1)}
    for (name, x, y, r, band, route, content) in lv["clearings"]:
        if content == "crowd":                       # a crowd pocket: a short side passage to the nearest clearing
            p = named[name]
            near = min((q for n_, q in named.items() if n_ != name and q != p),
                       key=lambda q: (q[0] - p[0]) ** 2 + (q[1] - p[1]) ** 2)
            cells |= WI._tunnel(p, near, rng, width=2)
    gate = set()
    if z == Z:
        gate, first = _gate(c, d)
        cells |= WI._tunnel(first, named["hub"], rng, width=3, wiggle=False)
        for ramp, _foot, approach, _land in _ramp_tiles(d, ox, oy, Z):
            cells |= ramp | approach                 # a straight 2-wide way up to each ramp
    cells = (cells & inner) | gate
    if z < Z and below is not None:
        # a hill: fill its little bays so it reads as one raised mass, then keep its top 2 tiles clear of the valleys
        # (one tile of rock face, then mountain under the rim), except at the ramps
        for _ in range(2):
            cells |= {t for t in inner if t not in cells and sum((t[0] + a, t[1] + b) in cells for a, b in D8) >= 5}
        ramps = _ramp_tiles(d, ox, oy, z + 1)
        rtiles = set().union(*[r for r, _f, _a, _l in ramps]) if ramps else set()
        valley = below - rtiles
        cells = {t for t in cells if t not in rtiles and not any((t[0] + a, t[1] + b) in valley for a, b in D8 + ((0, 0),))}
        for _r, _f, _a, landing in ramps:
            cells |= landing
    return cells, named, box, gate


def _ruins(m, c, ruins, cells7, rng, L, props=()):
    """Roofless broken stone buildings on the surface: the outline is Map.autowall stone, minus the doorways and a few
    fallen stretches; inside, cracked stone floor with the trail showing through. The wall tiles leave the open set."""
    ox, oy = X0 + c["x"], Y0 + c["y"]
    allw = set()
    for (rx, ry, rw, rh, gaps) in ruins:
        x0, y0, x1, y1 = ox + rx, oy + ry, ox + rx + rw - 1, oy + ry + rh - 1
        gap = {(ox + gx, oy + gy) for gx, gy in gaps}
        ring = [(x, y0) for x in range(x0, x1 + 1)] + [(x1, y) for y in range(y0 + 1, y1 + 1)] +                [(x, y1) for x in range(x1 - 1, x0 - 1, -1)] + [(x0, y) for y in range(y1 - 1, y0, -1)]
        corners = {(x0, y0), (x1, y0), (x0, y1), (x1, y1)}
        fallen, k = set(), 0
        while k < len(ring):                      # now and then a 1-2 tile stretch has fallen (never a corner)
            if ring[k] not in corners and rng.random() < 0.12:
                fallen |= set(ring[k:k + rng.choice((1, 2))]) - corners
                k += 4
            k += 1
        wall = [t for t in ring if t not in gap and t not in fallen]
        for (x, y) in {(x, y) for x in range(x0 + 1, x1) for y in range(y0 + 1, y1)} | gap | fallen:
            m.clear_items(x, y, Z)
            if rng.random() < 0.85:
                m.ground[(x, y, Z)] = m.pick("stonefloor")
        for (x, y) in fallen:                     # the fallen stones lie where the wall stood
            if rng.random() < 0.6:
                m.put(x, y, Z, rng.choice(WI.WALKOVER["gravel"]))
        for (x, y) in wall:
            m.clear_items(x, y, Z)
            m.ground[(x, y, Z)] = m.pick("stonefloor")
        m.autowall(wall, Z, "stone")
        allw |= set(wall)
        if props:                                 # a barrel, a crate or a heap of rubble in two inside corners (never by a door)
            inside = [(x0 + 1, y0 + 1), (x1 - 1, y0 + 1), (x0 + 1, y1 - 1), (x1 - 1, y1 - 1)]
            for (x, y) in rng.sample(inside, 2):
                if not any(abs(x - gx) + abs(y - gy) <= 1 for gx, gy in gap):
                    m.put(x, y, Z, rng.choice(props))
                    allw.add((x, y))
    cells7.difference_update(allw)
    L["ruin_walls"] = allw


def build(m, c):
    d = DESIGNS[c["design"]]
    rng = random.Random(sum(map(ord, c["id"])) * 104729)
    ox, oy = X0 + c["x"], Y0 + c["y"]
    rect = {(ox + u, oy + v) for u in range(c["w"]) for v in range(c["h"])}
    gid, (lo, hi) = c["id"], c["levels"]
    L = dict(id=gid, c=c, rect=rect, loops=[], routes={}, levels={}, boxes={}, clearings={}, landings=[], design=True)
    lv_cells = {}
    order = sorted(d["levels"], key=lambda z: (z != Z, z))      # the surface first: a hill keeps clear of its valleys
    for z in order:
        lv = d["levels"][z]
        cells, named, box, gate = _carve(c, d, z, lv, rng, below=lv_cells[Z][0] if z < Z else None)
        if z != Z:
            used = [t for t in box if (t[0], t[1], z) in m.ground]
            if used:
                raise ValueError(f"{gid}: level {z} would dig into something already there at {used[0]}")
        lv_cells[z] = (cells, named, box)
        if z == Z:
            L["gate"] = gate
            hx, hy = named["hub"]
            L["hub"] = {(hx + a, hy + b) for a in range(-4, 5) for b in range(-3, 5)} & cells
    # ---- the surface: wall material everywhere, then the open ground
    cells7, named7, _b = lv_cells[Z]
    for (x, y) in rect:
        m.ground[(x, y, Z)] = m.pick("grass")
        m.clear_items(x, y, Z)
    WI._mass(m, rect - cells7, rect, WI.SOLID[c["wall"]], rng)
    trail = WI.TRAIL_GROUND[c["trail"]]
    for (x, y) in cells7:
        m.ground[(x, y, Z)] = m.pick(trail)
        m.clear_items(x, y, Z)
    ramp_keep = set()
    for r, f, _a, _l in _ramp_tiles(d, ox, oy, Z):
        ramp_keep |= r | f
    for t in cells7:
        if t not in L["hub"] and t not in L["gate"] and t not in ramp_keep \
                and any((t[0] + a, t[1] + b) not in cells7 for a, b in D4) and rng.random() < 0.08:
            m.put(t[0], t[1], Z, rng.choice(WI.WALKOVER[trail]))
    _ruins(m, c, d["levels"][Z].get("ruins", []), cells7, rng, L, d["levels"][Z].get("ruin_props", []))
    L["open"] = cells7
    # ---- ponds (plan Part 5, Toad Pond): water over the wall mass; where a path crosses a pond it becomes a bridge
    inner7 = {(ox + u, oy + v) for u in range(2, c["w"] - 2) for v in range(2, c["h"] - 2)}
    for (px, py, pr) in d["levels"][Z].get("ponds", []):
        pond = _blobby(ox + px, oy + py, pr, rng) & inner7
        island = set()                                 # a clearing in the middle of a pond stays dry land
        for (_n, cx, cy, cr, _b, _r, _c) in d["levels"][Z]["clearings"]:
            if (ox + cx, oy + cy) in pond:
                island |= {(ox + cx + u, oy + cy + v) for u in range(-cr - 1, cr + 2) for v in range(-cr - 1, cr + 2) if u * u + v * v <= (cr + 1) ** 2}
        for t in sorted(pond):
            m.clear_items(t[0], t[1], Z)
            deep_in = sum((t[0] + u, t[1] + v) in pond for u, v in D8) >= 6
            if t in island or (t in cells7 and not deep_in):     # a path that only clips the edge stays on land
                m.ground[(t[0], t[1], Z)] = m.pick(trail)
            else:
                m.ground[(t[0], t[1], Z)] = 408 if t in cells7 else m.pick("water")
        banks = L.setdefault("banks", set())          # a grass bank round the water (painted after the groups stand)
        banks |= {(x + u, y + v) for (x, y) in pond for u in (-1, 0, 1) for v in (-1, 0, 1)} - pond - cells7
    # ---- a ring of old trees round a way down (Sproutling Glade's great tree), open to the south
    for (tx, ty) in d["levels"][Z].get("tree_rings", []):
        wx, wy = ox + tx, oy + ty
        for a in range(-2, 3):
            for b in range(-2, 3):
                if max(abs(a), abs(b)) == 2 and not (b == 2 and abs(a) <= 1):
                    m.clear_items(wx + a, wy + b, Z)
                    m.put(wx + a, wy + b, Z, rng.choice(WI.TREES_ALL_BROAD))
    # ---- hill tops (z 6): mountain under them, grass on top, a few flowers and stones
    for z, (cells, named, box) in lv_cells.items():
        if z < Z:
            m.hill(sorted(cells), z, ground="grass")
    # ---- lower levels: natural caves (guarded like the surface where the ground is guarded)
    for z, (cells, named, box) in lv_cells.items():
        if z <= Z:
            continue
        if d["levels"][z].get("built"):                       # a cellar or a mine: stone floor, stone walls
            for (x, y) in cells:
                m.ground[(x, y, z)] = m.pick("stonefloor")
            wall = {(x + a, y + b) for x, y in cells for a, b in D8} - cells
            for (x, y) in wall:
                m.ground[(x, y, z)] = m.pick("stonefloor")
            m.autowall(sorted(wall), z, "stone")
            continue
        DG.cave(m, cells, z)                                  # (zones for these levels: maps/layout_floor1.py)
    # ---- stairs between levels: stairs up at (x, y, z_low), the way down above it
    party_z = next((z for z, lv in d["levels"].items() if lv.get("party")), None)
    L["party_z"] = party_z
    den_done = False
    for link in d["links"]:
        kind, x, y, zl = link[:4]
        wx, wy = ox + x, oy + y
        if kind == "ramp":
            facing = link[4]
            fdy = RAMPS[facing][2]
            m.ramp(wx, wy, zl, facing=facing, width=2, name=f"{gid}_{x}_{y}_{zl}_{facing}")
            for i in (0, 1):
                L["landings"].append(((wx + i, wy - fdy, zl - 1), (wx + i, wy + fdy, zl)))
            continue
        for (tx, ty, tz) in ((wx, wy, zl), (wx, wy + 1, zl), (wx, wy, zl - 1), (wx, wy - 1, zl - 1)):
            if (tx, ty) not in lv_cells[tz][0]:
                raise ValueError(f"{gid}: the stairs at {(x, y, zl)} need open floor at {(tx - ox, ty - oy, tz)}")
        den = zl == party_z and not den_done
        m.stairs(wx, wy, zl, floor="stonefloor" if d["levels"][zl].get("built") else "cavefloor",
                 name=f"den_{gid}" if den else f"{gid}_{x}_{y}_{zl}")
        m.clear_items(wx, wy + 1, zl)
        m.clear_items(wx, wy - 1, zl - 1)
        if zl - 1 == Z:
            m.ground[(wx, wy, Z)] = HOLE
        L["landings"].append(((wx, wy - 1, zl - 1), (wx, wy + 1, zl)))
        if den:                                    # the party cave: the cavebot rule and the cave tests read these
            den_done = True
            m.points[f"den_{gid}"] = (wx, wy, zl - 1)
            L["den"] = ((wx, wy, zl - 1), (wx, wy + 1, zl))
    # ---- the ground's chest (FLOOR1_REVIEW.md F1-20): beside the quiet clearing deepest from the gate, never on the party
    # level; scripts/spirebound/chests.lua puts the chest there at start-up
    best = None
    gx_, gy_ = ox + d["gate"][0], oy + d["gate"][1]
    for z, lv in d["levels"].items():
        if z == party_z:
            continue
        cells, named, _box = lv_cells[z]
        for (name, x, y, r, band, route, content) in lv["clearings"]:
            if content != "rest" or band not in ("middle", "deep", "nest"):
                continue
            wx, wy = named[name]
            far = max(abs(wx - gx_), abs(wy - gy_)) + (20 if z != Z else 0)   # a lower or upper level counts as deeper
            for ddx, ddy in ((1, 1), (-1, 1), (1, -1), (-1, -1), (2, 0), (-2, 0), (0, 2), (0, -2)):
                if (wx + ddx, wy + ddy) in cells:
                    if best is None or far > best[0]:
                        best = (far, (wx + ddx, wy + ddy, z))
                    break
    if best:
        m.points[f"chest_{gid}"] = best[1]
    # ---- monsters, crowd spots, rest spots
    routes = {r: dict(name=r, groups=[], crowd=[]) for r in d["routes"]}
    offs = [(0, 0), (3, 0), (0, 3), (-3, 0)]
    for z, lv in d["levels"].items():
        cells, named, _box = lv_cells[z]
        for (name, x, y, r, band, route, content) in lv["clearings"]:
            wx, wy = named[name]
            L["clearings"][(wx, wy, z)] = (name, band, r)
            if isinstance(content, list):
                bxs = [t[0] for t in _box]
                away = -1 if wx < (min(bxs) + max(bxs)) / 2 else 1   # extra groups stand on the side away from the middle
                for k, members in enumerate(content):
                    dx, dy = offs[k]
                    dx *= away
                    if (wx + dx, wy + dy) not in cells:
                        dx, dy = -dx, -dy
                    WI.group(m, (wx + dx, wy + dy, z), list(members), CAVE_RESPAWN if z == party_z else c["respawn"])
                    if route in routes:
                        routes[route]["groups"].append((wx + dx, wy + dy, z))
                    else:                          # the party cave's groups belong to no hunting route
                        L.setdefault("party_groups", []).append((wx + dx, wy + dy, z))
            elif content == "crowd":
                routes[route]["crowd"].append((wx, wy, z))
                m.points[f"crowd_{gid}_{route}_{len(routes[route]['crowd'])}"] = (wx, wy, z)
            elif content == "rest" and z <= Z:
                spot = next(((wx + a, wy + b) for a, b in ((2, -1), (-2, -1), (1, -2), (-1, -2))
                             if (wx + a, wy + b) in cells and not m.items.get((wx + a, wy + b, z))), None)
                if spot:
                    m.clear_items(spot[0], spot[1], z)
                    m.put(spot[0], spot[1], z, rng.choice([2370, 1996]))
    for t in sorted(L.get("banks", set()) & inner7):
        m.clear_items(t[0], t[1], Z)
        m.ground[(t[0], t[1], Z)] = m.pick("grass")
    for route, start_name in d["routes"].items():
        start = next(lv_cells[z][1][start_name] + (z,) for z in sorted(d["levels"]) if start_name in lv_cells[z][1])
        routes[route]["start"] = start
        m.points[f"loop_{gid}_{route}"] = start
    L["routes"] = routes
    # ---- signs
    hx, hy = named7["hub"]
    names = ", ".join(d["route_names"][r] for r in sorted(d["route_names"]))
    m.sign(hx + 3, hy - 3, Z, f"{c['title']}. Levels {lo} to {hi}. Calm near the gate; the deeper you go, the more of them "
           f"there are. Hunting routes: {names}.")
    for link in d["links"]:
        kind, x, y, zl = link[:4]
        wx, wy = ox + x, oy + y
        above, below = d["levels"][zl - 1]["name"], d["levels"][zl]["name"]
        if kind == "ramp":                         # a sign beside the way up to the ramp, and one beside its top
            fdy = RAMPS[link[4]][2]
            for sx, sy, sz, text in ((wx - 1, wy + fdy * 3, zl, f"Up: {above}."), (wx + 2, wy + fdy * 3, zl, f"Up: {above}.")):
                if (sx, sy) in lv_cells[sz][0] and not m.items.get((sx, sy, sz)):
                    m.sign(sx, sy, sz, text)
                    break
            for sx, sy, sz, text in ((wx - 1, wy - fdy * 2, zl - 1, f"Down: {below}."), (wx + 2, wy - fdy * 2, zl - 1, f"Down: {below}.")):
                if (sx, sy) in lv_cells[sz][0] and not m.items.get((sx, sy, sz)):
                    m.sign(sx, sy, sz, text)
                    break
            continue
        if zl == party_z and L.get("den") and L["den"][0][:2] == (wx, wy):
            sx, sy = wx + 1, wy - 1
            if (sx, sy) in lv_cells[zl - 1][0]:
                m.clear_items(sx, sy, zl - 1)
                m.sign(sx, sy, zl - 1, f"{below}. For a party. Levels {den_level(c)} and up. Bots are refused below.")
            continue
        for sx, sy, sz, text in ((wx + 1, wy - 1, zl - 1, f"Down: {below}."), (wx - 1, wy - 1, zl - 1, f"Down: {below}."),
                                 (wx + 1, wy + 1, zl, f"Up: {above}."), (wx - 1, wy + 1, zl, f"Up: {above}.")):
            if (sx, sy) in lv_cells[sz][0] and not m.items.get((sx, sy, sz)) and (sx, sy) != (wx, wy):
                m.sign(sx, sy, sz, text)
                if sz == zl:
                    break
    for x, y, z in d.get("nest_signs", []):
        m.sign(ox + x, oy + y, z, "A nest. Not alone.")
    m.put(hx - 3, hy - 2, Z, 1996)
    m.put(hx + 3, hy + 2, Z, 2370)
    # ---- decoration below ground: stalagmites in open space only, bones and pebbles, never on a spawn, stair or sign
    land = {(a[0] + i, a[1] + j, a[2]) for pair in L["landings"] for a in pair for i in (-1, 0, 1) for j in (-1, 0, 1)}
    for z, (cells, named, box) in lv_cells.items():
        if z < Z:
            for t in sorted(cells):
                if rng.random() < 0.04 and (t[0], t[1], z) not in land and not m.items.get((t[0], t[1], z)):
                    m.put(t[0], t[1], z, rng.choice(WI.WALKOVER["grass"] + WI.WALKOVER["dirt"]))
        if z <= Z:
            continue
        xs = [t[0] for t in box]; ys = [t[1] for t in box]
        x0_, y0_, w_, h_ = min(xs), min(ys), max(xs) - min(xs) + 1, max(ys) - min(ys) + 1
        avoid = DG.keep_clear(m, z) | {(a[0] + i, a[1] + j) for pair in L["landings"] for a in pair if a[2] == z
                                       for i in (-1, 0, 1) for j in (-1, 0, 1)}
        if d["levels"][z].get("built"):            # a cellar or mine: torches on the walls, rubble, crates, cobwebs
            DG.hang_maze(m, x0_, y0_, w_, h_, z, share=0.12, h_item=DG.TORCH_H, v_item=DG.TORCH_V)
            props = d["levels"][z].get("props", DG.RUBBLE + DG.PILLARS)
            DG.scatter(m, x0_, y0_, w_, h_, z, props, len(cells) // 70, solid=True, avoid=avoid)
            DG.scatter(m, x0_, y0_, w_, h_, z, DG.COBWEBS + DG.BONES + DG.DEBRIS, len(cells) // 40, avoid=avoid)
            continue
        # fewer than at first: the client walk showed the Warren landing cluttered (2026-11-14)
        DG.scatter(m, x0_, y0_, w_, h_, z, DG.STALAGMITES, len(cells) // 80, solid=True, avoid=avoid)
        DG.scatter(m, x0_, y0_, w_, h_, z, DG.BONES + DG.DEBRIS, len(cells) // 50, avoid=avoid)
        # wall torches: the autopilot showed a new player sees only 2-3 tiles in the dark Warren (2026-11-14)
        DG.hang_cave(m, x0_, y0_, w_, h_, z, spacing=5)
    # ---- named points used by the game (crowd system, tests, guide)
    L["camp"], L["centre"] = (hx, hy), (hx, hy - 6)
    m.points["camp_" + gid] = (hx, hy, Z)
    xs = [p[0] for p in rect]; ys = [p[1] for p in rect]
    m.points[f"ground_{gid}_nw"] = (min(xs), min(ys), Z)
    m.points[f"ground_{gid}_se"] = (max(xs), max(ys), Z)
    for z, (cells, named, box) in lv_cells.items():
        L["levels"][z] = cells
        L["boxes"][z] = box
        if z != Z:
            bxs = [t[0] for t in box]; bys = [t[1] for t in box]
            kind = "den" if z == party_z else "level"
            pre = f"den_{gid}" if z == party_z else f"level_{gid}_{z}"
            m.points[f"{pre}_nw"] = (min(bxs), min(bys), z)
            m.points[f"{pre}_se"] = (max(bxs), max(bys), z)
            if kind == "den":                      # read by the cavebot rule and the calm checker (party limits)
                if not hasattr(m, "caves"):
                    m.caves = []
                groups = L.get("party_groups", [])
                m.caves.append(dict(id=gid, landing=L["den"][1], groups=groups,
                                    box=(min(bxs), min(bys), max(bxs) - min(bxs) + 1, max(bys) - min(bys) + 1)))
    m.points[f"gate_{gid}"] = (sum(p[0] for p in L["gate"]) // len(L["gate"]), max(p[1] for p in L["gate"]), Z)
    m.points[f"centre_{gid}"] = L["centre"] + (Z,)
    if not hasattr(m, "wilds"):
        m.wilds = []
    m.wilds.append(L)
    return L


def reach(m, L, block=None):
    """Every walkable tile of the ground that can be reached from its gate, on any level (through the stairs)."""
    block = block if block is not None else WI.blockers()
    got, todo, done = set(), [(x, y, Z) for x, y in L["gate"]], set()
    while todo:
        s = todo.pop()
        if s in done:
            continue
        done.add(s)
        area = L["levels"][s[2]] | (L["gate"] if s[2] == Z else set())
        part = WI.flood(m, [s], block, inside=area)
        got |= part
        for up, down in L["landings"]:                # standing next to the stairs on one level takes you to the other
            if up in part or any((up[0] + a, up[1] + b, up[2]) in part for a, b in D8):
                todo.append(down)
            if down in part or any((down[0] + a, down[1] + b, down[2]) in part for a, b in D8):
                todo.append(up)
    return got


def check(m):
    problems = []
    block = WI.blockers()
    for L in getattr(m, "wilds", []):
        if not L.get("design"):
            continue
        got = reach(m, L, block)
        for z in L["levels"]:
            if not any(t[2] == z for t in got):
                problems.append(f"{L['id']}: level {z} cannot be reached from the gate")
        for r in list(L["routes"].values()) + [dict(name="party cave", groups=L.get("party_groups", []), crowd=[], start=None)]:
            for p in r["groups"] + r["crowd"] + ([r["start"]] if r["start"] else []):
                if not any((p[0] + a, p[1] + b, p[2]) in got for a, b in D8 + ((0, 0),)):
                    problems.append(f"{L['id']}: route {r['name']} spot {p} cannot be reached from the gate")
            for p in r["crowd"] + ([r["start"]] if r["start"] else []):     # players and the tests stand on these
                if p not in got:
                    problems.append(f"{L['id']}: route {r['name']} spot {p} is not on open, walkable ground")
                elif m.ground.get(p) in (HOLE, 413, 469) or any(i in (5258, 1956, 1954) for i, _a in m.items.get(p, [])):
                    problems.append(f"{L['id']}: route {r['name']} spot {p} is on a way up or down")
        xs = [p[0] for p in L["rect"]]; ys = [p[1] for p in L["rect"]]
        edge = {(x, y) for (x, y) in L["rect"] if x in (min(xs), max(xs)) or y in (min(ys), max(ys))}
        leak = [(x, y) for (x, y, z) in got if z == Z and (x, y) in edge and (x, y) not in L["gate"]]
        if leak:
            problems.append(f"{L['id']}: the outer wall has a hole at {leak[:3]}")
    return problems
