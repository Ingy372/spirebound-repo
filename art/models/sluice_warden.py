"""Sluice Warden (the Underkeep, Wing 1 mini-boss, Q89): the keeper of the old sluices, in the den at the wing's heart.
"The water remembers!" Built on the approved Hopper Toad (toad.py, frozen), the Mire Toads' giant elder: a toad that
has sat in the sluice channel so long that the rusted gate has grown into its back.

Identity (art/CRAWLER_RULES.md step 1):
  Coat:      cold slate-teal drowned skin with dark blotches (no Tibia toad is blue; the Mire Toads are slate-violet),
             a pale bone-grey belly, river moss in the creases.
  Signature: a rusted iron sluice grate fused to its back: a rust-orange plate with dark bars and pale rivets (seen from
             every direction from above), and a heavy chain hanging from it down one flank.
  Attitude:  old, huge and immovable: low and wide, heavy brows over pale aqua eyes, slow ponderous hops.

Detail (art/DETAIL_RULES.md): the toad's anatomy is the frozen base's (five body lumps, brow ridges, slit pupils, a
mouth line, two-part legs with toes); on top: the grate plate with four bars and a cross bar (big), the chain and
moss patches (medium), rivets and warts (small).
Real proportion: a giant toad is still wider than tall; the grate covers the middle of the back like a saddle, about
half the body's length.
"""
from __future__ import annotations

import math

from mathutils import Euler, Vector

import toad as T

NAME = "sluice_warden"
WALK_FRAMES = 8
PALETTE = "sluice_warden"
HEIGHT_SHEAR = T.HEIGHT_SHEAR
LEAN = T.LEAN
REFERENCE = "look_222.png"   # Tibia's Toad (comparison only, never shipped)
SIZE = 2.42
GROUND_STRETCH = 0.72        # the hop makes the north view tall: shorter than the base (1.1)
AUTO_PLACE = (1, 1)
SIGNATURE = ["grate", "bar"]
HEAD_PARTS = ["head", "eye", "pupil", "line"]
LEG_PARTS = ["leg", "foot"]
CHECK = {"size": (0.95, 1.60)}   # a mini-boss: bigger than any toad (the canvas caps the take-off stretch)

PARTS = T.PARTS + ["grate", "bar", "rivet", "chain", "moss"]
PIXEL_RULES = {**T.PIXEL_RULES,
               "weight": {**T.PIXEL_RULES["weight"], "grate": 2.4, "bar": 3.0, "rivet": 4.0, "chain": 3.0, "moss": 1.6},
               "thin": {**T.PIXEL_RULES["thin"], "bar": 2, "rivet": 2, "chain": 2},
               "soft": [["body", "belly", "blotch", "wart", "stripe", "head", "line", "moss"], ["eye", "pupil"],
                        ["leg", "foot"], ["grate", "bar", "rivet"]],
               "texture": {**T.PIXEL_RULES["texture"], "grate": [0.8, 0.4], "moss": [1.0, 0.3]},
               "selout": ["body", "head", "grate"]}

BARS = [-0.060, -0.020, 0.020, 0.060]
RIVETS = [(0.068, 0.072), (0.068, -0.072), (-0.088, 0.072), (-0.088, -0.072)]
CHAIN = 6
MOSS = [(-0.120, 0.100), (0.050, -0.110), (-0.010, 0.125)]


def build(model_cls, facing):
    saved, T.PARTS = T.PARTS, PARTS    # the base builds its model with its module's part list: lend it ours
    try:
        m = T.build(model_cls, facing)
    finally:
        T.PARTS = saved
    m.box("plate", "grate", size=(1, 1, 1))
    for i in range(len(BARS)):
        m.capsule(f"bar{i}", "bar", segments=6)
    m.capsule("crossbar", "bar", segments=6)
    for i in range(len(RIVETS)):
        m.ellipsoid(f"rivet{i}", "rivet", radii=(0.011, 0.011, 0.009), segments=6, rings=4)
    for i in range(CHAIN):
        m.ellipsoid(f"link{i}", "chain", radii=(0.016, 0.010, 0.012), segments=8, rings=4)
    for i in range(len(MOSS)):
        m.ellipsoid(f"moss{i}", "moss", radii=(0.034, 0.024, 0.010), segments=8, rings=6)
    return m


def pose(m, t):
    T.pose(m, t)
    # a ponderous hop: the giant barely leaves the ground (the base's hop height, damped by 60%)
    drop = 0.60 * max(0.0, m.objects["body"].location.z - 0.092)
    for ob in m.objects.values():
        if ob.type == "CURVE":          # tubes keep their points in place: their location is never reset, so set it
            ob.location.z = -drop
        else:
            ob.location.z -= drop
    body = m.objects["body"].location
    rot = m.objects["body"].rotation_euler

    def on(v):
        v = Vector(v)
        v.rotate(rot)
        return body + v

    plate = m.objects["plate"]
    plate.location = on((-0.010, 0, 0.088))
    plate.rotation_mode = "XYZ"
    plate.rotation_euler = Euler((rot.x, rot.y - 0.10, rot.z))
    plate.scale = (0.180, 0.160, 0.020)
    for i, y in enumerate(BARS):
        m.put_segment(f"bar{i}", on((0.080, y, 0.104)), on((-0.100, y, 0.096)), 0.008)
    m.put_segment("crossbar", on((-0.010, 0.078, 0.104)), on((-0.010, -0.078, 0.104)), 0.009)
    for i, (x, y) in enumerate(RIVETS):
        m.objects[f"rivet{i}"].location = on((x, y, 0.104))
    # the chain hangs from the plate's corner down the right flank, swinging with the hop
    sw = 0.015 * math.sin(2 * math.pi * (t or 0.0)) if t is not None else 0.0
    start = on((-0.060, -0.085, 0.095))
    for i in range(CHAIN):
        u = i / (CHAIN - 1)
        p = start + Vector((0.020 * u + sw * u, -0.050 * u, -0.090 * u))
        p.z = max(p.z, 0.012)
        ob = m.objects[f"link{i}"]
        ob.location = p
        ob.rotation_mode = "XYZ"
        ob.rotation_euler = Euler((0.9 if i % 2 else 0.0, 0.3, 0))
    for i, (x, y) in enumerate(MOSS):
        z = 0.086 * math.sqrt(max(0.05, 1 - (x / 0.170) ** 2 - (y / 0.172) ** 2))
        m.objects[f"moss{i}"].location = on((x, y, z))


def assign_depth_parts(m, depth_of):
    return None
