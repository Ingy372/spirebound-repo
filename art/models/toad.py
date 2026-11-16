"""Hopper toad (Floor 1, Toad Pond): model + hop cycle.

ART_REQUESTS.md: "a fat green-and-yellow toad with big eyes, mid-hop pose for walking frames".

Identity (art/CRAWLER_RULES.md step 1):
  Coat:      mottled emerald-teal back (Tibia's toad is orange-gold; the meadow grass is yellow-green) with dark
             blotches and pale raised warts, a cream-yellow throat and belly.
  Signature: a pale dorsal stripe, copper-gold eyes under heavy brow ridges, a wide grim mouth line.
  Attitude:  squat and coiled: flat wide body, hind legs folded in a Z, ready to spring.

Detail (art/DETAIL_RULES.md): body made of several lumps (not one ball), brows, a drawn mouth line, warts and
blotches, two-part legs with splayed toes. Its walk is one hop per cycle: crouch, push off, fly, land, settle.
"""
from __future__ import annotations

import math

from mathutils import Euler, Vector

NAME = "toad"
WALK_FRAMES = 8
PALETTE = "toad"
HEIGHT_SHEAR = 0.30
LEAN = 10.0
REFERENCE = "look_222.png"   # Tibia's Toad, the closest look-alike (comparison only, never shipped)
SIZE = 2.15
GROUND_STRETCH = 1.1
AUTO_PLACE = (1, 1)
SIGNATURE = ["stripe", "eye"]
HEAD_PARTS = ["head", "eye", "pupil", "line"]
LEG_PARTS = ["leg", "foot"]
PIXEL_RULES = {
    "weight": {"eye": 5.0, "pupil": 9.0, "blotch": 1.6, "wart": 2.6, "leg": 1.6, "foot": 2.4, "belly": 1.2,
               "stripe": 2.0, "line": 3.5},
    "thin": {"pupil": 2, "eye": 3, "blotch": 4, "wart": 3, "leg": 4, "foot": 2, "stripe": 3, "line": 2},
    "soft": [["body", "belly", "blotch", "wart", "stripe", "head", "line"], ["eye", "pupil"], ["leg", "foot"]],
    "no_outline": [],
    "fur": [],
    "texture": {"body": [0.9, 0.35], "head": [0.7, 0.25], "belly": [0.4, 0.0], "leg": [0.6, 0.2]},
    "bands": [0.40, 0.52, 0.62, 0.71, 0.79, 0.86, 0.93],
    "selout": ["body", "head"],
}

PARTS = ["none", "body", "belly", "blotch", "wart", "eye", "pupil", "leg", "foot", "head", "stripe", "line"]

BLOTCHES = [(-0.070, 0.070, 0.9), (0.030, -0.085, 1.0), (-0.110, -0.040, 0.8), (0.060, 0.060, 0.7), (-0.020, -0.010, 0.6)]
WARTS = [(-0.120, 0.060), (-0.090, -0.095), (-0.030, 0.105), (0.020, 0.030), (0.070, -0.040), (-0.050, -0.055),
         (0.090, 0.095), (-0.140, -0.010), (0.010, -0.120), (-0.010, 0.070)]
MOUTH_N = 9


def build(model_cls, facing):
    m = model_cls(facing, PARTS)
    m.ellipsoid("body", "body", radii=(0.165, 0.165, 0.088), segments=20, rings=10)
    for k in ("l", "r"):
        m.ellipsoid(f"flank_{k}", "body", radii=(0.095, 0.070, 0.072), segments=14, rings=8)   # bulging sides
    m.ellipsoid("rump", "body", radii=(0.080, 0.110, 0.070), segments=14, rings=8)
    m.ellipsoid("head", "head", radii=(0.098, 0.132, 0.062), segments=16, rings=8)                # wide flat wedge
    m.ellipsoid("belly", "belly", radii=(0.150, 0.140, 0.050), segments=16, rings=8)
    m.ellipsoid("throat", "belly", radii=(0.070, 0.105, 0.040), segments=14, rings=8)
    m.ellipsoid("stripe", "stripe", radii=(0.150, 0.014, 0.012), segments=12, rings=6)
    m.tube("mouth", "line", points=MOUTH_N)
    for i in range(len(BLOTCHES)):
        m.ellipsoid(f"blotch{i}", "blotch", radii=(0.034, 0.026, 0.008), segments=10, rings=6)
    for i in range(len(WARTS)):
        m.ellipsoid(f"wart{i}", "wart", radii=(0.014, 0.013, 0.010), segments=8, rings=6)
    for k in ("l", "r"):
        m.ellipsoid(f"brow_{k}", "head", radii=(0.044, 0.036, 0.030), segments=10, rings=8)
        m.ellipsoid(f"eye_{k}", "eye", radii=(0.026, 0.024, 0.024), segments=10, rings=8)
        m.ellipsoid(f"pupil_{k}", "pupil", radii=(0.008, 0.016, 0.010), segments=8, rings=6)    # a level slit
        m.capsule(f"farm_{k}", "leg", segments=8)
        m.capsule(f"fore_{k}", "leg", segments=8)
        m.capsule(f"thigh_{k}", "leg", segments=8)
        m.capsule(f"shin_{k}", "leg", segments=8)
        m.capsule(f"hfoot_{k}", "leg", segments=8)
        for j in range(3):
            m.cone(f"ftoe{j}_{k}", "foot", segments=5)
            m.cone(f"htoe{j}_{k}", "foot", segments=5)
    return m


def pose(m, t):
    u = 0.0 if t is None else t
    hop = t is not None
    # hop profile: 0-0.08 crouch, 0.08-0.68 in the air, then land and settle
    air = max(0.0, math.sin(math.pi * (u - 0.08) / 0.6)) if hop and 0.08 <= u <= 0.68 else 0.0
    crouch = max(0.0, 1.0 - abs(u - 0.0) / 0.08) if hop else 0.0
    land = max(0.0, 1.0 - abs(u - 0.78) / 0.12) if hop else 0.0
    lift = 0.100 * air
    squash = 1.0 - 0.12 * (crouch + land) + 0.06 * air
    pitch = -0.30 * air if u < 0.42 else -0.30 * air + 0.25 * land     # nose up taking off, down landing
    body = Vector((0.03 * air, 0, 0.092 + lift))
    rot = Euler((0, pitch, 0))

    def put(name, offset, scale=None):
        ob = m.objects[name]
        v = Vector(offset)
        v.z *= squash
        v.rotate(rot)
        ob.location = body + v
        ob.rotation_mode = "XYZ"
        ob.rotation_euler = rot
        if scale:
            ob.scale = (scale[0], scale[1], scale[2] * squash)
        return ob.location.copy()

    put("body", (0, 0, 0), (0.165, 0.165, 0.088))
    put("rump", (-0.110, 0, -0.012))
    put("belly", (0.015, 0, -0.042))
    for s, k in ((1, "l"), (-1, "r")):
        put(f"flank_{k}", (-0.045, 0.118 * s, -0.012))
    put("head", (0.150, 0, 0.012))
    put("throat", (0.185, 0, -0.028))
    put("stripe", (-0.010, 0, 0.084))
    # the mouth: a dark line drawn round the front of the head, slightly turned down at the corners
    pts = []
    for i in range(MOUTH_N):
        th = -1.25 + 2.5 * i / (MOUTH_N - 1)
        v = Vector((0.150 + 0.100 * math.cos(th), 0.134 * math.sin(th), -0.004 - 0.010 * abs(math.sin(th))))
        v.z *= squash
        v.rotate(rot)
        pts.append(tuple(body + v))
    m.set_tube("mouth", pts, [0.007] * MOUTH_N)
    for i, (x, y, sc) in enumerate(BLOTCHES):
        z = 0.086 * math.sqrt(max(0.05, 1 - (x / 0.165) ** 2 - (y / 0.165) ** 2))
        put(f"blotch{i}", (x, y, z))
        m.objects[f"blotch{i}"].scale = (0.034 * sc, 0.026 * sc, 0.008)
    for i, (x, y) in enumerate(WARTS):
        z = 0.090 * math.sqrt(max(0.05, 1 - (x / 0.170) ** 2 - (y / 0.170) ** 2))
        put(f"wart{i}", (x, y, z))
    for s, k in ((1, "l"), (-1, "r")):
        put(f"brow_{k}", (0.150, 0.078 * s, 0.058))
        eye = put(f"eye_{k}", (0.166, 0.090 * s, 0.070))
        m.objects[f"pupil_{k}"].location = eye + Vector((0.016, 0.012 * s, 0.012))
        # front legs: elbow out, hand planted with three toes fanned forward
        sh = body + Vector((0.095, 0.105 * s, -0.020))
        hand = Vector((body.x + 0.165 + 0.050 * air, 0.150 * s, 0.012 + lift * 0.45))
        elbow = sh.lerp(hand, 0.5) + Vector((-0.030, 0.035 * s, 0.030))
        m.put_segment(f"farm_{k}", sh, elbow, 0.026)
        m.put_segment(f"fore_{k}", elbow, hand, 0.020)
        for j in range(3):
            fan = (j - 1) * 0.55 + 0.25 * s
            m.put_segment(f"ftoe{j}_{k}", hand, hand + Vector((0.050 * math.cos(fan), 0.050 * math.sin(fan), -0.006)), 0.011)
        # hind legs: folded in a Z beside the body, stretched straight back on take-off
        hip = body + Vector((-0.105, 0.105 * s, -0.020))
        stretch = air if u < 0.42 else air * 0.5
        foot = Vector((body.x - 0.115 - 0.200 * stretch, (0.185 - 0.030 * stretch) * s, 0.012 + lift * 0.3 * (1 - stretch)))
        knee = hip + Vector((0.085 * (1 - stretch) - 0.060 * stretch, 0.060 * s, 0.040 * (1 - stretch)))
        ankle = knee.lerp(foot, 0.55) + Vector((-0.060 * (1 - stretch), 0.020 * s, 0.0))
        ankle.z = max(0.014, ankle.z - 0.020)
        m.put_segment(f"thigh_{k}", hip, knee, 0.040)
        m.put_segment(f"shin_{k}", knee, ankle, 0.028)
        m.put_segment(f"hfoot_{k}", ankle, foot, 0.019)
        for j in range(3):
            fan = (j - 1) * 0.50 + 0.45 * s * (1 - stretch) + math.pi * stretch
            m.put_segment(f"htoe{j}_{k}", foot, foot + Vector((0.062 * math.cos(fan), 0.062 * math.sin(fan), -0.004)), 0.012)


def assign_depth_parts(m, depth_of):
    return None
