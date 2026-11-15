"""Merchant (Hearthgate market, town NPC): model + walk cycle, a variant of Bess.

ART_REQUESTS.md: "a merchant with an apron". Original design: long brown tunic, a tan leather apron, rolled
sleeves, short dark hair and a short beard, a fat coin pouch held out in one hand. Faces +X; sizes in tiles.
"""
from __future__ import annotations

import math

from mathutils import Euler, Vector

NAME = "merchant"
WALK_FRAMES = 8
PALETTE = "merchant"
REFERENCE = "outfit_128.png"       # Tibia's female citizen, grey (comparison only, never shipped)
PROJECTION = "oblique"
CANVAS_OFFSET = (8, 8)
PIXEL_RULES = {
    "weight": {"eye": 9.0, "cheek": 3.0, "hand": 2.4, "ladle": 3.2, "sleeve": 2.2, "shoe": 1.6, "bun": 1.5,
               "apron": 1.3},
    "thin": {"eye": 3, "cheek": 3, "hand": 3, "ladle": 2, "sleeve": 3, "shoe": 3},
    "soft": [["dress", "apron", "sleeve"], ["skin", "cheek", "hair", "bun", "eye"], ["hand", "ladle"],
             ["shoe", "legs"]],
    "no_outline": [],
    "fur": [],
    "selout": ["dress", "apron", "skin", "hair"],
}

PARTS = ["none", "skin", "eye", "cheek", "hair", "bun", "dress", "apron", "sleeve", "legs", "shoe", "hand",
         "ladle"]

HIP_Z, KNEE_LEN, SHIN_LEN = 0.46, 0.23, 0.23
HIP_Y = 0.075
LEG_R = 0.050
TORSO = Vector((0.0, 0.0, 0.66)); TORSO_R = (0.125, 0.175, 0.185)     # round build
SKIRT_TOP, SKIRT_BOTTOM = 0.58, 0.26                                  # long skirt, shoes show below
SKIRT_R = (0.165, 0.200)
HEAD = Vector((0.010, 0.0, 0.945)); HEAD_R = (0.150, 0.142, 0.160)
SHOULDER = Vector((0.0, 0.170, 0.790))
UPPER_ARM, FOREARM = 0.17, 0.17
ARM_R = 0.054
STRIDE, LIFT, STANCE = 0.14, 0.060, 0.5
BODY_SCALE = (1.15, 1.22, 0.80)


def build(model_cls, facing):
    import bpy
    body = bpy.data.objects.new("BodyScale", None)
    body.parent = facing
    body.scale = BODY_SCALE
    bpy.context.scene.collection.objects.link(body)
    m = model_cls(body, PARTS)
    for k in ("l", "r"):
        m.capsule(f"shin_{k}", "legs")
        m.ellipsoid(f"shoe_{k}", "shoe", radii=(0.078, 0.050, 0.046), segments=12, rings=8)
        m.capsule(f"upper_{k}", "dress")
        m.capsule(f"fore_{k}", "skin")                     # sleeves rolled up: bare forearms
        m.frustum(f"roll_{k}", "sleeve", top_ratio=1.0, segments=10)
        m.ellipsoid(f"hand_{k}", "hand", radii=(0.038, 0.032, 0.040), segments=10, rings=8)
    m.ellipsoid("torso", "dress", radii=TORSO_R)
    m.frustum("skirt", "dress", top_ratio=0.74)
    m.ellipsoid("bib", "apron", radii=(0.040, 0.105, 0.110), segments=14, rings=8)
    m.frustum("apron", "apron", top_ratio=0.80, segments=16)
    m.ellipsoid("head", "skin", radii=HEAD_R)
    m.ellipsoid("hair", "hair", radii=(0.138, 0.154, 0.152))
    m.ellipsoid("bun", "bun", radii=(0.075, 0.115, 0.060), segments=14, rings=10)   # short beard
    for k in ("l", "r"):
        m.ellipsoid(f"eye_{k}", "eye", radii=(0.012, 0.012, 0.018), segments=8, rings=6)
        m.ellipsoid(f"cheek_{k}", "cheek", radii=(0.012, 0.030, 0.022), segments=8, rings=6)
    m.capsule("ladle_handle", "ladle")
    m.ellipsoid("ladle_bowl", "ladle", radii=(0.052, 0.050, 0.058), segments=12, rings=8)   # coin pouch
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


def _place_frustum(o, base, radii, height, rot=(0.0, 0.0, 0.0)):
    o.location = base
    o.rotation_mode = "XYZ"
    o.rotation_euler = Euler(rot)
    o.scale = (radii[0], radii[1], height)


def pose(m, t):
    a = 0.0 if t is None else 2 * math.pi * t
    walking = t is not None
    bob = 0.012 * (0.5 + 0.5 * math.cos(2 * a)) if walking else 0.0
    sway = 0.08 * math.sin(a) if walking else 0.0            # a rounder walk: the skirt swings side to side
    up = Vector((0, 0, bob))
    m.objects["torso"].location = TORSO + up
    _place_frustum(m.objects["skirt"], Vector((0, 0, SKIRT_BOTTOM)) + up, SKIRT_R, SKIRT_TOP - SKIRT_BOTTOM,
                   (sway, 0.0, 0.0))
    # apron: a slightly smaller cut cone pushed forward over the skirt, plus a bib on the chest
    _place_frustum(m.objects["apron"], Vector((0.030, 0, SKIRT_BOTTOM + 0.05)) + up,
                   (SKIRT_R[0] * 0.95, SKIRT_R[1] * 0.82), SKIRT_TOP - SKIRT_BOTTOM - 0.04, (sway, 0.0, 0.0))
    m.objects["bib"].location = Vector((0.098, 0, 0.640)) + up
    head = HEAD + up
    m.objects["head"].location = head
    m.objects["hair"].location = head + Vector((-0.050, 0, 0.058))
    m.objects["bun"].location = head + Vector((0.085, 0, -0.085))
    for s, k in ((1, "l"), (-1, "r")):
        m.objects[f"eye_{k}"].location = head + Vector((0.136, 0.046 * s, 0.055))
        m.objects[f"cheek_{k}"].location = head + Vector((0.128, 0.078 * s, 0.000))
    for s, k, phase in ((1, "l", 0.0), (-1, "r", 0.5)):
        hip = Vector((0.0, HIP_Y * s, HIP_Z)) + up
        fx, fz = _foot(t, phase)
        ankle = Vector((fx, HIP_Y * s * 1.1, 0.050 + fz))
        knee, ankle = _two_bone(hip, ankle, KNEE_LEN, SHIN_LEN, Vector((1, 0, 0)))
        m.put_segment(f"shin_{k}", knee, ankle, LEG_R * 0.9)
        m.objects[f"shoe_{k}"].location = ankle + Vector((0.032, 0, -0.010))
    # arms: the left swings with the step; the right holds the ladle out to the side so it shows from every view
    for s, k in ((1, "l"), (-1, "r")):
        sh = Vector((SHOULDER.x, SHOULDER.y * s, SHOULDER.z)) + up
        if k == "l":
            swing = 0.10 * math.sin(a) if walking else 0.0
            hand = sh + Vector((swing, 0.040, -0.31))
        else:
            hand = sh + Vector((0.080, -0.110, -0.23 + 0.008 * math.sin(2 * a)))
        elbow, hand = _two_bone(sh, hand, UPPER_ARM, FOREARM, Vector((-1, 0.3 * s, 0)))
        m.put_segment(f"upper_{k}", sh, elbow, ARM_R)
        m.put_segment(f"fore_{k}", elbow, hand, ARM_R * 0.82)
        d = (hand - elbow).normalized()
        m.put_segment(f"roll_{k}", elbow - d * 0.010, elbow + d * 0.040, ARM_R * 1.18)
        m.objects[f"hand_{k}"].location = hand + d * 0.018
        if k == "r":
            grip = hand + d * 0.020
            m.put_segment("ladle_handle", grip + Vector((0, 0, 0.010)), grip + Vector((0, 0, 0.050)), 0.014)   # pouch neck
            m.objects["ladle_bowl"].location = grip + Vector((0.010, 0, -0.040))


def assign_depth_parts(m, depth_of):
    return None
