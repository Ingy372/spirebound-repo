"""Field shardling (Floor 1, Shard Fields): model + float cycle.

ART_REQUESTS.md: "a small creature made of floating pale-blue crystal shards around a glowing core".
Original design: a bright white-cyan core, six pale-blue crystal shards circling it at two heights, each
turning as it goes; the whole thing bobs as it floats. Its "walk" is one full turn of the shards.
Low creature: "tilt" projection like the rat. Faces +X; sizes in tiles.
"""
from __future__ import annotations

import math

from mathutils import Euler, Vector

NAME = "shardling"
WALK_FRAMES = 8
PALETTE = "shardling"
HEIGHT_SHEAR = 0.0
LEAN = 0.0
REFERENCE = "look_294.png"   # Tibia's Wisp, the closest look-alike (comparison only, never shipped)
SIZE = 1.5
GROUND_STRETCH = 1.4       # longer north/south view, like Tibia's creatures
CANVAS_OFFSET = (3, 5)       # placed like its Tibia look-alike: filling the tile, spilling up-left
PIXEL_RULES = {
    "weight": {"core": 4.0, "glow": 1.0, "shard": 1.8},
    "thin": {"core": 3, "shard": 3},
    "soft": [["core", "glow"]],
    "no_outline": [],
    "fur": [],
    "texture": {"shard": [0.6, 0.0]},
    "bands": [0.34, 0.45, 0.55, 0.64, 0.73, 0.82, 0.90],
    "selout": ["shard"],
}

PARTS = ["none", "core", "glow", "shard"]

FLOAT_Z = 0.17
SHARDS = [(0.0, 0.11, 0.05, 0.12), (1.05, 0.12, -0.03, 0.10), (2.1, 0.11, 0.06, 0.13),
          (3.15, 0.12, -0.04, 0.11), (4.2, 0.11, 0.05, 0.12), (5.25, 0.12, -0.03, 0.10)]


SCALE = 1.5


def build(model_cls, facing):
    import bpy
    body = bpy.data.objects.new("ShardScale", None)
    body.parent = facing
    body.scale = (SCALE, SCALE, SCALE)
    bpy.context.scene.collection.objects.link(body)
    m = model_cls(body, PARTS)
    m.ellipsoid("core", "core", radii=(0.034, 0.034, 0.034), segments=12, rings=8)
    m.ellipsoid("glow", "glow", radii=(0.062, 0.062, 0.062), segments=14, rings=8)
    for i in range(len(SHARDS)):
        m.cone(f"shard{i}", "shard", segments=5)
        m.cone(f"shardb{i}", "shard", segments=5)
    return m


def pose(m, t):
    a = 0.0 if t is None else 2 * math.pi * t
    moving = t is not None
    centre = Vector((0.0, 0.0, FLOAT_Z + (0.020 * math.sin(a) if moving else 0.0)))
    m.objects["core"].location = centre
    pulse = 1.0 + (0.12 * math.sin(2 * a) if moving else 0.0)
    m.objects["glow"].location = centre
    m.objects["glow"].scale = (0.062 * pulse, 0.062 * pulse, 0.062 * pulse)
    spin = a / 2.0                                          # the shards turn slowly round the core
    for i, (ph, r, z, length) in enumerate(SHARDS):
        ang = ph + spin
        mid = centre + Vector((r * math.cos(ang), r * math.sin(ang), z + 0.012 * math.sin(a * 2 + ph)))
        axis = Vector((0.25 * math.cos(ang + 1.2), 0.25 * math.sin(ang + 1.2), 1.0)).normalized()
        # each shard is a double point: two cones base to base
        m.put_segment(f"shard{i}", mid, mid + axis * length * 0.95, 0.022)
        m.put_segment(f"shardb{i}", mid, mid - axis * length * 0.45, 0.022)


def assign_depth_parts(m, depth_of):
    return None
