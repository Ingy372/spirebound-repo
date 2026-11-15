"""Reed snapper (Floor 1, Reedmarsh): model + walk cycle.

ART_REQUESTS.md: "a big green-brown snapping turtle-crab with a reed-covered shell and a hooked beak".

Identity (art/CRAWLER_RULES.md step 1):
  Coat:      a dark bog-green shell (Tibia's thornback tortoise is tan-brown; the meadow grass is yellow-green),
             mossy on top, with a pale khaki rim.
  Signature: two big brick-red crab claws held forward, bright reeds sprouting from the shell, an ivory hooked beak.
  Attitude:  low and wide, claws raised, scuttling side to side.
Original design: a low domed shell with a rough rim, tufts of reeds growing from the top, a heavy head with a
pale hooked beak, two crab claws in front, four stubby legs scuttling side to side. Low creature: "tilt"
projection like the rat. Faces +X (east), +Y left, +Z up; sizes in tiles.
"""
from __future__ import annotations

import math

from mathutils import Euler, Vector

NAME = "snapper"
WALK_FRAMES = 8
PALETTE = "snapper"
HEIGHT_SHEAR = 0.30
LEAN = 10.0
REFERENCE = "look_198.png"   # Tibia's Thornback Tortoise, the closest look-alike (comparison only, never shipped)
SIZE = 2.25
GROUND_STRETCH = 1.1       # longer north/south view, like Tibia's creatures
AUTO_PLACE = (1, 1)
SIGNATURE = ["claw", "reed"]
HEAD_PARTS = ["head", "beak", "eye"]
LEG_PARTS = ["leg", "claw"]
PIXEL_RULES = {
    "weight": {"eye": 9.0, "beak": 3.0, "reed": 2.6, "claw": 2.0, "leg": 1.8, "rim": 1.3},
    "thin": {"eye": 3, "beak": 3, "reed": 2, "claw": 3, "leg": 3},
    "soft": [["shell", "rim"], ["head", "beak", "eye"], ["claw", "leg"]],
    "no_outline": [],
    "fur": ["shell"],
    "texture": {"shell": [1.2, 0.3], "rim": [0.8, 0.0], "head": [0.6, 0.0], "claw": [0.5, 0.0], "leg": [0.5, 0.0], "reed": [0.6, 0.0]},
    "bands": [0.42, 0.55, 0.66, 0.75, 0.83, 0.90, 0.96],
    "selout": ["shell", "head", "claw"],
}

PARTS = ["none", "shell", "rim", "reed", "head", "beak", "eye", "claw", "leg"]

OX = 0.02
SHELL = Vector((0.0, 0.0, 0.105)); SHELL_R = (0.200, 0.175, 0.105)
STRIDE, LIFT = 0.050, 0.035


def build(model_cls, facing):
    m = model_cls(facing, PARTS)
    m.ellipsoid("shell", "shell", radii=SHELL_R, segments=20, rings=10)
    m.ellipsoid("rim", "rim", radii=(SHELL_R[0] * 1.06, SHELL_R[1] * 1.08, 0.030), segments=20, rings=8)
    for i in range(5):
        m.cone(f"reed{i}", "reed", segments=6)
    m.ellipsoid("head", "head", radii=(0.085, 0.078, 0.070))
    m.cone("beak", "beak", segments=10)
    for k in ("l", "r"):
        m.ellipsoid(f"eye_{k}", "eye", radii=(0.013, 0.012, 0.014), segments=8, rings=6)
        m.capsule(f"arm_{k}", "claw", segments=8)
        m.ellipsoid(f"pincer_{k}", "claw", radii=(0.055, 0.032, 0.026), segments=12, rings=8)
        m.ellipsoid(f"finger_{k}", "claw", radii=(0.034, 0.016, 0.014), segments=8, rings=6)
        for j in range(2):
            m.capsule(f"leg{j}_{k}", "leg", segments=8)
    return m


REEDS = [(-0.060, 0.030, 0.20, 0.30), (0.010, -0.050, 0.17, -0.25), (-0.010, 0.070, 0.15, 0.55),
         (-0.100, -0.030, 0.14, -0.50), (0.050, 0.020, 0.13, 0.10)]


def pose(m, t):
    a = 0.0 if t is None else 2 * math.pi * t
    walking = t is not None
    bob = 0.010 * abs(math.sin(2 * a)) if walking else 0.0
    rock = 0.06 * math.sin(2 * a) if walking else 0.0      # a heavy side-to-side waddle
    o = Vector((OX, 0, 0))
    shell = SHELL + o + Vector((0, 0, bob))
    for name in ("shell", "rim"):
        ob = m.objects[name]
        ob.rotation_mode = "XYZ"
        ob.rotation_euler = Euler((rock, 0, 0))
    m.objects["shell"].location = shell
    m.objects["rim"].location = shell + Vector((0, 0, -0.045))
    for i, (x, y, h, lean) in enumerate(REEDS):
        base = shell + Vector((x, y, SHELL_R[2] * 0.85))
        sway = 0.02 * math.sin(a + i) if walking else 0.0
        tip = base + Vector((0.030 * lean + sway, 0.050 * lean, h))
        m.put_segment(f"reed{i}", base, tip, 0.016)
    head = shell + Vector((0.200, 0, 0.020 + (0.008 * math.sin(2 * a) if walking else 0.0)))
    m.objects["head"].location = head
    m.put_segment("beak", head + Vector((0.050, 0, -0.004)), head + Vector((0.135, 0, -0.060)), 0.040, 0.034)
    for s, k in ((1, "l"), (-1, "r")):
        m.objects[f"eye_{k}"].location = head + Vector((0.046, 0.052 * s, 0.034))
    for s, k, phase in ((1, "l", 0.0), (-1, "r", 0.5)):
        u = (t + phase) % 1.0 if walking else 0.25
        reach = 0.040 * math.sin(2 * math.pi * u) if walking else 0.0
        shoulder = shell + Vector((0.120, 0.150 * s, -0.070))
        pincer = shoulder + Vector((0.075 + reach, 0.080 * s, -0.020))
        m.put_segment(f"arm_{k}", shoulder, pincer, 0.022)
        pc = m.objects[f"pincer_{k}"]
        pc.location = pincer + Vector((0.030, 0, 0))
        open_ = 0.25 + 0.20 * math.sin(4 * math.pi * u) if walking else 0.3
        fg = m.objects[f"finger_{k}"]
        fg.rotation_mode = "XYZ"
        fg.rotation_euler = Euler((0, open_, 0))
        fg.location = pincer + Vector((0.060, 0, 0.022))
        for j in range(2):
            hip = shell + Vector((0.030 - 0.130 * j, 0.150 * s, -0.050))
            ph = (u + 0.5 * j) % 1.0
            fx = STRIDE * math.cos(2 * math.pi * ph) if walking else 0.0
            fz = LIFT * max(0.0, math.sin(2 * math.pi * ph)) if walking else 0.0
            foot = Vector((hip.x + fx, hip.y + 0.070 * s, 0.012 + fz))
            m.put_segment(f"leg{j}_{k}", hip, foot, 0.026)


def assign_depth_parts(m, depth_of):
    return None
