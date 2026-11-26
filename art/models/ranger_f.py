"""Ranger, women's version (player class outfit): the approved Ranger (frozen) on a woman's figure.

Jay, 2026-11-25: women's characters need their own class outfits. Same hood, cloak, bow and quiver as the approved
Ranger (art/models/ranger.py, untouched); this file only changes the figure and the hair:
  Figure: narrower shoulders and waist, slimmer limbs.
  Hair:   two long auburn locks falling out of the hood over the chest, and a braid down the back over the cloak.
Addons: the same Hawk-Feather Hood and Huntsman's Horn (ranger_f_a1.py / ranger_f_a2.py).
"""
from __future__ import annotations

import math

from mathutils import Vector

import humanoid as H
import ranger as V
from ranger import (WALK_FRAMES, PALETTE, REFERENCE, PROJECTION, CANVAS_OFFSET, PARTS, PIXEL_RULES,  # noqa: F401
                    assign_depth_parts)

NAME = "ranger_f"
PALETTE = "ranger_f"                       # the base colours with its own hair (outfit_palettes.py)
# literal values: check_creature.py reads these lines without importing the model
SIGNATURE = ["hood", "bow"]
HEAD_PARTS = ["skin", "hair", "strand", "eye", "brow", "nose", "hood"]
LEG_PARTS = ["leg_a", "leg_b", "boot_a", "boot_b"]
CHECK = {"size": (0.85, 1.45), "head": 0.08, "legs_side": 0.05, "eye": 1}
SPEC = H.spec(torso_r=(0.088, 0.134, 0.178), arm_r=0.039, leg_r=0.043, cap=(-0.020, 0.010), cap_r=(0.110, 0.108, 0.100),
              stride=0.14, lift=0.065, bob=0.016, strands=(-0.6, 0.5))
V.SPEC = SPEC                            # the frozen base builds on this figure instead of its own
BRAID_N = 6


def build(model_cls, facing):
    m = V.build(model_cls, facing)
    for k in ("l", "r"):
        m.tube(f"lock_{k}", "hair", points=5)
    m.tube("braid", "hair", points=BRAID_N)
    return m


def pose(m, t):
    V.pose(m, t)
    head = m.objects["head"].location.copy()
    a = 0.0 if t is None else 2 * math.pi * t
    swing = 0.030 * math.sin(a) if t is not None else 0.0
    for sign, k in ((1, "l"), (-1, "r")):
        top = head + Vector((0.060, 0.098 * sign, -0.010))
        pts = [top + Vector((0.024 * i, 0.014 * sign * i, -0.052 * i)) for i in range(5)]   # out over the cloak, or the hood hides them
        m.set_tube(f"lock_{k}", [tuple(p) for p in pts], [0.030, 0.032, 0.030, 0.026, 0.018])
    root = head + Vector((-0.140, 0, -0.040))
    pts = [root + Vector((-0.016 * i, swing * i / 5, -0.070 * i)) for i in range(BRAID_N)]
    m.set_tube("braid", [tuple(p) for p in pts], [0.030 - 0.003 * i for i in range(BRAID_N)])
