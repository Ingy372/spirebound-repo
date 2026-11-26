"""The last decay step of a flesh-and-blood corpse (art/CORPSE_RULES.md C5): a small pile of bones on the ground.

Shared by every flesh monster of normal size; corpse_bones_big.py is the same pile for 2x2 bosses. Old-ivory bone
(the Ruin Archer's bone ramp), seen from the same tilted camera as the animals.
A skull with dark sockets and a dropped jaw, a curved spine with a ribcage arching over it, two long leg bones with
knobbly ends crossed beside it, and a few loose ribs, so it reads as "remains" at 1x and is not a white blob.
"""
from __future__ import annotations

import math

NAME = "corpse_bones"
WALK_FRAMES = 1
PALETTE = "archer"
PROJECTION = "tilt"
SIZE = 1.0
GROUND_STRETCH = 1.0
AUTO_PLACE = (1, 1)
LEAN = 0.0
PARTS = ["none", "skin", "rib", "jaw", "tooth", "knob", "eye"]
PIXEL_RULES = {"weight": {"eye": 6.0, "tooth": 3.0, "knob": 2.0, "rib": 2.0}, "thin": {"rib": 2, "eye": 2, "knob": 3}}
RIBS = 4


def build(model_cls, facing):
    m = model_cls(facing, PARTS)
    m.ellipsoid("skull", "skin", segments=14, rings=10)
    m.ellipsoid("snout", "skin", segments=12, rings=8)
    m.capsule("jaw", "jaw", segments=8)
    for k in ("l", "r"):
        m.ellipsoid(f"socket_{k}", "eye", segments=8, rings=6)
    m.tube("spine", "knob", points=8)
    for i in range(RIBS):
        for k in ("l", "r"):
            m.tube(f"rib{i}{k}", "rib", points=6)
    for i in range(2):
        m.capsule(f"bone{i}", "skin", segments=8)
        for e in ("a", "b"):
            m.ellipsoid(f"knob{i}{e}", "knob", segments=8, rings=6)
    for i in range(2):
        m.tube(f"loose{i}", "rib", points=5)
    return m


def pose(m, t):
    o = m.objects
    s = 1.0
    # skull at the front right, lying on its side, jaw dropped open
    o["skull"].location = (0.20 * s, -0.04 * s, 0.055 * s)
    o["skull"].scale = (0.075 * s, 0.065 * s, 0.058 * s)
    o["snout"].location = (0.275 * s, -0.06 * s, 0.040 * s)
    o["snout"].scale = (0.050 * s, 0.040 * s, 0.034 * s)
    m.put_segment("jaw", (0.20 * s, -0.10 * s, 0.018 * s), (0.30 * s, -0.12 * s, 0.014 * s), 0.016 * s)
    for sign, k in ((1, "l"), (-1, "r")):
        o[f"socket_{k}"].location = (0.245 * s, (-0.04 + 0.030 * sign) * s, 0.085 * s)
        o[f"socket_{k}"].scale = (0.020 * s, 0.017 * s, 0.014 * s)
    # spine: a gentle curve from behind the skull to the back
    sp = [(0.13 - 0.06 * i, 0.012 * math.sin(i * 0.9), 0.028) for i in range(8)]
    m.set_tube("spine", [tuple(c * s for c in p) for p in sp], [0.016 * s] * 8)
    # ribcage: arcs over the spine, shorter toward the back
    for i in range(RIBS):
        x = 0.09 - 0.055 * i
        span = (0.085 - 0.012 * i)
        for sign, k in ((1, "l"), (-1, "r")):
            pts = []
            for j in range(6):
                u = j / 5
                a = u * math.pi * 0.55
                pts.append(((x - 0.012 * u) * s, sign * span * math.sin(a) * s, (0.030 + 0.075 * math.cos(a) * (1 - 0.35 * u) * (1 - 0.1 * i)) * s * (1 if sign > 0 else 0.7)))
            m.set_tube(f"rib{i}{k}", pts, [0.010 * s] * 6)
    # two long bones crossed in front of the ribs
    ends = [((-0.22, -0.16, 0.016), (0.04, -0.20, 0.016)), ((-0.18, -0.24, 0.016), (-0.02, -0.10, 0.020))]
    for i, (a, b) in enumerate(ends):
        a = tuple(c * s for c in a)
        b = tuple(c * s for c in b)
        m.put_segment(f"bone{i}", a, b, 0.014 * s)
        for e, p in (("a", a), ("b", b)):
            o[f"knob{i}{e}"].location = p
            o[f"knob{i}{e}"].scale = (0.024 * s, 0.022 * s, 0.018 * s)
    # loose ribs behind
    for i in range(2):
        x0, y0 = -0.10 - 0.08 * i, 0.15 + 0.02 * i
        pts = [((x0 + 0.03 * j) * s, (y0 - 0.02 * j * j) * s, 0.012 * s) for j in range(5)]
        m.set_tube(f"loose{i}", pts, [0.009 * s] * 5)


def assign_depth_parts(m, depth_of):
    pass
