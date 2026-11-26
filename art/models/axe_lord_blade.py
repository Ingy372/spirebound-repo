"""Axe-Lord of the Stair, last phase (below 25%): the same warlord with a long curved blade instead of the axe,
a horn snapped off and cracks in his plate. All the drawing lives in axe_lord.py; this file only switches it."""
from __future__ import annotations

import axe_lord as _A

_A.WEAPON = "blade"
_A.DAMAGED = True

NAME = "axe_lord_blade"
WALK_FRAMES = _A.WALK_FRAMES
PALETTE = _A.PALETTE
REFERENCE = _A.REFERENCE
HEIGHT_SHEAR = _A.HEIGHT_SHEAR
LEAN = _A.LEAN
AUTO_PLACE = _A.AUTO_PLACE
SIGNATURE = ["horn", "steel", "cloth"]
HEAD_PARTS = ["helm", "visor", "eye", "horn", "nose", "brow"]
LEG_PARTS = ["leg_a", "leg_b", "boot_a", "boot_b", "knee"]
CHECK = {"size": (0.80, 1.05), "head": 0.07, "legs_side": 0.03, "legs_updown": 0.02, "eye": 1}
PARTS = _A.PARTS
PIXEL_RULES = _A.PIXEL_RULES
build = _A.build
pose = _A.pose
assign_depth_parts = _A.assign_depth_parts
