"""Vanguard (player class outfit), built on art/models/humanoid.py.

ART_REQUESTS.md: "a sturdy armored sword knight in steel plate with a blue tabard and a kite shield, short
cape, helmetless with short hair".

Identity (art/OUTFIT_RULES.md step 1):
  Silhouette: broad: round pauldrons wider than the hips, a kite shield on the left arm, a longsword angled out
              from the right hand, a short cape.
  Colours:    polished steel, a royal-blue tabard and shield, gold trim; short chestnut hair.
  Details:    gold hem and chest emblem on the tabard, a gorget, knee cops, gauntlet cuffs, a shield rim and boss,
              a sword with crossguard and pommel, a belt with a gold buckle.
"""
from __future__ import annotations

import math

from mathutils import Euler, Vector

import humanoid as H

NAME = "vanguard"
WALK_FRAMES = 8
PALETTE = "vanguard"
REFERENCE = "outfit_128.png"
PROJECTION = "oblique"
CANVAS_OFFSET = H.CANVAS_OFFSET
SIGNATURE = ["pauldron", "tabard"]
HEAD_PARTS = ["skin", "hair", "strand", "eye", "brow", "nose"]
LEG_PARTS = ["leg_a", "leg_b", "boot_a", "boot_b", "knee"]
CHECK = {"size": (0.85, 1.45), "head": 0.08, "legs_side": 0.05, "eye": 1}   # gear adds to the measured size; a face turned away shows one eye pixel

PARTS = H.PARTS + ["tabard", "trim", "cape", "pauldron", "gorget", "knee", "shield", "rim", "blade", "hilt"]
PIXEL_RULES = H.pixel_rules(
    weight={"trim": 2.4, "pauldron": 1.5, "knee": 2.2, "rim": 2.0, "blade": 3.0, "hilt": 3.0, "gorget": 1.4},
    thin={"trim": 2, "knee": 3, "rim": 2, "blade": 2, "hilt": 2},
    soft=[["tabard", "trim"], ["shield", "rim"], ["blade", "hilt"], ["torso", "gorget"]],
    texture={"tabard": [0.35, 0.15], "cape": [0.4, 0.2], "shield": [0.3, 0.15]},
    selout=["tabard", "pauldron", "shield", "cape"],
)

SPEC = H.spec(torso_r=(0.108, 0.160, 0.188), arm_r=0.050, leg_r=0.054, shoulder_y=0.168,
              stride=0.12, lift=0.055, bob=0.018, strands=(-1.2, -0.2, 0.9))


def build(model_cls, facing):
    m = H.build(model_cls, facing, SPEC, PARTS)
    m.ellipsoid("fringe", "hair", radii=(0.036, 0.085, 0.024), segments=12, rings=6)
    m.ellipsoid("tuft", "hair", radii=(0.040, 0.046, 0.034), segments=10, rings=6)
    m.ellipsoid("nape", "hair", radii=(0.050, 0.090, 0.060), segments=12, rings=6)
    for side in ("f", "b"):
        m.box(f"tabard_{side}", "tabard", size=(0.030, 0.200, 0.430))
        m.box(f"hem_{side}", "trim", size=(0.034, 0.208, 0.036))
    m.box("emblem", "trim", size=(0.036, 0.070, 0.080))
    m.box("cape", "cape", size=(0.028, 0.250, 0.330))
    m.ellipsoid("gorget", "gorget", radii=(0.082, 0.115, 0.040), segments=14, rings=8)
    for k in ("l", "r"):
        m.ellipsoid(f"pauldron_{k}", "pauldron", radii=(0.094, 0.092, 0.070), segments=14, rings=8)
        m.ellipsoid(f"knee_{k}", "knee", radii=(0.048, 0.050, 0.046), segments=10, rings=6)
    m.ellipsoid("shield", "shield", radii=(0.125, 0.026, 0.165), segments=18, rings=10)
    m.ellipsoid("shield_rim", "rim", radii=(0.140, 0.010, 0.182), segments=18, rings=10)
    m.ellipsoid("boss", "rim", radii=(0.036, 0.030, 0.036), segments=10, rings=6)
    m.capsule("blade", "blade")
    m.capsule("guard", "hilt")
    m.capsule("grip", "hilt")
    m.ellipsoid("pommel", "hilt", radii=(0.020, 0.020, 0.020), segments=8, rings=6)
    return m


def _shield_hand(sh, a, walking):
    return sh + Vector((0.115, 0.045, -0.250))


def _sword_hand(sh, a, walking):
    swing = 0.09 * math.sin(a) if walking else 0.0
    return sh + Vector((swing + 0.040, -0.040, -0.315))


def pose(m, t):
    p = H.pose(m, t, hands={"l": _shield_hand, "r": _sword_hand})
    up, head, a, walking = p["up"], p["head"], p["a"], p["walking"]
    m.objects["fringe"].location = head + Vector((0.050, 0, 0.116))
    m.objects["tuft"].location = head + Vector((0.030, 0.034, 0.128))
    m.objects["nape"].location = head + Vector((-0.085, 0, -0.030))
    flap = 0.09 * math.sin(a) if walking else 0.0
    for side, x in (("f", 0.100), ("b", -0.100)):
        rot = Euler((0.0, flap if side == "f" else -flap, 0.0))
        for name, z, xs in ((f"tabard_{side}", 0.635, 1.0), (f"hem_{side}", 0.430, 1.03)):
            o = m.objects[name]
            o.rotation_mode = "XYZ"
            o.rotation_euler = rot
            o.location = Vector((x * xs, 0, z)) + up
    m.objects["emblem"].location = Vector((0.110, 0, 0.730)) + up
    cape = m.objects["cape"]
    cape.rotation_mode = "XYZ"
    cape.rotation_euler = Euler((0.0, 0.20 + (0.08 * abs(math.sin(a)) if walking else 0.0), 0.0))
    cape.location = Vector((-0.135, 0, 0.690)) + up
    m.objects["gorget"].location = Vector((0.010, 0, 0.858)) + up
    for sign, k in ((1, "l"), (-1, "r")):
        m.objects[f"pauldron_{k}"].location = p[f"shoulder_{k}"] + Vector((0.0, 0.022 * sign, 0.024))
        m.objects[f"knee_{k}"].location = p[f"knee_{k}"] + Vector((0.030, 0, 0.0))
    # kite shield strapped to the left forearm, face outward
    hand = p["hand_l"]
    centre = hand + Vector((-0.030, 0.050, 0.030))
    for name, dy in (("shield_rim", 0.0), ("shield", 0.0), ("boss", 0.024)):
        o = m.objects[name]
        o.rotation_mode = "XYZ"
        o.rotation_euler = Euler((0.0, 0.12, 0.22))
        o.location = centre + Vector((0, dy, 0.02 if name == "boss" else 0.0))
    # longsword in the right hand, angled forward and out so it never lies along the body's lean
    hand = p["hand_r"]
    fwd = Vector((0.62, -0.55, 0.56)).normalized()
    side = fwd.cross(Vector((0, 0, 1))).normalized()
    m.put_segment("grip", hand - fwd * 0.050, hand + fwd * 0.040, 0.015)
    m.objects["pommel"].location = hand - fwd * 0.062
    m.put_segment("guard", hand + fwd * 0.040 - side * 0.060, hand + fwd * 0.040 + side * 0.060, 0.014)
    m.put_segment("blade", hand + fwd * 0.045, hand + fwd * 0.400, 0.022, 0.010)


def assign_depth_parts(m, depth_of):
    return None
