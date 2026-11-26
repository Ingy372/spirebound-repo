"""Hearthgate Watch guard (Guard Ressa and any later town guards), built on art/models/humanoid.py (2026-11-25).

She wore Tibia's knight outfit, one of the looks Tibia veterans know at a glance (Jay: "Redo any that stand out").
Hearthgate's watch gets a uniform of its own, in the town's hearth colours.

Identity (art/OUTFIT_RULES.md step 1):
  Silhouette: a brimmed iron kettle helm, a long padded red gambeson to the knee, a tall spear held upright at the
              right side. No shield (the Vanguard class owns the kite shield, rule O20).
  Colours:    ember-red gambeson with quilting lines, an iron helm and spearhead, a gold hearth-flame badge, brown
              leather belt and boots; dark hair in a short braid.
  Details:    the helm's brim and rim, quilting lines down the gambeson, its hem, the gold badge, a belt with an iron
              buckle and a horn whistle, bracers, the spear's leaf blade and binding.
Addons: none (an NPC, rule A1).
"""
from __future__ import annotations

import math

from mathutils import Euler, Vector

import humanoid as H

NAME = "watchguard"
WALK_FRAMES = 8
PALETTE = "watchguard"
REFERENCE = "outfit_128.png"
PROJECTION = "oblique"
CANVAS_OFFSET = H.CANVAS_OFFSET
SIGNATURE = ["helm", "spear"]
HEAD_PARTS = ["skin", "hair", "strand", "eye", "brow", "nose", "helm"]
LEG_PARTS = ["leg_a", "leg_b", "boot_a", "boot_b"]
CHECK = {"size": (0.85, 1.55), "head": 0.08, "legs_side": 0.05, "eye": 1}

PARTS = H.PARTS + ["helm", "brim", "gambeson", "quilt", "hem", "badge", "spear", "tip", "whistle"]
PIXEL_RULES = H.pixel_rules(
    weight={"helm": 1.4, "brim": 2.2, "gambeson": 1.3, "quilt": 3.0, "hem": 2.4, "badge": 5.0, "spear": 3.0,
            "tip": 3.0, "whistle": 3.0},
    thin={"brim": 2, "quilt": 2, "hem": 2, "badge": 2, "spear": 2, "tip": 2, "whistle": 2},
    soft=[["helm", "brim"], ["gambeson", "quilt", "hem", "badge", "torso"], ["spear", "tip"]],
    texture={"gambeson": [0.4, 0.2], "helm": [0.25, 0.05]},
    selout=["helm", "gambeson"],
)

SPEC = H.spec(torso_r=(0.100, 0.150, 0.184), arm_r=0.048, leg_r=0.050, stride=0.11, lift=0.050, bob=0.014,
              strands=(-1.0, 0.0, 1.0))


def build(model_cls, facing):
    m = H.build(model_cls, facing, SPEC, PARTS)
    m.ellipsoid("helm", "helm", radii=(0.118, 0.118, 0.080), segments=18, rings=8)
    m.ellipsoid("brim", "brim", radii=(0.136, 0.136, 0.012), segments=22, rings=6)
    m.tube("braid", "hair", points=4)
    for side in ("f", "b"):
        m.box(f"gamb_{side}", "gambeson", size=(0.030, 0.230, 0.260))
        m.box(f"hem_{side}", "hem", size=(0.034, 0.236, 0.026))
    for i in range(3):
        m.box(f"quilt{i}", "quilt", size=(0.034, 0.008, 0.240))
    m.ellipsoid("badge", "badge", radii=(0.020, 0.030, 0.030), segments=10, rings=6)
    m.capsule("whistle", "whistle")
    m.capsule("spear", "spear")
    m.ellipsoid("tip", "tip", radii=(0.026, 0.038, 0.082), segments=8, rings=8)
    return m


def _spear_hand(sh, a, walking):
    return sh + Vector((0.080, -0.080, -0.250))


def pose(m, t):
    p = H.pose(m, t, hands={"r": _spear_hand})
    up, head, a, walking = p["up"], p["head"], p["a"], p["walking"]
    s = m.spec
    helm = head + Vector((-0.036, 0, 0.078))      # high and back: the face shows from the side
    m.objects["helm"].location = helm
    o = m.objects["brim"]
    o.rotation_mode = "XYZ"
    o.rotation_euler = Euler((0, -0.30, 0))                 # tipped back: the face shows (O15)
    o.location = helm + Vector((0.004, 0, -0.022))
    swing = 0.02 * math.sin(a) if walking else 0.0
    pts = [head + Vector((-0.120 - 0.010 * i, swing * i / 3, -0.060 - 0.050 * i)) for i in range(4)]
    m.set_tube("braid", [tuple(q) for q in pts], [0.024, 0.022, 0.018, 0.012])
    flap = 0.22 * abs(math.sin(a)) if walking else 0.0
    for side, x in (("f", 0.100), ("b", -0.100)):
        rot = Euler((0, flap if side == "f" else -flap, 0))
        for name, z in ((f"gamb_{side}", 0.440), (f"hem_{side}", 0.315)):
            g = m.objects[name]
            g.rotation_mode = "XYZ"
            g.rotation_euler = rot
            g.location = Vector((x, 0, z)) + up
    for i, y in enumerate((-0.060, 0.0, 0.060)):
        q = m.objects[f"quilt{i}"]
        q.location = Vector((s["torso_r"][0] * 1.02, y, 0.700)) + up
    m.objects["badge"].location = Vector((s["torso_r"][0] * 1.06, 0.050, 0.800)) + up
    belt = Vector((s["torso_r"][0] * 0.5, s["torso_r"][1] * 0.95, s["belt_z"])) + up
    m.put_segment("whistle", belt, belt + Vector((0.030, 0.010, -0.060)), 0.012, 0.008)
    hand = p["hand_r"]
    d = Vector((0.08, -0.08, 1.0)).normalized()
    foot, top = hand - d * 0.360, hand + d * 0.540
    m.put_segment("spear", foot, top, 0.014)
    tip = m.objects["tip"]
    tip.location = top + d * 0.050
    tip.rotation_mode = "QUATERNION"
    tip.rotation_quaternion = d.to_track_quat("Z", "Y")


def assign_depth_parts(m, depth_of):
    return None
