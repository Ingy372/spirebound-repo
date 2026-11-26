"""Herd Bull (Floor 2 elite, Highrest Highlands): a four-legged creature built on art/models/quadruped.py.

It wore the toad's sprite (ART_COUNT.md: wrong animal). The highland herd's bull.

Identity (art/QUADRUPED_RULES.md step 1):
  Coat:      shaggy dark russet-black (Tibia's bulls and buffalo are brown or grey) with a lighter tawny mane over a
             tall shoulder hump, and pale lower legs.
  Signature: wide pale horns that sweep OUT sideways and curve forward (rule 8: sticking out sideways shows from every
             direction), and a shaggy tawny mane on the hump.
  Attitude:  about to charge: head low below the hump, horns leading, heavy shoulders, short tail swishing.

Detail (art/DETAIL_RULES.md): a hump, heavy chest and lighter hindquarters (three lumps), a broad blunt muzzle with
nostrils, small dark eyes under a heavy brow, a dewlap, two-part legs with cloven hooves, horn ridges and pale tips.
"""
from __future__ import annotations

import math

from mathutils import Vector

import quadruped as Q

NAME = "bull"
WALK_FRAMES = 8
PALETTE = "bull"
HEIGHT_SHEAR = 0.30
LEAN = 14.0
REFERENCE = None
SIZE = 1.95
GROUND_STRETCH = 1.25
AUTO_PLACE = (1, 1)
SIGNATURE = ["horn", "mane"]
CHECK = {"size": (0.95, 1.6), "eye": 1}   # an elite bull is meant to be big

PARTS = Q.PARTS + ["horn", "mane", "hump", "brow", "hoof"]
PIXEL_RULES = Q.pixel_rules(
    dark=True,
    weight={"horn": 2.6, "mane": 1.4, "hump": 1.2, "brow": 4.0, "hoof": 2.6, "eye": 9.0},
    thin={"horn": 2, "brow": 2, "hoof": 2, "eye": 2},
    soft=[["body", "hump", "mane", "belly"], ["head", "brow", "eye"]],
    texture={"body": [0.8, 0.3], "mane": [1.0, 0.4], "hump": [0.8, 0.3], "horn": [1.2, 0.0]},
    selout=["mane", "horn"],
)

SPEC = Q.spec(
    hip=(-0.120, 0.270), hip_r=(0.120, 0.100, 0.090),
    chest=(0.050, 0.300), chest_r=(0.140, 0.122, 0.118),
    belly_r=(0.170, 0.090, 0.060), belly_drop=0.060,
    head=(0.240, 0.235), head_r=(0.100, 0.090, 0.088),              # low, below the hump
    snout_tip=(0.375, 0.190), snout_r=(0.064, 0.056), snout_blunt=True,
    nose_r=(0.020, 0.036, 0.018),
    eye=(0.044, 0.060, 0.030), eye_r=0.012,
    ear_root=(-0.020, 0.070, 0.020), ear_tip=(-0.030, 0.120, 0.010), ear_r=0.022,
    front_x=0.085, hind_x=-0.145, leg_top_z=0.220,
    front_y=0.080, hind_y=0.075, front_feet_y=0.118, hind_feet_y=0.110,
    upper=0.115, lower=0.110, leg_r=0.032, paw_r=(0.034, 0.026, 0.018),
    shoulder_r=(0.066, 0.046, 0.080), haunch_r=(0.066, 0.044, 0.076),
    stride=0.090, lift=0.055, bob=0.012, nod=0.018,
    tail_len=0.160, tail_r=(0.018, 0.016), tail_raise=0.25, tail_curl=0.0, tail_split=0.7,
)
HORN_N = 9


def build(model_cls, facing):
    m = Q.build(model_cls, facing, SPEC, PARTS)
    m.ellipsoid("hump", "hump", radii=(0.110, 0.100, 0.080), segments=16, rings=8)
    for i in range(4):
        m.ellipsoid(f"mane{i}", "mane", radii=(0.060, 0.070, 0.040), segments=12, rings=6)
    for k in ("l", "r"):
        m.tube(f"horn_{k}", "horn", points=HORN_N)
        m.capsule(f"brow_{k}", "brow", segments=6)
    return m


def pose(m, t):
    p = Q.pose(m, t)
    chest, head = p["chest"], p["head"]
    m.objects["hump"].location = chest + Vector((0.010, 0, 0.100))
    for i in range(4):
        wob = 0.006 * math.sin(p["a"] * 2 + i) if p["walking"] else 0.0
        m.objects[f"mane{i}"].location = chest + Vector((0.060 - 0.050 * i, 0.016 * (1 if i % 2 else -1), 0.150 - 0.010 * i + wob))
    for sign, k in ((1, "l"), (-1, "r")):
        root = head + Vector((-0.010, 0.060 * sign, 0.050))
        pts, radii = [], []
        for i in range(HORN_N):
            u = i / (HORN_N - 1)
            pts.append(tuple(root + Vector((0.030 * u, sign * (0.100 * u), 0.010 + 0.070 * u * u))))   # out, then up at the tip: long forward horns read as tusks
            radii.append(0.020 * (1 - 0.75 * u) + 0.004)
        m.set_tube(f"horn_{k}", pts, radii)
        eye = m.objects[f"eye_{k}"].location
        m.put_segment(f"brow_{k}", eye + Vector((-0.026, 0.004 * sign, 0.020)), eye + Vector((0.026, -0.004 * sign, 0.010)), 0.010)


def assign_depth_parts(m, depth_of):
    Q.assign_depth_parts(m, depth_of)
