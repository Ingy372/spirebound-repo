"""Grey alpha (Floor 1, Wolf Copse elite): a four-legged creature built on art/models/quadruped.py.

ART_REQUESTS.md: "a bigger silver-grey wolf with a scarred face and a darker mane (elite version of the wolf)".

Identity (art/QUADRUPED_RULES.md step 1):
  Coat:      moonlit teal-silver (Tibia's war wolf is plain grey) with a pale frost belly.
  Signature: a thick near-black mane over the neck and shoulders (shows from every side), three pale scars
             raked across the left cheek, ice-blue eyes.
  Attitude:  dominant: the meadow wolf's build but heavier in front, head held high over the mane, ears up,
             tail raised.
"""
from __future__ import annotations

from mathutils import Vector

import quadruped as Q

NAME = "alpha"
WALK_FRAMES = 8
PALETTE = "alpha"
HEIGHT_SHEAR = 0.30
LEAN = 14.0
REFERENCE = "look_3.png"      # Tibia's War Wolf (comparison only, never shipped)
SIZE = 1.95
GROUND_STRETCH = 1.0
AUTO_PLACE = (1, 1)
SIGNATURE = ["mane", "eye"]

PARTS = Q.PARTS + ["mane", "scar"]
PIXEL_RULES = Q.pixel_rules(
    weight={"mane": 1.5, "scar": 4.0},
    thin={"mane": 4, "scar": 2},
    soft=[["head", "scar"], ["body", "mane"]],
    texture={"mane": [1.1, 0.25]},
    selout=["mane"],
)

SPEC = Q.spec(
    hip=(-0.115, 0.290), hip_r=(0.112, 0.086, 0.076),
    chest=(0.050, 0.315), chest_r=(0.128, 0.104, 0.104),
    belly_r=(0.155, 0.074, 0.048), belly_drop=0.060,
    head=(0.230, 0.350), head_r=(0.098, 0.090, 0.082),              # held high over the mane
    snout_tip=(0.410, 0.318), snout_r=(0.054, 0.036),
    nose_r=(0.017, 0.017, 0.015),
    eye=(0.054, 0.054, 0.036), eye_r=0.016,
    ear_root=(-0.025, 0.048, 0.060), ear_tip=(-0.022, 0.060, 0.150), ear_r=0.029,   # ears up
    front_x=0.080, hind_x=-0.140, leg_top_z=0.258,
    front_y=0.064, hind_y=0.062, front_feet_y=0.096, hind_feet_y=0.090,
    upper=0.148, lower=0.138, leg_r=0.029, paw_r=(0.032, 0.023, 0.016),
    shoulder_r=(0.060, 0.038, 0.080), haunch_r=(0.064, 0.038, 0.078),
    stride=0.115, lift=0.065, bob=0.010, nod=0.008,
    tail_len=0.200, tail_r=(0.036, 0.024), tail_raise=0.95, tail_curl=0.05, tail_split=0.75,
)


def build(model_cls, facing):
    m = Q.build(model_cls, facing, SPEC, PARTS)
    m.ellipsoid("mane", "mane", radii=(0.080, 0.118, 0.100), segments=18, rings=10)
    m.ellipsoid("mane_top", "mane", radii=(0.110, 0.070, 0.050), segments=14, rings=8)
    for i in range(3):
        m.capsule(f"scar{i}", "scar", segments=6)
    return m


def pose(m, t):
    p = Q.pose(m, t)
    chest, head = p["chest"], p["head"]
    m.objects["mane"].location = chest + Vector((0.085, 0, 0.030))
    m.objects["mane_top"].location = chest + Vector((0.010, 0, 0.080))
    # three raked scars on the left (camera-side when facing east) cheek
    for i in range(3):
        a = head + Vector((0.000 + 0.022 * i, -0.080, 0.062))
        m.put_segment(f"scar{i}", a, a + Vector((0.026, -0.004, -0.034)), 0.007)


def assign_depth_parts(m, depth_of):
    Q.assign_depth_parts(m, depth_of)
