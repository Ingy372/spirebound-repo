"""Black Crawler (Floor 1, the Underkeep): model + scuttle cycle.

It wore the rat's sprite (ART_COUNT.md: "a different animal, so the look is wrong"). A black crawler in a dungeon:
a giant cave beetle.

Identity (art/CRAWLER_RULES.md step 1):
  Coat:      glossy blue-black wing cases with a cold steel-blue sheen (Tibia's beetles are brown or bronze), a
             darker head and legs.
  Signature: big sickle mandibles that open SIDEWAYS (C2) with an amber inner edge (C3), a pale seam down the middle
             of the back where the wing cases meet (C6), two small blood-red eyes.
  Attitude:  low and wide, head down, scuttling fast on a tripod gait.

Detail (art/DETAIL_RULES.md): head, a shield-like pronotum and two domed wing cases (three lumps, never one ball);
mandibles with an inner tooth; elbowed antennae; six legs in two parts with spiky feet; a seam line and two rows of
pits on the wing cases; a pale rim round the wing cases (rule 7).
Look-alike (size only): Tibia's Beetle / Scarab.
"""
from __future__ import annotations

import math

from mathutils import Vector

NAME = "crawler"
WALK_FRAMES = 8
PALETTE = "crawler"
HEIGHT_SHEAR = 0.30
LEAN = 10.0
REFERENCE = None
SIZE = 1.30
GROUND_STRETCH = 1.25
AUTO_PLACE = (1, 1)
SIGNATURE = ["mandible", "seam"]
HEAD_PARTS = ["head", "mandible", "eye"]
LEG_PARTS = ["leg"]
CHECK = {"size": (0.85, 1.6), "legs_side": 0.03, "legs_updown": 0.0, "head": 0.06}   # a low, wide beetle: thin legs
PIXEL_RULES = {
    "weight": {"eye": 5.0, "mandible": 3.0, "inner": 3.6, "leg": 2.4, "antenna": 3.0, "seam": 3.4, "rim": 2.4,
               "pit": 3.0, "head": 1.4, "pronotum": 1.2},
    "thin": {"eye": 2, "mandible": 2, "inner": 2, "leg": 2, "antenna": 2, "seam": 2, "rim": 2, "pit": 2},
    "soft": [["shell", "seam", "rim", "pit"], ["pronotum"], ["head", "eye"], ["mandible", "inner"]],
    "no_outline": ["antenna"],
    "fur": [],
    "selout": ["shell", "pronotum"],
    "texture": {"shell": [0.25, 0.05], "pronotum": [0.3, 0.05], "head": [0.4, 0.05]},
    "bands": [0.30, 0.42, 0.53, 0.63, 0.72, 0.81, 0.90],
}

PARTS = ["none", "shell", "pronotum", "head", "eye", "mandible", "inner", "leg", "antenna", "seam", "rim", "pit"]

BODY_Z = 0.120
LEGS = [(0.070, 0.10, 0.75), (0.000, 0.14, 0.05), (-0.080, 0.12, -0.70)]   # hip x, reach, forward angle


def build(model_cls, facing):
    m = model_cls(facing, PARTS)
    for k in ("l", "r"):
        m.ellipsoid(f"shell_{k}", "shell", radii=(0.150, 0.072, 0.072), segments=18, rings=10)
        m.tube(f"rim_{k}", "rim", points=6)
        for i in range(3):
            m.ellipsoid(f"pit{i}_{k}", "pit", radii=(0.012, 0.010, 0.006), segments=6, rings=4)
        m.capsule(f"mand_{k}", "mandible")
        m.capsule(f"tooth_{k}", "inner")
        m.ellipsoid(f"eye_{k}", "eye", radii=(0.014, 0.012, 0.012), segments=8, rings=6)
        m.tube(f"antenna_{k}", "antenna", points=4)
        for j in range(3):
            m.capsule(f"femur{j}_{k}", "leg", segments=6)
            m.capsule(f"tibia{j}_{k}", "leg", segments=6)
    m.tube("seam", "seam", points=5)
    m.ellipsoid("pronotum", "pronotum", radii=(0.070, 0.098, 0.050), segments=16, rings=8)
    m.ellipsoid("head", "head", radii=(0.052, 0.064, 0.040), segments=14, rings=8)
    return m


def pose(m, t):
    a = 0.0 if t is None else 2 * math.pi * t
    walking = t is not None
    bob = 0.006 * abs(math.sin(2 * a)) if walking else 0.0
    body = Vector((-0.020, 0, BODY_Z + bob))
    for s, k in ((1, "l"), (-1, "r")):
        m.objects[f"shell_{k}"].location = body + Vector((-0.040, 0.050 * s, 0.010))
        rim = [body + Vector((0.100 - 0.050 * i, (0.090 + 0.014 * math.sin(math.pi * i / 5)) * s, 0.002)) for i in range(6)]
        m.set_tube(f"rim_{k}", [tuple(p) for p in rim], [0.007] * 6)
        for i in range(3):
            m.objects[f"pit{i}_{k}"].location = body + Vector((0.040 - 0.070 * i, 0.050 * s, 0.078))
    seam = [body + Vector((0.100 - 0.055 * i, 0, 0.082 - 0.006 * abs(i - 2))) for i in range(5)]
    m.set_tube("seam", [tuple(p) for p in seam], [0.007] * 5)
    pro = body + Vector((0.130, 0, 0.008))
    m.objects["pronotum"].location = pro
    head = pro + Vector((0.085, 0, -0.012))
    m.objects["head"].location = head
    snap = 0.35 + (0.25 * abs(math.sin(a)) if walking else 0.0)    # the mandibles work as it scuttles
    for s, k in ((1, "l"), (-1, "r")):
        m.objects[f"eye_{k}"].location = head + Vector((0.020, 0.052 * s, 0.018))
        root = head + Vector((0.040, 0.034 * s, -0.004))
        mid = root + Vector((0.060, (0.040 + 0.030 * snap) * s, 0.004))
        tip = mid + Vector((0.050, -0.040 * s, 0.000))
        m.put_segment(f"mand_{k}", root, mid, 0.016, 0.013)
        m.put_segment(f"tooth_{k}", mid, tip, 0.012, 0.005)          # the inner, amber-edged hook
        base = head + Vector((0.030, 0.040 * s, 0.024))
        pts = [base, base + Vector((0.030, 0.030 * s, 0.030)), base + Vector((0.070, 0.050 * s, 0.020)),
               base + Vector((0.100, 0.070 * s, -0.004))]
        m.set_tube(f"antenna_{k}", [tuple(p) for p in pts], [0.006, 0.006, 0.005, 0.004])
        # tripod gait: front and back legs of one side move with the middle leg of the other
        for j, (hx, reach, ang) in enumerate(LEGS):
            phase = a + (0 if (j % 2 == 0) == (s > 0) else math.pi)
            step = 0.040 * math.sin(phase) if walking else 0.0
            lift = 0.025 * max(0.0, math.cos(phase)) if walking else 0.0
            hip = body + Vector((hx + 0.060, 0.070 * s, -0.020))
            knee = hip + Vector((reach * 0.5 * math.sin(ang) + step * 0.5, (0.090 + reach * 0.3) * s, 0.040 + lift))
            foot = hip + Vector((reach * math.sin(ang) + step, (0.150 + reach * 0.3) * s, -BODY_Z + 0.015 + lift))
            m.put_segment(f"femur{j}_{k}", hip, knee, 0.014)
            m.put_segment(f"tibia{j}_{k}", knee, foot, 0.010, 0.006)


def assign_depth_parts(m, depth_of):
    return None
