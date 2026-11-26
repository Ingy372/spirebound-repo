"""Arcanist, men's version (player class outfit): the approved Arcanist (frozen) on a man's figure.

Jay, 2026-11-25: every class outfit needs a men's and a women's version; the approved Arcanist reads as a woman
(long hair). Same robe, collar, runes and ember (art/models/arcanist.py, untouched); this file only changes:
  Figure: broader shoulders and chest.
  Hair:   short black-brown hair and a short pointed beard; the base's long hair and locks are tucked away.
Addons: the same Orbiting Runestones and Floating Grimoire (arcanist_m_a1.py / arcanist_m_a2.py).
"""
from __future__ import annotations

from mathutils import Vector

import addon_kit as K
import humanoid as H
import arcanist as V
from arcanist import (WALK_FRAMES, PALETTE, REFERENCE, PROJECTION, CANVAS_OFFSET, PARTS, PIXEL_RULES,  # noqa: F401
                      assign_depth_parts)

NAME = "arcanist_m"
PALETTE = "arcanist_m"                       # the base colours with its own hair (outfit_palettes.py)
# literal values: check_creature.py reads these lines without importing the model
SIGNATURE = ["collar", "trim"]
HEAD_PARTS = ["skin", "hair", "strand", "eye", "brow", "nose"]
LEG_PARTS = ["boot_a", "boot_b", "sole"]
CHECK = {"size": (0.85, 1.45), "head": 0.08, "legs_side": 0.0, "legs_updown": 0.0, "eye": 1}
SPEC = H.spec(robe=("robe", "trim", 0.105), torso_r=(0.104, 0.158, 0.186), arm_r=0.056, leg_r=0.046, shoulder_y=0.168,
              stride=0.10, lift=0.045, bob=0.012, arm_swing=0.08, strands=(-1.3, -0.3, 0.8))
V.SPEC = SPEC                            # the frozen base builds on this figure instead of its own


def build(model_cls, facing):
    m = V.build(model_cls, facing)
    m.ellipsoid("nape_m", "hair", radii=(0.046, 0.092, 0.052), segments=12, rings=6)
    m.ellipsoid("beard_m", "hair", radii=(0.054, 0.070, 0.070), segments=10, rings=8)
    m.ellipsoid("stache_m", "hair", radii=(0.020, 0.052, 0.014), segments=8, rings=6)
    return m


def pose(m, t):
    V.pose(m, t)
    for name in ("backhair", "lock_l", "lock_r"):
        K.hide(m, name)
    head = m.objects["head"].location.copy()
    m.objects["nape_m"].location = head + Vector((-0.084, 0, -0.026))
    m.objects["beard_m"].location = head + Vector((0.080, 0, -0.100))
    m.objects["stache_m"].location = head + Vector((0.112, 0, -0.044))
