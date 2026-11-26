"""Women's Ranger addon 1: the approved ranger_a1 addon on the ranger_f figure (rules A1-A9).

The same parts and colours as art/models/ranger_a1.py (approved, untouched); only the figure under it changes.
"""
from __future__ import annotations

import ranger_f as G
import ranger_a1 as A

A.B = G                       # the approved addon now dresses this figure
from ranger_a1 import *  # noqa: E402,F401,F403

NAME = "ranger_f_a1"
BASE = "ranger_f"
PALETTE = G.PALETTE                     # the same colours as the figure under it, or the overlay repaints the hair
# literal values: check_creature.py reads these lines without importing the model
SIGNATURE = ["feather"]                 # the addon itself must show
HEAD_PARTS = ["skin", "hair", "strand", "eye", "brow", "nose", "hood", "band", "feather", "bar"]
LEG_PARTS = ["leg_a", "leg_b", "boot_a", "boot_b"]
CHECK = {"size": (0.85, 1.45), "head": 0.08, "legs_side": 0.05, "eye": 1}
