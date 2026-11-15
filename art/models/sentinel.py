"""Ruin sentinel (Floor 1, the Old Watchtower ruins): model + walk cycle, built on the road bandit's body.

ART_REQUESTS.md: "an old animated stone guard statue, cracked and mossy, holding a stone spear". Original
design: grey stone body with a rounded helmet and shoulder plates, moss growing on the helmet and shoulders,
faint pale-blue glowing eyes, a tall stone spear held upright in the right hand, a stiff heavy walk.
"""
from __future__ import annotations

import math

from mathutils import Euler, Vector

NAME = "sentinel"
WALK_FRAMES = 8
PALETTE = "sentinel"
REFERENCE = "look_67.png"   # Tibia's Stone Golem, the closest look-alike (comparison only, never shipped)
PROJECTION = "oblique"
SIZE = 1.35                 # a statue a head taller than a person, like Tibia's stone golem towers
CANVAS_OFFSET = (4, 5)
PIXEL_RULES = {
    "weight": {"moss": 2.0, "eye": 2.5, "hand": 2.4, "blade": 3.0, "hilt": 2.6, "belt": 2.0, "pelt": 1.4, "boot": 1.4,
               "beard": 1.8},
    "thin": {"moss": 3, "eye": 4, "hand": 3, "blade": 2, "hilt": 2, "belt": 3},
    "soft": [["tunic", "belt", "moss", "pelt", "pants", "boot", "hand"], ["skin", "hair", "beard", "eye", "moss"], ["hand", "skin"], ["pants", "boot"],
             ["blade", "hilt"]],
    "no_outline": [],
    "fur": ["tunic", "hair"],
    "selout": ["tunic", "pelt", "skin", "hair"],
    "texture": {"tunic": [2.16, 0.90], "pelt": [1.80, 0.72], "skin": [1.80, 0.72], "pants": [1.98, 0.90], "boot": [1.62, 0.54],
                "hand": [1.44, 0.36], "hair": [1.62, 0.54]},
    "bands": [0.30, 0.42, 0.53, 0.63, 0.72, 0.81, 0.89],
}

PARTS = ["none", "skin", "eye", "hair", "beard", "pelt", "tunic", "belt", "pants", "boot", "hand", "blade", "hilt",
         "moss"]

HIP_Z, KNEE_LEN, SHIN_LEN = 0.50, 0.25, 0.25
HIP_Y = 0.074
LEG_R = 0.056
TORSO = Vector((0.0, 0.0, 0.70)); TORSO_R = (0.110, 0.170, 0.190)
SKIRT_TOP, SKIRT_BOTTOM = 0.58, 0.40                      # short tunic: legs show
SKIRT_R = (0.130, 0.175)
HEAD = Vector((0.010, 0.0, 0.950)); HEAD_R = (0.122, 0.116, 0.130)
SHOULDER = Vector((0.0, 0.205, 0.825))
UPPER_ARM, FOREARM = 0.19, 0.18
ARM_R = 0.054
STRIDE, LIFT, STANCE = 0.10, 0.040, 0.5            # stiff, heavy steps
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
    m.frustum("belt", "belt", top_ratio=1.0)
    m.ellipsoid("pelt", "pelt", radii=(0.150, 0.250, 0.090), segments=18, rings=10)   # short hooded cape
    m.ellipsoid("pelt_back", "pelt", radii=(0.060, 0.150, 0.150), segments=14, rings=8)
    m.ellipsoid("head", "skin", radii=HEAD_R)
    m.ellipsoid("hair", "hair", radii=(0.162, 0.160, 0.150))   # stone helmet
    m.ellipsoid("beard", "beard", radii=(0.070, 0.120, 0.050), segments=14, rings=8)   # chin guard
    for i in range(4):
        m.ellipsoid(f"moss{i}", "moss", radii=(0.050, 0.045, 0.020), segments=10, rings=6)
    for k in ("l", "r"):
        m.ellipsoid(f"eye_{k}", "eye", radii=(0.012, 0.012, 0.018), segments=8, rings=6)
    m.capsule("blade", "blade")
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
    _frustum(m.objects["belt"], Vector((0, 0, 0.555)) + up, (TORSO_R[0] * 1.02, TORSO_R[1] * 0.97), 0.030)
    m.objects["pelt"].location = Vector((-0.010, 0, 0.835)) + up
    m.objects["pelt_back"].location = Vector((-0.085, 0, 0.740)) + up
    head = HEAD + up
    m.objects["head"].location = head
    m.objects["hair"].location = head + Vector((-0.050, 0, 0.065))
    m.objects["beard"].location = head + Vector((0.085, 0, -0.075))
    for i, off in enumerate(((-0.040, 0.050, 0.200), (-0.020, -0.060, 0.170), (0.0, 0.175, -0.150),
                             (-0.010, -0.170, -0.160))):
        m.objects[f"moss{i}"].location = head + Vector(off)
    for s, k in ((1, "l"), (-1, "r")):
        m.objects[f"eye_{k}"].location = head + Vector((0.120, 0.046 * s, 0.070))
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
            ax = Vector((0.30, -0.12, 1.0)).normalized()          # tilted forward and out from the body
            base = grip + Vector((0.020, -0.050, 0.0)) - ax * 0.280
            top = grip + Vector((0.020, -0.050, 0.0)) + ax * 0.400
            m.put_segment("grip", base, top, 0.016)
            m.put_segment("guard", top - ax * 0.010, top + ax * 0.020, 0.028)
            m.put_segment("blade", top + ax * 0.010, top + ax * 0.150, 0.024)


def assign_depth_parts(m, depth_of):
    return None
