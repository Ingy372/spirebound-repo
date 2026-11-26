"""Arcanist addon 1: the Orbiting Runestones (overlay on the approved Arcanist, which stays frozen; rules A1-A7).

  Addon:   two dark rune stones circling her head, each with a glowing cyan rune, bobbing as she walks.
  Details: two stones, each with a glowing mark on its face. (A first try put a gold circlet and gem on her brow:
           her fringe hid them in every direction, so it was dropped; see rule A8.)
"""
from __future__ import annotations

import math

from mathutils import Vector

import addon_kit as K
import arcanist as B
from arcanist import WALK_FRAMES, PALETTE, REFERENCE, PROJECTION, CANVAS_OFFSET, SPEC, assign_depth_parts  # noqa: F401

NAME = "arcanist_a1"
BASE = "arcanist"
# literal values: check_creature.py reads these lines without importing the model
SIGNATURE = ["stone"]            # the addon itself must show
HEAD_PARTS = ["skin", "hair", "strand", "eye", "brow", "nose"]
LEG_PARTS = ["boot_a", "boot_b", "sole"]
CHECK = {"size": (0.85, 1.45), "head": 0.08, "legs_side": 0.0, "legs_updown": 0.0, "eye": 1}
PARTS = B.PARTS + ["stone", "glow"]
PIXEL_RULES = {**B.PIXEL_RULES,
               "weight": {**B.PIXEL_RULES["weight"], "stone": 2.4, "glow": 6.0},
               "thin": {**B.PIXEL_RULES["thin"], "glow": 2},
               "soft": B.PIXEL_RULES["soft"] + [["stone", "glow"]],
               "selout": B.PIXEL_RULES["selout"] + ["stone"]}


def build(model_cls, facing):
    m = B.build(model_cls, facing)
    m.parts = PARTS                      # the base parts first, so their numbers do not change
    for i in range(2):
        m.ellipsoid(f"stone{i}", "stone", radii=(0.040, 0.040, 0.050), segments=10, rings=6)
        m.ellipsoid(f"glow{i}", "glow", radii=(0.016, 0.016, 0.020), segments=6, rings=4)
    return m


def pose(m, t):
    B.pose(m, t)
    a = K.anchors(m)
    ph = 2 * math.pi * t if t is not None else 0.0
    for i in range(2):
        u = ph * 0.5 + math.pi * i + 0.8                  # half a turn per walk cycle: slow and calm
        c = a["head"] + Vector((0.22 * math.cos(u) - 0.04, 0.25 * math.sin(u), 0.07 + 0.025 * math.sin(ph + i)))
        m.objects[f"stone{i}"].location = c
        m.objects[f"glow{i}"].location = c + Vector((0.030, 0, 0.016))
