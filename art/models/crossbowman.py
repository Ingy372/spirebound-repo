"""Bandit Crossbowman (Floor 1 monster, group grounds), built from the approved Road Bandit (frozen).

ART_REQUESTS.md (2026-11-25): a bandit that shoots, "bandit outfit in green and brown". Same body, hood, scarf and
jerkin as art/models/bandit.py (untouched); this file swaps the gear and colours:
  Silhouette: the bandit's round hood and mask, a heavy crossbow held across the body at the ready (stock forward,
              bow arms out to both sides), a bolt case at the right hip. No sword, no buckler.
  Colours:    a dark olive hood and cape (never the Ranger's bright green, rule O20), brown scarf; dark wood crossbow
              with iron arms.
  Details:    the crossbow's iron bow arms and string, a loaded bolt, the stock's iron trigger plate, bolt fletchings
              in the case.
Addons: none (a monster, rule A1).
"""
from __future__ import annotations

from mathutils import Vector

import addon_kit as K
import bandit as B
from bandit import WALK_FRAMES, REFERENCE, PROJECTION, CANVAS_OFFSET, SPEC, assign_depth_parts  # noqa: F401

NAME = "crossbowman"
PALETTE = "crossbowman"
# literal values: check_creature.py reads these lines without importing the model
SIGNATURE = ["scarf", "xbow"]
HEAD_PARTS = ["skin", "hair", "strand", "eye", "brow", "nose", "hood", "scarf"]
LEG_PARTS = ["leg_a", "leg_b", "boot_a", "boot_b"]
CHECK = {"size": (0.85, 1.45), "head": 0.08, "legs_side": 0.05, "eye": 1}
PARTS = B.PARTS + ["xbow", "arm", "string", "bolt"]   # the bolt case reuses "pouch": at most 33 parts (art/README.md)
PIXEL_RULES = {**B.PIXEL_RULES,
               "weight": {**B.PIXEL_RULES["weight"], "xbow": 2.4, "arm": 3.0, "string": 3.0, "bolt": 3.0},
               "thin": {**B.PIXEL_RULES["thin"], "arm": 2, "string": 2, "bolt": 2},
               "soft": B.PIXEL_RULES["soft"] + [["xbow", "arm", "string", "bolt"]],
               "selout": B.PIXEL_RULES["selout"] + ["xbow"]}
HIDDEN = ["blade", "guard", "grip", "buckler", "buckler_rim", "boss"]


def _stock_hand(sh, a, walking):
    return sh + Vector((0.120, 0.020, -0.200))


def _front_hand(sh, a, walking):
    return sh + Vector((0.200, -0.050, -0.190))


B._sword_hand, B._buckler_hand = _stock_hand, _front_hand     # both hands on the crossbow


def build(model_cls, facing):
    m = B.build(model_cls, facing)
    m.parts = PARTS                      # the base parts first, so their numbers do not change
    m.box("stock", "xbow", size=(0.260, 0.040, 0.040))
    for k in ("l", "r"):
        m.capsule(f"arm_{k}", "arm")
    m.capsule("xstring", "string")
    m.capsule("bolt", "bolt")
    m.capsule("case", "pouch")
    for i in range(3):
        m.capsule(f"fletch{i}", "bolt")
    return m


def pose(m, t):
    B.pose(m, t)
    for name in HIDDEN:
        K.hide(m, name)
    a = K.anchors(m)
    c = (a["hand_l"] + a["hand_r"]) / 2 + Vector((0.040, 0, 0.020))
    st = m.objects["stock"]
    st.location = c
    front = c + Vector((0.130, 0, 0.004))
    for sign, k in ((1, "l"), (-1, "r")):
        m.put_segment(f"arm_{k}", front, front + Vector((-0.040, 0.150 * sign, 0.010)), 0.014, 0.009)
    m.put_segment("xstring", front + Vector((-0.040, 0.148, 0.010)), front + Vector((-0.040, -0.148, 0.010)), 0.004)
    m.put_segment("bolt", c + Vector((-0.020, 0, 0.026)), front + Vector((0.030, 0, 0.026)), 0.006)
    s = m.spec
    hip = Vector((-0.020, -s["torso_r"][1] * 1.08, s["belt_z"] - 0.040)) + a["up"]
    top = hip + Vector((-0.030, -0.010, 0.140))
    m.put_segment("case", hip, top, 0.026)
    for i in range(3):
        b = top + Vector((0.008 * i, -0.012 + 0.012 * i, -0.010))
        m.put_segment(f"fletch{i}", b, b + Vector((-0.010, 0.004 * (i - 1), 0.040)), 0.007)
