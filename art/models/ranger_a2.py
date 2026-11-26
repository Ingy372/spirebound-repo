"""Ranger addon 2: the Huntsman's Horn (overlay on the approved Ranger, which stays frozen; rules A1-A7).

  Addon:   a studded leather guard over the right shoulder, and a curved hunting horn with a brass bell and
           mouthpiece hanging at the left hip on a strap across the chest.
  Details: three brass studs on the guard, its rolled edge (a line), the horn's brass bell and mouthpiece, the strap.
"""
from __future__ import annotations

import math

from mathutils import Vector

import addon_kit as K
import ranger as B
from ranger import WALK_FRAMES, PALETTE, REFERENCE, PROJECTION, CANVAS_OFFSET, SPEC, assign_depth_parts  # noqa: F401

NAME = "ranger_a2"
BASE = "ranger"
# literal values: check_creature.py reads these lines without importing the model
SIGNATURE = ["guard"]                   # the horn hangs in front of the left hip: hidden from behind, as it should be
HEAD_PARTS = ["skin", "hair", "strand", "eye", "brow", "nose", "hood"]
LEG_PARTS = ["leg_a", "leg_b", "boot_a", "boot_b"]
CHECK = {"size": (0.85, 1.45), "head": 0.08, "legs_side": 0.05, "eye": 1}
PARTS = B.PARTS + ["guard", "edge", "stud", "horn", "brass", "strap"]
PIXEL_RULES = {**B.PIXEL_RULES,
               "weight": {**B.PIXEL_RULES["weight"], "guard": 1.6, "edge": 2.4, "stud": 5.0, "horn": 2.2, "brass": 3.6,
                          "strap": 2.2},
               "thin": {**B.PIXEL_RULES["thin"], "edge": 2, "stud": 2, "brass": 2, "strap": 3},
               "soft": B.PIXEL_RULES["soft"] + [["guard", "edge", "stud"], ["horn", "brass"]],
               "selout": B.PIXEL_RULES["selout"] + ["guard", "horn"]}


def build(model_cls, facing):
    m = B.build(model_cls, facing)
    m.parts = PARTS                      # the base parts first, so their numbers do not change
    m.ellipsoid("guard", "guard", radii=(0.088, 0.072, 0.058), segments=14, rings=8)
    m.tube("guard_edge", "edge", points=6)
    for i in range(3):
        m.ellipsoid(f"stud{i}", "stud", radii=(0.012, 0.012, 0.012), segments=6, rings=4)
    m.tube("horn", "horn", points=7)
    m.frustum("bell", "brass", top_ratio=1.0, segments=12)
    m.ellipsoid("mouth", "brass", radii=(0.014, 0.014, 0.014), segments=6, rings=4)
    m.capsule("strap", "strap")
    return m


def pose(m, t):
    B.pose(m, t)
    a = K.anchors(m)
    sh = a["shoulder_r"] + Vector((0.0, -0.020, 0.036))
    m.objects["guard"].location = sh
    edge = [sh + Vector((0.085 * math.cos(u), -0.068 * abs(math.sin(u)) - 0.010, -0.034 + 0.010 * math.sin(u)))
            for u in (-1.5, -0.9, -0.3, 0.3, 0.9, 1.5)]
    m.set_tube("guard_edge", [tuple(p) for p in edge], [0.008] * 6)
    for i, u in enumerate((-0.6, 0.0, 0.6)):
        m.objects[f"stud{i}"].location = sh + Vector((0.050 * math.cos(u) + 0.010, -0.040 - 0.012 * math.sin(u), 0.040))
    swing = 0.025 * math.sin(2 * math.pi * t) if t is not None else 0.0
    hip = a["belt_l"] + Vector((0.110 + swing, 0.020, -0.010))       # in front of the hip, or the cloak hides it
    pts = [hip + Vector((0.030 - 0.020 * k, 0.010 * k, -0.016 * k + 0.0050 * k * k)) for k in range(7)]
    m.set_tube("horn", [tuple(p) for p in pts], [0.013, 0.018, 0.023, 0.028, 0.033, 0.038, 0.043])
    K.track(m.objects["bell"], pts[-1], pts[-1] - pts[-2], (0.048, 0.048, 0.018))
    m.objects["mouth"].location = pts[0] + Vector((0.012, 0, 0.004))
    m.put_segment("strap", a["shoulder_r"] + Vector((0.075, 0.010, 0.020)), hip + Vector((0.050, -0.020, 0.040)), 0.011)
