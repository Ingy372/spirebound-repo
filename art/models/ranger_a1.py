"""Ranger addon 1: the Hawk-Feather Hood (overlay on the approved Ranger, which stays frozen; rules A1-A7).

  Addon:   a tooled leather band round the hood with two long barred hawk feathers tucked in at the left side.
  Details: leather band (a line, O7) with a brass stud, two feathers with dark bars.
"""
from __future__ import annotations

import math

from mathutils import Vector

import humanoid as H
import ranger as B
from ranger import WALK_FRAMES, PALETTE, REFERENCE, PROJECTION, CANVAS_OFFSET, SPEC, assign_depth_parts  # noqa: F401

NAME = "ranger_a1"
BASE = "ranger"
# literal values: check_creature.py reads these lines without importing the model
SIGNATURE = ["feather"]                 # the addon itself must show
HEAD_PARTS = ["skin", "hair", "strand", "eye", "brow", "nose", "hood", "band", "feather", "bar"]
LEG_PARTS = ["leg_a", "leg_b", "boot_a", "boot_b"]
CHECK = {"size": (0.85, 1.45), "head": 0.08, "legs_side": 0.05, "eye": 1}
PARTS = B.PARTS + ["band", "feather", "bar", "stud"]
PIXEL_RULES = {**B.PIXEL_RULES,
               "weight": {**B.PIXEL_RULES["weight"], "band": 2.2, "feather": 2.4, "bar": 3.2, "stud": 5.0},
               "thin": {**B.PIXEL_RULES["thin"], "band": 2, "feather": 3, "bar": 2, "stud": 2},
               "soft": B.PIXEL_RULES["soft"] + [["feather", "bar"], ["band", "stud"]],
               "selout": B.PIXEL_RULES["selout"] + ["feather"]}
HOOD_R = (0.128, 0.130, 0.122)          # ranger.py's hood


def build(model_cls, facing):
    m = B.build(model_cls, facing)
    m.parts = PARTS                      # the base parts first, so their numbers do not change
    m.tube("band", "band", points=7)
    m.ellipsoid("stud", "stud", radii=(0.014, 0.014, 0.014), segments=6, rings=4)
    for i in range(2):
        m.tube(f"feather{i}", "feather", points=6)
        for j in range(2):
            m.tube(f"bar{i}{j}", "bar", points=3)
    return m


def pose(m, t):
    B.pose(m, t)
    hood_c = m.objects["hood"].location.copy()
    band = [H.on_ellipsoid(hood_c, HOOD_R, (math.cos(u), math.sin(u), -0.15), 1.04) for u in (-1.7, -1.1, -0.55, 0.0, 0.55, 1.1, 1.7)]
    m.set_tube("band", [tuple(p) for p in band], [0.011] * 7)
    m.objects["stud"].location = H.on_ellipsoid(hood_c, HOOD_R, (1.0, 0.0, -0.15), 1.08)
    sway = 0.010 * math.sin(2 * math.pi * t) if t is not None else 0.0
    root = H.on_ellipsoid(hood_c, HOOD_R, (-0.2, 1.0, -0.05), 1.03)
    for i, ln in enumerate((0.200, 0.165)):
        d = Vector((-0.14 - 0.02 * i, 0.030 + 0.020 * i, 0.140 - 0.030 * i)).normalized()
        pts = [root + d * ln * k / 5 + Vector((0, 0, -0.006 * k * k / 5 + sway * k / 5)) for k in range(6)]
        m.set_tube(f"feather{i}", [tuple(p) for p in pts], [0.008, 0.020, 0.024, 0.022, 0.016, 0.006])
        side = d.cross(Vector((0, 0, 1))).normalized() * 0.022
        for j, f in enumerate((0.45, 0.72)):
            c = root + d * ln * f + Vector((0, 0, -0.006 * (5 * f) ** 2 / 5 + sway * f))
            m.set_tube(f"bar{i}{j}", [tuple(c - side), tuple(c), tuple(c + side)], [0.006] * 3)
