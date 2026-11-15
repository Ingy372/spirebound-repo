"""Bandit captain (Floor 1, the Bandit Road boss): model + walk cycle, built on the road bandit.

ART_REQUESTS.md: "a bandit leader with a red sash, a feathered hat and a curved sabre". Original design: wide
dark hat with a red feather, black beard, dark leather coat with a broad red sash at the waist and across the
chest, curved sabre held out in the right hand, boots. Faces +X; sizes in tiles.
"""
from __future__ import annotations

import math

from mathutils import Euler, Vector

NAME = "captain"
WALK_FRAMES = 8
PALETTE = "captain"
REFERENCE = "outfit_128.png"       # Tibia's male citizen, grey (comparison only, never shipped)
PROJECTION = "oblique"
CANVAS_OFFSET = (8, 8)
PIXEL_RULES = {
    "weight": {"hat": 1.2, "feather": 3.0, "sash": 2.0, "eye": 9.0, "hand": 2.4, "blade": 3.0, "hilt": 2.6, "belt": 2.0, "pelt": 1.4, "boot": 1.4,
               "beard": 1.8},
    "thin": {"feather": 3, "sash": 3, "eye": 3, "hand": 3, "blade": 2, "hilt": 2, "belt": 3},
    "soft": [["tunic", "belt", "sash"], ["skin", "hair", "beard", "eye"], ["hat", "feather"], ["hand", "skin"], ["pants", "boot"],
             ["blade", "hilt"]],
    "no_outline": [],
    "fur": [],
    "selout": ["tunic", "pelt", "skin", "hair"],
}

PARTS = ["none", "skin", "eye", "hair", "beard", "pelt", "tunic", "belt", "pants", "boot", "hand", "blade", "hilt",
         "hat", "feather", "sash"]

HIP_Z, KNEE_LEN, SHIN_LEN = 0.50, 0.25, 0.25
HIP_Y = 0.074
LEG_R = 0.056
TORSO = Vector((0.0, 0.0, 0.70)); TORSO_R = (0.110, 0.170, 0.190)
SKIRT_TOP, SKIRT_BOTTOM = 0.58, 0.40                      # short tunic: legs show
SKIRT_R = (0.130, 0.175)
HEAD = Vector((0.010, 0.0, 0.975)); HEAD_R = (0.148, 0.140, 0.158)
SHOULDER = Vector((0.0, 0.172, 0.825))
UPPER_ARM, FOREARM = 0.19, 0.18
ARM_R = 0.054
STRIDE, LIFT, STANCE = 0.13, 0.060, 0.5
BODY_SCALE = (1.15, 1.22, 0.80)


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
        m.capsule(f"upper_{k}", "tunic")
        m.capsule(f"fore_{k}", "tunic")
        m.ellipsoid(f"hand_{k}", "hand", radii=(0.038, 0.032, 0.040), segments=10, rings=8)
    m.ellipsoid("torso", "tunic", radii=TORSO_R)
    m.frustum("skirt", "tunic", top_ratio=0.80)
    m.frustum("belt", "sash", top_ratio=1.0)
    m.capsule("sash_x", "sash")
    m.ellipsoid("brim", "hat", radii=(0.195, 0.185, 0.022), segments=24, rings=8)
    m.frustum("crown", "hat", top_ratio=0.80)
    m.tube("feather", "feather", points=9)
    m.ellipsoid("pelt", "tunic", radii=(0.130, 0.195, 0.070), segments=18, rings=10)   # coat shoulders
    m.ellipsoid("pelt_back", "pelt", radii=(0.060, 0.150, 0.150), segments=14, rings=8)
    m.ellipsoid("head", "skin", radii=HEAD_R)
    m.ellipsoid("hair", "hair", radii=(0.150, 0.152, 0.140))
    m.ellipsoid("beard", "beard", radii=(0.075, 0.115, 0.075), segments=14, rings=8)
    for k in ("l", "r"):
        m.ellipsoid(f"eye_{k}", "eye", radii=(0.012, 0.012, 0.018), segments=8, rings=6)
    m.capsule("blade", "blade")
    m.capsule("blade_tip", "blade")
    m.capsule("guard", "hilt")
    m.capsule("grip", "hilt")
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


def _frustum(o, base, radii, height, rot=(0.0, 0.0, 0.0)):
    o.location = base
    o.rotation_mode = "XYZ"
    o.rotation_euler = Euler(rot)
    o.scale = (radii[0], radii[1], height)


def pose(m, t):
    a = 0.0 if t is None else 2 * math.pi * t
    walking = t is not None
    bob = 0.014 * (0.5 + 0.5 * math.cos(2 * a)) if walking else 0.0
    up = Vector((0, 0, bob))
    m.objects["torso"].location = TORSO + up
    _frustum(m.objects["skirt"], Vector((0, 0, SKIRT_BOTTOM)) + up, SKIRT_R, SKIRT_TOP - SKIRT_BOTTOM,
             (0.04 * math.sin(a) if walking else 0.0, 0, 0))
    _frustum(m.objects["belt"], Vector((0, 0, 0.540)) + up, (TORSO_R[0] * 1.04, TORSO_R[1] * 0.99), 0.060)
    m.put_segment("sash_x", Vector((0.100, -0.140, 0.830)) + up, Vector((0.095, 0.150, 0.560)) + up, 0.026)
    m.objects["pelt"].location = Vector((-0.010, 0, 0.835)) + up
    m.objects["pelt_back"].location = Vector((-0.085, 0, 0.740)) + up
    head = HEAD + up
    m.objects["head"].location = head
    m.objects["hair"].location = head + Vector((-0.055, 0, 0.040))
    m.objects["beard"].location = head + Vector((0.085, 0, -0.090))
    for s, k in ((1, "l"), (-1, "r")):
        m.objects[f"eye_{k}"].location = head + Vector((0.128, 0.046 * s, 0.092))
    tilt = Euler((0.10, -0.42, 0.0))
    hat_base = head + Vector((-0.045, 0.0, 0.118))
    for name in ("brim", "crown"):
        o = m.objects[name]
        o.rotation_mode = "XYZ"
        o.rotation_euler = tilt
    m.objects["brim"].location = hat_base
    crown = m.objects["crown"]
    crown.location = hat_base
    crown.scale = (0.115, 0.108, 0.120)
    sway = 0.012 * math.sin(a) if walking else 0.0
    root = hat_base + Vector((-0.030, 0.105, 0.040))
    pts, radii = [], []
    for i in range(9):
        u = i / 8
        pts.append(root + Vector((-0.17 * u, 0.09 * u * u, 0.07 * math.sin(math.pi * u * 0.8) + sway * u)))
        radii.append(0.022 * (1 - u) ** 0.6 + 0.004)
    m.set_tube("feather", [tuple(p) for p in pts], radii)
    for s, k, phase in ((1, "l", 0.0), (-1, "r", 0.5)):
        hip = Vector((0.0, HIP_Y * s, HIP_Z)) + up
        fx, fz = _foot(t, phase)
        ankle = Vector((fx, HIP_Y * s * 1.1, 0.055 + fz))
        knee, ankle = _two_bone(hip, ankle, KNEE_LEN, SHIN_LEN, Vector((1, 0, 0)))
        m.put_segment(f"thigh_{k}", hip, knee, LEG_R)
        m.put_segment(f"shin_{k}", knee, ankle, LEG_R * 0.9)
        m.put_segment(f"bootleg_{k}", ankle, ankle + Vector((0, 0, 0.11)), LEG_R * 1.12)
        m.objects[f"boot_{k}"].location = ankle + Vector((0.030, 0, -0.012))
    for s, k, phase in ((1, "l", 0.5), (-1, "r", 0.0)):       # arms swing against the legs
        sh = Vector((SHOULDER.x, SHOULDER.y * s, SHOULDER.z)) + up
        swing = 0.12 * math.sin(a + math.pi * 2 * phase) if walking else 0.0
        hand = sh + Vector((swing, 0.030 * s, -0.34 + 0.02 * abs(swing) / 0.12))
        elbow, hand = _two_bone(sh, hand, UPPER_ARM, FOREARM, Vector((-1, 0, 0)))
        m.put_segment(f"upper_{k}", sh, elbow, ARM_R)
        m.put_segment(f"fore_{k}", elbow, hand, ARM_R * 0.92)
        d = (hand - elbow).normalized()
        m.objects[f"hand_{k}"].location = hand + d * 0.018
        if k == "r":
            grip = hand + d * 0.020
            fwd = Vector((0.75, -0.15, 0.65)).normalized()       # blade angled forward and up
            m.put_segment("grip", grip - fwd * 0.040, grip + fwd * 0.020, 0.014)
            side = Vector((0, 1, 0))
            m.put_segment("guard", grip + fwd * 0.025 - side * 0.040, grip + fwd * 0.025 + side * 0.040, 0.012)
            m.put_segment("blade", grip + fwd * 0.030, grip + fwd * 0.180, 0.018)
            tip = grip + fwd * 0.180 + (fwd * 0.120 + Vector((-0.060, 0, -0.030)))   # the blade curves back
            m.put_segment("blade_tip", grip + fwd * 0.175, tip, 0.015)


def assign_depth_parts(m, depth_of):
    return None
