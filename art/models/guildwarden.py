"""Guild Warden (Hearthgate guild hall, town NPC), built on art/models/humanoid.py (second draft, 2026-11-25).

ART_REQUESTS.md: "a guild official in blue robes holding a banner staff".
The first draft (2026-11-15) was the priest's old body recoloured; this one follows art/OUTFIT_RULES.md.

Identity (art/OUTFIT_RULES.md step 1):
  Silhouette: a long robe, a tall staff held upright out at the left side with a crossbar and a square banner
              hanging from it (no other person carries a flag: rule O14), a short neat beard.
  Colours:    deep navy robe, silver stole and hem, a gold guild badge; the banner navy with a gold border.
  Details:    silver stole down the front (two strips), silver hem, gold badge on the chest, a sash belt with a
              silver buckle, cuffs, the banner's gold border and a gold tower emblem, a gold finial on the staff,
              the staff's iron shoe at the foot.
Addons: none (an NPC, rule A1).
"""
from __future__ import annotations

import math

from mathutils import Euler, Vector

import humanoid as H

NAME = "guildwarden"
WALK_FRAMES = 8
PALETTE = "guildwarden"
REFERENCE = "outfit_128.png"
PROJECTION = "oblique"
CANVAS_OFFSET = H.CANVAS_OFFSET
SIGNATURE = ["banner", "robe"]
HEAD_PARTS = ["skin", "hair", "strand", "eye", "brow", "nose", "beard"]
LEG_PARTS = ["boot_a", "boot_b", "sole"]
CHECK = {"size": (0.85, 1.55), "head": 0.08, "legs_side": 0.0, "legs_updown": 0.0, "eye": 1}   # robe: no legs (O10)

PARTS = H.PARTS + ["robe", "trim", "stole", "badge", "beard", "staff", "finial", "banner", "border"]
PIXEL_RULES = H.pixel_rules(
    weight={"trim": 2.4, "stole": 2.0, "badge": 5.0, "beard": 1.4, "staff": 3.0, "finial": 4.0, "banner": 1.6,
            "border": 2.6},
    thin={"trim": 2, "stole": 3, "badge": 2, "staff": 2, "finial": 2, "border": 2},
    soft=[["robe", "trim", "torso", "stole", "badge"], ["skin", "beard"], ["banner", "border"], ["staff", "finial"]],
    texture={"robe": [0.4, 0.2], "banner": [0.35, 0.15], "beard": [0.35, 0.15]},
    selout=["robe", "banner"],
)

SPEC = H.spec(robe=("robe", "trim", 0.108), torso_r=(0.098, 0.150, 0.184), arm_r=0.052, leg_r=0.044, stride=0.10,
              lift=0.045, bob=0.012, arm_swing=0.08, strands=(-1.4, -0.6, 0.2, 1.0))


def build(model_cls, facing):
    m = H.build(model_cls, facing, SPEC, PARTS)
    m.ellipsoid("fringe", "hair", radii=(0.032, 0.080, 0.020), segments=12, rings=6)
    m.ellipsoid("nape", "hair", radii=(0.046, 0.090, 0.050), segments=12, rings=6)
    m.ellipsoid("beard", "beard", radii=(0.052, 0.074, 0.044), segments=12, rings=8)
    for k in ("l", "r"):
        m.box(f"stole_{k}", "stole", size=(0.026, 0.036, 0.420))
    m.ellipsoid("badge", "badge", radii=(0.020, 0.030, 0.030), segments=10, rings=6)
    m.ellipsoid("mantle", "stole", radii=(0.100, 0.165, 0.044), segments=16, rings=8)
    m.capsule("staff", "staff")
    m.capsule("crossbar", "staff")
    m.ellipsoid("finial", "finial", radii=(0.026, 0.026, 0.036), segments=10, rings=6)
    m.capsule("shoe", "finial")
    m.box("banner", "banner", size=(0.020, 0.150, 0.190))
    m.box("border_b", "border", size=(0.024, 0.156, 0.022))
    m.box("emblem", "border", size=(0.024, 0.040, 0.070))
    return m


def _staff_hand(sh, a, walking):
    swing = 0.03 * math.sin(a) if walking else 0.0
    return sh + Vector((0.090 + swing, 0.070, -0.240))


def pose(m, t):
    p = H.pose(m, t, hands={"l": _staff_hand})
    up, head, a, walking = p["up"], p["head"], p["a"], p["walking"]
    m.objects["fringe"].location = head + Vector((0.050, 0, 0.112))
    m.objects["nape"].location = head + Vector((-0.084, 0, -0.024))
    m.objects["beard"].location = head + Vector((0.072, 0, -0.070))
    for sign, k in ((1, "l"), (-1, "r")):
        o = m.objects[f"stole_{k}"]
        o.rotation_mode = "XYZ"
        o.rotation_euler = Euler((0, 0.08, 0))
        o.location = Vector((0.104, 0.050 * sign, 0.640)) + up
    m.objects["mantle"].location = Vector((0.0, 0, 0.850)) + up
    m.objects["badge"].location = Vector((0.110, 0.0, 0.770)) + up
    # banner staff: upright, out at the left side, leaning a little forward-out so it is its own shape (O5)
    hand = p["hand_l"]
    d = Vector((0.12, 0.10, 1.0)).normalized()
    foot, top = hand - d * 0.390, hand + d * 0.560
    m.put_segment("staff", foot, top, 0.016)
    m.put_segment("shoe", foot, foot + d * 0.040, 0.019)
    m.objects["finial"].location = top + d * 0.030
    bar = top - d * 0.050
    side = Vector((0, 1, 0))
    m.put_segment("crossbar", bar - side * 0.080, bar + side * 0.080, 0.011)
    sway = 0.10 * math.sin(a) if walking else 0.0         # the cloth swings a little behind the step
    for name, dz in (("banner", -0.105), ("border_b", -0.205), ("emblem", -0.090)):
        o = m.objects[name]
        o.rotation_mode = "XYZ"
        o.rotation_euler = Euler((0, sway, 0))
        o.location = bar + Vector((0.004 if name == "emblem" else 0.0, 0, dz))


def assign_depth_parts(m, depth_of):
    return None
