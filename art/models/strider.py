"""Dust Strider (Floor 2, Highrest Highlands): a four-legged creature built on art/models/quadruped.py.

It wore the boar's sprite (ART_COUNT.md: wrong animal). It "kicks up sand from range" (gen_monsters.py): a long-
legged highland lizard that runs high off the ground.

Identity (art/QUADRUPED_RULES.md step 1):
  Coat:      dusty sand-ochre scales with dark brown bands across the back and tail (Tibia's lizards are green), a
             pale throat and belly.
  Signature: a row of rust-red spines down the neck and back (on top: seen from every direction), and a long banded
             tail held out straight behind.
  Attitude:  quick and wary: body held high on long legs, head up on a lifted neck, tail stiff.

Detail (art/DETAIL_RULES.md): a long wedge head with a mouth line and small yellow eyes under a brow ridge, no ears,
a throat pouch, long two-part legs with splayed clawed toes, the back bands, the spines in two sizes.
"""
from __future__ import annotations

import math

from mathutils import Vector

import quadruped as Q

NAME = "strider"
WALK_FRAMES = 8
PALETTE = "strider"
HEIGHT_SHEAR = 0.30
LEAN = 14.0
REFERENCE = None
SIZE = 1.58
GROUND_STRETCH = 1.3
AUTO_PLACE = (1, 1)
SIGNATURE = ["spine", "bandtail"]
CHECK = {"eye": 1}

PARTS = Q.PARTS + ["spine", "bandtail", "stripe", "line", "brow", "pouch"]
PIXEL_RULES = Q.pixel_rules(
    weight={"spine": 3.0, "bandtail": 2.4, "stripe": 1.8, "line": 3.2, "brow": 4.0, "pouch": 1.6, "eye": 9.0},
    thin={"spine": 2, "bandtail": 2, "line": 2, "brow": 2, "eye": 2},
    soft=[["body", "stripe", "belly", "pouch"], ["head", "line", "brow", "eye"], ["tail_base", "tail_tip", "bandtail"]],
    texture={"body": [1.2, 0.3], "head": [0.9, 0.2], "tail_base": [1.2, 0.3]},
    selout=["body"],
)

SPEC = Q.spec(
    hip=(-0.100, 0.270), hip_r=(0.100, 0.072, 0.060),
    chest=(0.050, 0.285), chest_r=(0.104, 0.074, 0.064),
    belly_r=(0.140, 0.058, 0.036), belly_drop=0.040,
    head=(0.230, 0.345), head_r=(0.090, 0.060, 0.044),              # up on a lifted neck
    snout_tip=(0.385, 0.322), snout_r=(0.042, 0.022),   # long and flat: a lizard, not a dog
    nose_r=(0.010, 0.012, 0.010),
    eye=(0.030, 0.044, 0.026), eye_r=0.011,
    ear_root=(-0.050, 0.030, 0.010), ear_tip=(-0.060, 0.034, 0.012), ear_r=0.006,   # no ears: a lizard
    front_x=0.080, hind_x=-0.125, leg_top_z=0.250,
    front_y=0.068, hind_y=0.066, front_feet_y=0.120, hind_feet_y=0.116,
    upper=0.140, lower=0.130, leg_r=0.020, paw_r=(0.032, 0.026, 0.010),
    shoulder_r=(0.044, 0.030, 0.050), haunch_r=(0.054, 0.032, 0.060),
    stride=0.130, lift=0.070, bob=0.010, nod=0.012,
    tail_len=0.310, tail_r=(0.034, 0.008), tail_raise=1.05, tail_curl=0.0, tail_split=0.85,
)
SPINES = 8
BANDS = 4


def build(model_cls, facing):
    m = Q.build(model_cls, facing, SPEC, PARTS)
    m.ellipsoid("neck", "body", radii=(0.060, 0.044, 0.060), segments=12, rings=8)
    m.ellipsoid("pouch", "pouch", radii=(0.040, 0.034, 0.026), segments=10, rings=6)
    for i in range(SPINES):
        m.cone(f"spine{i}", "spine", segments=5)
    for i in range(3):
        m.ellipsoid(f"stripe{i}", "stripe", radii=(0.024, 0.070, 0.050), segments=10, rings=6)
    for i in range(BANDS):
        m.ellipsoid(f"band{i}", "bandtail", radii=(0.016, 0.030, 0.026), segments=10, rings=6)
    for k in ("l", "r"):
        m.capsule(f"mouth_{k}", "line", segments=6)
        m.capsule(f"brow_{k}", "brow", segments=6)
    return m


def pose(m, t):
    p = Q.pose(m, t)
    chest, hip, head, tip = p["chest"], p["hip"], p["head"], p["snout_tip"]
    s = SPEC
    neck = chest.lerp(head, 0.5)
    m.objects["neck"].location = neck
    m.objects["pouch"].location = head + Vector((0.020, 0, -0.050))
    start, end = head + Vector((-0.050, 0, 0.040)), hip + Vector((-0.060, 0, s["hip_r"][2] * 0.85))
    for i in range(SPINES):
        u = i / (SPINES - 1)
        q = start.lerp(end, u) + Vector((0, 0, 0.010 * math.sin(math.pi * u)))
        h = 0.060 + 0.050 * math.sin(math.pi * u)            # tallest over the shoulders
        m.put_segment(f"spine{i}", q, q + Vector((-0.024, 0, h * 1.15)), 0.028, 0.0)
    mid = (chest + hip) / 2
    for i in range(3):
        m.objects[f"stripe{i}"].location = mid + Vector((0.080 - 0.080 * i, 0, s["chest_r"][2] * 0.80))
    pts = m.objects["tail_a"].data.splines[0].points
    n = len(pts)
    for i in range(BANDS):
        co = pts[int(n * (0.20 + 0.18 * i))].co
        o = m.objects[f"band{i}"]
        o.location = Vector((co[0], co[1], co[2] + 0.004))
        o.scale = (0.020, 0.044 * (1 - 0.18 * i), 0.042 * (1 - 0.18 * i))   # wider than the tail, or the tail hides them
    for sign, k in ((1, "l"), (-1, "r")):
        m.put_segment(f"mouth_{k}", head + Vector((0.040, 0.030 * sign, -0.018)), tip + Vector((-0.010, 0.016 * sign, -0.012)), 0.006)
        eye = m.objects[f"eye_{k}"].location
        m.put_segment(f"brow_{k}", eye + Vector((-0.020, 0.004 * sign, 0.014)), eye + Vector((0.018, -0.002 * sign, 0.014)), 0.008)


def assign_depth_parts(m, depth_of):
    Q.assign_depth_parts(m, depth_of)
