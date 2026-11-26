"""Floor 4 plan (roadmap S6): Lakehold, levels 90-120, a drowned castle country of sand, water and old stone. Same shape
of file as maps/floor2_plan.py; read by maps/layout_floor.py and tools/balance.py (the floor recipe check).

Coordinates are tiles relative to Floor 4's corner (maps/floors.py origin(4) = 2800,1000).

The floor recipe (DESIGN.md 9.4, layer 3), Floor 4's version:
  training   Footman's Strand (90-97)              pairs of Drowned Footmen, beside the town
  class      Eel Shallows, Arcanist (93-101)         Lake Eel swarms
             Helm Barracks, Vanguard (98-107)        Helm Knights, loners, among broken castle walls
             Crabshell Flats, Mystic (100-110)       a Tide Crab colony; long, wearing fights
             Witchreed Marsh, Ranger (106-116)       Reed Witch sentries across open water
  mixed      The Moat Road (95-104)                  Footmen and Castle Hound packs
             The Drowned Bailey (104-114)            Crabs and Witches
  group      The Sunken Keep (110-120)               Castle Hound packs with knights and witches, led by Drowned Sergeants
  large      the Siege Beast's Breach (115-120)      the apex (maps/layout_floor.py)

Floor 4's twist (Claude's call, Jay can veto): the Reed Witches mend the hurt monsters around them, any kind (the
Hedge Hexer's trick from Floor 1's party caves, SpireHexMend). Kill the witch first (tools/gen_monsters.py, TWISTS).
"""
from floors import origin

ORG = origin(4)
FLOOR = 4


def G(*parts):
    return [p for p in parts]


def same(n, monster, count):
    return [G((monster, count)) for _ in range(n)]


EEL, FOOT, WITCH, CRAB, HOUND = "Lake Eel", "Drowned Footman", "Reed Witch", "Tide Crab", "Castle Hound"
KNIGHT, ELITE = "Helm Knight", "Drowned Sergeant"

CAMPS = [
    dict(id="f4_strand", type="training", title="Footman's Strand", x=50, y=252, w=44, h=42, gate="n", size="small",
         zone="open", levels=(90, 97), role="xp", wall="water", core="pool", trail="sand",
         groups=[G((FOOT, 2)), G((FOOT, 2)), G((FOOT, 1)), G((FOOT, 2))], respawn=100,
         note="Drowned Footmen still walk their rounds in twos. Your first Floor 4 hunt, just outside Lakehold."),
    dict(id="f4_shallows", type="class", cls="Arcanist", title="Eel Shallows", x=205, y=252, w=44, h=42, gate="n",
         size="small", zone="open", levels=(93, 101), role="xp", wall="water", core="pond", trail="sand",
         groups=[G((EEL, 7)), G((EEL, 6)), G((EEL, 8)), G((EEL, 7))], respawn=110,
         note="Lake Eels come up in knots, weak one by one. Area spells clear a knot in a few casts."),
    dict(id="f4_barracks", type="class", cls="Vanguard", title="Helm Barracks", x=8, y=190, w=52, h=48, gate="s",
         size="std", zone="open", levels=(98, 107), role="xp", wall="boulders", core="cutstone", trail="gravel",
         ruin_walls=True, groups=same(6, KNIGHT, 1), respawn=90,
         note="Helm Knights hold the old barracks alone and hit hard. Narrow ways between broken walls: stand and trade."),
    dict(id="f4_flats", type="class", cls="Mystic", title="Crabshell Flats", x=240, y=190, w=52, h=48, gate="s",
         size="std", zone="open", levels=(100, 110), role="xp", wall="boulders", core="gravelmound", trail="sand",
         groups=[G((CRAB, 2)), G((CRAB, 3)), G((CRAB, 7)), G((CRAB, 9)), G((CRAB, 3)), G((CRAB, 2))], respawn=110,
         den="The Crab Beds", den_groups=same(8, CRAB, 4),
         note="Tide Crabs pile up round their beds, hard-shelled and slow to die. Staying power wins here."),
    dict(id="f4_marsh", type="class", cls="Ranger", title="Witchreed Marsh", x=205, y=15, w=52, h=48, gate="s",
         size="std", zone="open", levels=(106, 116), role="money", wall="water", core="pool", trail="mud",
         groups=[G((WITCH, 2)), G((WITCH, 3)), G((WITCH, 2)), G((WITCH, 4)), G((WITCH, 2)), G((WITCH, 3))], respawn=140,
         note="Reed Witches keep their posts across the water and cast from range. Room to keep your distance."),
    dict(id="f4_moat", type="mixed", title="The Moat Road", x=75, y=140, w=60, h=40, gate="e", size="std",
         zone="open", levels=(95, 104), role="xp", wall="bushes", core="mounds", trail="sand",
         groups=[G((FOOT, 2)), G((HOUND, 3)), G((FOOT, 2)), G((HOUND, 4)), G((FOOT, 1)), G((ELITE, 1))],
         respawn=120, den="The Flooded Cellars", den_groups=[G((HOUND, 3), (FOOT, 1))] * 6 + [G((ELITE, 1), (HOUND, 3))] * 2,
         note="Footmen and hound packs along the old moat. A Drowned Sergeant stands at the far end of every loop."),
    dict(id="f4_bailey", type="mixed", title="The Drowned Bailey", x=165, y=150, w=60, h=40, gate="w", size="std",
         zone="open", levels=(104, 114), role="money", wall="boulders", core="hills", trail="gravel",
         groups=[G((CRAB, 3)), G((WITCH, 2)), G((CRAB, 4)), G((WITCH, 2)), G((CRAB, 3)), G((WITCH, 3))], respawn=130,
         note="Crab beds and witch posts in the castle's flooded yard. Witches carry coins and mend the crabs."),
    dict(id="f4_keep", type="group", title="The Sunken Keep", x=66, y=72, w=60, h=40, gate="e", size="std",
         zone="open", levels=(110, 120), role="xp", wall="boulders", core="cutstone", trail="gravel", ruin_walls=True,
         groups=[G((HOUND, 3), (WITCH, 1)), G((HOUND, 2), (KNIGHT, 1), (WITCH, 1)), G((HOUND, 3), (CRAB, 1)),
                 G((HOUND, 2), (WITCH, 2)), G((ELITE, 1), (HOUND, 2)), G((HOUND, 3), (KNIGHT, 1))], respawn=150,
         den="The Keep's Undercroft", den_groups=[G((HOUND, 3), (WITCH, 1))] * 6 + [G((ELITE, 1), (KNIGHT, 1), (WITCH, 1))] * 2,
         note="For a party of three or four. Hound packs with knights in front and witches mending them from behind: "
              "you need a tank, damage and healing."),
]

for _c in CAMPS:
    _c["org"] = ORG
    _c["floor"] = FLOOR
    _c["base"] = "sand"
    _c.setdefault("den", None)
    _c.setdefault("cls", None)
    _c["den_repeat"] = 2               # H14 (challenge, not calm): each cave group twice, like Floor 1's party caves

APEX = dict(id="f4_breach", type="large", title="the Siege Beast's Breach", levels=(115, 120))

SPURS = {
    "f4_strand": [(72, 245), (72, 251)],
    "f4_shallows": [(227, 245), (227, 251)],
    "f4_barracks": [(33, 238), (33, 245)],
    "f4_flats": [(265, 238), (265, 245)],
    "f4_marsh": [(230, 63), (230, 100), (151, 100)],
    "f4_moat": [(135, 160), (150, 160)],
    "f4_bailey": [(150, 169), (164, 169)],
    "f4_keep": [(126, 92), (150, 92)],
}
