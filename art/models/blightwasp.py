"""Blight Wasp (Floor 2, Highrest Highlands): the approved Meadow Wasp (frozen) gone sick, a creature of its own.

It wore the rat's sprite (ART_COUNT.md: wrong animal). It "spits blight from range" (gen_monsters.py), so:
  Coat:      sickly olive and bruise-purple bands instead of the wasp's amber and blue-black, grey-green wings.
  Signature: glowing yellow-green pustules swelling on the abdomen and a drop of venom hanging from the stinger,
             pale sick-yellow eyes (the meadow wasp's are ember red).
  Attitude:  the same hunting hover as the meadow wasp, so a player who knows one reads the other as its cousin.
Same body and hover as art/models/wasp.py (untouched); this file adds the pustules and the venom drop.
"""
from __future__ import annotations

from mathutils import Vector

import wasp as B
from wasp import (WALK_FRAMES, HEIGHT_SHEAR, LEAN, SIZE, GROUND_STRETCH, AUTO_PLACE,  # noqa: F401
                  assign_depth_parts)

NAME = "blightwasp"
PALETTE = "blightwasp"
REFERENCE = "look_44.png"
# literal values: check_creature.py reads these lines without importing the model
SIGNATURE = ["eye", "pustule"]
HEAD_PARTS = ["head", "face", "eye"]
LEG_PARTS = ["leg"]
CHECK = {"size": (0.85, 1.75), "legs_side": 0.02, "legs_updown": 0.0, "head": 0.07}
PARTS = B.PARTS + ["pustule", "venom"]
PIXEL_RULES = {**B.PIXEL_RULES,
               "weight": {**B.PIXEL_RULES["weight"], "pustule": 4.0, "venom": 5.0},
               "thin": {**B.PIXEL_RULES["thin"], "pustule": 2, "venom": 2},
               "no_outline": B.PIXEL_RULES["no_outline"] + ["venom"]}


def build(model_cls, facing):
    m = B.build(model_cls, facing)
    m.parts = PARTS                      # the base parts first, so their numbers do not change
    for i in range(4):
        m.ellipsoid(f"pustule{i}", "pustule", radii=(0.022, 0.022, 0.020), segments=8, rings=6)
    m.ellipsoid("venom", "venom", radii=(0.016, 0.016, 0.022), segments=8, rings=6)
    return m


def pose(m, t):
    B.pose(m, t)
    for i, (seg, dy, dz) in enumerate(((1, 0.040, 0.050), (2, -0.045, 0.055), (3, 0.030, 0.052), (4, -0.020, 0.045))):
        c = m.objects[f"seg{seg}"]
        m.objects[f"pustule{i}"].location = c.location + Vector((0.0, dy, dz))
    seg = m.objects[f"seg{B.SEGS - 1}"].location          # the stinger runs from the last band down and back
    m.objects["venom"].location = seg + Vector((-0.090, 0, -0.110))
