#!/usr/bin/env python3
"""The four class outfits' palettes, written into palette.json (run after changing a colour here).

  python art/pipeline/outfit_palettes.py

Each colour is a (dark, light, mid) anchor triple turned into an 8-tone ramp by outfit_palette.ramp().
Keeping the anchors here (not hand-edited ramps in palette.json) makes a recolour a one-line change.
"""
from __future__ import annotations

import json
from pathlib import Path

from outfit_palette import SKIN, base, ramp

GOLD = ((120, 76, 10), (255, 236, 150), (226, 170, 40))
LEATHER = ((36, 20, 12), (170, 116, 70), (100, 62, 36))
STEEL = ((24, 28, 42), (210, 218, 232), (100, 110, 134))
BRIGHT_STEEL = ((30, 36, 52), (236, 242, 250), (124, 136, 160))
ROYAL = ((14, 22, 70), (104, 150, 240), (34, 66, 170))
MOSS = ((18, 40, 16), (150, 196, 96), (66, 112, 44))
FOREST = ((8, 26, 14), (82, 140, 78), (26, 70, 38))
CRIMSON = ((52, 8, 14), (236, 84, 72), (156, 26, 32))
CREAM = ((150, 140, 118), (255, 254, 246), (236, 230, 212))
PALE_GREEN = ((50, 84, 50), (204, 232, 180), (124, 168, 110))
LEAF = ((10, 40, 14), (110, 190, 80), (36, 104, 40))

OUTFITS = {
    "vanguard": {
        **base(hair=((36, 20, 12), (176, 118, 72)), arms=STEEL, legs=STEEL, boots=((16, 18, 28), (128, 138, 158)),
               torso=STEEL, cuff=((50, 58, 78), (232, 238, 246)), buckle=GOLD),
        "tabard": ramp(*ROYAL), "trim": ramp(*GOLD), "cape": ramp((10, 16, 54), (70, 110, 200), (24, 48, 132)),
        "pauldron": ramp(*BRIGHT_STEEL), "gorget": ramp(*STEEL), "knee": ramp(*BRIGHT_STEEL),
        "shield": ramp(*ROYAL), "rim": ramp(*GOLD), "blade": ramp((70, 80, 100), (252, 254, 255), (186, 198, 214)),
        "hilt": ramp(*GOLD),
    },
    "ranger": {
        **base(hair=((90, 60, 24), (236, 204, 130)), arms=MOSS, legs=((60, 46, 30), (206, 180, 138), (132, 108, 76)),
               boots=((26, 14, 10), (140, 92, 56), (78, 48, 28)), torso=MOSS, cuff=LEATHER, belt=LEATHER, buckle=GOLD),
        "hood": ramp(*FOREST), "cloak": ramp((6, 20, 12), (64, 116, 64), (20, 56, 30)), "quiver": ramp(*LEATHER),
        "fletch": ramp((150, 140, 120), (252, 250, 240)), "bow": ramp((50, 28, 12), (196, 140, 84), (120, 76, 40)),
        "string": ramp((170, 164, 150), (236, 232, 220)), "pouch": ramp(*LEATHER), "clasp": ramp(*GOLD),
    },
    "arcanist": {
        **base(hair=((14, 10, 12), (96, 78, 76)), arms=CRIMSON, legs=CRIMSON, boots=((14, 10, 10), (90, 70, 60)),
               torso=CRIMSON, cuff=GOLD, belt=GOLD, buckle=((170, 120, 30), (255, 246, 190))),
        "robe": ramp(*CRIMSON), "trim": ramp(*GOLD), "collar": ramp((30, 4, 10), (190, 50, 50), (100, 14, 22)),
        "rune": [[190, 250, 255]] * 8, "ember": ramp((230, 110, 20), (255, 250, 200), (255, 196, 70)),
    },
    "mystic": {
        **base(hair=((84, 50, 20), (232, 190, 120)), arms=CREAM, legs=CREAM, boots=((70, 46, 26), (206, 170, 120)),
               torso=CREAM, cuff=PALE_GREEN, belt=((60, 36, 18), (176, 128, 80)), buckle=((60, 36, 18), (176, 128, 80))),
        "robe": ramp(*CREAM), "over": ramp(*PALE_GREEN), "leaf": ramp(*LEAF), "rib": ramp((90, 150, 70), (200, 236, 150)),
        "bead": ramp((60, 32, 14), (196, 136, 80), (120, 74, 38)), "staff": ramp((44, 26, 12), (180, 128, 78), (104, 66, 36)),
        "bud": ramp((90, 200, 120), (236, 255, 220)), "circlet": ramp(*LEAF),
    },
}

# Vanguard addons (overlays; the approved base colours above stay untouched)
OUTFITS["vanguard"].update({
    "helm": ramp(*BRIGHT_STEEL), "crest": ramp(*ROYAL), "seam": [[12, 18, 50]] * 8,
    "mantle": ramp((10, 16, 54), (80, 120, 210), (26, 50, 140)), "fur": ramp((96, 84, 70), (250, 246, 236), (196, 184, 164)),
    "tuft": ramp((120, 108, 92), (255, 252, 244), (220, 210, 192)),
})

# Ranger, Arcanist and Mystic addons (overlays: new keys only, the approved base colours stay untouched)
_ADDON_KEYS = {
    "ranger": {
        "band": ramp(*LEATHER), "stud": ramp(*GOLD), "feather": ramp((70, 46, 22), (236, 214, 170), (160, 116, 66)),
        "bar": [[40, 26, 14]] * 8, "guard": ramp((30, 16, 10), (160, 108, 64), (88, 54, 30)),
        "edge": ramp((20, 10, 6), (120, 80, 48)), "horn": ramp((110, 90, 60), (250, 240, 214), (206, 184, 140)),
        "brass": ramp(*GOLD), "strap": ramp(*LEATHER),
    },
    "arcanist": {
        "circlet": ramp(*GOLD), "gem": [[150, 240, 255]] * 8, "stone": ramp((30, 26, 40), (176, 168, 190), (86, 78, 100)),
        "glow": [[190, 250, 255]] * 8, "cover": ramp((20, 8, 10), (140, 60, 50), (70, 24, 24)),
        "page": ramp((150, 132, 100), (255, 250, 230), (232, 218, 184)), "corner": ramp(*GOLD), "mark": [[150, 240, 255]] * 8,
    },
    "mystic": {
        "antler": ramp((60, 40, 22), (226, 204, 168), (150, 120, 84)), "tip": ramp((150, 140, 118), (255, 252, 240)),
        "sprout": ramp(*LEAF), "owl": ramp((70, 72, 84), (255, 255, 252), (196, 198, 204)),
        "wing": ramp((40, 42, 52), (220, 222, 226), (130, 132, 142)), "disc": ramp((170, 170, 176), (255, 255, 255), (236, 236, 240)),
        "owl_eye": [[230, 150, 30]] * 8, "beak": ramp((60, 50, 40), (220, 210, 190)), "talon": ramp((40, 34, 30), (180, 170, 150)),
    },
}
for _name, _keys in _ADDON_KEYS.items():
    assert not set(_keys) & set(OUTFITS[_name]), f"{_name}: an addon colour would replace a base colour"
    OUTFITS[_name].update(_keys)

# Men's and women's versions of the class outfits (2026-11-25): the base colours plus their own hair, so the
# version reads at game size. Their addons use these palettes too (the addon keys are copied with the rest).
def _with_hair(name, hair):
    r = ramp(*hair)
    return {**OUTFITS[name], "hair": r, "strand": [r[1]] * 8, "brow": [[int(c * 0.7) for c in r[1]]] * 8}


OUTFITS["vanguard_f"] = _with_hair("vanguard", ((50, 20, 10), (210, 130, 80), (130, 64, 34)))      # chestnut-red
OUTFITS["ranger_f"] = _with_hair("ranger", ((50, 14, 8), (230, 120, 70), (150, 50, 24)))          # auburn
OUTFITS["arcanist_m"] = _with_hair("arcanist", ((10, 8, 8), (90, 76, 72), (34, 28, 28)))           # black
OUTFITS["mystic_m"] = _with_hair("mystic", ((40, 24, 12), (170, 120, 72), (96, 62, 32)))           # brown, darker than her honey

# The Floor 10 boss uses the same figure, so its colours live here too.
HIDE = ((6, 16, 46), (120, 176, 236), (30, 70, 150))            # cerulean hide
HIDE_LIT = ((14, 34, 84), (160, 208, 250), (54, 106, 190))      # the paler raised muscle
IRON = ((8, 8, 14), (120, 124, 140), (44, 46, 58))
BONE = ((110, 100, 84), (252, 248, 236), (206, 196, 172))
CYAN_FIRE = ((40, 150, 230), (240, 255, 255), (130, 230, 255))
OUTFITS["azhrakkar"] = {
    **base(hair=((120, 130, 150), (250, 252, 255), (200, 208, 224)), arms=HIDE, legs=HIDE, boots=((6, 6, 10), (84, 86, 100)),
           torso=HIDE, cuff=IRON, belt=IRON, buckle=BONE, skin=ramp((4, 8, 28), (70, 110, 180), (16, 36, 92))),   # a dark face, so the eyes burn
    "muscle": ramp(*HIDE_LIT), "line": [[4, 10, 32]] * 8, "jaw": ramp((4, 8, 28), (70, 110, 180), (16, 36, 92)),
    "tusk": ramp(*BONE), "horn": ramp((20, 18, 24), (176, 168, 160), (84, 78, 80)), "flame": ramp(*CYAN_FIRE),
    "iron": ramp(*IRON), "spike": ramp((30, 30, 40), (190, 194, 208), (96, 100, 116)), "knee": ramp(*IRON),
    "claw": ramp(*BONE), "blade": ramp((16, 18, 30), (150, 158, 180), (60, 66, 86)),
    "edge": ramp((90, 100, 124), (250, 252, 255), (190, 200, 220)), "rune": [[150, 240, 255]] * 8,
    "hilt": ramp((30, 22, 16), (150, 120, 84)), "tail": ramp(*HIDE),
}
OUTFITS["azhrakkar"]["eye"] = [[190, 250, 255]] * 8
OUTFITS["azhrakkar"]["brow"] = ramp(*BONE)
OUTFITS["azhrakkar"]["nose"] = ramp((4, 8, 28), (70, 110, 180), (16, 36, 92))

# Bounty Warden (town NPC on the humanoid figure, 2026-11-25)
OXBLOOD = ((34, 6, 10), (196, 72, 62), (112, 22, 26))
BRASS = ((96, 62, 14), (255, 230, 150), (206, 156, 52))
IRON_GREY = ((40, 40, 44), (226, 224, 220), (132, 130, 128))
SALT_PEPPER = ((22, 20, 22), (170, 166, 160), (82, 78, 76))   # light grey hair read as a steel helmet
OUTFITS["warden"] = {
    **base(hair=SALT_PEPPER, arms=OXBLOOD, legs=((18, 20, 28), (124, 130, 146), (60, 64, 78)),
           boots=((8, 6, 8), (96, 84, 80), (34, 28, 30)), torso=OXBLOOD, cuff=BRASS,
           belt=((20, 12, 8), (120, 84, 56)), buckle=BRASS),
    "skirt": ramp(*OXBLOOD), "trim": ramp(*BRASS), "button": ramp(*BRASS), "collar": ramp(*OXBLOOD),
    "stock": ramp((30, 16, 8), (170, 116, 70), (88, 52, 26)), "bow": ramp((20, 22, 28), (210, 214, 222), (100, 104, 116)),
    "string": ramp((150, 140, 120), (236, 230, 214)), "strap": ramp((20, 12, 8), (130, 90, 58), (66, 42, 24)),
    "beard": ramp(*IRON_GREY),
    "poster": ramp((120, 96, 60), (252, 240, 210), (214, 192, 150)), "seal": ramp((90, 8, 10), (240, 90, 70), (170, 24, 24)),
    "iron": ramp((20, 22, 28), (190, 196, 206), (90, 94, 104)),
}

# Guild Warden (town NPC on the humanoid figure, 2026-11-25)
NAVY = ((6, 10, 34), (90, 116, 190), (22, 34, 92))
SILVER = ((60, 66, 80), (250, 252, 255), (176, 184, 198))
OUTFITS["guildwarden"] = {
    **base(hair=((20, 14, 10), (130, 96, 70), (64, 44, 30)), arms=NAVY, legs=NAVY, boots=((10, 8, 10), (90, 78, 72)),
           torso=NAVY, cuff=SILVER, belt=((24, 30, 60), (110, 130, 190)), buckle=SILVER),
    "robe": ramp(*NAVY), "trim": ramp(*SILVER), "stole": ramp(*SILVER), "badge": ramp(*GOLD),
    "beard": ramp((20, 14, 10), (130, 96, 70), (64, 44, 30)), "staff": ramp((40, 24, 10), (176, 124, 76), (100, 64, 34)),
    "finial": ramp(*GOLD), "banner": ramp((10, 16, 54), (96, 130, 214), (30, 50, 140)), "border": ramp(*GOLD),
}

# Quartermaster (town NPC on the humanoid figure, 2026-11-25)
OLIVE = ((24, 28, 10), (170, 176, 100), (88, 96, 44))
OUTFITS["quartermaster"] = {
    **base(hair=((50, 50, 54), (220, 218, 214), (130, 128, 126)), arms=OLIVE, legs=((60, 46, 30), (206, 180, 138), (132, 108, 76)),
           boots=((26, 14, 10), (140, 92, 56), (78, 48, 28)), torso=OLIVE, cuff=LEATHER, belt=LEATHER, buckle=GOLD),
    "vest": ramp((24, 12, 8), (150, 100, 62), (78, 46, 26)), "edge": ramp((14, 8, 4), (100, 66, 40)),
    "bandolier": ramp(*LEATHER), "vial": ramp((70, 10, 14), (255, 140, 120), (196, 40, 40)),
    "stopper": ramp((60, 40, 20), (210, 170, 120)), "stache": ramp((50, 50, 54), (220, 218, 214), (130, 128, 126)),
    "crate": ramp((50, 30, 12), (214, 166, 104), (140, 96, 52)), "slat": ramp((30, 18, 8), (130, 90, 50)),
    "shaft": ramp((70, 46, 20), (220, 180, 120)), "fletch": ramp((150, 140, 120), (252, 250, 240)),
    "forearm": SKIN, "hat": ramp((16, 16, 22), (150, 150, 162), (60, 60, 72)),   # grey felt: brown merged with the crate, green with the tunic
}

# Hunter Brannoch (Floor 1 NPC on the humanoid figure, 2026-11-25)
WOLF = ((34, 34, 40), (210, 206, 200), (110, 108, 108))
OUTFITS["brannoch"] = {
    **base(hair=((16, 10, 8), (110, 76, 50), (50, 32, 20)), arms=((40, 22, 12), (176, 120, 72), (100, 62, 34)),
           legs=((36, 24, 14), (150, 110, 70), (84, 58, 34)), boots=((18, 10, 6), (120, 80, 48), (60, 38, 20)),
           torso=((40, 22, 12), (176, 120, 72), (100, 62, 34)), cuff=LEATHER, belt=((20, 12, 8), (110, 76, 46)), buckle=GOLD),
    "pelt": ramp(*WOLF), "muzzle": ramp((120, 116, 108), (250, 248, 240), (206, 202, 194)), "wolfeye": [[30, 20, 14]] * 8,
    "claw": ramp((150, 140, 118), (255, 252, 240)), "beard": ramp((16, 10, 8), (110, 76, 50), (50, 32, 20)),
    "scar": [[236, 176, 160]] * 8, "bow": ramp((30, 16, 8), (150, 100, 56), (76, 46, 22)),
    "string": ramp((150, 140, 120), (236, 230, 214)), "bracer": ramp((20, 12, 8), (130, 90, 58), (66, 42, 24)),
    "knife": ramp((50, 54, 64), (230, 234, 240), (140, 146, 158)),
}

# Road Bandit (Floor 1 monster on the humanoid figure, 2026-11-25)
MUD = ((30, 20, 12), (170, 134, 92), (92, 66, 40))
OUTFITS["bandit"] = {
    **base(hair=((16, 10, 8), (100, 70, 46)), arms=((18, 18, 22), (130, 128, 126), (54, 54, 58)),
           legs=((36, 24, 14), (150, 110, 70), (84, 58, 34)), boots=((16, 10, 6), (110, 76, 46), (54, 36, 20)),
           torso=((18, 18, 22), (130, 128, 126), (54, 54, 58)), cuff=LEATHER, belt=((20, 12, 8), (110, 76, 46)),
           buckle=((60, 60, 66), (200, 200, 206))),
    "hood": ramp(*MUD), "rim": ramp((16, 10, 6), (96, 70, 44)), "cape": ramp(*MUD),
    "scarf": ramp((60, 8, 10), (236, 90, 70), (170, 30, 30)), "lace": ramp((20, 12, 8), (120, 86, 56)),
    "pouch": ramp(*LEATHER), "buckler": ramp((40, 24, 12), (176, 124, 76), (100, 64, 34)),
    "iron": ramp((26, 28, 34), (190, 194, 204), (90, 94, 104)), "blade": ramp((60, 66, 78), (240, 244, 250), (160, 168, 182)),
    "hilt": ramp((30, 18, 10), (140, 100, 60)),
}

# Bandit Captain (Floor 1 boss on the humanoid figure, 2026-11-25)
COAL = ((10, 10, 12), (110, 104, 100), (40, 38, 38))
OUTFITS["captain"] = {
    **base(hair=((8, 6, 6), (80, 66, 60), (30, 24, 22)), arms=COAL, legs=((30, 22, 18), (140, 110, 86), (74, 56, 42)),
           boots=((8, 6, 6), (90, 78, 70), (34, 28, 26)), torso=((70, 10, 12), (236, 96, 80), (160, 30, 30)),
           cuff=GOLD, belt=COAL, buckle=GOLD),
    "coat": ramp(*COAL), "trim": ramp(*GOLD), "sash": ramp((60, 8, 10), (240, 96, 76), (176, 30, 30)), "button": ramp(*GOLD),
    "beard": ramp((8, 6, 6), (80, 66, 60), (30, 24, 22)), "hat": ramp((8, 8, 10), (96, 92, 96), (32, 30, 34)),
    "brass": ramp(*GOLD), "plume": ramp((90, 8, 10), (255, 120, 96), (210, 40, 36)),
    "blade": ramp((70, 80, 100), (252, 254, 255), (186, 198, 214)), "guard": ramp(*GOLD), "earring": ramp(*GOLD),
}

# Ruin Archer (Floor 1 monster on the humanoid figure, 2026-11-25): a skeleton
IVORY = ((70, 60, 46), (252, 246, 224), (196, 184, 156))
ROT = ((16, 12, 10), (110, 90, 70), (50, 40, 32))
OUTFITS["archer"] = {
    **base(hair=IVORY, arms=IVORY, legs=IVORY, boots=IVORY, torso=((40, 34, 28), (170, 160, 136), (100, 92, 76)),
           cuff=ROT, belt=ROT, buckle=((40, 40, 44), (150, 150, 156)), skin=ramp(*IVORY)),
    "jerkin": ramp(*ROT), "tatter": ramp((10, 8, 6), (80, 64, 50)), "rib": ramp(*IVORY), "jaw": ramp(*IVORY),
    "tooth": ramp((150, 140, 118), (255, 252, 240)), "knob": ramp(*IVORY), "bow": ramp((30, 16, 8), (150, 100, 56), (76, 46, 22)),
    "string": ramp((150, 140, 120), (236, 230, 214)), "quiver": ramp(*ROT), "shaft": ramp((70, 46, 20), (220, 180, 120)),
}
OUTFITS["archer"]["eye"] = [[14, 30, 18]] * 8          # near-black sockets, a hint of green
OUTFITS["archer"]["nose"] = [[40, 30, 24]] * 8         # the nose hole
OUTFITS["archer"]["brow"] = ramp(*IVORY)

# Ruin Sentinel (Floor 1 monster on the humanoid figure, 2026-11-25): a stone statue
STONE = ((34, 34, 38), (214, 206, 186), (120, 118, 114))
MOSS_G = ((14, 34, 12), (140, 186, 80), (60, 104, 36))
OUTFITS["sentinel"] = {
    **base(hair=STONE, arms=STONE, legs=STONE, boots=STONE, torso=STONE, cuff=STONE, belt=((26, 26, 30), (150, 146, 136)),
           buckle=STONE, skin=ramp(*STONE)),
    "helm": ramp(*STONE), "visor": [[16, 18, 24]] * 8, "crest": ramp(*STONE), "block": ramp(*STONE), "moss": ramp(*MOSS_G),
    "crack": [[24, 22, 24]] * 8, "spear": ramp(*STONE), "tip": ramp((60, 60, 66), (236, 232, 222), (150, 148, 144)),
    "band": ramp((26, 26, 30), (150, 146, 136)),
}
OUTFITS["sentinel"]["eye"] = [[170, 230, 255]] * 8      # pale-blue glow in the visor
OUTFITS["sentinel"]["brow"] = ramp(*STONE)
OUTFITS["sentinel"]["nose"] = ramp(*STONE)

# Bandit Crossbowman and Hedge Hexer (2026-11-25): the approved bandit's colours with their own gear
OLIVE_DRAB = ((20, 22, 12), (140, 140, 96), (66, 68, 40))
OUTFITS["crossbowman"] = {**OUTFITS["bandit"], "hood": ramp(*OLIVE_DRAB), "cape": ramp(*OLIVE_DRAB),
    "rim": ramp((10, 12, 6), (80, 80, 50)), "scarf": ramp((40, 22, 12), (180, 120, 70), (110, 66, 34)),
    "xbow": ramp((30, 16, 8), (150, 100, 56), (76, 46, 22)), "arm": ramp((26, 28, 34), (200, 204, 214), (100, 104, 116)),
    "string": ramp((150, 140, 120), (236, 230, 214)), "bolt": ramp((70, 46, 20), (230, 200, 150)), "case": ramp(*LEATHER)}
PLUM = ((30, 14, 28), (170, 120, 160), (90, 50, 86))
OUTFITS["hexer"] = {**OUTFITS["bandit"], "hair": ramp((60, 60, 64), (226, 224, 220), (140, 138, 136)),
    "strand": [[100, 98, 96]] * 8, "brow": [[110, 108, 106]] * 8,
    # her gear reuses hidden bandit parts (models have at most 33 parts): buckler = shawl patches, hilt = staff,
    # iron = bone charms, scarf = the green mending glow, pouch = herb bundles
    "shawl": ramp(*PLUM), "buckler": ramp((40, 30, 20), (176, 150, 110), (110, 90, 60)),
    "hilt": ramp((30, 18, 8), (140, 100, 60), (70, 46, 24)), "iron": ramp((150, 140, 118), (255, 252, 240)),
    "scarf": [[90, 230, 70]] * 8, "pouch": ramp((20, 40, 14), (140, 180, 90), (70, 100, 40))}

# Hearthgate Watch (town guards and their captain, 2026-11-25): ember red, iron, a gold hearth badge
EMBER_RED = ((50, 10, 8), (230, 110, 80), (160, 40, 30))
IRON_W = ((24, 26, 32), (210, 214, 222), (104, 108, 120))
OUTFITS["watchguard"] = {
    **base(hair=((16, 10, 8), (100, 70, 46)), arms=EMBER_RED, legs=((36, 24, 14), (150, 110, 70), (84, 58, 34)),
           boots=((18, 10, 6), (120, 80, 48), (60, 38, 20)), torso=EMBER_RED, cuff=LEATHER, belt=LEATHER, buckle=IRON_W),
    "helm": ramp(*IRON_W), "brim": ramp(*IRON_W), "gambeson": ramp(*EMBER_RED), "quilt": [[90, 20, 16]] * 8,
    "hem": ramp(*GOLD), "badge": ramp(*GOLD), "spear": ramp((40, 24, 10), (176, 124, 76), (100, 64, 34)),
    "tip": ramp(*IRON_W), "whistle": ramp((150, 140, 118), (255, 252, 240)),
}

OUTFITS["dorrow"] = {**OUTFITS["watchguard"], "hair": ramp((50, 50, 54), (220, 218, 214), (130, 128, 126)),
    "strand": [[96, 94, 92]] * 8, "brow": [[110, 108, 106]] * 8,
    "cape": ramp((40, 6, 6), (200, 80, 60), (120, 24, 20)), "epaulette": ramp(*GOLD),
    "scabbard": ramp((20, 12, 8), (120, 84, 56), (60, 38, 24))}

# Alchemist Ivo and Runewright Mael (Hearthgate crafters, 2026-11-25)
MUSTARD = ((40, 30, 6), (230, 200, 110), (160, 126, 40))
OUTFITS["alchemist"] = {
    **base(hair=((60, 20, 6), (250, 150, 80), (190, 80, 30)), arms=MUSTARD, legs=((10, 26, 16), (90, 140, 100), (30, 70, 44)),
           boots=((18, 10, 6), (120, 80, 48), (60, 38, 20)), torso=MUSTARD, cuff=MUSTARD, belt=LEATHER, buckle=GOLD),
    "smock": ramp(*MUSTARD), "stain": [[110, 120, 40]] * 8, "hem": ramp((60, 46, 10), (200, 170, 90)),
    "goggle": ramp(*GOLD), "lens": [[140, 220, 230]] * 8, "flask": ramp((20, 70, 30), (190, 255, 160), (80, 200, 90)),
    "vapour": [[200, 255, 190]] * 8, "vial": ramp((70, 10, 14), (255, 140, 120), (196, 40, 40)),
    "cork": ramp((60, 40, 20), (210, 170, 120)),
}
SLATE_BLUE = ((14, 20, 34), (150, 170, 200), (60, 76, 106))
OUTFITS["runewright"] = {
    **base(hair=((20, 14, 10), (110, 80, 56), (50, 34, 22)), arms=SLATE_BLUE, legs=((36, 24, 14), (150, 110, 70), (84, 58, 34)),
           boots=((18, 10, 6), (120, 80, 48), (60, 38, 20)), torso=SLATE_BLUE, cuff=LEATHER, belt=LEATHER, buckle=GOLD),
    "tunic": ramp(*SLATE_BLUE), "dust": [[220, 216, 206]] * 8, "tablet": ramp((16, 18, 22), (130, 136, 146), (50, 54, 62)),
    "rune": [[130, 240, 255]] * 8, "beard": ramp((20, 14, 10), (110, 80, 56), (50, 34, 22)), "bead": ramp(*GOLD),
    "tool": ramp((40, 40, 46), (210, 214, 222), (110, 114, 124)), "wrap": ramp((150, 140, 118), (240, 232, 214)),
}

# Weaponsmith Garrick (2026-11-25): soot leather, bronze skin, iron hammer, red bandana
BRONZE_SKIN = ((70, 34, 20), (240, 180, 130), (170, 100, 60))
OUTFITS["smith"] = {
    **base(hair=((8, 8, 10), (70, 66, 70), (26, 24, 28)), arms=((90, 80, 66), (240, 232, 214), (186, 174, 150)),
           legs=((30, 22, 16), (130, 100, 74), (70, 52, 36)), boots=((14, 8, 6), (100, 70, 44), (46, 30, 18)),
           torso=((90, 80, 66), (240, 232, 214), (186, 174, 150)), cuff=LEATHER, belt=LEATHER,
           buckle=((40, 40, 46), (190, 194, 204)), skin=ramp(*BRONZE_SKIN)),
    "vest": ramp((18, 10, 6), (120, 82, 50), (56, 36, 20)), "rivet": ramp((60, 60, 66), (230, 232, 236)),
    "bare": ramp(*BRONZE_SKIN), "gauntlet": ramp((20, 12, 8), (130, 90, 58), (66, 42, 24)),
    "beard": ramp((8, 8, 10), (70, 66, 70), (26, 24, 28)), "bandana": ramp((60, 8, 10), (236, 90, 70), (170, 30, 30)),
    "hammer": ramp((24, 26, 32), (200, 204, 214), (90, 94, 106)), "haft": ramp((30, 18, 8), (140, 100, 60)),
    "tongs": ramp((24, 26, 32), (180, 184, 194)), "soot": [[30, 28, 28]] * 8,
}

# Little Bix (2026-11-25): bright green tunic, straw hair, red scarf, a wooden toy sword
OUTFITS["bix"] = {
    **base(hair=((110, 80, 20), (255, 236, 150), (220, 180, 70)), arms=((10, 50, 16), (130, 220, 110), (40, 140, 50)),
           legs=((36, 24, 14), (150, 110, 70), (84, 58, 34)), boots=((18, 10, 6), (120, 80, 48), (60, 38, 20)),
           torso=((10, 50, 16), (130, 220, 110), (40, 140, 50)), cuff=((10, 50, 16), (130, 220, 110), (40, 140, 50)),
           belt=LEATHER, buckle=GOLD),
    "tunic": ramp((10, 50, 16), (130, 220, 110), (40, 140, 50)), "patch": ramp((60, 46, 26), (200, 170, 120)),
    "scarf": ramp((60, 8, 10), (240, 96, 76), (176, 30, 30)), "toysword": ramp((60, 36, 14), (230, 190, 130), (160, 116, 64)),
    "grip": ramp((40, 24, 10), (150, 110, 70)),
}

# Hill Cutthroat (2026-11-25): the bandit in sun-faded ochre, unmasked with red war paint, two curved knives
OCHRE = ((50, 34, 10), (230, 196, 120), (160, 120, 50))
OUTFITS["cutthroat"] = {**OUTFITS["bandit"], "hood": ramp(*OCHRE), "cape": ramp(*OCHRE), "rim": ramp((40, 26, 8), (150, 116, 60)),
    "knife": ramp((70, 80, 100), (252, 254, 255), (186, 198, 214)), "paint": [[200, 30, 24]] * 8,
    "fetish": ramp((150, 140, 118), (255, 252, 240))}

if __name__ == "__main__":
    path = Path(__file__).resolve().parent / "palette.json"
    data = json.loads(path.read_text())
    data["ramps"].update(OUTFITS)
    path.write_text(json.dumps(data, indent=1))
    print("wrote outfit palettes:", ", ".join(OUTFITS))
