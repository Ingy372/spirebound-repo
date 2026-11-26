"""Hollowfang (Floor 1 hidden mini-boss, woken at a secret in the Wolf Copse): a four-legged creature built on
art/models/quadruped.py, wearing the wolf's coat (wolf.py).

gen_monsters.py: "The copse is mine." / "AWOOOOO!", charges. Until now he borrowed the Grey Alpha's sprite.
A money monster (ART_REQUESTS.md Batch 11): the wolf veterans whisper about.

Identity (art/QUADRUPED_RULES.md step 1):
  Coat:      night-black with an indigo cast and a pale grey throat (Tibia's wolves are grey; our Meadow Wolf is tawny,
             our Grey Alpha teal-silver, so the copse's master is the dark one).
  Signature: a streak of bone-white fur from the brow over the neck to the shoulders, like a pale mane, and a white-tipped tail, and ONE great ivory fang
             jutting down over the lip on the left side (the "hollow fang"); yellow-green eyes.
  Attitude:  territorial, stalking: head low and level with the back, hackles raised along the white streak, tail
             held out straight behind.

Detail (art/DETAIL_RULES.md): the wolf coat (ruff, cheek tufts, brows, mouth line, ear tips, saddle tufts, hackles,
bushy tail); the white streak as separate pointed tufts (never a painted band); the fang and a smaller one opposite; a
torn left ear; raked scars on the shoulder. Real proportion: a big timber wolf, legs as long as the body is deep.
"""
from __future__ import annotations

import math

from mathutils import Vector

import quadruped as Q
import wolf

NAME = "hollowfang"
WALK_FRAMES = 8
PALETTE = "hollowfang"
HEIGHT_SHEAR = 0.30
LEAN = 14.0
REFERENCE = "look_3.png"      # Tibia's War Wolf (comparison only, never shipped)
SIZE = 2.05
GROUND_STRETCH = 0.85
AUTO_PLACE = (1, 1)
SIGNATURE = ["stripe"]        # the fang is an accent: no fang shows from behind
CHECK = {"eye": 1}

PARTS = Q.PARTS + wolf.FUR_PARTS + ["stripe", "fang", "scar"]
PIXEL_RULES = wolf.fur_rules(
    weight={"stripe": 2.2, "fang": 5.0, "scar": 4.0},
    thin={"stripe": 3, "fang": 2, "scar": 2},
    soft=[["head", "scar"], ["body", "stripe", "saddle"]],
    texture={"stripe": [0.6, 0.1], "body": [0.85, 0.12]},
    selout=["stripe"],
)
PIXEL_RULES["selout"] = [p for p in PIXEL_RULES["selout"] if p != "saddle"]   # a dark coat: tufts blend (QUADRUPED_RULES lessons)

SPEC = Q.spec(
    hip=(-0.115, 0.292), hip_r=(0.114, 0.088, 0.078),
    chest=(0.050, 0.312), chest_r=(0.126, 0.100, 0.100),
    belly_r=(0.152, 0.072, 0.046), belly_drop=0.058,
    head=(0.245, 0.290), head_r=(0.110, 0.094, 0.082),             # low and level with the back: stalking
    snout_tip=(0.440, 0.248), snout_r=(0.054, 0.035),
    nose_r=(0.020, 0.020, 0.017),
    eye=(0.052, 0.054, 0.036), eye_r=0.011,
    ear_root=(-0.030, 0.048, 0.052), ear_tip=(-0.040, 0.062, 0.140), ear_r=0.028,
    front_x=0.080, hind_x=-0.140, leg_top_z=0.258,
    front_y=0.064, hind_y=0.062, front_feet_y=0.096, hind_feet_y=0.090,
    upper=0.150, lower=0.140, leg_r=0.029, paw_r=(0.032, 0.023, 0.016),
    shoulder_r=(0.058, 0.036, 0.078), haunch_r=(0.064, 0.038, 0.078),
    stride=0.100, lift=0.060, bob=0.010, nod=0.010,
    tail_len=0.230, tail_r=(0.032, 0.020), tail_raise=0.95, tail_curl=0.04, tail_split=0.72,
)
STRIPE = 8           # brow to mid-back only: a full-length white stripe on a dark body reads as a skunk


def build(model_cls, facing):
    m = Q.build(model_cls, facing, SPEC, PARTS)
    wolf.build_fur(m)
    for i in range(STRIPE):
        m.cone(f"stripe{i}", "stripe", segments=6)
    m.cone("fang_big", "fang", segments=6)
    m.cone("fang_small", "fang", segments=6)
    for i in range(3):
        m.capsule(f"scar{i}", "scar", segments=6)
    return m


def pose(m, t):
    p = Q.pose(m, t)
    wolf.pose_fur(m, p, SPEC)
    chest, hip, head, tip, a, walking = p["chest"], p["hip"], p["head"], p["snout_tip"], p["a"], p["walking"]
    # the white streak: pointed tufts from the brow over the neck and spine to the rump, raised like hackles
    brow = head + Vector((0.040, 0, SPEC["head_r"][2] * 0.95))
    neck = chest + Vector((0.050, 0, SPEC["chest_r"][2] * 1.02))
    rump = hip + Vector((-0.060, 0, SPEC["hip_r"][2] * 0.98))
    for i in range(STRIPE):
        u = i / (STRIPE - 1)
        q = brow.lerp(neck, u / 0.40) if u < 0.40 else neck.lerp(rump, (u - 0.40) / 0.60 * 0.55)
        tall = (0.055 + 0.030 * math.sin(math.pi * min(u * 1.6, 1.0))) * (1.0 - 0.6 * max(0.0, u - 0.6) / 0.4)
        lift = 0.010 * math.sin(a * 2 + i * 0.8) if walking else 0.0
        side = 0.010 * (1 if i % 2 else -1)
        m.put_segment(f"stripe{i}", q - Vector((0, 0, 0.012)), q + Vector((-0.050, side, tall + lift)), 0.026, 0.016)
    # the great fang on the left, over the lip and down; a smaller one on the right
    for name, sign, length, r in (("fang_big", 1, 0.095, 0.020), ("fang_small", -1, 0.050, 0.013)):
        root = tip + Vector((-0.045, 0.034 * sign, -0.012))
        m.put_segment(name, root, root + Vector((0.016, 0.020 * sign, -length)), r, 0.003)   # out past the lip: shows from the side
    # raked scars on the shoulder facing the camera walking east
    for i in range(3):
        q = chest + Vector((-0.020 + 0.024 * i, -0.094, 0.060))
        m.put_segment(f"scar{i}", q, q + Vector((0.028, -0.004, -0.044)), 0.006)


def assign_depth_parts(m, depth_of):
    Q.assign_depth_parts(m, depth_of)
