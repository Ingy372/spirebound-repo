"""Bandit Lieutenant (Floor 1, the Bandit Road ground feature, FD2): one named lieutenant walks the road each hour and
the wanted poster pays on his badge. He throws knives and calls Road Bandits. Built on the approved Road Bandit
(bandit.py, frozen) like the Paymaster: the same body, hood and mask, his own colours and gear.

ART_REQUESTS.md: "a red sash and a tin badge on his chest" (the captain already owns the red sash and red coat, so the
lieutenant's officer mark is a mustard scarf instead; Claude's call, Jay can veto).

Identity (art/OUTFIT_RULES.md step 1; a monster, so O20: no class-outfit signature):
  Silhouette: the road bandit's round hood and masked face (one of them, so players know the gang), but two long
              knives instead of a sword and buckler, and two leather knife belts crossed over his chest.
  Colours:    a wine-black hood and short cape (the gang wears mud-brown, the captain a red coat), a mustard officer's
              scarf over the face, a dark leather-green jerkin, tan belts, a bright tin badge.
  Details:    the tin badge on the left breast (the thing the poster pays for), three throwing knives in the crossed
              belts, the hood rim, the scarf knot and tails, a knife in each hand with a crossguard.
  Attitude:   a sly, wanted man: both knives held low and ready, a quick prowling step.
Look-alike: Tibia's Bandit / Smuggler (human outlaws, the Hunter outfit); ours is hooded and masked with crossed knife
belts and a badge.
Addons: none (a monster, rule A1).
"""
from __future__ import annotations

import math

from mathutils import Vector

import addon_kit as K
import bandit as B
import humanoid as H
from bandit import WALK_FRAMES, PROJECTION, CANVAS_OFFSET, SPEC, assign_depth_parts  # noqa: F401

NAME = "bandit_lieutenant"
PALETTE = "bandit_lieutenant"
REFERENCE = "look_129.png"
# literal values: check_creature.py reads these lines without importing the model
SIGNATURE = ["strap", "scarf"]   # the badge is on the front only (seen S, E, W)
HEAD_PARTS = ["skin", "hair", "strand", "eye", "brow", "nose", "hood", "rim", "scarf"]
LEG_PARTS = ["leg_a", "leg_b", "boot_a", "boot_b"]
CHECK = {"size": (0.85, 1.45), "head": 0.08, "legs_side": 0.05, "eye": 1}
PARTS = B.PARTS + ["strap", "badge", "knife"]   # at most 33 parts (art/README.md)
PIXEL_RULES = {**B.PIXEL_RULES,
               "weight": {**B.PIXEL_RULES["weight"], "strap": 2.6, "badge": 6.0, "knife": 4.0},
               "thin": {**B.PIXEL_RULES["thin"], "strap": 2, "badge": 2, "knife": 2},
               "soft": B.PIXEL_RULES["soft"] + [["torso", "strap", "badge", "knife"]],
               "texture": {**B.PIXEL_RULES["texture"], "strap": [0.4, 0.0]},
               "selout": B.PIXEL_RULES["selout"]}
HIDDEN = ["buckler", "buckler_rim", "boss"]


def _knife_r(sh, a, walking):
    swing = 0.05 * math.sin(a) if walking else 0.0
    return sh + Vector((0.130 + swing, -0.050, -0.270))


def _knife_l(sh, a, walking):
    swing = -0.05 * math.sin(a) if walking else 0.0
    return sh + Vector((0.130 + swing, 0.050, -0.270))


B._sword_hand, B._buckler_hand = _knife_r, _knife_l     # a long knife low in each hand


def build(model_cls, facing):
    m = B.build(model_cls, facing)
    m.parts = PARTS                      # the base parts first, so their numbers do not change
    for k in ("a", "b", "c", "d"):
        m.capsule(f"strap_{k}", "strap", segments=8)
    m.ellipsoid("badge", "badge", radii=(0.018, 0.040, 0.040), segments=10, rings=6)
    m.cone("badge_pin", "badge", segments=6)
    for i in range(3):
        m.capsule(f"tknife{i}", "knife", segments=6)
    m.capsule("blade2", "blade")
    m.capsule("guard2", "hilt")
    m.capsule("grip2", "hilt")
    return m


def pose(m, t):
    B.pose(m, t)
    for name in HIDDEN:
        K.hide(m, name)
    a = K.anchors(m)
    s = m.spec
    up = a["up"]
    front = s["torso_r"][0] * 1.02
    # two knife belts crossed over the chest, shoulder to opposite hip, lying on the jerkin's front
    for k, sgn in (("a", 1), ("b", -1)):
        top = Vector((front - 0.010, 0.110 * sgn, s["shoulder_z"] - 0.020)) + up
        bot = Vector((front + 0.010, -0.120 * sgn, s["belt_z"] + 0.010)) + up
        m.put_segment(f"strap_{k}", top, bot, 0.017)
    # ...and over the shoulders, crossing again on the back (so they show from behind too)
    for k, sgn in (("c", 1), ("d", -1)):
        top = Vector((-front + 0.010, 0.110 * sgn, s["shoulder_z"] - 0.020)) + up
        bot = Vector((-front - 0.010, -0.120 * sgn, s["belt_z"] + 0.010)) + up
        m.put_segment(f"strap_{k}", top, bot, 0.017)
    # the tin badge on the left breast: the thing the wanted poster pays for
    badge = Vector((front + 0.024, 0.085, s["shoulder_z"] - 0.085)) + up
    m.objects["badge"].location = badge
    m.put_segment("badge_pin", badge + Vector((0.008, 0, 0.026)), badge + Vector((0.010, 0, 0.050)), 0.010, 0.003)
    # three throwing knives tucked in the belts, handles up
    for i in range(3):
        u = 0.25 + 0.22 * i
        root = (Vector((front, 0.110, s["shoulder_z"] - 0.020)).lerp(Vector((front, -0.120, s["belt_z"] + 0.010)), u)) + up
        root.x += 0.018
        m.put_segment(f"tknife{i}", root + Vector((0, 0, -0.030)), root + Vector((0.004, 0.010, 0.050)), 0.010, 0.006)
    # the base's sword becomes a long knife (shorter), and a second knife goes in the left hand
    hand = a["hand_r"]
    fwd = Vector((0.75, -0.35, -0.10)).normalized()
    side = fwd.cross(Vector((0, 0, 1))).normalized()
    m.put_segment("blade", hand + fwd * 0.036, hand + fwd * 0.200, 0.018, 0.008)
    hand = a["hand_l"]
    fwd = Vector((0.75, 0.35, -0.10)).normalized()
    side = fwd.cross(Vector((0, 0, 1))).normalized()
    m.put_segment("grip2", hand - fwd * 0.040, hand + fwd * 0.030, 0.014)
    m.put_segment("guard2", hand + fwd * 0.032 - side * 0.040, hand + fwd * 0.032 + side * 0.040, 0.011)
    m.put_segment("blade2", hand + fwd * 0.036, hand + fwd * 0.200, 0.018, 0.008)
    _ = H
