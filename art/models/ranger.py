"""Ranger (player class outfit), built on art/models/humanoid.py.

ART_REQUESTS.md: "a nimble ranger in green leather and a hooded cloak, quiver on the back, bracers".

Identity (art/OUTFIT_RULES.md step 1):
  Silhouette: lean: a pointed hood, a short cloak behind, a longbow held upright at the left side, a quiver of
              arrows slanting over the right shoulder.
  Colours:    forest-green hood and cloak, a lighter moss-green jerkin, brown leather bracers, belt and boots,
              tan trousers; a sandy fringe of hair under the hood.
  Details:    pale arrow fletchings, a bowstring, a belt pouch and knife, boot cuffs, a gold cloak clasp.
"""
from __future__ import annotations

import math

from mathutils import Euler, Vector

import humanoid as H

NAME = "ranger"
WALK_FRAMES = 8
PALETTE = "ranger"
REFERENCE = "outfit_128.png"
PROJECTION = "oblique"
CANVAS_OFFSET = H.CANVAS_OFFSET
SIGNATURE = ["hood", "bow"]
HEAD_PARTS = ["skin", "hair", "strand", "eye", "brow", "nose", "hood"]
LEG_PARTS = ["leg_a", "leg_b", "boot_a", "boot_b"]
CHECK = {"size": (0.85, 1.45), "head": 0.08, "legs_side": 0.05, "eye": 1}   # gear adds to the measured size; a face turned away shows one eye pixel

PARTS = H.PARTS + ["hood", "cloak", "quiver", "fletch", "bow", "string", "pouch", "clasp"]
PIXEL_RULES = H.pixel_rules(
    weight={"hood": 1.3, "fletch": 4.0, "bow": 3.0, "string": 1.6, "pouch": 2.0, "clasp": 5.0, "quiver": 1.8},
    thin={"fletch": 2, "bow": 2, "string": 2, "pouch": 3, "clasp": 2},
    soft=[["hood", "cloak", "clasp"], ["bow", "string"], ["quiver", "fletch"], ["belt", "pouch"]],
    texture={"hood": [0.4, 0.2], "cloak": [0.45, 0.25], "quiver": [0.4, 0.0]},
    selout=["hood", "cloak"],
    no_outline=["string"],
)

SPEC = H.spec(torso_r=(0.094, 0.142, 0.182), arm_r=0.042, leg_r=0.046, cap=(-0.020, 0.010), cap_r=(0.110, 0.108, 0.100),
              stride=0.14, lift=0.065, bob=0.016, strands=(-0.6, 0.5))
ARROWS = 3


def build(model_cls, facing):
    m = H.build(model_cls, facing, SPEC, PARTS)
    m.ellipsoid("fringe", "hair", radii=(0.034, 0.080, 0.026), segments=12, rings=6)
    m.ellipsoid("hood", "hood", radii=(0.128, 0.130, 0.122), segments=18, rings=10)
    m.cone("hood_tip", "hood", segments=10)
    m.ellipsoid("mantle", "hood", radii=(0.120, 0.185, 0.060), segments=16, rings=8)      # the cloak over the shoulders
    m.box("cloak", "cloak", size=(0.030, 0.270, 0.400))
    m.ellipsoid("clasp", "clasp", radii=(0.016, 0.020, 0.020), segments=8, rings=6)
    m.capsule("quiver", "quiver", segments=10)
    for i in range(ARROWS):
        m.cone(f"fletch{i}", "fletch", segments=5)
    m.tube("bow", "bow", points=9)
    m.capsule("string", "string", segments=5)
    m.ellipsoid("pouch", "pouch", radii=(0.040, 0.030, 0.044), segments=10, rings=6)
    m.capsule("knife", "pouch", segments=6)
    return m


def _bow_hand(sh, a, walking):
    swing = 0.05 * math.sin(a + math.pi) if walking else 0.0
    return sh + Vector((0.100 + swing, 0.070, -0.270))


def pose(m, t):
    p = H.pose(m, t, hands={"l": _bow_hand})
    up, head, a, walking = p["up"], p["head"], p["a"], p["walking"]
    m.objects["fringe"].location = head + Vector((0.066, 0, 0.088))
    m.objects["hood"].location = head + Vector((-0.050, 0, 0.022))
    m.put_segment("hood_tip", head + Vector((-0.110, 0, 0.070)), head + Vector((-0.225, 0, -0.010)), 0.070, 0.085)
    m.objects["mantle"].location = Vector((-0.012, 0, 0.850)) + up
    cloak = m.objects["cloak"]
    cloak.rotation_mode = "XYZ"
    cloak.rotation_euler = Euler((0.06 * math.sin(a) if walking else 0.0, 0.16 + (0.10 * abs(math.sin(a)) if walking else 0.0), 0.0))
    cloak.location = Vector((-0.125, 0, 0.660)) + up
    m.objects["clasp"].location = Vector((0.092, 0, 0.862)) + up
    # quiver slanting across the back, arrows over the right shoulder
    q0 = Vector((-0.125, 0.070, 0.560)) + up
    q1 = Vector((-0.125, -0.085, 0.900)) + up
    m.put_segment("quiver", q0, q1, 0.046)
    axis = (q1 - q0).normalized()
    for i in range(ARROWS):
        base = q1 + Vector((0.016 * (i - 1), 0.022 * (i - 1), 0.0))
        m.put_segment(f"fletch{i}", base + axis * 0.110, base + axis * 0.010, 0.026, 0.012)
    # longbow held upright in the left hand, a little forward and out from the body
    hand = p["hand_l"]
    lo, hi = hand + Vector((0.020, 0.030, -0.330)), hand + Vector((-0.040, 0.050, 0.420))
    pts, radii = [], []
    for i in range(9):
        u = i / 8
        pts.append(tuple(lo.lerp(hi, u) + Vector((0.085 * math.sin(math.pi * u), 0, 0))))
        radii.append(0.016 if 0.2 < u < 0.8 else 0.011)
    m.set_tube("bow", pts, radii)
    m.put_segment("string", lo, hi, 0.005)
    m.objects["pouch"].location = Vector((0.050, -0.150, 0.520)) + up
    m.put_segment("knife", Vector((-0.020, -0.160, 0.560)) + up, Vector((-0.060, -0.170, 0.440)) + up, 0.016)


def assign_depth_parts(m, depth_of):
    return None
