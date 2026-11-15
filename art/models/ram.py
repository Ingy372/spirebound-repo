"""Stonehorn ram (Floor 1, the Old Quarry): a four-legged creature built on art/models/quadruped.py.

ART_REQUESTS.md: "a mountain ram with huge curled stone-grey horns and thick wool".

Identity (art/QUADRUPED_RULES.md step 1):
  Coat:      a thick russet-red fleece (Tibia's sheep is white) in lumpy tufts, with a charcoal face and
             legs.
  Signature: two massive ridged horns of pale weathered stone that curl back, down and forward round the face,
             big enough to show from every direction.
  Attitude:  ready to butt: head lowered so the horns lead, heavy chest, short stamping steps.
"""
from __future__ import annotations

import math

from mathutils import Vector

import quadruped as Q

NAME = "ram"
WALK_FRAMES = 8
PALETTE = "ram"
HEIGHT_SHEAR = 0.30
LEAN = 14.0
REFERENCE = "look_14.png"     # Tibia's Sheep (comparison only, never shipped)
SIZE = 1.65
GROUND_STRETCH = 1.0
AUTO_PLACE = (1, 1)
SIGNATURE = ["horn"]
CHECK = {"size": (0.95, 1.45), "legs_updown": 0.025}   # a mountain ram is meant to be bigger than Tibia's sheep

PARTS = Q.PARTS + ["horn", "wool"]
PIXEL_RULES = Q.pixel_rules(
    weight={"horn": 2.4, "wool": 1.2},
    thin={"horn": 3},
    soft=[["body", "wool", "belly"]],
    texture={"body": [0.6, 0.45], "wool": [0.6, 0.45], "horn": [1.3, 0.0]},
    selout=["horn", "wool"],
)

SPEC = Q.spec(
    hip=(-0.110, 0.255), hip_r=(0.125, 0.115, 0.105),
    chest=(0.045, 0.270), chest_r=(0.130, 0.120, 0.115),
    belly_r=(0.165, 0.105, 0.060), belly_drop=0.060,
    head=(0.250, 0.250), head_r=(0.084, 0.072, 0.082),              # lowered: horns lead
    snout_tip=(0.385, 0.198), snout_r=(0.050, 0.040), snout_blunt=True,
    nose_r=(0.014, 0.022, 0.014),
    eye=(0.050, 0.052, 0.030), eye_r=0.015,
    ear_root=(-0.010, 0.050, 0.010), ear_tip=(-0.010, 0.110, -0.010), ear_r=0.018,   # ears out sideways
    front_x=0.080, hind_x=-0.140, leg_top_z=0.210,
    front_y=0.075, hind_y=0.070, front_feet_y=0.115, hind_feet_y=0.105,
    upper=0.110, lower=0.105, leg_r=0.024, paw_r=(0.028, 0.020, 0.016),
    shoulder_r=(0.050, 0.040, 0.060), haunch_r=(0.055, 0.040, 0.060),
    stride=0.085, lift=0.060, bob=0.012, nod=0.016,
    tail_len=0.070, tail_r=(0.030, 0.022), tail_raise=0.5, tail_curl=0.0, tail_split=0.6,
)
# fleece tufts: (x, side, z) around the body, so the outline is lumpy like real wool
TUFTS = [(0.10, 0.0, 0.10), (-0.02, 0.0, 0.11), (-0.14, 0.0, 0.10), (0.06, 0.10, 0.04), (0.06, -0.10, 0.04),
         (-0.10, 0.10, 0.04), (-0.10, -0.10, 0.04), (0.09, 0.06, 0.09), (0.09, -0.06, 0.09), (-0.22, 0.0, 0.04)]
HORN_N = 14


def build(model_cls, facing):
    m = Q.build(model_cls, facing, SPEC, PARTS)
    for i in range(len(TUFTS)):
        m.ellipsoid(f"tuft{i}", "wool", radii=(0.060, 0.058, 0.052), segments=12, rings=8)
    for k in ("l", "r"):
        m.tube(f"horn_{k}", "horn", points=HORN_N)
    return m


def pose(m, t):
    p = Q.pose(m, t)
    chest, hip, head = p["chest"], p["hip"], p["head"]
    mid = (chest + hip) / 2
    for i, (x, y, z) in enumerate(TUFTS):
        wob = 0.006 * math.sin(p["a"] * 2 + i) if p["walking"] else 0.0
        m.objects[f"tuft{i}"].location = mid + Vector((x, y, z + wob))
    # horns: a thick ridged spiral from the top of the head, back, down round the ear and forward past the cheek
    for sign, k in ((1, "l"), (-1, "r")):
        root = head + Vector((-0.030, 0.046 * sign, 0.058))
        pts, radii = [], []
        for i in range(HORN_N):
            u = i / (HORN_N - 1)
            ang = 1.55 * math.pi * u
            r = 0.100 * (1 - 0.42 * u)
            pts.append(tuple(root + Vector((-r * math.sin(ang), sign * (0.040 + 0.085 * u), r * (1 - math.cos(ang)) * -0.85 + 0.020))))
            radii.append(0.030 * (1 - 0.72 * u) + 0.007)
        m.set_tube(f"horn_{k}", pts, radii)


def assign_depth_parts(m, depth_of):
    Q.assign_depth_parts(m, depth_of)
