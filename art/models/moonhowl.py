"""Moonhowl (Floor 1, Wolf Copse elite): a four-legged creature built on art/models/quadruped.py, wearing the
wolf's coat (wolf.py). Leads its pack (gen_monsters.py: "AWOOOOOO!", events SpirePack). Until now it wore the
Meadow Wolf's sprite with a glow.

Identity (art/QUADRUPED_RULES.md step 1):
  Coat:      moon-white with cool lavender shadows (Tibia's wolves are grey; our Meadow Wolf is tawny, the Grey Alpha
             teal-silver with a black mane, Hollowfang night-black). The copse's pale one.
  Signature: a midnight-blue saddle of fur tufts down the back to a midnight tail tip and ear tips (the night sky on a
             moon-white wolf), and a pale-gold crescent moon on the brow; ice-blue eyes.
  Attitude:  the howler: head carried high, muzzle tilted up as if it is about to howl, tail raised like a plume.

Detail (art/DETAIL_RULES.md): the wolf coat (neck ruff, cheek tufts, brows, mouth line, ear tips, saddle tufts,
hackles, bushy tail), the crescent as three short curved strokes (never a dot), a lean build: long legs, deep chest.
"""
from __future__ import annotations

import math

from mathutils import Vector

import quadruped as Q
import wolf

NAME = "moonhowl"
WALK_FRAMES = 8
PALETTE = "moonhowl"
HEIGHT_SHEAR = 0.30
LEAN = 14.0
REFERENCE = "look_3.png"      # Tibia's War Wolf (comparison only, never shipped)
SIZE = 1.88
GROUND_STRETCH = 1.0
AUTO_PLACE = (1, 1)
SIGNATURE = ["saddle"]        # the crescent is an accent: it does not show from behind
CHECK = {"eye": 1}

PARTS = Q.PARTS + wolf.FUR_PARTS + ["crescent"]
PIXEL_RULES = wolf.fur_rules(
    weight={"crescent": 6.0, "saddle": 2.0},
    thin={"crescent": 2},
    soft=[["head", "crescent"]],
    texture={"saddle": [0.9, 0.2]},
)

SPEC = Q.spec(
    hip=(-0.112, 0.302), hip_r=(0.110, 0.084, 0.074),
    chest=(0.050, 0.326), chest_r=(0.122, 0.098, 0.100),
    belly_r=(0.150, 0.070, 0.044), belly_drop=0.058,
    head=(0.232, 0.360), head_r=(0.106, 0.092, 0.080),              # held high
    snout_tip=(0.410, 0.378), snout_r=(0.052, 0.034),                # muzzle tilted up: about to howl
    nose_r=(0.019, 0.019, 0.016),
    eye=(0.050, 0.052, 0.038), eye_r=0.011,
    ear_root=(-0.034, 0.046, 0.052), ear_tip=(-0.048, 0.060, 0.146), ear_r=0.028,
    front_x=0.080, hind_x=-0.138, leg_top_z=0.268,
    front_y=0.064, hind_y=0.062, front_feet_y=0.104, hind_feet_y=0.096,
    upper=0.156, lower=0.146, leg_r=0.027, paw_r=(0.031, 0.022, 0.015),
    shoulder_r=(0.056, 0.034, 0.076), haunch_r=(0.064, 0.036, 0.078),
    stride=0.115, lift=0.065, bob=0.010, nod=0.010,
    tail_len=0.240, tail_r=(0.032, 0.021), tail_raise=1.15, tail_curl=0.08, tail_split=0.70,
)


def build(model_cls, facing):
    m = Q.build(model_cls, facing, SPEC, PARTS)
    wolf.build_fur(m)
    for i in range(3):
        m.capsule(f"moon{i}", "crescent", segments=6)
    return m


def pose(m, t):
    p = Q.pose(m, t)
    wolf.pose_fur(m, p, SPEC)
    head = p["head"]
    # the crescent on the brow: three short strokes round a curve, horns pointing forward-up
    c = head + Vector((0.030, 0, SPEC["head_r"][2] * 0.92))
    pts = []
    for k in range(4):
        ang = math.pi * (0.15 + 0.70 * k / 3)
        pts.append(c + Vector((-math.sin(ang) * 0.030, math.cos(ang) * 0.036, 0.004 + 0.006 * math.sin(ang))))
    for i in range(3):
        m.put_segment(f"moon{i}", pts[i], pts[i + 1], 0.012 - 0.002 * abs(i - 1))


def assign_depth_parts(m, depth_of):
    Q.assign_depth_parts(m, depth_of)
