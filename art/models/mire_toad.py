"""Mire Toad (the Underkeep, Wing 1; tuned to Floor 2): a poisonous cave toad of the flooded halls. Built on the
approved Hopper Toad (toad.py, frozen) like the Goldback, so it hops the same way and reads as a toad, but a bigger,
fouler one that has lived in the dark.

Identity (art/CRAWLER_RULES.md step 1):
  Coat:      slate-violet cave-mud skin with near-black blotches (Tibia's toad is orange-gold; the pond's toad is
             emerald-teal; the Goldback bottle-green), a dirty lichen-ochre belly.
  Signature: glowing poison-green glands: two big swollen ones behind the eyes, a row of smaller ones down each flank,
             and a toxic green seam down the spine (all on top, so they show from every direction); slime dripping
             from the jaw.
  Attitude:  heavy and sullen: a big squat body, sickly yellow-green eyes, ready to spit.

Detail (art/DETAIL_RULES.md): the toad's anatomy is the frozen base's (five body lumps, brow ridges, slit pupils, a
mouth line, two-part legs with toes); on top: parotoid glands in three sizes (the two big ones, the flank row, the small
warts), the green spine seam, two slime strands from the mouth corners.
Real proportion: a cane toad's parotoid glands are about as long as its eye is wide, set right behind it.
"""
from __future__ import annotations

import math

from mathutils import Vector

import toad as T

NAME = "mire_toad"
WALK_FRAMES = 8
PALETTE = "mire_toad"
HEIGHT_SHEAR = T.HEIGHT_SHEAR
LEAN = T.LEAN
REFERENCE = "look_222.png"   # Tibia's Toad (comparison only, never shipped)
SIZE = 2.35                  # a Floor-2 toad: bigger than the pond's
GROUND_STRETCH = 0.92             # the hop makes the north view tall: shorter than the base (1.1)
AUTO_PLACE = (1, 1)
SIGNATURE = ["gland", "stripe"]
HEAD_PARTS = ["head", "eye", "pupil", "line"]
LEG_PARTS = ["leg", "foot"]
CHECK = {"size": (0.85, 1.35)}   # bigger than Tibia's toad on purpose (a dungeon toad)

PARTS = T.PARTS + ["gland", "slime"]
PIXEL_RULES = {**T.PIXEL_RULES,
               "weight": {**T.PIXEL_RULES["weight"], "gland": 2.6, "slime": 3.0, "stripe": 2.0},
               "thin": {**T.PIXEL_RULES["thin"], "gland": 2, "slime": 2},
               "soft": [["body", "belly", "blotch", "wart", "stripe", "head", "line", "gland"], ["eye", "pupil"],
                        ["leg", "foot"]],
               "no_outline": ["slime"],
               "texture": {**T.PIXEL_RULES["texture"], "gland": [0.4, 0.0]},
               "selout": ["body", "head"]}

FLANK = [(-0.110, 0.110), (-0.045, 0.124), (0.020, 0.116)]   # (x, |y|) of the flank glands


def build(model_cls, facing):
    saved, T.PARTS = T.PARTS, PARTS    # the base builds its model with its module's part list: lend it ours
    try:
        m = T.build(model_cls, facing)
    finally:
        T.PARTS = saved
    for k in ("l", "r"):
        m.ellipsoid(f"parotoid_{k}", "gland", radii=(0.030, 0.024, 0.018), segments=12, rings=6)
        for i in range(len(FLANK)):
            m.ellipsoid(f"fgland{i}_{k}", "gland", radii=(0.016, 0.014, 0.011), segments=8, rings=6)
        m.tube(f"drip_{k}", "slime", points=4)
    return m


def pose(m, t):
    T.pose(m, t)
    body = m.objects["body"].location
    head = m.objects["head"].location
    rot = m.objects["body"].rotation_euler
    # the base's spine stripe becomes a thicker toxic seam
    m.objects["stripe"].scale = (0.130, 0.012, 0.012)
    for s, k in ((1, "l"), (-1, "r")):
        v = Vector((0.090, 0.088 * s, 0.070))           # right behind the eye, on the head's back corner
        v.rotate(rot)
        pg = m.objects[f"parotoid_{k}"]
        pg.location = body + v
        pg.rotation_mode = "XYZ"
        pg.rotation_euler = (rot.x, rot.y, rot.z - 0.35 * s)
        for i, (x, y) in enumerate(FLANK):
            z = 0.090 * math.sqrt(max(0.05, 1 - (x / 0.170) ** 2 - (y / 0.172) ** 2)) + 0.004
            v = Vector((x, y * s, z))
            v.rotate(rot)
            m.objects[f"fgland{i}_{k}"].location = body + v
        # slime strands hanging from the mouth corners, swinging a little
        corner = head + Vector((0.040, 0.118 * s, -0.020))
        sw = 0.010 * math.sin(2 * math.pi * (t or 0.0) * 2 + s) if t is not None else 0.0
        pts = [corner, corner + Vector((0.006 + sw, 0.004 * s, -0.030)), corner + Vector((0.010 + sw, 0.006 * s, -0.055)),
               corner + Vector((0.012 + sw * 1.4, 0.006 * s, -0.070))]
        pts = [Vector((q.x, q.y, max(q.z, 0.008))) for q in pts]
        m.set_tube(f"drip_{k}", [tuple(q) for q in pts], [0.008, 0.006, 0.006, 0.009])


def assign_depth_parts(m, depth_of):
    return None
