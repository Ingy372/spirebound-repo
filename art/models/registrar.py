"""Registrar (Hearthgate, town NPC): model + walk cycle, a variant of the banker.

ART_REQUESTS.md: "a clerk with a ledger". Original design: dusty grey-brown clerk's coat with dull brass trim,
a cream cravat, full brown hair, a big ledger held at the chest, dark trousers. Faces +X; sizes in tiles.
"""
from __future__ import annotations

import math

from mathutils import Euler, Vector

NAME = "registrar"
WALK_FRAMES = 8
PALETTE = "registrar"
REFERENCE = "outfit_128.png"   # Tibia outfit Vesper borrows today, tinted (comparison only, never shipped)
PROJECTION = "oblique"             # standing figure: Tibia's own drawing rule (see art/pipeline/rig.py)
CANVAS_OFFSET = (8, 8)             # px right/down: standing figures sit low-right on the canvas like Tibia's
PIXEL_RULES = {
    "weight": {"glass": 1.6, "eye": 9.0, "feather": 3.0, "hand": 2.4, "book": 3.0, "page": 3.0, "band": 2.0, "shirt": 2.2,
               "trim": 1.8, "boot": 1.4, "hair": 1.3},
    "thin": {"glass": 4, "eye": 3, "feather": 3, "hand": 3, "book": 3, "page": 2, "band": 3, "shirt": 3, "trim": 3},
    "soft": [["coat", "trim", "shirt"], ["skin", "hair", "eye"], ["hat", "band"], ["book", "page", "hand"],
             ["pants", "boot"]],
    "no_outline": [],
    "fur": [],
    "selout": ["coat", "hat", "skin", "feather"],
}

PARTS = ["none", "skin", "eye", "hair", "hat", "band", "feather", "coat", "trim", "shirt", "pants", "boot",
         "hand", "book", "page", "glass"]

# body ------------------------------------------------------------------
HIP_Z, KNEE_LEN, SHIN_LEN = 0.50, 0.25, 0.25
HIP_Y = 0.070
LEG_R = 0.054
TORSO = Vector((0.0, 0.0, 0.70)); TORSO_R = (0.105, 0.165, 0.185)
SKIRT_TOP, SKIRT_BOTTOM = 0.60, 0.36
SKIRT_R = (0.140, 0.180)            # x, y radius at the hem (it narrows to 70% at the waist)
HEAD = Vector((0.010, 0.0, 0.975)); HEAD_R = (0.150, 0.140, 0.160)
SHOULDER = Vector((0.0, 0.165, 0.825))
UPPER_ARM, FOREARM = 0.19, 0.18
ARM_R = 0.050
STRIDE, LIFT, STANCE = 0.11, 0.055, 0.5


BODY_SCALE = (1.15, 1.22, 0.80)   # Tibia proportions: chunkier and shorter than a real person


def build(model_cls, facing):
    import bpy
    body = bpy.data.objects.new("BodyScale", None)      # every part hangs under this to get the chunky build
    body.parent = facing
    body.scale = BODY_SCALE
    bpy.context.scene.collection.objects.link(body)
    m = model_cls(body, PARTS)
    for k in ("l", "r"):
        m.capsule(f"thigh_{k}", "pants")
        m.capsule(f"shin_{k}", "pants")
        m.ellipsoid(f"boot_{k}", "boot", radii=(0.070, 0.042, 0.050), segments=12, rings=8)
        m.capsule(f"bootleg_{k}", "boot")
        m.capsule(f"upper_{k}", "coat")
        m.capsule(f"fore_{k}", "coat")
        m.frustum(f"cuff_{k}", "trim", top_ratio=1.0, segments=10)
        m.ellipsoid(f"hand_{k}", "hand", radii=(0.036, 0.030, 0.038), segments=10, rings=8)
    m.ellipsoid("torso", "coat", radii=TORSO_R)
    m.frustum("skirt", "coat", top_ratio=0.70)
    m.frustum("hem", "trim", top_ratio=0.97)
    m.ellipsoid("cravat", "shirt", radii=(0.050, 0.060, 0.070), segments=10, rings=8)
    m.ellipsoid("collar", "trim", radii=(0.085, 0.140, 0.040), segments=14, rings=8)
    m.ellipsoid("head", "skin", radii=HEAD_R)
    m.ellipsoid("hair", "hair", radii=(0.150, 0.154, 0.150))
    for k in ("l", "r"):
        m.ellipsoid(f"eye_{k}", "eye", radii=(0.012, 0.012, 0.018), segments=8, rings=6)
    for k in ("l", "r"):
        m.capsule(f"glass_{k}", "glass", segments=8)
    m.box("book", "book", size=(0.075, 0.016, 0.095))
    m.box("page", "page", size=(0.068, 0.006, 0.086))
    return m


def _two_bone(a, target, l1, l2, bend_hint):
    """Joint position for a two-segment limb from a to target, bending toward bend_hint."""
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
    sk.rotation_euler = Euler((0.04 * math.sin(a) if walking else 0.0, 0.0, 0.0))
    sk.scale = (SKIRT_R[0], SKIRT_R[1], SKIRT_TOP - SKIRT_BOTTOM)
    hem = m.objects["hem"]
    hem.location = Vector((0, 0, SKIRT_BOTTOM - 0.004)) + up
    hem.rotation_mode = "XYZ"
    hem.rotation_euler = sk.rotation_euler
    hem.scale = (SKIRT_R[0] + 0.004, SKIRT_R[1] + 0.004, 0.032)
    m.objects["cravat"].location = Vector((0.085, 0, 0.810)) + up
    m.objects["collar"].location = Vector((-0.010, 0, 0.870)) + up
    head = HEAD + up
    m.objects["head"].location = head
    m.objects["hair"].location = head + Vector((-0.050, 0, 0.045))
    for s, k in ((1, "l"), (-1, "r")):
        m.objects[f"eye_{k}"].location = head + Vector((0.140, 0.050 * s, 0.040))
    for s_, k in ((1, "l"), (-1, "r")):                # round spectacles: a pale rim just round each eye
        e = head + Vector((0.146, 0.050 * s_, 0.040))
        m.put_segment(f"glass_{k}", e + Vector((0, -0.020, 0)), e + Vector((0, 0.020, 0)), 0.012)
    # legs
    for s, k, phase in ((1, "l", 0.0), (-1, "r", 0.5)):
        hip = Vector((0.0, HIP_Y * s, HIP_Z)) + up
        fx, fz = _foot(t, phase)
        ankle = Vector((fx, HIP_Y * s * 1.1, 0.055 + fz))
        knee, ankle = _two_bone(hip, ankle, KNEE_LEN, SHIN_LEN, Vector((1, 0, 0)))
        m.put_segment(f"thigh_{k}", hip, knee, LEG_R)
        m.put_segment(f"shin_{k}", knee, ankle, LEG_R * 0.9)
        m.put_segment(f"bootleg_{k}", ankle, ankle + Vector((0, 0, 0.09)), LEG_R * 1.12)
        m.objects[f"boot_{k}"].location = ankle + Vector((0.030, 0, -0.012))
    # arms: the right arm swings against the left leg; the left hand holds the notebook at the chest
    for s, k in ((1, "l"), (-1, "r")):
        sh = Vector((SHOULDER.x, SHOULDER.y * s, SHOULDER.z)) + up
        if k == "l":
            hand = Vector((0.150, 0.070, 0.650)) + up + Vector((0, 0, 0.006 * math.sin(2 * a)))
            hint = Vector((-1, 0.6, 0))
        else:
            swing = -0.11 * math.sin(a) if walking else 0.0
            hand = sh + Vector((swing, -0.030, -0.34 + 0.02 * abs(swing) / 0.11))
            hint = Vector((-1, 0, 0))
        elbow, hand = _two_bone(sh, hand, UPPER_ARM, FOREARM, hint)
        m.put_segment(f"upper_{k}", sh, elbow, ARM_R)
        m.put_segment(f"fore_{k}", elbow, hand, ARM_R * 0.92)
        cuff = m.objects[f"cuff_{k}"]
        d = (hand - elbow).normalized()
        m.put_segment(f"cuff_{k}", hand - d * 0.045, hand - d * 0.012, ARM_R * 1.12)
        m.objects[f"hand_{k}"].location = hand + d * 0.018
        if k == "l":
            book = m.objects["book"]
            book.rotation_mode = "XYZ"
            book.rotation_euler = Euler((0.0, -0.35, 0.25))
            book.location = hand + Vector((0.020, -0.034, 0.030))
            page = m.objects["page"]
            page.rotation_mode = "XYZ"
            page.rotation_euler = book.rotation_euler
            page.location = book.location + Vector((0.002, -0.011, 0.0))


def assign_depth_parts(m, depth_of):
    """Vesper uses depth lines (pixelize.py) to separate limbs; no near/far colour swap needed."""
    return None
