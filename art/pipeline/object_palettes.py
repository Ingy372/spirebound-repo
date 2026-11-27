"""Colours for our own map objects rendered with the creature pipeline (2026-11-27: the Climbers' Monument).

Writes into palette.json like outfit_palettes.py, creature_palettes.py and boss_palettes.py (never hand-edit
palette.json; on a merge conflict take main's copy and rerun all four).
"""
from __future__ import annotations

import json
from pathlib import Path

from outfit_palette import ramp

GRANITE = ((50, 52, 60), (232, 234, 238), (142, 146, 156))
BRONZE = ((60, 34, 10), (255, 214, 130), (178, 118, 46))

OBJECTS = {
    "monument": {
        "plinth": ramp((34, 34, 40), (186, 186, 192), (104, 104, 112)),
        "step": ramp((38, 38, 44), (200, 200, 206), (114, 114, 122)),
        "stone": ramp(*GRANITE),
        "cap": ramp(*BRONZE),
        "plaque": ramp((70, 40, 12), (246, 200, 120), (166, 110, 44)),
        "names": [[44, 24, 8]] * 8,
        "gem": ramp((10, 40, 110), (210, 244, 255), (60, 150, 240)),
    },
}


def main():
    path = Path(__file__).resolve().parent / "palette.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["ramps"].update(OBJECTS)
    path.write_text(json.dumps(data, indent=1) + "\n", encoding="utf-8")
    print("wrote", ", ".join(OBJECTS), "into", path.name)


if __name__ == "__main__":
    main()
