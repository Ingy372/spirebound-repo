"""Thornsnap (Floor 1, Thornsnap Hollow): model + crawl cycle.

ART_REQUESTS.md: "a snapping plant with a thorny jaw-like flower head on a crawling vine body".
Original design: a thick green vine that slithers along the ground in an S-curve, a raised flower head made of
two jaw petals (green outside, red inside) that snap open and shut, pale thorns along the jaws and the vine,
two leaves near the head. Low creature: "tilt" projection like the rat. Faces +X; sizes in tiles.
"""
from __future__ import annotations

import math

from mathutils import Euler, Vector

NAME = "thornsnap"
WALK_FRAMES = 8
PALETTE = "thornsnap"
HEIGHT_SHEAR = 0.0
LEAN = 0.0
REFERENCE = "look_120.png"   # Tibia's Carniphila, the closest look-alike (comparison only, never shipped)
SIZE = 1.75
GROUND_STRETCH = 1.0       # longer north/south view, like Tibia's creatures
CANVAS_OFFSET = (-10, -3)       # placed like its Tibia look-alike: filling the tile, spilling up-left
PIXEL_RULES = {
    "weight": {"thorn": 3.0, "mouth": 3.0, "jaw": 1.6, "leaf": 1.2},
    "thin": {"thorn": 2, "mouth": 3, "leaf": 3},
    "soft": [["jaw", "mouth"]],
    "no_outline": [],
    "fur": [],
    "texture": {"vine": [0.9, 0.2], "jaw": [0.7, 0.1], "leaf": [0.6, 0.0]},
    "bands": [0.42, 0.55, 0.66, 0.75, 0.83, 0.90, 0.96],
    "selout": ["jaw", "vine", "leaf"],
}

PARTS = ["none", "vine", "jaw", "mouth", "thorn", "leaf"]
N = 10
LEAVES = {"l1": (0.95, 1, 0.3), "r1": (0.95, -1, 0.3), "l2": (0.55, 1, 0.5), "r2": (0.60, -1, 0.5),
          "l3": (0.20, 1, 0.6), "r3": (0.25, -1, 0.6)}


def build(model_cls, facing):
    m = model_cls(facing, PARTS)
    m.tube("vine", "vine", points=N)
    m.ellipsoid("jaw_top", "jaw", radii=(0.150, 0.130, 0.050), segments=14, rings=8)
    m.ellipsoid("jaw_bot", "jaw", radii=(0.140, 0.124, 0.046), segments=14, rings=8)
    m.ellipsoid("mouth", "mouth", radii=(0.118, 0.100, 0.040), segments=12, rings=6)
    for i in range(8):
        m.cone(f"thorn{i}", "thorn", segments=5)
    for k in LEAVES:
        m.ellipsoid(f"leaf_{k}", "leaf", radii=(0.110, 0.042, 0.012), segments=12, rings=6)
    return m


def pose(m, t):
    a = 0.0 if t is None else 2 * math.pi * t
    moving = t is not None
    # vine: S-curve that travels backwards along the body (slithering), rising to a neck under the head
    pts, radii = [], []
    for i in range(N):
        u = i / (N - 1)                                     # 0 = tail end, 1 = neck
        x = -0.22 + 0.32 * u
        wave = 0.060 * math.sin(2.2 * math.pi * u - a) * (1 - u * 0.6) if moving else 0.035 * math.sin(2.2 * math.pi * u)
        z = 0.025 + 0.16 * max(0.0, u - 0.60) / 0.40
        pts.append(Vector((x, wave, z)))
        radii.append(0.040 + 0.018 * u)
    m.set_tube("vine", [tuple(p) for p in pts], radii)
    neck = pts[-1]
    head = neck + Vector((0.080, 0, 0.050 + (0.012 * math.sin(a) if moving else 0.0)))
    open_ = 0.25 + 0.45 * max(0.0, math.sin(2 * a)) if moving else 0.70     # snaps twice per cycle
    for name, sign in (("jaw_top", 1), ("jaw_bot", -1)):
        j = m.objects[name]
        j.rotation_mode = "XYZ"
        j.rotation_euler = Euler((0, -sign * open_, 0))
        j.location = head + Vector((0.065, 0, sign * (0.026 + 0.060 * open_)))
    m.objects["mouth"].location = head + Vector((0.070, 0, 0.0))
    # thorns: three along each jaw edge, two on the vine's back
    k = 0
    for sign in (1, -1):
        for i, (dx, dy) in enumerate(((0.140, 0.085), (0.190, 0.0), (0.140, -0.085))):
            base = head + Vector((dx, dy, sign * (0.030 + 0.068 * open_)))
            tip = base + Vector((0.040, dy * 0.6, sign * 0.085))
            m.put_segment(f"thorn{k}", base, tip, 0.020)
            k += 1
    for i, u in enumerate((0.35, 0.65)):
        p = pts[int(u * (N - 1))]
        m.put_segment(f"thorn{k}", p + Vector((0, 0, 0.026)), p + Vector((-0.020, 0, 0.085)), 0.020)
        k += 1
    for kk, (u, s, tilt) in LEAVES.items():             # broad leaves along the vine, fanning out to both sides
        lf = m.objects[f"leaf_{kk}"]
        p = pts[int(u * (N - 1))]
        flap = 0.15 * math.sin(a + u * 4) if moving else 0.0
        lf.rotation_mode = "XYZ"
        lf.rotation_euler = Euler((tilt * s + flap, -0.25, (0.9 + 0.3 * u) * s))
        lf.location = p + Vector((-0.020, 0.075 * s, -0.005))


def assign_depth_parts(m, depth_of):
    return None
