"""Meadow wolf (Floor 1, Wolf Copse): a four-legged creature built on art/models/quadruped.py.

ART_REQUESTS.md: "a lean grey-brown wolf with a pale belly".

Identity (art/QUADRUPED_RULES.md step 1):
  Coat:      warm tawny ochre with a cream throat and belly (Tibia's wolf is cold grey).
  Signature: a dark saddle of ragged fur streaks down the spine to a black-tipped tail, amber eyes.
  Attitude:  prowling: head carried low and forward, below the line of the back, ears pricked, tail held low.

Detail (art/DETAIL_RULES.md): a neck ruff and pale cheek tufts, a dark brow over each small eye, a drawn mouth
line, dark ear tips, a saddle made of separate fur tufts (never a flat slab), raised hackles, a bushy tail.

The fur pieces live in build_fur() / pose_fur() so the grey alpha (alpha.py) wears the same coat.
"""
from __future__ import annotations

import math

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
SIGNATURE = ["saddle"]            # must show from all four directions (check_creature.py)
CHECK = {"eye": 1}                # a wolf's eye is one or two bright pixels under a brow (art/DETAIL_RULES.md)

FUR_PARTS = ["saddle", "bib", "brow", "line"]
PARTS = Q.PARTS + FUR_PARTS


def fur_rules(**extra):
    """The wolf coat's pixel rules; alpha.py adds its own parts on top."""
    return Q.pixel_rules(
        weight={"saddle": 1.7, "bib": 1.5, "brow": 4.0, "line": 3.0, "eye": 9.0, **extra.get("weight", {})},
        thin={"saddle": 3, "bib": 3, "brow": 2, "line": 2, "eye": 2, **extra.get("thin", {})},
        soft=[["body", "saddle", "bib", "belly"], ["head", "bib", "brow", "line", "eye", "saddle"]] + extra.get("soft", []),
        texture={"body": [1.0, 0.25], "head": [0.7, 0.15], "saddle": [0.8, 0.2], "bib": [0.5, 0.0], **extra.get("texture", {})},
        selout=["saddle"] + extra.get("selout", []),
    )


PIXEL_RULES = fur_rules()

SPEC = Q.spec(
    hip=(-0.105, 0.300), hip_r=(0.115, 0.086, 0.074),
    chest=(0.050, 0.318), chest_r=(0.118, 0.096, 0.094),
    belly_r=(0.150, 0.070, 0.045), belly_drop=0.055,
    head=(0.235, 0.268), head_r=(0.102, 0.088, 0.074),              # low and forward: prowling
    snout_tip=(0.405, 0.226), snout_r=(0.046, 0.030),
    nose_r=(0.019, 0.019, 0.016),
    eye=(0.050, 0.052, 0.036), eye_r=0.010,                         # small: one or two pixels
    ear_root=(-0.030, 0.046, 0.050), ear_tip=(-0.022, 0.060, 0.140), ear_r=0.028,
    front_x=0.080, hind_x=-0.135, leg_top_z=0.262,
    front_y=0.060, hind_y=0.060, front_feet_y=0.090, hind_feet_y=0.086,
    upper=0.150, lower=0.140, leg_r=0.027, paw_r=(0.030, 0.021, 0.015),
    shoulder_r=(0.054, 0.034, 0.074), haunch_r=(0.064, 0.036, 0.078),
    stride=0.115, lift=0.065, bob=0.010, nod=0.012,
    tail_len=0.240, tail_r=(0.030, 0.020), tail_raise=0.75, tail_curl=0.06, tail_split=0.72,
)
TUFTS = 7          # saddle tufts down the spine
HACKLES = 4        # raised fur on the shoulders


def build_fur(m):
    m.ellipsoid("neck", "body", radii=(0.080, 0.074, 0.074), segments=14, rings=8)
    for i in range(TUFTS):
        m.ellipsoid(f"tuft{i}", "saddle", radii=(0.062, 0.034, 0.022), segments=10, rings=6)
    for i in range(HACKLES):
        m.cone(f"hackle{i}", "saddle", segments=5)
    m.ellipsoid("bib", "bib", radii=(0.058, 0.066, 0.066), segments=14, rings=8)
    m.ellipsoid("tailfluff", "tail_base", radii=(0.060, 0.044, 0.044), segments=12, rings=8)
    for k in ("l", "r"):
        m.cone(f"cheek_{k}", "bib", segments=6)
        m.cone(f"cheek2_{k}", "bib", segments=6)
        m.capsule(f"brow_{k}", "brow", segments=6)
        m.capsule(f"mouth_{k}", "line", segments=6)
        m.cone(f"eartip_{k}", "saddle", segments=6)


def pose_fur(m, p, s):
    chest, hip, head, tip, a, walking = p["chest"], p["hip"], p["head"], p["snout_tip"], p["a"], p["walking"]
    m.objects["neck"].location = chest.lerp(head, 0.55) + Vector((0, 0, 0.012))
    # a saddle of separate dark tufts, staggered left and right, each tipped up at the back like real fur
    start = chest + Vector((0.040, 0, s["chest_r"][2] * 0.86))
    end = hip + Vector((-0.070, 0, s["hip_r"][2] * 0.88))
    for i in range(TUFTS):
        u = i / (TUFTS - 1)
        ob = m.objects[f"tuft{i}"]
        ob.location = start.lerp(end, u) + Vector((0, 0.020 * (1 if i % 2 else -1), 0.006 * math.sin(a * 2 + i) if walking else 0.0))
        ob.rotation_mode = "XYZ"
        ob.rotation_euler = (0, -0.28, 0.35 * (1 if i % 2 else -1))
        ob.scale = (0.066 - 0.014 * u, 0.036 - 0.006 * u, 0.022)
    for i in range(HACKLES):
        q = start + Vector((-0.030 - 0.038 * i, 0.012 * (1 if i % 2 else -1), -0.006))
        lift = 0.010 * math.sin(a * 2 + i * 1.3) if walking else 0.0
        m.put_segment(f"hackle{i}", q, q + Vector((-0.050, 0, 0.052 + lift)), 0.022, 0.014)
    m.objects["bib"].location = chest + Vector((0.080, 0, -0.030))
    # the tail's bushy middle
    tail = m.objects["tail_a"].data.splines[0].points
    mid = tail[len(tail) * 2 // 3].co
    m.objects["tailfluff"].location = Vector((mid[0], mid[1], mid[2]))
    for sign, k in ((1, "l"), (-1, "r")):
        # pale cheek tufts sweeping back and down from under the eye
        root = head + Vector((0.000, 0.066 * sign, -0.020))
        m.put_segment(f"cheek_{k}", root, root + Vector((-0.060, 0.040 * sign, -0.040)), 0.030, 0.020)
        m.put_segment(f"cheek2_{k}", root + Vector((0.020, 0, -0.016)), root + Vector((-0.030, 0.034 * sign, -0.070)), 0.024, 0.016)
        # a dark brow slanting down toward the nose: the eye sits in its shadow
        eye = m.objects[f"eye_{k}"].location
        m.put_segment(f"brow_{k}", eye + Vector((-0.030, 0.006 * sign, 0.020)), eye + Vector((0.030, -0.006 * sign, 0.010)), 0.011)
        # the mouth line along the side of the muzzle
        m.put_segment(f"mouth_{k}", head + Vector((0.060, 0.034 * sign, -0.040)), tip + Vector((-0.030, 0.020 * sign, -0.014)), 0.007)
        r0, r1 = s["ear_root"], s["ear_tip"]
        ear_tip = head + Vector((r1[0], r1[1] * sign, r1[2]))
        ear_root = head + Vector((r0[0], r0[1] * sign, r0[2]))
        m.put_segment(f"eartip_{k}", ear_root.lerp(ear_tip, 0.55), ear_tip + (ear_tip - ear_root) * 0.10, s["ear_r"] * 0.62, s["ear_r"] * 0.40)


def build(model_cls, facing):
    m = Q.build(model_cls, facing, SPEC, PARTS)
    build_fur(m)
    return m


def pose(m, t):
    p = Q.pose(m, t)
    pose_fur(m, p, SPEC)


def assign_depth_parts(m, depth_of):
    Q.assign_depth_parts(m, depth_of)
