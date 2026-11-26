#!/usr/bin/env python3
"""The danger-limit checker for hunting grounds (FLOOR1_HUNTING_PLAN.md Parts 3 and 10, DESIGN.md 9.4).

For every hunting ground and every level of it, measures how crowded it is from a player's point of view:
  pull of a tile = the danger that can come at a player standing there: the summed weight (tools/balance.py HABITS) of
  the monsters whose home is on the same level within NOTICE tiles (no walls considered: the engine picks targets
  without line of sight, it only needs a clear line to hit). Each band's limit is the danger budget of the ground's
  own type (training, class, mixed, group, large; tools/balance.py GROUND_TYPES).
Prints one line per ground and level and draws a heat map per ground and level into docs/previews/hunt_<id>_z<z>.png
(white = pull 0, green 1-2, yellow 3-4, orange 5-6, red 7+; black dots = monster homes).

Usage:  python tools/hunt_check.py [ground ids...] [--no-pictures] [--strict]
        --strict: exit 1 if any limit in Part 3 is broken (used by the map build from task H4 on).

NOTICE: Canary 3.6.1 lets a creature see 11 tiles each way (MAP_MAX_VIEW_PORT_X/Y = 11, map_const.hpp); monsters may use
a smaller range of their own (task H0 measures it). Until then the plan's value, 10, is used.
"""
from __future__ import annotations

import sys
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "maps"))

NOTICE = 10
D8 = ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1))

from balance import budget, weight  # noqa: E402

# density = walkable tiles per unit of weight (one weight-1 monster), per level
# H14 (Jay, 2026-11-25: "challenge, not calm"): about half the old minimums, so grounds may hold twice the monsters
DENSITY_MIN = {7: 22, 6: 18, 5: 18, 8: 18, 9: 13}
STARTER_DENSITY = 28
PARTY_DENSITY = 10
CROWD_EXTRA = 2                                   # with every crowd spot on, a band may go this much over its budget
SOLO_TYPES = ("training", "class", "mixed")       # breathing room and rest spots are checked for these


def W(name):
    """A monster's weight; anything not in the habit table counts as 1."""
    try:
        return weight(name)
    except KeyError:
        return 1.0


def limit(gtype, band):
    return budget(gtype, band)


def build_map(floors=()):
    """Floor 1, plus floors 2-10 when asked (the autopilot's routes on higher floors)."""
    import layout_floor1
    import layout_floor
    from mapgen import Map
    m = Map()
    layout_floor1.build(m)
    for n in floors:
        layout_floor.build(m, n)
    m.finish()
    return m


def homes(m):
    """Every monster's home tile: (x, y, z, name)."""
    out = []
    for kids, (x, y, z), _radius, count, *_r in m.monsters:
        if isinstance(kids, str):                       # an old-style area: `count` of one kind round the centre
            out += [(x, y, z, kids)] * count
            continue
        for mon, dx, dy, *_t in kids:
            out.append((x + dx, y + dy, z, mon))
    return out


def pull_map(tiles, mons, notice=NOTICE):
    """tile -> summed weight of the monsters within notice (Chebyshev) on the same level (rounded to 0.1)."""
    by_z = {}
    for x, y, z, n in mons:
        by_z.setdefault(z, []).append((x, y, W(n)))
    out = {}
    for (x, y, z) in tiles:
        out[(x, y, z)] = round(sum(w for mx, my, w in by_z.get(z, ()) if abs(mx - x) <= notice and abs(my - y) <= notice), 1)
    return out


def rest_distance(tiles, pull):
    """Worst number of steps from any walkable tile to a pull-0 tile (None if there is no pull-0 tile)."""
    start = [t for t in tiles if pull[t] == 0]
    if not start:
        return None
    dist = {t: 0 for t in start}
    q = deque(start)
    while q:
        x, y, z = q.popleft()
        for a, b in D8:
            n = (x + a, y + b, z)
            if n in tiles and n not in dist:
                dist[n] = dist[(x, y, z)] + 1
                q.append(n)
    return max(dist.get(t, 999) for t in tiles)


def spacing(mons):
    """Closest distance between two monster homes that belong to different groups (approximated by > 2 tiles apart)."""
    best = None
    pts = [(x, y, z) for x, y, z, _n in mons]
    for i, a in enumerate(pts):
        for b in pts[i + 1:]:
            if a[2] != b[2]:
                continue
            d = max(abs(a[0] - b[0]), abs(a[1] - b[1]))
            if d > 2 and (best is None or d < best):
                best = d
    return best


def areas(m):
    """(id, title, level label, walkable tiles, kind, guarded, type) for every ground level and party cave on Floor 1."""
    import wilds
    block = wilds.blockers()
    out = []
    for L in getattr(m, "wilds", []):
        if L.get("design"):                            # designed grounds: every level, reached from the gate via stairs
            import designed
            got = designed.reach(m, L, block)
            for z in sorted(L["levels"]):
                if z == L.get("party_z"):              # the party cave is checked below, with the party limits
                    continue
                tiles = {t for t in got if t[2] == z}
                out.append((L["id"], L["c"]["title"], f"z{z}", tiles, "designed", L["c"]["zone"] == "guarded", L["c"]["type"]))
            continue
        gate = [(x, y, wilds.Z) for x, y in L["gate"]]
        inside = wilds.flood(m, gate, block, inside=L["rect"])
        out.append((L["id"], L["c"]["title"], "z7", inside, "surface", L["c"]["zone"] == "guarded", L["c"]["type"]))
    for cv in getattr(m, "caves", []):
        x0, y0, w, h = cv["box"]
        reach = wilds.flood(m, [cv["landing"]], block, limit=(x0, y0, x0 + w, y0 + h))
        out.append((cv["id"], cv["id"] + " cave", f"z{cv['landing'][2]}", reach, "party", False, "group"))
    return out


def heatmap(path, tiles, pull, mons, px=6):
    from PIL import Image, ImageDraw
    xs = [t[0] for t in tiles]; ys = [t[1] for t in tiles]
    x0, y0 = min(xs) - 2, min(ys) - 2
    w, h = max(xs) - x0 + 3, max(ys) - y0 + 3
    img = Image.new("RGB", (w * px, h * px), (60, 60, 60))
    d = ImageDraw.Draw(img)
    for t in tiles:
        p = pull[t]
        col = (255, 255, 255) if p == 0 else (120, 200, 90) if p <= 2 else (240, 220, 60) if p <= 4 else (240, 150, 40) if p <= 6 else (220, 40, 40)
        d.rectangle([(t[0] - x0) * px, (t[1] - y0) * px, (t[0] - x0 + 1) * px - 1, (t[1] - y0 + 1) * px - 1], fill=col)
    for x, y, _z, _n in mons:
        cx, cy = (x - x0) * px + px // 2, (y - y0) * px + px // 2
        d.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=(0, 0, 0))
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path)


def main(argv):
    only = [a for a in argv if not a.startswith("--")]
    pictures = "--no-pictures" not in argv
    strict = "--strict" in argv
    m = build_map()
    mons_all = homes(m)
    bad = 0
    print(f"NOTICE = {NOTICE} tiles. pull = the danger (summed monster weight) that can come at a player standing on a tile.")
    print(f"{'ground':18s} {'lvl':4s} {'tiles':>6s} {'mons':>5s} {'tiles/wt':>9s} {'maxpull':>7s} {'avgpull':>7s} "
          f"{'pull0':>6s} {'pull<=2':>7s} {'rest':>5s} {'gap':>4s}  verdict")
    for gid, title, lvl, tiles, kind, guarded, gtype in areas(m):
        if only and gid not in only:
            continue
        z = next(iter(tiles))[2] if tiles else 7
        mons = [mm for mm in mons_all if mm[2] == z and (mm[0], mm[1], z) in tiles]
        pull = pull_map(tiles, mons)
        n = len(tiles)
        vals = list(pull.values()) or [0]
        p0 = sum(1 for v in vals if v == 0) / max(1, n)
        p2 = sum(1 for v in vals if v <= 2) / max(1, n)
        rest = rest_distance(tiles, pull)
        gap = spacing(mons)
        dens = n / max(0.1, sum(W(mm[3]) for mm in mons))
        probs = []
        want = PARTY_DENSITY if kind == "party" else (STARTER_DENSITY if guarded and z == 7 else DENSITY_MIN.get(z, 35))
        if dens < want:
            probs.append(f"density {dens:.0f} < {want}")
        if kind == "designed":                         # band by band: each tile belongs to its nearest clearing
            L = next(L_ for L_ in m.wilds if L_["id"] == gid)
            cl = [(p, band) for p, (_n, band, _r) in L["clearings"].items() if p[2] == z]
            crowd = [p for r in L["routes"].values() for p in r["crowd"] if p[2] == z]
            from floor1_plan import DESIGNS
            cg = DESIGNS[L["c"]["design"]]["crowd_group"]
            pull_c = pull_map(tiles, mons + [(x, y, z, mon) for x, y, _z in crowd for mon, k in cg for _ in range(k)])
            worst = {}
            for t in tiles:
                band = "approach" if (t[0], t[1]) in L.get("hub", ()) and z == 7 else \
                    min(cl, key=lambda q: (q[0][0] - t[0]) ** 2 + (q[0][1] - t[1]) ** 2)[1] if cl else "deep"
                lim = limit(gtype, band)
                if pull[t] > lim:
                    worst[band] = max(worst.get(band, 0), pull[t])
                if pull_c[t] > lim + CROWD_EXTRA:
                    worst[band + " with crowd"] = max(worst.get(band + " with crowd", 0), pull_c[t])
            for band, v in sorted(worst.items()):
                probs.append(f"{band} pull {v} > {limit(gtype, band.split()[0]) + (CROWD_EXTRA if 'crowd' in band else 0)}")
        else:
            lim = limit("group", "deep") if kind == "party" else limit(gtype, "deep")
            if max(vals) > lim:
                probs.append(f"max pull {max(vals)} > {lim}")
        if kind != "party" and gtype in SOLO_TYPES:
            if p0 < 0.10:                          # H14: a breather somewhere, not a quarter of the ground
                probs.append(f"pull-0 {p0:.0%} < 10%")
            if rest is None or rest > 35:
                probs.append(f"rest spot {rest} steps > 35")
        bad += bool(probs)
        print(f"{gid:18s} {lvl:4s} {n:6d} {len(mons):5d} {dens:9.1f} {max(vals):7.1f} {sum(vals) / max(1, n):7.1f} "
              f"{p0:6.0%} {p2:7.0%} {str(rest):>5s} {str(gap):>4s}  " + ("OK" if not probs else "; ".join(probs)))
        if pictures and tiles:
            heatmap(ROOT / "docs" / "previews" / f"hunt_{gid}_{lvl}.png", tiles, pull, mons)
    print(f"{bad} area(s) break the danger limits")
    return 1 if (strict and bad) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
