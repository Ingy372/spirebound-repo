"""Weaponsmith Garrick (Hearthgate), built on art/models/humanoid.py (2026-11-25).

He wore Tibia's knight outfit (Jay: "Redo any that stand out"). A smith of our own:
  Silhouette: broad and heavy, bare muscled arms, a big forge hammer resting on his right shoulder, thick leather
              gauntlets, a sleeveless leather vest (no apron: the merchant owns that outline, rule O14), a bushy beard.
  Colours:    soot-dark leather vest over a linen shirt (brown on brown read as one blob, O18), bronze-tanned skin, iron hammer head on a dark haft; a
              red bandana on dark hair; ember-orange glints.
  Details:    the vest's laces and rivets, soot smudges, gauntlet cuffs, the hammer's iron bands, a pair of tongs on
              the belt, a red bandana knot.
Addons: none (an NPC, rule A1).
"""
from __future__ import annotations

import math

from mathutils import Euler, Vector

import humanoid as H

NAME = "smith"
WALK_FRAMES = 8
PALETTE = "smith"
REFERENCE = "outfit_128.png"
PROJECTION = "oblique"
CANVAS_OFFSET = H.CANVAS_OFFSET
SIGNATURE = ["hammer", "bandana"]
HEAD_PARTS = ["skin", "hair", "strand", "eye", "brow", "nose", "beard", "bandana"]
LEG_PARTS = ["leg_a", "leg_b", "boot_a", "boot_b"]
CHECK = {"size": (0.85, 1.50), "head": 0.08, "legs_side": 0.05, "eye": 1}

PARTS = H.PARTS + ["vest", "rivet", "bare", "gauntlet", "beard", "bandana", "hammer", "haft", "tongs", "soot"]
PIXEL_RULES = H.pixel_rules(
    weight={"vest": 1.3, "rivet": 4.0, "bare": 1.6, "gauntlet": 2.0, "beard": 1.5, "bandana": 2.0, "hammer": 2.6,
            "haft": 3.0, "tongs": 3.0, "soot": 2.6},
    thin={"rivet": 2, "haft": 2, "tongs": 2, "soot": 2},
    soft=[["vest", "rivet", "torso", "soot"], ["skin", "beard"], ["hair", "bandana"], ["hammer", "haft"]],
    texture={"vest": [0.4, 0.2], "beard": [0.4, 0.2], "hammer": [0.3, 0.1]},
    selout=["vest", "hammer"],
)

SPEC = H.spec(torso_r=(0.116, 0.172, 0.188), arm_r=0.060, leg_r=0.056, shoulder_y=0.172, stride=0.10, lift=0.045,
              bob=0.016, strands=(-1.2, -0.3, 0.6))


def build(model_cls, facing):
    m = H.build(model_cls, facing, SPEC, PARTS)
    m.ellipsoid("beard", "beard", radii=(0.066, 0.090, 0.066), segments=12, rings=8)
    m.ellipsoid("bandana", "bandana", radii=(0.096, 0.104, 0.032), segments=16, rings=8)   # smaller than the head (O23)
    m.capsule("knot", "bandana")
    for side in ("f_l", "f_r", "b"):
        m.box(f"vest_{side}", "vest", size=(0.026, 0.110 if side != "b" else 0.260, 0.240))
    for i in range(3):
        m.ellipsoid(f"rivet{i}", "rivet", radii=(0.010, 0.010, 0.010), segments=6, rings=4)
    m.ellipsoid("soot", "soot", radii=(0.010, 0.030, 0.022), segments=8, rings=6)
    for k in ("l", "r"):
        m.capsule(f"bare_{k}", "bare")
        m.frustum(f"gaunt_{k}", "gauntlet", top_ratio=1.15, segments=10)
    m.capsule("haft", "haft")
    m.box("hammer", "hammer", size=(0.080, 0.150, 0.070))
    m.capsule("tongs", "tongs")
    return m


def _hammer_hand(sh, a, walking):
    return sh + Vector((0.070, -0.040, -0.060))           # the hand up at the shoulder, steadying the haft


def pose(m, t):
    p = H.pose(m, t, hands={"r": _hammer_hand})
    up, head, a, walking = p["up"], p["head"], p["a"], p["walking"]
    s = m.spec
    m.objects["beard"].location = head + Vector((0.074, 0, -0.080))
    m.objects["bandana"].location = head + Vector((-0.030, 0, 0.108))
    m.put_segment("knot", head + Vector((-0.110, 0, 0.060)), head + Vector((-0.160, 0, 0.010)), 0.018, 0.010)
    for side, (x, y) in (("f_l", (0.110, 0.070)), ("f_r", (0.110, -0.070)), ("b", (-0.112, 0.0))):
        m.objects[f"vest_{side}"].location = Vector((x, y, 0.720)) + up
    for i in range(3):
        m.objects[f"rivet{i}"].location = Vector((s["torso_r"][0] * 1.10, 0.040, 0.800 - 0.070 * i)) + up
    m.objects["soot"].location = Vector((s["torso_r"][0] * 1.08, -0.060, 0.660)) + up
    for k in ("l", "r"):
        sh, e, h = p[f"shoulder_{k}"], p[f"elbow_{k}"], p[f"hand_{k}"]
        m.put_segment(f"bare_{k}", sh, e + (h - e) * 0.4, s["arm_r"] * 1.12, s["arm_r"] * 0.98)   # bare muscled arms
        d = (h - e).normalized()
        g = m.objects[f"gaunt_{k}"]
        g.location = e + (h - e) * 0.55
        g.rotation_mode = "QUATERNION"
        g.rotation_quaternion = d.to_track_quat("Z", "Y")
        g.scale = (s["arm_r"] * 1.25, s["arm_r"] * 1.25, 0.110)
    hand = p["hand_r"]
    d = Vector((-0.60, -0.10, 0.80)).normalized()          # the haft rests on the shoulder, head behind it
    m.put_segment("haft", hand - d * 0.120, hand + d * 0.200, 0.014)
    hm = m.objects["hammer"]
    hm.location = hand + d * 0.230
    hm.rotation_mode = "QUATERNION"
    hm.rotation_quaternion = d.to_track_quat("Z", "Y")
    belt = Vector((s["torso_r"][0] * 0.5, s["torso_r"][1] * 0.98, s["belt_z"])) + up
    m.put_segment("tongs", belt, belt + Vector((0.020, 0.010, -0.140)), 0.010)


def assign_depth_parts(m, depth_of):
    return None
