"""Men's Mystic addon 1: the approved mystic_a1 addon on the mystic_m figure (rules A1-A9).

The same parts and colours as art/models/mystic_a1.py (approved, untouched); only the figure under it changes.
"""
from __future__ import annotations

import mystic_m as G
import mystic_a1 as A

A.B = G                       # the approved addon now dresses this figure
from mystic_a1 import *  # noqa: E402,F401,F403

NAME = "mystic_m_a1"
BASE = "mystic_m"
PALETTE = G.PALETTE                     # the same colours as the figure under it, or the overlay repaints the hair
# literal values: check_creature.py reads these lines without importing the model
SIGNATURE = ["antler"]                  # the addon itself must show
HEAD_PARTS = ["skin", "hair", "strand", "eye", "brow", "nose", "circlet", "antler", "sprout"]
LEG_PARTS = ["boot_a", "boot_b", "sole"]
CHECK = {"size": (0.85, 1.55), "head": 0.08, "legs_side": 0.0, "legs_updown": 0.0, "eye": 1}
