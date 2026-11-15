"""Ruin archer (Floor 1, the Old Watchtower ruins): model + walk cycle, built on Brannoch's body.

ART_REQUESTS.md: "a skeletal archer in rotted leather with a bow". Original design: bone-white skull with dark
eye sockets, thin bony arms and legs, a torn dark leather jerkin and belt, the bow slung across the back,
a jerky walk. Faces +X; sizes in tiles.
"""
from __future__ import annotations

import math

from mathutils import Euler, Vector

NAME = "archer"
WALK_FRAMES = 8
PALETTE = "archer"
REFERENCE = "look_33.png"   # Tibia's Skeleton, the closest look-alike (comparison only, never shipped)
PROJECTION = "oblique"
CANVAS_OFFSET = (8, 8)
PIXEL_RULES = {
    "weight": {"eye": 9.0, "rib": 2.0, "scar": 6.0, "hand": 2.4, "bow": 2.6, "string": 2.0, "belt": 2.0, "pelt": 1.4,
               "boot": 1.4, "beard": 1.6},
    "thin": {"eye": 3, "scar": 2, "hand": 3, "bow": 2, "string": 2, "belt": 3},
    "soft": [["tunic", "belt"], ["skin", "hair", "beard", "eye", "scar"], ["hand", "skin"], ["pants", "boot"],
             ["bow", "string"]],
    "no_outline": ["string"],
    "fur": ["tunic"],
    "selout": ["tunic", "pelt", "hair"],
    "texture": {"tunic": [0.9, 0.3], "skin": [0.4, 0.0], "pants": [0.4, 0.0]},
    "bands": [0.30, 0.42, 0.53, 0.63, 0.72, 0.81, 0.89],
}

PARTS = ["none", "skin", "eye", "scar", "hair", "beard", "pelt", "tunic", "belt", "pants", "boot", "hand",
         "bow", "string"]

HIP_Z, KNEE_LEN, SHIN_LEN = 0.50, 0.25, 0.25
HIP_Y = 0.074
LEG_R = 0.021
TORSO = Vector((0.0, 0.0, 0.70)); TORSO_R = (0.072, 0.118, 0.165)
SKIRT_TOP, SKIRT_BOTTOM = 0.58, 0.40                      # short tunic: legs show
SKIRT_R = (0.110, 0.150)
HEAD = Vector((0.010, 0.0, 0.965)); HEAD_R = (0.128, 0.120, 0.138)
SHOULDER = Vector((0.0, 0.172, 0.825))
UPPER_ARM, FOREARM = 0.19, 0.18
ARM_R = 0.020
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
        m.capsule(f"bootleg_{k}", "pants")
        m.ellipsoid(f"boot_{k}", "pants", radii=(0.060, 0.032, 0.026), segments=12, rings=8)   # bony feet
        m.capsule(f"upper_{k}", "hand")
        m.capsule(f"fore_{k}", "hand")
        m.ellipsoid(f"hand_{k}", "hand", radii=(0.038, 0.032, 0.040), segments=10, rings=8)
    m.ellipsoid("torso", "tunic", radii=TORSO_R)
    m.frustum("skirt", "tunic", top_ratio=0.80)
    m.frustum("belt", "belt", top_ratio=1.0)
    m.ellipsoid("pelt", "tunic", radii=(0.085, 0.140, 0.045), segments=18, rings=10)
    m.ellipsoid("pelt_back", "tunic", radii=(0.050, 0.120, 0.120), segments=14, rings=8)
    m.ellipsoid("head", "skin", radii=HEAD_R)
    m.ellipsoid("hair", "skin", radii=(0.140, 0.132, 0.140))   # skull cap
    m.ellipsoid("beard", "beard", radii=(0.070, 0.090, 0.050), segments=14, rings=8)   # jaw
    for k in ("l", "r"):
        m.ellipsoid(f"eye_{k}", "eye", radii=(0.032, 0.030, 0.034), segments=8, rings=6)   # eye sockets
    for i in range(4):
        m.capsule(f"rib{i}", "skin")                    # ribs showing through the rotted jerkin
    m.tube("bow", "bow", points=9)
    m.capsule("string", "string")
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
    _frustum(m.objects["belt"], Vector((0, 0, 0.555)) + up, (TORSO_R[0] * 1.02, TORSO_R[1] * 0.97), 0.030)
    m.objects["pelt"].location = Vector((-0.010, 0, 0.835)) + up
    m.objects["pelt_back"].location = Vector((-0.085, 0, 0.740)) + up
    head = HEAD + up
    m.objects["head"].location = head
    m.objects["hair"].location = head + Vector((-0.020, 0, 0.030))
    m.objects["beard"].location = head + Vector((0.070, 0, -0.105))
    for s, k in ((1, "l"), (-1, "r")):
        m.objects[f"eye_{k}"].location = head + Vector((0.104, 0.046 * s, 0.035))
    for i in range(4):
        z = 0.775 - 0.055 * i
        w = 0.105 - 0.010 * i
        m.put_segment(f"rib{i}", Vector((0.080, -w, z)) + up, Vector((0.080, w, z)) + up, 0.016)
    # bow across the back, from the right hip up over the left shoulder; the string runs straight between the tips
    lo = Vector((-0.120, -0.150, 0.420)) + up
    hi = Vector((-0.110, 0.170, 1.000)) + up
    pts, radii = [], []
    for i in range(9):
        u = i / 8
        p = lo.lerp(hi, u) + Vector((-0.070 * math.sin(math.pi * u), 0, 0))
        pts.append(tuple(p))
        radii.append(0.016 if 0.2 < u < 0.8 else 0.012)
    m.set_tube("bow", pts, radii)
    m.put_segment("string", lo + Vector((0.006, 0, 0)), hi + Vector((0.006, 0, 0)), 0.005)
    for s, k, phase in ((1, "l", 0.0), (-1, "r", 0.5)):
        hip = Vector((0.0, HIP_Y * s, HIP_Z)) + up
        fx, fz = _foot(t, phase)
        ankle = Vector((fx, HIP_Y * s * 1.1, 0.055 + fz))
        knee, ankle = _two_bone(hip, ankle, KNEE_LEN, SHIN_LEN, Vector((1, 0, 0)))
        m.put_segment(f"thigh_{k}", hip, knee, LEG_R)
        m.put_segment(f"shin_{k}", knee, ankle, LEG_R * 0.9)
        m.put_segment(f"bootleg_{k}", ankle, ankle + Vector((0, 0, 0.06)), LEG_R)
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


def assign_depth_parts(m, depth_of):
    return None
