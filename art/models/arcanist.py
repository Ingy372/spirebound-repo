"""Arcanist (player class outfit), built on art/models/humanoid.py.

ART_REQUESTS.md: "a battle mage in deep red robes with gold trim and a high collar, glowing runes on the sleeves".

Identity (art/OUTFIT_RULES.md step 1):
  Silhouette: a long bell-shaped robe, wide sleeves, a tall flared collar behind the head, long dark hair down
              the back, a small ember burning over the raised right hand.
  Colours:    deep crimson robe, gold trim, pale glowing runes; black-brown hair.
  Details:    a gold hem, front seam and collar edge, a gold sash with a buckle, two glowing runes on each
              sleeve, gold cuffs, dark shoes peeking from under the hem.
"""
from __future__ import annotations

import math

from mathutils import Euler, Vector

import humanoid as H

NAME = "arcanist"
WALK_FRAMES = 8
PALETTE = "arcanist"
REFERENCE = "outfit_136.png"
PROJECTION = "oblique"
CANVAS_OFFSET = H.CANVAS_OFFSET
SIGNATURE = ["collar", "trim"]
HEAD_PARTS = ["skin", "hair", "strand", "eye", "brow", "nose"]
LEG_PARTS = ["boot_a", "boot_b", "sole"]
# a floor-length robe hides the legs: only the shoes show; a face turned away shows one eye pixel
CHECK = {"size": (0.85, 1.45), "head": 0.08, "legs_side": 0.0, "legs_updown": 0.0, "eye": 1}

PARTS = H.PARTS + ["robe", "trim", "collar", "rune", "ember"]
PIXEL_RULES = H.pixel_rules(
    weight={"trim": 2.6, "rune": 6.0, "ember": 4.0, "collar": 1.3},
    thin={"trim": 2, "rune": 2, "ember": 3},
    soft=[["robe", "trim", "torso"], ["collar", "trim"], ["arm_a", "rune"], ["arm_b", "rune"]],
    texture={"robe": [0.4, 0.22], "collar": [0.3, 0.1]},
    selout=["robe", "collar"],
    no_outline=["ember"],
)

SPEC = H.spec(robe=("robe", "trim", 0.105), torso_r=(0.096, 0.146, 0.182), arm_r=0.054, leg_r=0.044, stride=0.10, lift=0.045, bob=0.012,
              arm_swing=0.08, strands=(-1.3, -0.3, 0.8))


def build(model_cls, facing):
    m = H.build(model_cls, facing, SPEC, PARTS)
    m.ellipsoid("fringe", "hair", radii=(0.034, 0.084, 0.024), segments=12, rings=6)
    m.ellipsoid("backhair", "hair", radii=(0.060, 0.105, 0.175), segments=14, rings=10)   # long hair down the back
    for k in ("l", "r"):
        m.ellipsoid(f"lock_{k}", "hair", radii=(0.040, 0.030, 0.110), segments=10, rings=8)
        for j in range(2):
            m.ellipsoid(f"rune{j}_{k}", "rune", radii=(0.016, 0.016, 0.016), segments=8, rings=6)
    m.box("seam", "trim", size=(0.026, 0.040, 0.300))
    m.frustum("collar", "collar", top_ratio=1.45, segments=16)
    m.tube("collar_edge", "trim", points=7)
    m.ellipsoid("ember", "ember", radii=(0.040, 0.040, 0.050), segments=10, rings=8)
    m.cone("flame", "ember", segments=6)
    return m


def _cast_hand(sh, a, walking):
    return sh + Vector((0.170, -0.050, -0.130 + (0.012 * math.sin(2 * a) if walking else 0.0)))


def pose(m, t):
    p = H.pose(m, t, hands={"r": _cast_hand})
    up, head, a, walking = p["up"], p["head"], p["a"], p["walking"]
    sway = 0.05 * math.sin(a) if walking else 0.0
    m.objects["fringe"].location = head + Vector((0.050, 0, 0.114))
    m.objects["backhair"].location = head + Vector((-0.105, 0, -0.110))
    for sign, k in ((1, "l"), (-1, "r")):
        m.objects[f"lock_{k}"].location = head + Vector((0.010, 0.104 * sign, -0.060))
        elbow, d = p[f"elbow_{k}"], p[f"arm_dir_{k}"]
        out = Vector((0.0, sign, 0.2)).normalized() * 0.052
        for j in range(2):
            m.objects[f"rune{j}_{k}"].location = elbow + d * (0.040 + 0.065 * j) + out
    m.objects["seam"].location = Vector((0.100, 0, 0.700)) + up
    m.objects["seam"].rotation_mode = "XYZ"
    m.objects["seam"].rotation_euler = Euler((0, 0.0, 0))
    # a tall collar standing BEHIND the head (tilted well back, so it never rings the face)
    tilt = -0.55
    base = Vector((-0.060, 0, 0.850)) + up
    H.frustum(m, "collar", base, (0.070, 0.105), 0.170, (0, tilt, 0))
    # gold piping along the back half of the collar's top edge (a line, not a disc)
    pts = []
    for i in range(7):
        th = math.pi * (0.5 + i / 6)                       # from the left side, round the back, to the right side
        v = Vector((0.070 * 1.45 * math.cos(th), 0.105 * 1.45 * math.sin(th), 0.170))
        v.rotate(Euler((0, tilt, 0)))
        pts.append(tuple(base + v))
    m.set_tube("collar_edge", pts, [0.010] * 7)
    hand = p["hand_r"]
    flick = 0.012 * math.sin(4 * a) if walking else 0.0
    m.objects["ember"].location = hand + Vector((0.020, 0, 0.075))
    m.put_segment("flame", hand + Vector((0.020, 0, 0.095)), hand + Vector((0.020 + flick, flick, 0.200)), 0.030)


def assign_depth_parts(m, depth_of):
    return None
