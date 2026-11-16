"""Mystic (player class outfit), built on art/models/humanoid.py.

ART_REQUESTS.md: "a nature mystic in pale green and white robes, leaf-shaped shoulder pieces, wooden beads".

Identity (art/OUTFIT_RULES.md step 1):
  Silhouette: a soft robe with two big leaves standing out from each shoulder, a tall wooden staff with a leafy
              crook in the right hand, a long braid down the back.
  Colours:    cream-white robe, a pale green overrobe, deep green leaves, warm brown wood and beads; honey hair.
  Details:    midribs on the leaves, a string of wooden beads across the chest, a leaf circlet in the hair,
              a green hem, sandals, a crystal bud glowing in the crook of the staff.
"""
from __future__ import annotations

import math

from mathutils import Euler, Vector

import humanoid as H

NAME = "mystic"
WALK_FRAMES = 8
PALETTE = "mystic"
REFERENCE = "outfit_136.png"
PROJECTION = "oblique"
CANVAS_OFFSET = H.CANVAS_OFFSET
SIGNATURE = ["leaf", "staff"]
HEAD_PARTS = ["skin", "hair", "strand", "eye", "brow", "nose"]
LEG_PARTS = ["boot_a", "boot_b", "sole"]
# a floor-length robe hides the legs: only the sandals show; a face turned away shows one eye pixel
CHECK = {"size": (0.85, 1.55), "head": 0.08, "legs_side": 0.0, "legs_updown": 0.0, "eye": 1}

PARTS = H.PARTS + ["robe", "over", "leaf", "rib", "bead", "staff", "bud", "circlet"]
PIXEL_RULES = H.pixel_rules(
    weight={"leaf": 1.8, "rib": 2.6, "bead": 5.0, "staff": 3.0, "bud": 5.0, "circlet": 3.0, "over": 1.3},
    thin={"rib": 2, "bead": 2, "staff": 2, "bud": 3, "circlet": 2},
    soft=[["robe", "over", "torso"], ["leaf", "rib"], ["staff", "bud"], ["hair", "circlet"]],
    texture={"robe": [0.3, 0.15], "over": [0.35, 0.15], "leaf": [0.4, 0.0], "staff": [0.5, 0.0]},
    selout=["robe", "over", "leaf"],
    no_outline=["bud"],
)

SPEC = H.spec(robe=("robe", "over", 0.105), torso_r=(0.094, 0.142, 0.182), arm_r=0.050, leg_r=0.044, stride=0.10, lift=0.045, bob=0.012,
              arm_swing=0.08, strands=(-1.2, -0.1, 1.0))
BEADS = 7
BRAID_N = 6


def build(model_cls, facing):
    m = H.build(model_cls, facing, SPEC, PARTS)
    m.ellipsoid("fringe", "hair", radii=(0.034, 0.084, 0.024), segments=12, rings=6)
    m.ellipsoid("backhair", "hair", radii=(0.055, 0.100, 0.110), segments=14, rings=10)
    m.tube("braid", "hair", points=BRAID_N)
    m.frustum("circlet", "circlet", top_ratio=1.0, segments=16)
    for side in ("f", "b"):
        m.box(f"over_{side}", "over", size=(0.030, 0.150, 0.330))
    m.ellipsoid("mantle", "over", radii=(0.105, 0.170, 0.050), segments=16, rings=8)
    for k in ("l", "r"):
        for j in range(2):
            m.ellipsoid(f"leaf{j}_{k}", "leaf", radii=(0.100, 0.046, 0.014), segments=12, rings=6)
            m.ellipsoid(f"rib{j}_{k}", "rib", radii=(0.094, 0.008, 0.018), segments=8, rings=6)
    for i in range(BEADS):
        m.ellipsoid(f"bead{i}", "bead", radii=(0.020, 0.020, 0.020), segments=8, rings=6)
    m.tube("staff", "staff", points=8)
    m.ellipsoid("bud", "bud", radii=(0.036, 0.036, 0.046), segments=10, rings=8)
    for j in range(2):
        m.ellipsoid(f"staffleaf{j}", "leaf", radii=(0.060, 0.026, 0.010), segments=10, rings=6)
    return m


def _staff_hand(sh, a, walking):
    swing = 0.04 * math.sin(a) if walking else 0.0
    return sh + Vector((0.110 + swing, -0.060, -0.230))


def pose(m, t):
    p = H.pose(m, t, hands={"r": _staff_hand})
    up, head, a, walking = p["up"], p["head"], p["a"], p["walking"]
    sway = 0.05 * math.sin(a) if walking else 0.0
    m.objects["fringe"].location = head + Vector((0.050, 0, 0.114))
    m.objects["backhair"].location = head + Vector((-0.100, 0, -0.050))
    swing = 0.040 * math.sin(a) if walking else 0.0
    pts = [head + Vector((-0.120 - 0.020 * math.sin(i * 0.6), swing * i / 5, -0.110 - 0.075 * i)) for i in range(BRAID_N)]
    m.set_tube("braid", [tuple(q) for q in pts], [0.036 - 0.004 * i for i in range(BRAID_N)])
    H.frustum(m, "circlet", head + Vector((-0.010, 0, 0.060)), (0.122, 0.118), 0.022, (0, -0.25, 0))
    step = 0.22 * abs(math.sin(a)) if walking else 0.0     # the green panels are pushed out by the striding legs
    for side, x, lean in (("f", 0.108, 0.10), ("b", -0.108, -0.10)):
        o = m.objects[f"over_{side}"]
        o.rotation_mode = "XYZ"
        o.rotation_euler = Euler((0, lean + (step if side == "f" else -step), 0))
        o.location = Vector((x * (1 + step), 0, 0.640)) + up
    m.objects["mantle"].location = Vector((0.0, 0, 0.848)) + up
    # two leaves fanning out and up from each shoulder
    flutter = 0.10 * math.sin(2 * a) if walking else 0.0
    for sign, k in ((1, "l"), (-1, "r")):
        sh = p[f"shoulder_{k}"]
        for j, (yaw, roll, dx) in enumerate(((1.25, 0.45, 0.030), (1.85, 0.30, -0.040))):
            rot = Euler((roll * sign + flutter * sign * (1 if j else -1), -0.35, yaw * sign))
            d = Vector((1, 0, 0))
            d.rotate(rot)
            for name in (f"leaf{j}_{k}", f"rib{j}_{k}"):
                o = m.objects[name]
                o.rotation_mode = "XYZ"
                o.rotation_euler = rot
                o.location = sh + Vector((dx, 0.020 * sign, 0.040)) + d * 0.078
    # wooden beads hanging in an arc across the chest
    for i in range(BEADS):
        u = i / (BEADS - 1)
        y = -0.105 + 0.210 * u
        z = 0.800 - 0.085 * math.sin(math.pi * u)
        x = 0.102 * math.sqrt(max(0.1, 1 - (y / 0.150) ** 2)) + 0.012
        m.objects[f"bead{i}"].location = Vector((x, y, z)) + up
    # staff: upright in the right hand, tilted out, its top curling into a crook that holds a glowing bud
    hand = p["hand_r"]
    foot = hand + Vector((0.030, -0.030, -0.400))
    top = hand + Vector((-0.060, -0.070, 0.520))
    pts = [foot, hand, hand.lerp(top, 0.5), top, top + Vector((0.050, 0, 0.070)), top + Vector((0.115, 0, 0.060)),
           top + Vector((0.140, 0, 0.000)), top + Vector((0.105, 0, -0.040))]
    m.set_tube("staff", [tuple(q) for q in pts], [0.020, 0.020, 0.019, 0.018, 0.017, 0.015, 0.013, 0.011])
    glow = 1.0 + (0.12 * math.sin(2 * a) if walking else 0.0)
    bud = m.objects["bud"]
    bud.location = top + Vector((0.075, 0, 0.010))
    bud.scale = (0.036 * glow, 0.036 * glow, 0.046 * glow)
    for j, sgn in enumerate((1, -1)):
        o = m.objects[f"staffleaf{j}"]
        o.rotation_mode = "XYZ"
        o.rotation_euler = Euler((0.4 * sgn, -0.6, 1.2 * sgn))
        o.location = top + Vector((0.010, 0.050 * sgn, 0.050))


def assign_depth_parts(m, depth_of):
    return None
