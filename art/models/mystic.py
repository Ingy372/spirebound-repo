"""Mystic (player class outfit): model + walk cycle, built on Veyra's robe.

ART_REQUESTS.md: "a nature mystic in pale green and white robes, leaf-shaped shoulder pieces, wooden beads".
Original design: white robe with a pale green overrobe down the front and back, big green leaf shapes on
both shoulders, a string of wooden beads across the chest, a soft green glow in the raised hand, long brown
hair, simple sandals. Faces +X; sizes in tiles.
"""
from __future__ import annotations

import math

from mathutils import Euler, Vector

NAME = "mystic"
WALK_FRAMES = 8
PALETTE = "mystic"
REFERENCE = "outfit_136.png"
PROJECTION = "oblique"
CANVAS_OFFSET = (8, 8)
PIXEL_RULES = {
    "weight": {"staff": 3.0, "leaf": 2.2, "bead": 3.0, "eye": 9.0, "glow": 3.5, "hand": 2.4, "stole": 1.8, "collar": 1.6, "shoe": 1.6, "hair": 1.2},
    "thin": {"staff": 2, "leaf": 3, "bead": 2, "eye": 3, "glow": 3, "hand": 3, "stole": 3, "shoe": 3},
    "soft": [["robe", "stole"], ["skin", "hair", "eye"], ["hand", "glow"], ["collar", "stole"]],
    "no_outline": [],
    "fur": [],
    "selout": ["robe", "collar", "skin", "hair"],
}

PARTS = ["none", "skin", "eye", "hair", "robe", "stole", "collar", "shoe", "hand", "glow", "leaf", "bead", "staff"]

HIP_Z, KNEE_LEN, SHIN_LEN = 0.48, 0.24, 0.24
HIP_Y = 0.066
LEG_R = 0.048
TORSO = Vector((0.0, 0.0, 0.69)); TORSO_R = (0.100, 0.150, 0.190)
SKIRT_TOP, SKIRT_BOTTOM = 0.62, 0.16
SKIRT_R = (0.150, 0.180)
HEAD = Vector((0.010, 0.0, 0.965)); HEAD_R = (0.142, 0.134, 0.156)
SHOULDER = Vector((0.0, 0.158, 0.815))
UPPER_ARM, FOREARM = 0.18, 0.17
ARM_R = 0.052
STRIDE, LIFT, STANCE = 0.13, 0.050, 0.5             # calm, gliding steps
BODY_SCALE = (1.15, 1.18, 0.80)


def build(model_cls, facing):
    import bpy
    body = bpy.data.objects.new("BodyScale", None)
    body.parent = facing
    body.scale = BODY_SCALE
    bpy.context.scene.collection.objects.link(body)
    m = model_cls(body, PARTS)
    for k in ("l", "r"):
        m.capsule(f"shin_{k}", "robe")
        m.ellipsoid(f"shoe_{k}", "shoe", radii=(0.066, 0.042, 0.040), segments=12, rings=8)
        m.capsule(f"upper_{k}", "robe")
        m.frustum(f"sleeve_{k}", "robe", top_ratio=0.55, segments=12)   # wide bell sleeves
        m.ellipsoid(f"hand_{k}", "hand", radii=(0.036, 0.030, 0.038), segments=10, rings=8)
    m.ellipsoid("glow", "glow", radii=(0.078, 0.078, 0.078), segments=12, rings=8)
    m.ellipsoid("torso", "robe", radii=TORSO_R)
    m.frustum("skirt", "robe", top_ratio=0.70)
    m.box("stole_f", "stole", size=(0.024, 0.070, 0.560))
    m.box("stole_b", "stole", size=(0.024, 0.090, 0.420))
    m.frustum("collar", "collar", top_ratio=1.25, segments=18)
    for k in ("l", "r"):
        m.ellipsoid(f"leaf_{k}", "leaf", radii=(0.090, 0.060, 0.018), segments=12, rings=6)
    for i in range(6):
        m.ellipsoid(f"bead{i}", "bead", radii=(0.022, 0.022, 0.022), segments=8, rings=6)
    m.tube("staff", "staff", points=7)
    m.ellipsoid("staff_leaves", "leaf", radii=(0.060, 0.060, 0.045), segments=12, rings=8)
    m.ellipsoid("head", "skin", radii=HEAD_R)
    m.ellipsoid("hair", "hair", radii=(0.150, 0.150, 0.150))
    m.ellipsoid("hair_long", "hair", radii=(0.070, 0.120, 0.170), segments=12, rings=8)
    for k in ("l", "r"):
        m.ellipsoid(f"eye_{k}", "eye", radii=(0.012, 0.012, 0.016), segments=8, rings=6)
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
    bob = 0.008 * (0.5 + 0.5 * math.cos(2 * a)) if walking else 0.0
    sway = 0.07 * math.sin(a) if walking else 0.0
    up = Vector((0, 0, bob))
    m.objects["torso"].location = TORSO + up
    sk = m.objects["skirt"]
    sk.location = Vector((0, 0, SKIRT_BOTTOM)) + up
    sk.rotation_mode = "XYZ"
    sk.rotation_euler = Euler((sway, 0, 0))
    sk.scale = (SKIRT_R[0], SKIRT_R[1], SKIRT_TOP - SKIRT_BOTTOM)
    for side, x, z in (("f", 0.108, 0.520), ("b", -0.110, 0.600)):
        st = m.objects[f"stole_{side}"]
        st.rotation_mode = "XYZ"
        st.rotation_euler = Euler((sway * 0.5, 0.10 if side == "f" else -0.10, 0.0))
        st.location = Vector((x, 0, z)) + up
    col = m.objects["collar"]
    col.location = Vector((-0.040, 0, 0.790)) + up
    col.rotation_mode = "XYZ"
    col.rotation_euler = Euler((0, -0.20, 0))
    col.scale = (0.105, 0.135, 0.090)
    for s_, k in ((1, "l"), (-1, "r")):                # big leaf shapes on the shoulders
        lf = m.objects[f"leaf_{k}"]
        lf.rotation_mode = "XYZ"
        lf.rotation_euler = Euler((0.55 * s_, -0.15, 0.25 * s_))
        lf.location = Vector((-0.010, 0.165 * s_, 0.850)) + up
    for i in range(6):                                  # a string of wooden beads across the chest
        u = i / 5
        m.objects[f"bead{i}"].location = Vector((0.110, -0.100 + 0.200 * u, 0.800 - 0.090 * math.sin(math.pi * u))) + up
    head = HEAD + up
    m.objects["head"].location = head
    m.objects["hair"].location = head + Vector((-0.045, 0, 0.040))
    m.objects["hair_long"].location = head + Vector((-0.110, 0, -0.120))
    for s, k in ((1, "l"), (-1, "r")):
        m.objects[f"eye_{k}"].location = head + Vector((0.126, 0.044 * s, 0.080))
    for s, k, phase in ((1, "l", 0.0), (-1, "r", 0.5)):
        hip = Vector((0.0, HIP_Y * s, HIP_Z)) + up
        fx, fz = _foot(t, phase)
        ankle = Vector((fx, HIP_Y * s * 1.1, 0.050 + fz))
        knee, ankle = _two_bone(hip, ankle, KNEE_LEN, SHIN_LEN, Vector((1, 0, 0)))
        m.put_segment(f"shin_{k}", knee, ankle, LEG_R * 0.9)
        m.objects[f"shoe_{k}"].location = ankle + Vector((0.030, 0, -0.010))
    # right arm hangs and sways a little; left hand raised in front at chest height, glowing
    for s, k in ((1, "l"), (-1, "r")):
        sh = Vector((SHOULDER.x, SHOULDER.y * s, SHOULDER.z)) + up
        if k == "l":
            hand = Vector((0.170, 0.110, 0.690 + 0.010 * math.sin(2 * a))) + up
        else:
            swing = 0.06 * math.sin(a) if walking else 0.0
            hand = sh + Vector((swing, -0.030, -0.32))
        elbow, hand = _two_bone(sh, hand, UPPER_ARM, FOREARM, Vector((-1, 0.3 * s, 0)))
        m.put_segment(f"upper_{k}", sh, elbow, ARM_R)
        d = (hand - elbow).normalized()
        slv = m.objects[f"sleeve_{k}"]
        m.put_segment(f"sleeve_{k}", hand - d * 0.010, elbow, ARM_R * 1.6)
        m.objects[f"hand_{k}"].location = hand + d * 0.020
        if k == "r":                                       # gnarled staff tilted out from the body
            lo = hand + Vector((0.080, 0.030, -0.300))
            hi = hand + Vector((-0.020, -0.200, 0.380))
            pts = [tuple(lo.lerp(hi, i / 6) + Vector((0.012 * math.sin(i * 2.1), 0, 0))) for i in range(7)]
            m.set_tube("staff", pts, [0.016, 0.015, 0.016, 0.014, 0.015, 0.016, 0.018])
            m.objects["staff_leaves"].location = hi + Vector((0, 0, 0.030))
        if k == "l":
            m.objects["glow"].location = hand + d * 0.040 + Vector((0, 0, 0.020))


def assign_depth_parts(m, depth_of):
    return None
