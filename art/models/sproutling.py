"""Sproutling (Floor 1, Sproutling Glade): model + walk cycle.

ART_REQUESTS.md: "a small walking plant creature, a bulb body with two leaf arms and a sprout on its head".
Original design: a round onion-like bulb body (pale green, darker at the bottom), two little dark eyes, two
leaf arms that flap as it walks, a curly sprout with two leaves on top, two stubby root feet. It stands up,
so it uses the "oblique" projection like people. Faces +X; sizes in tiles.
"""
from __future__ import annotations

import math

from mathutils import Euler, Vector

NAME = "sproutling"
WALK_FRAMES = 8
PALETTE = "sproutling"
REFERENCE = "rat_client.png"       # size reference only
PROJECTION = "oblique"
CANVAS_OFFSET = (6, 6)
PIXEL_RULES = {
    "weight": {"eye": 9.0, "leaf": 2.0, "sprout": 2.6, "root": 2.0},
    "thin": {"eye": 3, "leaf": 3, "sprout": 2, "root": 3},
    "soft": [["bulb", "base"], ["sprout", "leaf"]],
    "no_outline": [],
    "fur": [],
    "selout": ["bulb", "leaf"],
}

PARTS = ["none", "bulb", "base", "eye", "leaf", "sprout", "root"]


def build(model_cls, facing):
    m = model_cls(facing, PARTS)
    m.ellipsoid("bulb", "bulb", radii=(0.150, 0.160, 0.120), segments=20, rings=12)
    m.ellipsoid("base", "base", radii=(0.120, 0.130, 0.070), segments=18, rings=8)
    m.cone("tip", "bulb", segments=12)
    for k in ("l", "r"):
        m.ellipsoid(f"eye_{k}", "eye", radii=(0.016, 0.016, 0.024), segments=8, rings=6)
        m.ellipsoid(f"arm_{k}", "leaf", radii=(0.125, 0.034, 0.062), segments=12, rings=6)
        m.capsule(f"foot_{k}", "root", segments=8)
    m.tube("stem", "sprout", points=6)
    m.ellipsoid("sleaf_a", "leaf", radii=(0.085, 0.036, 0.016), segments=10, rings=6)
    m.ellipsoid("sleaf_b", "leaf", radii=(0.075, 0.032, 0.016), segments=10, rings=6)
    return m


def pose(m, t):
    a = 0.0 if t is None else 2 * math.pi * t
    walking = t is not None
    hop = 0.030 * abs(math.sin(a)) if walking else 0.0
    rock = 0.14 * math.sin(a) if walking else 0.0          # waddles side to side
    up = Vector((0, 0, 0.040 + hop))
    bulb = Vector((0, 0, 0.130)) + up
    for name, loc in (("bulb", bulb), ("base", bulb + Vector((0, 0, -0.080)))):
        ob = m.objects[name]
        ob.location = loc
        ob.rotation_mode = "XYZ"
        ob.rotation_euler = Euler((rock, 0, 0))
    m.put_segment("tip", bulb + Vector((0, 0, 0.095)), bulb + Vector((0, 0.020 * rock, 0.150)), 0.045)
    for s, k in ((1, "l"), (-1, "r")):
        m.objects[f"eye_{k}"].location = bulb + Vector((0.135, 0.055 * s, 0.045 + 0.012 * rock * s))
        flap = 0.6 * math.sin(a + (0 if s > 0 else math.pi)) if walking else 0.2
        arm = m.objects[f"arm_{k}"]
        arm.rotation_mode = "XYZ"
        arm.rotation_euler = Euler((0.5 * s + flap * 0.5 * s, 0.4 + flap * 0.3, 0.3 * s))
        arm.location = bulb + Vector((0.020, 0.205 * s, -0.010))
        ph = a + (0 if s > 0 else math.pi)
        fx = 0.045 * math.cos(ph) if walking else 0.0
        fz = 0.025 * max(0.0, math.sin(ph)) if walking else 0.0
        hip = bulb + Vector((0, 0.060 * s, -0.120))
        m.put_segment(f"foot_{k}", hip, Vector((fx + 0.020, 0.075 * s, 0.020 + fz)), 0.026)
    # the sprout: a curly stem from the top with two leaves, bobbing a little
    top = bulb + Vector((0, 0, 0.140))
    sway = 0.03 * math.sin(a + 0.8) if walking else 0.0
    pts = [top + Vector((sway * i / 5, 0.006 * i, 0.020 * i)) for i in range(6)]
    m.set_tube("stem", [tuple(p) for p in pts], [0.012] * 6)
    tipp = pts[-1]
    for name, side, ang in (("sleaf_a", 1, 0.5), ("sleaf_b", -1, -0.4)):
        lf = m.objects[name]
        lf.rotation_mode = "XYZ"
        lf.rotation_euler = Euler((0.6 * side, -0.3, 1.2 * side))
        lf.location = tipp + Vector((0.000, 0.045 * side, -0.010 + 0.010 * side))


def assign_depth_parts(m, depth_of):
    return None
