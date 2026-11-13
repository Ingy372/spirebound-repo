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
         levels=(1, 4), role="xp", wall="bushes", core="mounds", trail="dirt", decor="rats",
         groups=same(4, "Field Rat"), respawn=110,
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
    dict(id="burrow_hills", title="Burrow Hills", x=240, y=188, w=60, h=40, gate="w", size="std", zone="open",
         levels=(11, 16), role="xp", wall="boulders", core="hills", trail="dirt", decor="hills",
         groups=same(6, "Burrow Mole"), respawn=215,
         den="The Molework", den_groups=same(8, "Burrow Mole", 4),
         note="Sturdy diggers with plenty of health. Slow and steady experience."),
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
         groups=same(5, "Road Bandit") + [G(("Bandit Captain", 1), ("Road Bandit", 2))], respawn=210,
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
