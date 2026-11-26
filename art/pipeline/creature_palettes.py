#!/usr/bin/env python3
"""Palettes for creatures made in the wrong-animal cleanup (Jay, 2026-11-25: "clean it up"), written into palette.json.

  python art/pipeline/creature_palettes.py

Like outfit_palettes.py and boss_palettes.py: the anchors live here, so palette.json can always be rebuilt
(after a merge conflict in palette.json: take main's copy, then rerun the three palette scripts).
Each colour is (dark, light, mid) turned into an 8-tone ramp.
"""
from __future__ import annotations

import json
from pathlib import Path

from outfit_palette import ramp

CREATURES = {
    # Black Crawler: glossy blue-black cave beetle, amber inner mandibles, blood-red eyes, pale seam and rim
    "crawler": {
        "shell": ramp((4, 6, 12), (118, 138, 180), (18, 24, 42)), "pronotum": ramp((4, 5, 10), (96, 112, 146), (16, 20, 34)),
        "head": ramp((6, 6, 10), (100, 104, 120), (20, 22, 30)), "eye": [[220, 30, 24]] * 8,
        "mandible": ramp((10, 10, 14), (140, 140, 150), (40, 40, 48)), "inner": ramp((120, 60, 10), (255, 210, 100), (230, 150, 40)),
        "leg": ramp((6, 6, 10), (96, 100, 116), (22, 24, 32)), "antenna": [[30, 32, 40]] * 8,
        "seam": ramp((90, 110, 150), (220, 232, 250)), "rim": ramp((60, 76, 110), (180, 196, 226)), "pit": [[8, 10, 18]] * 8,
    },
    # Blight Wasp: the meadow wasp gone sick: olive and bruise-purple bands, glowing pustules, sick-yellow eyes
    "blightwasp": {
        "thorax": ramp((30, 34, 14), (190, 196, 110), (100, 108, 44)), "abdomen": ramp((26, 30, 10), (180, 190, 90), (96, 104, 36)),
        "stripe": ramp((24, 10, 30), (160, 110, 170), (70, 40, 84)), "head": ramp((20, 22, 12), (150, 156, 90), (70, 76, 36)),
        "face": ramp((30, 30, 14), (200, 200, 120)), "eye": [[230, 230, 90]] * 8, "stinger": ramp((14, 10, 18), (120, 100, 130)),
        "wing": ramp((90, 100, 90), (200, 210, 196), (150, 160, 146)), "leg": ramp((14, 12, 10), (110, 106, 90)),
        "antenna": [[30, 30, 20]] * 8, "vein": [[60, 64, 50]] * 8, "waist": ramp((20, 20, 10), (120, 120, 60)),
        "pustule": ramp((90, 140, 20), (240, 255, 140), (190, 230, 60)), "venom": [[170, 255, 90]] * 8,
    },
    # Ridge Cat: dusty slate-tawny mountain cat, dark spots, cream muzzle and belly, black ear tufts, ringed tail
    "ridgecat": {
        "body": ramp((30, 30, 34), (190, 176, 150), (100, 94, 84)), "belly": ramp((110, 96, 78), (252, 244, 226), (210, 196, 170)),
        "head": ramp((30, 30, 34), (196, 182, 156), (104, 98, 88)), "snout": ramp((110, 96, 78), (252, 244, 226), (210, 196, 170)),
        "nose": ramp((40, 20, 20), (180, 110, 100)), "ear": ramp((40, 32, 26), (200, 176, 140), (120, 100, 78)),
        "eye": [[240, 180, 40]] * 8, "leg_near": ramp((40, 32, 26), (200, 176, 140), (120, 100, 78)),
        "leg_far": ramp((30, 24, 20), (170, 146, 116), (96, 80, 62)), "paw_near": ramp((40, 32, 26), (200, 176, 140), (120, 100, 78)),
        "paw_far": ramp((30, 24, 20), (170, 146, 116), (96, 80, 62)), "tail_base": ramp((30, 30, 34), (190, 176, 150), (100, 94, 84)),
        "tail_tip": ramp((8, 8, 10), (60, 56, 56), (24, 22, 22)), "spot": ramp((14, 12, 12), (80, 70, 60), (36, 30, 26)),
        "pad": ramp((120, 106, 88), (255, 250, 236)), "eartuft": [[12, 10, 10]] * 8, "ring": ramp((14, 12, 12), (80, 70, 60)),
        "brow": [[30, 24, 20]] * 8,
    },
    # Herd Bull: shaggy russet-black, tawny mane on the hump, pale sideways horns, pale lower legs
    "bull": {
        "body": ramp((14, 8, 6), (150, 90, 60), (60, 32, 20)), "belly": ramp((20, 12, 8), (130, 84, 60), (60, 36, 24)),
        "head": ramp((12, 8, 6), (140, 84, 56), (54, 30, 18)), "snout": ramp((40, 30, 26), (200, 170, 150), (110, 84, 70)),
        "nose": ramp((20, 14, 12), (110, 80, 70)), "ear": ramp((14, 8, 6), (130, 80, 54), (54, 30, 18)), "eye": [[30, 14, 10]] * 8,
        "leg_near": ramp((40, 30, 22), (220, 196, 160), (130, 104, 80)), "leg_far": ramp((30, 22, 16), (180, 156, 124), (100, 80, 60)),
        "paw_near": ramp((10, 8, 8), (90, 80, 76)), "paw_far": ramp((8, 6, 6), (70, 62, 58)),
        "tail_base": ramp((14, 8, 6), (150, 90, 60), (60, 32, 20)), "tail_tip": ramp((10, 6, 4), (90, 60, 40)),
        "horn": ramp((120, 110, 90), (255, 250, 236), (220, 208, 180)), "mane": ramp((60, 34, 14), (240, 190, 120), (170, 110, 56)),
        "hump": ramp((14, 8, 6), (150, 90, 60), (60, 32, 20)), "brow": [[10, 6, 4]] * 8, "hoof": ramp((10, 8, 8), (90, 80, 76)),
    },
}
# Stonehide Bull: the herd bull's body in slate grey, rock plates and moss instead of the mane
CREATURES["stonebull"] = {**CREATURES["bull"],
    "body": ramp((20, 22, 26), (170, 170, 168), (80, 82, 86)), "belly": ramp((16, 18, 20), (140, 140, 140), (66, 68, 70)),
    "head": ramp((18, 20, 24), (160, 160, 158), (74, 76, 80)), "hump": ramp((20, 22, 26), (170, 170, 168), (80, 82, 86)),
    "tail_base": ramp((20, 22, 26), (170, 170, 168), (80, 82, 86)), "ear": ramp((18, 20, 24), (150, 150, 150), (70, 72, 76)),
    "leg_near": ramp((14, 14, 16), (120, 120, 120), (50, 52, 54)), "leg_far": ramp((10, 10, 12), (100, 100, 100), (40, 42, 44)),
    "mane": ramp((30, 30, 32), (190, 186, 176), (110, 108, 104)), "plate": ramp((40, 40, 44), (226, 220, 204), (130, 126, 118)),
    "moss": ramp((14, 34, 12), (140, 186, 80), (60, 104, 36))}
# Horned Grazer: sandy-fawn antelope, dark flank band, white belly and rump, dark ridged lyre horns
FAWN = ((50, 34, 18), (240, 210, 150), (176, 136, 80))
CREATURES["grazer"] = {
    "body": ramp(*FAWN), "belly": ramp((140, 130, 116), (255, 252, 244), (226, 220, 206)), "head": ramp(*FAWN),
    "snout": ramp((60, 44, 28), (220, 196, 150), (150, 116, 74)), "nose": [[24, 18, 16]] * 8,
    "ear": ramp(*FAWN), "eye": [[24, 16, 12]] * 8, "leg_near": ramp((30, 22, 16), (170, 140, 100), (90, 70, 46)),
    "leg_far": ramp((24, 18, 12), (140, 114, 80), (70, 54, 36)), "paw_near": [[20, 16, 14]] * 8, "paw_far": [[16, 12, 10]] * 8,
    "tail_base": ramp(*FAWN), "tail_tip": [[16, 12, 10]] * 8, "horn": ramp((20, 16, 14), (170, 160, 146), (70, 62, 56)),
    "ridge": ramp((120, 110, 96), (240, 232, 214)), "band": ramp((30, 20, 12), (120, 86, 50), (64, 44, 24)),
    "rump": ramp((140, 130, 116), (255, 252, 244), (226, 220, 206)), "ring": [[250, 246, 236]] * 8,
}
# Dust Strider: sand-ochre lizard, dark back bands, rust-red spines, pale throat
SAND = ((60, 44, 20), (240, 214, 150), (180, 144, 80))
CREATURES["strider"] = {
    "body": ramp(*SAND), "belly": ramp((140, 126, 100), (255, 248, 226), (222, 210, 180)), "head": ramp(*SAND),
    "snout": ramp(*SAND), "nose": [[40, 30, 20]] * 8, "ear": ramp(*SAND), "eye": [[240, 210, 40]] * 8,
    "leg_near": ramp((50, 36, 18), (220, 190, 130), (150, 116, 64)), "leg_far": ramp((40, 28, 14), (180, 150, 100), (110, 84, 44)),
    "paw_near": ramp((30, 22, 12), (140, 110, 70)), "paw_far": ramp((24, 18, 10), (110, 86, 54)),
    "tail_base": ramp(*SAND), "tail_tip": ramp((50, 36, 18), (200, 170, 110)),
    "spine": ramp((80, 20, 10), (240, 120, 70), (180, 60, 30)), "bandtail": ramp((30, 20, 10), (120, 86, 50), (60, 40, 22)),
    "stripe": ramp((30, 20, 10), (120, 86, 50), (60, 40, 22)), "line": [[40, 26, 14]] * 8, "brow": [[50, 34, 18]] * 8,
    "pouch": ramp((140, 126, 100), (255, 248, 226), (222, 210, 180)),
}

if __name__ == "__main__":
    path = Path(__file__).resolve().parent / "palette.json"
    data = json.loads(path.read_text())
    data["ramps"].update(CREATURES)
    path.write_text(json.dumps(data, indent=1))
    print("wrote creature palettes:", ", ".join(CREATURES))
