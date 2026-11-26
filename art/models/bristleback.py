"""Old Bristleback (Floor 1, Boar Meadow elite): a four-legged creature built on art/models/quadruped.py, the Bristle
Boar (boar.py) with its back gone to quills. Until now it wore the Bristle Boar's sprite with a glow.

Identity (art/QUADRUPED_RULES.md step 1):
  Coat:      deep rust-umber (the meadow's boars are charcoal with an ember crest; Old Tusk is grizzled grey;
             Tibia's boar is orange-brown and smooth), a darker face mask.
  Signature: a mantle of long quill-bristles over the whole back, three rows fanning out sideways like a porcupine's,
             each quill dark at the root with a bone-pale tip; long tusks that curl up; amber eyes.
  Attitude:  an old, wary brute: the boar's low head and tall hump, a little heavier, quills raised.

Detail (art/DETAIL_RULES.md): a boar's anatomy (hump, wedge head, snout disc, tusks, small eyes under a scowl, pinned
ears, short legs with hooves); big marks: the quill mantle; medium: the face mask; small: the pale quill tips.
Real proportion: a boar's body is about 1.6x as long as it is tall at the hump, the head a third of the body.
"""
from __future__ import annotations

import math

from mathutils import Vector

import quadruped as Q

NAME = "bristleback"
WALK_FRAMES = 8
PALETTE = "bristleback"
HEIGHT_SHEAR = 0.30
LEAN = 14.0
REFERENCE = "look_380.png"    # Tibia's Boar (comparison only, never shipped)
SIZE = 1.95
GROUND_STRETCH = 1.0
AUTO_PLACE = (1, 1)
SIGNATURE = ["quill", "tusk"]

PARTS = Q.PARTS + ["tusk", "quill", "quilltip", "brow"]
PIXEL_RULES = Q.pixel_rules(
    dark=True,
    bands=[0.38, 0.50, 0.60, 0.69, 0.78, 0.86, 0.93],
    weight={"tusk": 5.0, "quill": 2.2, "quilltip": 4.0, "nose": 2.0, "brow": 4.0},
    thin={"tusk": 2, "quill": 2, "quilltip": 2, "brow": 3},
    soft=[["head", "brow", "eye"], ["quill", "quilltip"]],
    texture={"quill": [0.4, 0.0], "body": [0.9, 0.15]},
    selout=["quill"],
)

SPEC = Q.spec(
    hip=(-0.120, 0.250), hip_r=(0.116, 0.116, 0.100),
    chest=(0.050, 0.296), chest_r=(0.144, 0.140, 0.142),
    belly_r=(0.168, 0.102, 0.060), belly_drop=0.075,
    head=(0.218, 0.224), head_r=(0.110, 0.106, 0.092),
    snout_tip=(0.385, 0.170), snout_r=(0.060, 0.052), snout_blunt=True,
    nose_r=(0.020, 0.056, 0.050),
    eye=(0.066, 0.086, 0.042), eye_r=0.016,
    ear_root=(-0.040, 0.068, 0.060), ear_tip=(-0.105, 0.105, 0.110), ear_r=0.028,
    front_x=0.075, hind_x=-0.135, leg_top_z=0.205,
    front_y=0.098, hind_y=0.086, front_feet_y=0.136, hind_feet_y=0.118,
    upper=0.112, lower=0.105, leg_r=0.037, paw_r=(0.038, 0.030, 0.020),
    shoulder_r=(0.066, 0.044, 0.090), haunch_r=(0.066, 0.042, 0.078),
    stride=0.095, lift=0.060, bob=0.012, nod=0.012,
    tail_len=0.100, tail_r=(0.016, 0.018), tail_raise=0.9, tail_curl=0.0, tail_split=0.55,
)
ROWS = (-1, 0, 1)      # three rows of quills: left flank, spine, right flank
PER_ROW = 6


def build(model_cls, facing):
    m = Q.build(model_cls, facing, SPEC, PARTS)
    for k in ("l", "r"):
        m.tube(f"tusk_{k}", "tusk", points=6)
        m.capsule(f"brow_{k}", "brow", segments=6)
    for r in ROWS:
        for i in range(PER_ROW):
            m.cone(f"quill{r}_{i}", "quill", segments=5)
            m.cone(f"qtip{r}_{i}", "quilltip", segments=5)
    return m


def pose(m, t):
    p = Q.pose(m, t)
    head, chest, hip, tip = p["head"], p["chest"], p["hip"], p["snout_tip"]
    # long tusks curling out and up, longer than the meadow boar's
    for sign, k in ((1, "l"), (-1, "r")):
        root = tip + Vector((-0.050, 0.046 * sign, -0.034))
        pts, radii = [], []
        for i in range(6):
            u = i / 5
            pts.append(tuple(root + Vector((0.070 * math.sin(u * 2.1), sign * (0.080 * u), 0.125 * u * u))))
            radii.append(0.022 * (1 - 0.74 * u))
        m.set_tube(f"tusk_{k}", pts, radii)
        eye = m.objects[f"eye_{k}"].location
        m.put_segment(f"brow_{k}", eye + Vector((-0.040, 0.004 * sign, 0.034)), eye + Vector((0.034, -0.010 * sign, 0.014)), 0.013)
    # the quill mantle: from behind the head over the hump to the rump, three rows fanning up and out
    neck = head.lerp(chest, 0.55) + Vector((0, 0, SPEC["chest_r"][2] * 0.80))
    hump = chest + Vector((-0.010, 0, SPEC["chest_r"][2] * 0.96))
    rump = hip + Vector((-0.010, 0, SPEC["hip_r"][2] * 0.90))
    for r in ROWS:
        for i in range(PER_ROW):
            u = (i + 0.5 * (r != 0)) / PER_ROW
            q = neck.lerp(hump, u / 0.35) if u < 0.35 else hump.lerp(rump, (u - 0.35) / 0.65)
            q = q + Vector((-abs(r) * 0.015, r * 0.042, 0.0))
            tall = (0.125 if r == 0 else 0.110) * (1.0 - 0.35 * max(0.0, u - 0.6) / 0.4) * (1.0 if i % 2 else 0.86)
            flick = 0.010 * math.sin(p["a"] * 2 + i * 0.9 + r) if p["walking"] else 0.0
            d = Vector((-0.085 - flick, r * 0.030, tall))
            base = q - Vector((0, 0, 0.020))
            m.put_segment(f"quill{r}_{i}", base, base + d * 0.72, 0.022, 0.012)
            m.put_segment(f"qtip{r}_{i}", base + d * 0.68, base + d, 0.012, 0.003)


def assign_depth_parts(m, depth_of):
    Q.assign_depth_parts(m, depth_of)
