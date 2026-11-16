"""Grey alpha (Floor 1, Wolf Copse elite): a four-legged creature built on art/models/quadruped.py.

ART_REQUESTS.md: "a bigger silver-grey wolf with a scarred face and a darker mane (elite version of the wolf)".

Identity (art/QUADRUPED_RULES.md step 1):
  Coat:      moonlit teal-silver (Tibia's war wolf is plain grey) with a pale frost belly.
  Signature: a shaggy near-black mane of spiked tufts over the neck and shoulders, three pale scars raked across
             the cheek, ice-blue eyes.
  Attitude:  dominant: the meadow wolf's build but heavier in front, head held high over the mane, ears up,
             tail raised.

Detail (art/DETAIL_RULES.md): wears the wolf's coat (wolf.build_fur: neck ruff, cheek tufts, brows, mouth line,
ear tips, saddle tufts, hackles, bushy tail) and adds the mane as separate pointed tufts, never a ball.
"""
from __future__ import annotations

import math

from mathutils import Vector

import quadruped as Q
import wolf

NAME = "alpha"
WALK_FRAMES = 8
PALETTE = "alpha"
HEIGHT_SHEAR = 0.30
LEAN = 14.0
REFERENCE = "look_3.png"      # Tibia's War Wolf (comparison only, never shipped)
SIZE = 1.95
GROUND_STRETCH = 1.0
AUTO_PLACE = (1, 1)
SIGNATURE = ["mane"]
CHECK = {"eye": 1}

PARTS = Q.PARTS + wolf.FUR_PARTS + ["mane", "scar"]
PIXEL_RULES = wolf.fur_rules(
    weight={"mane": 1.6, "scar": 4.0},
    thin={"mane": 3, "scar": 2},
    soft=[["head", "scar"], ["body", "mane", "saddle"]],
    texture={"mane": [1.1, 0.25]},
    selout=["mane"],
)

SPEC = Q.spec(
    hip=(-0.115, 0.290), hip_r=(0.112, 0.086, 0.076),
    chest=(0.050, 0.315), chest_r=(0.128, 0.104, 0.104),
    belly_r=(0.155, 0.074, 0.048), belly_drop=0.060,
    head=(0.235, 0.345), head_r=(0.098, 0.088, 0.078),              # held high over the mane
    snout_tip=(0.420, 0.308), snout_r=(0.052, 0.034),
    nose_r=(0.020, 0.020, 0.017),
    eye=(0.054, 0.056, 0.038), eye_r=0.011,
    ear_root=(-0.030, 0.050, 0.056), ear_tip=(-0.030, 0.064, 0.150), ear_r=0.029,   # ears up
    front_x=0.080, hind_x=-0.140, leg_top_z=0.258,
    front_y=0.064, hind_y=0.062, front_feet_y=0.096, hind_feet_y=0.090,
    upper=0.148, lower=0.138, leg_r=0.029, paw_r=(0.032, 0.023, 0.016),
    shoulder_r=(0.060, 0.038, 0.080), haunch_r=(0.064, 0.038, 0.078),
    stride=0.115, lift=0.065, bob=0.010, nod=0.008,
    tail_len=0.200, tail_r=(0.032, 0.022), tail_raise=0.95, tail_curl=0.05, tail_split=0.75,
)
MANE = 9


def build(model_cls, facing):
    m = Q.build(model_cls, facing, SPEC, PARTS)
    wolf.build_fur(m)
    m.ellipsoid("mane_core", "mane", radii=(0.070, 0.100, 0.085), segments=16, rings=10)
    for i in range(MANE):
        m.cone(f"mane{i}", "mane", segments=6)
    for i in range(3):
        m.capsule(f"scar{i}", "scar", segments=6)
    return m


def pose(m, t):
    p = Q.pose(m, t)
    wolf.pose_fur(m, p, SPEC)
    chest, head, a, walking = p["chest"], p["head"], p["a"], p["walking"]
    core = chest + Vector((0.085, 0, 0.030))
    m.objects["mane_core"].location = core
    # the mane: pointed tufts fanning back and out from the neck, lifting as he trots
    for i in range(MANE):
        ang = -1.9 + 3.8 * i / (MANE - 1)                    # round the top of the neck, side to side
        out = Vector((0.0, math.sin(ang) * 0.092, math.cos(ang) * 0.080))
        lift = 0.012 * math.sin(a * 2 + i * 0.8) if walking else 0.0
        root = core + out * 0.75 + Vector((0.010 - 0.012 * (i % 2), 0, 0))
        m.put_segment(f"mane{i}", root, root + out * 0.75 + Vector((-0.075 - 0.020 * (i % 2), 0, lift)), 0.034, 0.022)
    # three raked scars on the cheek that faces the camera when he walks east
    for i in range(3):
        q = head + Vector((0.004 + 0.022 * i, -0.078, 0.056))
        m.put_segment(f"scar{i}", q, q + Vector((0.026, -0.004, -0.034)), 0.006)


def assign_depth_parts(m, depth_of):
    Q.assign_depth_parts(m, depth_of)
