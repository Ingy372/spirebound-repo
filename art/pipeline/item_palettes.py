"""Colours for item icons rendered with the creature pipeline (2026-11-27, art/ITEM_RULES.md).

Writes into palette.json like outfit_palettes.py, creature_palettes.py, boss_palettes.py and object_palettes.py
(never hand-edit palette.json; on a merge conflict take main's copy and rerun all five).
Each ramp is 8 tones, dark -> light (item_kit.BANDS picks the tone from the light).
"""
from __future__ import annotations

import json
from pathlib import Path

from outfit_palette import ramp

# shared materials: (dark, light, mid)
STEEL = ((34, 40, 52), (246, 250, 255), (128, 140, 158))
BRONZE = ((52, 30, 10), (255, 226, 150), (176, 120, 48))
GOLD = ((70, 38, 6), (255, 246, 170), (214, 156, 34))
BRASS = ((60, 36, 8), (255, 240, 170), (196, 146, 46))
PEWTER = ((36, 40, 46), (236, 240, 244), (130, 138, 148))
IRON = ((22, 24, 30), (180, 186, 196), (82, 88, 100))
LEATHER = ((40, 20, 10), (222, 160, 104), (128, 74, 40))
DARK_LEATHER = ((26, 14, 8), (176, 116, 70), (92, 52, 28))
WOOD = ((40, 22, 10), (214, 160, 102), (120, 76, 40))
BARK = ((30, 20, 12), (168, 128, 90), (90, 62, 38))
BIRCH = ((70, 66, 60), (255, 252, 240), (200, 196, 184))
LEAF = ((14, 42, 14), (190, 240, 120), (70, 150, 50))
PAPER = ((90, 62, 30), (255, 244, 206), (210, 180, 120))
STONE = ((40, 40, 46), (214, 214, 220), (120, 120, 128))
RED_GEM = ((60, 0, 6), (255, 190, 170), (210, 30, 30))
BLUE_GEM = ((6, 20, 80), (210, 240, 255), (40, 110, 230))
GREEN_GLASS = ((6, 40, 16), (200, 255, 190), (40, 150, 60))
EMBER = ((90, 16, 0), (255, 250, 190), (255, 130, 20))
CORK = ((60, 36, 16), (226, 186, 132), (150, 104, 60))
FOAM = ((150, 146, 136), (255, 255, 252), (230, 228, 220))
GLOW_WHITE = ((120, 150, 110), (255, 255, 250), (220, 245, 210))
GLOW_GOLD = ((140, 70, 0), (255, 255, 220), (255, 200, 70))

r = lambda t: ramp(*t)
flat = lambda c: [list(c)] * 8

ITEMS = {
    "item_briarguard_sabre": {
        "blade": r(((34, 10, 6), (214, 120, 84), (104, 34, 22))),         # a deep red-brown thorn
        "edge": r(((90, 110, 80), (250, 255, 230), (190, 214, 170))),     # its pale honed edge
        "grip": r(((22, 14, 8), (150, 112, 74), (70, 46, 26))), "coil": r(((20, 50, 18), (170, 220, 110), (70, 130, 46))),
        "leaf": r(LEAF), "quillon": r(((60, 30, 18), (240, 200, 160), (150, 90, 60))), "hip": r(RED_GEM),
        "hiptip": flat((40, 16, 10)),
    },
    "item_copsewood_bow": {
        "limb": r(BIRCH), "knot": r(((30, 24, 20), (110, 96, 80), (60, 50, 40))), "burl": r(BARK),
        "string": r(((20, 70, 20), (200, 250, 150), (90, 170, 60))), "leaf": r(LEAF), "twig": r(BIRCH),
    },
    "item_wand_of_ember_script": {
        "paper": r(PAPER), "script": r(EMBER), "band": r(BRASS), "curl": r(PAPER),
        "burn": r(((150, 30, 0), (255, 236, 120), (255, 120, 20))), "spark": r(((255, 140, 30), (255, 255, 220), (255, 220, 120))),
    },
    "item_thornward_rod": {
        "shaft": r(WOOD), "vine": r(LEAF), "leaf": r(LEAF), "pod": r(GLOW_GOLD),
        "rib": r(((140, 80, 10), (255, 230, 150), (220, 160, 50))), "tendril": r(LEAF),
        "thorn": r(((60, 50, 30), (230, 220, 180), (150, 130, 90))),
    },
    "item_brass_spyglass": {
        "tube": r(BRASS), "ring": r(((80, 46, 10), (255, 250, 200), (224, 176, 70))), "leather": r(DARK_LEATHER),
        "stitch": r(((120, 90, 50), (240, 220, 170), (200, 170, 120))), "lens": r(((40, 80, 120), (230, 250, 255), (130, 190, 230))),
        "glint": flat((255, 255, 255)), "eyecup": r(((14, 12, 10), (110, 90, 70), (48, 38, 30))),
    },
    "item_millrace_boots": {
        "leather": r(((50, 24, 10), (232, 170, 104), (140, 82, 40))), "cuff": r(((14, 40, 80), (170, 220, 255), (50, 120, 200))),
        "sole": r(((18, 12, 10), (110, 84, 64), (50, 36, 28))), "strap": r(DARK_LEATHER), "buckle": r(BRASS),
        "toecap": r(((46, 22, 8), (220, 156, 94), (128, 74, 36))), "inside": flat((30, 16, 8)),
        "rim": r(((22, 14, 8), (130, 92, 56), (60, 40, 22))), "paddle": r(((40, 70, 90), (220, 240, 250), (120, 160, 186))), "hub": r(BRASS),
    },
    "item_shrinekeepers_pendant": {
        "wall": r(((60, 58, 56), (250, 246, 236), (176, 170, 160))), "roof": r(((20, 24, 34), (150, 160, 180), (60, 68, 86))),
        "ridge": r(GOLD), "door": r(((20, 18, 20), (90, 84, 80), (44, 40, 40))), "glow": r(GLOW_GOLD),
        "cord": r(((70, 0, 6), (250, 150, 130), (190, 30, 30))), "bead": r(GOLD), "step": r(STONE),
    },
    "item_wardens_signet": {
        "band": r(((28, 30, 38), (226, 232, 242), (112, 118, 134))), "key": r(GOLD), "bow": r(GOLD), "stone": r(BLUE_GEM), "glint": flat((255, 255, 255)),
    },
    "item_inn_tankard": {
        "body": r(PEWTER), "bandring": r(((30, 34, 40), (200, 206, 214), (100, 108, 118))), "handle": r(PEWTER),
        "foam": r(FOAM), "beer": r(((90, 40, 4), (255, 210, 110), (210, 130, 30))),
        "mark": r(((24, 26, 30), (90, 96, 104), (50, 54, 60))),
    },
    "item_plains_map": {
        "paper": r(PAPER), "roll": r(((100, 70, 34), (255, 240, 200), (214, 182, 124))),
        "plains": r(((40, 90, 30), (190, 230, 120), (110, 170, 70))), "road": r(((80, 50, 20), (160, 110, 60), (120, 80, 40))),
        "tower": r(((50, 50, 56), (200, 200, 206), (120, 120, 128))), "ribbon": r(RED_GEM), "mark": r(((120, 0, 0), (255, 80, 60), (200, 20, 20))),
    },
    "item_message_bottle": {
        "glass": r(GREEN_GLASS), "letter": r(((70, 110, 60), (240, 255, 220), (170, 210, 150))), "shine": flat((236, 255, 230)),
        "cork": r(CORK), "seal": r(RED_GEM), "twine": r(((90, 70, 40), (230, 210, 160), (170, 140, 90))),
    },
}


def main():
    path = Path(__file__).resolve().parent / "palette.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["ramps"].update(ITEMS)
    path.write_text(json.dumps(data, indent=1) + "\n", encoding="utf-8")
    print("wrote", ", ".join(ITEMS), "into", path.name)


if __name__ == "__main__":
    main()
