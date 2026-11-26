"""Floor 3 plan (roadmap S6): Rootwell Fogwood, levels 60-90, a jungle floor. Same shape of file as maps/floor2_plan.py;
read by maps/layout_floor.py and tools/balance.py (the floor recipe check).

Coordinates are tiles relative to Floor 3's corner (maps/floors.py origin(3) = 2400,1000). Floor 3 is 300 x 300, with
the town (Rootwell), the Pass, the labyrinth and the apex in the same places as on every generated floor.

The floor recipe (DESIGN.md 9.4, layer 3), Floor 3's version:
  training   Mantis Lea (60-66)                  pairs of Bark Mantises, beside the town
  class      Batroost Thicket, Arcanist (62-70)    Spore Bat swarms
             Lurkfog Tangle, Vanguard (66-75)      Fog Lurkers, loners, in a thick tangle
             Mosswallow Mire, Mystic (68-78)       a Moss Crawler colony round the pools; the crawlers regrow
             Wisplight Glade, Ranger (74-84)       Lantern Wisp sentries in open glades
  mixed      Fogwood Run (64-72)                   Mantises and Fog Lurkers
             Glowcap Dell (72-82)                  Wisps and Spore Bats
  group      The Husk Hollows (80-90)              Rootbound Husk packs led by a Moss Elder; plus three party caves
  large      the Hydraling's Grove (85-90)         the apex (maps/layout_floor.py)

Floor 3's twist (Claude's call, Jay can veto): the plant creatures (Moss Crawlers and Rootbound Husks) regrow: they
heal a little every few seconds, so a fight you walk away from starts again from full (tools/gen_monsters.py, TWISTS).
"""
from floors import origin

ORG = origin(3)
FLOOR = 3


def G(*parts):
    return [p for p in parts]


def same(n, monster, count):
    return [G((monster, count)) for _ in range(n)]


BAT, CRAWLER, LURKER, MANTIS, WISP = "Spore Bat", "Moss Crawler", "Fog Lurker", "Bark Mantis", "Lantern Wisp"
HUSK, ELITE = "Rootbound Husk", "Moss Elder"

CAMPS = [
    dict(id="f3_lea", type="training", title="Mantis Lea", x=205, y=252, w=44, h=42, gate="n", size="small",
         zone="open", levels=(60, 66), role="xp", wall="ferns", core="grove", trail="jungle",
         groups=[G((MANTIS, 2)), G((MANTIS, 2)), G((MANTIS, 1)), G((MANTIS, 2))], respawn=100,
         note="Bark Mantises hunt in twos. Your first Floor 3 hunt, just outside Rootwell."),
    dict(id="f3_roost", type="class", cls="Arcanist", title="Batroost Thicket", x=50, y=252, w=44, h=42, gate="n",
         size="small", zone="open", levels=(62, 70), role="xp", wall="broadleaf", core="mounds", trail="jungle",
         groups=[G((BAT, 7)), G((BAT, 6)), G((BAT, 8)), G((BAT, 6))], respawn=110,
         note="Clouds of spore bats, weak one by one. Area spells clear a cloud in a few casts."),
    dict(id="f3_tangle", type="class", cls="Vanguard", title="Lurkfog Tangle", x=210, y=145, w=60, h=40, gate="w",
         size="std", zone="open", levels=(66, 75), role="xp", wall="hedge", core="oakgrove", trail="dirt",
         groups=same(6, LURKER, 1), respawn=90,
         note="Fog Lurkers wait alone in the tangle and hit hard. Narrow trails: stand and trade blows."),
    dict(id="f3_mire", type="class", cls="Mystic", title="Mosswallow Mire", x=8, y=190, w=52, h=48, gate="s",
         size="std", zone="open", levels=(68, 78), role="xp", wall="water", core="pool", trail="mud",
         groups=[G((CRAWLER, 2)), G((CRAWLER, 3)), G((CRAWLER, 7)), G((CRAWLER, 9)), G((CRAWLER, 3)), G((CRAWLER, 2))],
         respawn=110, den="The Rootmire", den_groups=same(8, CRAWLER, 4),
         note="Moss Crawlers thicken round the pools and regrow if you let them. Long fights: staying power wins."),
    dict(id="f3_glade", type="class", cls="Ranger", title="Wisplight Glade", x=205, y=15, w=52, h=48, gate="s",
         size="std", zone="open", levels=(74, 84), role="money", wall="firs", core="firs", trail="jungle",
         groups=[G((WISP, 2)), G((WISP, 3)), G((WISP, 2)), G((WISP, 4)), G((WISP, 2)), G((WISP, 3))], respawn=140,
         note="Lantern Wisps keep their posts and shoot from range. Wide glades: room to keep your distance."),
    dict(id="f3_run", type="mixed", title="Fogwood Run", x=75, y=140, w=60, h=40, gate="e", size="std",
         zone="open", levels=(64, 72), role="xp", wall="oaks", core="firs", trail="dirt",
         groups=[G((MANTIS, 2)), G((LURKER, 1)), G((MANTIS, 2)), G((LURKER, 1)), G((MANTIS, 2)), G((ELITE, 1))],
         respawn=120, den="The Fog Cellar", den_groups=[G((LURKER, 2), (MANTIS, 2))] * 6 + [G((ELITE, 1), (LURKER, 3))] * 2,
         note="Mantis pairs and lurking loners side by side. A Moss Elder roots at the far end of every loop."),
    dict(id="f3_dell", type="mixed", title="Glowcap Dell", x=240, y=190, w=52, h=48, gate="s", size="std",
         zone="open", levels=(72, 82), role="money", wall="thorns", core="flowerbed", trail="jungle",
         groups=[G((BAT, 5)), G((WISP, 2)), G((BAT, 6)), G((WISP, 2)), G((BAT, 5)), G((WISP, 3))], respawn=130,
         note="Bat clouds and wisp posts among the glowcaps. Wisps carry coins."),
    dict(id="f3_hollows", type="group", title="The Husk Hollows", x=66, y=72, w=60, h=40, gate="e", size="std",
         zone="open", levels=(80, 90), role="xp", wall="thorns", core="thorns", trail="mud",
         groups=[G((HUSK, 3), (WISP, 1)), G((HUSK, 2), (LURKER, 1), (WISP, 1)), G((HUSK, 3), (CRAWLER, 1)),
                 G((HUSK, 2), (WISP, 2)), G((ELITE, 1), (HUSK, 2)), G((HUSK, 3), (LURKER, 1))], respawn=150,
         den="The Root Deeps", den_groups=[G((HUSK, 3), (WISP, 1))] * 6 + [G((ELITE, 1), (HUSK, 2), (WISP, 1))] * 2,
         note="For a party of three or four. Husk packs with wisps behind them: you need a tank, damage and healing."),
]

for _c in CAMPS:
    _c["org"] = ORG
    _c["floor"] = FLOOR
    _c["base"] = "jungle"
    _c.setdefault("den", None)
    _c.setdefault("cls", None)

APEX = dict(id="f3_grove", type="large", title="the Hydraling's Grove", levels=(85, 90))

SPURS = {
    "f3_lea": [(227, 245), (227, 251)],
    "f3_roost": [(72, 245), (72, 251)],
    "f3_tangle": [(150, 164), (209, 164)],
    "f3_mire": [(33, 238), (33, 245)],
    "f3_glade": [(230, 63), (230, 100), (151, 100)],
    "f3_run": [(135, 160), (150, 160)],
    "f3_dell": [(265, 238), (265, 245)],
    "f3_hollows": [(126, 92), (150, 92)],
}
