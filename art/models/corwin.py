"""Corwin, the fisher (Floor 1): model + walk cycle.

ART_REQUESTS.md: "a lean fisher in a patched oilskin coat and a floppy hat, a fishing rod over his shoulder".
Original design: knee-length ochre oilskin coat with two darker patches, soft wide-brimmed hat drooping at the
sides, fishing rod resting on the right shoulder with a little line hanging from the tip, grey trousers, boots.
Runs inside Blender via art/pipeline/render_creature.py. Faces +X (east), +Y left, +Z up; sizes in tiles.
"""
from __future__ import annotations

import math

from mathutils import Euler, Vector

NAME = "corwin"
WALK_FRAMES = 8
PALETTE = "corwin"
REFERENCE = "outfit_128.png"
PROJECTION = "oblique"
CANVAS_OFFSET = (8, 8)
PIXEL_RULES = {
    "weight": {"eye": 9.0, "hand": 2.4, "rod": 3.0, "line": 2.5, "patch": 2.0, "boot": 1.4, "hat": 1.2},
    "thin": {"eye": 3, "hand": 3, "rod": 2, "line": 2, "patch": 3},
    "soft": [["coat", "patch"], ["skin", "hair", "eye"], ["hand", "skin"], ["pants", "boot"], ["rod", "line"]],
    "no_outline": ["line"],
    "fur": [],
    "selout": ["coat", "hat", "skin"],
}

PARTS = ["none", "skin", "eye", "hair", "hat", "coat", "patch", "pants", "boot", "hand", "rod", "line"]

HIP_Z, KNEE_LEN, SHIN_LEN = 0.50, 0.25, 0.25
HIP_Y = 0.066
LEG_R = 0.050
TORSO = Vector((0.0, 0.0, 0.70)); TORSO_R = (0.100, 0.150, 0.190)       # lean
SKIRT_TOP, SKIRT_BOTTOM = 0.60, 0.32
SKIRT_R = (0.130, 0.165)
HEAD = Vector((0.010, 0.0, 0.975)); HEAD_R = (0.145, 0.136, 0.158)
SHOULDER = Vector((0.0, 0.155, 0.825))
UPPER_ARM, FOREARM = 0.19, 0.18
ARM_R = 0.050
STRIDE, LIFT, STANCE = 0.13, 0.060, 0.5
BODY_SCALE = (1.15, 1.18, 0.80)


def build(model_cls, facing):
    import bpy
    body = bpy.data.objects.new("BodyScale", None)
    body.parent = facing
    body.scale = BODY_SCALE
    bpy.context.scene.collection.objects.link(body)
    m = model_cls(body, PARTS)
    for k in ("l", "r"):
        m.capsule(f"thigh_{k}", "pants")
        m.capsule(f"shin_{k}", "pants")
        m.capsule(f"bootleg_{k}", "boot")
        m.ellipsoid(f"boot_{k}", "boot", radii=(0.072, 0.046, 0.050), segments=12, rings=8)
        m.capsule(f"upper_{k}", "coat")
        m.capsule(f"fore_{k}", "coat")
        m.ellipsoid(f"hand_{k}", "hand", radii=(0.038, 0.032, 0.040), segments=10, rings=8)
    m.ellipsoid("torso", "coat", radii=TORSO_R)
    m.frustum("skirt", "coat", top_ratio=0.75)
    m.ellipsoid("patch_a", "patch", radii=(0.020, 0.050, 0.045), segments=10, rings=6)
    m.ellipsoid("patch_b", "patch", radii=(0.050, 0.020, 0.045), segments=10, rings=6)
    m.ellipsoid("head", "skin", radii=HEAD_R)
    m.ellipsoid("hair", "hair", radii=(0.150, 0.150, 0.140))
    for k in ("l", "r"):
        m.ellipsoid(f"eye_{k}", "eye", radii=(0.012, 0.012, 0.018), segments=8, rings=6)
    m.ellipsoid("brim", "hat", radii=(0.180, 0.180, 0.028), segments=24, rings=8)
    m.ellipsoid("crown", "hat", radii=(0.120, 0.115, 0.090), segments=16, rings=8)
    m.capsule("rod", "rod")
    m.tube("line", "line", points=6)
    return m


def _two_bone(a, target, l1, l2, bend_hint):
    d = target - a
    dist = min(d.length, l1 + l2 - 1e-4)
    d.normalize()
    side = d.cross(bend_hint)
    if side.length < 1e-6:
        side = Vector((0, 1, 0))
    bend = side.cross(d).normalized()
    x = (l1 ** 2 + dist ** 2 - l2 ** 2) / (2 * dist)
    h = math.sqrt(max(l1 ** 2 - x ** 2, 0.0))
    return a + d * x + bend * h, a + d * dist


def _foot(t, phase):
    if t is None:
        return 0.0, 0.0
    u = (t + phase) % 1.0
    if u < STANCE:
        return STRIDE * (1 - 2 * u / STANCE), 0.0
    k = (u - STANCE) / (1 - STANCE)
    ease = 0.5 - 0.5 * math.cos(math.pi * k)
    return STRIDE * (-1 + 2 * ease), LIFT * math.sin(math.pi * k)


def pose(m, t):
    a = 0.0 if t is None else 2 * math.pi * t
    walking = t is not None
    bob = 0.014 * (0.5 + 0.5 * math.cos(2 * a)) if walking else 0.0
    up = Vector((0, 0, bob))
    m.objects["torso"].location = TORSO + up
    sk = m.objects["skirt"]
    sk.location = Vector((0, 0, SKIRT_BOTTOM)) + up
    sk.rotation_mode = "XYZ"
    sk.rotation_euler = Euler((0.04 * math.sin(a) if walking else 0.0, 0, 0))
    sk.scale = (SKIRT_R[0], SKIRT_R[1], SKIRT_TOP - SKIRT_BOTTOM)
    m.objects["patch_a"].location = Vector((0.110, 0.060, 0.470)) + up       # on the front of the coat
    m.objects["patch_b"].location = Vector((-0.020, -0.150, 0.700)) + up     # on the right side
    head = HEAD + up
    m.objects["head"].location = head
    m.objects["hair"].location = head + Vector((-0.050, 0, 0.040))
    for s, k in ((1, "l"), (-1, "r")):
        m.objects[f"eye_{k}"].location = head + Vector((0.128, 0.046 * s, 0.080))
    # floppy hat: soft brim tipped back, crown low; the brim is squashed into a gentle droop by the scale
    hat_base = head + Vector((-0.060, 0, 0.125))
    for name in ("brim", "crown"):
        o = m.objects[name]
        o.rotation_mode = "XYZ"
        o.rotation_euler = Euler((0.05, -0.55, 0.0))
    m.objects["brim"].location = hat_base
    m.objects["crown"].location = hat_base + Vector((-0.020, 0, 0.050))
    for s, k, phase in ((1, "l", 0.0), (-1, "r", 0.5)):
        hip = Vector((0.0, HIP_Y * s, HIP_Z)) + up
        fx, fz = _foot(t, phase)
        ankle = Vector((fx, HIP_Y * s * 1.1, 0.055 + fz))
        knee, ankle = _two_bone(hip, ankle, KNEE_LEN, SHIN_LEN, Vector((1, 0, 0)))
        m.put_segment(f"thigh_{k}", hip, knee, LEG_R)
        m.put_segment(f"shin_{k}", knee, ankle, LEG_R * 0.9)
        m.put_segment(f"bootleg_{k}", ankle, ankle + Vector((0, 0, 0.11)), LEG_R * 1.12)
        m.objects[f"boot_{k}"].location = ankle + Vector((0.030, 0, -0.012))
    # left arm swings; right hand holds the rod at chest height, the rod resting back over the right shoulder
    for s, k in ((1, "l"), (-1, "r")):
        sh = Vector((SHOULDER.x, SHOULDER.y * s, SHOULDER.z)) + up
        if k == "l":
            swing = 0.11 * math.sin(a) if walking else 0.0
            hand = sh + Vector((swing, 0.030, -0.34 + 0.02 * abs(swing) / 0.11))
        else:
            hand = Vector((0.120, -0.120, 0.700)) + up
        elbow, hand = _two_bone(sh, hand, UPPER_ARM, FOREARM, Vector((-1, -0.3 * s, 0)))
        m.put_segment(f"upper_{k}", sh, elbow, ARM_R)
        m.put_segment(f"fore_{k}", elbow, hand, ARM_R * 0.92)
        d = (hand - elbow).normalized()
        m.objects[f"hand_{k}"].location = hand + d * 0.018
        if k == "r":
            butt = hand + Vector((0.050, 0.010, -0.050))
            tip = hand + Vector((-0.400, -0.170, 0.600 + 0.012 * math.sin(2 * a)))
            m.put_segment("rod", butt, tip, 0.012)
            sway = 0.02 * math.sin(a) if walking else 0.0
            pts = [tuple(tip + Vector((-0.012 * i + sway * i / 5, -0.004 * i, -0.060 * i))) for i in range(6)]
            m.set_tube("line", pts, [0.004] * 6)


def assign_depth_parts(m, depth_of):
    return None
