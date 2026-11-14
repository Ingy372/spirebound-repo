"""Designed hunting grounds (FLOOR1_HUNTING_PLAN.md Part 6).

A designed ground is drawn from a hand-written list in maps/floor1_plan.py (DESIGNS): clearings and paths on several
levels joined by stairs. Monsters stand in the clearings, spread out and layered calm (near the gate) -> middle -> deep,
so a player meets a few at a time. The surface keeps the walled ground of maps/wilds.py (outer wall, one gate); lower
levels are natural caves. tools/hunt_check.py measures how many monsters can reach a player on every tile.

build(m, c) paints it; check(m) is its walk test (gate -> every level -> every group and crowd spot).
"""
import random

import dungeon as DG
import wilds as WI
from floor1_plan import DESIGNS

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


def _carve(c, d, z, lv, rng):
    """The open tiles of one level, and its named clearing centres (world coordinates)."""
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
    for (name, x, y, r, band, route, content) in lv["clearings"]:
        if content == "crowd":                       # a crowd pocket: a short side passage to the nearest clearing
            p = named[name]
            near = min((q for n_, q in named.items() if n_ != name and q != p),
                       key=lambda q: (q[0] - p[0]) ** 2 + (q[1] - p[1]) ** 2)
            cells |= WI._tunnel(p, near, rng, width=2)
    gate = set()
    if z == Z:
        gx, gy = ox + d["gate"][0], oy + c["h"] - 1
        gate = {(gx + a, gy - b) for a in (-1, 0, 1) for b in (0, 1)}
        cells |= WI._tunnel((gx, gy - 1), named["hub"], rng, width=3, wiggle=False)
    cells = (cells & inner) | gate
    return cells, named, box, gate


def build(m, c):
    d = DESIGNS[c["design"]]
    rng = random.Random(sum(map(ord, c["id"])) * 104729)
    ox, oy = X0 + c["x"], Y0 + c["y"]
    rect = {(ox + u, oy + v) for u in range(c["w"]) for v in range(c["h"])}
    gid, (lo, hi) = c["id"], c["levels"]
    L = dict(id=gid, c=c, rect=rect, loops=[], routes={}, levels={}, boxes={}, clearings={}, landings=[], design=True)
    lv_cells = {}
    for z, lv in d["levels"].items():
        cells, named, box, gate = _carve(c, d, z, lv, rng)
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
    for t in cells7:
        if t not in L["hub"] and t not in L["gate"] and any((t[0] + a, t[1] + b) not in cells7 for a, b in D4) and rng.random() < 0.08:
            m.put(t[0], t[1], Z, rng.choice(WI.WALKOVER[trail]))
    L["open"] = cells7
    # ---- lower levels: natural caves (guarded like the surface where the ground is guarded)
    for z, (cells, named, box) in lv_cells.items():
        if z == Z:
            continue
        DG.cave(m, cells, z)                                  # (zones for these levels: maps/layout_floor1.py)
    # ---- stairs between levels: stairs up at (x, y, z_low), the way down above it
    for _kind, x, y, zl in d["links"]:
        wx, wy = ox + x, oy + y
        for (tx, ty, tz) in ((wx, wy, zl), (wx, wy + 1, zl), (wx, wy, zl - 1), (wx, wy - 1, zl - 1)):
            if (tx, ty) not in lv_cells[tz][0]:
                raise ValueError(f"{gid}: the stairs at {(x, y, zl)} need open floor at {(tx - ox, ty - oy, tz)}")
        m.stairs(wx, wy, zl, floor="cavefloor", name=f"{gid}_{x}_{y}_{zl}")
        m.clear_items(wx, wy + 1, zl)
        m.clear_items(wx, wy - 1, zl - 1)
        if zl - 1 == Z:
            m.ground[(wx, wy, Z)] = HOLE
        L["landings"].append(((wx, wy - 1, zl - 1), (wx, wy + 1, zl)))
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
                    WI.group(m, (wx + dx, wy + dy, z), list(members), c["respawn"])
                    routes[route]["groups"].append((wx + dx, wy + dy, z))
            elif content == "crowd":
                routes[route]["crowd"].append((wx, wy, z))
                m.points[f"crowd_{gid}_{route}_{len(routes[route]['crowd'])}"] = (wx, wy, z)
            elif content == "rest" and z == Z:
                spot = next(((wx + a, wy + b) for a, b in ((2, -1), (-2, -1), (1, -2), (-1, -2)) if (wx + a, wy + b) in cells), None)
                if spot:
                    m.clear_items(spot[0], spot[1], Z)
                    m.put(spot[0], spot[1], Z, rng.choice([2370, 1996]))
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
    for _kind, x, y, zl in d["links"]:
        wx, wy = ox + x, oy + y
        above, below = d["levels"][zl - 1]["name"], d["levels"][zl]["name"]
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
    for z, (cells, named, box) in lv_cells.items():
        if z == Z:
            continue
        xs = [t[0] for t in box]; ys = [t[1] for t in box]
        x0_, y0_, w_, h_ = min(xs), min(ys), max(xs) - min(xs) + 1, max(ys) - min(ys) + 1
        avoid = DG.keep_clear(m, z) | {(a[0] + i, a[1] + j) for pair in L["landings"] for a in pair if a[2] == z
                                       for i in (-1, 0, 1) for j in (-1, 0, 1)}
        DG.scatter(m, x0_, y0_, w_, h_, z, DG.STALAGMITES, len(cells) // 45, solid=True, avoid=avoid)
        DG.scatter(m, x0_, y0_, w_, h_, z, DG.BONES + DG.DEBRIS, len(cells) // 30, avoid=avoid)
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
            m.points[f"level_{gid}_{z}_nw"] = (min(bxs), min(bys), z)
            m.points[f"level_{gid}_{z}_se"] = (max(bxs), max(bys), z)
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
        for r in L["routes"].values():
            for p in r["groups"] + r["crowd"] + [r["start"]]:
                if not any((p[0] + a, p[1] + b, p[2]) in got for a, b in D8 + ((0, 0),)):
                    problems.append(f"{L['id']}: route {r['name']} spot {p} cannot be reached from the gate")
        xs = [p[0] for p in L["rect"]]; ys = [p[1] for p in L["rect"]]
        edge = {(x, y) for (x, y) in L["rect"] if x in (min(xs), max(xs)) or y in (min(ys), max(ys))}
        leak = [(x, y) for (x, y, z) in got if z == Z and (x, y) in edge and (x, y) not in L["gate"]]
        if leak:
            problems.append(f"{L['id']}: the outer wall has a hole at {leak[:3]}")
    return problems
