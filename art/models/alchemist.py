"""Alchemist Ivo (Hearthgate), built on art/models/humanoid.py (2026-11-25).

He wore Tibia's mage outfit with its tall pointed hat, a look Tibia veterans know at once (Jay: "Redo any that stand
out"). An alchemist of our own:
  Silhouette: brass goggles pushed up on his forehead over wild hair, a knee-length smock, a round flask held up in
              his right hand with a puff of green vapour above it, a belt hung with vials. No apron (the merchant owns
              that outline, rule O14), no pointed hat.
  Colours:    a stained mustard smock, dark green trousers, brass goggles, a green-glowing flask; frizzy ginger hair.
  Details:    goggle lenses and strap, smock hem and stains, rolled cuffs, three vials on the belt (red, blue, green),
              the flask's cork, the vapour puff.
Addons: none (an NPC, rule A1).
"""
from __future__ import annotations

import math

from mathutils import Euler, Vector

import humanoid as H

NAME = "alchemist"
WALK_FRAMES = 8
PALETTE = "alchemist"
REFERENCE = "outfit_128.png"
PROJECTION = "oblique"
CANVAS_OFFSET = H.CANVAS_OFFSET
SIGNATURE = ["goggle", "flask"]
HEAD_PARTS = ["skin", "hair", "strand", "eye", "brow", "nose", "goggle", "lens"]
LEG_PARTS = ["leg_a", "leg_b", "boot_a", "boot_b"]
CHECK = {"size": (0.85, 1.45), "head": 0.08, "legs_side": 0.05, "eye": 1}

PARTS = H.PARTS + ["smock", "stain", "hem", "goggle", "lens", "flask", "vapour", "vial", "cork"]
PIXEL_RULES = H.pixel_rules(
    weight={"smock": 1.3, "stain": 2.6, "hem": 2.4, "goggle": 3.0, "lens": 5.0, "flask": 2.6, "vapour": 1.0,
            "vial": 4.0, "cork": 4.0},
    thin={"stain": 2, "hem": 2, "goggle": 2, "lens": 2, "vial": 2, "cork": 2},
    soft=[["smock", "stain", "hem", "torso"], ["goggle", "lens"], ["flask", "cork"]],
    texture={"smock": [0.4, 0.2], "hair": [0.6, 0.3]},
    no_outline=["vapour"],
    selout=["smock", "hair"],
)

SPEC = H.spec(torso_r=(0.098, 0.150, 0.182), arm_r=0.046, leg_r=0.048, stride=0.11, lift=0.050, bob=0.016,
              strands=(-1.6, -0.8, 0.0, 0.8, 1.6))


def build(model_cls, facing):
    m = H.build(model_cls, facing, SPEC, PARTS)
    for i in range(4):
        m.ellipsoid(f"tuft{i}", "hair", radii=(0.026, 0.026, 0.022), segments=10, rings=6)
    for k in ("l", "r"):
        m.capsule(f"strap_{k}", "goggle")           # short side straps: a full ring read as a halo (O7)
    for k in ("l", "r"):
        m.ellipsoid(f"lens_{k}", "lens", radii=(0.020, 0.024, 0.024), segments=10, rings=6)
    for side in ("f", "b"):
        m.box(f"smock_{side}", "smock", size=(0.030, 0.220, 0.240))
        m.box(f"hem_{side}", "hem", size=(0.034, 0.226, 0.024))
    for i in range(2):
        m.ellipsoid(f"stain{i}", "stain", radii=(0.010, 0.030, 0.024), segments=8, rings=6)
    for i in range(3):
        m.capsule(f"vial{i}", "vial")
        m.ellipsoid(f"vcork{i}", "cork", radii=(0.010, 0.010, 0.008), segments=6, rings=4)
    m.ellipsoid("flask", "flask", radii=(0.042, 0.042, 0.042), segments=12, rings=8)
    m.capsule("neck_f", "flask")
    m.ellipsoid("cork", "cork", radii=(0.012, 0.012, 0.010), segments=6, rings=4)
    for i in range(2):
        m.ellipsoid(f"puff{i}", "vapour", radii=(0.030, 0.030, 0.024), segments=8, rings=6)
    return m


def _flask_hand(sh, a, walking):
    return sh + Vector((0.180, 0.150, -0.120))            # held up in front of the middle of his chest (seen from both sides)


def pose(m, t):
    p = H.pose(m, t, hands={"r": _flask_hand})
    up, head, cap, a, walking = p["up"], p["head"], p["cap"], p["a"], p["walking"]
    s = m.spec
    for i, (dx, dy, dz) in enumerate(((-0.040, 0.100, 0.020), (-0.040, -0.100, 0.020), (-0.090, 0.050, 0.060), (-0.090, -0.050, 0.060))):
        m.objects[f"tuft{i}"].location = cap + Vector((dx, dy, dz))
    for sign, k in ((1, "l"), (-1, "r")):
        m.put_segment(f"strap_{k}", head + Vector((0.090, 0.062 * sign, 0.088)), head + Vector((0.020, 0.112 * sign, 0.060)), 0.008)
    for sign, k in ((1, "l"), (-1, "r")):
        m.objects[f"lens_{k}"].location = head + Vector((0.100, 0.036 * sign, 0.088))   # pushed up on the forehead
    flap = 0.22 * abs(math.sin(a)) if walking else 0.0
    for side, x in (("f", 0.098), ("b", -0.098)):
        for name, z in ((f"smock_{side}", 0.440), (f"hem_{side}", 0.320)):
            o = m.objects[name]
            o.rotation_mode = "XYZ"
            o.rotation_euler = Euler((0, flap if side == "f" else -flap, 0))
            o.location = Vector((x, 0, z)) + up
    m.objects["stain0"].location = Vector((s["torso_r"][0] * 1.02, 0.050, 0.720)) + up
    m.objects["stain1"].location = Vector((0.112, -0.050, 0.470)) + up
    for i in range(3):
        b = Vector((s["torso_r"][0] * 0.9, -0.090 + 0.090 * i, s["belt_z"] - 0.020)) + up
        m.put_segment(f"vial{i}", b, b + Vector((0, 0, -0.050)), 0.014)
        m.objects[f"vcork{i}"].location = b + Vector((0, 0, 0.010))
    hand = p["hand_r"]
    fl = hand + Vector((0.010, 0, 0.050))
    m.objects["flask"].location = fl
    m.put_segment("neck_f", fl + Vector((0, 0, 0.030)), fl + Vector((0, 0, 0.070)), 0.012)
    m.objects["cork"].location = fl + Vector((0, 0, 0.076))
    rise = (t or 0.0) * 0.040
    for i in range(2):
        m.objects[f"puff{i}"].location = fl + Vector((-0.010 * i, 0.010 * i, 0.110 + 0.040 * i + rise))


def assign_depth_parts(m, depth_of):
    return None
