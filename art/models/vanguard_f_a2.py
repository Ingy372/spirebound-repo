"""Women's Vanguard addon 2: the approved vanguard_a2 addon on the vanguard_f figure (rules A1-A9).

The same parts and colours as art/models/vanguard_a2.py (approved, untouched); only the figure under it changes.
"""
from __future__ import annotations

import vanguard_f as G
import vanguard_a2 as A

A.V = G                       # the approved addon now dresses this figure
from vanguard_a2 import *  # noqa: E402,F401,F403

NAME = "vanguard_f_a2"
BASE = "vanguard_f"
PALETTE = G.PALETTE                     # the same colours as the figure under it, or the overlay repaints the hair
# literal values: check_creature.py reads these lines without importing the model
SIGNATURE = ["mantle", "fur"]                 # the addon itself must show
HEAD_PARTS = ["skin", "hair", "strand", "eye", "brow", "nose"]
LEG_PARTS = ["leg_a", "leg_b", "boot_a", "boot_b", "knee"]
CHECK = {"size": (0.85, 1.45), "head": 0.08, "legs_side": 0.05, "eye": 1}
