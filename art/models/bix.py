"""Little Bix ("a child who never stops running", Hearthgate), built on art/models/humanoid.py (2026-11-25).

Bix wore Tibia's grown-up citizen outfit, so the town's child stood as tall as the guards (Jay: "Redo any that
stand out"). Now a child:
  Silhouette: about three quarters of an adult's height, a bigger head for the body, a mop of hair, a wooden toy sword
              waved overhead, a fast bouncing run (bigger stride and bob than any adult).
  Colours:    a bright green tunic with a patched knee on brown breeches, a little red scarf; straw-blond hair.
  Details:    the patch, the scarf's flying ends, the toy sword's crossguard and string-wrapped grip, scuffed boots,
              freckle-pink cheeks (the nose highlight).
Addons: none (an NPC, rule A1).
"""
from __future__ import annotations

import math

from mathutils import Vector

import humanoid as H

NAME = "bix"
WALK_FRAMES = 8
PALETTE = "bix"
REFERENCE = "outfit_128.png"
PROJECTION = "oblique"
CANVAS_OFFSET = H.CANVAS_OFFSET
SIZE = 0.76                             # a child: the figure scales round its feet, so it still stands on the tile
SIGNATURE = ["torso", "toysword"]       # the green tunic is the torso; the little scarf hides under his big head
HEAD_PARTS = ["skin", "hair", "strand", "eye", "brow", "nose"]
LEG_PARTS = ["leg_a", "leg_b", "boot_a", "boot_b"]
CHECK = {"size": (0.60, 1.30), "head": 0.10, "legs_side": 0.05, "eye": 1}   # smaller than an adult on purpose

PARTS = H.PARTS + ["tunic", "patch", "scarf", "toysword", "grip"]
PIXEL_RULES = H.pixel_rules(
    weight={"tunic": 1.3, "patch": 3.0, "scarf": 2.4, "toysword": 3.0, "grip": 3.0},
    thin={"patch": 2, "scarf": 2, "toysword": 2, "grip": 2},
    soft=[["tunic", "torso", "patch"], ["toysword", "grip"]],
    texture={"tunic": [0.4, 0.2], "hair": [0.5, 0.2]},
    selout=["tunic", "hair"],
)

SPEC = H.spec(torso_r=(0.096, 0.144, 0.176), arm_r=0.048, leg_r=0.050, head_r=(0.130, 0.124, 0.138),
              cap_r=(0.130, 0.132, 0.112), eye_r=(0.012, 0.013, 0.018), stride=0.17, lift=0.090, bob=0.040, arm_swing=0.18,
              strands=(-1.4, -0.6, 0.2, 1.0))


def build(model_cls, facing):
    m = H.build(model_cls, facing, SPEC, PARTS)
    for i in range(3):
        m.ellipsoid(f"mop{i}", "hair", radii=(0.030, 0.050, 0.024), segments=10, rings=6)
    m.box("tunic", "tunic", size=(0.030, 0.220, 0.120))
    m.ellipsoid("patch", "patch", radii=(0.014, 0.030, 0.028), segments=8, rings=6)
    m.ellipsoid("scarf", "scarf", radii=(0.080, 0.110, 0.030), segments=12, rings=6)
    for i in range(2):
        m.capsule(f"tail{i}", "scarf")
    m.capsule("toysword", "toysword")
    m.capsule("guard", "grip")
    m.capsule("grip", "grip")
    return m


def _sword_hand(sh, a, walking):
    wave = 0.05 * math.sin(2 * a) if walking else 0.0
    # held out in front, not out to the side: held out sideways the arm read as broken in the south view
    # (Jay, 2026-11-27: "little bix arm looks broken on the left side")
    return sh + Vector((0.140, 0.010, -0.110 + wave))


def pose(m, t):
    p = H.pose(m, t, hands={"r": _sword_hand})
    up, head, cap, a, walking = p["up"], p["head"], p["cap"], p["a"], p["walking"]
    for i, (dx, dy) in enumerate(((0.040, 0.060), (0.045, -0.050), (0.020, 0.000))):
        m.objects[f"mop{i}"].location = cap + Vector((dx, dy, 0.040))
    m.objects["tunic"].location = Vector((0.098, 0, 0.480)) + up
    m.objects["patch"].location = p["knee_l"] + Vector((0.050, 0, 0.010))
    m.objects["scarf"].location = Vector((0.0, 0, 0.880)) + up
    flap = 0.04 * math.sin(2 * a) if walking else 0.0
    for i, sgn in enumerate((1, -1)):
        root = Vector((-0.090, 0.030 * sgn, 0.880)) + up
        m.put_segment(f"tail{i}", root, root + Vector((-0.110, 0.030 * sgn, -0.030 + flap * sgn)), 0.020, 0.012)
    hand = p["hand_r"]
    d = Vector((0.80, -0.05, 0.60)).normalized()        # pointed ahead and up, like a knight's charge
    side = d.cross(Vector((1, 0, 0))).normalized()
    m.put_segment("grip", hand - d * 0.030, hand + d * 0.030, 0.012)
    m.put_segment("guard", hand + d * 0.034 - side * 0.040, hand + d * 0.034 + side * 0.040, 0.012)
    m.put_segment("toysword", hand + d * 0.036, hand + d * 0.300, 0.026, 0.020)


def assign_depth_parts(m, depth_of):
    return None
