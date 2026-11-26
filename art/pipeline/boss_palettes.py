#!/usr/bin/env python3
"""The Floor 1 bosses' palettes, written into palette.json (run after changing a colour here).

  python art/pipeline/boss_palettes.py

Each colour is a (dark, light, mid) anchor triple turned into an 8-tone ramp by outfit_palette.ramp(), so a
recolour is a one-line change here, never a hand edit in palette.json.
"""
from __future__ import annotations

import json
from pathlib import Path

from outfit_palette import ramp

# Gate Hound: sooty slate-blue coat (Tibia's Hellhound is red-black; our boar is charcoal), ash muzzles,
# black iron collars with pale steel spikes, ember eyes and ember-lit jaws.
SLATE = ((38, 45, 62), (160, 174, 192), (78, 92, 114))   # shadows deep blue-grey, never black
SLATE_DARK = ((28, 34, 48), (112, 124, 142), (58, 68, 86))
ASH = ((40, 38, 44), (214, 206, 196), (128, 122, 122))
IRON = ((40, 44, 56), (226, 230, 236), (120, 126, 140))   # lighter than the coat, so the collar reads as a band
STEEL = ((60, 62, 72), (246, 246, 240), (168, 170, 176))
EMBER = ((96, 18, 6), (255, 214, 120), (246, 110, 30))
NIGHT = ((6, 7, 12), (40, 44, 58), (20, 22, 32))

GATE_HOUND = {
    "body": ramp(*SLATE), "head": ramp(*SLATE), "head2": ramp(*SLATE), "tail_base": ramp(*SLATE),
    "belly": ramp(*ASH), "snout": ramp(*ASH), "snout2": ramp(*ASH), "bib": ramp(*ASH),
    "nose": ramp((8, 8, 12), (90, 90, 100), (30, 30, 38)), "ear": ramp(*SLATE_DARK),
    "eye": [[255, 150, 40]],
    "leg_near": ramp(*SLATE_DARK), "leg_far": ramp((6, 8, 12), (56, 62, 74), (22, 26, 36)),
    "paw_near": ramp(*NIGHT), "paw_far": ramp((4, 5, 8), (26, 28, 36), (12, 14, 20)),
    "tail_tip": ramp(*NIGHT), "saddle": ramp(*SLATE_DARK), "brow": ramp((16, 18, 26), (58, 64, 80)),   # saddle: a darker ridge, not black spots
    "line": ramp((6, 4, 6), (40, 24, 20)), "collar": ramp(*IRON), "spike": ramp(*STEEL),
    "maw": ramp(*EMBER), "claw": ramp(*STEEL), "scar": ramp((70, 60, 66), (196, 184, 180)),
}

# Axe-Lord of the Stair: rusted bronze plate with teal patina, a ragged crimson tabard, dark leather, bone horns on
# the helm, pale steel axe blades, a gold glow through the visor slit. (Tibia's knights are steel and blue.)
BRONZE = ((38, 20, 10), (250, 206, 130), (150, 92, 40))
BRONZE_DARK = ((24, 13, 8), (190, 140, 80), (96, 58, 28))
PATINA = ((18, 46, 42), (156, 210, 184), (64, 124, 106))
CRIMSON = ((48, 8, 14), (232, 90, 76), (150, 28, 34))
LEATHER = ((20, 12, 8), (130, 88, 56), (64, 40, 24))
BONE = ((70, 58, 40), (246, 236, 210), (176, 160, 130))
GOLD = ((110, 70, 12), (255, 236, 150), (222, 168, 44))
WOOD = ((28, 16, 10), (150, 104, 62), (82, 52, 30))
BLADE = ((64, 70, 84), (252, 254, 255), (176, 186, 202))

AXE_LORD = {
    "helm": ramp(*BRONZE), "skin": ramp(*BRONZE), "hair": ramp(*BRONZE_DARK), "strand": ramp(*BRONZE_DARK),
    "torso": ramp(*BRONZE), "bronze": ramp(*BRONZE), "arm_a": ramp(*BRONZE_DARK), "arm_b": ramp(*BRONZE_DARK),
    "hand": ramp(*BRONZE_DARK), "cuff": ramp(*GOLD), "leg_a": ramp(*LEATHER), "leg_b": ramp(*LEATHER),
    "boot_a": ramp(*BRONZE_DARK), "boot_b": ramp(*BRONZE_DARK), "sole": [[14, 10, 8]] * 8,
    "belt": ramp(*LEATHER), "buckle": ramp(*GOLD), "patina": ramp(*PATINA), "cloth": ramp(*CRIMSON),
    "trim": ramp(*GOLD), "emblem": ramp(*GOLD), "rivet": ramp(*GOLD), "horn": ramp(*BONE),
    "visor": ramp((6, 4, 4), (44, 28, 22)), "eye": [[255, 226, 150]], "brow": ramp((6, 4, 4), (44, 28, 22)),
    "nose": ramp(*BRONZE), "haft": ramp(*WOOD), "wrap": ramp(*LEATHER), "steel": ramp(*BLADE),
    "edge": ramp((140, 150, 166), (255, 255, 255)), "line": ramp((16, 8, 4), (70, 40, 20)), "knee": ramp(*BRONZE),
}

EMBER_GLOW = ((150, 40, 6), (255, 236, 160), (255, 128, 30))
AXE_LORD["glow"] = ramp(*EMBER_GLOW)

# The last phase must read as a different fight at a glance (Jay, 2026-11-25: "If there is supposed to be a visual
# phase shift, my eyes can't pick it up"): scorched, blackened bronze, fire glowing through cracks in the plate,
# red eyes, a red-hot edge on the blade, a darker, burnt tabard.
SCORCHED = ((16, 10, 8), (150, 104, 66), (66, 40, 22))
SCORCHED_DARK = ((10, 7, 6), (106, 74, 48), (42, 26, 16))
AXE_LORD_BLADE = {**AXE_LORD,
    "helm": ramp(*SCORCHED), "skin": ramp(*SCORCHED), "torso": ramp(*SCORCHED), "bronze": ramp(*SCORCHED),
    "nose": ramp(*SCORCHED), "knee": ramp(*SCORCHED), "hair": ramp(*SCORCHED_DARK), "strand": ramp(*SCORCHED_DARK),
    "arm_a": ramp(*SCORCHED_DARK), "arm_b": ramp(*SCORCHED_DARK), "hand": ramp(*SCORCHED_DARK),
    "boot_a": ramp(*SCORCHED_DARK), "boot_b": ramp(*SCORCHED_DARK),
    "patina": ramp((20, 30, 26), (96, 120, 104), (44, 62, 54)), "cloth": ramp((28, 6, 8), (150, 46, 34), (84, 16, 18)),
    "eye": [[255, 60, 30]], "edge": ramp(*EMBER_GLOW), "glow": ramp(*EMBER_GLOW),
}

# Old Tusk: the Bristle Boar grown ancient (secret boss in the Boar Meadow): grizzled charcoal frosted grey on the
# back and muzzle, the ember crest burnt down to pale frosted tips, a yellowed tusk, old arrows in his back.
GRIZZLE = ((24, 20, 18), (172, 164, 154), (70, 62, 56))
OLD_TUSK = {
    "body": ramp(*GRIZZLE), "head": ramp(*GRIZZLE), "tail_base": ramp(*GRIZZLE),
    "belly": ramp((26, 20, 18), (128, 112, 104), (62, 52, 48)), "snout": ramp((44, 38, 36), (196, 184, 176), (112, 100, 94)),
    "nose": ramp((96, 70, 66), (234, 212, 204), (170, 138, 130)), "ear": ramp((18, 14, 14), (110, 100, 96), (52, 46, 44)),
    "eye": [[255, 54, 24]],
    "leg_near": ramp((20, 16, 16), (112, 104, 98), (52, 46, 42)), "leg_far": ramp((12, 10, 10), (60, 54, 52), (30, 26, 24)),
    "paw_near": ramp((8, 7, 8), (60, 54, 52), (28, 24, 24)), "paw_far": ramp((6, 5, 6), (32, 28, 28), (16, 14, 14)),
    "tail_tip": ramp((70, 14, 8), (250, 220, 190), (200, 90, 40)),
    "crest": ramp((70, 14, 8), (255, 206, 150), (224, 92, 34)),       # still ember, a little paler at the tips
    "frost": ramp((48, 44, 42), (170, 164, 158), (100, 94, 90)),   # grizzle: grey frosting, never white patches
    "tusk": ramp((110, 88, 54), (252, 240, 204), (200, 176, 124)), "brow": ramp((8, 6, 8), (30, 26, 28)),
    "shaft": ramp((40, 26, 16), (196, 160, 112), (120, 88, 56)), "fletch": ramp((96, 92, 86), (252, 250, 244), (196, 192, 184)),   # white feathers: not the crest
    "scar": ramp((96, 70, 72), (222, 196, 190), (160, 128, 126)),
}

# Hollowfang: the Wolf Copse's hidden master. Night-black with an indigo cast (Tibia's wolves are grey, our alpha is
# teal-silver), a bone-white streak from brow to tail, one great ivory fang, yellow-green eyes.
NIGHTFUR = ((22, 20, 34), (138, 134, 162), (56, 52, 78))
HOLLOWFANG = {
    "body": ramp(*NIGHTFUR), "head": ramp(*NIGHTFUR), "tail_base": ramp(*NIGHTFUR),
    "belly": ramp((26, 24, 36), (120, 116, 136), (60, 56, 74)), "snout": ramp((30, 28, 40), (150, 146, 164), (74, 70, 90)),
    "bib": ramp((40, 38, 50), (176, 172, 186), (96, 92, 110)), "nose": ramp((6, 6, 10), (60, 58, 70), (24, 22, 30)),
    "ear": ramp((14, 12, 22), (96, 92, 116), (40, 36, 56)), "eye": [[206, 255, 96]],
    # legs a step LIGHTER than the coat and far legs darker, so each leg reads on its own; pale grey socks
    "leg_near": ramp((34, 32, 48), (164, 160, 186), (78, 74, 102)), "leg_far": ramp((12, 11, 18), (72, 68, 90), (32, 30, 44)),
    "paw_near": ramp((70, 68, 78), (226, 224, 230), (150, 148, 158)), "paw_far": ramp((36, 34, 42), (120, 118, 128), (72, 70, 80)),
    "tail_tip": ramp((110, 106, 100), (250, 248, 240), (196, 192, 184)),
    "saddle": ramp((12, 11, 20), (84, 80, 104), (34, 32, 48)), "brow": ramp((6, 6, 10), (30, 28, 40)),
    "line": ramp((6, 5, 8), (40, 32, 36)), "stripe": ramp((110, 106, 100), (252, 250, 244), (200, 196, 188)),
    "fang": ramp((120, 104, 70), (255, 250, 228), (214, 200, 160)), "scar": ramp((90, 76, 84), (206, 190, 196), (150, 132, 140)),
}

# Briar Mother: the thornsnaps' mother (hidden mini-boss in Thornsnap Hollow). Wine-purple bramble (never grass green,
# CRAWLER_RULES C1), olive leaves, pale thorns, rose-pink blossoms, magenta throats.
BRIAR_MOTHER = {
    "briar": ramp((26, 10, 20), (176, 104, 132), (86, 36, 62)), "vine": ramp((22, 12, 18), (150, 96, 112), (70, 36, 52)),
    "root": ramp((24, 16, 12), (130, 100, 78), (66, 46, 34)), "bud": ramp((22, 26, 16), (150, 160, 104), (62, 72, 40)),   # dark olive jaws, not watermelons
    "throat": ramp((110, 10, 70), (255, 190, 236), (232, 60, 160)), "petal": ramp((110, 30, 60), (255, 214, 226), (226, 104, 140)),
    "bloom": ramp((110, 30, 60), (255, 220, 230), (230, 110, 150)), "thorn": ramp((120, 108, 84), (252, 246, 226), (208, 194, 160)),
    "leaf": ramp((18, 36, 22), (128, 168, 96), (50, 90, 48)), "rib": ramp((100, 130, 80), (220, 236, 190)),
    "eye": [[255, 230, 120]],
}

# The Underkeeper: the jailer of the dungeon under Hearthgate. Bone, black iron, rotted grey-brown cloth, ghost-teal
# fire in his lantern and eyes, tarnished brass keys, a rust-red padlock.
BONE2 = ((70, 64, 50), (244, 238, 214), (176, 166, 136))
ROT = ((22, 20, 18), (146, 134, 114), (70, 64, 54))
IRON2 = ((16, 18, 22), (160, 166, 172), (64, 68, 76))
GHOST = ((20, 90, 80), (226, 255, 244), (90, 230, 200))
UNDERKEEPER = {
    "skin": ramp(*BONE2), "bone": ramp(*BONE2), "hand": ramp(*BONE2), "arm_a": ramp(*BONE2), "arm_b": ramp(*BONE2),
    "nose": ramp(*BONE2), "brow": ramp((10, 8, 6), (60, 50, 40)), "hair": ramp(*IRON2), "strand": ramp(*IRON2),
    "eye": [[150, 255, 226]], "torso": ramp(*ROT), "robe": ramp(*ROT), "hem": ramp((14, 12, 10), (96, 88, 74), (42, 38, 32)),
    "leg_a": ramp(*BONE2), "leg_b": ramp(*BONE2), "boot_a": ramp((18, 14, 12), (110, 92, 74), (52, 42, 34)),
    "boot_b": ramp((18, 14, 12), (110, 92, 74), (52, 42, 34)), "sole": [[12, 10, 8]] * 8, "cuff": ramp(*IRON2),
    "belt": ramp((20, 14, 10), (120, 90, 62), (60, 42, 28)), "buckle": ramp(*IRON2), "iron": ramp(*IRON2),
    "chain": ramp((26, 28, 32), (196, 200, 206), (96, 100, 108)), "lock": ramp((44, 18, 8), (210, 124, 70), (126, 58, 26)),
    "lantern": ramp((40, 28, 10), (226, 186, 104), (124, 88, 38)), "flame": ramp(*GHOST), "glow": ramp(*GHOST),
    "key": ramp((60, 44, 14), (240, 210, 124), (152, 118, 48)), "rib": ramp((90, 84, 66), (240, 234, 210), (180, 170, 140)),
}

BOSSES = {"gate_hound": GATE_HOUND, "axe_lord": AXE_LORD, "axe_lord_blade": AXE_LORD_BLADE, "old_tusk": OLD_TUSK,
          "hollowfang": HOLLOWFANG, "briar_mother": BRIAR_MOTHER, "underkeeper": UNDERKEEPER,
          "vault_wraith": {
              # a spectral violet shroud (Tibia's ghost is white), a dark hood, amber eyes, bound to an iron strongbox
              "shroud": ramp((30, 16, 44), (206, 178, 240), (106, 72, 154)), "hood": ramp((16, 8, 26), (128, 98, 170), (56, 36, 86)),
              "face": ramp((6, 4, 10), (40, 28, 52)), "eye": [[255, 210, 90]],
              "claw": ramp((80, 70, 90), (238, 230, 248), (162, 152, 182)), "box": ramp((18, 16, 20), (152, 148, 158), (62, 58, 68)),
              "gold": ramp(*GOLD), "chain": ramp((60, 40, 90), (232, 214, 255), (150, 120, 210)), "coin": ramp(*GOLD),
          }}


# ---- Floor 1 ground elites (ART_REQUESTS.md Batch 7): each is its ground's monster with one big readable change.
# Moonhowl: moon-white wolf with lavender shadows, a midnight-blue saddle and tail tip, a gold crescent on the brow.
MOONFUR = ((58, 56, 86), (252, 250, 242), (176, 176, 200))
MIDNIGHT = ((12, 14, 36), (104, 118, 178), (34, 42, 88))
MOONHOWL = {
    "body": ramp(*MOONFUR), "head": ramp(*MOONFUR), "tail_base": ramp(*MOONFUR),
    "belly": ramp((70, 68, 96), (240, 238, 236), (160, 158, 182)), "snout": ramp((76, 74, 100), (255, 254, 248), (190, 190, 210)),
    "bib": ramp((86, 84, 110), (255, 255, 252), (206, 206, 222)), "nose": ramp((8, 8, 16), (60, 60, 80), (24, 24, 38)),
    "ear": ramp(*MIDNIGHT), "eye": [[150, 230, 255]],
    "leg_near": ramp((52, 50, 78), (236, 234, 240), (160, 160, 186)), "leg_far": ramp((30, 30, 52), (140, 140, 166), (78, 78, 108)),
    "paw_near": ramp((40, 40, 66), (200, 200, 220), (120, 120, 150)), "paw_far": ramp((22, 22, 40), (110, 110, 136), (60, 60, 86)),
    "tail_tip": ramp(*MIDNIGHT), "saddle": ramp(*MIDNIGHT), "brow": ramp((10, 10, 26), (60, 62, 96)),
    "line": ramp((8, 8, 20), (50, 50, 80)), "crescent": ramp((150, 110, 30), (255, 250, 200), (250, 214, 110)),
}
# Old Bristleback: a dark bark-olive boar (Tibia's boar is orange-brown, ours charcoal, Old Tusk grizzled grey) with a
# blacker face mask, a mantle of near-black quills with bone-pale tips, amber eyes.
BARK = ((20, 17, 10), (158, 142, 98), (76, 66, 40))
BRISTLEBACK = {
    "body": ramp(*BARK), "head": ramp((12, 13, 8), (112, 108, 72), (50, 50, 30)), "tail_base": ramp(*BARK),
    "belly": ramp((18, 18, 12), (120, 114, 84), (60, 58, 38)), "snout": ramp((26, 24, 18), (150, 140, 112), (82, 76, 58)),
    "nose": ramp((92, 66, 60), (232, 200, 186), (178, 140, 126)), "ear": ramp((10, 11, 7), (96, 92, 60), (44, 44, 26)),
    "eye": [[255, 190, 40]],
    "leg_near": ramp((14, 15, 9), (118, 114, 76), (56, 56, 34)), "leg_far": ramp((8, 9, 6), (62, 60, 40), (30, 30, 20)),
    "paw_near": ramp((8, 7, 6), (56, 50, 42), (26, 22, 18)), "paw_far": ramp((5, 5, 4), (30, 28, 24), (14, 13, 11)),
    "tail_tip": ramp((10, 9, 8), (84, 76, 62), (38, 34, 28)),
    "quill": ramp((8, 7, 6), (92, 82, 66), (36, 32, 26)), "quilltip": ramp((120, 104, 76), (255, 248, 222), (214, 198, 160)),
    "tusk": ramp((120, 108, 84), (254, 252, 240), (220, 210, 180)), "brow": ramp((6, 5, 4), (30, 26, 18)),
}
# Mossback Snapper: peat-brown shell under bright moss cushions, olive-brown skin, orange toadstools, a red eye.
MOSS = ((22, 30, 8), (226, 232, 110), (112, 136, 30))
MOSSBACK = {
    "shell": ramp((20, 14, 10), (130, 100, 70), (62, 44, 30)), "rim": ramp((40, 32, 20), (170, 150, 108), (100, 84, 56)),
    "seam": ramp((8, 6, 4), (40, 30, 20)), "knob": ramp((110, 100, 76), (246, 238, 214), (196, 184, 150)),
    "reed": ramp((40, 56, 20), (190, 210, 120), (110, 140, 60)),
    "head": ramp((22, 22, 12), (150, 140, 92), (72, 68, 40)), "leg": ramp((22, 22, 12), (150, 140, 92), (72, 68, 40)),
    "beak": ramp((90, 78, 56), (240, 228, 196), (180, 164, 124)), "claw": ramp((90, 78, 56), (240, 228, 196), (180, 164, 124)),
    "eye": [[255, 70, 40]],
    "moss": ramp(*MOSS), "drape": ramp((14, 30, 10), (150, 186, 80), (60, 100, 30)),
    "stem": ramp((120, 108, 86), (250, 242, 224), (206, 194, 168)), "cap": ramp((100, 30, 6), (255, 180, 90), (230, 100, 30)),
    "spot": ramp((200, 190, 170), (255, 252, 240)),
}
# Blackthorn: ink-black vine and leaves with a violet sheen, dark wine jaws, a poison-green throat and lips, a crown
# of black thorns, bone teeth.
INK = ((8, 6, 12), (110, 92, 130), (40, 30, 54))
BLACKTHORN = {
    "vine": ramp(*INK), "leaf": ramp((8, 6, 12), (96, 84, 120), (34, 28, 48)), "rib": ramp((40, 90, 30), (170, 240, 110), (90, 170, 50)),
    "jaw": ramp((22, 4, 12), (150, 50, 86), (70, 14, 36)), "mouth": ramp((30, 110, 10), (236, 255, 150), (130, 230, 40)),
    "lip": ramp((40, 110, 20), (200, 255, 130), (110, 200, 50)), "thorn": ramp((110, 100, 90), (250, 244, 230), (200, 190, 170)),
    "crown": ramp((10, 2, 6), (200, 70, 96), (60, 14, 30)), "barb": ramp((4, 3, 6), (110, 92, 130), (28, 22, 38)),
}
# Prism Shardling: six shards in six hues with pale edges, a white-hot core, a soft pearl glow, white chips.
PRISM_SHARDLING = {
    "core": ramp((200, 190, 170), (255, 255, 255), (255, 250, 236)), "glow": ramp((50, 60, 120), (220, 236, 255), (130, 156, 220)),
    "chip": ramp((150, 150, 170), (255, 255, 255), (226, 230, 240)),
    "red": ramp((70, 6, 16), (255, 170, 160), (220, 40, 50)), "amber": ramp((90, 34, 4), (255, 214, 150), (244, 120, 20)),
    "gold": ramp((96, 76, 6), (255, 250, 170), (240, 210, 40)), "green": ramp((6, 60, 24), (170, 255, 170), (40, 190, 80)),
    "blue": ramp((8, 30, 96), (170, 214, 255), (40, 110, 230)), "violet": ramp((44, 10, 80), (230, 180, 255), (140, 60, 220)),
}
# Granite Warden: warm pink-grey speckled granite, gold trim, ochre lichen, amber eyes, a cracked granite tower shield.
GRANITE = ((40, 32, 34), (236, 214, 204), (140, 120, 118))
GRANITE_DARK = ((28, 22, 24), (176, 156, 150), (96, 82, 82))
GRANITE_WARDEN = {
    **{k: ramp(*GRANITE) for k in ("skin", "hand", "nose", "brow", "hair", "torso", "arm_a", "arm_b", "leg_a", "leg_b",
                                    "boot_a", "boot_b", "helm", "block", "spear")},
    "strand": [[70, 58, 60]] * 8, "sole": [[14, 10, 10]] * 8, "eye": [[255, 196, 70]] * 8, "visor": [[18, 12, 10]] * 8,
    "cuff": ramp(*GRANITE_DARK), "belt": ramp(*GOLD), "buckle": ramp(*GOLD), "crest": ramp(*GOLD), "band": ramp(*GOLD),
    "moss": ramp((70, 46, 10), (236, 190, 90), (170, 120, 40)), "crack": [[22, 16, 16]] * 8,
    "tip": ramp((60, 60, 66), (246, 242, 232), (160, 156, 150)),
    "shield": ramp(*GRANITE_DARK), "rim": ramp(*GOLD),
}
# Old Bristleback (Jay, 2026-11-26: the charcoal ember-crested boar becomes the elite, "just a little more"): the
# approved boar's colours with a hotter crest, yellow-hot coal tips and a brighter eye.
OLD_BRISTLEBACK = {**{k: v for k, v in json.loads((Path(__file__).resolve().parent / "palette.json").read_text(
                        encoding="utf-8"))["ramps"]["boar"].items()},
                   "crest": ramp((70, 10, 6), (255, 150, 60), (214, 56, 16)),
                   "ember": ramp((170, 60, 10), (255, 252, 200), (255, 190, 60)),
                   "eye": [[255, 80, 30]]}
ELITES = {"old_bristleback": OLD_BRISTLEBACK, "granite_warden": GRANITE_WARDEN, "moonhowl": MOONHOWL, "bristleback": BRISTLEBACK, "mossback": MOSSBACK, "blackthorn": BLACKTHORN,
          "prism_shardling": PRISM_SHARDLING}


def main():
    path = Path(__file__).resolve().parent / "palette.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["ramps"].update(BOSSES)
    data["ramps"].update(ELITES)
    path.write_text(json.dumps(data, indent=1) + "\n", encoding="utf-8")
    print("wrote", ", ".join(list(BOSSES) + list(ELITES)), "into", path.name)


if __name__ == "__main__":
    main()
