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
}

if __name__ == "__main__":
    path = Path(__file__).resolve().parent / "palette.json"
    data = json.loads(path.read_text())
    data["ramps"].update(CREATURES)
    path.write_text(json.dumps(data, indent=1))
    print("wrote creature palettes:", ", ".join(CREATURES))
