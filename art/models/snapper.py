"""Reed snapper (Floor 1, Reedmarsh): model + walk cycle.

ART_REQUESTS.md: "a big green-brown snapping turtle-crab with a reed-covered shell and a hooked beak".
Jay, 2026-11-15: it "looks like a mix between a crab and a turtle". So it is now ONE animal: a heavy snapping
turtle. The crab pincers are gone; the "crab" in the name lives on only in its wide, low, sideways scuttle.

Identity (art/CRAWLER_RULES.md step 1):
  Coat:      a dark bog-green shell cut into plates (Tibia's thornback tortoise is tan-brown; the meadow grass
             is yellow-green), a pale khaki rim, slate-blue leathery skin.
  Signature: three rows of pale horn knobs down the shell with reeds growing between them, and a big ivory
             hooked beak.
  Attitude:  low, wide and armoured: head thrust out on a thick neck, beak open a crack, ready to snap.

Detail (art/DETAIL_RULES.md): plate seams drawn on the shell, a separate rim, knobs, a two-part beak, thick legs
with three pale claws each, a ridged tail.
"""
from __future__ import annotations

import math

from mathutils import Vector

NAME = "snapper"
WALK_FRAMES = 8
PALETTE = "snapper"
HEIGHT_SHEAR = 0.30
LEAN = 10.0
REFERENCE = "look_198.png"   # Tibia's Thornback Tortoise (comparison only, never shipped)
SIZE = 2.1
GROUND_STRETCH = 1.0
AUTO_PLACE = (1, 1)
SIGNATURE = ["knob", "beak"]
HEAD_PARTS = ["head", "beak", "eye"]
LEG_PARTS = ["leg", "claw"]
PIXEL_RULES = {
    "weight": {"eye": 9.0, "beak": 3.0, "reed": 2.6, "claw": 3.0, "leg": 1.6, "rim": 1.3, "seam": 2.2, "knob": 3.0},
    "thin": {"eye": 2, "beak": 3, "reed": 2, "claw": 2, "leg": 4, "seam": 2, "knob": 2},
    "soft": [["shell", "rim", "seam", "knob"], ["head", "beak", "eye"], ["claw", "leg"]],
    "no_outline": [],
    "fur": [],
    "texture": {"shell": [0.9, 0.4], "rim": [0.6, 0.0], "head": [0.7, 0.3], "leg": [0.7, 0.3], "reed": [0.5, 0.0]},
    "bands": [0.40, 0.52, 0.62, 0.71, 0.79, 0.86, 0.93],
    "selout": ["shell", "head", "rim"],
}

PARTS = ["none", "shell", "rim", "reed", "head", "beak", "eye", "claw", "leg", "seam", "knob"]

SHELL = Vector((-0.020, 0.0, 0.120)); SHELL_R = (0.205, 0.178, 0.105)
STRIDE, LIFT = 0.055, 0.035
RING_N = 13
RADIALS = 6
KNOBS = [(x, y) for y in (0.0, 0.092, -0.092) for x in (0.085, -0.010, -0.105)]
REEDS = [(-0.055, 0.045, 0.17, 0.30), (0.035, -0.048, 0.15, -0.25), (-0.060, -0.045, 0.14, -0.45), (0.040, 0.045, 0.13, 0.35)]
TAIL_N = 6


def on_shell(x, y, lift=0.004):
    k = max(0.02, 1 - (x / SHELL_R[0]) ** 2 - (y / SHELL_R[1]) ** 2)
    return Vector((x, y, SHELL_R[2] * math.sqrt(k) + lift))


def build(model_cls, facing):
    m = model_cls(facing, PARTS)
    m.ellipsoid("shell", "shell", radii=SHELL_R, segments=24, rings=12)
    m.ellipsoid("rim", "rim", radii=(SHELL_R[0] * 1.07, SHELL_R[1] * 1.09, 0.032), segments=24, rings=8)
    m.tube("ring", "seam", points=RING_N)
    for i in range(RADIALS):
        m.tube(f"radial{i}", "seam", points=3)
    m.tube("spine", "seam", points=4)
    for i in range(len(KNOBS)):
        m.cone(f"knob{i}", "knob", segments=6)
    for i in range(len(REEDS)):
        m.cone(f"reed{i}", "reed", segments=6)
    m.capsule("neck", "head", segments=10)
    m.ellipsoid("head", "head", radii=(0.088, 0.078, 0.066), segments=16, rings=10)
    m.cone("beak", "beak", segments=10)
    m.cone("hook", "beak", segments=8)
    m.ellipsoid("jaw", "beak", radii=(0.050, 0.046, 0.018), segments=10, rings=6)
    for k in ("l", "r"):
        m.ellipsoid(f"brow_{k}", "head", radii=(0.030, 0.018, 0.016), segments=8, rings=6)
        m.ellipsoid(f"eye_{k}", "eye", radii=(0.014, 0.012, 0.014), segments=8, rings=6)
        for j in ("f", "h"):
            m.capsule(f"leg{j}_{k}", "leg", segments=8)
            m.ellipsoid(f"foot{j}_{k}", "leg", radii=(0.052, 0.046, 0.024), segments=10, rings=6)
            for c in range(3):
                m.cone(f"claw{j}{c}_{k}", "claw", segments=5)
    m.tube("tail", "leg", points=TAIL_N)
    for i in range(3):
        m.cone(f"tailspike{i}", "knob", segments=5)
    return m


def pose(m, t):
    a = 0.0 if t is None else 2 * math.pi * t
    walking = t is not None
    bob = 0.008 * abs(math.sin(2 * a)) if walking else 0.0
    rock = 0.05 * math.sin(2 * a) if walking else 0.0      # a heavy side-to-side waddle
    shell = SHELL + Vector((0, 0, bob))

    def top(x, y, lift=0.004):
        p = on_shell(x, y, lift)
        return shell + Vector((p.x, p.y, p.z + rock * y * 0.6))

    for name in ("shell", "rim"):
        ob = m.objects[name]
        ob.rotation_mode = "XYZ"
        ob.rotation_euler = (rock, 0, 0)
    m.objects["shell"].location = shell
    m.objects["rim"].location = shell + Vector((0, 0, -0.050))
    # plate seams: a ring round the top plates, lines running down to the rim, and a line down the spine
    ring = [top(0.115 * math.cos(2 * math.pi * i / (RING_N - 1)), 0.098 * math.sin(2 * math.pi * i / (RING_N - 1)))
            for i in range(RING_N)]
    m.set_tube("ring", [tuple(p) for p in ring], [0.0065] * RING_N)
    for i in range(RADIALS):
        th = 2 * math.pi * (i + 0.5) / RADIALS
        pts = [top(f * SHELL_R[0] * math.cos(th), f * SHELL_R[1] * math.sin(th)) for f in (0.56, 0.78, 0.97)]
        m.set_tube(f"radial{i}", [tuple(p) for p in pts], [0.0065] * 3)
    m.set_tube("spine", [tuple(top(x, 0)) for x in (-0.112, -0.040, 0.040, 0.112)], [0.006] * 4)
    for i, (x, y) in enumerate(KNOBS):
        base = top(x, y, -0.006)
        big = 1.0 if y == 0 else 0.8
        m.put_segment(f"knob{i}", base, base + Vector((-0.022, y * 0.25, 0.062 * big)), 0.030 * big)
    for i, (x, y, h, lean) in enumerate(REEDS):
        base = top(x, y, -0.004)
        sway = 0.02 * math.sin(a + i) if walking else 0.0
        m.put_segment(f"reed{i}", base, base + Vector((0.030 * lean + sway, 0.050 * lean, h)), 0.015)
    # head on a thick neck, thrust forward and low; a hooked upper beak over a small lower jaw
    nod = 0.008 * math.sin(2 * a) if walking else 0.0
    head = shell + Vector((0.285, 0, -0.010 + nod))
    m.put_segment("neck", shell + Vector((0.150, 0, -0.035)), head, 0.058)
    m.objects["head"].location = head
    m.put_segment("beak", head + Vector((0.030, 0, 0.004)), head + Vector((0.138, 0, -0.022)), 0.060, 0.050)
    m.put_segment("hook", head + Vector((0.112, 0, -0.010)), head + Vector((0.136, 0, -0.078)), 0.022)
    m.objects["jaw"].location = head + Vector((0.060, 0, -0.050))
    for s, k in ((1, "l"), (-1, "r")):
        m.objects[f"eye_{k}"].location = head + Vector((0.040, 0.066 * s, 0.030))
        m.objects[f"brow_{k}"].location = head + Vector((0.030, 0.060 * s, 0.048))
    # four thick legs reaching out past the rim, three pale claws on each foot
    for s, k, phase in ((1, "l", 0.0), (-1, "r", 0.5)):
        for j, hx, ph2 in (("f", 0.130, 0.0), ("h", -0.150, 0.5)):
            u = (t + phase + ph2) % 1.0 if walking else 0.25
            fx = STRIDE * math.cos(2 * math.pi * u) if walking else 0.0
            fz = LIFT * max(0.0, math.sin(2 * math.pi * u)) if walking else 0.0
            hip = shell + Vector((hx * 0.85, 0.120 * s, -0.060))
            foot = Vector((shell.x + hx * 1.15 + fx, 0.192 * s, 0.022 + fz))
            m.put_segment(f"leg{j}_{k}", hip, foot, 0.052)
            m.objects[f"foot{j}_{k}"].location = foot
            fwd = 1 if j == "f" else -0.4
            for c in range(3):
                fan = (c - 1) * 0.55
                d = Vector((fwd * math.cos(fan) + 0.2, s * (0.75 + 0.35 * math.sin(fan + 0.6)), -0.10)).normalized()
                m.put_segment(f"claw{j}{c}_{k}", foot + d * 0.036, foot + d * 0.074, 0.014)
    # a short ridged tail swinging behind
    base = shell + Vector((-SHELL_R[0] * 0.95, 0, -0.050))
    pts, radii = [], []
    for i in range(TAIL_N):
        u = i / (TAIL_N - 1)
        swing = 0.050 * math.sin(a + u * 2.0) * u if walking else 0.020 * u
        pts.append(base + Vector((-0.170 * u, swing, -0.045 * u)))
        radii.append(0.036 * (1 - 0.75 * u))
    m.set_tube("tail", [tuple(p) for p in pts], radii)
    for i in range(3):
        p = pts[1 + i]
        m.put_segment(f"tailspike{i}", p, p + Vector((-0.015, 0, 0.050 - 0.010 * i)), 0.016)


def assign_depth_parts(m, depth_of):
    return None
