"""Mystic addon 2: the Owl Companion (overlay on the approved Mystic, which stays frozen; rules A1-A7).

  Addon:   a small snowy owl (pale, so it never merges with her sandy hair) perched on her left shoulder (the staff is in her right hand), turning with her.
  Detail (DETAIL_RULES step 1): round body, big head with ear tufts, facial disc, two small amber eyes, a hooked
           beak, folded wings with a pale bar, talons gripping the shoulder.
"""
from __future__ import annotations

import math

from mathutils import Vector

import addon_kit as K
import mystic as B
from mystic import WALK_FRAMES, PALETTE, REFERENCE, PROJECTION, CANVAS_OFFSET, SPEC, assign_depth_parts  # noqa: F401

NAME = "mystic_a2"
BASE = "mystic"
# literal values: check_creature.py reads these lines without importing the model
SIGNATURE = ["owl"]                     # the face disc cannot show from behind; the owl itself must
HEAD_PARTS = ["skin", "hair", "strand", "eye", "brow", "nose"]
LEG_PARTS = ["boot_a", "boot_b", "sole"]
CHECK = {"size": (0.85, 1.55), "head": 0.08, "legs_side": 0.0, "legs_updown": 0.0, "eye": 1}
OWL = 1.45                              # owl size: smaller than this vanishes at game size
PARTS = B.PARTS + ["owl", "wing", "disc", "owl_eye", "beak", "talon"]
PIXEL_RULES = {**B.PIXEL_RULES,
               "weight": {**B.PIXEL_RULES["weight"], "owl": 1.6, "wing": 1.8, "disc": 2.0, "owl_eye": 8.0, "beak": 5.0,
                          "talon": 4.0},
               "thin": {**B.PIXEL_RULES["thin"], "owl_eye": 3, "beak": 2, "talon": 2},
               "soft": B.PIXEL_RULES["soft"] + [["owl", "disc", "owl_eye", "beak"]],
               "texture": {**B.PIXEL_RULES["texture"], "owl": [0.6, 0.3], "wing": [0.6, 0.3]},
               "selout": B.PIXEL_RULES["selout"] + ["owl", "wing"]}


def build(model_cls, facing):
    m = B.build(model_cls, facing)
    m.parts = PARTS                      # the base parts first, so their numbers do not change
    m.ellipsoid("owl_body", "owl", radii=(0.050 * OWL, 0.046 * OWL, 0.062 * OWL), segments=12, rings=8)
    m.ellipsoid("owl_head", "owl", radii=(0.046 * OWL, 0.050 * OWL, 0.042 * OWL), segments=12, rings=8)
    m.ellipsoid("owl_disc", "disc", radii=(0.014 * OWL, 0.040 * OWL, 0.032 * OWL), segments=10, rings=6)
    for k in ("l", "r"):
        m.ellipsoid(f"owl_wing_{k}", "wing", radii=(0.040 * OWL, 0.016 * OWL, 0.050 * OWL), segments=10, rings=6)
        m.ellipsoid(f"owl_eye_{k}", "owl_eye", radii=(0.008 * OWL, 0.010 * OWL, 0.010 * OWL), segments=6, rings=4)
        m.cone(f"owl_tuft_{k}", "owl", segments=6)
        m.ellipsoid(f"owl_talon_{k}", "talon", radii=(0.012 * OWL, 0.010 * OWL, 0.008 * OWL), segments=6, rings=4)
    m.ellipsoid("owl_beak", "beak", radii=(0.010 * OWL, 0.008 * OWL, 0.012 * OWL), segments=6, rings=4)
    return m


def pose(m, t):
    B.pose(m, t)
    a = K.anchors(m)
    sh = a["shoulder_l"] + Vector((-0.010, 0.085, 0.040))   # out on the shoulder point, clear of her head
    bob = 0.006 * OWL * math.sin(4 * math.pi * t) if t is not None else 0.0
    body = sh + Vector((0, 0, 0.060 * OWL + bob))
    head = body + Vector((0.006 * OWL, 0, 0.078 * OWL))
    m.objects["owl_body"].location = body
    m.objects["owl_head"].location = head
    m.objects["owl_disc"].location = head + Vector((0.038 * OWL, 0, -0.002 * OWL))
    for sgn, k in ((1, "l"), (-1, "r")):
        m.objects[f"owl_wing_{k}"].location = body + Vector((-0.006 * OWL, 0.036 * OWL * sgn, 0.000 * OWL))
        m.objects[f"owl_eye_{k}"].location = head + Vector((0.050 * OWL, 0.018 * OWL * sgn, 0.006 * OWL))
        m.put_segment(f"owl_tuft_{k}", head + Vector((-0.004 * OWL, 0.028 * OWL * sgn, 0.030 * OWL)), head + Vector((-0.012 * OWL, 0.036 * OWL * sgn, 0.062 * OWL)), 0.014 * OWL, 0.0)
        m.objects[f"owl_talon_{k}"].location = sh + Vector((0.020 * OWL, 0.014 * OWL * sgn, 0.004 * OWL))
    m.objects["owl_beak"].location = head + Vector((0.054 * OWL, 0, -0.012 * OWL))
