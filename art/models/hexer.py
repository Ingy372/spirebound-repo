"""Hedge Hexer (Floor 1 monster, group grounds: a caster who mends hurt allies), built from the approved Road Bandit.

ART_REQUESTS.md (2026-11-25): a bandit caster "players should learn to kill her first". Same body and hood as
art/models/bandit.py (untouched); this file makes her a hedge witch:
  Silhouette: unmasked (the face shows: she is the one to spot first), long grey hair falling from the hood, a patched
              shawl over the shoulders, a crooked staff hung with bone charms in the right hand, a green mending glow
              held up in the left. No sword, no buckler, no scarf.
  Colours:    the bandit's mud-brown hood, a faded plum shawl with patches, charcoal jerkin; bleached bone charms and a
              sickly-green glow (never the Mystic's leaves or bud, rule O20).
  Details:    shawl patches and its ragged hem, three bone charms on cords, the staff's crook, herb pouches at the belt,
              grey hair locks, the glow's bright core.
Addons: none (a monster, rule A1).
"""
from __future__ import annotations

import math

import humanoid as H
from mathutils import Vector

import addon_kit as K
import bandit as B
from bandit import WALK_FRAMES, REFERENCE, PROJECTION, CANVAS_OFFSET, assign_depth_parts  # noqa: F401

NAME = "hexer"
PALETTE = "hexer"
# literal values: check_creature.py reads these lines without importing the model
SIGNATURE = ["shawl", "hilt"]           # "hilt" is her staff (part reuse, see PARTS)
HEAD_PARTS = ["skin", "hair", "strand", "eye", "brow", "nose", "hood"]
LEG_PARTS = ["leg_a", "leg_b", "boot_a", "boot_b"]
CHECK = {"size": (0.85, 1.50), "head": 0.08, "legs_side": 0.05, "eye": 1}
# at most 33 parts (art/README.md): her gear reuses the bandit parts she hides, recoloured in her palette:
#   staff -> "hilt", bone charms -> "iron", patches -> "buckler", glow -> "scarf", herbs -> "pouch", locks -> "hair"
PARTS = B.PARTS + ["shawl"]
PIXEL_RULES = {**B.PIXEL_RULES,
               "weight": {**B.PIXEL_RULES["weight"], "shawl": 1.4, "buckler": 2.6, "hilt": 3.0, "iron": 4.0, "scarf": 6.0},
               "thin": {**B.PIXEL_RULES["thin"], "buckler": 2, "hilt": 2, "iron": 2, "scarf": 3},
               "soft": B.PIXEL_RULES["soft"] + [["shawl", "buckler"], ["hilt", "iron"]],
               "texture": {**B.PIXEL_RULES["texture"], "shawl": [0.45, 0.2]},
               "no_outline": B.PIXEL_RULES.get("no_outline", []) + ["scarf"],
               "selout": B.PIXEL_RULES["selout"] + ["shawl"]}
SPEC = H.spec(torso_r=(0.092, 0.138, 0.178), arm_r=0.042, leg_r=0.046, stride=0.11, lift=0.050, bob=0.014,
              strands=(-1.0, 0.0, 1.0))
B.SPEC = SPEC                            # a slighter figure than the bandit's
HIDDEN = ["blade", "guard", "grip", "buckler", "buckler_rim", "boss", "scarf", "tail0", "tail1"]


def _staff_hand(sh, a, walking):
    swing = 0.04 * math.sin(a) if walking else 0.0
    return sh + Vector((0.100 + swing, -0.070, -0.230))


def _glow_hand(sh, a, walking):
    return sh + Vector((0.170, 0.060, -0.110))            # held up and out, palm glowing


B._sword_hand, B._buckler_hand = _staff_hand, _glow_hand


def build(model_cls, facing):
    m = B.build(model_cls, facing)
    m.parts = PARTS                      # the base parts first, so their numbers do not change
    m.ellipsoid("shawl", "shawl", radii=(0.135, 0.205, 0.090), segments=16, rings=8)
    m.box("shawl_back", "shawl", size=(0.030, 0.270, 0.230))
    for i in range(2):
        m.ellipsoid(f"patch{i}", "buckler", radii=(0.030, 0.034, 0.020), segments=8, rings=6)
    for k in ("l", "r"):
        m.tube(f"lock_{k}", "hair", points=4)
    m.capsule("staff", "hilt")
    m.tube("crook", "hilt", points=5)
    for i in range(3):
        m.ellipsoid(f"charm{i}", "iron", radii=(0.014, 0.012, 0.022), segments=6, rings=4)
    m.ellipsoid("glow", "scarf", radii=(0.042, 0.042, 0.042), segments=10, rings=8)
    for i in range(2):
        m.ellipsoid(f"herb{i}", "pouch", radii=(0.024, 0.024, 0.028), segments=8, rings=6)
    return m


def pose(m, t):
    B.pose(m, t)
    for name in HIDDEN:
        K.hide(m, name)
    a = K.anchors(m)
    up, head, s = a["up"], a["head"], m.spec
    m.objects["shawl"].location = Vector((-0.010, 0, 0.860)) + up
    m.objects["shawl_back"].location = Vector((-0.125, 0, 0.740)) + up
    m.objects["patch0"].location = Vector((0.080, 0.090, 0.880)) + up
    m.objects["patch1"].location = Vector((-0.100, -0.080, 0.820)) + up
    for sign, k in ((1, "l"), (-1, "r")):
        top = head + Vector((0.050, 0.100 * sign, -0.010))
        pts = [top + Vector((0.010 * i, 0.012 * sign * i, -0.050 * i)) for i in range(4)]
        m.set_tube(f"lock_{k}", [tuple(p) for p in pts], [0.030, 0.032, 0.028, 0.020])
    hand = a["hand_r"]
    d = Vector((0.08, -0.06, 1.0)).normalized()
    foot, top = hand - d * 0.380, hand + d * 0.520
    m.put_segment("staff", foot, top, 0.015)
    crook = [top + Vector((0.030 * math.sin(u), 0, 0.040 * math.cos(u) - 0.040)) for u in (0.0, 0.8, 1.6, 2.4, 3.0)]
    crook = [top + Vector((0, 0, 0))] + crook[1:]
    m.set_tube("crook", [tuple(p) for p in crook], [0.015, 0.014, 0.013, 0.012, 0.010])
    sway = 0.02 * math.sin(2 * math.pi * t) if t is not None else 0.0
    for i in range(3):
        m.objects[f"charm{i}"].location = top - d * (0.040 + 0.035 * i) + Vector((0.030 + sway, 0.020 * (i - 1), -0.020))
    m.objects["glow"].location = a["hand_l"] + Vector((0.050, 0, 0.060))   # above the palm, clear of the hand
    for i in range(2):
        m.objects[f"herb{i}"].location = Vector((s["torso_r"][0] * 0.6, (0.120 if i else 0.060) * 1.0, s["belt_z"] - 0.030)) + up
