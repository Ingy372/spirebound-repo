"""Blackthorn (Floor 1, Thornsnap Hollow elite): the Thornsnap (thornsnap.py) gone black and poisonous. Until now it
wore the Thornsnap's sprite with a glow.

Identity (art/CRAWLER_RULES.md step 1):
  Coat:      an ink-black vine and leaves with a violet sheen (Tibia's carniphila is grass green; our Thornsnap is
             blue-green with crimson jaws; the Briar Mother is wine-purple with rose blooms).
  Signature: a crown of long blood-dark thorns standing up behind the head, black barbs along the vine, and a throat that
             glows poison-green between dark wine jaws rimmed in green.
  Attitude:  the Thornsnap's lunging snake, reared higher: the crown flares as it snaps.

Detail (art/DETAIL_RULES.md): the Thornsnap's anatomy (S-curved vine, two flytrap jaws, thorn teeth, leaves with
midribs, sepal collar, jaw lips); big marks: the crown; medium: green lips and leaf ribs; small: the barbs.
"""
from __future__ import annotations

import math

from mathutils import Vector

import thornsnap as T

NAME = "blackthorn"
WALK_FRAMES = 8
PALETTE = "blackthorn"
HEIGHT_SHEAR = 0.30
LEAN = 10.0
REFERENCE = "look_120.png"   # Tibia's Carniphila (comparison only, never shipped)
SIZE = 2.2
GROUND_STRETCH = 0.7
AUTO_PLACE = (1, 1)
SIGNATURE = ["crown", "mouth"]
HEAD_PARTS = ["jaw", "mouth", "thorn", "crown"]
LEG_PARTS = []
PIXEL_RULES = {
    **T.PIXEL_RULES,
    "weight": {**T.PIXEL_RULES["weight"], "crown": 3.0, "barb": 3.0, "mouth": 4.0},
    "thin": {**T.PIXEL_RULES["thin"], "crown": 2, "barb": 2},
    "soft": T.PIXEL_RULES["soft"] + [["crown", "barb"]],
}

PARTS = T.PARTS + ["crown", "barb"]
CROWN = 7
BARBS = 5


def build(model_cls, facing):
    base_parts = T.PARTS
    T.PARTS = PARTS                       # the base builder reads its module's PARTS
    try:
        m = T.build(model_cls, facing)
    finally:
        T.PARTS = base_parts
    for i in range(CROWN):
        m.cone(f"crown{i}", "crown", segments=5)
    for i in range(BARBS):
        m.cone(f"barb{i}", "barb", segments=5)
    return m


def pose(m, t):
    T.pose(m, t)
    a = 0.0 if t is None else 2 * math.pi * t
    moving = t is not None
    head = m.objects["mouth"].location - Vector((0.050, 0, -0.010))
    open_ = 0.40 + 0.40 * max(0.0, math.sin(2 * a)) if moving else 0.70
    # the crown: long black thorns fanning up and back from behind the head, flaring as the jaws open
    for i in range(CROWN):
        th = math.pi * (0.10 + 0.80 * i / (CROWN - 1))          # an arc over the top, side to side
        root = head + Vector((-0.050, 0.050 * math.cos(th), 0.045 * math.sin(th)))
        tall = (0.190 if i % 2 == 0 else 0.140) * (0.9 + 0.2 * open_)
        tip = root + Vector((-0.060, 0.070 * math.cos(th), tall * math.sin(th) + 0.020))
        m.put_segment(f"crown{i}", root, tip, 0.024, 0.004)
    # black barbs along the vine's back, re-using the base's curve
    for i in range(BARBS):
        u = 0.15 + 0.65 * i / (BARBS - 1)
        x = -0.22 + 0.32 * u
        wave = 0.060 * math.sin(2.2 * math.pi * u - a) * (1 - u * 0.6) if moving else 0.035 * math.sin(2.2 * math.pi * u)
        z = 0.025 + 0.11 * max(0.0, u - 0.60) / 0.40
        p = Vector((x, wave, z + 0.040 + 0.018 * u))
        side = 0.030 * (1 if i % 2 else -1)
        m.put_segment(f"barb{i}", p - Vector((0, 0, 0.010)), p + Vector((-0.030, side, 0.070)), 0.018, 0.003)


def assign_depth_parts(m, depth_of):
    return None
