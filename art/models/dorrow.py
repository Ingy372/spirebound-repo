"""Captain Dorrow (captain of Hearthgate's north gate, story quest giver), built on the Watch uniform (watchguard.py).

He wore Tibia's warrior outfit with its addons, an instantly recognisable Tibia look (Jay: "Redo any that stand
out"). The captain wears the watch's uniform with an officer's marks:
  Silhouette: bare-headed (no kettle helm: the guards wear those), a long red cape, gold shoulder boards, a sheathed
              sword at the left hip with his right hand resting on the hilt.
  Colours:    the watch's ember red and gold; grey hair and a thick grey moustache; a dark leather scabbard.
  Details:    gold shoulder boards with a fringe line, a gold cape clasp, the cape's hem, the scabbard's iron tip and
              the sword's gold crossguard, the hearth badge and quilting of the uniform.
Addons: none (an NPC, rule A1).
"""
from __future__ import annotations

import math

from mathutils import Euler, Vector

import addon_kit as K
import humanoid as H
import watchguard as B
from watchguard import WALK_FRAMES, REFERENCE, PROJECTION, CANVAS_OFFSET, assign_depth_parts  # noqa: F401

NAME = "dorrow"
PALETTE = "dorrow"
# literal values: check_creature.py reads these lines without importing the model
SIGNATURE = ["cape", "epaulette"]
HEAD_PARTS = ["skin", "hair", "strand", "eye", "brow", "nose"]
LEG_PARTS = ["leg_a", "leg_b", "boot_a", "boot_b"]
CHECK = {"size": (0.85, 1.45), "head": 0.08, "legs_side": 0.05, "eye": 1}
PARTS = B.PARTS + ["cape", "epaulette", "scabbard"]
PIXEL_RULES = {**B.PIXEL_RULES,
               "weight": {**B.PIXEL_RULES["weight"], "cape": 1.3, "epaulette": 3.0, "scabbard": 2.4},
               "thin": {**B.PIXEL_RULES["thin"], "epaulette": 2, "scabbard": 2},
               "soft": B.PIXEL_RULES["soft"] + [["cape", "hem"]],
               "texture": {**B.PIXEL_RULES["texture"], "cape": [0.4, 0.2]},
               "selout": B.PIXEL_RULES["selout"] + ["cape"]}
SPEC = H.spec(torso_r=(0.108, 0.160, 0.188), arm_r=0.052, leg_r=0.052, stride=0.11, lift=0.050, bob=0.014,
              strands=(-1.3, -0.4, 0.5, 1.3))
B.SPEC = SPEC                            # a broader, older man than the guard
HIDDEN = ["helm", "brim", "spear", "tip", "braid"]


def _hilt_hand(sh, a, walking):
    return sh + Vector((0.050, 0.120, -0.290))           # right hand across to the hilt at his left hip


B._spear_hand = _hilt_hand


def build(model_cls, facing):
    m = B.build(model_cls, facing)
    m.parts = PARTS                      # the base parts first, so their numbers do not change
    m.ellipsoid("stache", "hair", radii=(0.024, 0.070, 0.020), segments=10, rings=6)
    m.ellipsoid("nape_c", "hair", radii=(0.046, 0.090, 0.050), segments=12, rings=6)
    m.box("cape", "cape", size=(0.026, 0.270, 0.500))
    m.box("cape_hem", "hem", size=(0.030, 0.276, 0.026))
    m.ellipsoid("clasp", "badge", radii=(0.018, 0.018, 0.018), segments=8, rings=6)
    for k in ("l", "r"):
        m.box(f"epaulette_{k}", "epaulette", size=(0.090, 0.060, 0.024))
    m.capsule("scabbard", "scabbard")
    m.capsule("guard_x", "badge")
    m.capsule("grip_x", "scabbard")
    return m


def pose(m, t):
    B.pose(m, t)
    for name in HIDDEN:
        K.hide(m, name)
    a = K.anchors(m)
    up, head, s = a["up"], a["head"], m.spec
    m.objects["stache"].location = head + Vector((0.110, 0, -0.040))
    m.objects["nape_c"].location = head + Vector((-0.084, 0, -0.024))
    walk = t is not None
    tilt = 0.14 + (0.08 * abs(math.sin(2 * math.pi * t)) if walk else 0.0)
    for name, z in (("cape", 0.560), ("cape_hem", 0.318)):
        c = m.objects[name]
        c.rotation_mode = "XYZ"
        c.rotation_euler = Euler((0, tilt, 0))
        c.location = Vector((-0.150 - (0.820 - z) * math.sin(tilt) * 0.6, 0, z)) + up
    m.objects["clasp"].location = Vector((0.090, 0.0, 0.870)) + up
    for sign, k in ((1, "l"), (-1, "r")):
        m.objects[f"epaulette_{k}"].location = a[f"shoulder_{k}"] + Vector((0.0, 0.010 * sign, 0.048))
    hip = Vector((0.020, s["torso_r"][1] * 1.05, s["belt_z"] - 0.010)) + up
    d = Vector((-0.55, 0.10, -0.80)).normalized()          # hanging back and down from the left hip
    m.put_segment("scabbard", hip, hip + d * 0.320, 0.018, 0.014)
    m.put_segment("grip_x", hip, hip - d * 0.080, 0.012)
    side = d.cross(Vector((0, 0, 1))).normalized()
    m.put_segment("guard_x", hip - side * 0.040, hip + side * 0.040, 0.010)
