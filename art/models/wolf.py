"""Meadow wolf (Floor 1, Wolf Copse): a four-legged creature built on art/models/quadruped.py.

ART_REQUESTS.md: "a lean grey-brown wolf with a pale belly".

Identity (art/QUADRUPED_RULES.md step 1):
  Coat:      warm tawny grey-brown with a cream throat and belly (Tibia's wolf is cold grey).
  Signature: a dark charcoal saddle running down the spine to the tail, a black-tipped tail, amber eyes.
  Attitude:  prowling: head carried low and level with the back, ears pricked forward, tail held low.
"""
from __future__ import annotations

from mathutils import Vector

import quadruped as Q

NAME = "wolf"
WALK_FRAMES = 8
PALETTE = "wolf"
HEIGHT_SHEAR = 0.30
LEAN = 14.0
REFERENCE = "look_27.png"     # Tibia's Wolf (comparison only, never shipped)
SIZE = 1.8
GROUND_STRETCH = 1.3
AUTO_PLACE = (1, 1)
SIGNATURE = ["saddle", "eye"]     # must show from all four directions (check_creature.py)
CHECK = {"eye": 2}

PARTS = Q.PARTS + ["saddle", "bib"]
PIXEL_RULES = Q.pixel_rules(
    weight={"saddle": 1.6, "bib": 1.4},
    thin={"saddle": 4},
    soft=[["body", "saddle", "bib", "belly"], ["head", "bib"]],
    texture={"saddle": [0.7, 0.2], "bib": [0.4, 0.0]},
    selout=["saddle"],
)

SPEC = Q.spec(
    hip=(-0.105, 0.300), hip_r=(0.115, 0.086, 0.074),
    chest=(0.050, 0.312), chest_r=(0.118, 0.094, 0.092),
    belly_r=(0.150, 0.070, 0.045), belly_drop=0.055,
    head=(0.215, 0.318), head_r=(0.086, 0.080, 0.072),              # level with the back: prowling
    snout_tip=(0.380, 0.282), snout_r=(0.048, 0.032),
    nose_r=(0.016, 0.016, 0.014),
    eye=(0.052, 0.052, 0.034), eye_r=0.016,
    ear_root=(-0.020, 0.046, 0.058), ear_tip=(-0.004, 0.058, 0.145), ear_r=0.028,   # pricked forward
    front_x=0.080, hind_x=-0.135, leg_top_z=0.262,
    front_y=0.060, hind_y=0.060, front_feet_y=0.090, hind_feet_y=0.086,
    upper=0.150, lower=0.140, leg_r=0.027, paw_r=(0.030, 0.021, 0.015),
    shoulder_r=(0.054, 0.034, 0.074), haunch_r=(0.064, 0.036, 0.078),
    stride=0.115, lift=0.065, bob=0.010, nod=0.010,
    tail_len=0.240, tail_r=(0.034, 0.022), tail_raise=0.75, tail_curl=0.06, tail_split=0.72,
)


def build(model_cls, facing):
    m = Q.build(model_cls, facing, SPEC, PARTS)
    m.ellipsoid("saddle_c", "saddle", radii=(0.110, 0.070, 0.030), segments=16, rings=8)
    m.ellipsoid("saddle_h", "saddle", radii=(0.110, 0.064, 0.028), segments=16, rings=8)
    m.ellipsoid("bib", "bib", radii=(0.060, 0.070, 0.070), segments=14, rings=8)
    return m


def pose(m, t):
    p = Q.pose(m, t)
    chest, hip, head = p["chest"], p["hip"], p["head"]
    # the dark saddle lies along the top of the back
    m.objects["saddle_c"].location = chest + Vector((-0.020, 0, SPEC["chest_r"][2] * 0.78))
    m.objects["saddle_h"].location = hip + Vector((0.010, 0, SPEC["hip_r"][2] * 0.78))
    # cream throat and chest bib under the head
    m.objects["bib"].location = chest + Vector((0.085, 0, -0.005)).lerp(head - chest, 0.25)


def assign_depth_parts(m, depth_of):
    Q.assign_depth_parts(m, depth_of)
