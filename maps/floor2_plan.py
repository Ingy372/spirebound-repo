"""Floor 2 plan (roadmap R13b, S6): Highrest Highlands, levels 35-60. The one place that says where Floor 2's hunting
grounds are and what lives in them. Read by maps/layout_floor.py (draws them with the same walled-ground skeleton as
Floor 1, maps/wilds.py), tools/balance.py (the spawn-rule check) and tools/gen_bestiary.py.

Coordinates are tiles relative to Floor 2's corner (maps/floors.py origin(2) = 2000,1000). Floor 2 is 300 x 300.
Highrest (the walled town) sits south-centre at x 105..194, y 210..279; the Pass and the labyrinth are north-centre
(x 126..176, y 8..92); the Mesa Wyrm's Roost (the apex, a large-group ground) is the walled square in the north-west
(x 20..59, y 20..59).

The floor recipe (DESIGN.md 9.4, layer 3), Floor 2's version:
  training   Grazing Downs (35-41)             pairs of Horned Grazers, beside the town
  class      Strider Flats, Arcanist (37-44)    Dust Strider swarms
             Ridgecat Crags, Vanguard (42-50)   Ridge Cats, loners, in tight rock trails
             Blighthive Gully, Mystic (44-52)   a Blight Wasp colony, thin outside, thick round the hive
             Cutthroat Mesa, Ranger (48-56)     Hill Cutthroat sentries on open ground
  mixed      Hornpath Ridge (40-48)             Grazers, Ridge Cats and a Herd Bull
             Dustwind Steppe (46-54)            Striders and Cutthroats
  group      Bullrun Canyon (52-60)             mixed packs led by Stonehide Bulls; plus the party caves under three grounds
  large      the Mesa Wyrm's Roost (55-60)      the apex (maps/layout_floor.py)
The ladder runs outward from Highrest: the easiest grounds are just outside the walls, the hardest in the far north.

Floor 2's twist (Claude's call, Jay can veto): the herd animals (Horned Grazers and Dust Striders) run when badly
hurt and come back once they have recovered, so a fight with a herd spills across the trail (tools/gen_monsters.py,
FLEE_WHEN_HURT).
"""
from floors import origin

ORG = origin(2)
FLOOR = 2


def G(*parts):
    return [p for p in parts]


def same(n, monster, count):
    return [G((monster, count)) for _ in range(n)]


GRAZER, STRIDER, CAT, WASP, CUT = "Horned Grazer", "Dust Strider", "Ridge Cat", "Blight Wasp", "Hill Cutthroat"
BULL, ELITE = "Stonehide Bull", "Herd Bull"

# Same fields as Floor 1's CAMPS (maps/floor1_plan.py); "org" and "floor" put them on Floor 2.
CAMPS = [
    dict(id="f2_downs", type="training", title="Grazing Downs", x=50, y=252, w=44, h=42, gate="n", size="small",
         zone="open", levels=(35, 41), role="xp", wall="broadleaf", core="grove", trail="grass",
         groups=[G((GRAZER, 2)), G((GRAZER, 1)), G((GRAZER, 2)), G((GRAZER, 2))], respawn=100,
         note="Grazers wander in twos. They charge when cornered and run when hurt. Your first Floor 2 hunt."),
    dict(id="f2_flats", type="class", cls="Arcanist", title="Strider Flats", x=205, y=252, w=44, h=42, gate="n",
         size="small", zone="open", levels=(37, 44), role="xp", wall="bushes", core="flowerbed", trail="grass",
         groups=[G((STRIDER, 6)), G((STRIDER, 5)), G((STRIDER, 7)), G((STRIDER, 6))], respawn=110,
         note="Flocks of striders, weak one by one. Area spells clear a flock in a few casts."),
    dict(id="f2_crags", type="class", cls="Vanguard", title="Ridgecat Crags", x=8, y=190, w=52, h=48, gate="s",
         size="std", zone="open", levels=(42, 50), role="xp", wall="boulders", core="hills", trail="dirt",
         groups=same(6, CAT, 1), respawn=90,
         note="Ridge Cats hunt alone and pounce. Tight trails between the rocks: stand and trade blows."),
    dict(id="f2_gully", type="class", cls="Mystic", title="Blighthive Gully", x=240, y=190, w=52, h=48, gate="s",
         size="std", zone="open", levels=(44, 52), role="xp", wall="thorns", core="thorns", trail="dirt",
         groups=[G((WASP, 2)), G((WASP, 3)), G((WASP, 6)), G((WASP, 8)), G((WASP, 3)), G((WASP, 2))], respawn=110,
         den="The Blighthive", den_groups=same(8, WASP, 4),
         note="Blight Wasps spit poison from range. Thin at the edges, thick round each hive. Long, wearing fights."),
    dict(id="f2_ridge", type="mixed", title="Hornpath Ridge", x=165, y=150, w=60, h=40, gate="w", size="std",
         zone="open", levels=(40, 48), role="xp", wall="oaks", core="oakgrove", trail="dirt",
         groups=[G((GRAZER, 2)), G((CAT, 1)), G((GRAZER, 2)), G((CAT, 1)), G((GRAZER, 2)), G((ELITE, 1))], respawn=120,
         den="Hornpath Hollow", den_groups=[G((BULL, 3), (GRAZER, 1))] * 6 + [G((ELITE, 1), (BULL, 3))] * 2,
         note="Grazers and Ridge Cats side by side. A Herd Bull grazes at the far end of every loop."),
    dict(id="f2_steppe", type="mixed", title="Dustwind Steppe", x=75, y=140, w=60, h=40, gate="e", size="std",
         zone="open", levels=(46, 54), role="money", wall="bushes", core="mounds", trail="dirt",
         groups=[G((STRIDER, 5)), G((CUT, 2)), G((STRIDER, 5)), G((CUT, 2)), G((STRIDER, 6)), G((CUT, 3))], respawn=130,
         den="The Dry Wells", den_groups=[G((CUT, 2), (STRIDER, 2))] * 8,
         note="Strider flocks and Cutthroat camps on the open steppe. Cutthroats carry coins."),
    dict(id="f2_mesa", type="class", cls="Ranger", title="Cutthroat Mesa", x=205, y=15, w=52, h=48, gate="s",
         size="std", zone="open", levels=(48, 56), role="money", wall="boulders", core="cutstone", trail="gravel",
         groups=[G((CUT, 2)), G((CUT, 3)), G((CUT, 2)), G((CUT, 4)), G((CUT, 2)), G((CUT, 3))], respawn=140,
         note="Cutthroats hold the mesa ledges. Open ground and long sight lines: room to shoot and keep your distance."),
    dict(id="f2_canyon", type="group", title="Bullrun Canyon", x=66, y=72, w=60, h=40, gate="e", size="std",
         zone="open", levels=(52, 60), role="xp", wall="boulders", core="gravelmound", trail="gravel",
         groups=[G((BULL, 3), (CUT, 1)), G((BULL, 2), (CAT, 1), (CUT, 1)), G((BULL, 3), (WASP, 1)),
                 G((BULL, 2), (CUT, 2)), G((ELITE, 1), (BULL, 2)), G((BULL, 3), (CAT, 1))], respawn=150,
         den="The Stampede Deeps", den_groups=[G((BULL, 3), (CUT, 1))] * 6 + [G((ELITE, 1), (BULL, 2), (CUT, 1))] * 2,
         note="For a party of three or four. Stonehide herds with Cutthroats and Ridge Cats among them: you need a tank, "
              "damage and healing."),
]

for _c in CAMPS:
    _c["org"] = ORG
    _c["floor"] = FLOOR
    _c.setdefault("den", None)
    _c.setdefault("cls", None)

# the apex (built by maps/layout_floor.py): the floor's one large-group ground
APEX = dict(id="f2_roost", type="large", title="the Mesa Wyrm's Roost", levels=(55, 60))

# roads from the town's main roads to each ground's gate: lists of points (local), walked with Map.road
SPURS = {
    "f2_downs": [(72, 245), (72, 251)],
    "f2_flats": [(227, 245), (227, 251)],
    "f2_crags": [(33, 238), (33, 245)],
    "f2_gully": [(265, 238), (265, 245)],
    "f2_ridge": [(150, 169), (164, 169)],
    "f2_steppe": [(135, 160), (150, 160)],
    "f2_mesa": [(230, 63), (230, 100), (151, 100)],
    "f2_canyon": [(126, 92), (150, 92)],
}
