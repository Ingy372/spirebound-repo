"""Bristle boar (Floor 1, Boar Meadow): model + walk cycle, built from the approved rat.

ART_REQUESTS.md: "a wild boar with dark bristly fur, short tusks, angry red eyes". Runs inside Blender via
art/pipeline/render_creature.py. Stocky barrel body, heavy wedge head with a flat snout, pale tusks, a ridge
of bristles along the back, short legs, a thin tufted tail.

Sizes are in tiles (1 tile = 32 px). The rat faces +X (east), +Y is its left side, +Z is up.
Everything about the LOOK lives here; the camera, light and palette rules live in art/pipeline/.
"""
from __future__ import annotations

import math

from mathutils import Vector

NAME = "boar"
WALK_FRAMES = 8
PALETTE = "boar"            # ramp set in art/pipeline/palette.json
HEIGHT_SHEAR = 0.30        # a light up-left lean, like Tibia's own animals
LEAN = 18.0                 # degrees: north/south bodies run slightly diagonal, like hand-made rats
REFERENCE = "look_380.png"   # Tibia's Boar, the closest look-alike (comparison only, never shipped)
SIZE = 2.2
GROUND_STRETCH = 1.6       # full body length walking north/south, like Tibia's animals
PIXEL_RULES = {               # how art/pipeline/pixelize.py treats each part (see the notes there)
    "weight": {"tusk": 4.0, "mane": 2.6, "eye": 9.0, "nose": 4.0, "tail_tip": 5.0, "tail_base": 2.5, "paw_near": 2.2, "paw_far": 1.6,
               "leg_near": 1.7, "leg_far": 1.2, "ear": 2.2, "snout": 1.3},
    "thin": {"tusk": 2, "mane": 3, "eye": 3, "tail_tip": 2, "tail_base": 3, "nose": 3, "leg_near": 4, "leg_far": 4,
             "paw_near": 3, "paw_far": 4, "ear": 4},
    "soft": [["body", "head", "snout", "nose", "ear"]],
    "no_outline": ["tail_tip"],
    "fur": ["body", "head"],
    "texture": {"mane": [1.2, 0.0], "body": [1.4, 0.15], "head": [0.9, 0.08], "snout": [0.4, 0.0], "tail_base": [0.6, 0.0],
                "leg_near": [0.4, 0.0], "leg_far": [0.3, 0.0]},
    "bands": [0.40, 0.52, 0.62, 0.71, 0.79, 0.86, 0.93],
    "selout": ["body", "head", "snout", "ear"],
}

PARTS = ["none", "body", "head", "snout", "nose", "ear", "eye",
         "leg_near", "leg_far", "paw_near", "paw_far", "tail_base", "tail_tip", "tusk", "mane"]

OX = 0.0
CANVAS_OFFSET = (-7, 2)       # spill left of the tile like Tibia's bigger animals

# body ------------------------------------------------------------------
HIP = Vector((-0.085, 0.0, 0.240)); HIP_R = (0.122, 0.108, 0.095)
CHEST = Vector((0.055, 0.0, 0.258)); CHEST_R = (0.135, 0.122, 0.122)
HEAD = Vector((0.205, 0.0, 0.230)); HEAD_R = (0.100, 0.092, 0.092)
SNOUT_TIP = Vector((0.360, 0.0, 0.165))
EYE = Vector((0.272, 0.064, 0.268)); EYE_R = 0.014
EAR = Vector((0.170, 0.062, 0.305)); EAR_R = (0.020, 0.032, 0.052)

# legs: name -> (hip position, gait phase offset, is_front)
LEGS = {
    "fl": (Vector((0.085, -0.062, 0.200)), 0.00, True),
    "fr": (Vector((0.085, 0.062, 0.200)), 0.50, True),
    "hl": (Vector((-0.105, -0.062, 0.200)), 0.57, False),
    "hr": (Vector((-0.105, 0.062, 0.200)), 0.07, False),
}
UPPER, LOWER = 0.105, 0.100
LEG_R = 0.028
PAW_R = (0.024, 0.020, 0.016)
STRIDE = 0.092             # foot travel either side of its rest spot (about 2.5 px)
LIFT = 0.060
STANCE = 0.55              # share of the cycle a foot spends on the ground

TAIL_N = 12
BRISTLES = 11


def build(model_cls, facing):
    m = model_cls(facing, PARTS)
    m.ellipsoid("hip", "body", radii=HIP_R)
    m.ellipsoid("chest", "body", radii=CHEST_R)
    m.ellipsoid("head", "head", radii=HEAD_R)
    m.cone("snout", "snout")
    m.ellipsoid("nose", "nose", radii=(0.014, 0.014, 0.013), segments=8, rings=6)
    for s in (1, -1):
        k = "l" if s > 0 else "r"
        m.ellipsoid(f"eye_{k}", "eye", radii=(EYE_R, EYE_R * 0.8, EYE_R), segments=8, rings=6)
        m.ellipsoid(f"ear_{k}", "ear", radii=EAR_R, segments=10, rings=8)
    for leg in LEGS:
        m.capsule(f"{leg}_up", "leg_near")
        m.capsule(f"{leg}_lo", "leg_near")
        m.ellipsoid(f"{leg}_paw", "paw_near", radii=PAW_R, segments=8, rings=6)
    for k in ("l", "r"):
        m.cone(f"tusk_{k}", "tusk", segments=6)
    for i in range(BRISTLES):
        m.cone(f"mane{i}", "mane", segments=5)
    m.tube("tail_a", "tail_base", points=TAIL_N // 3 + 1)
    m.tube("tail_b", "tail_tip", points=TAIL_N - TAIL_N // 3 + 1)
    return m


def _foot(t, phase, rest_x):
    """Foot target relative to the hip's rest x. Stance: planted, slides back. Swing: lifted, comes forward."""
    if t is None:
        return rest_x, 0.0
    u = (t + phase) % 1.0
    if u < STANCE:
        k = u / STANCE
        return rest_x + STRIDE * (1 - 2 * k), 0.0
    k = (u - STANCE) / (1 - STANCE)
    ease = 0.5 - 0.5 * math.cos(math.pi * k)
    return rest_x + STRIDE * (-1 + 2 * ease), LIFT * math.sin(math.pi * k)


def _leg(m, leg, hip, foot, front):
    d = foot - hip
    dist = min(d.length, UPPER + LOWER - 1e-4)
    d.normalize()
    # bend: front elbows point back, hind knees point forward (in the leg's vertical plane)
    side = Vector((0, 0, 1)).cross(d) if abs(d.z) < 0.99 else Vector((0, 1, 0))
    bend_axis = d.cross(side).normalized()
    if bend_axis.x * (-1 if front else 1) < 0:
        bend_axis = -bend_axis
    a = (UPPER ** 2 + dist ** 2 - LOWER ** 2) / (2 * dist)
    h = math.sqrt(max(UPPER ** 2 - a ** 2, 0.0))
    knee = hip + d * a + bend_axis * h
    m.put_segment(f"{leg}_up", hip, knee, LEG_R)
    m.put_segment(f"{leg}_lo", knee, foot, LEG_R * 0.85)
    paw = m.objects[f"{leg}_paw"]
    paw.location = foot + Vector((0.012, 0, 0))


def pose(m, t):
    """t = None for the standing frame, else 0..1 through the walk cycle."""
    o = Vector((OX, 0, 0))
    if t is None:
        stretch, bob, sway = 0.0, 0.0, 0.0
    else:
        a = 2 * math.pi * t
        # diagonal trot (front-left with hind-right): legs never bunch up, the body rocks twice per cycle
        stretch = 0.35 * math.cos(2 * a)
        bob = 0.008 * (0.5 + 0.5 * math.cos(2 * a))
        sway = math.sin(a)
    chest = CHEST + o + Vector((0.016 * stretch, 0, bob + 0.006 * (1 - stretch) / 2))
    hip = HIP + o + Vector((-0.016 * stretch, 0, bob * 0.6 + 0.016 * (1 - stretch) / 2))
    head = HEAD + o + Vector((0.020 * stretch, 0, bob - 0.004 * stretch))
    m.objects["chest"].location = chest
    m.objects["hip"].location = hip
    m.objects["head"].location = head
    hd = head - (HEAD + o)
    snout_base = head + Vector((0.010, 0, -0.006))
    m.put_segment("snout", snout_base, SNOUT_TIP + o + hd, 0.064, 0.050)
    m.objects["nose"].location = SNOUT_TIP + o + hd + Vector((-0.004, 0, 0.001))
    for s, k in ((1, "l"), (-1, "r")):
        m.objects[f"eye_{k}"].location = Vector((EYE.x, EYE.y * s, EYE.z)) + o + hd
        m.objects[f"ear_{k}"].location = Vector((EAR.x, EAR.y * s, EAR.z)) + o + hd
    for leg, (hip_pt, phase, front) in LEGS.items():
        body = chest if front else hip
        base = CHEST + o if front else HIP + o
        hp = hip_pt + o + (body - base)
        fx, fz = _foot(t, phase, hip_pt.x + (0.012 if front else -0.004))
        foot = Vector((fx + OX, hip_pt.y * 1.05, PAW_R[2] + fz))
        _leg(m, leg, hp, foot, front)
    for s_, k in ((1, "l"), (-1, "r")):
        root = SNOUT_TIP + o + hd + Vector((-0.040, 0.040 * s_, -0.020))
        m.put_segment(f"tusk_{k}", root, root + Vector((0.030, 0.012 * s_, 0.045)), 0.012)
    for i in range(BRISTLES):                           # a spiky ridge of bristles from the neck to the rump
        u = i / (BRISTLES - 1)
        neck = head + Vector((-0.040, 0, HEAD_R[2] * 0.7))
        top_c = chest + Vector((0, 0, CHEST_R[2] * 0.95))
        top_h = hip + Vector((0, 0, HIP_R[2] * 0.95))
        p = neck.lerp(top_c, min(1.0, u * 2.2)) if u < 0.45 else top_c.lerp(top_h, (u - 0.45) / 0.55)
        tall = 0.170 * (1.0 - 0.40 * u) * (1.0 if i % 2 else 0.75)
        side = 0.022 * (1 if i % 3 == 0 else -1 if i % 3 == 1 else 0)
        m.put_segment(f"mane{i}", p - Vector((0, 0, 0.02)), p + Vector((-0.050, side, tall)), 0.018)
    # tail: leaves the rump, droops to the ground, curls slightly to one side, sways along its length
    base = hip + Vector((-HIP_R[0] * 0.80, 0, -0.035))
    pts, radii = [], []
    for i in range(TAIL_N + 1):
        u = i / TAIL_N
        x = base.x - 0.11 * u
        y = 0.050 * math.sin(math.pi * u * 0.9) + 0.060 * sway * math.sin(math.pi * u * 0.8) * u
        z = (base.z - 0.010) * (1 - u) ** 2.4 + 0.010 + 0.022 * max(0.0, u - 0.75) / 0.25 \
            + 0.018 * sway * math.sin(math.pi * u) * (t is not None)
        pts.append((x, y, z))
        radii.append(0.017 * (1 - u) + 0.006)
    half = TAIL_N // 3
    m.set_tube("tail_a", pts[:half + 1], radii[:half + 1])
    m.set_tube("tail_b", pts[half:], radii[half:])


def assign_depth_parts(m, depth_of):
    """Legs on the far side of the body (seen from the camera) use the darker 'far' ramp."""
    body_depth = depth_of(m.objects["chest"].matrix_world.translation) * 0.5 + \
        depth_of(m.objects["hip"].matrix_world.translation) * 0.5
    for leg in LEGS:
        hip_world = m.objects[f"{leg}_up"].matrix_world.translation
        far = depth_of(hip_world) > body_depth + 0.005
        for piece in ("up", "lo"):
            m.set_part(f"{leg}_{piece}", "leg_far" if far else "leg_near")
        m.set_part(f"{leg}_paw", "paw_far" if far else "paw_near")
