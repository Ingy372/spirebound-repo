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

BOSSES = {"gate_hound": GATE_HOUND}


def main():
    path = Path(__file__).resolve().parent / "palette.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["ramps"].update(BOSSES)
    path.write_text(json.dumps(data, indent=1) + "\n", encoding="utf-8")
    print("wrote", ", ".join(BOSSES), "into", path.name)


if __name__ == "__main__":
    main()
