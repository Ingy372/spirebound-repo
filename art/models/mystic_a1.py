"""Mystic addon 1: the Antler Crown (overlay on the approved Mystic, which stays frozen; rules A1-A7).

  Addon:   two short branching antlers rising from her leaf circlet, back and outward, with small leaves sprouting
           at the tips (O8: tall things go behind the head).
  Details: two-tined antlers (a main beam and a tine each), pale tips, three leaves, a knot where each meets the circlet.
"""
from __future__ import annotations

import math

from mathutils import Vector

import addon_kit as K
import mystic as B
from mystic import WALK_FRAMES, PALETTE, REFERENCE, PROJECTION, CANVAS_OFFSET, SPEC, assign_depth_parts  # noqa: F401

NAME = "mystic_a1"
BASE = "mystic"
# literal values: check_creature.py reads these lines without importing the model
SIGNATURE = ["antler"]                  # the addon itself must show
HEAD_PARTS = ["skin", "hair", "strand", "eye", "brow", "nose", "circlet", "antler", "sprout"]
LEG_PARTS = ["boot_a", "boot_b", "sole"]
CHECK = {"size": (0.85, 1.55), "head": 0.08, "legs_side": 0.0, "legs_updown": 0.0, "eye": 1}
PARTS = B.PARTS + ["antler", "tip", "sprout"]
PIXEL_RULES = {**B.PIXEL_RULES,
               "weight": {**B.PIXEL_RULES["weight"], "antler": 2.6, "tip": 4.0, "sprout": 2.4},
               "thin": {**B.PIXEL_RULES["thin"], "antler": 2, "tip": 2},
               "soft": B.PIXEL_RULES["soft"] + [["antler", "tip"]],
               "selout": B.PIXEL_RULES["selout"] + ["antler"]}


def build(model_cls, facing):
    m = B.build(model_cls, facing)
    m.parts = PARTS                      # the base parts first, so their numbers do not change
    for k in ("l", "r"):
        m.tube(f"beam_{k}", "antler", points=5)
        m.tube(f"tine_{k}", "antler", points=3)
        m.ellipsoid(f"tip_{k}", "tip", radii=(0.012, 0.012, 0.014), segments=6, rings=4)
        m.ellipsoid(f"knot_{k}", "antler", radii=(0.018, 0.018, 0.016), segments=6, rings=4)
    for i in range(3):
        m.ellipsoid(f"sprout{i}", "sprout", radii=(0.040, 0.018, 0.024), segments=8, rings=4)
    return m


def pose(m, t):
    B.pose(m, t)
    a = K.anchors(m)
    cap = a["cap"]
    for sgn, k in ((1, "l"), (-1, "r")):
        root = cap + Vector((0.000, 0.070 * sgn, 0.060))
        pts = [root + Vector((-0.036 * i, 0.040 * sgn * i, 0.060 * i - 0.0040 * i * i)) for i in range(5)]   # big enough to clear her hair
        m.set_tube(f"beam_{k}", [tuple(p) for p in pts], [0.020, 0.018, 0.016, 0.013, 0.010])
        fork = pts[2]
        m.set_tube(f"tine_{k}", [tuple(fork), tuple(fork + Vector((0.020, 0.020 * sgn, 0.045))),
                                 tuple(fork + Vector((0.030, 0.034 * sgn, 0.090)))], [0.014, 0.012, 0.009])
        m.objects[f"tip_{k}"].location = pts[-1]
        m.objects[f"knot_{k}"].location = root
    sway = 0.006 * math.sin(2 * math.pi * t) if t is not None else 0.0
    for i, (k, f) in enumerate((("l", 4), ("r", 4), ("l", 2))):
        sgn = 1 if k == "l" else -1
        base = cap + Vector((0.000, 0.070 * sgn, 0.060))
        m.objects[f"sprout{i}"].location = base + Vector((-0.036 * f + 0.012, (0.040 * f + 0.020) * sgn, 0.060 * f - 0.0040 * f * f + sway))
