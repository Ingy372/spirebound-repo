"""Road Bandit (Floor 1 monster, the Bandit Road), built on art/models/humanoid.py (second draft, 2026-11-25).

ART_REQUESTS.md: "a human bandit with a brown hood, a face scarf and a short sword".
The first draft (2026-11-15) had its own copied body; this one follows art/OUTFIT_RULES.md.

Identity (art/OUTFIT_RULES.md step 1):
  Silhouette: a ROUND brown hood (the Ranger player class owns the pointed hood: a monster must never pass for
              a player, rule O14), a red scarf over nose and mouth so only the eyes show, a short sword held low and
              forward in the right hand, a small round buckler on the left forearm.
  Colours:    mud-brown hood and short cape, a charcoal jerkin (brown on brown read as one blob), a red scarf,
              brown trousers; iron sword.
  Details:    scarf knot with two hanging tails at the back of the neck, hood rim, jerkin laces, a coin pouch at the
              belt, the buckler's iron rim and boss, the sword's crossguard.
Look-alike: Tibia's Bandit and Smuggler (human outlaws): ours is masked and hooded, theirs bare-headed.
Addons: none (a monster, rule A1).
"""
from __future__ import annotations

import math

from mathutils import Euler, Vector

import humanoid as H

NAME = "bandit"
WALK_FRAMES = 8
PALETTE = "bandit"
REFERENCE = "outfit_128.png"
PROJECTION = "oblique"
CANVAS_OFFSET = H.CANVAS_OFFSET
SIGNATURE = ["scarf", "hood"]
HEAD_PARTS = ["skin", "hair", "strand", "eye", "brow", "nose", "hood", "scarf"]
LEG_PARTS = ["leg_a", "leg_b", "boot_a", "boot_b"]
CHECK = {"size": (0.85, 1.45), "head": 0.08, "legs_side": 0.05, "eye": 1}

PARTS = H.PARTS + ["hood", "rim", "cape", "scarf", "lace", "pouch", "buckler", "iron", "blade", "hilt"]
PIXEL_RULES = H.pixel_rules(
    weight={"hood": 1.3, "rim": 2.2, "scarf": 1.8, "lace": 3.0, "pouch": 2.4, "buckler": 1.8, "iron": 3.0,
            "blade": 3.0, "hilt": 3.0},
    thin={"rim": 2, "lace": 2, "iron": 2, "blade": 2, "hilt": 2},
    soft=[["hood", "rim", "cape"], ["torso", "lace"], ["belt", "pouch"], ["buckler", "iron"], ["blade", "hilt"]],
    texture={"hood": [0.45, 0.2], "cape": [0.45, 0.25], "scarf": [0.35, 0.12]},
    selout=["hood", "cape", "scarf"],
)

SPEC = H.spec(torso_r=(0.100, 0.150, 0.182), arm_r=0.048, leg_r=0.050, stride=0.13, lift=0.060, bob=0.016,
              strands=(-1.0, 0.0, 1.0))


def build(model_cls, facing):
    m = H.build(model_cls, facing, SPEC, PARTS)
    m.ellipsoid("hood", "hood", radii=(0.132, 0.136, 0.120), segments=18, rings=10)
    m.tube("hood_rim", "rim", points=7)
    m.ellipsoid("cape", "cape", radii=(0.110, 0.180, 0.070), segments=16, rings=8)
    m.box("cape_back", "cape", size=(0.026, 0.240, 0.200))
    m.ellipsoid("scarf", "scarf", radii=(0.076, 0.120, 0.052), segments=14, rings=8)
    for i in range(2):
        m.capsule(f"tail{i}", "scarf")
        m.capsule(f"lace{i}", "lace")
    m.ellipsoid("pouch", "pouch", radii=(0.030, 0.030, 0.034), segments=8, rings=6)
    m.ellipsoid("buckler", "buckler", radii=(0.090, 0.022, 0.090), segments=16, rings=8)
    m.ellipsoid("buckler_rim", "iron", radii=(0.100, 0.010, 0.100), segments=16, rings=8)
    m.ellipsoid("boss", "iron", radii=(0.026, 0.022, 0.026), segments=8, rings=6)
    m.capsule("blade", "blade")
    m.capsule("guard", "hilt")
    m.capsule("grip", "hilt")
    return m


def _sword_hand(sh, a, walking):
    swing = 0.06 * math.sin(a) if walking else 0.0
    return sh + Vector((0.120 + swing, -0.040, -0.270))


def _buckler_hand(sh, a, walking):
    return sh + Vector((0.120, 0.060, -0.230))


def pose(m, t):
    p = H.pose(m, t, hands={"r": _sword_hand, "l": _buckler_hand})
    up, head, a, walking = p["up"], p["head"], p["a"], p["walking"]
    hood_c, hood_r = head + Vector((-0.052, 0, 0.034)), (0.132, 0.136, 0.120)   # set back: the eyes must show (O3)
    m.objects["hood"].location = hood_c
    rim = [H.on_ellipsoid(hood_c, hood_r, (0.55, math.sin(u), math.cos(u) * 0.8), 1.02) for u in (-1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5)]
    m.set_tube("hood_rim", [tuple(q) for q in rim], [0.010] * 7)
    m.objects["cape"].location = Vector((-0.010, 0, 0.860)) + up
    cb = m.objects["cape_back"]
    cb.rotation_mode = "XYZ"
    cb.rotation_euler = Euler((0, 0.15 + (0.08 * abs(math.sin(a)) if walking else 0.0), 0))
    cb.location = Vector((-0.128, 0, 0.740)) + up
    m.objects["scarf"].location = head + Vector((0.058, 0, -0.060))          # over nose and mouth: eyes stay clear
    flap = 0.03 * math.sin(a) if walking else 0.0
    for i, sgn in enumerate((1, -1)):
        knot = head + Vector((-0.100, 0.020 * sgn, -0.050))
        m.put_segment(f"tail{i}", knot, knot + Vector((-0.050 - flap, 0.030 * sgn, -0.090)), 0.014, 0.008)
        z = 0.780 - 0.070 * i
        m.put_segment(f"lace{i}", Vector((0.104, -0.030, z)) + up, Vector((0.104, 0.030, z - 0.020)) + up, 0.005)
    s = m.spec
    m.objects["pouch"].location = Vector((s["torso_r"][0] * 0.7, s["torso_r"][1] * 0.9, s["belt_z"] - 0.030)) + up
    hand = p["hand_l"]
    for name, dy in (("buckler_rim", 0.0), ("buckler", 0.004), ("boss", 0.020)):
        o = m.objects[name]
        o.rotation_mode = "XYZ"
        o.rotation_euler = Euler((0.0, 0.10, 0.30))
        o.location = hand + Vector((-0.010, 0.040 + dy, 0.020))
    hand = p["hand_r"]
    fwd = Vector((0.75, -0.35, -0.10)).normalized()                      # held low and forward, point out
    side = fwd.cross(Vector((0, 0, 1))).normalized()
    m.put_segment("grip", hand - fwd * 0.040, hand + fwd * 0.030, 0.014)
    m.put_segment("guard", hand + fwd * 0.032 - side * 0.045, hand + fwd * 0.032 + side * 0.045, 0.012)
    m.put_segment("blade", hand + fwd * 0.036, hand + fwd * 0.250, 0.020, 0.010)


def assign_depth_parts(m, depth_of):
    return None
