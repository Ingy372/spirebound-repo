"""Burrow mole (Floor 1, Burrow Hills): a four-legged creature built on art/models/quadruped.py.

ART_REQUESTS.md: "a stocky grey-brown mole with huge pale digging claws, tiny eyes, a pink nose, a little dirt
on its back".

Identity (art/QUADRUPED_RULES.md step 1):
  Coat:      soft mouse-grey velvet (Tibia's mole is near-black olive), paler on the face.
  Signature: two huge ivory spade-claws thrust forward and out to the sides (they show from above in every
             direction), a fleshy pink snout, crumbs of earth on its back.
  Attitude:  a hunched digger: low to the ground, shoulders humped high, head down, claws reaching ahead.
"""
from __future__ import annotations

from mathutils import Vector

import quadruped as Q

NAME = "mole"
WALK_FRAMES = 8
PALETTE = "mole"
HEIGHT_SHEAR = 0.30
LEAN = 14.0
REFERENCE = "look_1048.png"   # Tibia's Mole (comparison only, never shipped)
SIZE = 2.05
GROUND_STRETCH = 1.1
AUTO_PLACE = (1, 1)
SIGNATURE = ["claw", "nose"]
CHECK = {"legs_side": 0.05, "legs_updown": 0.03}

PARTS = Q.PARTS + ["claw", "dirt"]
PIXEL_RULES = Q.pixel_rules(
    weight={"claw": 3.0, "dirt": 2.0, "nose": 4.0},
    thin={"claw": 2, "dirt": 3},
    soft=[["body", "dirt"]],
    texture={"body": [0.9, 0.2], "dirt": [0.8, 0.0]},
    selout=["claw"],
)

SPEC = Q.spec(
    hip=(-0.110, 0.140), hip_r=(0.135, 0.125, 0.105),
    chest=(0.040, 0.165), chest_r=(0.125, 0.135, 0.120),            # humped shoulders
    belly_r=(0.170, 0.110, 0.055), belly_drop=0.060,
    head=(0.170, 0.128), head_r=(0.094, 0.096, 0.080),              # head down
    snout_tip=(0.305, 0.098), snout_r=(0.046, 0.030),
    nose_r=(0.024, 0.030, 0.024),
    eye=(0.050, 0.060, 0.034), eye_r=0.011,                         # tiny eyes
    ear_root=(-0.030, 0.050, 0.040), ear_tip=(-0.040, 0.060, 0.050), ear_r=0.006,   # no visible ears
    front_x=0.095, hind_x=-0.140, leg_top_z=0.110,
    front_y=0.120, hind_y=0.100, front_feet_y=0.165, hind_feet_y=0.130,
    upper=0.065, lower=0.060, leg_r=0.032, paw_r=(0.034, 0.028, 0.016),
    shoulder_r=(0.060, 0.050, 0.060), haunch_r=(0.060, 0.050, 0.055),
    stride=0.065, lift=0.040, bob=0.012, nod=0.012,
    tail_len=0.070, tail_r=(0.014, 0.008), tail_raise=0.6, tail_curl=0.0, tail_split=0.5,
)
DIRT = [(-0.090, 0.040), (-0.040, -0.050), (-0.140, -0.020), (0.010, 0.030)]


def build(model_cls, facing):
    m = Q.build(model_cls, facing, SPEC, PARTS)
    for k in ("fl", "fr"):
        m.ellipsoid(f"{k}_palm", "claw", radii=(0.040, 0.044, 0.014), segments=12, rings=6)
        for j in range(3):
            m.cone(f"{k}_claw{j}", "claw", segments=6)
    for i in range(len(DIRT)):
        m.ellipsoid(f"dirt{i}", "dirt", radii=(0.022, 0.018, 0.010), segments=8, rings=6)
    return m


def pose(m, t):
    p = Q.pose(m, t)
    hip = p["hip"]
    # the spade claws: a broad pale palm on each front paw, three long claws fanning forward and outward
    for k, side in (("fl", -1), ("fr", 1)):
        paw = m.objects[f"{k}_paw"].location
        palm = paw + Vector((0.040, 0.030 * side, 0.010))
        m.objects[f"{k}_palm"].location = palm
        for j in range(3):
            sp = (j - 1) * 0.030
            root = palm + Vector((0.025, sp, 0.004))
            m.put_segment(f"{k}_claw{j}", root, root + Vector((0.075, sp * 0.9 + 0.022 * side, -0.004)), 0.014)
    for i, (x, y) in enumerate(DIRT):
        m.objects[f"dirt{i}"].location = hip + Vector((x + 0.060, y, SPEC["hip_r"][2] * 0.97))


def assign_depth_parts(m, depth_of):
    Q.assign_depth_parts(m, depth_of)
