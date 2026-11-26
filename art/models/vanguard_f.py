"""Vanguard, women's version (player class outfit): the approved Vanguard (frozen) on a woman's figure.

Jay, 2026-11-25: women's characters need their own class outfits. Same armour, colours, shield and sword as the
approved Vanguard (art/models/vanguard.py, untouched); this file only changes the figure and the hair:
  Figure: narrower shoulders and waist, slimmer arms and legs.
  Hair:   chestnut hair tied in a long ponytail that swings behind (reads as a woman from every side), side locks.
Addons: the same Crested Helm and Knight's Mantle (vanguard_f_a1.py / vanguard_f_a2.py).
"""
from __future__ import annotations

import math

from mathutils import Vector

import humanoid as H
import vanguard as V
from vanguard import (WALK_FRAMES, PALETTE, REFERENCE, PROJECTION, CANVAS_OFFSET, PARTS, PIXEL_RULES,  # noqa: F401
                      assign_depth_parts)

NAME = "vanguard_f"
PALETTE = "vanguard_f"                       # the base colours with its own hair (outfit_palettes.py)
# literal values: check_creature.py reads these lines without importing the model
SIGNATURE = ["pauldron", "tabard"]
HEAD_PARTS = ["skin", "hair", "strand", "eye", "brow", "nose"]
LEG_PARTS = ["leg_a", "leg_b", "boot_a", "boot_b", "knee"]
CHECK = {"size": (0.85, 1.45), "head": 0.08, "legs_side": 0.05, "eye": 1}
SPEC = H.spec(torso_r=(0.098, 0.146, 0.182), arm_r=0.045, leg_r=0.049, shoulder_y=0.154,
              stride=0.12, lift=0.055, bob=0.018, strands=(-1.2, -0.2, 0.9))
V.SPEC = SPEC                            # the frozen base builds on this figure instead of its own


def build(model_cls, facing):
    m = V.build(model_cls, facing)
    m.tube("ponytail", "hair", points=6)
    m.ellipsoid("tie", "cuff", radii=(0.018, 0.024, 0.024), segments=8, rings=6)
    for k in ("l", "r"):
        m.ellipsoid(f"sidelock_{k}", "hair", radii=(0.028, 0.022, 0.080), segments=8, rings=6)
    return m


def pose(m, t):
    V.pose(m, t)
    head = m.objects["head"].location.copy()
    a = 0.0 if t is None else 2 * math.pi * t
    swing = 0.035 * math.sin(a) if t is not None else 0.0
    root = head + Vector((-0.112, 0, 0.020))      # hangs DOWN the back: pointing back, it stood up like a horn from the front
    pts = [root + Vector((-0.014 * k, swing * k / 5, -0.058 * k)) for k in range(6)]
    m.set_tube("ponytail", [tuple(p) for p in pts], [0.030, 0.034, 0.032, 0.028, 0.022, 0.014])
    m.objects["tie"].location = root + Vector((-0.012, 0, -0.006))
    for sign, k in ((1, "l"), (-1, "r")):
        m.objects[f"sidelock_{k}"].location = head + Vector((0.044, 0.104 * sign, -0.046))
