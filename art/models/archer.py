"""Ruin Archer (Floor 1 monster, the Old Watchtower), built on art/models/humanoid.py (second draft, 2026-11-25).

ART_REQUESTS.md: "a skeletal archer in rotted leather with a bow".
The first draft (2026-11-15) had its own copied body; this one follows art/OUTFIT_RULES.md.

Identity (art/OUTFIT_RULES.md step 1):
  Silhouette: thin bone limbs (much thinner than a living figure), a skull with a hanging jaw, a torn leather jerkin
              open over the ribs, a short recurve bow held down at the left side, a quiver at the right hip.
  Colours:    old-ivory bone with brown-grey shadows, near-black eye sockets with a faint green glint, rotted dark
              leather; the bow dark wood.
  Details:    ribs showing between the jerkin's torn edges, a spine and back ribs below the short back of the
              jerkin (bone must show from behind too), cheekbones and big dark sockets (a smooth skull read as an egg), a dropped jaw with a tooth line, knobbly knees and
              elbows, a tattered hem, the quiver's arrows, the bowstring.
Look-alike: Tibia's Skeleton and Skeleton Warrior: ours wears rotted leather and carries a bow, with green-glinting
sockets.
Addons: none (a monster, rule A1).
"""
from __future__ import annotations

import math

from mathutils import Euler, Vector

import humanoid as H

NAME = "archer"
WALK_FRAMES = 8
PALETTE = "archer"
REFERENCE = "outfit_128.png"
PROJECTION = "oblique"
CANVAS_OFFSET = H.CANVAS_OFFSET
SIGNATURE = ["rib", "bow"]
HEAD_PARTS = ["skin", "hair", "strand", "eye", "brow", "nose", "jaw", "tooth"]
LEG_PARTS = ["leg_a", "leg_b", "boot_a", "boot_b", "knob"]
CHECK = {"size": (0.80, 1.45), "head": 0.08, "legs_side": 0.03, "eye": 1}   # thin bone legs show less than cloth ones

PARTS = H.PARTS + ["jerkin", "tatter", "rib", "jaw", "tooth", "knob", "bow", "string", "quiver", "shaft"]
PIXEL_RULES = H.pixel_rules(
    weight={"jerkin": 1.4, "tatter": 2.2, "rib": 3.0, "jaw": 1.8, "tooth": 4.0, "knob": 2.6, "bow": 3.0, "string": 3.0,
            "quiver": 1.8, "shaft": 3.0},
    thin={"tatter": 2, "rib": 2, "tooth": 2, "bow": 2, "string": 2, "shaft": 2},
    soft=[["skin", "jaw", "tooth"], ["torso", "rib"], ["jerkin", "tatter"], ["bow", "string"], ["quiver", "shaft"]],
    texture={"jerkin": [0.5, 0.25], "skin": [0.3, 0.1], "torso": [0.3, 0.1]},
    selout=["jerkin", "skin"],
)

# bone figure: thin limbs, a narrow chest; the "hair" cap is set inside the skull so the skull shows
SPEC = H.spec(torso_r=(0.080, 0.124, 0.176), arm_r=0.026, leg_r=0.028, boot_r=0.034, foot_r=(0.064, 0.036, 0.032),
              stride=0.13, lift=0.060, bob=0.020, arm_swing=0.14, eye_r=(0.024, 0.028, 0.030),
              cap=(-0.040, 0.000), cap_r=(0.090, 0.090, 0.090), strands=())


def build(model_cls, facing):
    m = H.build(model_cls, facing, SPEC, PARTS)
    m.ellipsoid("jaw", "jaw", radii=(0.060, 0.074, 0.030), segments=12, rings=6)
    m.tube("crack", "tatter", points=5)          # a dark crack across the crown: breaks up the smooth skull (DETAIL rule 4)
    m.capsule("teeth", "tooth")
    for i in range(3):
        m.capsule(f"rib{i}", "rib")
    for k in ("l", "r"):
        m.box(f"jerkin_{k}", "jerkin", size=(0.030, 0.070, 0.230))
        m.box(f"tatter_{k}", "tatter", size=(0.034, 0.074, 0.024))
        m.ellipsoid(f"knee_{k}", "knob", radii=(0.030, 0.030, 0.030), segments=8, rings=6)
        m.ellipsoid(f"elbow_{k}", "knob", radii=(0.024, 0.024, 0.024), segments=8, rings=6)
    m.box("jerkin_b", "jerkin", size=(0.030, 0.220, 0.120))      # short at the back: the spine shows below it
    m.tube("spine", "rib", points=5)
    for i in range(2):
        m.capsule(f"backrib{i}", "rib")
    for k in ("l", "r"):
        m.ellipsoid(f"cheek_{k}", "jaw", radii=(0.030, 0.024, 0.020), segments=8, rings=6)
    m.tube("bow", "bow", points=7)
    m.capsule("bowstring", "string")
    m.capsule("quiver", "quiver")
    for i in range(3):
        m.capsule(f"shaft{i}", "shaft")
    return m


def _bow_hand(sh, a, walking):
    swing = 0.06 * math.sin(a) if walking else 0.0
    return sh + Vector((0.030 + swing, 0.110, -0.290))   # out at the side, so the bow shows from behind too


def pose(m, t):
    p = H.pose(m, t, hands={"l": _bow_hand})
    up, head, a, walking = p["up"], p["head"], p["a"], p["walking"]
    s = m.spec
    jaw_drop = 0.012 * abs(math.sin(a)) if walking else 0.0      # the jaw rattles with the step
    m.objects["jaw"].location = head + Vector((0.050, 0, -0.092 - jaw_drop))
    cap = head + Vector((s["cap"][0], 0, s["cap"][1]))
    crack = [H.on_ellipsoid(head, s["head_r"], (0.5 - 0.25 * i, 0.30 - 0.18 * i + 0.06 * (i % 2), 0.85), 1.03) for i in range(5)]
    m.set_tube("crack", [tuple(q) for q in crack], [0.006] * 5)
    m.put_segment("teeth", head + Vector((0.104, -0.040, -0.074 - jaw_drop)), head + Vector((0.104, 0.040, -0.074 - jaw_drop)), 0.007)
    for i in range(3):
        z = 0.790 - 0.055 * i
        m.put_segment(f"rib{i}", Vector((0.072, -0.060, z)) + up, Vector((0.072, 0.060, z)) + up, 0.008)
    for sign, k in ((1, "l"), (-1, "r")):
        for name, z in ((f"jerkin_{k}", 0.700), (f"tatter_{k}", 0.580)):
            o = m.objects[name]
            o.rotation_mode = "XYZ"
            o.rotation_euler = Euler((0, 0, 0.30 * sign))           # hanging open at the front, ribs between
            o.location = Vector((0.072, 0.082 * sign, z)) + up
        m.objects[f"knee_{k}"].location = p[f"knee_{k}"] + Vector((0.016, 0, 0))
        m.objects[f"elbow_{k}"].location = p[f"elbow_{k}"]
    m.objects["jerkin_b"].location = Vector((-0.086, 0, 0.770)) + up
    spine = [Vector((-0.080, 0, 0.700 - 0.040 * i)) + up for i in range(5)]
    m.set_tube("spine", [tuple(q) for q in spine], [0.016] * 5)
    for i in range(2):
        z = 0.680 - 0.050 * i
        m.put_segment(f"backrib{i}", Vector((-0.078, -0.070, z)) + up, Vector((-0.078, 0.070, z)) + up, 0.009)
    for sign, k in ((1, "l"), (-1, "r")):
        m.objects[f"cheek_{k}"].location = head + Vector((0.080, 0.060 * sign, -0.030))
    # recurve bow held down at the left side, string toward the body
    hand = p["hand_l"]
    d = Vector((0.10, 0.08, 1.0)).normalized()
    lo, hi = hand - d * 0.230, hand + d * 0.260
    out = Vector((0.060, 0.030, 0))
    pts = [lo + (hi - lo) * (k / 6) + out * math.sin(math.pi * k / 6) - out * 0.35 * (1 if k in (0, 6) else 0) for k in range(7)]
    m.set_tube("bow", [tuple(q) for q in pts], [0.008, 0.013, 0.016, 0.018, 0.016, 0.013, 0.008])
    m.put_segment("bowstring", pts[0], pts[-1], 0.004)
    # quiver at the right hip, arrows up and back
    hip = Vector((-0.020, -s["torso_r"][1] * 1.10, s["belt_z"] - 0.020)) + up
    top = hip + Vector((-0.050, -0.010, 0.170))
    m.put_segment("quiver", hip, top, 0.030)
    for i in range(3):
        b = top + Vector((0.006 * i, -0.010 + 0.010 * i, -0.010))
        m.put_segment(f"shaft{i}", b, b + Vector((-0.020, 0.004 * (i - 1), 0.060)), 0.006)


def assign_depth_parts(m, depth_of):
    return None
