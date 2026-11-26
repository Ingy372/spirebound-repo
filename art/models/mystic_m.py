"""Mystic, men's version (player class outfit): the approved Mystic (frozen) on a man's figure.

Jay, 2026-11-25: every class outfit needs a men's and a women's version; the approved Mystic reads as a woman
(long braid). Same robes, shoulder leaves, beads and staff (art/models/mystic.py, untouched); this file only changes:
  Figure: broader shoulders and chest.
  Hair:   short brown hair and a full beard (darker than her honey hair, to read against his skin) (a hedge druid); the base's braid and back hair are tucked away.
Addons: the same Antler Crown and Owl Companion (mystic_m_a1.py / mystic_m_a2.py).
"""
from __future__ import annotations

from mathutils import Vector

import addon_kit as K
import humanoid as H
import mystic as V
from mystic import (WALK_FRAMES, PALETTE, REFERENCE, PROJECTION, CANVAS_OFFSET, PARTS, PIXEL_RULES,  # noqa: F401
                    assign_depth_parts)

NAME = "mystic_m"
PALETTE = "mystic_m"                       # the base colours with its own hair (outfit_palettes.py)
# literal values: check_creature.py reads these lines without importing the model
SIGNATURE = ["leaf", "staff"]
HEAD_PARTS = ["skin", "hair", "strand", "eye", "brow", "nose"]
LEG_PARTS = ["boot_a", "boot_b", "sole"]
CHECK = {"size": (0.85, 1.55), "head": 0.08, "legs_side": 0.0, "legs_updown": 0.0, "eye": 1}
SPEC = H.spec(robe=("robe", "over", 0.105), torso_r=(0.102, 0.156, 0.186), arm_r=0.054, leg_r=0.046, shoulder_y=0.166,
              stride=0.10, lift=0.045, bob=0.012, arm_swing=0.08, strands=(-1.2, -0.1, 1.0))
V.SPEC = SPEC                            # the frozen base builds on this figure instead of its own


def build(model_cls, facing):
    m = V.build(model_cls, facing)
    m.ellipsoid("nape_m", "hair", radii=(0.046, 0.094, 0.054), segments=12, rings=6)
    m.ellipsoid("beard_m", "hair", radii=(0.060, 0.086, 0.086), segments=12, rings=8)
    m.ellipsoid("stache_m", "hair", radii=(0.022, 0.062, 0.016), segments=8, rings=6)
    return m


def pose(m, t):
    V.pose(m, t)
    for name in ("backhair", "braid"):
        K.hide(m, name)
    head = m.objects["head"].location.copy()
    m.objects["nape_m"].location = head + Vector((-0.084, 0, -0.026))
    m.objects["beard_m"].location = head + Vector((0.080, 0, -0.098))
    m.objects["stache_m"].location = head + Vector((0.112, 0, -0.046))
