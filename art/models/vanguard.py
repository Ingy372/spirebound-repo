"""Vanguard (player class outfit): model + walk cycle, built on Pell's body.

ART_REQUESTS.md: "a sturdy armored sword knight in steel plate with a blue tabard and a kite shield, short
cape, helmetless with short hair". Original design: steel plate on arms, legs and shoulders (round pauldrons),
blue tabard with a gold border over the breastplate, a short blue cape behind, a blue kite shield with a
gold rim on the left arm, a sword held low in the right hand, short brown hair, steel boots.
"""
from __future__ import annotations

import math

from mathutils import Euler, Vector

NAME = "vanguard"
WALK_FRAMES = 8
PALETTE = "vanguard"
REFERENCE = "outfit_128.png"
PROJECTION = "oblique"
CANVAS_OFFSET = (8, 8)
PIXEL_RULES = {
    "weight": {"belt": 2.0, "buckle": 4.0, "crest": 3.0, "eye": 9.0, "mouth": 5.0, "hand": 2.4, "stick": 3.0, "pennant": 2.6, "strap": 2.2, "satchel": 1.6,
               "trim": 2.0, "boot": 1.4},
    "thin": {"belt": 3, "buckle": 2, "crest": 3, "eye": 3, "mouth": 2, "hand": 3, "stick": 2, "pennant": 3, "strap": 2, "trim": 3},
    "soft": [["shirt", "tabard", "trim", "strap", "satchel"], ["skin", "hair", "eye", "mouth"], ["hand", "skin"],
             ["pants", "boot"], ["stick", "pennant"]],
    "no_outline": [],
    "fur": [],
    "selout": ["tabard", "shirt", "skin", "hair"],
}

PARTS = ["none", "skin", "eye", "mouth", "hair", "shirt", "tabard", "trim", "strap", "satchel", "pants", "boot",
         "hand", "stick", "pennant", "belt", "buckle", "crest"]

HIP_Z, KNEE_LEN, SHIN_LEN = 0.50, 0.25, 0.25
HIP_Y = 0.068
LEG_R = 0.060
TORSO = Vector((0.0, 0.0, 0.70)); TORSO_R = (0.112, 0.172, 0.190)
HEAD = Vector((0.010, 0.0, 0.975)); HEAD_R = (0.146, 0.138, 0.156)
SHOULDER = Vector((0.0, 0.160, 0.825))
UPPER_ARM, FOREARM = 0.19, 0.18
ARM_R = 0.058
STRIDE, LIFT, STANCE = 0.12, 0.055, 0.5             # a steady, heavy march
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
        m.ellipsoid(f"boot_{k}", "boot", radii=(0.070, 0.045, 0.048), segments=12, rings=8)
        m.capsule(f"upper_{k}", "shirt")
        m.capsule(f"fore_{k}", "shirt")
        m.ellipsoid(f"hand_{k}", "hand", radii=(0.038, 0.032, 0.040), segments=10, rings=8)
    m.ellipsoid("torso", "shirt", radii=TORSO_R)
    m.box("tabard_f", "tabard", size=(0.030, 0.200, 0.420))
    m.box("tabard_b", "tabard", size=(0.030, 0.200, 0.420))
    m.box("trim_f", "trim", size=(0.026, 0.224, 0.040))
    m.box("trim_b", "trim", size=(0.026, 0.224, 0.040))
    m.box("strap", "strap", size=(0.030, 0.230, 0.300))          # short cape (behind)
    m.ellipsoid("satchel", "satchel", radii=(0.120, 0.022, 0.150), segments=16, rings=8)   # kite shield
    for k in ("l", "r"):
        m.ellipsoid(f"pauldron_{k}", "shirt", radii=(0.088, 0.085, 0.064), segments=12, rings=8)
    m.frustum("belt", "belt", top_ratio=1.0, segments=18)
    m.ellipsoid("buckle", "buckle", radii=(0.014, 0.026, 0.020), segments=8, rings=6)
    m.ellipsoid("gorget", "shirt", radii=(0.085, 0.120, 0.040), segments=14, rings=8)
    m.ellipsoid("crest", "crest", radii=(0.008, 0.050, 0.070), segments=10, rings=8)
    m.ellipsoid("head", "skin", radii=HEAD_R)
    m.ellipsoid("hair", "hair", radii=(0.152, 0.152, 0.142))
    m.ellipsoid("tuft", "hair", radii=(0.050, 0.060, 0.040), segments=10, rings=6)
    for k in ("l", "r"):
        m.ellipsoid(f"eye_{k}", "eye", radii=(0.012, 0.012, 0.018), segments=8, rings=6)
    m.capsule("mouth", "mouth")
    m.capsule("stick", "stick")          # sword blade
    m.capsule("pennant", "pennant")      # sword hilt
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
    bob = 0.018 * (0.5 + 0.5 * math.cos(2 * a)) if walking else 0.0
    flap = 0.08 * math.sin(a) if walking else 0.0
    up = Vector((0, 0, bob))
    m.objects["torso"].location = TORSO + up
    for side, x in (("f", 0.098), ("b", -0.098)):
        tab = m.objects[f"tabard_{side}"]
        tab.rotation_mode = "XYZ"
        tab.rotation_euler = Euler((0.0, flap if side == "f" else -flap, 0.0))
        tab.location = Vector((x, 0, 0.640)) + up
        trim = m.objects[f"trim_{side}"]
        trim.rotation_mode = "XYZ"
        trim.rotation_euler = tab.rotation_euler
        trim.location = Vector((x * 1.04, 0, 0.440)) + up
    cape = m.objects["strap"]
    cape.rotation_mode = "XYZ"
    cape.rotation_euler = Euler((0.0, 0.18 + (0.06 * abs(math.sin(a)) if walking else 0.0), 0.0))
    cape.location = Vector((-0.125, 0, 0.680)) + up
    for s_, k in ((1, "l"), (-1, "r")):
        m.objects[f"pauldron_{k}"].location = Vector((0.0, 0.180 * s_, 0.845)) + up
    bl = m.objects["belt"]
    bl.location = Vector((0, 0, 0.555)) + up
    bl.scale = (TORSO_R[0] * 1.10, TORSO_R[1] * 1.04, 0.040)
    m.objects["buckle"].location = Vector((0.130, 0, 0.575)) + up
    m.objects["gorget"].location = Vector((0.010, 0, 0.860)) + up
    head = HEAD + up
    m.objects["head"].location = head
    m.objects["hair"].location = head + Vector((-0.050, 0, 0.045))
    m.objects["tuft"].location = head + Vector((0.040, 0.030, 0.150))
    for s, k in ((1, "l"), (-1, "r")):
        m.objects[f"eye_{k}"].location = head + Vector((0.128, 0.046 * s, 0.085))
    m.put_segment("mouth", head + Vector((0.142, -0.030, 0.020)), head + Vector((0.142, 0.030, 0.020)), 0.010)
    for s, k, phase in ((1, "l", 0.0), (-1, "r", 0.5)):
        hip = Vector((0.0, HIP_Y * s, HIP_Z)) + up
        fx, fz = _foot(t, phase)
        ankle = Vector((fx, HIP_Y * s * 1.1, 0.055 + fz))
        knee, ankle = _two_bone(hip, ankle, KNEE_LEN, SHIN_LEN, Vector((1, 0, 0)))
        m.put_segment(f"thigh_{k}", hip, knee, LEG_R)
        m.put_segment(f"shin_{k}", knee, ankle, LEG_R * 0.9)
        m.put_segment(f"bootleg_{k}", ankle, ankle + Vector((0, 0, 0.10)), LEG_R * 1.12)
        m.objects[f"boot_{k}"].location = ankle + Vector((0.030, 0, -0.012))
    # left arm swings; right hand holds the pennant stick up and a little forward
    for s, k in ((1, "l"), (-1, "r")):
        sh = Vector((SHOULDER.x, SHOULDER.y * s, SHOULDER.z)) + up
        if k == "l":
            hand = sh + Vector((0.120, 0.030, -0.260))
        else:
            swing = 0.10 * math.sin(a) if walking else 0.0
            hand = sh + Vector((swing + 0.030, -0.030, -0.320))
        elbow, hand = _two_bone(sh, hand, UPPER_ARM, FOREARM, Vector((-1, -0.4 * s, 0)))
        m.put_segment(f"upper_{k}", sh, elbow, ARM_R)
        m.put_segment(f"fore_{k}", elbow, hand, ARM_R * 0.92)
        d = (hand - elbow).normalized()
        m.objects[f"hand_{k}"].location = hand + d * 0.018
        if k == "l":
            sh_ = m.objects["satchel"]
            sh_.rotation_mode = "XYZ"
            sh_.rotation_euler = Euler((0.0, 0.10, 0.25))
            sh_.location = hand + Vector((0.050, 0.050, -0.010))
            cr = m.objects["crest"]
            cr.rotation_mode = "XYZ"
            cr.rotation_euler = sh_.rotation_euler
            cr.location = sh_.location + Vector((0.004, 0.024, 0.0))
        if k == "r":
            fwd = Vector((0.60, -0.55, 0.60)).normalized()      # angled forward and out from the body
            m.put_segment("pennant", hand - fwd * 0.040, hand + fwd * 0.030, 0.016)
            m.put_segment("stick", hand + fwd * 0.030, hand + fwd * 0.300, 0.020)


def assign_depth_parts(m, depth_of):
    return None
