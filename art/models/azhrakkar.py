"""Azhrakkar, the Cerulean Ruin's boss (phase 5): model + walk cycle, built on Brannoch's body, scaled up.

ART_REQUESTS.md: "a giant muscular blue-skinned horned fiend with glowing pale-cyan eyes, dark ridged armor
plates on the shoulders, wielding an enormous jagged greatsword taller than itself". Original design: deep
blue skin, two thick horns curving back from the brow, glowing pale-cyan eyes, heavy dark slate shoulder
plates, a dark armoured kilt and belt, bare muscular blue arms and legs, dark iron boots, and a huge jagged
greatsword held point-up beside it. It fills the whole 2x2-tile canvas. Faces +X; sizes in tiles.
"""
from __future__ import annotations

import math

from mathutils import Euler, Vector

NAME = "azhrakkar"
WALK_FRAMES = 8
PALETTE = "azhrakkar"
REFERENCE = "outfit_128.png"       # Tibia's male citizen, grey (comparison only, never shipped)
PROJECTION = "oblique"
CANVAS_OFFSET = (2, 2)             # a big boss uses almost the whole canvas
PIXEL_RULES = {
    "weight": {"eye": 2.5, "scar": 3.0, "hand": 2.0, "bow": 2.0, "string": 2.0, "belt": 2.0, "pelt": 1.4,
               "boot": 1.4, "beard": 1.6},
    "thin": {"eye": 4, "scar": 2, "hand": 3, "bow": 2, "string": 2, "belt": 3},
    "soft": [["tunic", "belt"], ["skin", "hair", "beard", "eye"], ["hand", "skin", "pants"], ["bow", "string"]],
    "no_outline": [],
    "fur": [],
    "selout": ["tunic", "pelt", "skin", "hair"],
}

PARTS = ["none", "skin", "eye", "scar", "hair", "beard", "pelt", "tunic", "belt", "pants", "boot", "hand",
         "bow", "string"]

HIP_Z, KNEE_LEN, SHIN_LEN = 0.50, 0.25, 0.25
HIP_Y = 0.074
LEG_R = 0.066
TORSO = Vector((0.0, 0.0, 0.70)); TORSO_R = (0.125, 0.190, 0.200)   # broad chest
SKIRT_TOP, SKIRT_BOTTOM = 0.58, 0.40                      # short tunic: legs show
SKIRT_R = (0.130, 0.175)
HEAD = Vector((0.020, 0.0, 0.960)); HEAD_R = (0.120, 0.112, 0.128)   # small head on a big body
SHOULDER = Vector((0.0, 0.172, 0.825))
UPPER_ARM, FOREARM = 0.19, 0.18
ARM_R = 0.068
STRIDE, LIFT, STANCE = 0.11, 0.045, 0.5             # heavy, stomping steps
BODY_SCALE = (1.15 * 1.55, 1.22 * 1.60, 0.80 * 1.55)   # giant


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
        m.capsule(f"upper_{k}", "pants")      # bare blue arms
        m.capsule(f"fore_{k}", "pants")
        m.ellipsoid(f"hand_{k}", "hand", radii=(0.038, 0.032, 0.040), segments=10, rings=8)
    m.ellipsoid("torso", "skin", radii=TORSO_R)     # bare blue chest
    m.frustum("skirt", "tunic", top_ratio=0.80)
    m.frustum("belt", "belt", top_ratio=1.0)
    m.ellipsoid("pelt", "pelt", radii=(0.120, 0.250, 0.085), segments=18, rings=10)   # shoulder plates
    m.ellipsoid("pelt_back", "pelt", radii=(0.050, 0.130, 0.110), segments=14, rings=8)
    m.ellipsoid("head", "skin", radii=HEAD_R)
    m.ellipsoid("hair", "skin", radii=(0.095, 0.100, 0.060))   # brow ridge
    m.ellipsoid("beard", "skin", radii=(0.070, 0.095, 0.050), segments=14, rings=8)   # heavy jaw
    for k in ("l", "r"):
        m.tube(f"horn_{k}", "scar", points=8)
    for k in ("l", "r"):
        m.ellipsoid(f"eye_{k}", "eye", radii=(0.018, 0.018, 0.020), segments=8, rings=6)
    m.tube("bow", "bow", points=9)        # the greatsword blade
    m.capsule("string", "string")        # its crossguard
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
    m.objects["hair"].location = head + Vector((-0.010, 0, 0.085))
    m.objects["beard"].location = head + Vector((0.050, 0, -0.080))
    for s, k in ((1, "l"), (-1, "r")):
        m.objects[f"eye_{k}"].location = head + Vector((0.108, 0.040 * s, 0.040))
    for s_, k in ((1, "l"), (-1, "r")):                # thick horns curving back and up from the brow
        root = head + Vector((0.040, 0.075 * s_, 0.080))
        pts, radii = [], []
        for i in range(8):
            u = i / 7
            pts.append(tuple(root + Vector((-0.130 * u, 0.050 * s_ * u, 0.150 * math.sin(math.pi * u * 0.6)))))
            radii.append(0.034 * (1 - 0.75 * u) + 0.006)
        m.set_tube(f"horn_{k}", pts, radii)
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
        if k == "r":                                       # the jagged greatsword, point up beside it
            grip = hand + d * 0.020
            ax = Vector((0.20, -0.30, 1.0)).normalized()
            pts, radii = [], []
            for i in range(9):
                u = i / 8
                pts.append(tuple(grip + ax * (0.050 + 0.850 * u)))
                radii.append((0.050 if i % 2 == 0 else 0.036) * (1 - 0.55 * u) + 0.010)
            m.set_tube("bow", pts, radii)
            side = Vector((0.6, 0.8, 0)).normalized()
            m.put_segment("string", grip + ax * 0.040 - side * 0.090, grip + ax * 0.040 + side * 0.090, 0.022)


def assign_depth_parts(m, depth_of):
    return None
