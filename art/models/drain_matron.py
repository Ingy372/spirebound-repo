"""The Drain Matron (the Underkeep, Wing 2 boss; tuned to Floor 2): the Mire Toads' monstrous mother in the drowned
drains. Built on the approved Hopper Toad (toad.py, frozen) like the Mire Toad and the Sluice Warden, so the family
reads at a glance; she is the biggest and the most bloated.

Identity (art/CRAWLER_RULES.md step 1):
  Coat:      deep plum-bruise skin mottled with ochre (Tibia's toad is orange-gold; her brood is slate-violet; the Sluice
             Warden drowned teal), a sallow belly.
  Signature: a back pitted with a honeycomb of egg pockets, each holding a pale luminous-green egg (like a Surinam toad;
             seen from every direction from above), and a swollen yellow throat sac.
  Attitude:  a bloated queen: too heavy to hop far, she heaves forward, jowls drooping, poison-green eyes half-lidded.

Detail (art/DETAIL_RULES.md): the toad's anatomy is the frozen base's (five body lumps, brow ridges, slit pupils, a
mouth line, two-part legs with toes); on top: the egg pockets (dark rims) with eggs in two sizes, the throat sac, the
jowls, ochre mottling and warts.
Real proportion: a Surinam toad's eggs sit flush in the skin of the back, packed edge to edge over its middle.
"""
from __future__ import annotations

import math

from mathutils import Vector

import toad as T

NAME = "drain_matron"
WALK_FRAMES = 8
PALETTE = "drain_matron"
HEIGHT_SHEAR = T.HEIGHT_SHEAR
LEAN = T.LEAN
REFERENCE = "look_222.png"   # Tibia's Toad (comparison only, never shipped)
SIZE = 2.75
GROUND_STRETCH = 0.80
AUTO_PLACE = (1, 1)
SIGNATURE = ["egg", "pocket"]
HEAD_PARTS = ["head", "eye", "pupil", "line", "sac"]
LEG_PARTS = ["leg", "foot"]
CHECK = {"size": (1.05, 1.70)}   # the wing boss: the biggest of the toad family

PARTS = T.PARTS + ["egg", "pocket", "sac"]
PIXEL_RULES = {**T.PIXEL_RULES,
               "weight": {**T.PIXEL_RULES["weight"], "egg": 3.6, "pocket": 2.4, "sac": 1.6},
               "thin": {**T.PIXEL_RULES["thin"], "egg": 2, "pocket": 2},
               "soft": [["body", "belly", "blotch", "wart", "stripe", "head", "line", "sac"], ["eye", "pupil"],
                        ["leg", "foot"], ["pocket", "egg"]],
               "texture": {**T.PIXEL_RULES["texture"], "egg": [0.3, 0.0], "sac": [0.4, 0.1]},
               "selout": ["body", "head"]}

# egg pockets packed over the back: (x, y) in rows, big in the middle, smaller toward the edge
EGGS = [(-0.090, 0.0), (-0.030, 0.0), (0.030, 0.0), (-0.120, 0.055), (-0.060, 0.058), (0.000, 0.058), (0.055, 0.050),
        (-0.120, -0.055), (-0.060, -0.058), (0.000, -0.058), (0.055, -0.050), (-0.080, 0.105), (-0.020, 0.108),
        (-0.080, -0.105), (-0.020, -0.108)]


def build(model_cls, facing):
    saved, T.PARTS = T.PARTS, PARTS    # the base builds its model with its module's part list: lend it ours
    try:
        m = T.build(model_cls, facing)
    finally:
        T.PARTS = saved
    for i in range(len(EGGS)):
        m.ellipsoid(f"pocket{i}", "pocket", radii=(0.024, 0.024, 0.010), segments=10, rings=4)
        m.ellipsoid(f"egg{i}", "egg", radii=(0.016, 0.016, 0.012), segments=8, rings=6)
    m.ellipsoid("sac", "sac", radii=(0.070, 0.100, 0.050), segments=14, rings=8)
    for k in ("l", "r"):
        m.ellipsoid(f"jowl_{k}", "body", radii=(0.040, 0.034, 0.034), segments=10, rings=6)
    return m


def pose(m, t):
    # far too heavy to hop: she rocks between the base hop's landing, settle and crouch and never takes off
    # (a smooth back-and-forth over 0.70 -> 1.08 of the base cycle; 1.08 is the moment before take-off)
    T.pose(m, None if t is None else (0.70 + 0.38 * (0.5 - 0.5 * math.cos(2 * math.pi * t))) % 1.0)
    # far too heavy to hop: the base's hop is flattened into a heave (90% of its height taken away)
    drop = 0.90 * max(0.0, m.objects["body"].location.z - 0.092)
    for ob in m.objects.values():
        if ob.type == "CURVE":          # tubes keep their points in place: their location is never reset, so set it
            ob.location.z = -drop
        else:
            ob.location.z -= drop
    body = m.objects["body"].location
    head = m.objects["head"].location
    rot = m.objects["body"].rotation_euler
    # the base's spine stripe is hidden under the eggs
    m.objects["stripe"].scale = (0.001, 0.001, 0.001)
    for i, (x, y) in enumerate(EGGS):
        z = 0.090 * math.sqrt(max(0.05, 1 - (x / 0.170) ** 2 - (y / 0.172) ** 2))
        big = 1.0 if abs(y) < 0.07 else 0.80
        v = Vector((x, y, z))
        v.rotate(rot)
        po = m.objects[f"pocket{i}"]
        po.location = body + v
        po.rotation_mode = "XYZ"
        po.rotation_euler = rot
        po.scale = (0.029 * big, 0.029 * big, 0.011)
        eg = m.objects[f"egg{i}"]
        eg.location = body + v + Vector((0, 0, 0.004))
        eg.scale = (0.018 * big, 0.018 * big, 0.012)
    pulse = 0.010 * math.sin(4 * math.pi * (t or 0.0)) if t is not None else 0.0      # the throat sac swells and sinks
    m.objects["sac"].location = head + Vector((0.040, 0, -0.048))
    m.objects["sac"].scale = (0.070 + pulse, 0.100 + pulse, 0.050 + pulse)
    for s, k in ((1, "l"), (-1, "r")):
        m.objects[f"jowl_{k}"].location = head + Vector((0.020, 0.110 * s, -0.030))


def assign_depth_parts(m, depth_of):
    return None
