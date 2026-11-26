"""Ridge Cat (Floor 2, Highrest Highlands): a four-legged creature built on art/models/quadruped.py.

It wore the grey alpha's sprite (ART_COUNT.md: a wolf, wrong animal). It "pounces: a swipe that hits next to it"
(gen_monsters.py): a highland mountain cat.

Identity (art/QUADRUPED_RULES.md step 1):
  Coat:      dusty slate-tawny (Tibia's big cats are orange or striped), with rows of dark spots down the back and a
             pale cream muzzle, chest and belly.
  Signature: tall black tufts on the ear tips and a long tail ringed in dark bands with a black tip, both of which
             show from every direction (rule 8).
  Attitude:  stalking: low shoulders, head level and forward, long silent steps, the tail held out low behind.

Detail (art/DETAIL_RULES.md): round head with a short muzzle (a cat, not a dog), whisker pads, small amber eyes under
a brow line, ear tufts, heavy forepaws, shoulder blades rolling over the back; spots in two sizes; the tail rings.
"""
from __future__ import annotations

import math

from mathutils import Vector

import quadruped as Q

NAME = "ridgecat"
WALK_FRAMES = 8
PALETTE = "ridgecat"
HEIGHT_SHEAR = 0.30
LEAN = 14.0
REFERENCE = None
SIZE = 1.75
GROUND_STRETCH = 1.3
AUTO_PLACE = (1, 1)
SIGNATURE = ["eartuft", "ring"]
CHECK = {"eye": 1}

PARTS = Q.PARTS + ["spot", "pad", "eartuft", "ring", "brow"]
PIXEL_RULES = Q.pixel_rules(
    weight={"spot": 2.2, "pad": 1.6, "eartuft": 3.0, "ring": 2.4, "brow": 4.0, "eye": 9.0},
    thin={"spot": 2, "eartuft": 2, "ring": 2, "brow": 2, "eye": 2},
    soft=[["body", "spot", "belly"], ["head", "pad", "brow", "eye"], ["tail_base", "tail_tip", "ring"]],
    texture={"body": [0.9, 0.25], "head": [0.6, 0.15]},
    selout=["body"],
)

SPEC = Q.spec(
    hip=(-0.110, 0.268), hip_r=(0.112, 0.082, 0.072),
    chest=(0.045, 0.262), chest_r=(0.118, 0.090, 0.086),            # low shoulders: stalking
    belly_r=(0.160, 0.066, 0.040), belly_drop=0.050,
    head=(0.220, 0.272), head_r=(0.098, 0.094, 0.082),              # round head, level and forward
    snout_tip=(0.330, 0.248), snout_r=(0.044, 0.038), snout_blunt=True,
    nose_r=(0.014, 0.016, 0.012),
    eye=(0.054, 0.046, 0.028), eye_r=0.010,
    ear_root=(-0.020, 0.054, 0.058), ear_tip=(-0.026, 0.070, 0.140), ear_r=0.030,
    front_x=0.080, hind_x=-0.140, leg_top_z=0.232,
    front_y=0.062, hind_y=0.060, front_feet_y=0.094, hind_feet_y=0.088,
    upper=0.130, lower=0.120, leg_r=0.028, paw_r=(0.036, 0.026, 0.016),
    shoulder_r=(0.058, 0.036, 0.070), haunch_r=(0.064, 0.038, 0.074),
    stride=0.120, lift=0.050, bob=0.006, nod=0.006,
    tail_len=0.320, tail_r=(0.028, 0.022), tail_raise=0.95, tail_curl=0.10, tail_split=0.80,   # held up in a curve: seen from every side
)
SPOTS = [(0.08, 0.04), (0.02, -0.04), (-0.04, 0.04), (-0.10, -0.04), (-0.16, 0.03), (0.12, -0.02), (-0.06, 0.0)]
RINGS = 4


def build(model_cls, facing):
    m = Q.build(model_cls, facing, SPEC, PARTS)
    for i in range(len(SPOTS)):
        m.ellipsoid(f"spot{i}", "spot", radii=(0.022, 0.018, 0.010), segments=8, rings=5)
    for k in ("l", "r"):
        m.ellipsoid(f"pad_{k}", "pad", radii=(0.022, 0.020, 0.018), segments=8, rings=6)
        m.cone(f"eartuft_{k}", "eartuft", segments=5)
        m.capsule(f"brow_{k}", "brow", segments=6)
    for i in range(RINGS):
        m.ellipsoid(f"ring{i}", "ring", radii=(0.018, 0.032, 0.032), segments=10, rings=6)
    return m


def pose(m, t):
    p = Q.pose(m, t)
    chest, hip, head, tip = p["chest"], p["hip"], p["head"], p["snout_tip"]
    s = SPEC
    mid = (chest + hip) / 2
    for i, (x, y) in enumerate(SPOTS):
        m.objects[f"spot{i}"].location = mid + Vector((x, y, s["chest_r"][2] * 0.92 - abs(x) * 0.12))
    for sign, k in ((1, "l"), (-1, "r")):
        m.objects[f"pad_{k}"].location = tip + Vector((-0.020, 0.022 * sign, -0.006))
        r0, r1 = s["ear_root"], s["ear_tip"]
        ear_tip = head + Vector((r1[0], r1[1] * sign, r1[2]))
        m.put_segment(f"eartuft_{k}", ear_tip - Vector((0, 0, 0.010)), ear_tip + Vector((-0.006, 0.010 * sign, 0.075)), 0.020, 0.0)
        eye = m.objects[f"eye_{k}"].location
        m.put_segment(f"brow_{k}", eye + Vector((-0.024, 0.004 * sign, 0.018)), eye + Vector((0.020, -0.004 * sign, 0.012)), 0.008)
    pts = m.objects["tail_a"].data.splines[0].points
    n = len(pts)
    for i in range(RINGS):
        co = pts[int(n * (0.35 + 0.14 * i))].co
        m.objects[f"ring{i}"].location = Vector((co[0], co[1], co[2] + 0.004))


def assign_depth_parts(m, depth_of):
    Q.assign_depth_parts(m, depth_of)
