"""Bone colours for the skeleton step of our corpses (art/CORPSE_RULES.md C6), written into palette.json.

For every monster with a corpse, a ramp set "<palette>_bones": each part of the living monster becomes old bone
(the Ruin Archer's bone ramp), except parts that are bone or horn already (tusks, horns, teeth, claws keep their
own colours) and eyes and noses, which become dark sockets. Rerun after outfit_palettes.py, creature_palettes.py
and boss_palettes.py (palette.json is generated: never hand-edit it).
"""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ART = HERE.parent
KEEP = ("horn", "tusk", "tooth", "fang", "claw", "spike")
SOCKET = [[34, 26, 20]] * 8

if __name__ == "__main__":
    path = HERE / "palette.json"
    data = json.loads(path.read_text())
    bone = data["ramps"]["archer"]["skin"]
    far = [[max(0, int(c * 0.78)) for c in col] for col in bone]
    bases = sorted({p.stem[len("corpse_"):] for p in (ART / "models").glob("corpse_*.py")
                    if not p.stem.endswith("_bones") and p.stem not in ("corpse_kit",)})
    made = []
    for b in bases:
        src = (ART / "models" / f"{b}.py")
        if not src.exists():
            continue
        pal = next((l.split("=")[1].strip().strip('"\'') for l in src.read_text().splitlines()
                    if l.startswith("PALETTE")), b)
        ramps = data["ramps"].get(pal)
        if not ramps:
            continue
        out = {}
        for part, r in ramps.items():
            if any(k in part for k in KEEP):
                out[part] = r
            elif "eye" in part or part == "nose":
                out[part] = SOCKET
            elif part.endswith("_far"):
                out[part] = far
            else:
                out[part] = bone
        data["ramps"][pal + "_bones"] = out
        made.append(pal + "_bones")
    path.write_text(json.dumps(data, indent=1))
    print("wrote corpse bone palettes:", ", ".join(made))
