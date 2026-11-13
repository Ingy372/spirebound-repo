"""Hunting grounds for the wilds (FLOOR1_WILDS_PLAN.md Part 5): the same skeleton for every ground, dressed differently.

    W W W W W W W W W W W W      W = the ground's wall, 2 tiles thick (thicket, rock or water); one 3-wide gate
    W  loop    +   loop   W      each loop = a 2-wide ring trail round a solid core, monster groups at fixed spots
    W + + + + + + + + + + W      + = cross trails between the loops (they meet in the middle: the cave stairs go there)
    W  loop    +   loop   W      H = the hub inside the gate: sign, fire, bench; no monsters within 8 tiles of the gate
    W H H H H H H H H H H W
    W W W W  gate  W W W W

layout(c) works out every tile from the plan table (maps/floor1_plan.py) the same way on every build; build(m, c) paints
it, places the monster groups and the named points; check(m, grounds) is the walk test that fails the build (Part 5.2.9).
Grounds are laid out in a local frame with the gate on the north side, then turned to face their real gate side.
"""
import random

import scenery as S
from floor1_plan import ELITE_RESPAWN, ELITES, SIZES, spawn_time

X0, Y0, Z = 1000, 1000, 7
MOUNTAIN = 1128

# ---- what solid things are made of. "edge" kinds (rock, water) paint their ground only where every neighbour is solid
# too: the map tool then hangs rock faces / shorelines on the tiles round them, and those block walking as well.
TREES_ALL_BROAD = [3615, 3616, 3617, 3619, 3621, 3622, 3625] * 4 + [3618, 3620]   # mostly green, a few maples
FIRS = [3614, 3682, 7024, 3614, 3682]
ROCKS = [1772, 1843, 1851, 1853, 1859, 1860, 1822]  # single-tile stones that block (no multi-piece rocks here)
REEDS = [3688, 3690, 3685]
SOLID = {
    # name: (ground under it, things for the edge of the mass, things inside it, edge kind or None)
    "bushes": ("grass", [3681, 3681, 3699, 3700], TREES_ALL_BROAD + [3681], None),
    "broadleaf": ("grass", TREES_ALL_BROAD + [3751, 3754, 3681], TREES_ALL_BROAD, None),
    "ferns": ("grass", [3751, 3754, 3751, 3681], [3625, 3617, 3619, 3751, 3754], None),
    "hedge": ("grass", [3681, 3699, 3700], [3681, 3699, 3700, 3619], None),
    "oaks": ("grass", TREES_ALL_BROAD + [3681], TREES_ALL_BROAD, None),
    "firs": ("grass", FIRS + [3751], FIRS, None),
    "thorns": ("grass", S.THORNS + [3698], S.THORNS + [3623, 3624], None),
    "boulders": ("grass", ROCKS, [], "mountain"),
    "water": ("grass", REEDS + [3623, 3624, 958], [], "water"),
}
CORE = {
    "mounds": ("dirt", [3681, 3699, 3681], [1783, 1772, 1843, 3681], None),
    "pond": ("mud", REEDS + [3681], [], "water"),
    "grove": ("grass", [3751, 3754, 3681, 3699], [3625, 3617, 3619, 3620], None),
    "flowerbed": ("grass", [3681, 3699, 3700], S.FLOWERS, None),          # flowers inside a hedge, a tree in the middle
    "oakgrove": ("grass", TREES_ALL_BROAD + [3681], TREES_ALL_BROAD, None),
    "hills": ("dirt", ROCKS, [], "mountain"),
    "firs": ("grass", FIRS, FIRS, None),
    "pool": ("mud", REEDS + [958], [], "water"),
    "thorns": ("grass", S.THORNS, S.THORNS, None),
    "gravelmound": ("gravel", ROCKS, [], "mountain"),
    "banditcamp": ("dirt", [17233], [5543, 116, 2519, 2523, 116], None),      # a fenced heap; the fence is set in build()
    "cutstone": ("gravel", [1822, 2264, 2290, 1859], [], "mountain"),
}
TRAIL_GROUND = {"dirt": "dirt", "grass": "grass", "mud": "mud", "gravel": "gravel"}
WALKOVER = {"dirt": S.STONES + [3114, 3115], "grass": S.FLOWERS + [3737], "mud": [3737, 3115], "gravel": S.STONES + [6475]}
SIDE_NAMES = {(0, 0): "nw", (1, 0): "ne", (0, 1): "sw", (1, 1): "se"}
SIDE_WORDS = {"nw": "north-west", "ne": "north-east", "sw": "south-west", "se": "south-east"}
D4 = ((1, 0), (-1, 0), (0, 1), (0, -1))
D8 = D4 + ((1, 1), (1, -1), (-1, 1), (-1, -1))


# ------------------------------------------------------------------------------------------------ geometry
def _frame(c):
    """Local frame: u across the gate side, v inwards from it. Returns (W, D, to_world)."""
    x, y, w, h = X0 + c["x"], Y0 + c["y"], c["w"], c["h"]
    side = c["gate"]
    if side == "n":
        return w, h, lambda u, v: (x + u, y + v)
    if side == "s":
        return w, h, lambda u, v: (x + w - 1 - u, y + h - 1 - v)
    if side == "w":
        return h, w, lambda u, v: (x + v, y + h - 1 - u)
    return h, w, lambda u, v: (x + w - 1 - v, y + u)          # "e"


def _attempt(c, rng, wobble):
    sz = SIZES[c["size"]]
    W, D, tw = _frame(c)
    lw, lh = sz["loop"]
    A, Dp = (lw, lh) if c["gate"] in "ns" else (lh, lw)       # loop box across / deep, in the local frame
    cross, hub, ng = sz["cross"], sz["hub"], sz["groups"]
    gate = {(u, v) for u in range(W // 2 - 1, W // 2 + 2) for v in (0, 1)}
    hub_t = {(u, v) for u in range(2, W - 2) for v in range(2, hub)}
    vcross = {(u, v) for u in range(A, A + cross) for v in range(hub, D - 2)}
    hcross = {(u, v) for u in range(2, W - 2) for v in range(hub + Dp, hub + Dp + cross)}
    loops = []
    for j in (0, 1):
        for i in (0, 1):
            u0, v0 = i * (A + cross), hub + j * (Dp + cross)
            if wobble:
                du = rng.randint(-1, 2) if i == 0 else rng.randint(-2, max(-2, min(1, W - 2 * A - cross + 1)))
                dv = rng.randint(-2, 2) if j == 0 else rng.randint(-2, max(-2, min(2, D - hub - 2 * Dp - cross + 1)))
            else:
                du = dv = 0
            ux0, ux1 = u0 + 3 + du, u0 + A - 4 + du
            vy0, vy1 = v0 + 3 + dv, v0 + Dp - 4 + dv
            rect = {(u, v) for u in range(ux0, ux1 + 1) for v in range(vy0, vy1 + 1)}
            def chamfer(r, x0, x1, y0, y1, k):
                return {(u, v) for u, v in r if min(u - x0, x1 - u) + min(v - y0, y1 - v) >= k}
            outer = chamfer(rect, ux0, ux1, vy0, vy1, 2)
            inner = chamfer({(u, v) for u, v in rect if ux0 + 2 <= u <= ux1 - 2 and vy0 + 2 <= v <= vy1 - 2},
                            ux0 + 2, ux1 - 2, vy0 + 2, vy1 - 2, 1)
            mu = (ux0 + ux1) // 2
            if wobble:                                            # bulges (core and trail step out) and pinches (wider trail)
                for side in "nsew":
                    if rng.random() < 0.55:
                        if side in "ns":
                            n_ = rng.randint(3, 5); a = rng.randint(ux0 + 3, max(ux0 + 3, ux1 - 3 - n_)); seg = range(a, a + n_)
                            if side == "n" and any(abs(u - mu) <= 3 for u in seg):
                                continue
                            out_v, in_v = (vy0 - 1, vy0 + 1) if side == "n" else (vy1 + 1, vy1 - 1)
                            tiles_o, tiles_i = [(u, out_v) for u in seg], [(u, in_v) for u in seg]
                        else:
                            n_ = rng.randint(3, 5); a = rng.randint(vy0 + 3, max(vy0 + 3, vy1 - 3 - n_)); seg = range(a, a + n_)
                            out_u, in_u = (ux0 - 1, ux0 + 1) if side == "w" else (ux1 + 1, ux1 - 1)
                            tiles_o, tiles_i = [(out_u, v) for v in seg], [(in_u, v) for v in seg]
                        if rng.random() < 0.7:
                            outer |= set(tiles_o); inner |= {t for t in tiles_i if t in outer}
                        else:
                            pin = {(t[0] + (t[0] - o[0]) // 2, t[1] + (t[1] - o[1]) // 2) for t, o in zip(tiles_i, tiles_o)}   # core's edge row
                            inner -= pin
            ring = outer - inner
            core = set(inner)
            target_v = hub if j == 0 else hub + Dp + cross        # first row past the hub / the cross trail
            mouth = {(u, v) for u in (mu - 1, mu, mu + 1) for v in range(target_v, vy0 + 2) if (u, v) not in core}
            mouth -= ring
            loops.append(dict(i=i, j=j, ring=ring, core=core, mouth=mouth, mu=mu, vy0=vy0, box=(ux0, vy0, ux1, vy1)))
    # monster groups and crowd spots: 2 x groups points spread evenly along the ring, starting half a step from the mouth
    for lp in loops:
        ux0, vy0, ux1, vy1 = lp["box"]
        inner_lane = [t for t in lp["ring"] if any((t[0] + a, t[1] + b) in lp["core"] for a, b in D8)]
        cx0, cy0, cx1, cy1 = ux0 + 0.5, vy0 + 0.5, ux1 - 0.5, vy1 - 0.5
        wC, hC = cx1 - cx0, cy1 - cy0
        P = 2 * (wC + hC)
        start = lp["mu"] - cx0                                # mouth position along the top edge
        pts = []
        npts = 2 * ng
        for k in range(npts):
            s = (start + (k + 0.5) * P / npts) % P
            if s < wC:
                fx, fy = cx0 + s, cy0
            elif s < wC + hC:
                fx, fy = cx1, cy0 + (s - wC)
            elif s < 2 * wC + hC:
                fx, fy = cx1 - (s - wC - hC), cy1
            else:
                fx, fy = cx0, cy1 - (s - 2 * wC - hC)
            pts.append(min(inner_lane, key=lambda t: (t[0] - fx) ** 2 + (t[1] - fy) ** 2))
        lp["groups"] = pts[0::2]
        odd = pts[1::2]
        lp["crowd"] = odd if sz["crowd"] == len(odd) else odd[0::2][:sz["crowd"]]
        lp["patches"] = set()
        for gx, gy in lp["groups"] + lp["crowd"]:
            lp["patches"] |= {(gx + a, gy + b) for a in (-1, 0, 1) for b in (-1, 0, 1)}
    open_l = hub_t | vcross | hcross | gate
    for lp in loops:
        open_l |= lp["ring"] | lp["mouth"] | lp["patches"]
    # ---- checks on the drawing itself: separation between loops and other open places, nothing near the gate
    problems = []
    others = hub_t | vcross | hcross | gate
    for k, lp in enumerate(loops):
        own = lp["ring"] | lp["patches"]
        foreign = others | set().union(*[o["ring"] | o["patches"] | o["mouth"] for n, o in enumerate(loops) if n != k])
        for (u, v) in own:
            if not (2 <= u <= W - 3 and 2 <= v <= D - 3):
                problems.append("loop touches the wall")
                break
            if any((u + a, v + b) in foreign and (u + a, v + b) not in lp["mouth"] for a, b in D8):
                problems.append("loop touches another open place")
                break
        for gx, gy in lp["groups"]:
            if max(abs(gx - W // 2), gy) < 9:
                problems.append("group within 8 tiles of the gate")
            if any(abs(gx - m[0]) <= 1 and abs(gy - m[1]) <= 1 for m in lp["mouth"]):
                problems.append("group in a mouth")
    special = {}
    if c.get("wallow"):                                        # Old Tusk's wallow: a hollow core with a 1-tile way in
        lp = next(o for o in loops if (o["i"], o["j"]) == c["wallow"])
        core = lp["core"] - lp["patches"]
        us = sorted({u for u, _v in core}); vs = sorted({v for _u, v in core})
        cu, cv = (us[0] + us[-1]) // 2, (vs[0] + vs[-1]) // 2
        clear = {(u, v) for u in range(cu - 3, cu + 3) for v in range(cv - 3, cv + 4)}
        clear = {t for t in clear if all((t[0] + a, t[1] + b) in core for a, b in D8)}   # keep a 1-tile thicket round it
        if len(clear) < 28 or (cu, cv) not in clear:
            problems.append("wallow does not fit")
        else:
            # the way in: one tile wide, from the wallow's hub-facing edge straight out to the ring
            top = min(v for u, v in clear if u == cu)
            gap_u, gv = cu, top - 1
            while (gap_u, gv) in core:
                gv -= 1
            gap = {(gap_u, v) for v in range(gv + 1, top)}
            special = dict(clear=clear, gap=gap, centre=(cu, cv))
            open_l |= clear | gap
    return dict(W=W, D=D, tw=tw, gate=gate, hub=hub_t, cross=vcross | hcross, loops=loops, open=open_l, special=special,
                centre=(A + cross // 2, hub + Dp + cross // 2), camp=(W // 2, (hub + 1) // 2), problems=problems)


def layout(c):
    """Every tile of a ground, in world coordinates. The same plan always gives the same ground."""
    rng = random.Random(sum(map(ord, c["id"])) * 7919)
    loc = None
    for _try in range(200):
        loc = _attempt(c, rng, wobble=True)
        if not loc["problems"]:
            break
    else:
        loc = _attempt(c, rng, wobble=False)
        if loc["problems"]:
            raise ValueError(f"{c['id']}: the hunting-ground skeleton does not fit: {sorted(set(loc['problems']))}")
    tw = loc["tw"]
    T = lambda s: {tw(u, v) for u, v in s}                   # noqa: E731
    W, D = loc["W"], loc["D"]
    rect = {tw(u, v) for u in range(W) for v in range(D)}
    out = dict(id=c["id"], c=c, rect=rect, gate=T(loc["gate"]), hub=T(loc["hub"]), cross=T(loc["cross"]),
               open=T(loc["open"]), centre=tw(*loc["centre"]), camp=tw(*loc["camp"]), loops=[])
    cx = sum(p[0] for p in rect) / len(rect); cy = sum(p[1] for p in rect) / len(rect)
    for lp in loc["loops"]:
        ring = T(lp["ring"])
        lx = sum(p[0] for p in ring) / len(ring); ly = sum(p[1] for p in ring) / len(ring)
        name = SIDE_NAMES[(int(lx > cx), int(ly > cy))]
        mouth_pt = tw(lp["mu"], min((v for _u, v in lp["mouth"]), default=lp["vy0"]))
        cut = T({(u, v) for u, v in lp["ring"] if abs(u - lp["mu"]) <= 1 and v <= lp["vy0"] + 2})
        out["loops"].append(dict(name=name, ring=ring, cut=cut, core=T(lp["core"]) - T(lp["patches"]), mouth=T(lp["mouth"]),
                                 mouth_pt=mouth_pt, groups=[tw(*g) for g in lp["groups"]], crowd=[tw(*g) for g in lp["crowd"]],
                                 patches=T(lp["patches"]), local=lp))
    sp = loc["special"]
    if sp:
        out["wallow"] = dict(clear=T(sp["clear"]), gap=T(sp["gap"]), centre=tw(*sp["centre"]))
    # sign spots: beside the gate inside the hub, and beside each loop's mouth (on the solid side of its first tile)
    gu = W // 2
    out["gate_sign"] = tw(gu + 2, 2)
    out["fire"] = tw(4, 3) if W > 12 else tw(gu - 3, 3)
    out["bench"] = tw(W - 5, 3)
    for lp, ol in zip(loc["loops"], out["loops"]):
        mv = min((v for _u, v in lp["mouth"]), default=lp["vy0"])
        ol["sign"] = tw(lp["mu"] + 2, mv)
    return out


# ------------------------------------------------------------------------------------------------ painting
def _interior(tiles, rect):
    """Solid tiles whose eight neighbours are solid too (outside the ground counts as solid)."""
    return {t for t in tiles if all((t[0] + a, t[1] + b) in tiles or (t[0] + a, t[1] + b) not in rect for a, b in D8)}


def _mass(m, tiles, rect, spec, rng, ground_key=None):
    """Fill a solid area: an edge kind paints rock/water inside and leaves its rim to the edge pieces; anything else puts
    one blocking thing on every tile (rim things on the rim, inside things inside)."""
    gkey, rim_items, inside_items, edge = spec
    gkey = ground_key or gkey
    inner = _interior(tiles, rect)
    for t in tiles:
        m.ground[(t[0], t[1], Z)] = m.pick(gkey)
        m.clear_items(t[0], t[1], Z)
    if edge:
        # rock or water only where it has rock/water all round, so its edge pieces land on the rim (which blocks)
        core = _interior(inner, rect) if edge == "water" else inner
        for t in core:
            m.ground[(t[0], t[1], Z)] = MOUNTAIN if edge == "mountain" else m.pick("water")
        covered = {(t[0] + a, t[1] + b) for t in core for a, b in D8}
        for t in tiles - core:
            if t not in covered:                               # a thin bit with no rock/water beside it: a stone or reed
                m.put(t[0], t[1], Z, rng.choice(rim_items))
        return
    for t in tiles:
        pool = inside_items if (t in inner and inside_items) else rim_items
        m.put(t[0], t[1], Z, rng.choice(pool))


def build(m, c, extra_points=True):
    """Paint the ground, place its groups and named points. Returns the layout (kept for the walk test)."""
    L = layout(c)
    rng = random.Random(sum(map(ord, c["id"])) * 104729)
    rect, opn = L["rect"], L["open"]
    trail_key = TRAIL_GROUND[c["trail"]]
    # clean slate
    for (x, y) in rect:
        m.ground[(x, y, Z)] = m.pick("grass")
        m.clear_items(x, y, Z)
    cores = set().union(*[lp["core"] for lp in L["loops"]])
    if L.get("wallow"):
        cores -= L["wallow"]["clear"] | L["wallow"]["gap"]
    walls = rect - opn - cores
    _mass(m, walls, rect, SOLID[c["wall"]], rng)
    for lp in L["loops"]:
        core = lp["core"] - (L["wallow"]["clear"] | L["wallow"]["gap"] if L.get("wallow") else set())
        spec = CORE[c["core"]]
        _mass(m, core, rect, spec, rng)
        inner = _interior(core, rect)
        if c["core"] == "flowerbed" and inner:                 # a tree in the middle of each flower bed
            mid = min(inner, key=lambda t: (t[0] - sum(p[0] for p in inner) / len(inner)) ** 2 + (t[1] - sum(p[1] for p in inner) / len(inner)) ** 2)
            m.clear_items(mid[0], mid[1], Z); m.put(mid[0], mid[1], Z, 3619)
        if c["core"] == "thorns" and inner:                    # a dead tree in the middle of each thicket
            mid = sorted(inner)[len(inner) // 2]
            m.clear_items(mid[0], mid[1], Z); m.put(mid[0], mid[1], Z, 3623)
        if c["core"] == "oakgrove" and len(inner) > 12:        # one mud wallow in each grove, seen through the trees
            mid = sorted(inner)[len(inner) // 2]
            for a in (0, 1):
                for b in (0, 1):
                    q = (mid[0] + a, mid[1] + b)
                    if q in inner and _interior(inner, rect).__contains__(q) or q == mid:
                        m.ground[(q[0], q[1], Z)] = m.pick("mud"); m.clear_items(q[0], q[1], Z)
        if c["core"] == "banditcamp":                          # the camp heap: a fence ring, a fire in the middle
            ring = core - inner
            hz = {t for t in ring if (t[0] + 1, t[1]) in ring or (t[0] - 1, t[1]) in ring}
            for t in ring:
                m.clear_items(t[0], t[1], Z)
                m.put(t[0], t[1], Z, 17233 if t in hz else 17232)
            if inner:
                mid = sorted(inner)[len(inner) // 2]
                m.clear_items(mid[0], mid[1], Z); m.put(mid[0], mid[1], Z, 1996)
    # the open places: trail ground, a little walk-over dressing at the edges
    for (x, y) in opn:
        m.ground[(x, y, Z)] = m.pick(trail_key)
        m.clear_items(x, y, Z)
    if L.get("wallow"):
        for (x, y) in L["wallow"]["clear"] | L["wallow"]["gap"]:
            m.ground[(x, y, Z)] = m.pick("mud")
    patches = set().union(*[lp["patches"] for lp in L["loops"]])
    edge_open = [t for t in opn if any((t[0] + a, t[1] + b) not in opn for a, b in D4) and t not in patches
                 and t not in L["gate"] and t not in L["hub"]]
    for t in edge_open:
        if rng.random() < 0.07:
            m.put(t[0], t[1], Z, rng.choice(WALKOVER[trail_key]))
    # the hub: a sign at the gate, a fire and a bench
    lo, hi = c["levels"]
    m.sign(*L["gate_sign"], Z, f"{c['title']}. Levels {lo} to {hi}. Four loops: north-west, north-east, south-west, south-east.")
    m.put(*L["fire"], Z, 1996)
    m.put(*L["bench"], Z, 2370)
    for lp in L["loops"]:
        sx, sy = lp["sign"]
        if (sx, sy) not in opn:
            m.clear_items(sx, sy, Z)
            m.sign(sx, sy, Z, f"{SIDE_WORDS[lp['name']].capitalize()} loop. {c['title']}, levels {lo} to {hi}.")
    # monster groups: fixed places on each loop's ring (plan Part 5.2.6); crowd spots are named points only (Part 7)
    gid = c["id"]
    for lp in L["loops"]:
        for k, (gx, gy) in enumerate(lp["groups"]):
            members = [mon for mon, n in c["groups"][k] for _ in range(n)]
            spots = sorted(lp["patches"] & {(gx + a, gy + b) for a in (-1, 0, 1) for b in (-1, 0, 1)},
                           key=lambda t: (abs(t[0] - gx) + abs(t[1] - gy), t))
            kids = [(mon, sx - gx, sy - gy, spawn_time(ELITE_RESPAWN if mon in ELITES else c["respawn"]))
                    for mon, (sx, sy) in zip(members, spots)]
            m.monsters.append((kids, (gx, gy, Z), 2, len(kids), spawn_time(c["respawn"])))
        for n, (cx_, cy_) in enumerate(lp["crowd"], 1):
            m.points[f"crowd_{gid}_{lp['name']}_{n}"] = (cx_, cy_, Z)
        m.points[f"loop_{gid}_{lp['name']}"] = lp["mouth_pt"] + (Z,)
    m.points["camp_" + gid] = L["camp"] + (Z,)
    xs = [p[0] for p in rect]; ys = [p[1] for p in rect]
    m.points[f"ground_{gid}_nw"] = (min(xs), min(ys), Z)        # the ground's rectangle (crowd system, tests)
    m.points[f"ground_{gid}_se"] = (max(xs), max(ys), Z)
    m.points[f"gate_{gid}"] = (sum(p[0] for p in L["gate"]) // len(L["gate"]), sum(p[1] for p in L["gate"]) // len(L["gate"]), Z)
    m.points[f"centre_{gid}"] = L["centre"] + (Z,)
    if not hasattr(m, "wilds"):
        m.wilds = []
    m.wilds.append(L)
    return L


# ------------------------------------------------------------------------------------------------ walk test
def blockers():
    """Item and ground ids that cannot be walked on: from the game's appearances file when it is on this PC, otherwise a
    list of everything the wilds use that blocks."""
    from pathlib import Path
    root = Path(__file__).resolve().parent.parent
    try:
        import sys
        sys.path.insert(0, str(root / "tools"))
        import appearances
        path = next((root / ".local" / "client").glob("**/appearances-*.dat"))
        return {i for i, (f, _n) in appearances.load(str(path)).items() if f.get("unpass")}
    except (StopIteration, OSError, ImportError):
        from mapgen import WALL_IDS
        ids = set(WALL_IDS) | set(TREES_ALL_BROAD + FIRS + ROCKS + REEDS + S.THORNS + S.BUSHES + S.TREES_DEAD + S.BOULDERS)
        ids |= {3751, 3754, 3698, 1784, 1785, 1786, 2264, 2290, 2012, 5543, 116, 17232, 17233, 1081, 1082, 1085, MOUNTAIN}
        ids |= set(range(4457, 4469)) | set(range(4597, 4645))
        return ids


def walkable(m, p, block):
    g = m.ground.get(p)
    if g is None or g in block:
        return False
    return not any(i in block for i, _a in m.items.get(p, []))


def flood(m, starts, block, inside=None, limit=None):
    seen, todo = set(), [s for s in starts if walkable(m, s, block)]
    seen.update(todo)
    while todo:
        x, y, z = todo.pop()
        for a, b in D8:
            q = (x + a, y + b, z)
            if q in seen or (inside is not None and (q[0], q[1]) not in inside):
                continue
            if limit and not (limit[0] <= q[0] < limit[2] and limit[1] <= q[1] < limit[3]):
                continue
            if walkable(m, q, block):
                seen.add(q)
                todo.append(q)
    return seen


def check(m, home):
    """The walk test (plan Part 5.2.9). Run after Map.finish() so edge pieces and whole objects are in place.
    Returns a list of problems (empty = every ground passes)."""
    block = blockers()
    problems = []
    world = flood(m, [home], block, limit=(X0, Y0, X0 + 400, Y0 + 400))
    for L in getattr(m, "wilds", []):
        gid, rect = L["id"], L["rect"]
        gate = [(x, y, Z) for x, y in L["gate"]]
        if not any(g in world for g in gate):
            problems.append(f"{gid}: the gate cannot be reached from the Hearthstone")
        inside = flood(m, gate, block, inside=rect)
        xs = [p[0] for p in rect]; ys = [p[1] for p in rect]
        edge = {(x, y) for (x, y) in rect if x in (min(xs), max(xs)) or y in (min(ys), max(ys))}
        leak = [(x, y) for (x, y, _z) in inside if (x, y) in edge and (x, y) not in L["gate"]]
        if leak:
            problems.append(f"{gid}: the outer wall has a hole at {leak[:3]}")
        outside = flood(m, [(x, y, Z) for (x, y) in rect if (x, y) in edge and (x, y) not in L["gate"]], block, inside=rect)
        for lp in L["loops"]:
            for pt in lp["groups"] + lp["crowd"]:
                if (pt[0], pt[1], Z) not in inside:
                    problems.append(f"{gid}: {lp['name']} spot {pt} cannot be reached from the gate")
            bad = [t for t in lp["ring"] if not walkable(m, (t[0], t[1], Z), block)]
            if bad:
                problems.append(f"{gid}: {lp['name']} loop trail is blocked at {bad[:3]}")
                continue
            # a closed ring: cut it next to the mouth; the two ends must still meet the long way round
            rest = lp["ring"] - lp["cut"]
            if rest:
                s = next(iter(rest))
                reach = flood(m, [(s[0], s[1], Z)], block, inside=rest)
                if len(reach) < len(rest):
                    problems.append(f"{gid}: {lp['name']} loop is not a closed ring")
        if outside & inside:
            problems.append(f"{gid}: the inside can be reached without the gate")
    return problems


if __name__ == "__main__":
    # scratch test (plan task W2): every ground on a blank meadow must build and pass the walk test
    import os
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
    from mapgen import Map
    from floor1_plan import CAMPS
    only = sys.argv[1:] or [c["id"] for c in CAMPS]
    fails = 0
    for c in CAMPS:
        if c["id"] not in only:
            continue
        m = Map()
        m.fill(X0 + c["x"] - 6, Y0 + c["y"] - 6, c["w"] + 12, c["h"] + 12, Z, "grass")
        L = build(m, c)
        gx, gy, _ = m.points["gate_" + c["id"]]
        step = {"n": (0, -1), "s": (0, 1), "e": (1, 0), "w": (-1, 0)}[c["gate"]]
        m.finish()
        probs = check(m, (gx + 3 * step[0], gy + 3 * step[1], Z))
        n = sum(len(k) for kids, *_r in m.monsters for k in [kids])
        print(f"{c['id']:18s} groups {len(m.monsters):3d} monsters {n:3d}  " + ("OK" if not probs else "; ".join(probs[:4])))
        fails += bool(probs)
    sys.exit(1 if fails else 0)
