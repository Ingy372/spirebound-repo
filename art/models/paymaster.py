"""The Paymaster (Floor 1 rare roamer, levels 19-30; adventure design 4.4), built from the approved Road Bandit (frozen):
the bandits' banker, out on the road with the payroll chest and two guards. He runs for the ground's edge when hurt.

Same body as art/models/bandit.py (untouched); this file swaps the gear and colours (like crossbowman.py):
  Silhouette: bare-faced (no mask: he never fights if he can help it) under a round low-crowned felt hat with a brim
              (the bandit's hood and its rim, re-shaped and recoloured), carrying a big iron-banded strongbox in both
              arms in front of his belly. No sword, no buckler.
  Colours:    a bottle-green coat-cape and a mustard waistcoat (the bandits wear mud and charcoal), a black felt hat
              with a gold band, a dark oak strongbox with brass bands and a brass lock, gold coins at the lid.
  Details:    hat brim, gold hat band, the chest's two brass bands and lock plate, coins glinting at the lid's edge,
              the coin pouch at his belt (the bandit's), jerkin laces.
Look-alike: Tibia's Hunter / Citizen outfits (plain townsfolk): ours carries the chest and wears the felt hat.
Addons: none (a monster, rule A1).
"""
from __future__ import annotations

import math

from mathutils import Euler, Vector

import addon_kit as K
import bandit as B
import humanoid as H
from bandit import WALK_FRAMES, PROJECTION, CANVAS_OFFSET, SPEC, assign_depth_parts  # noqa: F401

NAME = "paymaster"
PALETTE = "paymaster"
REFERENCE = "look_129.png"
# literal values: check_creature.py reads these lines without importing the model
SIGNATURE = ["box", "band"]
HEAD_PARTS = ["skin", "hair", "strand", "eye", "brow", "nose", "hood", "rim"]
LEG_PARTS = ["leg_a", "leg_b", "boot_a", "boot_b"]
CHECK = {"size": (0.85, 1.45), "head": 0.08, "legs_side": 0.05, "eye": 1}
PARTS = B.PARTS + ["box", "band", "coin"]   # at most 33 parts (art/README.md); hat = the hood, hat band = its rim
PIXEL_RULES = {**B.PIXEL_RULES,
               "weight": {**B.PIXEL_RULES["weight"], "box": 2.0, "band": 3.0, "coin": 5.0},
               "thin": {**B.PIXEL_RULES["thin"], "band": 2, "coin": 2},
               "soft": B.PIXEL_RULES["soft"] + [["box", "band", "coin"]],
               "texture": {**B.PIXEL_RULES["texture"], "box": [0.5, 0.2], "hood": [0.15, 0.0]},
               "selout": B.PIXEL_RULES["selout"] + ["box"]}
HIDDEN = ["blade", "guard", "grip", "buckler", "buckler_rim", "boss", "scarf", "tail0", "tail1"]


def _carry_r(sh, a, walking):
    return sh + Vector((0.150, 0.050, -0.250))


def _carry_l(sh, a, walking):
    return sh + Vector((0.150, -0.050, -0.250))


B._sword_hand, B._buckler_hand = _carry_r, _carry_l     # both arms round the chest


def build(model_cls, facing):
    m = B.build(model_cls, facing)
    m.parts = PARTS                      # the base parts first, so their numbers do not change
    m.ellipsoid("brim", "hood", radii=(0.128, 0.128, 0.012), segments=20, rings=6)
    m.box("chest", "box", size=(0.150, 0.230, 0.140))
    m.box("lid", "box", size=(0.160, 0.240, 0.040))
    for k in ("a", "b"):
        m.box(f"band_{k}", "band", size=(0.164, 0.022, 0.186))
    m.box("lock", "band", size=(0.012, 0.040, 0.044))
    for i in range(3):
        m.ellipsoid(f"coin{i}", "coin", radii=(0.020, 0.020, 0.008), segments=8, rings=4)
    return m


def pose(m, t):
    B.pose(m, t)
    for name in HIDDEN:
        K.hide(m, name)
    a = K.anchors(m)
    head = a["head"]
    # the hood becomes a round low-crowned felt hat sitting on top of the head, with a brim and a gold band
    hat = m.objects["hood"]
    top = head + Vector((-0.030, 0, 0.150))           # pushed back on the crown of the head: the eyes stay clear (O3)
    hat.location = top
    hat.scale = (0.090, 0.092, 0.058)
    hat.rotation_mode = "XYZ"
    hat.rotation_euler = Euler((0, -0.30, 0))
    brim = m.objects["brim"]
    brim.location = top + Vector((0.000, 0, -0.034))
    brim.rotation_mode = "XYZ"
    brim.rotation_euler = Euler((0, -0.30, 0))
    band = [tuple(top + Vector((0.092 * math.cos(u), 0.094 * math.sin(u), -0.020 + 0.027 * math.cos(u)))) for u in
            (-1.5, -0.9, -0.3, 0.3, 0.9, 1.5, 2.4)]
    m.set_tube("hood_rim", band, [0.012] * 7)
    # the strongbox, held in both arms in front of the belly
    c = (a["hand_l"] + a["hand_r"]) / 2 + Vector((0.030, 0, 0.040))
    m.objects["chest"].location = c
    m.objects["lid"].location = c + Vector((0, 0, 0.090))
    for k, dy in (("a", 0.070), ("b", -0.070)):
        m.objects[f"band_{k}"].location = c + Vector((0, dy, 0.020))
    m.objects["lock"].location = c + Vector((0.080, 0, 0.060))
    walk = 0.006 * math.sin(4 * math.pi * t) if t is not None else 0.0     # coins jingle at the lid
    for i in range(3):
        m.objects[f"coin{i}"].location = c + Vector((0.050 - 0.040 * i, -0.060 + 0.060 * i, 0.116 + walk))
