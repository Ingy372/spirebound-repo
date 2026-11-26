"""Horned Grazer (Floor 2, Highrest Highlands): a four-legged creature built on art/models/quadruped.py.

It wore the wolf's sprite (ART_COUNT.md: wrong animal). It "lowers its horns and charges" (gen_monsters.py): a
highland antelope.

Identity (art/QUADRUPED_RULES.md step 1):
  Coat:      warm sandy-fawn (Tibia's deer are red-brown) with a dark band along each flank, a white belly and a
             white rump patch, dark lower legs.
  Signature: long ridged lyre-shaped horns rising up and back from the head (on top: seen from every direction), and
             the white rump with a short black tail.
  Attitude:  alert, ready to charge: head held high, ears out sideways, light springy steps on long thin legs.

Detail (art/DETAIL_RULES.md): deep chest, slim waist, round haunches (three lumps), a long narrow face with a dark
nose and pale eye ring, horn ridges and pale tips, the flank band, two-part legs with small dark hooves.
"""
from __future__ import annotations

import math

from mathutils import Vector

import quadruped as Q

NAME = "grazer"
WALK_FRAMES = 8
PALETTE = "grazer"
HEIGHT_SHEAR = 0.30
LEAN = 14.0
REFERENCE = None
SIZE = 1.75
GROUND_STRETCH = 1.3
AUTO_PLACE = (1, 1)
SIGNATURE = ["horn", "rump"]
CHECK = {"eye": 1}

PARTS = Q.PARTS + ["horn", "ridge", "band", "rump", "ring"]
PIXEL_RULES = Q.pixel_rules(
    weight={"horn": 2.6, "ridge": 3.2, "band": 1.6, "rump": 1.8, "ring": 4.0, "eye": 9.0},
    thin={"horn": 2, "ridge": 2, "ring": 2, "eye": 2},
    soft=[["body", "band", "rump", "belly"], ["head", "ring", "eye"], ["horn", "ridge"]],
    texture={"body": [0.7, 0.2], "head": [0.5, 0.1], "horn": [1.3, 0.0]},
    selout=["horn", "body"],
)

SPEC = Q.spec(
    hip=(-0.110, 0.330), hip_r=(0.100, 0.078, 0.072),
    chest=(0.050, 0.345), chest_r=(0.104, 0.080, 0.084),
    belly_r=(0.140, 0.060, 0.040), belly_drop=0.050,
    head=(0.220, 0.420), head_r=(0.080, 0.068, 0.072),              # head high: alert
    snout_tip=(0.350, 0.388), snout_r=(0.040, 0.032),
    nose_r=(0.012, 0.016, 0.012),
    eye=(0.040, 0.046, 0.022), eye_r=0.011,
    ear_root=(-0.020, 0.044, 0.030), ear_tip=(-0.030, 0.110, 0.040), ear_r=0.020,   # ears out sideways
    front_x=0.075, hind_x=-0.130, leg_top_z=0.300,
    front_y=0.055, hind_y=0.052, front_feet_y=0.082, hind_feet_y=0.078,
    upper=0.170, lower=0.160, leg_r=0.018, paw_r=(0.020, 0.016, 0.012),
    shoulder_r=(0.050, 0.032, 0.070), haunch_r=(0.060, 0.034, 0.074),
    stride=0.120, lift=0.075, bob=0.016, nod=0.012,
    tail_len=0.070, tail_r=(0.016, 0.010), tail_raise=0.9, tail_curl=0.0, tail_split=0.5,
)
HORN_N = 10


def build(model_cls, facing):
    m = Q.build(model_cls, facing, SPEC, PARTS)
    m.ellipsoid("neck", "body", radii=(0.060, 0.050, 0.090), segments=12, rings=8)
    for k in ("l", "r"):
        m.tube(f"horn_{k}", "horn", points=HORN_N)
        for j in range(3):
            m.capsule(f"ridge{j}_{k}", "ridge", segments=6)
        m.ellipsoid(f"band_{k}", "band", radii=(0.120, 0.012, 0.022), segments=12, rings=6)
        m.ellipsoid(f"ring_{k}", "ring", radii=(0.008, 0.016, 0.014), segments=8, rings=4)
    m.ellipsoid("rump", "rump", radii=(0.060, 0.064, 0.060), segments=12, rings=8)
    return m


def pose(m, t):
    p = Q.pose(m, t)
    chest, hip, head = p["chest"], p["hip"], p["head"]
    s = SPEC
    m.objects["neck"].location = chest.lerp(head, 0.5)
    m.objects["rump"].location = hip + Vector((-0.070, 0, 0.010))
    for sign, k in ((1, "l"), (-1, "r")):
        root = head + Vector((-0.010, 0.026 * sign, 0.052))
        pts, radii = [], []
        for i in range(HORN_N):
            u = i / (HORN_N - 1)
            # lyre: up and back, spreading out, then the tips curving in and forward
            pts.append(root + Vector((-0.090 * u + 0.030 * u ** 3, sign * (0.030 * math.sin(u * math.pi) + 0.020 * u), 0.190 * u)))
            radii.append(0.016 * (1 - 0.70 * u) + 0.004)
        m.set_tube(f"horn_{k}", [tuple(q) for q in pts], radii)
        for j, u in enumerate((0.25, 0.45, 0.65)):
            c = pts[int(u * (HORN_N - 1))]
            m.put_segment(f"ridge{j}_{k}", c + Vector((0.006, -0.012, 0)), c + Vector((0.006, 0.012, 0)), 0.008)
        mid = (chest + hip) / 2
        m.objects[f"band_{k}"].location = mid + Vector((0.0, (s["chest_r"][1] * 0.95) * sign, -0.012))
        m.objects[f"ring_{k}"].location = m.objects[f"eye_{k}"].location + Vector((0, 0.004 * sign, 0.004))


def assign_depth_parts(m, depth_of):
    Q.assign_depth_parts(m, depth_of)
