"""Prism Shardling (Floor 1, Shard Fields elite): the Field Shardling (shardling.py) grown into a prism. Until now it
wore the Field Shardling's sprite with a glow.

Identity (art/CRAWLER_RULES.md step 1):
  Coat:      every shard a different colour of the rainbow, each with a pale edge (the Field Shardling is all pale
             blue; Tibia's wisp is a pale cloud).
  Signature: six big prismatic shards (red, amber, gold, green, blue, violet) circling a white-hot core, and a
             second, faster ring of small white chips turning the other way.
  Attitude:  bigger and busier than the field kind: the big shards stand upright like a crown and spin as it floats.

Detail (art/DETAIL_RULES.md): a core, a soft glow, double-pointed shards (two cones base to base), a ring of chips.
"""
from __future__ import annotations

import math

from mathutils import Vector

NAME = "prism_shardling"
WALK_FRAMES = 8
PALETTE = "prism_shardling"
HEIGHT_SHEAR = 0.0
LEAN = 0.0
REFERENCE = "look_294.png"   # Tibia's Wisp (comparison only, never shipped)
SIZE = 1.5
GROUND_STRETCH = 1.4
AUTO_PLACE = (1, 1)
LEG_PARTS = []               # it floats: no legs
HEAD_PARTS = ["core", "glow"]  # the core is its face
SIGNATURE = ["red", "blue"]
HUES = ["red", "amber", "gold", "green", "blue", "violet"]
PIXEL_RULES = {
    "weight": {"core": 4.0, "glow": 1.0, "chip": 3.0, **{h: 1.8 for h in HUES}},
    "thin": {"core": 3, "chip": 2, **{h: 3 for h in HUES}},
    "soft": [["core", "glow"]],
    "no_outline": [],
    "fur": [],
    "texture": {h: [0.5, 0.0] for h in HUES},
    "bands": [0.34, 0.45, 0.55, 0.64, 0.73, 0.82, 0.90],
    "selout": HUES,
}

PARTS = ["none", "core", "glow", "chip"] + HUES

FLOAT_Z = 0.19
SHARDS = [(0.0, 0.13, 0.05, 0.15), (1.05, 0.14, -0.02, 0.13), (2.1, 0.13, 0.06, 0.16),
          (3.15, 0.14, -0.03, 0.14), (4.2, 0.13, 0.05, 0.15), (5.25, 0.14, -0.02, 0.13)]
CHIPS = 8
SCALE = 2.2


def build(model_cls, facing):
    import bpy
    body = bpy.data.objects.new("ShardScale", None)
    body.parent = facing
    body.scale = (SCALE, SCALE, SCALE)
    bpy.context.scene.collection.objects.link(body)
    m = model_cls(body, PARTS)
    m.ellipsoid("core", "core", radii=(0.030, 0.030, 0.030), segments=12, rings=8)
    m.ellipsoid("glow", "glow", radii=(0.052, 0.052, 0.052), segments=14, rings=8)
    for i, hue in enumerate(HUES):
        m.cone(f"shard{i}", hue, segments=5)
        m.cone(f"shardb{i}", hue, segments=5)
    for i in range(CHIPS):
        m.cone(f"chip{i}", "chip", segments=4)
    return m


def pose(m, t):
    a = 0.0 if t is None else 2 * math.pi * t
    moving = t is not None
    centre = Vector((0.0, 0.0, FLOAT_Z + (0.020 * math.sin(a) if moving else 0.0)))
    m.objects["core"].location = centre
    pulse = 1.0 + (0.12 * math.sin(2 * a) if moving else 0.0)
    m.objects["glow"].location = centre
    m.objects["glow"].scale = (0.052 * pulse, 0.052 * pulse, 0.052 * pulse)
    spin = a / 2.0
    for i, (ph, r, z, length) in enumerate(SHARDS):
        ang = ph + spin
        mid = centre + Vector((r * math.cos(ang), r * math.sin(ang), z + 0.012 * math.sin(a * 2 + ph)))
        axis = Vector((0.20 * math.cos(ang + 1.2), 0.20 * math.sin(ang + 1.2), 1.0)).normalized()
        m.put_segment(f"shard{i}", mid, mid + axis * length * 0.95, 0.026)
        m.put_segment(f"shardb{i}", mid, mid - axis * length * 0.45, 0.026)
    # the small white chips: a tight, faster ring turning the other way
    for i in range(CHIPS):
        ang = 2 * math.pi * i / CHIPS - a
        mid = centre + Vector((0.075 * math.cos(ang), 0.075 * math.sin(ang), -0.050 + 0.010 * math.sin(a * 3 + i)))
        d = Vector((math.cos(ang + 1.6), math.sin(ang + 1.6), 0.4)).normalized()
        m.put_segment(f"chip{i}", mid - d * 0.016, mid + d * 0.022, 0.010)


def assign_depth_parts(m, depth_of):
    return None
