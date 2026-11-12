"""Floor 1 plan: the one place that says where the hunting grounds are and what lives in them.

Read by maps/layout_floor1.py (draws the map and places the monsters) and tools/gen_bestiary.py (writes BESTIARY.md and
the in-game hunting guide), so the map, the guide and the bestiary can never disagree.

Coordinates are tiles relative to the corner of Floor 1 (the map builder adds X0, Y0). Floor 1 is 400 x 400.
Hearthgate (the walled city) occupies x 190..269, y 250..321.

How the ladder works (DESIGN.md 3.1, level band 1-35). Each camp is a step; a player outgrows one and walks to the next:
  * "xp" camps give the best experience for their level range.
  * "money" camps give less experience but drop more coins and sellable gear.
  * level ranges overlap on purpose, so there is always a choice and always somewhere to go.
Density: about one monster per 30 tiles, so 20 players find empty ground and 500 players still find monsters.
"""

TOWN = dict(x=190, y=250, w=80, h=72)          # Hearthgate, walled
MILLCROSS = dict(x=35, y=195, w=64, h=44)       # the village west of the river

# id, title, x, y, w, h, zone, decor (key, density), levels (lo, hi), role, [(monster, group size, share of the camp)]
# share = fraction of the camp's monsters (shares add up to 1.0)
CAMPS = [
    dict(id="starter_west", title="The Ratwarren", x=132, y=255, w=45, h=30, zone="guarded", decor="rats",
         levels=(1, 4), role="xp", mix=[("Field Rat", 6, 1.0)], respawn=40,
         note="Your first fights. Hit it, loot it, hit the next. Safe: no one can attack you here."),
    dict(id="starter_east", title="Toad Pond", x=278, y=255, w=50, h=30, zone="guarded", decor="pond",
         levels=(3, 7), role="xp", mix=[("Hopper Toad", 6, 0.7), ("Field Rat", 6, 0.3)], respawn=40,
         note="Toads hit a little harder and give a little more. Leave when rats feel too easy."),
    dict(id="starter_south", title="Sproutling Glade", x=210, y=330, w=50, h=35, zone="guarded", decor="glade",
         levels=(5, 10), role="xp", mix=[("Sproutling", 6, 0.75), ("Hopper Toad", 6, 0.25)], respawn=45,
         note="Sproutlings spit a little poison-green magic. Still inside the Guarded ring around town."),
    dict(id="wasp_fields", title="Waspgrass Fields", x=210, y=195, w=50, h=40, zone="guarded", decor="wasps",
         levels=(7, 12), role="xp", mix=[("Meadow Wasp", 6, 1.0)], respawn=50,
         note="Fast and stingy, little health. Just north of the city gate, beside the Pass road."),
    dict(id="boar_meadow", title="Boar Meadow", x=150, y=330, w=50, h=50, zone="open", decor="boars",
         levels=(9, 15), role="xp", mix=[("Bristle Boar", 6, 1.0)], respawn=55,
         note="Where most climbers spend their first real hours. Boars drop ham. Old Tusk hides here."),
    dict(id="burrow_hills", title="Burrow Hills", x=260, y=185, w=45, h=40, zone="open", decor="hills",
         levels=(11, 16), role="xp", mix=[("Burrow Mole", 6, 1.0)], respawn=55,
         note="Sturdy diggers with plenty of health. Slow and steady experience."),
    dict(id="wolf_copse", title="Wolf Copse", x=40, y=270, w=55, h=50, zone="open", decor="copse",
         levels=(12, 18), role="xp", mix=[("Meadow Wolf", 6, 0.88), ("Grey Alpha", 1, 0.12)], respawn=60,
         note="Wolves hunt in packs, and each pack has a Grey Alpha that calls for help. Across the river, beside Millcross."),
    dict(id="thornsnap_hollow", title="Thornsnap Hollow", x=140, y=140, w=45, h=40, zone="open", decor="thorns",
         levels=(14, 20), role="xp", mix=[("Thornsnap", 6, 0.8), ("Bristle Boar", 6, 0.2)], respawn=60,
         note="Poison bites; bring antidotes or healing. Good experience for the effort."),
    dict(id="reed_marsh", title="Reedmarsh", x=60, y=330, w=50, h=45, zone="open", decor="marsh",
         levels=(14, 19), role="money", mix=[("Reed Snapper", 6, 1.0)], respawn=60,
         note="Snappers carry more coins than their level suggests. Good first money run."),
    dict(id="shard_fields", title="Shard Fields", x=320, y=300, w=60, h=60, zone="open", decor="shards",
         levels=(17, 24), role="xp", mix=[("Field Shardling", 6, 1.0)], respawn=60,
         note="Shardlings hit with energy and resist it; wands are weak here. Strong experience."),
    dict(id="bandit_road", title="The Bandit Road", x=330, y=180, w=55, h=50, zone="open", decor="bandits",
         levels=(19, 27), role="money", mix=[("Road Bandit", 6, 0.88), ("Bandit Captain", 1, 0.12)], respawn=65,
         note="Bandits carry coins and gear you can sell. Captains lead them and drop platinum. Best early money."),
    dict(id="old_quarry", title="The Old Quarry", x=220, y=130, w=55, h=40, zone="open", decor="quarry",
         levels=(23, 30), role="money", mix=[("Ruin Sentinel", 5, 0.4), ("Ruin Archer", 5, 0.4), ("Field Shardling", 6, 0.2)], respawn=65,
         note="Stone sentinels and archers guard the old works. Tough, but arrows and gear sell well."),
]

APEX = dict(id="apex_watchtower", title="The Old Watchtower", levels=(28, 40), role="xp+money",
            note="The floor's apex spawn: an easy outer ring, a packed inner room, and a hidden rope to a cave. Contested: players can fight here.")

ROLE_TEXT = {"xp": "experience", "money": "money", "xp+money": "experience and money"}

# Where each camp sits is data; the map reads this list. Keys used elsewhere in the game:
#   camp_<id> points (tests and events), so ids must not change.
