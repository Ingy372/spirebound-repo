"""Thistle Hen (Floor 1 small game on the empty lawns, Q94): a ground bird with its own body (art/CRAWLER_RULES.md).
Harmless; it scurries off when you come near.

Identity (art/CRAWLER_RULES.md step 1):
  Coat:      slate-blue plumage freckled with white (Tibia's chicken is white with a red comb), a rust-red breast,
             a bronze-black tail.
  Signature: a spiky crest of thistle-purple feathers with lilac tips on top of the head (like a thistle head, seen
             from every direction), and the white freckles across the back and wings.
  Attitude:  busy and fussy: tail cocked up, chest out, the head jerking forward and back with every step.

Detail (art/DETAIL_RULES.md): a ground bird's anatomy: an egg-shaped body with a full breast, folded wings with a
dark feather edge, a fan of upright tail feathers, a small head on a short neck, a hooked horn beak, a red wattle,
a round eye, two thin scaly legs with three toes forward and one back. Marks: big = the rust breast; medium = the
folded wings and their edge line; small = the white freckles, the lilac crest tips.
Real proportion: a partridge-sized hen is about as long as it is tall; its head is about a fifth of its height; its
legs show for about a third of its height.
"""
from __future__ import annotations

import math

from mathutils import Euler, Vector

NAME = "thistle_hen"
WALK_FRAMES = 8
PALETTE = "thistle_hen"
HEIGHT_SHEAR = 0.30
LEAN = 10.0
REFERENCE = "look_111.png"   # Tibia's Chicken (comparison only, never shipped)
SIZE = 1.70
GROUND_STRETCH = 1.0
AUTO_PLACE = (1, 1)
SIGNATURE = ["crest", "speck"]
HEAD_PARTS = ["head", "beak", "wattle", "eye", "crest", "crestip"]
LEG_PARTS = ["leg", "foot"]
CHECK = {"eye": 1, "signature": 3, "legs_side": 0.04, "legs_updown": 0.02, "head": 0.08}   # a tiny bird: thin legs, one-pixel eye

PARTS = ["none", "body", "breast", "wing", "tail", "head", "beak", "wattle", "eye", "crest", "crestip", "leg", "foot",
         "speck", "line"]
PIXEL_RULES = {
    "weight": {"eye": 9.0, "beak": 4.0, "wattle": 3.5, "crest": 3.0, "crestip": 4.5, "leg": 2.6, "foot": 2.8,
               "speck": 4.0, "line": 3.0, "wing": 1.4, "tail": 1.6, "breast": 1.2, "head": 1.4},
    "thin": {"eye": 2, "beak": 2, "wattle": 2, "crest": 2, "crestip": 2, "leg": 3, "foot": 2, "speck": 2, "line": 2},
    "soft": [["body", "breast", "speck"], ["wing", "line", "speck"], ["head", "eye", "beak", "wattle"],
             ["crest", "crestip"], ["leg", "foot"]],
    "no_outline": [],
    "fur": [],
    "texture": {"body": [0.6, 0.2], "wing": [0.6, 0.15], "breast": [0.4, 0.1], "tail": [0.5, 0.0], "head": [0.4, 0.1]},
    "bands": [0.36, 0.48, 0.58, 0.67, 0.76, 0.84, 0.92],
    "selout": ["body", "wing", "tail"],
}

SPECKS = [(0.02, 0.045), (-0.04, 0.030), (-0.07, 0.058), (0.04, 0.020), (-0.01, 0.065), (-0.09, 0.025)]
CREST = 6
TAIL = 5


def build(model_cls, facing):
    m = model_cls(facing, PARTS)
    m.ellipsoid("body", "body", radii=(0.105, 0.072, 0.072), segments=18, rings=10)
    m.ellipsoid("rump", "body", radii=(0.060, 0.060, 0.058), segments=12, rings=8)
    m.ellipsoid("breast", "breast", radii=(0.064, 0.062, 0.068), segments=14, rings=8)
    m.ellipsoid("neck", "head", radii=(0.034, 0.032, 0.046), segments=10, rings=6)
    m.ellipsoid("head", "head", radii=(0.044, 0.040, 0.041), segments=14, rings=8)
    m.cone("beak", "beak", segments=8)
    m.ellipsoid("wattle", "wattle", radii=(0.012, 0.010, 0.016), segments=8, rings=4)
    for k in ("l", "r"):
        m.ellipsoid(f"eye_{k}", "eye", radii=(0.010, 0.010, 0.010), segments=8, rings=4)
        m.ellipsoid(f"wing_{k}", "wing", radii=(0.088, 0.026, 0.050), segments=14, rings=8)
        m.tube(f"edge_{k}", "line", points=6)
        m.capsule(f"thigh_{k}", "body", segments=8)
        m.capsule(f"shank_{k}", "leg", segments=6)
        for j in range(4):
            m.cone(f"toe{j}_{k}", "foot", segments=5)
        for i in range(len(SPECKS)):
            m.ellipsoid(f"speck{i}_{k}", "speck", radii=(0.008, 0.008, 0.006), segments=6, rings=4)
    for i in range(CREST):
        m.cone(f"crest{i}", "crest", segments=6)
        m.ellipsoid(f"ctip{i}", "crestip", radii=(0.008, 0.008, 0.009), segments=6, rings=4)
    for i in range(TAIL):
        m.cone(f"tail{i}", "tail", segments=6)
    return m


def pose(m, t):
    walking = t is not None
    a = 2 * math.pi * (t or 0.0)
    bob = 0.008 * (0.5 + 0.5 * math.cos(2 * a)) if walking else 0.0
    thrust = 0.020 * math.sin(2 * a) if walking else 0.0          # the hen's head jerks forward and back each step
    body = Vector((0, 0, 0.180 + bob))
    m.objects["body"].location = body
    m.objects["body"].rotation_mode = "XYZ"
    m.objects["body"].rotation_euler = Euler((0, 0.25, 0))       # tail end raised
    m.objects["rump"].location = body + Vector((-0.070, 0, 0.022))
    m.objects["breast"].location = body + Vector((0.060, 0, 0.000))
    head = body + Vector((0.110 + thrust, 0, 0.120))
    m.objects["neck"].location = body.lerp(head, 0.55) + Vector((0.010, 0, 0))
    m.objects["head"].location = head
    m.put_segment("beak", head + Vector((0.030, 0, -0.004)), head + Vector((0.074, 0, -0.016)), 0.016, 0.003)
    m.objects["wattle"].location = head + Vector((0.030, 0, -0.036))
    for i in range(CREST):
        u = i / (CREST - 1)
        side = 0.018 * math.sin(i * 2.4)
        base = head + Vector((0.020 - 0.040 * u, side * 0.6, 0.030))
        tip = base + Vector((-0.012 - 0.020 * u, side * 1.6, 0.058 - 0.012 * abs(u - 0.4)))
        if walking:
            tip += Vector((-0.006 * math.sin(2 * a + i), 0, 0))
        m.put_segment(f"crest{i}", base, tip, 0.012, 0.004)
        m.objects[f"ctip{i}"].location = tip
    for i in range(TAIL):
        u = (i - (TAIL - 1) / 2) / ((TAIL - 1) / 2)
        base = body + Vector((-0.110, 0.020 * u, 0.040))
        tip = base + Vector((-0.060, 0.045 * u, 0.110 - 0.020 * abs(u)))
        m.put_segment(f"tail{i}", base, tip, 0.026, 0.012)
    for s, k in ((1, "l"), (-1, "r")):
        m.objects[f"eye_{k}"].location = head + Vector((0.018, 0.036 * s, 0.010))
        w = m.objects[f"wing_{k}"]
        w.location = body + Vector((-0.010, 0.060 * s, 0.018))
        w.rotation_mode = "XYZ"
        w.rotation_euler = Euler((0.30 * s, 0.30, 0))
        edge = [w.location + Vector((0.060 - 0.030 * j, 0.022 * s, -0.030 + 0.006 * j)) for j in range(6)]
        m.set_tube(f"edge_{k}", [tuple(q) for q in edge], [0.006] * 6)
        for i, (x, off) in enumerate(SPECKS):
            z = 0.072 * math.sqrt(max(0.1, 1 - (x / 0.11) ** 2 - (off / 0.075) ** 2)) + 0.004
            m.objects[f"speck{i}_{k}"].location = body + Vector((x, off * s, z + 0.012))
        # legs: thigh under the body, a thin shank to the foot; feet alternate
        phase = 0.0 if k == "l" else 0.5
        if walking:
            uu = (t + phase) % 1.0
            if uu < 0.5:
                fx, fz = 0.040 * (1 - 4 * uu), 0.0
            else:
                kk = (uu - 0.5) / 0.5
                fx, fz = 0.040 * (-1 + 2 * (0.5 - 0.5 * math.cos(math.pi * kk))), 0.040 * math.sin(math.pi * kk)
        else:
            fx, fz = 0.0, 0.0
        hipj = body + Vector((0.005, 0.034 * s, -0.050))
        foot = Vector((0.010 + fx, 0.044 * s, 0.010 + fz))
        knee = hipj.lerp(foot, 0.35) + Vector((-0.010, 0.004 * s, 0))
        m.put_segment(f"thigh_{k}", hipj, knee, 0.024, 0.016)
        m.put_segment(f"shank_{k}", knee, foot, 0.012)
        for j in range(4):
            fan = (-0.5, 0.0, 0.5, math.pi)[j]
            ln = 0.034 if j < 3 else 0.020
            m.put_segment(f"toe{j}_{k}", foot, foot + Vector((ln * math.cos(fan), ln * math.sin(fan) * 0.8, -0.004)), 0.007)


def assign_depth_parts(m, depth_of):
    return None
