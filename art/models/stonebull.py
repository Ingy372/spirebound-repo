"""Stonehide Bull (Floor 2, the Highrest labyrinth): a variant of the Herd Bull (bull.py) with a hide of stone.

It wore the thornsnap's sprite (ART_COUNT.md: wrong animal).
  Coat:      slate-grey hide fading to dark at the legs, the mane replaced by rough rock slabs.
  Signature: jagged stone plates standing up along the hump and back, patches of moss on them, the same wide pale
             horns as the herd bull (so players read it as its tougher cousin).
  Attitude:  the herd bull's charge, heavier.
"""
from __future__ import annotations

from mathutils import Euler, Vector

import bull as B
from bull import (WALK_FRAMES, HEIGHT_SHEAR, LEAN, REFERENCE, GROUND_STRETCH, AUTO_PLACE, SPEC,  # noqa: F401
                  assign_depth_parts)

NAME = "stonebull"
PALETTE = "stonebull"
SIZE = 2.0
SIGNATURE = ["horn", "plate"]
CHECK = {"size": (0.95, 1.65), "eye": 1}   # an elite bull is meant to be big
PARTS = B.PARTS + ["plate", "moss"]
PIXEL_RULES = {**B.PIXEL_RULES,
               "weight": {**B.PIXEL_RULES["weight"], "plate": 2.0, "moss": 2.4},
               "thin": {**B.PIXEL_RULES["thin"], "moss": 2},
               "soft": B.PIXEL_RULES["soft"] + [["plate", "moss"]],
               "texture": {**B.PIXEL_RULES["texture"], "plate": [1.2, 0.5]}}
PLATES = [(0.10, 0.00, 0.17, 0.0), (0.03, 0.03, 0.18, 0.3), (-0.04, -0.03, 0.16, -0.3), (-0.11, 0.02, 0.13, 0.2),
          (-0.18, -0.01, 0.10, -0.2)]


def build(model_cls, facing):
    m = B.build(model_cls, facing)
    m.parts = PARTS                      # the base parts first, so their numbers do not change
    for i in range(len(PLATES)):
        m.box(f"plate{i}", "plate", size=(0.070, 0.040, 0.080))
    for i in range(3):
        m.ellipsoid(f"moss{i}", "moss", radii=(0.030, 0.026, 0.014), segments=8, rings=5)
    return m


def pose(m, t):
    B.pose(m, t)
    chest = m.objects["hump"].location - Vector((0.010, 0, 0.100))
    for i, (x, y, z, r) in enumerate(PLATES):
        o = m.objects[f"plate{i}"]
        o.rotation_mode = "XYZ"
        o.rotation_euler = Euler((r, -0.25, r * 0.5))
        o.location = chest + Vector((x, y, z))
    for i, j in enumerate((0, 2, 3)):
        x, y, z, _r = PLATES[j]
        m.objects[f"moss{i}"].location = chest + Vector((x - 0.010, y + 0.016, z + 0.040))
