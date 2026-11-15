"""Hopper toad (Floor 1, Toad Pond): model + hop cycle.

ART_REQUESTS.md: "a fat green-and-yellow toad with big eyes, mid-hop pose for walking frames".

Identity (art/CRAWLER_RULES.md step 1):
  Coat:      deep emerald-teal back (Tibia's toad is orange-gold; the meadow grass is yellow-green) with dark
             warts, a lemon-yellow throat and belly.
  Signature: a bright yellow stripe down the spine and big golden eyes on top of the head (both show from above).
  Attitude:  squat and coiled, head up, ready to spring.
Its walk is one hop per cycle: crouch, push off with the long hind legs (body up, legs stretched back),
land on the front legs, settle. Low creature: "tilt" projection like the rat. Faces +X; sizes in tiles.
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
SIZE = 1.9
GROUND_STRETCH = 1.1       # longer north/south view, like Tibia's creatures
AUTO_PLACE = (1, 1)
SIGNATURE = ["stripe", "eye"]
HEAD_PARTS = ["head", "eye", "pupil"]
LEG_PARTS = ["leg", "foot"]
PIXEL_RULES = {
    "weight": {"eye": 4.0, "pupil": 9.0, "spot": 2.0, "leg": 1.8, "foot": 2.0, "belly": 1.2, "stripe": 2.2},
    "thin": {"pupil": 3, "eye": 3, "spot": 3, "leg": 3, "foot": 3, "stripe": 3},
    "soft": [["body", "belly", "spot", "stripe", "head"], ["eye", "pupil"]],
    "no_outline": [],
    "fur": [],
    "texture": {"body": [1.0, 0.25], "head": [0.7, 0.15], "belly": [0.5, 0.0], "leg": [0.5, 0.0], "stripe": [0.4, 0.0]},
    "bands": [0.42, 0.55, 0.66, 0.75, 0.83, 0.90, 0.96],
    "selout": ["body", "eye"],
}

PARTS = ["none", "body", "belly", "spot", "eye", "pupil", "leg", "foot", "head", "stripe"]

OX = 0.0


SCALE = 1.15


def build(model_cls, facing):
    import bpy
    body = bpy.data.objects.new("ToadScale", None)
    body.parent = facing
    body.scale = (SCALE, SCALE, SCALE)
    bpy.context.scene.collection.objects.link(body)
    m = model_cls(body, PARTS)
    m.ellipsoid("body", "body", radii=(0.165, 0.150, 0.100), segments=20, rings=10)
    m.ellipsoid("head", "head", radii=(0.090, 0.120, 0.070), segments=16, rings=8)
    m.ellipsoid("belly", "belly", radii=(0.150, 0.130, 0.060), segments=16, rings=8)
    m.ellipsoid("stripe", "stripe", radii=(0.150, 0.026, 0.020), segments=14, rings=6)
    for i in range(4):
        m.ellipsoid(f"spot{i}", "spot", radii=(0.030, 0.026, 0.012), segments=10, rings=6)
    for k in ("l", "r"):
        m.ellipsoid(f"eye_{k}", "eye", radii=(0.040, 0.040, 0.040), segments=12, rings=8)
        m.ellipsoid(f"pupil_{k}", "pupil", radii=(0.016, 0.016, 0.016), segments=8, rings=6)
        m.capsule(f"farm_{k}", "leg", segments=8)
        m.ellipsoid(f"ffoot_{k}", "foot", radii=(0.030, 0.026, 0.010), segments=10, rings=6)
        m.capsule(f"thigh_{k}", "leg", segments=8)
        m.capsule(f"shin_{k}", "leg", segments=8)
        m.ellipsoid(f"hfoot_{k}", "foot", radii=(0.048, 0.030, 0.010), segments=10, rings=6)
    return m


SPOTS = [(-0.050, 0.060), (0.020, -0.070), (-0.090, -0.030), (0.050, 0.040)]


def pose(m, t):
    u = 0.0 if t is None else t
    hop = t is not None
    # hop profile: 0-0.15 crouch, 0.15-0.65 in the air, 0.65-1 land and settle
    air = max(0.0, math.sin(math.pi * (u - 0.08) / 0.6)) if hop and 0.08 <= u <= 0.68 else 0.0
    crouch = max(0.0, 1.0 - abs(u - 0.0) / 0.08) if hop else 0.0
    land = max(0.0, 1.0 - abs(u - 0.78) / 0.12) if hop else 0.0
    lift = 0.090 * air
    squash = 1.0 - 0.10 * (crouch + land) + 0.06 * air
    pitch = -0.30 * air if u < 0.42 else -0.30 * air + 0.25 * land     # nose up when taking off, down when landing
    o = Vector((OX + 0.03 * air, 0, 0))
    body = Vector((0, 0, 0.095 + lift)) + o
    for name, base, sc in (("body", body, (0.165, 0.150, 0.100 * squash)),
                           ("belly", body + Vector((0.020, 0, -0.040)), (0.150, 0.130, 0.060 * squash))):
        ob = m.objects[name]
        ob.location = base
        ob.rotation_mode = "XYZ"
        ob.rotation_euler = Euler((0, pitch, 0))
        ob.scale = sc
    head = body + Vector((0.130, 0, 0.020 + 0.040 * (-pitch)))
    m.objects["head"].location = head
    st = m.objects["stripe"]
    st.location = body + Vector((0.010, 0, 0.088 * squash))
    st.rotation_mode = "XYZ"
    st.rotation_euler = Euler((0, pitch, 0))
    for i, (x, y) in enumerate(SPOTS):
        m.objects[f"spot{i}"].location = body + Vector((x, y, 0.092 * squash))
    for s, k in ((1, "l"), (-1, "r")):
        eye = head + Vector((0.020, 0.068 * s, 0.058))
        m.objects[f"eye_{k}"].location = eye
        m.objects[f"pupil_{k}"].location = eye + Vector((0.022, 0.010 * s, 0.026))
        # front legs: reach forward in the air, plant on landing
        sh = body + Vector((0.110, 0.100 * s, -0.030))
        ff = Vector((body.x + 0.160 + 0.050 * air, 0.120 * s, 0.010 + lift * 0.4))
        m.put_segment(f"farm_{k}", sh, ff, 0.020)
        m.objects[f"ffoot_{k}"].location = ff + Vector((0.015, 0, -0.004))
        # hind legs: folded beside the body, stretched back on take-off
        hip = body + Vector((-0.100, 0.120 * s, -0.020))
        stretch = air if u < 0.42 else air * 0.5
        foot = Vector((body.x - 0.150 - 0.170 * stretch, 0.150 * s, 0.010 + lift * 0.3 * (1 - stretch)))
        knee = hip.lerp(foot, 0.5) + Vector((0.070 * (1 - stretch), 0.020 * s, 0.050 * (1 - stretch)))
        m.put_segment(f"thigh_{k}", hip, knee, 0.034)
        m.put_segment(f"shin_{k}", knee, foot, 0.024)
        m.objects[f"hfoot_{k}"].location = foot + Vector((-0.020 * stretch, 0, -0.004))


def assign_depth_parts(m, depth_of):
    return None
