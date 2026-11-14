#!/usr/bin/env python3
"""The calm checker for hunting grounds (FLOOR1_HUNTING_PLAN.md Part 3).

For every hunting ground and every level of it, measures how crowded it is from a player's point of view:
  pull of a tile = monsters whose home is on the same level within NOTICE tiles (no walls considered: the engine picks
  targets without line of sight, it only needs a clear line to hit).
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

# plan Part 3: limits by band (pull, density = walkable tiles per monster)
PULL_LIMIT = {"approach": 0, "calm": 3, "middle": 4, "deep": 6, "nest": 8, "party": 8}
DENSITY_MIN = {7: 45, 6: 35, 5: 35, 8: 35, 9: 25}
STARTER_DENSITY = 50
PARTY_DENSITY = 20


def build_map():
    import layout_floor1
    from mapgen import Map
    m = Map()
    layout_floor1.build(m)
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
    """tile -> number of monsters within notice (Chebyshev) on the same level."""
    by_z = {}
    for x, y, z, _n in mons:
        by_z.setdefault(z, []).append((x, y))
    out = {}
    for (x, y, z) in tiles:
        out[(x, y, z)] = sum(1 for mx, my in by_z.get(z, ()) if abs(mx - x) <= notice and abs(my - y) <= notice)
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
    """(id, title, level label, walkable tiles, monsters, kind) for every ground level and party cave on Floor 1."""
    import wilds
    block = wilds.blockers()
    out = []
    for L in getattr(m, "wilds", []):
        if L.get("design"):                            # designed grounds: every level, reached from the gate via stairs
            import designed
            got = designed.reach(m, L, block)
            for z in sorted(L["levels"]):
                tiles = {t for t in got if t[2] == z}
                out.append((L["id"], L["c"]["title"], f"z{z}", tiles, "designed", L["c"]["zone"] == "guarded"))
            continue
        gate = [(x, y, wilds.Z) for x, y in L["gate"]]
        inside = wilds.flood(m, gate, block, inside=L["rect"])
        out.append((L["id"], L["c"]["title"], "z7", inside, "surface", L["c"]["zone"] == "guarded"))
    for cv in getattr(m, "caves", []):
        x0, y0, w, h = cv["box"]
        reach = wilds.flood(m, [cv["landing"]], block, limit=(x0, y0, x0 + w, y0 + h))
        out.append((cv["id"], cv["id"] + " cave", f"z{cv['landing'][2]}", reach, "party", False))
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
    print(f"NOTICE = {NOTICE} tiles. pull = monsters that can come at a player standing on a tile.")
    print(f"{'ground':18s} {'lvl':4s} {'tiles':>6s} {'mons':>5s} {'tiles/mon':>9s} {'maxpull':>7s} {'avgpull':>7s} "
          f"{'pull0':>6s} {'pull<=2':>7s} {'rest':>5s} {'gap':>4s}  verdict")
    for gid, title, lvl, tiles, kind, guarded in areas(m):
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
        dens = n / max(1, len(mons))
        probs = []
        want = PARTY_DENSITY if kind == "party" else (STARTER_DENSITY if guarded and z == 7 else DENSITY_MIN.get(z, 35))
        if dens < want:
            probs.append(f"density {dens:.0f} < {want}")
        if kind == "designed":                         # band by band: each tile belongs to its nearest clearing
            L = next(L_ for L_ in m.wilds if L_["id"] == gid)
            cl = [(p, band) for p, (_n, band, _r) in L["clearings"].items() if p[2] == z]
            crowd = [p for r in L["routes"].values() for p in r["crowd"] if p[2] == z]
            pull_c = pull_map(tiles, mons + [(x, y, z, "crowd") for x, y, _z in crowd])
            worst = {}
            for t in tiles:
                band = "approach" if (t[0], t[1]) in L.get("hub", ()) and z == 7 else \
                    min(cl, key=lambda q: (q[0][0] - t[0]) ** 2 + (q[0][1] - t[1]) ** 2)[1] if cl else "deep"
                lim = PULL_LIMIT[band]
                if pull[t] > lim:
                    worst[band] = max(worst.get(band, 0), pull[t])
                if pull_c[t] > lim + 2:
                    worst[band + " with crowd"] = max(worst.get(band + " with crowd", 0), pull_c[t])
            for band, v in sorted(worst.items()):
                probs.append(f"{band} pull {v} > {PULL_LIMIT[band.split()[0]] + (2 if 'crowd' in band else 0)}")
        else:
            lim = PULL_LIMIT["party"] if kind == "party" else PULL_LIMIT["deep"]
            if max(vals) > lim:
                probs.append(f"max pull {max(vals)} > {lim}")
        if kind != "party":
            if p0 < 0.25:
                probs.append(f"pull-0 {p0:.0%} < 25%")
            if rest is None or rest > 20:
                probs.append(f"rest spot {rest} steps > 20")
        bad += bool(probs)
        print(f"{gid:18s} {lvl:4s} {n:6d} {len(mons):5d} {dens:9.1f} {max(vals):7d} {sum(vals) / max(1, n):7.1f} "
              f"{p0:6.0%} {p2:7.0%} {str(rest):>5s} {str(gap):>4s}  " + ("OK" if not probs else "; ".join(probs)))
        if pictures and tiles:
            heatmap(ROOT / "docs" / "previews" / f"hunt_{gid}_{lvl}.png", tiles, pull, mons)
    print(f"{bad} area(s) break the calm rules")
    return 1 if (strict and bad) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
