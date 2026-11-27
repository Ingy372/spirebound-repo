"""Floor 1 depth, Session D (roadmap FD2; docs/superpowers/specs/2026-11-27-floor1-depth-design.md 4.2): one feature per
hunting ground that is used, not just seen, and the Town Works' map pieces (FD5, 4.5).

This module only places what stands still (a bell, nests, a stone, crystals, a poster, a winch, bushes...) and names
the spots the scripts need (m.points "feat_..."). Everything that changes while the server runs (lily paths at night, the
tide, the vine walls, finished Works) is done by scripts/spirebound/ground_features.lua and works.lua at those spots, so
the walk test always sees the plain map.

Map rules (CLAUDE.md): never on the gate side of the hub, nothing on trails, roads, doorways or spawns, whole objects.
"""
import dungeon as DG
import scenery as S

Z = 7
# the bell is a lamp-on-a-post placeholder: a carryable bell item could not be used where it stood (client test)
BELL, NEST, HOWL_STONE, BALLISTA, WINCH, CACHE, STASH, BRAZIER = 2117, 48576, 4850, 2065, 2772, 2478, 1772, 2113
SHARDS = [7808, 7809, 7810, 7811]          # the four chime shards (blue, deep blue, light blue, red)
BERRY_BUSH = 3699                           # a blueberry bush (the core script picks it; the berries are bramble berries)
MOUND = 1787                                # a mole mound (placeholder: a heap of earth and stones)
WATER = set(range(4597, 4626)) - {4621}     # the water grounds (4621 is a sandy shore piece and walkable)
SIGN = 2012


def _ground(m, gid):
    return next(L for L in m.wilds if L["id"] == gid)


def _dist(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def _gate(L):
    g = sorted(L["gate"])
    return g[len(g) // 2]


def _busy(m, z):
    """tiles to leave alone: points, spawns (3x3), signs, teleports, roads"""
    out = DG.keep_clear(m, z)
    out |= {(t[0], t[1]) for t in getattr(m, "road_tiles", set()) if len(t) == 2 or t[2] == z}
    return out


NATURAL = set(S.TREES_BROAD + S.TREES_FIR + S.TREES_DEAD + S.BUSHES + S.THORNS + S.FLOWERS + S.FERNS + S.STONES)


def _free(m, x, y, z, busy, natural_ok=False):
    """a tile with ground and nothing on it; natural_ok: a lone tree, bush, flower or stone may be cleared away"""
    if (x, y, z) not in m.ground or (x, y) in busy or m.ground[(x, y, z)] in WATER:
        return False
    items = m.items.get((x, y, z), [])
    return not items or (natural_ok and all(i in NATURAL for i, _a in items))


def _beside_trail(m, L, z, busy, near, min_gate=9, k=1, gap=6, cells=None):
    """free tiles just off a trail (never on it), far enough from the gate, closest to `near`; k of them, `gap` apart"""
    gate = _gate(L)
    open_ = cells if cells is not None else (L["open"] if z == Z else L["levels"].get(z, set()))
    cand = []
    for (x, y) in sorted(L["rect"] if z == Z else L["boxes"].get(z, set())):
        if (x, y) in open_ or not _free(m, x, y, z, busy, natural_ok=True):
            continue
        if not any((x + dx, y + dy) in open_ for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
            continue
        if z == Z and _dist((x, y), gate) < min_gate:
            continue
        cand.append((_dist((x, y), near), (x, y)))
    cand.sort()
    out = []
    for _d, p in cand:
        if all(_dist(p, q) >= gap for q in out):
            out.append(p)
        if len(out) == k:
            break
    return out


def _hub_far(m, L, busy):
    """a free hub tile on the hub's edge, as far from the gate as the hub goes (the gate side stays quiet)"""
    gate, best = _gate(L), None
    for (x, y) in sorted(L["hub"]):
        if not _free(m, x, y, Z, busy) or (x, y) in L["gate"]:
            continue
        edge = any((x + dx, y + dy) not in L["open"] for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
        if not edge:
            continue
        d = _dist((x, y), gate)
        if best is None or d > best[0]:
            best = (d, (x, y))
    return best[1] if best else None


def _hub_line(m, L, line):
    """add one plain line about the ground's feature to its hub sign (designed.py puts it at camp + (3, -3))"""
    hx, hy = L["camp"]
    for p in ((hx + 3, hy - 3, Z),) + tuple((x, y, Z) for (x, y) in sorted(L["hub"])):
        items = m.items.get(p, [])
        for i, (iid, attrs) in enumerate(items):
            if iid == SIGN and attrs[:1] == bytes([6]):
                n = attrs[1] | (attrs[2] << 8)
                text = attrs[3:3 + n].decode("latin-1") + " " + line
                b = text.encode("latin-1")
                items[i] = (iid, bytes([6]) + bytes([len(b) & 0xFF, len(b) >> 8]) + b)
                return True
    return False


def _place(m, name, x, y, z, iid):
    m.clear_items(x, y, z)
    m.put(x, y, z, iid)
    m.points[name] = (x, y, z)


# ---------------------------------------------------------------- the grounds
def ratwarren(m, busy):
    L = _ground(m, "starter_west")
    p = _hub_far(m, L, busy)
    _place(m, "feat_bell", p[0], p[1], Z, BELL)
    _hub_line(m, L, "The Ratcatcher's Bell hangs here: ring it, if you dare.")


def toad_pond(m, busy):
    """Night lilies: a pond with no bridge gets an island; at night a lily path rises to it (the script swaps the path's
    water for lily pads). On the island: a spot where night fish bite, and toads at night."""
    L = _ground(m, "starter_east")
    water = {(x, y) for (x, y) in L["rect"] if m.ground.get((x, y, Z)) in WATER}
    seen, ponds = set(), []
    for t in sorted(water):
        if t in seen:
            continue
        comp, todo = set(), [t]
        while todo:
            c = todo.pop()
            if c in comp or c not in water:
                continue
            comp.add(c)
            todo += [(c[0] + 1, c[1]), (c[0] - 1, c[1]), (c[0], c[1] + 1), (c[0], c[1] - 1)]
        seen |= comp
        ponds.append(comp)
    gate = _gate(L)

    def island_of(comp):
        """the 2x2 of the pond whose every tile is at least 2 tiles from its shore"""
        best = None
        for (x, y) in sorted(comp):
            sq = [(x, y), (x + 1, y), (x, y + 1), (x + 1, y + 1)]
            if all((a + dx, b + dy) in comp for a, b in sq for dx in (-1, 0, 1) for dy in (-1, 0, 1)):
                cx = sum(a for a, _ in comp) / len(comp)
                cy = sum(b for _, b in comp) / len(comp)
                d = abs(x + 0.5 - cx) + abs(y + 0.5 - cy)
                if best is None or d < best[0]:
                    best = (d, sq)
        return best[1] if best else None

    pond, isle = None, None
    for comp in sorted(ponds, key=lambda c: (-len(c), min(c))):
        bridged = any(m.items.get((x, y, Z)) for (x, y) in comp)
        sq = island_of(comp)
        if sq and not bridged and _dist(min(comp), gate) >= 9:
            pond, isle = comp, sq
            break
    if not pond:
        raise ValueError("Toad Pond: no unbridged pond is big enough for the night island")
    for i, (x, y) in enumerate(isle):
        m.ground[(x, y, Z)] = m.pick("grass")
        m.clear_items(x, y, Z)
        if i in (1, 2):              # a flower on two corners: land with something on it is never tidied into water
            m.put(x, y, Z, 6225)
    # the lily path: the shortest straight line of water from the shore to the island
    best = None
    for (ix, iy) in isle:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            path, x, y = [], ix + dx, iy + dy
            while (x, y) in pond and (x, y) not in isle:
                path.append((x, y))
                x, y = x + dx, y + dy
            shore = (x, y)
            if path and shore not in pond and (shore[0], shore[1], Z) in m.ground and \
                    m.ground[(shore[0], shore[1], Z)] not in WATER and not m.items.get((shore[0], shore[1], Z)):
                if best is None or len(path) < len(best[0]):
                    best = (path, shore)
    if not best:
        raise ValueError("Toad Pond: no straight way from the shore to the island")
    path, shore = best
    for i, (x, y) in enumerate(path):
        m.points[f"feat_lily_{i + 1}"] = (x, y, Z)
    m.points["feat_lily_shore"] = (shore[0], shore[1], Z)
    ring = [(x + dx, y + dy) for (x, y) in isle for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))]
    fish = next(t for t in sorted(ring) if t in pond and t not in path)
    m.points["feat_nightfish"] = (fish[0], fish[1], Z)
    m.points["feat_island"] = (isle[0][0], isle[0][1], Z)
    m.points["feat_island_2"] = (isle[3][0], isle[3][1], Z)
    _hub_line(m, L, "On clear nights, they say, lilies rise across one of the ponds.")


def wasp_fields(m, busy):
    L = _ground(m, "wasp_fields")
    starts = [L["routes"][r]["start"] for r in sorted(L["routes"]) if L["routes"][r]["start"][2] == Z]
    n = 0
    for s in starts:
        for (x, y) in _beside_trail(m, L, Z, busy, s[:2], k=2, gap=8):
            n += 1
            _place(m, f"feat_nest_{n}", x, y, Z, NEST)
    _hub_line(m, L, "Smoke a wasp nest out with a lit torch for its honeycomb, and mind the queen.")


def boar_meadow(m, busy):
    _hub_line(m, _ground(m, "boar_meadow"), "Leave a rooting boar be: where it digs, a shovel may find a truffle.")


def sproutling_glade(m, busy):
    _hub_line(m, _ground(m, "starter_south"), "Stamp out the seedlings fallen sproutlings leave, or an elder will grow.")


def burrow_hills(m, busy):
    L = _ground(m, "burrow_hills")
    n = 0
    # surface and cellar loops only: a mound on a hill top is tidied away by the edge pass, and one landed on a ramp's
    # foot (boot test, 2026-11-27)
    starts = [L["routes"][r]["start"] for r in sorted(L["routes"]) if L["routes"][r]["start"][2] in (7, 8)]
    if len(starts) < 4:
        starts.append(L["centre"] + (7,) if len(L["centre"]) == 2 else L["centre"])
    for s in starts:
        spot = _beside_trail(m, L, s[2], _busy(m, s[2]), s[:2], min_gate=10)
        if spot:
            n += 1
            _place(m, f"feat_mole_{n}", spot[0][0], spot[0][1], s[2], MOUND)
    if n < 3:
        raise ValueError(f"Burrow Hills: only {n} mole mounds found room")
    _hub_line(m, L, "The moles' tunnels join the four loops: use a mound to dive in.")


def wolf_copse(m, busy):
    L = _ground(m, "wolf_copse")
    p = _hub_far(m, L, busy)
    _place(m, "feat_howl", p[0], p[1], Z, HOWL_STONE)
    _hub_line(m, L, "The Howling Stone calls every wolf of a loop at once. Bigger packs answer at night.")


def reed_marsh(m, busy):
    """The tide: water tiles touching land (no further than 2 from the shore) become sandbars for 10 minutes of every 30"""
    L = _ground(m, "reed_marsh")
    gate = _gate(L)
    water = {(x, y) for (x, y) in L["rect"] if m.ground.get((x, y, Z)) in WATER}
    shore = {t for t in water if any((t[0] + dx, t[1] + dy) not in water and (t[0] + dx, t[1] + dy, Z) in m.ground
                                     for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))}
    bars = sorted(t for t in shore if _dist(t, gate) >= 10 and not m.items.get((t[0], t[1], Z)))
    if len(bars) < 12:
        raise ValueError(f"Reedmarsh: only {len(bars)} shore tiles for the tide")
    step = max(1, len(bars) // 40)
    bars = bars[::step][:40]
    for i, (x, y) in enumerate(bars):
        m.points[f"feat_tide_{i + 1}"] = (x, y, Z)
    _hub_line(m, L, "Every half hour the water drops for a while: look for turtle nests on the sandbars.")


def thornsnap_hollow(m, busy):
    """Vine walls: trail cuts 2-3 tiles across where the scripts grow vines (never on the hub or a spawn)"""
    L = _ground(m, "thornsnap_hollow")
    gate, open_ = _gate(L), L["open"]
    cuts = []
    for (x, y) in sorted(open_):
        if (x, y) in L["hub"] or _dist((x, y), gate) < 14:
            continue
        for horiz in (True, False):
            run = []
            if horiz:      # a corridor running north-south: cut it east-west
                if (x - 1, y) in open_:
                    continue
                k = x
                while (k, y) in open_:
                    run.append((k, y)); k += 1
                ok = (x, y - 1) in open_ and (x, y + 1) in open_
            else:
                if (x, y - 1) in open_:
                    continue
                k = y
                while (x, k) in open_:
                    run.append((x, k)); k += 1
                ok = (x - 1, y) in open_ and (x + 1, y) in open_
            if ok and 2 <= len(run) <= 3 and all(t not in busy and not m.items.get((t[0], t[1], Z)) for t in run):
                cuts.append(run)
    chosen = []
    for run in cuts:
        if all(_dist(run[0], c[0]) >= 9 for c in chosen):
            chosen.append(run)
        if len(chosen) == 8:
            break
    if len(chosen) < 4:
        raise ValueError(f"Thornsnap Hollow: only {len(chosen)} places for vine walls")
    for i, run in enumerate(chosen):
        for j, (x, y) in enumerate(run):
            m.points[f"feat_vine_{i + 1}_{j + 1}"] = (x, y, Z)
    _hub_line(m, L, "Vines close the trails and grow back: cut them with a sword or axe, or burn them with a lit torch.")


def shard_fields(m, busy):
    L = _ground(m, "shard_fields")
    s = L["routes"]["d"]["start"] if L["routes"]["d"]["start"][2] == Z else L["routes"]["a"]["start"]
    spots = _beside_trail(m, L, Z, busy, s[:2], k=5, gap=2)
    if len(spots) < 5:
        raise ValueError("Shard Fields: no room for the four chimes and the cache")
    for i, (x, y) in enumerate(spots[:4]):
        _place(m, f"feat_chime_{i + 1}", x, y, Z, SHARDS[i])
    _place(m, "feat_cache", spots[4][0], spots[4][1], Z, CACHE)
    _hub_line(m, L, "Four shards ring when struck. Every few minutes the wind plays them in turn.")


def bandit_road(m, busy):
    L = _ground(m, "bandit_road")
    gate = _gate(L)
    # the poster: beside the gate, inside (posters, not monsters: the gate side stays quiet)
    best = None
    for (x, y) in sorted(L["hub"]):
        if _free(m, x, y, Z, busy) and (x, y) not in L["gate"] and \
                any((x + dx, y + dy) not in L["open"] for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
            d = _dist((x, y), gate)
            if best is None or d < best[0]:
                best = (d, (x, y))
    x, y = best[1]
    m.clear_items(x, y, Z)
    m.sign(x, y, Z, "WANTED: a Bandit Lieutenant, out on this road. Use this poster to hear where he was last seen; "
           "bring his badge here for the bounty.")
    m.points["feat_poster"] = (x, y, Z)


def old_quarry(m, busy):
    """The lift: a platform on the quarry floor under the upper ledge; one player works the winch, the other rides up"""
    L = _ground(m, "old_quarry")
    top = L["levels"].get(6, set())
    if not top:
        raise ValueError("Old Quarry: no upper ledge")
    gate, best = _gate(L), None
    for (x, y) in sorted(L["open"]):
        if (x, y) in busy or (x, y) in L["hub"] or m.items.get((x, y, Z)) or _dist((x, y), gate) < 10:
            continue
        near = [t for t in top if _dist(t, (x, y)) <= 4 and not m.items.get((t[0], t[1], 6))]
        if not near:
            continue
        winch = _beside_trail(m, L, Z, busy, (x, y), min_gate=8, gap=1, cells=L["open"])
        if winch and _dist(winch[0], (x, y)) == 1:
            score = _dist((x, y), gate)
            if best is None or score < best[0]:
                best = (score, (x, y), winch[0], min(near))
    if not best:
        raise ValueError("Old Quarry: no spot for the lift")
    _s, plat, winch, land = best
    m.points["feat_lift_platform"] = (plat[0], plat[1], Z)
    _place(m, "feat_lift_winch", winch[0], winch[1], Z, WINCH)
    m.points["feat_lift_top"] = (land[0], land[1], 6)
    _hub_line(m, L, "An old winch lifts a climber to the upper ledge, if a friend turns it.")


def watchtower(m, busy):
    """The signal fire: a brazier in the middle of the keep"""
    ax, ay = m.points["apex_watchtower"][0] - 22, m.points["apex_watchtower"][1] - 40
    x, y = ax + 22, ay + 22
    for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1)):
        if not m.items.get((x + dx, y + dy, Z)) and (x + dx, y + dy) not in busy:
            x, y = x + dx, y + dy
            break
    _place(m, "feat_signal", x, y, Z, BRAZIER)
    m.points["feat_signal_nw"] = (ax + 13, ay + 13, Z)
    m.points["feat_signal_se"] = (ax + 30, ay + 30, Z)
    m.sign(x + 1, y + 1, Z, "The signal brazier of the Old Watchtower. Light it and hold the keep while the ruin answers: "
           "a lit fire makes the whole tower richer for a while, and the server hears who lit it.") \
        if not m.items.get((x + 1, y + 1, Z)) else None


def bramble_run(m, busy):
    """Bramble berries: bushes along the loops (the core script picks a bush; it grows back). Rousing a thornsnap now
    and then, and the berries feed two dishes."""
    L = _ground(m, "bramble_run")
    n = 0
    for r in sorted(L["routes"]):
        s = L["routes"][r]["start"]
        for (x, y) in _beside_trail(m, L, Z, busy, s[:2], k=2, gap=5):
            n += 1
            _place(m, f"feat_berry_{n}", x, y, Z, BERRY_BUSH)
    _hub_line(m, L, "Bramble berries grow along the loops. Pick them, and listen for what sleeps under the bush.")


def smugglers_ridge(m, busy):
    """Contraband stashes: one loose stone per loop; each hour one of them holds a stash (it glints now and then)"""
    L = _ground(m, "smugglers_ridge")
    n = 0
    for r in sorted(L["routes"]):
        s = L["routes"][r]["start"]
        spot = _beside_trail(m, L, Z, busy, s[:2], min_gate=10)
        if spot:
            n += 1
            _place(m, f"feat_stash_{n}", spot[0][0], spot[0][1], Z, STASH)
    _hub_line(m, L, "The smugglers hide their goods under loose stones. Watch for a glint, and for whoever comes to collect.")


def fallen_bastion(m, busy):
    L = _ground(m, "fallen_bastion")
    p = _hub_far(m, L, busy)
    _place(m, "feat_ballista", p[0], p[1], Z, BALLISTA)
    _hub_line(m, L, "The bastion's old ballista still shoots: use it to loose a bolt at the nearest ruin guards.")


def build(m):
    busy = _busy(m, Z)
    for f in (ratwarren, toad_pond, sproutling_glade, wasp_fields, boar_meadow, burrow_hills, wolf_copse, reed_marsh,
              thornsnap_hollow, shard_fields, bandit_road, old_quarry, watchtower, bramble_run, smugglers_ridge,
              fallen_bastion):
        f(m, busy)
        busy = _busy(m, Z)


# ================================================================ FD5: the Town Works' map pieces (design 4.5)
# Each project is a list of pieces the server lays when the project is finished (and again at every start), kept in
# server/data-spirebound/lib/spirebound/works_pieces.lua (written here). Before that, the unfinished state stands on the
# map: a broken bridge, unlit lamp posts, an empty camp site, a blocked keep gate, a bare Monument.
WORKS_OUT = __import__("pathlib").Path(__file__).resolve().parent.parent / "server/data-spirebound/lib/spirebound/works_pieces.lua"
LAMP_UNLIT, LAMP_LIT, BRIDGE, BANNER, RUBBLE_HEAP = 8659, 8660, 408, 8526, 5866
CAMPFIRE, CRATE, HEALER, BENCH = 1996, 8772, 2025, 2370


def _w_free(m, x, y, z=Z):
    return (x, y, z) in m.ground and not m.items.get((x, y, z)) and m.ground[(x, y, z)] not in WATER and \
        (x, y) not in m.road_tiles and (x, y, z) not in m.road_tiles


def works(m):
    P = {1: [], 2: [], 3: [], 4: [], 5: [], "banners": []}
    # 1. The River Bridge: south of the old bridges, a short way from the cabins to the marsh side
    for y in (1318, 1319):
        run = [x for x in range(1100, 1140) if m.ground.get((x, y, Z)) in WATER]
        if not 3 <= len(run) <= 7:
            raise ValueError(f"Works: the river at y {y} is {len(run)} wide, not a bridge site")
        m.ground[(run[0], y, Z)] = BRIDGE                      # the broken ends that stand there today
        m.ground[(run[-1], y, Z)] = BRIDGE
        for x in run[1:-1]:
            P[1].append(dict(x=x, y=y, z=Z, op="ground", id=BRIDGE))
    m.points["works_bridge"] = (run[0] - 1, 1318, Z)
    # 2. The Road Lanterns: unlit posts along the road from Millcross to the river bank
    for x in range(1062, 1100, 8):
        for y in (1223, 1224, 1218, 1217):
            if _w_free(m, x, y) and not any(_w_free(m, x, yy) is False and m.items.get((x, yy, Z)) for yy in ()):
                m.put(x, y, Z, LAMP_UNLIT)
                P[2].append(dict(x=x, y=y, z=Z, op="transform", id=LAMP_LIT, src=LAMP_UNLIT))
                break
    # 3. The Stair Camp: an empty site beside the north road at the foot of the labyrinth
    cx, cy = 1236, 1096
    site = [(cx + dx, cy + dy) for dx in range(0, 7) for dy in range(0, 5)]
    for (x, y) in site:
        if (x, y, Z) in m.ground and m.ground[(x, y, Z)] not in WATER:
            m.clear_items(x, y, Z)
    m.sign(cx, cy, Z, "The site of the Stair Camp. The Works Board in Hearthgate's Hearth raises the money to build it.")
    m.points["works_camp"] = (cx + 3, cy + 2, Z)
    for (dx, dy, iid) in ((3, 2, CAMPFIRE), (1, 4, CRATE), (5, 4, HEALER), (2, 1, BENCH), (4, 1, BENCH)):
        P[3].append(dict(x=cx + dx, y=cy + dy, z=Z, op="item", id=iid))
    # 4. The Watchtower's north gate: the keep's second way in, today a heap of fallen stone
    ax, ay = m.points["apex_watchtower"][0] - 22, m.points["apex_watchtower"][1] - 40
    for x in (ax + 21, ax + 22):
        m.put(x, ay + 11, Z, RUBBLE_HEAP) if not m.items.get((x, ay + 11, Z)) else None
        P[4].append(dict(x=x, y=ay + 11, z=Z, op="clear"))
        P[4].append(dict(x=x, y=ay + 12, z=Z, op="clear"))
    # 5. The Monument Garden: flower beds and two benches round the Monument, and the givers' plaque
    mx, my = m.points["monument"][0], m.points["monument"][1]
    n = 0
    for r in (2, 3):
        for dx in range(-r, r + 1):
            for dy in (-r, r):
                for (x, y) in ((mx + dx, my + dy), (mx + dy, my + dx)):
                    if _w_free(m, x, y) and (x, y) not in {(p["x"], p["y"]) for p in P[5]} and n < 12:
                        P[5].append(dict(x=x, y=y, z=Z, op="item", id=S.FLOWERS[n % len(S.FLOWERS)]))
                        n += 1
    benches = [(mx + dx, my + 3) for dx in (-3, 3)] + [(mx + dx, my - 3) for dx in (-3, 3)]
    for (x, y) in benches[:2]:
        if _w_free(m, x, y):
            P[5].append(dict(x=x, y=y, z=Z, op="item", id=BENCH))
    # the Works Board: beside the notice board
    nb = m.points["hearth_notice_board"]
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, 1), (2, 0), (-2, 0)):
        x, y = nb[0] + dx, nb[1] + dy
        if _w_free(m, x, y):
            m.put(x, y, Z, 2597)
            m.points["works_board"] = (x, y, Z)
            break
    if "works_board" not in m.points:
        raise ValueError("Works: no room for the Works Board beside the notice board")
    # banners on Hearthgate's four gates after the Axe-Lord's first fall each season
    for (x, y) in ((1229, 1235), (1236, 1235), (1229, 1332), (1236, 1332), (1175, 1282), (1175, 1288), (1288, 1282), (1288, 1288)):
        if (x, y, Z) in m.ground and not m.items.get((x, y, Z)):
            P["banners"].append(dict(x=x, y=y, z=Z, op="item", id=BANNER))

    def row(p):
        return "{ " + ", ".join(f'{k} = {v if not isinstance(v, str) else chr(34) + v + chr(34)}' for k, v in p.items()) + " }"
    L = ["-- Generated by maps/floor1_features.py (tools/mapgen.py): the Town Works' finished pieces. Do not edit by hand.",
         "SpireWorksPieces = {"]
    for k in (1, 2, 3, 4, 5):
        L.append(f"\t[{k}] = {{")
        L += [f"\t\t{row(p)}," for p in P[k]]
        L.append("\t},")
    L.append("\tbanners = {")
    L += [f"\t\t{row(p)}," for p in P["banners"]]
    L.append("\t},")
    L.append("}")
    WORKS_OUT.write_bytes(("\n".join(L) + "\n").encode("utf-8"))
    return P


_build_features = build


def build(m):
    _build_features(m)
    works(m)
