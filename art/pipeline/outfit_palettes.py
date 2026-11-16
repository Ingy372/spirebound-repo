#!/usr/bin/env python3
"""The four class outfits' palettes, written into palette.json (run after changing a colour here).

  python art/pipeline/outfit_palettes.py

Each colour is a (dark, light, mid) anchor triple turned into an 8-tone ramp by outfit_palette.ramp().
Keeping the anchors here (not hand-edited ramps in palette.json) makes a recolour a one-line change.
"""
from __future__ import annotations

import json
from pathlib import Path

from outfit_palette import base, ramp

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

if __name__ == "__main__":
    path = Path(__file__).resolve().parent / "palette.json"
    data = json.loads(path.read_text())
    data["ramps"].update(OUTFITS)
    path.write_text(json.dumps(data, indent=1))
    print("wrote outfit palettes:", ", ".join(OUTFITS))
