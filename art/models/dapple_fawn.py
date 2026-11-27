"""Dapple Fawn (Floor 1 small game on the empty lawns, Q94): a four-legged creature built on art/models/quadruped.py.
Harmless and shy; it bolts when you come near.

Identity (art/QUADRUPED_RULES.md step 1):
  Coat:      cool dun-taupe (Tibia's deer is red-brown) with a cream belly and throat.
  Signature: a dark stripe down the spine with two rows of bright cream dapples either side of it (the spots a fawn
             wears in its first summer), seen from every direction from above; big dark-rimmed ears.
  Attitude:  young and shy: a short body on long thin legs, a big head held up, ears wide and turning, light steps.

Detail (art/DETAIL_RULES.md): a fawn's anatomy: a short neck and a big head for its body, huge ears with dark rims and
pale insides, a dark wet nose and a mouth line, large dark eyes, a slim body (chest, waist, rump), long two-part legs
with knobby joints and tiny dark hooves, a short tail with a white underside. Marks: big = the spine stripe;
medium = the cream belly and rump; small = the dapples and the dark ear rims.
Real proportion: a white-tailed fawn stands about as tall at the shoulder as its body is long; its legs are over half
its height; its ears are about two-thirds the length of its head.
"""
from __future__ import annotations

import math

from mathutils import Vector

import quadruped as Q

NAME = "dapple_fawn"
WALK_FRAMES = 8
PALETTE = "dapple_fawn"
HEIGHT_SHEAR = 0.30
LEAN = 14.0
REFERENCE = "look_31.png"    # Tibia's Deer (comparison only, never shipped)
SIZE = 1.40
GROUND_STRETCH = 1.2
AUTO_PLACE = (1, 1)
SIGNATURE = ["spot", "stripe"]
CHECK = {"eye": 1, "size": (0.70, 1.05)}   # a fawn: smaller than Tibia's grown deer on purpose
HEAD_PARTS = ["head", "snout", "nose", "ear", "rim", "inner", "eye", "line"]

PARTS = Q.PARTS + ["spot", "stripe", "rim", "inner", "line"]
PIXEL_RULES = Q.pixel_rules(
    weight={"spot": 4.0, "stripe": 2.2, "rim": 3.0, "inner": 2.6, "line": 3.0, "eye": 9.0, "ear": 2.4},
    thin={"spot": 2, "stripe": 2, "rim": 2, "inner": 2, "line": 2, "eye": 2},
    soft=[["body", "belly", "spot", "stripe"], ["head", "snout", "nose", "line", "eye"], ["ear", "rim", "inner"]],
    texture={"body": [0.35, 0.10], "head": [0.35, 0.08]},
    selout=["ear"],
)

SPEC = Q.spec(
    hip=(-0.100, 0.330), hip_r=(0.088, 0.066, 0.068),
    chest=(0.050, 0.338), chest_r=(0.092, 0.068, 0.076),
    belly_r=(0.122, 0.052, 0.036), belly_drop=0.044,
    head=(0.180, 0.440), head_r=(0.078, 0.062, 0.066),              # a big head for its body, held up
    snout_tip=(0.315, 0.400), snout_r=(0.042, 0.028),
    nose_r=(0.013, 0.016, 0.013),
    eye=(0.034, 0.044, 0.022), eye_r=0.013,
    ear_root=(-0.025, 0.040, 0.040), ear_tip=(-0.055, 0.105, 0.110), ear_r=0.028,   # big ears, held wide
    front_x=0.070, hind_x=-0.115, leg_top_z=0.300,
    front_y=0.048, hind_y=0.046, front_feet_y=0.072, hind_feet_y=0.068,
    upper=0.165, lower=0.160, leg_r=0.014, paw_r=(0.016, 0.013, 0.011),
    shoulder_r=(0.042, 0.028, 0.062), haunch_r=(0.052, 0.030, 0.068),
    stride=0.120, lift=0.080, bob=0.016, nod=0.016,
    tail_len=0.050, tail_r=(0.016, 0.012), tail_raise=1.2, tail_curl=0.0, tail_split=0.45,
)
SPOTS = [(0.07, 0.036), (-0.02, 0.040), (-0.11, 0.038), (0.03, 0.062), (-0.07, 0.062)]   # (x along the back, distance off the spine)


def build(model_cls, facing):
    m = Q.build(model_cls, facing, SPEC, PARTS)
    m.ellipsoid("neck", "body", radii=(0.050, 0.042, 0.080), segments=12, rings=8)
    m.ellipsoid("throat", "belly", radii=(0.034, 0.032, 0.050), segments=10, rings=6)
    m.ellipsoid("rump", "belly", radii=(0.036, 0.050, 0.046), segments=10, rings=6)
    m.tube("stripe", "stripe", points=8)
    m.capsule("mouth", "line", segments=6)
    for k in ("l", "r"):
        for i in range(len(SPOTS)):
            m.ellipsoid(f"spot{i}_{k}", "spot", radii=(0.010, 0.009, 0.007), segments=8, rings=4)
        m.tube(f"rim_{k}", "rim", points=6)
        m.capsule(f"inner_{k}", "inner", segments=6)
    return m


def _on_back(chest, hip, x, side):
    """A point on the top of the body at x (in the animal's frame) and `side` off the spine."""
    span = chest.x - hip.x
    u = max(0.0, min(1.0, (x - hip.x) / span))
    c = hip.lerp(chest, u)
    r = SPEC["hip_r"][2] + (SPEC["chest_r"][2] - SPEC["hip_r"][2]) * u
    w = SPEC["hip_r"][1] + (SPEC["chest_r"][1] - SPEC["hip_r"][1]) * u
    k = min(0.95, abs(side) / w)
    return Vector((x, side, c.z + r * math.sqrt(1 - k * k) * 1.02))


def pose(m, t):
    p = Q.pose(m, t)
    chest, hip, head = p["chest"], p["hip"], p["head"]
    m.objects["neck"].location = chest.lerp(head, 0.48)
    m.objects["throat"].location = chest.lerp(head, 0.40) + Vector((0.040, 0, -0.030))
    m.objects["rump"].location = hip + Vector((-0.070, 0, 0.004))
    xs = [hip.x - 0.060 + (chest.x + 0.040 - hip.x + 0.060) * i / 7 for i in range(8)]
    m.set_tube("stripe", [tuple(_on_back(chest, hip, x, 0.0)) for x in xs], [0.016] * 8)
    for sign, k in ((1, "l"), (-1, "r")):
        for i, (dx, off) in enumerate(SPOTS):
            m.objects[f"spot{i}_{k}"].location = _on_back(chest, hip, (chest.x + hip.x) / 2 + dx, off * sign)
        # dark rim round the outer edge of the big ear, pale inside
        r0, r1 = SPEC["ear_root"], SPEC["ear_tip"]
        root = head + Vector((r0[0], r0[1] * sign, r0[2]))
        end = head + Vector((r1[0], r1[1] * sign, r1[2]))
        d = end - root
        up = Vector((0, 0, 1))
        rim = [root + d * u + up * (SPEC["ear_r"] * 0.85 * math.sin(math.pi * min(u, 0.95))) for u in (0.2, 0.4, 0.6, 0.8, 0.95, 1.05)]
        m.set_tube(f"rim_{k}", [tuple(q) for q in rim], [0.007] * 6)
        m.put_segment(f"inner_{k}", root + d * 0.25 + Vector((0.012, 0, 0)), root + d * 0.75 + Vector((0.012, 0, 0)), 0.012)
    tip = p["snout_tip"]
    m.put_segment("mouth", tip + Vector((-0.010, 0.018, -0.022)), tip + Vector((-0.010, -0.018, -0.022)), 0.005)


def assign_depth_parts(m, depth_of):
    Q.assign_depth_parts(m, depth_of)
