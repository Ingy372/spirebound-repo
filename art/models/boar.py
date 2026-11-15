"""Bristle boar (Floor 1, Boar Meadow): a four-legged creature built on art/models/quadruped.py.

ART_REQUESTS.md: "a wild boar with dark bristly fur, short tusks, angry red eyes".

OUR boar (deliberately not Tibia's orange-brown boar): a charcoal-black brute with an ember-red crest of bristles
running from its brow to its rump, heavy ivory tusks that sweep out and up, a pale snout disc and burning
red eyes. Built to look like it is about to charge: head held low and thrust forward, a tall shoulder hump,
small hindquarters, ears pinned back, tail straight up with a red tuft.
"""
from __future__ import annotations

import math

from mathutils import Vector

import quadruped as Q

NAME = "boar"
WALK_FRAMES = 8
PALETTE = "boar"
HEIGHT_SHEAR = 0.30
LEAN = 14.0
REFERENCE = "look_380.png"   # Tibia's Boar, the closest look-alike (comparison only, never shipped)
SIZE = 2.0
GROUND_STRETCH = 1.0
AUTO_PLACE = (1, 1)
SIGNATURE = ["crest", "tusk"]     # what makes it OUR boar: must show from all four directions (check_creature.py)

PARTS = Q.PARTS + ["tusk", "crest", "brow"]
PIXEL_RULES = Q.pixel_rules(
    dark=True,
    bands=[0.38, 0.50, 0.60, 0.69, 0.78, 0.86, 0.93],
    weight={"tusk": 5.0, "crest": 2.4, "nose": 2.0, "brow": 4.0},
    thin={"tusk": 2, "crest": 3, "brow": 3},
    soft=[["head", "brow", "eye"]],
    texture={"crest": [0.5, 0.0]},
    selout=["crest"],
)

SPEC = Q.spec(
    hip=(-0.120, 0.250), hip_r=(0.112, 0.112, 0.098),
    chest=(0.050, 0.296), chest_r=(0.140, 0.136, 0.140),          # the shoulder hump: the tallest point
    belly_r=(0.165, 0.100, 0.060), belly_drop=0.075,
    head=(0.215, 0.226), head_r=(0.108, 0.106, 0.092),            # low and forward, under the hump
    snout_tip=(0.380, 0.172), snout_r=(0.060, 0.052), snout_blunt=True,
    nose_r=(0.020, 0.056, 0.050),                                 # the flat pale snout disc
    eye=(0.066, 0.086, 0.042), eye_r=0.017,
    ear_root=(-0.040, 0.068, 0.060), ear_tip=(-0.105, 0.105, 0.110), ear_r=0.028,   # pinned back
    front_x=0.075, hind_x=-0.135, leg_top_z=0.205,
    front_y=0.098, hind_y=0.086, front_feet_y=0.136, hind_feet_y=0.118,
    upper=0.112, lower=0.105, leg_r=0.037, paw_r=(0.038, 0.030, 0.020),
    shoulder_r=(0.066, 0.044, 0.090), haunch_r=(0.066, 0.042, 0.078),
    stride=0.100, lift=0.065, bob=0.012, nod=0.014,
    tail_len=0.150, tail_r=(0.016, 0.020), tail_raise=1.85, tail_curl=0.0, tail_split=0.55,
)
CREST = 10


def build(model_cls, facing):
    m = Q.build(model_cls, facing, SPEC, PARTS)
    for k in ("l", "r"):
        m.tube(f"tusk_{k}", "tusk", points=6)
    for i in range(CREST):
        m.cone(f"crest{i}", "crest", segments=6)
    for k in ("l", "r"):
        m.capsule(f"brow_{k}", "brow", segments=6)
    return m


def pose(m, t):
    p = Q.pose(m, t)
    head, chest, hip, tip = p["head"], p["chest"], p["hip"], p["snout_tip"]
    # tusks: out of the lower jaw, sweeping sideways and up past the snout (they show from every direction)
    for sign, k in ((1, "l"), (-1, "r")):
        root = tip + Vector((-0.050, 0.046 * sign, -0.034))
        pts, radii = [], []
        for i in range(6):
            u = i / 5
            pts.append(tuple(root + Vector((0.075 * math.sin(u * 1.7), sign * (0.070 * u), 0.105 * u * u))))
            radii.append(0.021 * (1 - 0.72 * u))
        m.set_tube(f"tusk_{k}", pts, radii)
    # heavy dark brows slanting down toward the snout: the scowl
    for sign, k in ((1, "l"), (-1, "r")):
        eye = m.objects[f"eye_{k}"].location
        m.put_segment(f"brow_{k}", eye + Vector((-0.040, 0.004 * sign, 0.034)), eye + Vector((0.034, -0.010 * sign, 0.014)), 0.013)
    # crest: ember bristles from the brow, over the hump, fading out at the rump; they flick as it trots
    brow = head + Vector((0.020, 0, SPEC["head_r"][2] * 0.92))
    hump = chest + Vector((-0.010, 0, SPEC["chest_r"][2] * 0.97))
    rump = hip + Vector((-0.020, 0, SPEC["hip_r"][2] * 0.95))
    for i in range(CREST):
        u = i / (CREST - 1)
        q = brow.lerp(hump, u / 0.42) if u < 0.42 else hump.lerp(rump, (u - 0.42) / 0.58)
        tall = (0.085 + 0.085 * math.sin(math.pi * min(1.0, u / 0.55) * 0.5)) * (1.0 - 0.55 * max(0.0, u - 0.45) / 0.55)
        tall *= 1.0 if i % 2 else 0.78
        flick = 0.012 * math.sin(p["a"] * 2 + i * 0.9) if p["walking"] else 0.0
        side = 0.014 * (1 if i % 2 else -1)
        m.put_segment(f"crest{i}", q - Vector((0, 0, 0.025)), q + Vector((-0.045 - flick, side, tall)), 0.030, 0.020)


def assign_depth_parts(m, depth_of):
    Q.assign_depth_parts(m, depth_of)
