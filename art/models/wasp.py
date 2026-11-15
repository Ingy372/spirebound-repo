"""Meadow wasp (Floor 1, Waspgrass Fields): model + hover cycle.

ART_REQUESTS.md: "a large striped wasp the size of a dog, yellow and black, translucent wings, a long stinger".

Identity (art/CRAWLER_RULES.md step 1):
  Coat:      deep amber-gold and blue-black bands (Tibia's wasp is lemon yellow and brown-black), a russet fuzzy thorax.
  Signature: a long black hooked stinger, big ember-red compound eyes, glassy wings the body shows through.
  Attitude:  hunting: long abdomen hanging low with the stinger hooked down, wings a blur.
It flies, so its "walk" is a hover: two wing beats per cycle, the body bobbing and the legs dangling.
Low creature: "tilt" projection like the rat. Faces +X (east), +Y left, +Z up; sizes in tiles.
"""
from __future__ import annotations

import math

from mathutils import Euler, Vector

NAME = "wasp"
WALK_FRAMES = 8
PALETTE = "wasp"
HEIGHT_SHEAR = 0.30
LEAN = 10.0
REFERENCE = "look_44.png"   # Tibia's Wasp, the closest look-alike (comparison only, never shipped)
SIZE = 1.25
GROUND_STRETCH = 1.4       # longer north/south view, like Tibia's creatures
AUTO_PLACE = (1, 1)
SIGNATURE = ["eye", "stinger"]
HEAD_PARTS = ["head", "face", "eye"]
LEG_PARTS = ["leg"]
CHECK = {"signature": 3, "size": (0.85, 1.45), "legs_side": 0.02, "legs_updown": 0.0}   # "the size of a dog"; a flier's legs dangle thin; the stinger is a thin point (hidden from the front)
PIXEL_RULES = {
    "weight": {"eye": 4.0, "stinger": 4.0, "leg": 2.4, "antenna": 3.0, "wing": 0.35, "stripe": 1.2, "head": 1.4},
    "thin": {"eye": 3, "stinger": 2, "leg": 2, "antenna": 2, "wing": 4},
    "soft": [["thorax", "abdomen", "stripe", "head", "face"], ["head", "eye", "face"]],
    "no_outline": ["antenna"],
    "fur": ["thorax"],
    "selout": ["abdomen", "thorax"],
    "texture": {"thorax": [1.2, 0.2], "abdomen": [0.4, 0.1], "stripe": [0.3, 0.0], "head": [0.5, 0.0]},
    "bands": [0.34, 0.45, 0.55, 0.64, 0.73, 0.82, 0.90],
}

PARTS = ["none", "thorax", "abdomen", "stripe", "head", "face", "eye", "stinger", "wing", "leg", "antenna"]

FLY_Z = 0.30                       # hovering height of the body
OX = 0.10                          # nudged forward so the long abdomen and stinger stay on the canvas


SCALE = 1.12               # "the size of a dog": bigger than the rat


def build(model_cls, facing):
    import bpy
    body = bpy.data.objects.new("WaspScale", None)
    body.parent = facing
    body.scale = (SCALE, SCALE, SCALE)
    bpy.context.scene.collection.objects.link(body)
    m = model_cls(body, PARTS)
    m.ellipsoid("thorax", "thorax", radii=(0.075, 0.068, 0.068))
    m.ellipsoid("head", "head", radii=(0.064, 0.074, 0.064))
    m.ellipsoid("face", "face", radii=(0.030, 0.042, 0.038), segments=10, rings=8)
    for k in ("l", "r"):
        m.ellipsoid(f"eye_{k}", "eye", radii=(0.032, 0.024, 0.040), segments=10, rings=8)
        m.tube(f"antenna_{k}", "antenna", points=4)
    for i in range(5):                                     # abdomen: alternating yellow and black bands
        m.ellipsoid(f"seg{i}", "abdomen" if i % 2 == 0 else "stripe", radii=(0.040, 0.075, 0.068))
    m.cone("stinger", "stinger", segments=8)
    for k in ("l", "r"):
        for w in ("f", "b"):
            m.ellipsoid(f"wing_{w}{k}", "wing", radii=(0.092, 0.030, 0.006), segments=14, rings=6)
        for j in range(3):
            m.capsule(f"leg{j}_{k}", "leg", segments=6)
    return m


def pose(m, t):
    a = 0.0 if t is None else 2 * math.pi * t
    hover = t is not None
    bob = 0.025 * math.sin(a) if hover else 0.0
    flap = 1.5 * math.sin(2 * a) if hover else 0.4         # two big wing beats per cycle: a blur
    o = Vector((OX, 0, FLY_Z + bob))
    tilt = 0.10 * math.cos(a) if hover else 0.0            # the abdomen swings up and down a little
    thorax = o
    m.objects["thorax"].location = thorax
    head = thorax + Vector((0.112, 0, 0.012))
    m.objects["head"].location = head
    m.objects["face"].location = head + Vector((0.034, 0, -0.010))
    for s, k in ((1, "l"), (-1, "r")):
        m.objects[f"eye_{k}"].location = head + Vector((0.018, 0.054 * s, 0.010))
        base = head + Vector((0.030, 0.022 * s, 0.040))
        pts = [base + Vector((0.030 * i, 0.012 * s * i, 0.030 * i - 0.006 * i * i)) for i in range(4)]
        m.set_tube(f"antenna_{k}", [tuple(p) for p in pts], [0.006] * 4)
    # abdomen: a chain of bands hanging back and down from the waist, ending in the stinger
    waist = thorax + Vector((-0.075, 0, -0.010))
    for i in range(5):
        u = i / 4
        r = 0.050 + 0.040 * math.sin(math.pi * (u * 0.85 + 0.1))
        p = waist + Vector((-0.050 - 0.060 * i, 0, -0.030 * i - 0.003 * i * i - tilt * 0.06 * i))
        seg = m.objects[f"seg{i}"]
        seg.location = p
        seg.scale = (0.042, r, r * 0.92)
    tail = waist + Vector((-0.050 - 0.060 * 4, 0, -0.030 * 4 - 0.048 - tilt * 0.24))
    m.put_segment("stinger", tail + Vector((-0.030, 0, -0.005)), tail + Vector((-0.100, 0, -0.090)), 0.026)
    # wings: hinged on top of the thorax, sweeping up and down
    for s, k in ((1, "l"), (-1, "r")):
        for w, dx, back in (("f", 0.010, 0.0), ("b", -0.030, 0.35)):
            wing = m.objects[f"wing_{w}{k}"]
            ang = 0.55 * flap + 0.25
            wing.rotation_mode = "XYZ"
            wing.rotation_euler = Euler((ang * s, 0.0, (0.45 + back) * s * -1 + math.pi / 2 * s))
            reach = Vector((-0.030 - back * 0.08, 0.080 * s * math.cos(ang), 0.080 * math.sin(ang)))
            wing.location = thorax + Vector((dx, 0.020 * s, 0.050)) + reach
    # legs: three pairs dangling under the thorax, swinging a little
    for s, k in ((1, "l"), (-1, "r")):
        for j in range(3):
            hip = thorax + Vector((0.040 - 0.040 * j, 0.040 * s, -0.050))
            swing = 0.025 * math.sin(a + j * 1.2) if hover else 0.0
            foot = hip + Vector((0.020 - 0.040 * j + swing, 0.050 * s, -0.110))
            m.put_segment(f"leg{j}_{k}", hip, foot, 0.010)


def assign_depth_parts(m, depth_of):
    return None
