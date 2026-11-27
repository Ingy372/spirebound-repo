"""Meadow Hare (Floor 1 small game on the empty lawns, Q94): a four-legged creature built on art/models/quadruped.py.
Harmless, quick, it runs from you.

Identity (art/QUADRUPED_RULES.md step 1):
  Coat:      silver-grey with a warm buff wash on the flanks and cheeks (Tibia's rabbit is plain brown), a cream belly
             and pale feet.
  Signature: very long upright ears with black tips and pink insides (a hare, not a bunny), seen from every direction;
             a white scut raised behind.
  Attitude:  alert and ready to bolt: ears straight up, big haunches gathered under it, head raised, a bouncy gait.

Detail (art/DETAIL_RULES.md): a hare's anatomy: long ears with dark tips, a round head with a split upper lip and a
twitchy pink nose, big amber eyes set high on the sides, a narrow chest, big round haunches, long flat hind feet,
short thin front legs, a white scut. Marks: big = the buff flank patch; medium = the cream belly and the ear insides;
small = the black ear tips, the nose.
Real proportion: a brown hare's ears are as long as its head and then some (about 1.3x); its hind feet are about a
third of its body length; sitting, the haunch is the highest point.
"""
from __future__ import annotations

import math

from mathutils import Vector

import quadruped as Q

NAME = "meadow_hare"
WALK_FRAMES = 8
PALETTE = "meadow_hare"
HEIGHT_SHEAR = 0.30
LEAN = 12.0
REFERENCE = "look_74.png"    # Tibia's Rabbit (comparison only, never shipped)
SIZE = 1.05
GROUND_STRETCH = 1.0
AUTO_PLACE = (1, 1)
SIGNATURE = ["eartip", "ear"]
CHECK = {"eye": 1, "legs_updown": 0.02, "signature": 4}   # a tiny 20 px animal: one-or-two-pixel eye, legs tuck under the haunch, 4 px ear tips
HEAD_PARTS = ["head", "snout", "nose", "ear", "eartip", "inner", "eye"]

PARTS = Q.PARTS + ["eartip", "inner", "buff", "line", "hindfoot"]
PIXEL_RULES = Q.pixel_rules(
    weight={"eartip": 4.0, "inner": 3.0, "buff": 1.6, "line": 3.0, "hindfoot": 2.0, "tail_base": 3.5, "tail_tip": 4.0,
            "ear": 2.6},
    thin={"eartip": 2, "inner": 2, "line": 2, "hindfoot": 3},
    soft=[["body", "belly", "buff"], ["head", "snout", "nose", "line", "eye"], ["ear", "inner", "eartip"],
          ["leg_near", "paw_near", "hindfoot"]],
    texture={"body": [0.6, 0.15], "buff": [0.5, 0.1], "head": [0.4, 0.1]},
    selout=["ear"],
)

SPEC = Q.spec(
    hip=(-0.105, 0.215), hip_r=(0.120, 0.098, 0.105),                # big round haunch: the highest point
    chest=(0.045, 0.175), chest_r=(0.085, 0.070, 0.080),
    belly_r=(0.130, 0.068, 0.045), belly_drop=0.050,
    head=(0.140, 0.245), head_r=(0.068, 0.058, 0.060),               # head raised, alert
    snout_tip=(0.222, 0.222), snout_r=(0.038, 0.030), snout_blunt=True,
    nose_r=(0.012, 0.016, 0.012),
    eye=(0.020, 0.048, 0.018), eye_r=0.014,
    ear_root=(-0.025, 0.026, 0.045), ear_tip=(-0.075, 0.050, 0.300), ear_r=0.027,
    front_x=0.065, hind_x=-0.110, leg_top_z=0.150,
    front_y=0.052, hind_y=0.075, front_feet_y=0.068, hind_feet_y=0.100,
    upper=0.080, lower=0.078, leg_r=0.016, paw_r=(0.022, 0.016, 0.012),
    shoulder_r=(0.040, 0.030, 0.060), haunch_r=(0.080, 0.042, 0.080),
    stride=0.085, lift=0.070, bob=0.030, nod=0.012,
    tail_len=0.050, tail_r=(0.030, 0.026), tail_raise=1.6, tail_curl=0.0, tail_split=0.4,
)


def build(model_cls, facing):
    m = Q.build(model_cls, facing, SPEC, PARTS)
    m.ellipsoid("buff", "buff", radii=(0.080, 0.050, 0.058), segments=14, rings=8)
    m.ellipsoid("cheek", "buff", radii=(0.036, 0.050, 0.032), segments=10, rings=6)
    m.capsule("lip", "line", segments=6)
    for k in ("l", "r"):
        m.cone(f"tip_{k}", "eartip", segments=8)
        m.capsule(f"inner_{k}", "inner", segments=6)
        m.ellipsoid(f"hfoot_{k}", "hindfoot", radii=(0.048, 0.018, 0.012), segments=10, rings=6)
    return m


def pose(m, t):
    p = Q.pose(m, t)
    head, hip, chest = p["head"], p["hip"], p["chest"]
    m.objects["buff"].location = hip.lerp(chest, 0.35) + Vector((0, 0, 0.020))
    m.objects["cheek"].location = head + Vector((0.010, 0, -0.022))
    tip = p["snout_tip"]
    m.put_segment("lip", tip + Vector((-0.004, 0, -0.008)), tip + Vector((-0.010, 0, -0.030)), 0.005)
    twitch = 0.012 * math.sin(p["a"] * 2) if p["walking"] else 0.0
    for sign, k in ((1, "l"), (-1, "r")):
        r0, r1 = SPEC["ear_root"], SPEC["ear_tip"]
        root = head + Vector((r0[0], r0[1] * sign, r0[2]))
        end = head + Vector((r1[0] + twitch * sign, r1[1] * sign, r1[2]))
        d = end - root
        # the black tip: the top fifth of the ear; the pink inside: a thin strip down the ear's front face
        m.put_segment(f"tip_{k}", root + d * 0.70, end + d * 0.08, SPEC["ear_r"] * 0.85, SPEC["ear_r"] * 0.30)
        m.put_segment(f"inner_{k}", root + d * 0.18 + Vector((0.010, 0, 0)), root + d * 0.72 + Vector((0.012, 0, 0)), 0.010)
        # long flat hind feet, flat on the ground under the haunch
        paw = m.objects[f"h{k}_paw"].location
        m.objects[f"hfoot_{k}"].location = paw + Vector((0.018, 0, -0.002))


def assign_depth_parts(m, depth_of):
    Q.assign_depth_parts(m, depth_of)
