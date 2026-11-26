"""Vanguard addon 2: the Knight's Mantle (an overlay on the approved Vanguard, which stays frozen).

  Addon:   a long royal-blue mantle to the calves with a gold hem, fastened by a pale fur collar over the shoulders.
  Details: fur collar with drawn tufts, gold hem (a line, O7), two gold clasps at the collar, a darker lining edge.
  The base's short cape still shows under it; the mantle hangs behind and a little wider (O8: tall things behind).
"""
from __future__ import annotations

import math

from mathutils import Euler, Vector

import vanguard as V
from vanguard import WALK_FRAMES, PALETTE, REFERENCE, PROJECTION, CANVAS_OFFSET, SPEC, assign_depth_parts  # noqa: F401

NAME = "vanguard_a2"
BASE = "vanguard"
# literal values: check_creature.py reads these lines without importing the model
SIGNATURE = ["mantle", "fur"]                 # the addon itself must show
HEAD_PARTS = ["skin", "hair", "strand", "eye", "brow", "nose"]
LEG_PARTS = ["leg_a", "leg_b", "boot_a", "boot_b", "knee"]
CHECK = {"size": (0.85, 1.45), "head": 0.08, "legs_side": 0.05, "eye": 1}
PARTS = V.PARTS + ["mantle", "fur", "tuft"]
PIXEL_RULES = {**V.PIXEL_RULES,
               "weight": {**V.PIXEL_RULES["weight"], "fur": 1.8, "tuft": 2.6},
               "thin": {**V.PIXEL_RULES["thin"], "tuft": 2},
               "soft": V.PIXEL_RULES["soft"] + [["mantle", "trim"], ["fur", "tuft"]],
               "texture": {**V.PIXEL_RULES["texture"], "mantle": [0.4, 0.2], "fur": [0.6, 0.3]},
               "selout": V.PIXEL_RULES["selout"] + ["mantle", "fur"]}


def build(model_cls, facing):
    m = V.build(model_cls, facing)
    m.parts = PARTS                      # the base parts first, so their numbers do not change
    m.box("mantle", "mantle", size=(0.024, 0.260, 0.540))
    m.box("mantle_hem", "trim", size=(0.028, 0.268, 0.030))
    m.ellipsoid("fur", "fur", radii=(0.120, 0.190, 0.050), segments=18, rings=8)
    for i in range(5):
        m.ellipsoid(f"tuft{i}", "tuft", radii=(0.020, 0.020, 0.016), segments=6, rings=4)
    for k in ("l", "r"):
        m.ellipsoid(f"clasp_{k}", "trim", radii=(0.018, 0.018, 0.018), segments=8, rings=6)
    return m


def pose(m, t):
    V.pose(m, t)
    up = m.objects["torso"].location - Vector((0, 0, m.spec["torso_z"]))
    walking = t is not None
    a = 0.0 if t is None else 2 * math.pi * t
    tilt = 0.16 + (0.10 * abs(math.sin(a)) if walking else 0.0)      # swings out behind with the stride
    for name, z in (("mantle", 0.555), ("mantle_hem", 0.295)):
        o = m.objects[name]
        o.rotation_mode = "XYZ"
        o.rotation_euler = Euler((0.0, tilt, 0.0))
        o.location = Vector((-0.165 - (0.825 - z) * math.sin(tilt) * 0.6, 0, z)) + up
    m.objects["fur"].location = Vector((-0.020, 0, 0.880)) + up
    for i in range(5):
        ang = -1.2 + 0.6 * i
        m.objects[f"tuft{i}"].location = Vector((-0.020 + 0.115 * math.cos(ang), 0.180 * math.sin(ang), 0.905)) + up
    for sign, k in ((1, "l"), (-1, "r")):
        m.objects[f"clasp_{k}"].location = Vector((0.100, 0.060 * sign, 0.868)) + up
