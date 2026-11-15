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
ELITES = {"Grey Alpha", "Bandit Captain"}
CAVE_RESPAWN = 160


def G(*parts):
    """One monster group: G(("Meadow Wolf", 3)) or G(("Grey Alpha", 1), ("Meadow Wolf", 2))."""
    return [p for p in parts]


def same(n, monster, count=3):
    return [G((monster, count)) for _ in range(n)]


# id, title, x, y, w, h, gate side, loop size, zone, levels, role, note,
# wall / core / trail = how the ground is dressed (plan Part 6), groups = the groups on EACH loop,
# respawn = real seconds (plan Part 5.3), den = cave name, den_groups = the cave's 8 groups (plan Part 5.4).
CAMPS = [
    dict(id="starter_west", title="The Ratwarren", x=134, y=242, w=38, h=40, gate="s", size="small", zone="guarded",
         levels=(1, 4), role="xp", wall="broadleaf", core="mounds", trail="dirt", decor="rats",
         groups=same(4, "Field Rat"), respawn=110, design="RATWARREN",
         note="Your first fights. Hit it, loot it, hit the next. Safe: no one can attack you here."),
    dict(id="starter_east", title="Toad Pond", x=296, y=242, w=38, h=40, gate="s", size="small", zone="guarded",
         levels=(3, 7), role="xp", wall="broadleaf", core="pond", trail="grass", decor="pond",
         groups=same(3, "Hopper Toad") + same(1, "Field Rat"), respawn=110,
         note="Toads hit a little harder and give a little more. Four ponds, four loops; fishing works here."),
    dict(id="starter_south", title="Sproutling Glade", x=190, y=338, w=38, h=40, gate="n", size="small", zone="guarded",
         levels=(5, 10), role="xp", wall="ferns", core="grove", trail="grass", decor="glade",
         groups=same(3, "Sproutling") + same(1, "Hopper Toad"), respawn=110,
         note="Sproutlings spit a little poison-green magic. Still inside the Guarded ring around town."),
    dict(id="wasp_fields", title="Waspgrass Fields", x=184, y=194, w=44, h=34, gate="e", size="small", zone="guarded",
         levels=(7, 12), role="xp", wall="hedge", core="flowerbed", trail="grass", decor="wasps",
         groups=same(4, "Meadow Wasp"), respawn=110,
         note="Fast and stingy, little health. Just north of the city gate, beside the Pass road."),
    dict(id="boar_meadow", title="Boar Meadow", x=140, y=338, w=39, h=57, gate="n", size="tall", zone="open",
         levels=(9, 15), role="xp", wall="oaks", core="oakgrove", trail="dirt", decor="boars",
         groups=same(6, "Bristle Boar"), respawn=190, wallow=(1, 1),   # Old Tusk's wallow in the south-east loop
         note="Where most climbers spend their first real hours. Boars drop ham. Old Tusk wallows somewhere in here."),
    dict(id="burrow_hills", title="Burrow Hills", x=240, y=170, w=84, h=58, gate="w", size="std", zone="open",
         levels=(11, 16), role="xp", wall="boulders", core="hills", trail="dirt", decor="hills",
         groups=same(5, "Burrow Mole") + [G(("Bristle Boar", 1), ("Burrow Mole", 2))], respawn=215, design="BURROW",
         den="The Molework", den_groups=same(8, "Burrow Mole", 4),
         note="Sturdy diggers with plenty of health. Slow and steady experience. Climb the Crown or dig down into the Molework."),
    dict(id="wolf_copse", title="Wolf Copse", x=28, y=262, w=60, h=40, gate="e", size="std", zone="open",
         levels=(12, 18), role="xp", wall="firs", core="firs", trail="grass", decor="copse",
         groups=same(5, "Meadow Wolf") + [G(("Grey Alpha", 1), ("Meadow Wolf", 2))], respawn=190,
         den="The Alpha's Den", den_groups=same(6, "Meadow Wolf", 4) + [G(("Grey Alpha", 1), ("Meadow Wolf", 3))] * 2,
         note="Wolves hunt in packs, and one pack in each loop follows a Grey Alpha. Across the river, south of Millcross."),
    dict(id="reed_marsh", title="Reedmarsh", x=44, y=322, w=52, h=48, gate="n", size="std", zone="open",
         levels=(14, 19), role="money", wall="water", core="pool", trail="mud", decor="marsh",
         groups=same(6, "Reed Snapper"), respawn=215,
         note="Snappers carry more coins than their level suggests. Good first money run; fishing works on every pool."),
    dict(id="thornsnap_hollow", title="Thornsnap Hollow", x=158, y=132, w=60, h=40, gate="e", size="std", zone="open",
         levels=(14, 20), role="xp", wall="thorns", core="thorns", trail="dirt", decor="thorns",
         groups=same(5, "Thornsnap") + same(1, "Bristle Boar"), respawn=195,
         den="The Rootcellar", den_groups=same(8, "Thornsnap", 4),
         note="Poison bites; bring antidotes or healing. Good experience for the effort."),
    dict(id="shard_fields", title="Shard Fields", x=340, y=300, w=52, h=48, gate="n", size="std", zone="open",
         levels=(17, 24), role="xp", wall="boulders", core="gravelmound", trail="gravel", decor="shards",
         groups=same(6, "Field Shardling"), respawn=180,
         den="Shard Grotto", den_groups=same(8, "Field Shardling", 4),
         note="Shardlings hit with energy and resist it; wands are weak here. Strong experience."),
    dict(id="bandit_road", title="The Bandit Road", x=328, y=172, w=52, h=48, gate="s", size="std", zone="open",
         levels=(19, 27), role="money", wall="broadleaf", core="banditcamp", trail="dirt", decor="bandits",
         groups=same(5, "Road Bandit") + [G(("Bandit Captain", 1), ("Road Bandit", 2))], respawn=210, ruin_walls=True,
         den="Smugglers' Cellar", den_groups=same(6, "Road Bandit", 4) + [G(("Bandit Captain", 1), ("Road Bandit", 3))] * 2,
         note="Bandits carry coins and gear you can sell. Captains lead them and drop platinum. Best early money."),
    dict(id="old_quarry", title="The Old Quarry", x=240, y=124, w=60, h=40, gate="w", size="std", zone="open",
         levels=(23, 30), role="money", wall="boulders", core="cutstone", trail="gravel", decor="quarry",
         groups=[G(("Ruin Sentinel", 1), ("Ruin Archer", 1), ("Field Shardling", 1))] * 4
         + [G(("Ruin Sentinel", 1), ("Ruin Archer", 2))] * 2, respawn=220,
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
_T, _N = (("Field Rat", 3),), (("Field Rat", 4),)
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
        8: dict(name="The Warren", box=(-8, -6, 44, 101), clearings=[
            ("A", 10, 30, 4, "middle", "b", "rest"),
            ("B", 17, 7, 4, "middle", "c", "rest"),
            ("D", 14, 33, 4, "middle", None, "rest"),
            ("L0", -3, -2, 5, "middle", "b", [_P, _P]), ("L1", -3, 21, 5, "middle", "b", [_P, _P]),
            ("L2", -3, 44, 5, "middle", "b", [_P, _P]),
            ("R0", 30, -2, 5, "middle", "c", [_P, _P]), ("R1", 30, 21, 5, "middle", "c", [_P, _P]),
            ("R2", 30, 44, 5, "middle", "c", [_P, _P]),
            ("E", 14, 57, 5, "deep", "d", "rest"),
            ("DL0", -3, 67, 5, "deep", "d", [_P, _T]), ("DR0", 30, 67, 5, "deep", "d", [_P, _T]),
            ("DL1", -3, 90, 5, "deep", "d", [_P, _P]),
            ("DR1", 30, 90, 5, "nest", "d", [_N]),
            ("cb1", -3, 10, 1, "middle", "b", "crowd"), ("cb2", -3, 33, 1, "middle", "b", "crowd"),
            ("cb3", 4, -3, 1, "middle", "b", "crowd"),
            ("cc1", 30, 10, 1, "middle", "c", "crowd"), ("cc2", 30, 33, 1, "middle", "c", "crowd"),
            ("cc3", 23, 46, 1, "middle", "c", "crowd"),
            ("cd1", -3, 78, 1, "deep", "d", "crowd"), ("cd2", 14, 78, 1, "deep", "d", "crowd"),
            ("cd3", 14, 92, 1, "deep", "d", "crowd"),
        ], paths=[("L0", "L1", 3), ("L1", "L2", 3), ("R0", "R1", 3), ("R1", "R2", 3), ("L0", "B", 3), ("B", "R0", 3),
                  ("L2", "D", 3), ("D", "R2", 3), ("A", "L1", 3), ("A", "D", 3), ("B", "D", 3),
                  ("D", "E", 3), ("E", "DL0", 3), ("E", "DR0", 3), ("DL0", "DL1", 3), ("DL1", "cd3", 3),
                  ("DR0", "DR1", 2)]),
    },
    links=[("stairs", 10, 28, 8), ("stairs", 17, 6, 8)],
    nest_signs=[(29, 82, 8)],
)
# Burrow Hills (H5): two boulder hollows on the surface (north and south of the Crown), the Crown itself (a ring-shaped
# plateau at z 6, two ramps up from the south hollow), the Molework (solo tunnels at z 8, two holes down) and the Deep
# Molework (the party cave at z 9). Groups along each route are spaced so no tile can notice more than the band allows:
# neighbours along a route may both be in reach, the one after next never (21+ tiles apart).
_M1, _M2, _M3, _M5 = (("Burrow Mole", 1),), (("Burrow Mole", 2),), (("Burrow Mole", 3),), (("Burrow Mole", 5),)
_M4 = (("Burrow Mole", 4),)
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
            ("a1", 14, 9, 3, "calm", "a", [_B1]), ("a2", 24, 5, 3, "calm", "a", [_M2]), ("q1", 36, 6, 3, "calm", "a", "rest"),
            ("a3", 48, 5, 3, "middle", "a", [_M2]), ("a4", 57, 7, 3, "middle", "a", [_M1]), ("q2", 68, 5, 3, "deep", "a", "rest"),
            ("a6", 80, 7, 3, "deep", "a", [_M3]), ("a7", 78, 16, 3, "deep", "a", [_M3]),
            ("ej", 76, 29, 5, "deep", None, "rest"),
            ("b1", 14, 49, 3, "calm", "b", [_B1]), ("b2", 24, 53, 3, "calm", "b", [_M2]), ("q3", 35, 52, 3, "calm", "b", "rest"),
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
            ("nest", 24, 59, 4, "nest", "d", [_M5]),
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
DESIGNS = {"RATWARREN": RATWARREN, "BURROW": BURROW}

APEX = dict(id="apex_watchtower", title="The Old Watchtower", levels=(28, 40), role="xp+money",
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
