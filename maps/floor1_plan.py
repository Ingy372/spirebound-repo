"""Floor 1 plan: the one place that says where the hunting grounds are and what lives in them.

Read by maps/layout_floor1.py (draws the map and places the monsters), tools/gen_bestiary.py (BESTIARY.md and the in-game
hunting guide), tools/gen_economy.py (ECONOMY.md) and tools/wilds_plan_check.py (the plan picture and its overlap check),
so none of them can disagree.

Coordinates are tiles relative to the corner of Floor 1 (the map builder adds X0, Y0). Floor 1 is 400 x 400.
Hearthgate (the walled city) occupies x 176..287, y 236..331.

The wilds rebuild (FLOOR1_WILDS_PLAN.md, 2026-11-12/13). Every hunting ground is a walled place:
  * a 2-tile outer wall (thicket, rock or water) with one 3-wide gate;
  * a hub (clearing) inside the gate, with a sign, a fire and a bench;
  * four hunting loops: a 2-wide ring trail around a solid core, monster groups at fixed spots on the ring;
  * cross trails between the loops; six grounds have a cave (z 8) under the middle, for parties.
One loop feeds one player hunting flat out (the Tibia rule, plan Part 5.3):
    respawn seconds = 2,770 x monsters in the loop / kills per hour of one player there.
"respawn" below is the REAL wait. The engine waits about twice its spawn-file number (W0, PROGRESS.md 2026-11-13), so the
map builder writes half of it into the spawn file (see spawn_time()).
"""

TOWN = dict(x=176, y=236, w=112, h=96)          # Hearthgate, walled
MILLCROSS = dict(x=35, y=195, w=64, h=44)       # the village west of the river

# The loop skeleton (plan Part 5.1): loop box (w, h), cross trail width, hub depth, groups and crowd spots per loop.
SIZES = {
    "small": dict(loop=(18, 16), cross=2, hub=6, groups=4, crowd=4),
    "std": dict(loop=(24, 18), cross=3, hub=8, groups=6, crowd=3),
    "tall": dict(loop=(18, 24), cross=3, hub=6, groups=6, crowd=3),
}
ELITE_RESPAWN = 900                               # Grey Alpha, Bandit Captain: 15 minutes
ELITES = {"Grey Alpha", "Bandit Captain", "Old Bristleback", "Moonhowl", "Mossback Snapper", "Blackthorn", "Prism Shardling",
          "Granite Warden"}
CAVE_RESPAWN = 160


def G(*parts):
    """One monster group: G(("Meadow Wolf", 3)) or G(("Grey Alpha", 1), ("Meadow Wolf", 2))."""
    return [p for p in parts]


def same(n, monster, count=3):
    return [G((monster, count)) for _ in range(n)]


# type (DESIGN.md 9.4): training / class (cls = the class it suits) / mixed / group / large; every party cave (den)
# is a group ground inside its ground. Habits, weights and budgets: tools/balance.py.
# id, title, x, y, w, h, gate side, loop size, zone, levels, role, note,
# wall / core / trail = how the ground is dressed (plan Part 6), groups = the groups on EACH loop,
# respawn = real seconds (plan Part 5.3), den = cave name, den_groups = the cave's 8 groups (plan Part 5.4).
CAMPS = [
    dict(id="starter_west", type="training", title="The Ratwarren", x=134, y=242, w=38, h=40, gate="s", size="small", zone="guarded",
         levels=(1, 4), role="xp", wall="broadleaf", core="mounds", trail="dirt", decor="rats",
         groups=same(4, "Field Rat"), respawn=110, design="RATWARREN",
         note="Your first fights. Hit it, loot it, hit the next. Safe: no one can attack you here."),
    dict(id="starter_east", type="training", title="Toad Pond", x=294, y=230, w=70, h=52, gate="s", size="small", zone="guarded", design="TOADPOND",
         levels=(3, 7), role="xp", wall="broadleaf", core="pond", trail="grass", decor="pond",
         groups=same(3, "Hopper Toad") + same(1, "Field Rat"), respawn=110,
         note="Toads hit a little harder and give a little more. Five ponds, five loops; fishing works here."),
    dict(id="starter_south", type="training", title="Sproutling Glade", x=184, y=338, w=44, h=56, gate="n", size="small", zone="guarded", design="GLADE",
         levels=(5, 10), role="xp", wall="ferns", core="grove", trail="grass", decor="glade",
         groups=same(3, "Sproutling") + same(1, "Hopper Toad"), respawn=110,
         note="Sproutlings spit a little poison-green magic. Still inside the Guarded ring around town."),
    dict(id="wasp_fields", type="class", cls="Arcanist", title="Waspgrass Fields", x=160, y=180, w=68, h=50, gate="e", size="small", zone="guarded", design="WASPS",
         levels=(7, 12), role="xp", wall="hedge", core="flowerbed", trail="grass", decor="wasps",
         groups=same(4, "Meadow Wasp"), respawn=110,
         note="Fast and stingy, little health. Just north of the city gate, beside the Pass road."),
    dict(id="boar_meadow", type="class", cls="Vanguard", title="Boar Meadow", x=140, y=338, w=39, h=57, gate="n", size="tall", zone="open",
         levels=(9, 15), role="xp", wall="oaks", core="oakgrove", trail="dirt", decor="boars",
         groups=same(6, "Bristle Boar"), respawn=100, design="BOARS",   # H7: Old Tusk's wallow is in the Wallows (z 8)
         note="Where most climbers spend their first real hours. Boars drop ham. Old Tusk wallows somewhere in here."),
    dict(id="burrow_hills", type="mixed", title="Burrow Hills", x=240, y=170, w=84, h=58, gate="w", size="std", zone="open",
         levels=(11, 16), role="xp", wall="boulders", core="hills", trail="dirt", decor="hills",
         groups=same(5, "Burrow Mole") + [G(("Bristle Boar", 1), ("Burrow Mole", 2))], respawn=215, design="BURROW",
         den="The Molework", den_groups=same(8, "Burrow Mole", 4),
         note="Sturdy diggers with plenty of health. Slow and steady experience. Climb the Crown or dig down into the Molework."),
    dict(id="wolf_copse", type="mixed", title="Wolf Copse", x=28, y=262, w=60, h=40, gate="e", size="std", zone="open",
         levels=(12, 18), role="xp", wall="firs", core="firs", trail="grass", decor="copse",
         groups=same(5, "Meadow Wolf") + [G(("Grey Alpha", 1), ("Meadow Wolf", 2))], respawn=140, design="WOLVES",
         den="The Alpha's Den", den_groups=same(6, "Meadow Wolf", 4) + [G(("Grey Alpha", 1), ("Meadow Wolf", 3))] * 2,
         note="Wolves hunt in packs, and one pack in each loop follows a Grey Alpha. Across the river, south of Millcross."),
    dict(id="reed_marsh", type="class", cls="Ranger", title="Reedmarsh", x=44, y=322, w=52, h=48, gate="n", size="std", zone="open",
         levels=(14, 19), role="money", wall="water", core="pool", trail="mud", decor="marsh",
         groups=same(6, "Reed Snapper"), respawn=100, design="MARSH",
         note="Snappers carry more coins than their level suggests. Good first money run; fishing works on every pool."),
    dict(id="thornsnap_hollow", type="class", cls="Mystic", title="Thornsnap Hollow", x=158, y=132, w=60, h=40, gate="e", size="std", zone="open",
         levels=(14, 20), role="xp", wall="thorns", core="thorns", trail="dirt", decor="thorns",
         groups=same(5, "Thornsnap") + same(1, "Bristle Boar"), respawn=70, design="THORNS",
         den="The Rootcellar", den_groups=same(8, "Thornsnap", 4),
         note="Poison bites; bring antidotes or healing. Good experience for the effort."),
    dict(id="shard_fields", type="mixed", title="Shard Fields", x=340, y=300, w=52, h=48, gate="n", size="std", zone="open",
         levels=(17, 24), role="xp", wall="boulders", core="gravelmound", trail="gravel", decor="shards",
         groups=same(6, "Field Shardling"), respawn=100, design="SHARDS",
         den="Shard Grotto", den_groups=same(8, "Field Shardling", 4),
         note="Shardlings hit with energy and resist it; wands are weak here. Strong experience."),
    dict(id="bandit_road", type="mixed", title="The Bandit Road", x=328, y=172, w=52, h=48, gate="s", size="std", zone="open",
         levels=(19, 27), role="money", wall="broadleaf", core="banditcamp", trail="dirt", decor="bandits",
         groups=same(5, "Road Bandit") + [G(("Bandit Captain", 1), ("Road Bandit", 2))], respawn=140, design="BANDITS",
         den="Smugglers' Cellar", den_groups=same(6, "Road Bandit", 4) + [G(("Bandit Captain", 1), ("Road Bandit", 3))] * 2,
         note="Bandits carry coins and gear you can sell. Captains lead them and drop platinum. Best early money."),
    dict(id="old_quarry", type="mixed", title="The Old Quarry", x=240, y=124, w=60, h=40, gate="w", size="std", zone="open",
         levels=(23, 30), role="money", wall="boulders", core="cutstone", trail="gravel", decor="quarry",
         groups=[G(("Ruin Sentinel", 1), ("Ruin Archer", 1), ("Field Shardling", 1))] * 4
         + [G(("Ruin Sentinel", 1), ("Ruin Archer", 2))] * 2, respawn=150, design="QUARRY",
         den="The Lower Works", den_groups=[G(("Ruin Sentinel", 2), ("Ruin Archer", 1), ("Field Shardling", 1))] * 4
         + [G(("Ruin Sentinel", 1), ("Ruin Archer", 2), ("Field Shardling", 1))] * 4,
         note="Stone sentinels and archers guard the old works. Tough, but arrows and gear sell well."),
]

# ---- Designed grounds (FLOOR1_HUNTING_PLAN.md Part 6): a ground drawn from a list of clearings and paths on several
# levels, so monsters can be spread out and layered calm -> middle -> deep. Coordinates are local to the ground's corner
# (c["x"], c["y"]); levels below the surface may reach outside the surface rectangle, up to their own "box".
#   clearing: (name, x, y, radius, band, route, content). content: None, "rest", "hub", a group list (one or more groups:
#             [(("Field Rat", 2),), (("Field Rat", 1),)] = a pair and a single 3 tiles apart), or "crowd" (a crowd spot:
#             one group of the route's crowd group, switched on by the crowd system only).
#   path: (from, to, width).   link: ("stairs", x, y, z_low) = stairs up at (x, y, z_low), the way down at (x, y, z_low - 1).
#   band limits and the checker: tools/hunt_check.py.
_P, _S = (("Field Rat", 2),), (("Field Rat", 1),)
_R = {n: (("Field Rat", n),) for n in range(3, 13)}           # Field Rats are a swarm (DESIGN.md 9.4): clumps of 5 to 8
RATWARREN = dict(
    gate=(19, 39), crowd_group=[("Field Rat", 1)],
    routes={"a": "w2", "b": "A", "c": "B", "d": "E"},
    route_names={"a": "The Yard", "b": "The Warren, west", "c": "The Warren, east", "d": "The Deep Warren"},
    levels={
        7: dict(name="The Yard", box=(0, 0, 38, 40), clearings=[
            ("hub", 19, 34, 4, "approach", None, "hub"),
            ("wa", 10, 28, 2, "calm", "a", None),
            ("w2", 6, 18, 3, "calm", "a", [_S]),
            ("w1", 5, 8, 4, "calm", "a", [_P]),
            ("N", 17, 4, 3, "calm", "a", "rest"),
            ("e1", 31, 7, 4, "calm", "a", [_P]),
            ("e2", 31, 18, 3, "calm", "a", [_S]),
            ("rest", 19, 15, 4, "calm", "a", "rest"),
            ("ca1", 11, 3, 1, "calm", "a", "crowd"), ("ca2", 26, 25, 1, "calm", "a", "crowd"),
            ("ca3", 4, 28, 1, "calm", "a", "crowd"),
        ], paths=[("hub", "wa", 3), ("wa", "w2", 3), ("w2", "w1", 3), ("w1", "N", 3), ("N", "e1", 3), ("e1", "e2", 3),
                  ("e2", "hub", 3), ("hub", "rest", 3), ("rest", "N", 3)]),
        # The Warren (north half, middle band) and, past a long quiet tunnel, the Deep Warren (south half, deep band).
        # Both are on level 8: level 9 below is the Underkeep's Wing 4. Chamber rows are 23 apart so no tile can
        # notice two chambers at once (NOTICE 10, members spread one tile).
        8: dict(name="The Warren", box=(-8, -6, 44, 104), clearings=[
            ("A", 10, 30, 4, "middle", "b", "rest"),
            ("B", 17, 7, 4, "middle", "c", "rest"),
            ("D", 14, 33, 4, "middle", None, "rest"),
            ("L0", -3, -3, 5, "middle", "b", [_R[5]]), ("L1", -3, 21, 5, "middle", "b", [_R[6]]),
            ("L2", -3, 45, 5, "middle", "b", [_R[5]]),
            ("R0", 30, -3, 5, "middle", "c", [_R[6]]), ("R1", 30, 21, 5, "middle", "c", [_R[5]]),
            ("R2", 30, 45, 5, "middle", "c", [_R[6]]),
            ("E", 14, 57, 5, "deep", "d", "rest"),
            ("DL0", -3, 69, 5, "deep", "d", [_R[7]]), ("DR0", 30, 69, 5, "deep", "d", [_R[8]]),
            ("DL1", -3, 93, 5, "deep", "d", [_R[7]]),
            ("DR1", 30, 93, 5, "nest", "d", [_R[8]]),
            ("cb1", -3, 10, 1, "middle", "b", "crowd"), ("cb2", -3, 33, 1, "middle", "b", "crowd"),
            ("cb3", 4, -3, 1, "middle", "b", "crowd"),
            ("cc1", 30, 10, 1, "middle", "c", "crowd"), ("cc2", 30, 33, 1, "middle", "c", "crowd"),
            ("cc3", 23, 46, 1, "middle", "c", "crowd"),
            ("cd1", -3, 81, 1, "deep", "d", "crowd"), ("cd2", 14, 80, 1, "deep", "d", "crowd"),
            ("cd3", 14, 92, 1, "deep", "d", "crowd"),
        ], paths=[("L0", "L1", 3), ("L1", "L2", 3), ("R0", "R1", 3), ("R1", "R2", 3), ("L0", "B", 3), ("B", "R0", 3),
                  ("L2", "D", 3), ("D", "R2", 3), ("A", "L1", 3), ("A", "D", 3), ("B", "D", 3),
                  ("D", "E", 3), ("E", "DL0", 3), ("E", "DR0", 3), ("DL0", "DL1", 3), ("DL1", "cd3", 3),
                  ("DR0", "DR1", 2)]),
    },
    links=[("stairs", 10, 28, 8), ("stairs", 17, 6, 8)],
    nest_signs=[(29, 84, 8)],
)
def ring_level(name, box, rect, halls, links, monster, mid_clusters, route="d", start=0, crowd=3, inner=10, gap=25,
               mid_band="middle", party=False, extra=(), extra_paths=(), mid=None, deep=None):
    """A lower level laid out as a ring of tunnels round a rectangle (x0, y0, x1, y1), groups in twos along it with a quiet
    stretch between each two (FLOOR1_HUNTING_PLAN.md Part 3: no tile can notice the group after next), and quiet halls
    inside the ring under the ways down. The first `mid_clusters` twos are pairs (middle band), the rest threes (deep).
    halls: [(name, x, y, r)]; links: [(hall, "q<n>" or hall, width)] (q<n> = the n-th quiet stretch on the ring).
    `start` = how far along the ring (clockwise from the top-left corner) the first group stands.
    mid / deep: what stands at each spot (a clearing's content list), by default a pair / a three of `monster`; a list
    of contents is used in turn, so the groups differ along the ring."""
    x0, y0, x1, y1 = rect
    mid_c = mid or [[((monster, 2),)]]
    deep_c = deep or [[((monster, 3),)]]
    ring = [(x, y0) for x in range(x0, x1)] + [(x1, y) for y in range(y0, y1)] +            [(x, y1) for x in range(x1, x0, -1)] + [(x0, y) for y in range(y1, y0, -1)]
    ring = ring[start:] + ring[:start]
    cheb = lambda a, b: max(abs(a[0] - b[0]), abs(a[1] - b[1]))
    clusters, cur = [], []
    for i, p in enumerate(ring):
        if not clusters and not cur:
            cur = [(i, p)]
            continue
        last = cur[-1][1] if cur else clusters[-1][-1][1]
        first = (clusters[0] if clusters else cur)[0][1]
        if cur and len(cur) < 2 and cheb(p, last) >= inner:
            cur.append((i, p))
        elif len(cur) == 2 and cheb(p, last) >= gap and cheb(p, cur[0][1]) >= gap:
            clusters.append(cur)
            cur = []
        if not cur and clusters and cheb(p, clusters[-1][-1][1]) >= gap and cheb(p, clusters[-1][0][1]) >= gap                 and cheb(p, clusters[0][0][1]) >= gap + inner + 2 and cheb(p, clusters[0][1][1]) >= gap + inner + 2:
            cur = [(i, p)]
    if len(cur) == 2 and cheb(cur[-1][1], clusters[0][0][1]) >= gap:
        clusters.append(cur)
    clearings, order = [], []
    for k, cl in enumerate(clusters):
        deep = k >= mid_clusters
        for j, (i, (x, y)) in enumerate(cl):
            want = (deep_c if deep else mid_c)
            grp = want[(2 * k + j) % len(want)]
            nm = f"r{k}{j}"
            clearings.append((nm, x, y, 4, "deep" if deep else mid_band, route, grp))
            order.append((i, nm))
        nxt = clusters[(k + 1) % len(clusters)][0][0]
        i_end = cl[-1][0]
        mid_i = ((i_end + (nxt if nxt > i_end else nxt + len(ring))) // 2) % len(ring)
        qx, qy = ring[mid_i]
        clearings.append((f"q{k}", qx, qy, 3, "deep" if deep else mid_band, route, "rest"))
        order.append((mid_i if mid_i > i_end else mid_i + len(ring), f"q{k}"))
        if k < crowd:                                 # a crowd pocket beside the first group of the first twos
            cx, cy = cl[0][1]
            mx, my = (x0 + x1) // 2, (y0 + y1) // 2
            cx += 4 if cx < mx - 6 else -4 if cx > mx + 6 else 0
            cy += 4 if cy < my - 6 else -4 if cy > my + 6 else 0
            clearings.append((f"cr{k}", cx, cy, 1, "deep" if deep else mid_band, route, "crowd"))
    order.sort()
    names = [n for _i, n in order]
    paths = [(a, b, 4) for a, b in zip(names, names[1:] + names[:1])]
    for h in halls:                                   # (name, x, y, r[, band])
        hn, hx, hy, hr = h[:4]
        clearings.append((hn, hx, hy, hr, h[4] if len(h) > 4 else mid_band, route if hn == halls[0][0] else None, "rest"))
    paths += list(links)
    clearings += list(extra)                          # hand-placed chambers inside the ring
    paths += list(extra_paths)
    return dict(name=name, box=box, clearings=clearings, paths=paths, party=party)


# Burrow Hills (H5): two boulder hollows on the surface (north and south of the Crown), the Crown itself (a ring-shaped
# plateau at z 6, two ramps up from the south hollow), the Molework (solo tunnels at z 8, two holes down) and the Deep
# Molework (the party cave at z 9). Groups along each route are spaced so no tile can notice more than the band allows:
# neighbours along a route may both be in reach, the one after next never (21+ tiles apart).
_M1, _M2, _M3, _M5 = (("Burrow Mole", 1),), (("Burrow Mole", 2),), (("Burrow Mole", 3),), (("Burrow Mole", 5),)
_M4, _M8 = (("Burrow Mole", 4),), (("Burrow Mole", 8),)
_B1 = (("Bristle Boar", 1),)                       # the soft monster for the low end of the level range, calm band only
BURROW = dict(
    gate=(0, 29), crowd_group=[("Burrow Mole", 2)],
    routes={"a": "a1", "b": "b1", "c": "l1", "d": "mw"},
    route_names={"a": "The North Hollow", "b": "The South Hollow", "c": "The Crown", "d": "The Molework"},
    levels={
        # The hollows: a quiet meadow inside the gate, then a north and a south valley between the outer wall and the
        # Crown. Groups come in twos with a quiet stretch (q1..q4) between, so a rest is never far.
        7: dict(name="the Hollows", box=(0, 0, 84, 58), clearings=[
            ("hub", 8, 29, 4, "approach", None, "hub"),
            ("m0", 18, 29, 6, "calm", None, "rest"), ("w1", 17, 21, 5, "calm", None, None), ("w2", 17, 37, 5, "calm", None, None),
            ("w3", 7, 21, 3, "calm", None, None), ("w4", 7, 37, 3, "calm", None, None),
            ("a1", 14, 9, 3, "calm", "a", [_B1]), ("a2", 24, 5, 3, "calm", "a", [_M1]), ("q1", 36, 6, 3, "calm", "a", "rest"),
            ("a3", 48, 5, 3, "middle", "a", [_M2]), ("a4", 57, 7, 3, "middle", "a", [_M1]), ("q2", 68, 5, 3, "deep", "a", "rest"),
            ("a6", 80, 7, 3, "deep", "a", [_M3]), ("a7", 78, 16, 3, "deep", "a", [_M3]),
            ("ej", 76, 29, 5, "deep", None, "rest"),
            ("b1", 14, 49, 3, "calm", "b", [_B1]), ("b2", 24, 53, 3, "calm", "b", [_M1]), ("q3", 35, 52, 3, "calm", "b", "rest"),
            ("b3", 48, 53, 3, "middle", "b", [_M2]), ("b4", 57, 51, 3, "middle", "b", [_M1]), ("q4", 68, 53, 3, "deep", "b", "rest"),
            ("b6", 80, 51, 3, "deep", "b", [_M3]), ("b7", 78, 42, 3, "deep", "b", [_M3]),
            ("ca1", 5, 12, 1, "calm", "a", "crowd"), ("ca2", 42, 2, 1, "calm", "a", "crowd"), ("ca3", 64, 2, 1, "middle", "a", "crowd"),
            ("cb1", 5, 46, 1, "calm", "b", "crowd"), ("cb2", 42, 55, 1, "calm", "b", "crowd"), ("cb3", 64, 55, 1, "middle", "b", "crowd"),
        ], paths=[("hub", "m0", 5), ("m0", "w1", 4), ("hub", "w3", 4), ("hub", "w4", 4), ("w1", "a1", 4), ("a1", "a2", 4), ("a2", "q1", 4), ("q1", "a3", 4),
                  ("a3", "a4", 4), ("a4", "q2", 4), ("q2", "a6", 4), ("a6", "a7", 4), ("a7", "ej", 4),
                  ("m0", "w2", 4), ("w2", "b1", 4), ("b1", "b2", 4), ("b2", "q3", 4), ("q3", "b3", 4), ("b3", "b4", 4),
                  ("b4", "q4", 4), ("q4", "b6", 4), ("b6", "b7", 4), ("b7", "ej", 4)]),
        # The Crown: a ring of high ground round a sunken middle; you climb it from the south hollow at either end.
        6: dict(name="The Crown", box=(26, 11, 46, 37), clearings=[
            ("l1", 32, 41, 6, "middle", "c", "rest"),
            ("c1", 30, 26, 3, "middle", "c", [_M2]), ("c2", 31, 18, 3, "middle", "c", [_M2]),
            ("l3", 45, 15, 5, "middle", "c", "rest"),
            ("c4", 60, 15, 3, "deep", "c", [_M3]), ("c5", 67, 27, 3, "deep", "c", [_M3]),
            ("l2", 66, 41, 6, "deep", "c", "rest"), ("c7", 49, 42, 3, "deep", "c", [_M3]),
            ("cc1", 36, 24, 1, "middle", "c", "crowd"), ("cc2", 63, 21, 1, "deep", "c", "crowd"),
            ("cc3", 56, 37, 1, "deep", "c", "crowd"),
        ], paths=[("l1", "c1", 5), ("c1", "c2", 5), ("c2", "l3", 5), ("l3", "c4", 5), ("c4", "c5", 5), ("c5", "l2", 5),
                  ("l2", "c7", 5), ("c7", "l1", 5)]),
        # The Molework: tunnels round the edge in twos with quiet stretches between; middle band in the north-west,
        # deep in the north-east, the south and the west branch, the nest at the end of the south tunnel. Quiet halls
        # under both holes and in the middle, where the party cave goes down.
        8: dict(name="The Molework", box=(-6, -6, 96, 70), clearings=[
            ("mw", 18, 31, 5, "middle", "d", "rest"), ("me", 76, 31, 5, "deep", None, "rest"),
            ("pz", 47, 31, 4, "deep", None, "rest"),
            ("d1", 2, 16, 4, "middle", "d", [_M2]), ("d2", 4, 2, 4, "middle", "d", [_M2]), ("q5", 17, -2, 3, "middle", "d", "rest"),
            ("d4", 30, -2, 4, "middle", "d", [_M2]), ("d5", 36, 3, 4, "middle", "d", [_M2]), ("q6", 49, -1, 3, "middle", "d", "rest"),
            ("d6", 63, -2, 4, "deep", "d", [_M3]), ("d7", 73, 3, 4, "deep", "d", [_M3]),
            ("d10", 84, 46, 4, "deep", "d", [_M3]), ("d11", 77, 58, 4, "deep", "d", [_M3]), ("q7", 63, 57, 3, "deep", "d", "rest"),
            ("d12", 50, 54, 4, "deep", "d", [_M3]), ("q8", 37, 59, 4, "deep", "d", "rest"),
            ("nest", 24, 59, 4, "nest", "d", [(("Burrow Mole", 6),)]),
            ("d14", 2, 44, 4, "deep", "d", [_M3]), ("d16", 47, 45, 4, "deep", "d", [_M3]),
            ("cd1", -3, 9, 1, "middle", "d", "crowd"), ("cd2", 33, 8, 1, "middle", "d", "crowd"),
            ("cd3", 65, 8, 1, "deep", "d", "crowd"),
        ], paths=[("mw", "d1", 3), ("d1", "d2", 4), ("d2", "q5", 4), ("q5", "d4", 4), ("d4", "d5", 4), ("d5", "q6", 4),
                  ("q6", "d6", 4), ("d6", "d7", 4), ("d7", "me", 4), ("me", "d10", 4), ("d10", "d11", 4), ("d11", "q7", 4),
                  ("q7", "d12", 4), ("d12", "q8", 4), ("q8", "nest", 3), ("mw", "d14", 3), ("pz", "d16", 3),
                  ("mw", "pz", 4), ("pz", "me", 4)]),
        # The Deep Molework: the party cave. An empty entry chamber, eight chambers of four round it.
        9: dict(name="The Deep Molework", party=True, box=(18, 10, 58, 42), clearings=[
            ("pe", 47, 32, 4, "party", None, "rest"),
            ("p1", 25, 16, 4, "party", None, [_M4]), ("p2", 47, 14, 4, "party", None, [_M4]),
            ("p3", 69, 16, 4, "party", None, [_M4]), ("p4", 70, 31, 4, "party", None, [_M4]),
            ("p5", 69, 46, 4, "party", None, [_M4]), ("p6", 47, 47, 4, "party", None, [_M4]),
            ("p7", 25, 46, 4, "party", None, [_M4]), ("p8", 24, 31, 4, "party", None, [_M4]),
        ], paths=[("pe", "p2", 3), ("pe", "p6", 3), ("pe", "p4", 3), ("pe", "p8", 3), ("p1", "p2", 3), ("p2", "p3", 3),
                  ("p3", "p4", 3), ("p4", "p5", 3), ("p5", "p6", 3), ("p6", "p7", 3), ("p7", "p8", 3), ("p8", "p1", 3)]),
    },
    links=[("stairs", 18, 28, 8), ("stairs", 76, 28, 8), ("ramp", 33, 46, 7, "n"), ("ramp", 67, 46, 7, "n"),
           ("stairs", 47, 30, 9)],
    nest_signs=[(32, 58, 8)],
)
# Toad Pond (H6): three routes round four ponds on the surface (the middle one has an island, reached by bridges), and
# the Sunken Grotto below (route D), a ring of wet tunnels with quiet halls under the two holes.
_TS, _TP = (("Hopper Toad", 1),), (("Hopper Toad", 2),)
_TT = (("Hopper Toad", 3),)
_RS, _RP = (("Field Rat", 1),), (("Field Rat", 2),)
TOADPOND = dict(
    gate=(29, 51), crowd_group=[("Hopper Toad", 1)],
    routes={"a": "a1", "b": "b1", "c": "cs", "d": "gn", "e": "r1"},
    route_names={"a": "The West Ponds", "b": "The East Ponds", "c": "The Island", "d": "The Sunken Grotto",
                 "e": "The Reed Beds"},
    levels={
        # P4 (Jay, 2026-11-23: "way to small now"): 12 tiles wider, a fifth pond and a fifth route down the east side
        7: dict(name="Toad Pond", box=(0, 0, 70, 52),
                ponds=[(29, 25, 6), (13, 13, 4), (46, 13, 3), (12, 34, 3), (63, 18, 3)],
                clearings=[
            ("hub", 29, 46, 4, "approach", None, "hub"),
            ("w0", 16, 43, 3, "calm", None, "rest"), ("e0", 42, 44, 3, "calm", None, "rest"),
            ("a1", 6, 40, 3, "calm", "a", [_RP]), ("a2", 6, 30, 3, "calm", "a", [_TS]), ("q1", 7, 17, 3, "calm", "a", "rest"),
            ("a3", 7, 4, 3, "middle", "a", [_TP]), ("a4", 18, 4, 3, "middle", "a", "rest"),
            ("b1", 52, 40, 3, "calm", "b", [_RP]), ("b2", 52, 30, 3, "calm", "b", [_TS]), ("q2", 51, 17, 3, "calm", "b", "rest"),
            ("b3", 51, 4, 3, "middle", "b", [_TP]), ("b4", 40, 4, 3, "middle", "b", "rest"),
            ("cs", 29, 36, 3, "calm", "c", "rest"), ("c1", 29, 25, 2, "middle", "c", [_TP]),
            ("cn", 29, 15, 3, "deep", "c", "rest"), ("c2", 29, 4, 3, "middle", "c", "rest"),
            ("ca1", 3, 22, 1, "calm", "a", "crowd"), ("ca2", 11, 46, 1, "calm", "a", "crowd"), ("ca3", 15, 5, 1, "middle", "a", "crowd"),
            ("cb1", 54, 22, 1, "calm", "b", "crowd"), ("cb2", 47, 46, 1, "calm", "b", "crowd"), ("cb3", 47, 10, 1, "middle", "b", "crowd"),
            ("cc1", 22, 38, 1, "calm", "c", "crowd"), ("cc2", 36, 38, 1, "calm", "c", "crowd"), ("cc3", 36, 9, 1, "deep", "c", "crowd"),
            ("r0", 63, 44, 3, "calm", None, "rest"), ("r1", 65, 34, 3, "calm", "e", [_TP]), ("r2", 65, 26, 2, "middle", "e", "rest"),
            ("r3", 64, 9, 3, "middle", "e", [_TP]), ("r4", 59, 4, 3, "middle", "e", "rest"),
            ("cr1", 67, 21, 1, "calm", "e", "crowd"), ("cr2", 58, 47, 1, "calm", "e", "crowd"),
        ], paths=[("b1", "r0", 4), ("r0", "r1", 4), ("r1", "r2", 4), ("r2", "r3", 4), ("r3", "r4", 4), ("r4", "b3", 4),("hub", "w0", 4), ("w0", "a1", 4), ("a1", "a2", 4), ("a2", "q1", 4), ("q1", "a3", 4), ("a3", "a4", 4),
                  ("a4", "c2", 4), ("c2", "b4", 4), ("b4", "b3", 4), ("b3", "q2", 4), ("q2", "b2", 4), ("b2", "b1", 4),
                  ("b1", "e0", 4), ("e0", "hub", 4), ("hub", "cs", 4), ("cs", "c1", 3), ("c1", "cn", 3), ("cn", "c2", 3)]),
        # (east of x 13: Underkeep Wing 2 lies under the west part of the pond at this depth)
        8: ring_level("The Sunken Grotto", (13, 4, 70, 72), (17, 8, 79, 72),
                      [("gn", 29, 16, 4), ("ge", 42, 42, 4)],
                      [("gn", "ge", 3), ("gn", "q4", 3), ("ge", "q3", 3)],
                      "Hopper Toad", 0, gap=23, start=50, deep=[[_TP], [_TP], [_TS], [_TP]],
                      extra=[("x1", 58, 30, 4, "deep", "d", [_TP]), ("x2", 56, 54, 4, "deep", "d", [_TS])],
                      extra_paths=[("ge", "x1", 3), ("ge", "x2", 3)]),
    },
    links=[("stairs", 29, 14, 8), ("stairs", 42, 42, 8)],
)

# Sproutling Glade (H6): two fern groves down the sides and a great tree in the middle (a ring of old trees round the way
# down), and the Root Hollow below (route D).
_SS, _SP = (("Sproutling", 1),), (("Sproutling", 2),)
_HS = (("Hopper Toad", 1),)
GLADE = dict(
    gate=(22, 0), crowd_group=[("Sproutling", 1)],
    routes={"a": "a1", "b": "b1", "c": "c1", "d": "rt"},
    route_names={"a": "The West Grove", "b": "The East Grove", "c": "The Great Tree", "d": "The Root Hollow"},
    levels={
        7: dict(name="Sproutling Glade", box=(0, 0, 44, 56), tree_rings=[(22, 31)], clearings=[
            ("hub", 22, 5, 4, "approach", None, "hub"), ("nw", 8, 8, 3, "calm", None, None), ("ne", 36, 8, 3, "calm", None, None),
            ("a1", 3, 21, 3, "calm", "a", [_HS]), ("a2", 6, 28, 3, "calm", "a", [_SS]), ("q1", 6, 39, 3, "calm", "a", "rest"),
            ("a3", 6, 50, 3, "middle", "a", [_SP]),
            ("b1", 40, 21, 3, "calm", "b", [_HS]), ("b2", 37, 28, 3, "calm", "b", [_SS]), ("q2", 37, 39, 3, "calm", "b", "rest"),
            ("b3", 37, 50, 3, "middle", "b", [_SP]),
            ("m0", 22, 13, 2, "calm", None, None), ("c1", 22, 24, 3, "calm", "c", [_SS]), ("cr", 22, 31, 4, "calm", "c", "rest"), ("c2", 22, 47, 3, "middle", "c", [_SS]),
            ("ca1", 2, 23, 1, "calm", "a", "crowd"), ("ca2", 11, 44, 1, "middle", "a", "crowd"), ("ca3", 12, 53, 1, "middle", "a", "crowd"),
            ("cb1", 41, 23, 1, "calm", "b", "crowd"), ("cb2", 32, 44, 1, "middle", "b", "crowd"), ("cb3", 31, 53, 1, "middle", "b", "crowd"),
            ("cc1", 16, 24, 1, "calm", "c", "crowd"), ("cc2", 28, 24, 1, "calm", "c", "crowd"), ("cc3", 22, 39, 1, "calm", "c", "crowd"),
        ], paths=[("hub", "nw", 4), ("nw", "a1", 4), ("a1", "a2", 4), ("a2", "q1", 4), ("q1", "a3", 4), ("a3", "c2", 4), ("c2", "b3", 4),
                  ("b3", "q2", 4), ("q2", "b2", 4), ("b2", "b1", 4), ("b1", "ne", 4), ("ne", "hub", 4), ("hub", "m0", 4), ("m0", "c1", 4), ("c1", "cr", 4),
                  ("cr", "c2", 3)]),
        8: ring_level("The Root Hollow", (-4, 2, 80, 56), (0, 6, 72, 54),
                      [("rt", 22, 32, 4), ("re", 37, 37, 3), ("rm", 52, 28, 4, "nest")],
                      [("rt", "re", 3), ("re", "rm", 3), ("rm", "q1", 3), ("rt", "q4", 3)],
                      "Sproutling", 0, gap=24, deep=[[_SP], [(("Sproutling", 3),)]],
                      extra=[("x1", 41, 22, 4, "nest", "d", [(("Sproutling", 7),)]), ("x2", 52, 38, 4, "deep", "d", [_SS])],
                      extra_paths=[("rm", "x1", 3), ("rm", "x2", 3)]),
    },
    links=[("stairs", 22, 31, 8), ("stairs", 37, 37, 8)],
)

# Waspgrass Fields (H6): flower meadows north and south of Hive Knoll (a flat-topped hill, z 6, two ramps up from the
# south meadow, the hive as its nest), and the Under-Hive below (z 8: tunnels of ground-nesting wasps; Claude's call, so
# the ground can hold its monsters without breaking the calm rules).
_WS, _WP, _WT = (("Meadow Wasp", 1),), (("Meadow Wasp", 2),), (("Meadow Wasp", 3),)
_WN = (("Meadow Wasp", 9),)
_W4, _W6 = (("Meadow Wasp", 4),), (("Meadow Wasp", 6),)
WASPS = dict(
    gate=(67, 25), crowd_group=[("Meadow Wasp", 1)],
    routes={"a": "a1", "b": "b1", "c": "kl", "d": "uw"},
    route_names={"a": "The North Meadow", "b": "The South Meadow", "c": "Hive Knoll", "d": "The Under-Hive"},
    levels={
        7: dict(name="Waspgrass Fields", box=(0, 0, 68, 50), clearings=[
            ("hub", 61, 25, 4, "approach", None, "hub"), ("n0", 55, 14, 2, "calm", None, None), ("s0", 55, 36, 2, "calm", None, None),
            ("a1", 47, 7, 3, "calm", "a", [_WS]), ("a2", 42, 5, 3, "calm", "a", [_WT]), ("q1", 28, 6, 3, "calm", "a", "rest"),
            ("a3", 14, 5, 3, "middle", "a", [_W4]), ("a4", 6, 10, 3, "middle", "a", [_WP]),
            ("b1", 47, 43, 3, "calm", "b", [_WS]), ("b2", 42, 45, 3, "calm", "b", [_WT]), ("q2", 28, 44, 3, "calm", "b", "rest"),
            ("b3", 14, 45, 3, "middle", "b", [_W4]), ("b4", 6, 40, 3, "middle", "b", [_WP]),
            ("cw", 4, 25, 3, "middle", None, "rest"), ("w0", 54, 24, 3, "calm", None, "rest"),
            ("ca1", 56, 3, 1, "calm", "a", "crowd"), ("ca2", 24, 2, 1, "deep", "a", "crowd"), ("ca3", 10, 3, 1, "middle", "a", "crowd"),
            ("cb1", 56, 47, 1, "calm", "b", "crowd"), ("cb2", 34, 47, 1, "calm", "b", "crowd"), ("cb3", 10, 47, 1, "middle", "b", "crowd"),
        ], paths=[("hub", "n0", 4), ("n0", "a1", 4), ("a1", "a2", 4), ("a2", "q1", 4), ("q1", "a3", 4), ("a3", "a4", 4), ("a4", "cw", 4),
                  ("cw", "b4", 4), ("b4", "b3", 4), ("b3", "q2", 4), ("q2", "b2", 4), ("b2", "b1", 4), ("b1", "s0", 4), ("s0", "hub", 4), ("hub", "w0", 4)]),
        6: dict(name="Hive Knoll", box=(19, 12, 32, 27), clearings=[
            ("kl", 24, 33, 4, "middle", "c", "rest"), ("kr", 46, 33, 4, "middle", "c", "rest"),
            ("k1", 24, 21, 3, "middle", "c", [_W4]), ("k2", 24, 14, 3, "middle", "c", [_W4]), ("kt", 45, 26, 2, "nest", "c", None),
            ("kn", 45, 16, 4, "nest", "c", [_WN]),
            ("kc1", 35, 29, 1, "middle", "c", "crowd"), ("kc2", 30, 31, 1, "middle", "c", "crowd"), ("kc3", 38, 33, 1, "middle", "c", "crowd"),
        ], paths=[("kl", "k1", 4), ("k1", "k2", 4), ("kr", "kt", 3), ("kt", "kn", 2), ("kl", "kr", 4)]),
        8: ring_level("The Under-Hive", (-6, -6, 80, 62), (-2, -2, 70, 51),
                      [("uw", 54, 25, 4), ("um", 34, 24, 4), ("us", 28, 43, 3)],
                      [("uw", "um", 3), ("um", "q0", 3), ("uw", "q2", 3), ("um", "us", 3)],
                      "Meadow Wasp", 1, gap=25, mid=[[_W4]], deep=[[_W6], [_W4]]),
    },
    links=[("ramp", 23, 37, 7, "n"), ("ramp", 45, 37, 7, "n"), ("stairs", 54, 23, 8), ("stairs", 28, 43, 8)],
    nest_signs=[(47, 27, 6)],
)
# Boar Meadow (H7, 2026-11-23 overnight, FLOOR1_REVIEW.md F1-30): the narrow meadow stacks three levels. The surface is
# a ring of oak glades round the foot of Oak Ridge; the Ridge (z 6) runs up the middle, climbed by a ramp at its south
# end; the Wallows (z 8) are mud tunnels underneath, reached by holes in the two southern glades, with Old Tusk's wallow
# a dead-end chamber in the middle of them. Boars are loners (DESIGN.md 9.4): always one to a glade, far apart.
_BB = (("Bristle Boar", 1),)
BOARS = dict(
    gate=(19, 0), crowd_group=[("Bristle Boar", 1)],
    routes={"a": "a1", "b": "b1", "c": "kl", "d": "wm"},
    route_names={"a": "The West Glades", "b": "The East Glades", "c": "Oak Ridge", "d": "The Wallows"},
    levels={
        7: dict(name="Boar Meadow", box=(0, 0, 39, 57), clearings=[
            ("hub", 19, 5, 4, "approach", None, "hub"), ("nw", 8, 6, 3, "calm", None, None), ("ne", 30, 6, 3, "calm", None, None),
            ("a1", 3, 20, 3, "calm", "a", [_BB]), ("qa", 4, 31, 3, "calm", "a", "rest"), ("a2", 4, 42, 3, "middle", "a", [_BB]),
            ("b1", 35, 20, 3, "calm", "b", [_BB]), ("qb", 34, 31, 3, "calm", "b", "rest"), ("b2", 34, 42, 3, "middle", "b", [_BB]),
            ("sw", 8, 52, 3, "middle", "a", "rest"), ("se", 30, 52, 3, "middle", "b", "rest"), ("sf", 19, 53, 3, "middle", None, [_BB]),
            ("ca1", 5, 25, 1, "calm", "a", "crowd"), ("ca2", 2, 47, 1, "middle", "a", "crowd"), ("ca3", 5, 36, 1, "middle", "a", "crowd"),
            ("cb1", 33, 25, 1, "calm", "b", "crowd"), ("cb2", 36, 47, 1, "middle", "b", "crowd"), ("cb3", 33, 36, 1, "middle", "b", "crowd"),
        ], paths=[("hub", "nw", 4), ("nw", "a1", 4), ("a1", "qa", 4), ("qa", "a2", 4), ("a2", "sw", 4), ("sw", "sf", 4),
                  ("sf", "se", 4), ("se", "b2", 4), ("b2", "qb", 4), ("qb", "b1", 4), ("b1", "ne", 4), ("ne", "hub", 4)]),
        6: dict(name="Oak Ridge", box=(12, 12, 15, 37), clearings=[
            ("kl", 19, 44, 3, "middle", "c", "rest"), ("k1", 19, 34, 3, "deep", "c", "rest"), ("kq", 19, 26, 3, "deep", "c", "rest"),
            ("k2", 19, 15, 3, "deep", "c", [(("Old Bristleback", 1),)]),
            ("kc1", 16, 19, 1, "deep", "c", "crowd"), ("kc2", 22, 18, 1, "deep", "c", "crowd"), ("kc3", 19, 30, 1, "deep", "c", "crowd"),
        ], paths=[("kl", "k1", 3), ("k1", "kq", 3), ("kq", "k2", 3)]),
        8: ring_level("The Wallows", (-6, 2, 45, 62), (-2, 8, 35, 58),
                      [("wm", 19, 52, 5), ("wl", 8, 52, 4), ("wr", 30, 52, 4), ("tusk", 19, 31, 4, "nest")],
                      [("wm", "wl", 3), ("wm", "wr", 3), ("wl", "q1", 3), ("wr", "q0", 3), ("wl", "tusk", 2)],
                      "Bristle Boar", 1, gap=20, mid_band="deep", mid=[[_BB]], deep=[[_BB]]),
    },
    links=[("ramp", 19, 46, 7, "n"), ("stairs", 8, 52, 8), ("stairs", 30, 52, 8)],
)
# Wolf Copse (H7, 2026-11-23 overnight): dense firs. Wolves hunt in packs (DESIGN.md 9.4: 3 to 5), so packs stand far
# apart: two along the north edge, two along the south, one in the far west, with quiet glades between. Howling Rock
# (z 6, up a ramp) holds the Grey Alpha's pack; the Alpha's Den (z 8) is the party cave, down the stair in the middle.
_W3, _W4 = (("Meadow Wolf", 3),), (("Meadow Wolf", 4),)
_GA = (("Grey Alpha", 1), ("Meadow Wolf", 3))
WOLVES = dict(
    gate=(59, 20), crowd_group=[("Meadow Wolf", 2)],   # crowd spots add two stragglers, not a whole pack (Claude's call)
    routes={"a": "a1", "b": "b1", "c": "kl", "d": "w0"},
    route_names={"a": "The North Firs", "b": "The South Firs", "c": "Howling Rock", "d": "The West Pass"},
    levels={
        7: dict(name="Wolf Copse", box=(0, 0, 60, 40), clearings=[
            ("hub", 54, 20, 4, "approach", None, "hub"), ("n0", 48, 9, 3, "calm", None, None), ("s0", 48, 31, 3, "calm", None, None),
            ("mc", 46, 20, 3, "calm", None, "rest"),
            ("a1", 38, 5, 3, "calm", "a", [_W3]), ("qa", 26, 5, 3, "middle", "a", "rest"), ("a2", 10, 5, 3, "deep", "a", [(("Moonhowl", 1), ("Meadow Wolf", 2))]),
            ("b1", 38, 35, 3, "calm", "b", [_W3]), ("qb", 26, 35, 3, "calm", "b", "rest"), ("b2", 10, 35, 3, "deep", "b", [_W3]),
            ("w0", 2, 20, 2, "deep", "d", "rest"), ("mr", 36, 30, 2, "calm", None, "rest"),
            ("ca1", 50, 4, 1, "calm", "a", "crowd"), ("ca2", 24, 2, 1, "deep", "a", "crowd"),
            ("cb1", 50, 36, 1, "calm", "b", "crowd"), ("cb2", 24, 36, 1, "deep", "b", "crowd"), ("cb3", 16, 30, 1, "deep", "b", "crowd"),
        ], paths=[("hub", "n0", 4), ("n0", "a1", 4), ("a1", "qa", 4), ("qa", "a2", 4), ("a2", "w0", 3), ("w0", "b2", 3),
                  ("b2", "qb", 4), ("qb", "b1", 4), ("b1", "s0", 4), ("s0", "hub", 4), ("hub", "mc", 4), ("b1", "mr", 3)]),
        6: dict(name="Howling Rock", box=(5, 13, 37, 13), clearings=[
            ("kl", 37, 20, 3, "middle", "c", "rest"), ("kq", 29, 19, 3, "middle", "c", "rest"),
            ("kn", 11, 19, 4, "nest", "c", [_GA]), ("kw", 19, 19, 2, "nest", "c", None),
            ("kc1", 40, 16, 1, "middle", "c", "crowd"), ("kc2", 33, 23, 1, "middle", "c", "crowd"), ("kc3", 13, 24, 1, "nest", "c", "crowd"),
        ], paths=[("kl", "kq", 3), ("kq", "kn", 3)]),
        8: dict(name="The Alpha's Den", party=True, box=(0, -4, 60, 48), clearings=[
            ("pe", 46, 20, 4, "party", None, "rest"),
            ("p1", 8, 3, 4, "party", None, [_W4]), ("p2", 30, 0, 4, "party", None, [_GA]),
            ("p3", 52, 3, 4, "party", None, [_W4]), ("p4", 55, 20, 4, "party", None, [_W4]),
            ("p5", 52, 38, 4, "party", None, [_W4]), ("p6", 30, 41, 4, "party", None, [_GA]),
            ("p7", 8, 38, 4, "party", None, [_W4]), ("p8", 5, 20, 4, "party", None, [_W4]),
            ("ca3", 41, 40, 1, "party", "a", "crowd"),
            ("cd1", 19, 2, 1, "party", "d", "crowd"), ("cd2", 41, 2, 1, "party", "d", "crowd"), ("cd3", 19, 39, 1, "party", "d", "crowd"),
        ], paths=[("pe", "p3", 3), ("pe", "p5", 3), ("pe", "p4", 3), ("p1", "p2", 3), ("p2", "p3", 3),
                  ("p3", "p4", 3), ("p4", "p5", 3), ("p5", "p6", 3), ("p6", "p7", 3), ("p7", "p8", 3), ("p8", "p1", 3)]),
    },
    links=[("ramp", 36, 24, 7, "n"), ("stairs", 46, 20, 8)],
)
# Reedmarsh (H7, 2026-11-23 overnight): mud islands in open water, the Ranger's ground (room to keep your distance;
# water is the wall). Snappers are pairs; single Hopper Toads are the soft monster on the near islands. The central
# island sits in the big pond, reached by bridges; the far southern islands are the deep part. Surface only.
_RS1, _RS2, _HT1 = (("Reed Snapper", 1),), (("Reed Snapper", 2),), (("Hopper Toad", 1),)
MARSH = dict(
    gate=(26, 0), crowd_group=[("Reed Snapper", 1)],
    routes={"a": "a1", "b": "b1", "c": "cn", "d": "dq"},
    route_names={"a": "The West Islands", "b": "The East Islands", "c": "The Middle Island", "d": "The Far Islands"},
    levels={
        7: dict(name="Reedmarsh", box=(0, 0, 52, 48),
                ponds=[(26, 27, 7), (9, 22, 3), (43, 22, 3), (16, 38, 3), (36, 38, 3)],
                clearings=[
            ("hub", 26, 5, 4, "approach", None, "hub"), ("w0", 14, 6, 3, "calm", None, None), ("e0", 38, 6, 3, "calm", None, None),
            ("a0", 5, 10, 2, "calm", "a", [_HT1]), ("a1", 4, 18, 3, "calm", "a", [_RS2]), ("qa", 3, 31, 3, "calm", "a", "rest"),
            ("a2", 6, 42, 3, "middle", "a", [_RS2]),
            ("b0", 47, 10, 2, "calm", "b", [_HT1]), ("b1", 48, 18, 3, "calm", "b", [_RS2]), ("qb", 49, 31, 3, "calm", "b", "rest"),
            ("b2", 46, 42, 3, "middle", "b", [_RS2]),
            ("cn", 26, 15, 3, "middle", "c", "rest"), ("c1", 26, 27, 3, "middle", "c", [_RS2]), ("cs", 26, 39, 2, "middle", "c", "rest"),
            ("dq", 26, 45, 2, "deep", "d", "rest"), ("d1", 12, 46, 2, "deep", "d", [_RS2, (("Mossback Snapper", 1),)]), ("d2", 40, 46, 2, "deep", "d", [_RS2, _RS1]),
            ("ca1", 4, 25, 1, "calm", "a", "crowd"), ("ca2", 9, 8, 1, "calm", "a", "crowd"), ("ca3", 9, 43, 1, "middle", "a", "crowd"),
            ("cb1", 48, 25, 1, "calm", "b", "crowd"), ("cb2", 43, 8, 1, "calm", "b", "crowd"), ("cb3", 43, 43, 1, "middle", "b", "crowd"),
            ("cc1", 21, 15, 1, "middle", "c", "crowd"), ("cc2", 31, 15, 1, "middle", "c", "crowd"), ("cc3", 22, 40, 1, "middle", "c", "crowd"),
            ("cd1", 7, 44, 1, "deep", "d", "crowd"), ("cd2", 45, 44, 1, "deep", "d", "crowd"), ("cd3", 31, 44, 1, "deep", "d", "crowd"),
        ], paths=[("hub", "w0", 4), ("w0", "a0", 3), ("a0", "a1", 3), ("a1", "qa", 3), ("qa", "a2", 3), ("a2", "d1", 3),
                  ("d1", "dq", 3), ("dq", "d2", 3), ("d2", "b2", 3), ("b2", "qb", 3), ("qb", "b1", 3), ("b1", "b0", 3),
                  ("b0", "e0", 3), ("e0", "hub", 4), ("hub", "cn", 3), ("cn", "c1", 2), ("c1", "cs", 2), ("cs", "dq", 2)]),
    },
    links=[],
)
# Thornsnap Hollow (H7, 2026-11-23 overnight): the Mystic's ground. A north rim and a south rim round a ring of
# brambles, with a gap into the hollow's middle (route c). Thornsnaps are sentries: rooted at bends, in ones and twos.
# The Rootcellar (z 8) is the party cave: eight root chambers of four, down the stair by the gate.
_T1, _T2, _T4 = (("Thornsnap", 1),), (("Thornsnap", 2),), (("Thornsnap", 4),)
THORNS = dict(
    gate=(59, 20), crowd_group=[("Thornsnap", 1)],
    routes={"a": "a1", "b": "b1", "c": "ce", "d": "w0"},
    route_names={"a": "The North Rim", "b": "The South Rim", "c": "The Bramble Ring", "d": "The Rootcellar"},
    levels={
        7: dict(name="Thornsnap Hollow", box=(0, 0, 60, 40), clearings=[
            ("hub", 54, 20, 4, "approach", None, "hub"), ("n0", 48, 9, 3, "calm", None, None), ("s0", 48, 31, 3, "calm", None, None),
            ("a1", 40, 4, 3, "calm", "a", [_T1]), ("qa", 30, 5, 3, "calm", "a", "rest"), ("a2", 17, 4, 3, "deep", "a", [_T2]),
            ("b1", 40, 36, 3, "calm", "b", [_T1]), ("qb", 30, 35, 3, "calm", "b", "rest"), ("b2", 17, 36, 3, "deep", "b", [_T2]),
            ("w0", 3, 20, 3, "deep", "d", "rest"),
            ("ce", 42, 20, 3, "calm", "c", "rest"), ("c1", 27, 20, 4, "middle", "c", [(("Blackthorn", 1),)]),
            ("ms", 48, 26, 2, "calm", None, "rest"),
            ("ca1", 47, 3, 1, "calm", "a", "crowd"), ("ca2", 24, 2, 1, "deep", "a", "crowd"), ("ca3", 9, 6, 1, "deep", "a", "crowd"),
            ("cb1", 47, 37, 1, "calm", "b", "crowd"), ("cb2", 24, 37, 1, "deep", "b", "crowd"), ("cb3", 9, 34, 1, "deep", "b", "crowd"),
        ], paths=[("hub", "n0", 4), ("n0", "a1", 4), ("a1", "qa", 3), ("qa", "a2", 3), ("a2", "w0", 3), ("w0", "b2", 3),
                  ("b2", "qb", 3), ("qb", "b1", 3), ("b1", "s0", 4), ("s0", "hub", 4), ("hub", "ce", 3), ("ce", "c1", 2),
                  ("hub", "ms", 3)]),
        8: dict(name="The Rootcellar", party=True, box=(0, -10, 60, 49), clearings=[
            ("pe", 48, 26, 4, "party", None, "rest"),
            ("p1", 8, -2, 4, "party", None, [_T4]), ("p2", 30, -5, 4, "party", None, [_T4]),
            ("p3", 52, -2, 4, "party", None, [_T4]), ("p4", 55, 12, 4, "party", None, [_T4]),
            ("p5", 52, 34, 4, "party", None, [_T4]), ("p6", 30, 34, 4, "party", None, [_T4]),
            ("p7", 8, 33, 4, "party", None, [_T4]), ("p8", 5, 15, 4, "party", None, [_T4]),
            ("cd1", 19, -3, 1, "party", "d", "crowd"), ("cd2", 41, -3, 1, "party", "d", "crowd"), ("cd3", 19, 34, 1, "party", "d", "crowd"),
            ("cc1", 5, 6, 1, "party", "c", "crowd"), ("cc2", 41, 34, 1, "party", "c", "crowd"), ("cc3", 5, 25, 1, "party", "c", "crowd"),
        ], paths=[("pe", "p4", 4), ("pe", "p5", 4), ("p1", "p2", 4), ("p2", "p3", 4), ("p3", "p4", 4),
                  ("p5", "p6", 4), ("p6", "p7", 4), ("p7", "p8", 4), ("p8", "p1", 4)]),
    },
    links=[("stairs", 48, 26, 8)],
)
# Shard Fields (H8, 2026-11-23 overnight): gravel flats on the west, the Terraces (z 6) up the east side by a ramp at
# their south end, the Shard Grotto (z 8) as the party cave down the stair in the south. Shardlings are pairs.
_FS1, _FS2, _FS4 = (("Field Shardling", 1),), (("Field Shardling", 2),), (("Field Shardling", 4),)
SHARDS = dict(
    gate=(26, 0), crowd_group=[("Field Shardling", 1)],
    routes={"a": "a1", "b": "b1", "c": "kl", "d": "s0"},
    route_names={"a": "The West Flats", "b": "The Middle Flats", "c": "The Terraces", "d": "The Shard Grotto"},
    levels={
        7: dict(name="Shard Fields", box=(0, 0, 52, 48), clearings=[
            ("hub", 26, 5, 4, "approach", None, "hub"), ("n0", 14, 7, 3, "calm", None, None),
            ("a1", 3, 14, 3, "calm", "a", [_FS2]), ("qa", 3, 27, 3, "calm", "a", "rest"), ("a2", 4, 40, 3, "deep", "a", [_FS2]),
            ("b1", 26, 26, 3, "calm", "b", [_FS2]), ("qb", 25, 33, 3, "middle", "b", "rest"), ("b2", 24, 42, 3, "deep", "b", [_FS2]),
            ("s0", 14, 44, 3, "deep", "d", "rest"), ("rf", 34, 45, 2, "middle", None, "rest"),
            ("ca1", 3, 8, 1, "calm", "a", "crowd"), ("ca2", 8, 27, 1, "calm", "a", "crowd"), ("ca3", 9, 45, 1, "deep", "a", "crowd"),
            ("cb1", 14, 30, 1, "calm", "b", "crowd"), ("cb2", 14, 20, 1, "calm", "b", "crowd"), ("cb3", 29, 45, 1, "deep", "b", "crowd"),
        ], paths=[("hub", "n0", 4), ("n0", "a1", 4), ("a1", "qa", 4), ("qa", "a2", 4), ("a2", "s0", 4), ("s0", "b2", 4),
                  ("b2", "qb", 4), ("qb", "b1", 4), ("b1", "hub", 4), ("b2", "rf", 3)]),
        6: dict(name="The Terraces", box=(30, 8, 21, 37), clearings=[
            ("kl", 34, 39, 3, "middle", "c", "rest"), ("k1", 41, 29, 3, "middle", "c", "rest"), ("kq", 46, 19, 3, "deep", "c", "rest"),
            ("k2", 38, 12, 3, "deep", "c", [_FS2, (("Prism Shardling", 1),)]),
            ("kc1", 45, 30, 1, "middle", "c", "crowd"), ("kc2", 35, 20, 1, "deep", "c", "crowd"), ("kc3", 47, 11, 1, "deep", "c", "crowd"),
        ], paths=[("kl", "k1", 3), ("k1", "kq", 3), ("kq", "k2", 3)]),
        8: dict(name="The Shard Grotto", party=True, box=(0, 8, 52, 50), clearings=[
            ("pe", 11, 45, 4, "party", None, "rest"),
            ("p1", 5, 14, 4, "party", None, [_FS4]), ("p2", 26, 12, 4, "party", None, [_FS4]),
            ("p3", 46, 14, 4, "party", None, [_FS4]), ("p4", 47, 31, 4, "party", None, [_FS4]),
            ("p5", 45, 50, 4, "party", None, [_FS4]), ("p6", 27, 51, 4, "party", None, [_FS4]),
            ("p7", 4, 52, 3, "party", None, [_FS4]), ("p8", 5, 31, 4, "party", None, [_FS4]),
            ("cd1", 16, 12, 1, "party", "d", "crowd"), ("cd2", 37, 12, 1, "party", "d", "crowd"), ("cd3", 37, 51, 1, "party", "d", "crowd"),
        ], paths=[("pe", "p8", 4), ("pe", "p6", 4), ("p1", "p2", 4), ("p2", "p3", 4), ("p3", "p4", 4), ("p4", "p5", 4),
                  ("p5", "p6", 4), ("p6", "p7", 4), ("p7", "p8", 4), ("p8", "p1", 4)]),
    },
    links=[("ramp", 33, 42, 7, "n"), ("stairs", 11, 45, 8)],
)
# The Bandit Road (H8, 2026-11-25): the old road runs north from the gate through broadleaf woods past a ruined waystation
# and a roadside shrine to the bandits' camp in a ruined watch-house. Bandits are sentries: ones and twos at the ruins,
# far apart (spots 20+ tiles apart: NOTICE 10; a pair stands side by side, east-west). The Bandit Captain (the ground's
# elite) holds the camp. The shrine sits in a quiet strip between the waystation and the camp. The Smugglers' Cellar
# (z 8) is the party cave, a built cellar down the stair on the road.
DGP_RUBBLE = [5866, 5708, 2264, 1822]                      # rubble and cut blocks (maps/dungeon.py RUBBLE + stones)
_RB1, _RB2, _RB4 = (("Road Bandit", 1),), (("Road Bandit", 2),), (("Road Bandit", 4),)
_CAP1, _CAP4 = (("Bandit Captain", 1),), (("Bandit Captain", 1), ("Road Bandit", 3))   # the elite stands alone (H8 client walk)
BANDITS = dict(
    gate=(25, 47), crowd_group=[("Road Bandit", 1)],
    routes={"a": "a1", "b": "b1", "c": "c0", "d": "dq"},
    route_names={"a": "The West Woods", "b": "The East Woods", "c": "The Old Road", "d": "The Bandit Camp"},
    levels={
        7: dict(name="The Bandit Road", box=(0, 0, 52, 48), clearings=[
            ("hub", 25, 41, 4, "approach", None, "hub"), ("sw", 16, 40, 4, "calm", None, None), ("se", 35, 40, 4, "calm", None, None),
            ("qa", 4, 37, 3, "calm", "a", "rest"), ("a1", 4, 26, 3, "calm", "a", [_RB1]), ("a2", 5, 15, 2, "middle", "a", [_RB2]),
            ("qb", 47, 37, 3, "calm", "b", "rest"), ("b1", 47, 26, 3, "calm", "b", [_RB1]), ("b2", 47, 15, 2, "middle", "b", [_RB2]),
            ("c0", 25, 35, 3, "calm", "c", "rest"), ("c1", 25, 27, 3, "middle", "c", [_RB2]), ("cs", 25, 15, 3, "deep", "c", "rest"),
            ("dq", 13, 3, 2, "deep", "d", "rest"), ("d1", 26, 3, 3, "deep", "d", [_CAP1]), ("de", 38, 3, 2, "deep", "d", "rest"),
            ("ca1", 10, 37, 1, "calm", "a", "crowd"), ("ca2", 9, 30, 1, "calm", "a", "crowd"), ("ca3", 9, 9, 1, "middle", "a", "crowd"),
            ("cb1", 41, 37, 1, "calm", "b", "crowd"), ("cb2", 42, 30, 1, "calm", "b", "crowd"), ("cb3", 42, 9, 1, "middle", "b", "crowd"),
            ("cc1", 19, 32, 1, "calm", "c", "crowd"), ("cc2", 31, 32, 1, "calm", "c", "crowd"), ("cc3", 25, 20, 1, "middle", "c", "crowd"),
            ("cd1", 19, 7, 1, "deep", "d", "crowd"), ("cd2", 33, 7, 1, "deep", "d", "crowd"), ("cd3", 26, 9, 1, "deep", "d", "crowd"),
        ], paths=[("hub", "sw", 4), ("sw", "qa", 3), ("qa", "a1", 3), ("a1", "a2", 3), ("a2", "dq", 3), ("dq", "d1", 3),
                  ("d1", "de", 3), ("de", "b2", 3), ("b2", "b1", 3), ("b1", "qb", 3), ("qb", "se", 3), ("se", "hub", 4),
                  ("hub", "c0", 4), ("c0", "c1", 3), ("c1", "cs", 3), ("cs", "d1", 3)],
                # ruins (x, y, w, h, doorways): the farmhouse (west), the guard post (east), the waystation, the shrine
                # and the watch-house the bandits camp in
                ruins=[(2, 12, 7, 7, [(5, 12), (8, 15), (5, 18)]), (44, 12, 7, 7, [(47, 12), (44, 15), (47, 18)]),
                       (21, 24, 9, 7, [(25, 24), (25, 30), (21, 27), (29, 27)]), (23, 13, 5, 5, [(25, 13), (25, 17)]),
                       (20, 2, 12, 5, [(26, 6), (20, 4), (31, 4)])], ruin_props=[2519, 2523, 116, 117]),   # barrels, crates
        8: dict(name="The Smugglers' Cellar", party=True, built=True, box=(4, 4, 46, 42),
                props=[2519, 2523, 116, 117, 2519, 2523] + [5866, 5708], clearings=[
            ("pe", 25, 35, 3, "party", None, "rest"),
            ("p1", 9, 9, 4, "party", None, [_RB4]), ("p2", 26, 8, 4, "party", None, [_CAP4]),
            ("p3", 43, 9, 4, "party", None, [_RB4]), ("p4", 44, 25, 4, "party", None, [_RB4]),
            ("p5", 40, 40, 3, "party", None, [_CAP4]), ("p6", 11, 40, 3, "party", None, [_RB4]),
            ("p7", 9, 25, 4, "party", None, [_RB4]),
            ("cd1", 17, 8, 1, "party", "d", "crowd"), ("cd2", 35, 8, 1, "party", "d", "crowd"), ("cd3", 33, 40, 1, "party", "d", "crowd"),
        ], paths=[("pe", "p5", 3), ("pe", "p6", 3), ("p1", "p2", 3), ("p2", "p3", 3), ("p3", "p4", 3),
                  ("p4", "p5", 3), ("p6", "p7", 3), ("p7", "p1", 3), ("pe", "p2", 3)]),
    },
    links=[("stairs", 25, 33, 8)],
)
# The Old Quarry (H8, 2026-11-25): a worked pit round a great block of uncut stone. A gravel ring runs round the block
# (the North and South Pits, the Deep Cut at the far east end, quiet ledges in its corners); the Upper Cut (z 6) is the
# block's top, up a ramp from the south pit: an archer at its west end, the Granite Warden (the ground's elite) at the
# east end, a quiet plaza between. The Lower Works (z 8) is the party cave: the old mine, built with stone walls, down
# the pit-head stair by the gate.
_A1, _QS1 = (("Ruin Archer", 1),), (("Field Shardling", 1),)
_SA, _SF = (("Ruin Sentinel", 1), ("Ruin Archer", 1)), (("Ruin Sentinel", 1), ("Field Shardling", 1))
_LW1, _LW2 = (("Ruin Sentinel", 2), ("Ruin Archer", 1), ("Field Shardling", 1)), (("Ruin Sentinel", 1), ("Ruin Archer", 2), ("Field Shardling", 1))
QUARRY = dict(
    gate=(0, 19), crowd_group=[("Ruin Archer", 1)],
    routes={"a": "a1", "b": "b1", "c": "kl", "d": "dq"},
    route_names={"a": "The North Pit", "b": "The South Pit", "c": "The Upper Cut", "d": "The Deep Cut"},
    levels={
        7: dict(name="The Old Quarry", box=(0, 0, 60, 40), clearings=[
            ("hub", 6, 19, 4, "approach", None, "hub"), ("n0", 9, 8, 3, "calm", None, "rest"), ("s0", 9, 31, 3, "calm", None, None),
            ("mw", 11, 26, 2, "calm", None, "rest"),
            ("a1", 18, 4, 3, "calm", "a", [_A1]), ("qa", 30, 4, 2, "calm", "a", "rest"), ("a2", 42, 4, 3, "deep", "a", [_SA]),
            ("b1", 18, 35, 3, "calm", "b", [_QS1]), ("qb", 30, 35, 2, "calm", "b", "rest"), ("b2", 42, 35, 3, "deep", "b", [_SF]),
            ("ne", 54, 5, 3, "deep", None, "rest"), ("dq", 55, 12, 2, "deep", "d", "rest"),
            ("d1", 55, 20, 3, "deep", "d", [_SA]), ("se", 54, 34, 3, "deep", None, "rest"),
            ("ca1", 17, 8, 1, "calm", "a", "crowd"), ("ca2", 25, 7, 1, "calm", "a", "crowd"), ("ca3", 35, 7, 1, "deep", "a", "crowd"),
            ("cb1", 14, 36, 1, "calm", "b", "crowd"), ("cb2", 25, 32, 1, "calm", "b", "crowd"), ("cb3", 35, 32, 1, "deep", "b", "crowd"),
            ("cd1", 50, 12, 1, "deep", "d", "crowd"), ("cd2", 50, 27, 1, "deep", "d", "crowd"), ("cd3", 57, 26, 1, "deep", "d", "crowd"),
        ], paths=[("hub", "n0", 4), ("n0", "a1", 4), ("a1", "qa", 4), ("qa", "a2", 4), ("a2", "ne", 3), ("ne", "dq", 3),
                  ("dq", "d1", 3), ("d1", "se", 3), ("se", "b2", 3), ("b2", "qb", 4), ("qb", "b1", 4), ("b1", "s0", 4),
                  ("s0", "hub", 4), ("hub", "mw", 3)],
                ruins=[(9, 2, 7, 5, [(12, 6), (15, 4)])], ruin_props=DGP_RUBBLE),     # the old quarry office by the north pit
        6: dict(name="The Upper Cut", box=(16, 9, 34, 22), clearings=[
            ("kl", 31, 26, 2, "middle", "c", "rest"), ("km", 32, 20, 5, "middle", None, "rest"),
            ("k1", 19, 19, 3, "middle", "c", [_A1]), ("kq", 32, 14, 3, "deep", "c", "rest"),
            ("k2", 46, 18, 3, "nest", "c", [(("Granite Warden", 1),)]),
            ("kc1", 22, 24, 1, "middle", "c", "crowd"), ("kc2", 40, 12, 1, "deep", "c", "crowd"), ("kc3", 44, 24, 1, "nest", "c", "crowd"),
        ], paths=[("kl", "km", 3), ("km", "k1", 3), ("km", "kq", 3), ("kq", "k2", 3), ("km", "k2", 3)]),
        8: dict(name="The Lower Works", party=True, built=True, box=(2, 1, 57, 37), clearings=[
            ("pe", 12, 28, 3, "party", None, "rest"),
            ("p1", 8, 8, 4, "party", None, [_LW1]), ("p2", 24, 6, 4, "party", None, [_LW2]),
            ("p3", 40, 6, 4, "party", None, [_LW1]), ("p4", 53, 10, 4, "party", None, [_LW2]),
            ("p5", 53, 28, 4, "party", None, [_LW1]), ("p6", 40, 32, 3, "party", None, [_LW2]),
            ("p7", 26, 32, 3, "party", None, [_LW1]),
            ("cd1", 16, 6, 1, "party", "d", "crowd"), ("cd2", 47, 6, 1, "party", "d", "crowd"), ("cd3", 47, 33, 1, "party", "d", "crowd"),
        ], paths=[("pe", "p1", 3), ("pe", "p7", 3), ("p1", "p2", 3), ("p2", "p3", 3), ("p3", "p4", 3), ("p4", "p5", 3),
                  ("p5", "p6", 3), ("p6", "p7", 3)]),
    },
    links=[("ramp", 30, 29, 7, "n"), ("stairs", 11, 26, 8)],
)
DESIGNS = {"RATWARREN": RATWARREN, "BURROW": BURROW, "TOADPOND": TOADPOND, "GLADE": GLADE, "WASPS": WASPS, "BOARS": BOARS, "WOLVES": WOLVES, "MARSH": MARSH, "THORNS": THORNS, "SHARDS": SHARDS,
           "BANDITS": BANDITS, "QUARRY": QUARRY}

APEX = dict(id="apex_watchtower", type="large", title="The Old Watchtower", levels=(28, 40), role="xp+money",
            x=30, y=30, w=44, h=44,
            # plan Part 6: fixed groups instead of four big spawn areas (real respawn seconds)
            courtyard=dict(groups=same(6, "Stonehorn Ram"), respawn=150),
            inner=dict(groups=same(4, "Stonehorn Ram", 4), respawn=120),
            cave=dict(groups=same(8, "Stonehorn Ram", 4), respawn=120),
            note="The floor's apex spawn: an easy outer ring, a packed inner room, and a hidden rope to a cave. Contested: players can fight here.")

ROLE_TEXT = {"xp": "experience", "money": "money", "xp+money": "experience and money"}


def spawn_time(real_seconds):
    """What to write in the spawn file so the monster really returns after about real_seconds (W0: the engine waits about
    twice the file's number)."""
    return max(1, round(real_seconds / 2))


def monsters_per_loop(c):
    return sum(n for g in c["groups"] for _m, n in g)


def den_level(c):
    lo, hi = c["levels"]
    return (lo + hi) // 2 + 1


for _c in CAMPS:
    _c.setdefault("den", None)
    _c.setdefault("den_groups", [])
    sz = SIZES[_c["size"]]
    assert len(_c["groups"]) == sz["groups"], (_c["id"], "groups per loop")
    # share of each monster kind in the ground (read by the economy model and the bestiary)
    _tot = {}
    for _g in _c["groups"]:
        for _m, _n in _g:
            _tot[_m] = _tot.get(_m, 0) + _n
    _all = sum(_tot.values())
    _c["mix"] = [(m, 3, n / _all) for m, n in _tot.items()]

# Where each camp sits is data; the map reads this list. Keys used elsewhere in the game:
#   camp_<id> points (tests and events), so ids must not change.
#   loop_<id>_<nw|ne|sw|se> (each loop's mouth), crowd_<id>_<loop>_<n> (crowd spots, W10), den_<id> (cave stairs).
