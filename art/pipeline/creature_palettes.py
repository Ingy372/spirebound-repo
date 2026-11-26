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
}

if __name__ == "__main__":
    path = Path(__file__).resolve().parent / "palette.json"
    data = json.loads(path.read_text())
    data["ramps"].update(CREATURES)
    path.write_text(json.dumps(data, indent=1))
    print("wrote creature palettes:", ", ".join(CREATURES))
