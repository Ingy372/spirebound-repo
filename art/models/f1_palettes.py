#!/usr/bin/env python3
"""Palettes for the Floor 1 creatures that wore borrowed Tibia looks until 2026-11-27 (small game, ground-feature
monsters, the Underkeep's Wing 1, the Oathkeeper...). Normal Python:

  python art/models/f1_palettes.py

Like art/pipeline/boss_palettes.py: the anchors live here, so palette.json can always be rebuilt (after a merge
conflict in palette.json: take main's copy, rerun the four pipeline palette scripts, then this one). It only ADDS its
own ramp sets; it never changes another creature's. Each colour is (dark, light, mid) turned into an 8-tone ramp.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

PIPE = Path(__file__).resolve().parent.parent / "pipeline"
sys.path.insert(0, str(PIPE))
from outfit_palette import base, ramp  # noqa: E402

PAL = {}
flat = lambda c: [list(c)] * 8   # noqa: E731

# ---------------------------------------------------------------- small game on the lawns (Q94)
# Meadow Hare: silver-grey with a warm buff wash (Tibia's rabbit is brown), cream belly, black-tipped long ears,
# a white scut, amber eyes.
SILVER = ((34, 34, 42), (222, 216, 202), (128, 122, 116))
PAL["meadow_hare"] = {
    "body": ramp(*SILVER), "head": ramp(*SILVER), "belly": ramp((120, 112, 100), (255, 250, 238), (222, 214, 196)),
    "snout": ramp((110, 102, 92), (250, 244, 230), (206, 196, 180)), "nose": ramp((90, 40, 46), (240, 160, 160)),
    "ear": ramp(*SILVER), "eye": ramp((40, 22, 12), (210, 150, 70), (110, 64, 26)),
    "leg_near": ramp((40, 38, 44), (210, 204, 190), (124, 118, 110)), "leg_far": ramp((30, 28, 34), (160, 154, 144), (92, 88, 82)),
    "paw_near": ramp((110, 104, 96), (250, 246, 236)), "paw_far": ramp((84, 80, 74), (200, 196, 186)),
    "tail_base": ramp((150, 146, 140), (255, 255, 255)), "tail_tip": ramp((170, 166, 160), (255, 255, 255)),
    "eartip": ramp((6, 6, 8), (64, 60, 62), (24, 22, 24)), "inner": ramp((120, 70, 70), (250, 196, 190), (210, 140, 136)),
    "buff": ramp((54, 46, 38), (232, 212, 180), (150, 134, 110)), "line": flat((20, 18, 20)),
    "hindfoot": ramp((60, 56, 54), (236, 230, 216), (150, 144, 134)),
}

# Dapple Fawn: cool dun-taupe (Tibia's deer is red-brown), a dark stripe down the spine with rows of bright cream
# dapples either side, cream belly and throat, dark-rimmed big ears, a black nose, dark brown eyes.
DUN = ((36, 28, 28), (190, 160, 128), (112, 88, 72))
PAL["dapple_fawn"] = {
    "body": ramp(*DUN), "head": ramp(*DUN), "belly": ramp((120, 110, 96), (255, 248, 230), (222, 210, 186)),
    "snout": ramp((60, 50, 44), (220, 204, 176), (140, 122, 104)), "nose": flat((16, 14, 16)),
    "ear": ramp(*DUN), "eye": ramp((10, 8, 8), (120, 80, 50), (40, 26, 20)),
    "leg_near": ramp((36, 30, 30), (196, 174, 146), (110, 92, 78)), "leg_far": ramp((26, 22, 22), (150, 132, 110), (80, 66, 56)),
    "paw_near": flat((22, 18, 18)), "paw_far": flat((16, 14, 14)),
    "tail_base": ramp(*DUN), "tail_tip": ramp((170, 160, 146), (255, 252, 244)),
    "spot": ramp((170, 156, 130), (255, 252, 236), (240, 230, 206)), "stripe": ramp((20, 16, 18), (110, 88, 74), (56, 44, 40)),
    "rim": ramp((14, 12, 12), (80, 66, 60), (36, 30, 28)), "inner": ramp((120, 96, 90), (246, 222, 210), (200, 170, 160)),
    "line": flat((24, 18, 18)),
}

# Thistle Hen: slate-blue plumage freckled with white (Tibia's chicken is white with a red comb), a rust breast, a
# spiky thistle-purple crest with lilac tips, a bronze-black tail, horn beak, orange legs.
SLATE_HEN = ((22, 26, 38), (164, 176, 196), (70, 80, 102))
PAL["thistle_hen"] = {
    "body": ramp(*SLATE_HEN), "head": ramp((20, 22, 32), (140, 150, 170), (60, 66, 86)),
    "breast": ramp((60, 20, 12), (236, 150, 96), (164, 74, 40)), "wing": ramp((18, 22, 32), (140, 150, 170), (56, 64, 84)),
    "tail": ramp((10, 10, 12), (150, 120, 70), (40, 34, 28)), "crest": ramp((40, 10, 50), (230, 150, 240), (130, 50, 150)),
    "crestip": ramp((150, 100, 170), (255, 230, 255), (220, 180, 240)), "beak": ramp((110, 90, 50), (255, 240, 190), (220, 190, 120)),
    "wattle": ramp((90, 20, 50), (240, 110, 150), (180, 50, 90)), "eye": flat((250, 190, 60)),
    "leg": ramp((110, 50, 10), (255, 190, 90), (220, 120, 40)), "foot": ramp((110, 50, 10), (255, 190, 90), (220, 120, 40)),
    "speck": ramp((180, 186, 196), (255, 255, 255)), "line": flat((14, 14, 22)),
}

# Acorn Squirrel: dusky ash-grey (Tibia's squirrel is red-brown with a pale tail), a cream belly, a huge charcoal brush
# of a tail frosted russet at the end, russet ear tufts, a golden acorn with a dark cap in its mouth.
ASH_SQ = ((30, 30, 40), (200, 196, 196), (96, 96, 108))
PAL["acorn_squirrel"] = {
    "body": ramp(*ASH_SQ), "head": ramp(*ASH_SQ), "belly": ramp((120, 110, 96), (255, 248, 230), (220, 206, 180)),
    "snout": ramp((80, 74, 70), (236, 228, 214), (160, 150, 140)), "nose": flat((30, 20, 22)),
    "ear": ramp(*ASH_SQ), "eye": ramp((6, 6, 8), (90, 80, 80), (24, 22, 24)),
    "leg_near": ramp((30, 28, 30), (170, 162, 154), (90, 86, 84)), "leg_far": ramp((22, 20, 22), (130, 124, 118), (66, 62, 62)),
    "paw_near": ramp((60, 56, 52), (210, 200, 186)), "paw_far": ramp((44, 40, 38), (160, 152, 140)),
    "tail_base": ramp((10, 10, 16), (130, 124, 136), (44, 42, 52)), "tail_tip": ramp((60, 26, 14), (236, 176, 120), (150, 76, 40)),
    "tuft": ramp((60, 20, 8), (240, 150, 90), (170, 70, 30)), "acorn": ramp((90, 50, 10), (255, 214, 120), (200, 140, 50)),
    "cap": ramp((24, 16, 10), (130, 96, 60), (66, 46, 28)), "stripe": ramp((70, 30, 14), (230, 160, 100), (150, 80, 40)),
    "line": flat((20, 16, 18)),
}

# ---------------------------------------------------------------- ground-feature monsters (FD2)
# Nest Queen: the meadow wasps' mother: a long honey-gold abdomen with burgundy-black bands (her wasps are amber and
# blue-black; Tibia's are lemon and brown), a russet fuzzy thorax, an ivory crown of horn spikes, ember eyes, smoky
# amber wings torn ragged, a glowing amber venom drop.
PAL["nest_queen"] = {
    "thorax": ramp((40, 14, 8), (230, 150, 80), (140, 64, 30)), "abdomen": ramp((90, 46, 6), (255, 226, 120), (214, 150, 30)),
    "stripe": ramp((16, 4, 10), (120, 50, 70), (52, 14, 30)), "head": ramp((16, 4, 10), (120, 50, 70), (52, 14, 30)),
    "face": ramp((90, 60, 20), (255, 230, 150), (200, 160, 80)), "eye": ramp((120, 10, 6), (255, 160, 90), (230, 60, 30)),
    "stinger": ramp((10, 4, 8), (90, 50, 60), (36, 16, 24)), "wing": ramp((90, 70, 50), (226, 206, 170), (170, 146, 110)),
    "leg": ramp((14, 6, 10), (100, 60, 64), (40, 20, 28)), "antenna": flat((26, 10, 18)), "vein": flat((50, 30, 26)),
    "waist": ramp((16, 4, 10), (120, 50, 70), (52, 14, 30)), "crown": ramp((120, 100, 60), (255, 250, 220), (230, 214, 160)),
    "venom": ramp((180, 100, 10), (255, 250, 170), (255, 200, 60)),
}

# Elder Sproutling: a sproutling grown old: a sage-olive bulb face on a grey-brown bark trunk, a crown of deep emerald
# leaves (bluer and darker than the meadow grass) with pale-pink blossoms, mossy patches, amber eyes under bark brows.
PAL["elder_sproutling"] = {
    "bulb": ramp((22, 34, 20), (186, 200, 132), (92, 114, 62)), "bark": ramp((24, 18, 14), (176, 150, 120), (92, 74, 56)),
    "ridge": flat((20, 14, 10)), "eye": ramp((140, 70, 0), (255, 230, 120), (250, 170, 30)), "brow": ramp((20, 14, 10), (120, 96, 70), (60, 46, 32)),
    "mouth": flat((16, 10, 8)), "leaf": ramp((4, 24, 20), (96, 170, 112), (24, 92, 62)), "vein": flat((150, 214, 150)),
    "twig": ramp((24, 18, 14), (160, 132, 100), (84, 64, 46)), "root": ramp((22, 16, 12), (150, 120, 90), (76, 58, 40)),
    "moss": ramp((20, 44, 18), (130, 176, 80), (60, 104, 40)), "blossom": ramp((170, 100, 120), (255, 236, 240), (240, 180, 196)),
}


def main():
    path = PIPE / "palette.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["ramps"].update(PAL)
    path.write_bytes((json.dumps(data, indent=1) + "\n").encode("utf-8"))
    print("wrote", ", ".join(PAL), "into", path.name)


if __name__ == "__main__":
    main()
