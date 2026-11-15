"""Burrow mole (Floor 1, Burrow Hills): model + walk cycle, built from the approved rat.

ART_REQUESTS.md: "a stocky grey-brown mole with huge pale digging claws, tiny eyes, a pink nose, a little dirt
on its back". Runs inside Blender via art/pipeline/render_creature.py.

Sizes are in tiles (1 tile = 32 px). The rat faces +X (east), +Y is its left side, +Z is up.
Everything about the LOOK lives here; the camera, light and palette rules live in art/pipeline/.
"""
from __future__ import annotations

import math

from mathutils import Vector

NAME = "mole"
WALK_FRAMES = 8
PALETTE = "mole"            # ramp set in art/pipeline/palette.json
HEIGHT_SHEAR = 0.30        # a light up-left lean, like Tibia's own animals
LEAN = 18.0                # degrees: north/south bodies run slightly diagonal, like hand-made rats
REFERENCE = "look_1048.png"   # Tibia's Mole, the closest look-alike (comparison only, never shipped)
SIZE = 2.0
GROUND_STRETCH = 1.6       # full body length walking north/south, like Tibia's animals
PIXEL_RULES = {               # how art/pipeline/pixelize.py treats each part (see the notes there)
    "weight": {"dirt": 2.0, "eye": 9.0, "nose": 4.0, "tail_tip": 5.0, "tail_base": 2.5, "paw_near": 2.2, "paw_far": 1.6,
               "leg_near": 1.7, "leg_far": 1.2, "ear": 2.2, "snout": 1.3},
    "thin": {"eye": 3, "tail_tip": 2, "tail_base": 3, "nose": 3, "leg_near": 4, "leg_far": 4,
             "paw_near": 3, "paw_far": 4, "ear": 4},
    "soft": [["body", "head", "snout", "nose", "ear", "dirt"]],
    "no_outline": ["tail_tip"],
    "fur": ["body", "head"],
    "texture": {"body": [1.4, 0.15], "head": [0.9, 0.08], "snout": [0.4, 0.0], "tail_base": [0.6, 0.0],
                "leg_near": [0.4, 0.0], "leg_far": [0.3, 0.0]},
    "bands": [0.42, 0.55, 0.66, 0.75, 0.83, 0.90, 0.96],
    "selout": ["body", "head", "snout", "ear"],
}

PARTS = ["none", "body", "head", "snout", "nose", "ear", "eye",
         "leg_near", "leg_far", "paw_near", "paw_far", "tail_base", "tail_tip", "dirt"]

OX = 0.0
CANVAS_OFFSET = (-7, -3)       # spill left of the tile like Tibia's bigger animals

# body ------------------------------------------------------------------
HIP = Vector((-0.070, 0.0, 0.124)); HIP_R = (0.140, 0.122, 0.088)
CHEST = Vector((0.045, 0.0, 0.118)); CHEST_R = (0.112, 0.112, 0.080)
HEAD = Vector((0.150, 0.0, 0.112)); HEAD_R = (0.076, 0.080, 0.066)
SNOUT_TIP = Vector((0.272, 0.0, 0.088))
EYE = Vector((0.188, 0.056, 0.138)); EYE_R = 0.009
EAR = Vector((0.100, 0.030, 0.120)); EAR_R = (0.010, 0.010, 0.010)   # moles have no visible ears: hidden inside the head

# legs: name -> (hip position, gait phase offset, is_front)
LEGS = {
    "fl": (Vector((0.100, -0.110, 0.085)), 0.00, True),
    "fr": (Vector((0.100, 0.110, 0.085)), 0.50, True),
    "hl": (Vector((-0.080, -0.085, 0.085)), 0.57, False),
    "hr": (Vector((-0.080, 0.085, 0.085)), 0.07, False),
}
UPPER, LOWER = 0.046, 0.046
LEG_R = 0.026
PAW_R = (0.026, 0.020, 0.014)
PAW_R_FRONT = (0.042, 0.044, 0.016)   # huge flat digging claws
STRIDE = 0.062             # foot travel either side of its rest spot (about 2.5 px)
LIFT = 0.040
STANCE = 0.55              # share of the cycle a foot spends on the ground

TAIL_N = 12


SCALE = 1.25               # a stocky burrower, bigger than the rat


def build(model_cls, facing):
    import bpy
    body = bpy.data.objects.new("MoleScale", None)
    body.parent = facing
    body.scale = (SCALE, SCALE, SCALE)
    bpy.context.scene.collection.objects.link(body)
    m = model_cls(body, PARTS)
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
        m.ellipsoid(f"{leg}_paw", "paw_near", radii=PAW_R_FRONT if LEGS[leg][2] else PAW_R, segments=8, rings=6)
        if LEGS[leg][2]:
            for j in range(3):
                m.cone(f"{leg}_claw{j}", "paw_near", segments=5)
    m.ellipsoid("dirt", "dirt", radii=(0.020, 0.018, 0.008), segments=10, rings=6)
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
    side = 1.0 if foot.y > 0 else -1.0
    # the big digging claws sit forward and out to the sides, so they show from above in every direction
    paw.location = foot + (Vector((0.045, 0.035 * side, 0.010)) if front else Vector((0.012, 0, 0)))
    if front:
        for j in range(3):                     # three long pale claws fanning forward
            sp = (j - 1) * 0.030
            root = paw.location + Vector((0.025, sp, 0.004))
            m.put_segment(f"{leg}_claw{j}", root, root + Vector((0.065, sp * 0.8 + 0.010 * side, -0.006)), 0.013)


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
    m.put_segment("snout", snout_base, SNOUT_TIP + o + hd, 0.048, 0.056)
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
    m.objects["dirt"].location = hip + Vector((0.010, 0.020, HIP_R[2] * 0.93))
    # tail: leaves the rump, droops to the ground, curls slightly to one side, sways along its length
    base = hip + Vector((-HIP_R[0] * 0.80, 0, -0.035))
    pts, radii = [], []
    for i in range(TAIL_N + 1):
        u = i / TAIL_N
        x = base.x - 0.10 * u
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
        for j in range(3):
            if f"{leg}_claw{j}" in m.objects:
                m.set_part(f"{leg}_claw{j}", "paw_far" if far else "paw_near")
