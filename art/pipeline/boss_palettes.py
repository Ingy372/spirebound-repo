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
    "leg_near": ramp((18, 16, 28), (110, 106, 132), (44, 40, 62)), "leg_far": ramp((10, 9, 16), (60, 56, 76), (26, 24, 36)),
    "paw_near": ramp((8, 8, 12), (56, 54, 66), (24, 22, 30)), "paw_far": ramp((5, 5, 8), (30, 28, 36), (14, 13, 18)),
    "tail_tip": ramp((110, 106, 100), (250, 248, 240), (196, 192, 184)),
    "saddle": ramp((12, 11, 20), (84, 80, 104), (34, 32, 48)), "brow": ramp((6, 6, 10), (30, 28, 40)),
    "line": ramp((6, 5, 8), (40, 32, 36)), "stripe": ramp((110, 106, 100), (252, 250, 244), (200, 196, 188)),
    "fang": ramp((120, 104, 70), (255, 250, 228), (214, 200, 160)), "scar": ramp((90, 76, 84), (206, 190, 196), (150, 132, 140)),
}

BOSSES = {"gate_hound": GATE_HOUND, "axe_lord": AXE_LORD, "axe_lord_blade": AXE_LORD_BLADE, "old_tusk": OLD_TUSK,
          "hollowfang": HOLLOWFANG}


def main():
    path = Path(__file__).resolve().parent / "palette.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["ramps"].update(BOSSES)
    path.write_text(json.dumps(data, indent=1) + "\n", encoding="utf-8")
    print("wrote", ", ".join(BOSSES), "into", path.name)


if __name__ == "__main__":
    main()
