"""Pale Stag (Floor 1 rare roamer, levels 14-24; adventure design 4.4): a four-legged creature built on
art/models/quadruped.py. It flees at speed and gores with its antlers when cornered.

Identity (art/QUADRUPED_RULES.md step 1):
  Coat:      moon-pale ash-white with cool blue-grey shadows (Tibia's deer is red-brown), a charcoal face mask and
             charcoal lower legs, so the pale body floats like a ghost between the trees.
  Signature: a great crown of branching antlers (two beams, four tines each) in pale bone with frost-blue tips, seen
             from every direction from above; and a dark shaggy ruff at the throat. Pale-blue eyes.
  Attitude:  proud and wary: head high on a long neck, ears turned out, long legs, light high steps.

Detail (art/DETAIL_RULES.md): a deer's anatomy: deep chest, slim waist, round haunches (body in three lumps plus a
neck), a long narrow face with a dark nose and a pale eye ring, branching antlers with tines, the throat ruff, a short
pale tail, two-part legs with small dark hooves. Marks: big = the dark ruff; medium = the face mask; small = the
frost-blue antler tips.
Real proportion: a red deer stands about as tall at the shoulder as its body is long; the antlers of a big stag
reach about as high above the head as the head is long, times two.
"""
from __future__ import annotations

import math

from mathutils import Vector

import quadruped as Q

NAME = "pale_stag"
WALK_FRAMES = 8
PALETTE = "pale_stag"
HEIGHT_SHEAR = 0.30
LEAN = 14.0
REFERENCE = "look_31.png"    # Tibia's Deer (comparison only, never shipped)
SIZE = 1.60
GROUND_STRETCH = 1.3
AUTO_PLACE = (1, 1)
SIGNATURE = ["antler", "ruff"]
CHECK = {"eye": 1, "size": (0.85, 1.35)}   # a great stag beside Tibia's fawn-sized deer: bigger on purpose
HEAD_PARTS = ["head", "snout", "nose", "mask", "ring", "eye", "ear"]

PARTS = Q.PARTS + ["antler", "tine", "ruff", "mask", "ring"]
PIXEL_RULES = Q.pixel_rules(
    weight={"antler": 2.8, "tine": 4.0, "ruff": 1.8, "mask": 1.8, "ring": 4.0, "eye": 9.0},
    thin={"antler": 2, "tine": 2, "ring": 2, "eye": 2},
    soft=[["body", "belly", "ruff"], ["head", "mask", "ring", "eye"], ["antler", "tine"]],
    texture={"body": [0.35, 0.1], "head": [0.4, 0.1], "ruff": [1.0, 0.3], "antler": [0.8, 0.0]},
    selout=["antler", "body", "ruff"],
)

SPEC = Q.spec(
    hip=(-0.115, 0.335), hip_r=(0.098, 0.076, 0.074),
    chest=(0.055, 0.350), chest_r=(0.108, 0.080, 0.088),
    belly_r=(0.142, 0.060, 0.040), belly_drop=0.050,
    head=(0.215, 0.445), head_r=(0.084, 0.066, 0.070),              # head high on a long neck: wary
    snout_tip=(0.355, 0.410), snout_r=(0.044, 0.036),
    nose_r=(0.012, 0.016, 0.012),
    eye=(0.038, 0.042, 0.022), eye_r=0.011,
    ear_root=(-0.020, 0.040, 0.030), ear_tip=(-0.040, 0.100, 0.050), ear_r=0.018,
    front_x=0.080, hind_x=-0.135, leg_top_z=0.305,
    front_y=0.055, hind_y=0.052, front_feet_y=0.082, hind_feet_y=0.078,
    upper=0.175, lower=0.165, leg_r=0.017, paw_r=(0.019, 0.015, 0.012),
    shoulder_r=(0.050, 0.032, 0.072), haunch_r=(0.060, 0.034, 0.076),
    stride=0.130, lift=0.085, bob=0.018, nod=0.014,
    tail_len=0.055, tail_r=(0.016, 0.010), tail_raise=1.0, tail_curl=0.0, tail_split=0.5,
)
BEAM_N = 9
TINES = (0.30, 0.50, 0.70, 0.92)    # where along the beam each tine springs


def build(model_cls, facing):
    m = Q.build(model_cls, facing, SPEC, PARTS)
    m.ellipsoid("neck", "body", radii=(0.058, 0.048, 0.100), segments=12, rings=8)
    m.ellipsoid("ruff", "ruff", radii=(0.050, 0.056, 0.070), segments=12, rings=8)      # throat ruff
    m.ellipsoid("mane", "ruff", radii=(0.070, 0.040, 0.040), segments=12, rings=8)      # ...running up the neck's top
    m.ellipsoid("mask", "mask", radii=(0.060, 0.046, 0.040), segments=12, rings=8)
    m.ellipsoid("rump", "belly", radii=(0.050, 0.058, 0.054), segments=12, rings=8)
    for k in ("l", "r"):
        m.tube(f"beam_{k}", "antler", points=BEAM_N)
        for j in range(len(TINES)):
            m.cone(f"tine{j}_{k}", "antler", segments=5)
            m.ellipsoid(f"tip{j}_{k}", "tine", radii=(0.010, 0.010, 0.012), segments=6, rings=4)
        m.ellipsoid(f"ring_{k}", "ring", radii=(0.008, 0.015, 0.013), segments=8, rings=4)
    return m


def pose(m, t):
    p = Q.pose(m, t)
    chest, hip, head = p["chest"], p["hip"], p["head"]
    neck = chest.lerp(head, 0.5)
    m.objects["neck"].location = neck
    m.objects["ruff"].location = chest.lerp(head, 0.35) + Vector((0.035, 0, -0.030))
    m.objects["mane"].location = neck + Vector((-0.020, 0, 0.060))
    m.objects["mane"].rotation_mode = "XYZ"
    m.objects["mane"].rotation_euler = (0, -0.7, 0)
    m.objects["mask"].location = head + Vector((0.060, 0, -0.008))
    m.objects["rump"].location = hip + Vector((-0.072, 0, 0.012))
    sway = 0.010 * math.sin(p["a"] * 2) if p["walking"] else 0.0
    for sign, k in ((1, "l"), (-1, "r")):
        root = head + Vector((-0.018 + 0.012 * sign, 0.024 * sign, 0.050))
        pts, radii = [], []
        for i in range(BEAM_N):
            u = i / (BEAM_N - 1)
            # the beam: up, back and out, then the top curving forward (a stag's crown)
            # the two beams lean apart front-to-back as well as sideways, so both read from the side
            pts.append(root + Vector((-0.080 * u + 0.060 * u ** 3 + sway * u + 0.040 * sign * u,
                                      sign * (0.085 * u + 0.025 * math.sin(u * math.pi)), 0.210 * u)))
            radii.append(0.013 * (1 - 0.6 * u) + 0.004)
        m.set_tube(f"beam_{k}", [tuple(q) for q in pts], radii)
        for j, u in enumerate(TINES):
            c = pts[int(round(u * (BEAM_N - 1)))]
            # brow tines point forward, the upper ones up and a little out
            d = Vector((0.070, 0.010 * sign, 0.020)) if j == 0 else Vector((0.030, 0.022 * sign, 0.060 - 0.008 * j))
            m.put_segment(f"tine{j}_{k}", c, c + d, 0.009, 0.003)
            m.objects[f"tip{j}_{k}"].location = c + d
        m.objects[f"ring_{k}"].location = m.objects[f"eye_{k}"].location + Vector((0, 0.004 * sign, 0.004))


def assign_depth_parts(m, depth_of):
    Q.assign_depth_parts(m, depth_of)
