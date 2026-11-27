"""Acorn Squirrel (Floor 1 small game on the empty lawns, Q94): a four-legged creature built on art/models/quadruped.py.
Harmless and the quickest thing on the lawns; it carries an acorn everywhere.

Identity (art/QUADRUPED_RULES.md step 1):
  Coat:      dusky ash-grey with a cream belly (Tibia's squirrel is red-brown with a pale tail), a russet stripe along
             each flank.
  Signature: a huge charcoal brush of a tail curled up over its back, frosted russet at the end (seen from every
             direction), russet ear tufts, and a golden acorn held in its mouth.
  Attitude:  twitchy and quick: hunched with the haunches gathered, the tail high, the head up, always about to dash.

Detail (art/DETAIL_RULES.md): a tree squirrel's anatomy: a big bushy tail as long as the body, a round head with
small tufted ears, big black eyes, a short blunt muzzle, strong hind legs with long feet, small front paws, a pale
belly. Marks: big = the dark tail; medium = the russet flank stripe and cream belly; small = the ear tufts, the acorn
and its cap.
Real proportion: a grey squirrel's tail is about as long as its head and body together; sitting, the hind legs fold
under it and the body is half again as tall as it is long.
"""
from __future__ import annotations

import math

from mathutils import Vector

import quadruped as Q

NAME = "acorn_squirrel"
WALK_FRAMES = 8
PALETTE = "acorn_squirrel"
HEIGHT_SHEAR = 0.30
LEAN = 12.0
REFERENCE = "look_274.png"   # Tibia's Squirrel (comparison only, never shipped)
SIZE = 1.38
GROUND_STRETCH = 1.0
AUTO_PLACE = (1, 1)
SIGNATURE = ["tail_base", "tail_tip"]
CHECK = {"eye": 1, "signature": 3, "legs_updown": 0.02, "head": 0.08}   # a tiny animal under a big tail
HEAD_PARTS = ["head", "snout", "nose", "ear", "tuft", "eye", "acorn", "cap"]

PARTS = Q.PARTS + ["tuft", "acorn", "cap", "stripe", "line"]
PIXEL_RULES = Q.pixel_rules(
    weight={"tuft": 4.0, "acorn": 4.5, "cap": 4.5, "stripe": 2.0, "line": 3.0, "tail_base": 1.3, "tail_tip": 2.2,
            "eye": 9.0},
    thin={"tuft": 2, "acorn": 2, "cap": 2, "stripe": 2, "line": 2},
    soft=[["body", "belly", "stripe"], ["head", "snout", "nose", "line", "eye"], ["ear", "tuft"], ["acorn", "cap"]],
    texture={"body": [0.6, 0.15], "tail_base": [1.0, 0.35], "tail_tip": [0.9, 0.3]},
    selout=["tail_base", "tail_tip"],
)
PIXEL_RULES["fur"] = ["body", "head", "tail_base", "tail_tip"]

SPEC = Q.spec(
    hip=(-0.080, 0.170), hip_r=(0.090, 0.075, 0.085),
    chest=(0.040, 0.185), chest_r=(0.070, 0.060, 0.075),
    belly_r=(0.100, 0.052, 0.040), belly_drop=0.040,
    head=(0.120, 0.245), head_r=(0.058, 0.052, 0.054),
    snout_tip=(0.195, 0.228), snout_r=(0.032, 0.024), snout_blunt=True,
    nose_r=(0.010, 0.012, 0.010),
    eye=(0.020, 0.040, 0.016), eye_r=0.013,
    ear_root=(-0.020, 0.030, 0.040), ear_tip=(-0.026, 0.040, 0.085), ear_r=0.016,
    front_x=0.055, hind_x=-0.090, leg_top_z=0.130,
    front_y=0.042, hind_y=0.060, front_feet_y=0.058, hind_feet_y=0.080,
    upper=0.072, lower=0.070, leg_r=0.014, paw_r=(0.020, 0.014, 0.011),
    shoulder_r=(0.032, 0.026, 0.050), haunch_r=(0.064, 0.036, 0.066),
    stride=0.075, lift=0.060, bob=0.026, nod=0.014,
    tail_len=0.060, tail_r=(0.012, 0.010), tail_raise=2.0, tail_curl=0.0, tail_split=0.80,
)

BRUSH = 8


def build(model_cls, facing):
    m = Q.build(model_cls, facing, SPEC, PARTS)
    m.ellipsoid("acorn", "acorn", radii=(0.020, 0.018, 0.024), segments=10, rings=6)
    m.ellipsoid("cap", "cap", radii=(0.020, 0.020, 0.010), segments=10, rings=4)
    m.capsule("mouth", "line", segments=6)
    for i in range(BRUSH):
        m.ellipsoid(f"brush{i}", "tail_tip" if i >= BRUSH - 2 else "tail_base", radii=(1, 1, 1), segments=12, rings=8)
    for k in ("l", "r"):
        m.cone(f"tuft_{k}", "tuft", segments=6)
        m.ellipsoid(f"stripe_{k}", "stripe", radii=(0.080, 0.012, 0.012), segments=10, rings=4)
    return m


def pose(m, t):
    p = Q.pose(m, t)
    head, hip, chest = p["head"], p["hip"], p["chest"]
    tip = p["snout_tip"]
    m.objects["acorn"].location = tip + Vector((0.014, 0, -0.026))
    m.objects["cap"].location = tip + Vector((0.014, 0, -0.006))
    m.put_segment("mouth", tip + Vector((-0.016, 0.016, -0.018)), tip + Vector((-0.016, -0.016, -0.018)), 0.004)
    for sign, k in ((1, "l"), (-1, "r")):
        r1 = SPEC["ear_tip"]
        end = head + Vector((r1[0], r1[1] * sign, r1[2]))
        m.put_segment(f"tuft_{k}", end - Vector((0, 0, 0.012)), end + Vector((-0.010, 0.008 * sign, 0.034)), 0.012, 0.003)
        s = m.objects[f"stripe_{k}"]
        s.location = hip.lerp(chest, 0.5) + Vector((0, (SPEC["hip_r"][1] * 0.92) * sign, 0.010))
    # the brush: Q's upright tail, then curled forward over the back at the top
    # the brush: a curve up from the rump and forward over the back, built of overlapping tufts (never one sausage)
    base = hip + Vector((-SPEC["hip_r"][0] * 0.85, 0, SPEC["hip_r"][2] * 0.10))
    flick = 0.020 * math.sin(p["a"] * 2 + 0.8) if p["walking"] else 0.0
    curve = lambda u: base + Vector((-0.30 * u * (1 - u) + (0.060 + flick) * u ** 2,   # noqa: E731
                                     0.020 * p["sway"] * u * u, 0.300 * u - 0.040 * u ** 3))
    # (Q's tube tail is kept tiny inside the first tuft)
    for i in range(BRUSH):
        u = 0.10 + 0.88 * i / (BRUSH - 1)
        c = curve(u)
        side = 0.012 * (1 if i % 2 else -1)
        r = 0.034 + 0.030 * math.sin(math.pi * min(1.0, u * 0.85 + 0.1))
        ob = m.objects[f"brush{i}"]
        ob.location = c + Vector((0, side, 0))
        ob.scale = (r * 1.05, r * 0.95, r * 0.85)


def assign_depth_parts(m, depth_of):
    Q.assign_depth_parts(m, depth_of)
