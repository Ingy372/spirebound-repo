"""Arcanist addon 2: the Floating Grimoire (overlay on the approved Arcanist, which stays frozen; rules A1-A7).

  Addon:   a thick spellbook hovering open beside her left hip (her free side), pages glowing, bobbing with her step.
  Details: dark leather covers with gold corners, a gold clasp strap, pale pages, a glowing rune on the open page.
"""
from __future__ import annotations

import math

from mathutils import Euler, Vector

import addon_kit as K
import arcanist as B
from arcanist import WALK_FRAMES, PALETTE, REFERENCE, PROJECTION, CANVAS_OFFSET, SPEC, assign_depth_parts  # noqa: F401

NAME = "arcanist_a2"
BASE = "arcanist"
# literal values: check_creature.py reads these lines without importing the model
SIGNATURE = ["cover", "page"]           # the addon itself must show
HEAD_PARTS = ["skin", "hair", "strand", "eye", "brow", "nose"]
LEG_PARTS = ["boot_a", "boot_b", "sole"]
CHECK = {"size": (0.85, 1.45), "head": 0.08, "legs_side": 0.0, "legs_updown": 0.0, "eye": 1}
PARTS = B.PARTS + ["cover", "page", "corner", "mark"]
PIXEL_RULES = {**B.PIXEL_RULES,
               "weight": {**B.PIXEL_RULES["weight"], "cover": 1.8, "page": 2.4, "corner": 4.0, "mark": 6.0},
               "thin": {**B.PIXEL_RULES["thin"], "corner": 2, "mark": 2, "page": 3},
               "soft": B.PIXEL_RULES["soft"] + [["cover", "corner"], ["page", "mark"]],
               "selout": B.PIXEL_RULES["selout"] + ["cover"]}


def build(model_cls, facing):
    m = B.build(model_cls, facing)
    m.parts = PARTS                      # the base parts first, so their numbers do not change
    for k in ("l", "r"):
        m.box(f"cover_{k}", "cover", size=(0.150, 0.110, 0.018))
        m.box(f"page_{k}", "page", size=(0.130, 0.094, 0.012))
        m.ellipsoid(f"corner_{k}", "corner", radii=(0.012, 0.012, 0.010), segments=6, rings=4)
    m.box("spine", "cover", size=(0.150, 0.022, 0.026))
    m.ellipsoid("mark", "mark", radii=(0.016, 0.016, 0.006), segments=8, rings=4)
    return m


def pose(m, t):
    B.pose(m, t)
    a = K.anchors(m)
    ph = 2 * math.pi * t if t is not None else 0.0
    c = a["belt_l"] + Vector((0.030, 0.200, 0.160 + 0.020 * math.sin(ph)))   # clear of the robe, so it shows from every side
    tilt = 0.42                                            # open book tipped up toward the viewer
    for k, sgn in (("l", 1), ("r", -1)):
        rot = Euler((sgn * 0.22, -tilt, 0.0))
        for name, dz in ((f"cover_{k}", 0.0), (f"page_{k}", 0.010)):
            o = m.objects[name]
            o.rotation_mode = "XYZ"
            o.rotation_euler = rot
            o.location = c + Vector((0.0, sgn * 0.056, dz + abs(sgn) * 0.008)) - Vector((0, 0, 0.010 if name.startswith("cover") else 0.0))
        m.objects[f"corner_{k}"].location = c + Vector((0.068, sgn * 0.104, 0.004))
    m.objects["spine"].location = c + Vector((0, 0, -0.006))
    m.objects["mark"].location = c + Vector((0.004, 0.040, 0.026))
