"""Goldback Toad (Floor 1 rare roamer, levels 5-12; adventure design 4.4): built on the approved Hopper Toad (toad.py,
frozen), so it hops the same way and reads as "a toad, but THAT toad".

Identity (art/CRAWLER_RULES.md step 1):
  Coat:      deep bottle-green, almost black on the flanks (Tibia's toad is orange-gold; our common toad is
             emerald-teal), so the gold reads as treasure and not as the animal's colour.
  Signature: a back covered in raised gold plates like coins (the "gold back", seen from every direction from above)
             and a tiny gold crown with a ruby between the eyes. Ruby-red eyes.
  Attitude:  smug and skittish: head up, puffed body, ready to hop away (it flees in the game).

Detail (art/DETAIL_RULES.md): the toad's anatomy is the frozen base's (five body lumps, brow ridges, slit pupils, a
mouth line, two-part legs with toes); on top: a mosaic of gold plates in three sizes (big coins along the spine,
medium ones on the flanks, small gold warts), a crown band with three points and a ruby, cream belly.
Real proportion: a toad is wider than it is tall and its eyes sit on top of the head (the base's measurements).
"""
from __future__ import annotations

import math

from mathutils import Vector

import toad as T

NAME = "goldback_toad"
WALK_FRAMES = 8
PALETTE = "goldback_toad"
HEIGHT_SHEAR = T.HEIGHT_SHEAR
LEAN = T.LEAN
REFERENCE = "look_222.png"   # Tibia's Toad (comparison only, never shipped)
SIZE = 2.15                  # a little bigger than the pond's toads
GROUND_STRETCH = T.GROUND_STRETCH
AUTO_PLACE = (1, 1)
SIGNATURE = ["coin", "crown"]
HEAD_PARTS = ["head", "eye", "pupil", "line", "crown", "ruby"]
LEG_PARTS = ["leg", "foot"]

PARTS = T.PARTS + ["coin", "crown", "ruby"]
PIXEL_RULES = {**T.PIXEL_RULES,
               "weight": {**T.PIXEL_RULES["weight"], "coin": 3.0, "crown": 4.0, "ruby": 9.0},
               "thin": {**T.PIXEL_RULES["thin"], "coin": 2, "crown": 2, "ruby": 2},
               "soft": [["body", "belly", "blotch", "wart", "stripe", "head", "line"], ["eye", "pupil"], ["leg", "foot"],
                        ["coin", "line"], ["crown", "ruby"]],
               "texture": {**T.PIXEL_RULES["texture"], "coin": [0.7, 0.35]},
               "selout": ["body", "head", "coin", "crown"]}

# gold plates on the back: (x, y, size) on the body's top; big ones down the spine, smaller toward the flanks
COINS = [(-0.140, 0.0, 0.85), (-0.090, 0.0, 1.0), (-0.035, 0.0, 1.05), (0.020, 0.0, 0.9)]   # a ridge of nuggets
POINTS = 3


def build(model_cls, facing):
    saved, T.PARTS = T.PARTS, PARTS    # the base builds its model with its module's part list: lend it ours
    try:
        m = T.build(model_cls, facing)
    finally:
        T.PARTS = saved
    m.ellipsoid("saddle", "coin", radii=(0.125, 0.085, 0.030), segments=18, rings=8)      # the gold back itself
    for i in range(len(COINS)):
        m.ellipsoid(f"coin{i}", "crown", radii=(0.016, 0.016, 0.012), segments=8, rings=6)  # bright gold nuggets
    m.ellipsoid("band", "crown", radii=(0.036, 0.050, 0.016), segments=12, rings=6)
    for i in range(POINTS):
        m.cone(f"point{i}", "crown", segments=5)
    m.ellipsoid("ruby", "ruby", radii=(0.010, 0.010, 0.010), segments=8, rings=6)
    return m


def pose(m, t):
    T.pose(m, t)
    body = m.objects["body"].location
    head = m.objects["head"].location
    rot = m.objects["body"].rotation_euler
    v = Vector((-0.040, 0, 0.068))
    v.rotate(rot)
    sad = m.objects["saddle"]
    sad.location = body + v
    sad.rotation_mode = "XYZ"
    sad.rotation_euler = rot
    for i, (x, y, sc) in enumerate(COINS):
        z = 0.108 * math.sqrt(max(0.05, 1 - (x / 0.170) ** 2 - (y / 0.170) ** 2))
        v = Vector((x, y, z))
        v.rotate(rot)
        ob = m.objects[f"coin{i}"]
        ob.location = body + v
        ob.rotation_mode = "XYZ"
        ob.rotation_euler = rot
        ob.scale = (0.026 * sc, 0.026 * sc, 0.016)
    # the crown sits between the eyes, on top of the head, tipped back a little
    top = head + Vector((0.010, 0, 0.074))
    m.objects["band"].location = top
    for i in range(POINTS):
        a = (i - 1) * 0.9
        base = top + Vector((0.014 * math.cos(a) - 0.004, 0.040 * math.sin(a), 0.006))
        tall = 0.046 if i == 1 else 0.036
        m.put_segment(f"point{i}", base, base + Vector((-0.006, 0.006 * math.sin(a), tall)), 0.014, 0.003)
    m.objects["ruby"].location = top + Vector((0.026, 0, 0.004))


def assign_depth_parts(m, depth_of):
    return None
