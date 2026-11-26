"""Runewright Mael (Hearthgate), built on art/models/humanoid.py (2026-11-25).

Mael wore Tibia's mage outfit with its tall pointed hat (Jay: "Redo any that stand out"). A runewright cuts runes
into stone, so: a stone-cutter, not a wizard.
  Silhouette: a sturdy figure in a stone-dusted work tunic (no apron: the merchant owns that outline, rule O14) with
              a wide leather belt of tools; a slate tablet held at the chest
              with a glowing blue rune, a chisel in the other hand; short cropped dark hair and a long braided beard.
  Colours:    slate-blue tunic dusted pale, brown leather, a dark slate tablet with a cyan rune; dark beard.
  Details:    the rune's glow, the tablet's chipped rim, chisel and mallet on the belt, wrist wraps, the beard's braid
              bead, stone dust flecks on the tunic.
Addons: none (an NPC, rule A1).
"""
from __future__ import annotations

import math

from mathutils import Euler, Vector

import humanoid as H

NAME = "runewright"
WALK_FRAMES = 8
PALETTE = "runewright"
REFERENCE = "outfit_128.png"
PROJECTION = "oblique"
CANVAS_OFFSET = H.CANVAS_OFFSET
SIGNATURE = ["tunic", "wrap"]           # the tablet and beard are on his front; the wrists show from every side
HEAD_PARTS = ["skin", "hair", "strand", "eye", "brow", "nose", "beard"]
LEG_PARTS = ["leg_a", "leg_b", "boot_a", "boot_b"]
CHECK = {"size": (0.85, 1.45), "head": 0.08, "legs_side": 0.05, "eye": 1}

PARTS = H.PARTS + ["tunic", "dust", "tablet", "rune", "beard", "bead", "tool", "wrap"]
PIXEL_RULES = H.pixel_rules(
    weight={"tunic": 1.3, "dust": 3.0, "tablet": 1.8, "rune": 6.0, "beard": 1.5, "bead": 5.0, "tool": 3.0, "wrap": 2.4},
    thin={"dust": 2, "rune": 2, "bead": 2, "tool": 2, "wrap": 2},
    soft=[["tunic", "dust", "torso"], ["tablet", "rune"], ["skin", "beard", "bead"]],
    texture={"tunic": [0.4, 0.2], "tablet": [0.5, 0.3], "beard": [0.35, 0.15]},
    no_outline=["rune"],
    selout=["tunic", "tablet"],
)

SPEC = H.spec(torso_r=(0.110, 0.162, 0.180), arm_r=0.054, leg_r=0.054, stride=0.10, lift=0.045, bob=0.014,
              strands=(-1.2, -0.3, 0.6))                   # short cropped hair: a bald crown read as an egg (rule O23)


def build(model_cls, facing):
    m = H.build(model_cls, facing, SPEC, PARTS)
    m.ellipsoid("beard", "beard", radii=(0.060, 0.084, 0.066), segments=12, rings=8)
    m.tube("braid", "beard", points=4)
    m.ellipsoid("bead", "bead", radii=(0.012, 0.012, 0.012), segments=6, rings=4)
    for side in ("f", "b"):
        m.box(f"tunic_{side}", "tunic", size=(0.030, 0.230, 0.150))
    for i in range(3):
        m.ellipsoid(f"dust{i}", "dust", radii=(0.008, 0.012, 0.010), segments=6, rings=4)
    m.box("tablet", "tablet", size=(0.024, 0.130, 0.150))
    m.box("rune", "rune", size=(0.028, 0.050, 0.070))
    m.capsule("chisel", "tool")
    m.capsule("mallet", "tool")
    for k in ("l", "r"):
        m.frustum(f"wrap_{k}", "wrap", top_ratio=1.0, segments=10)
    return m


def _tablet_hand(sh, a, walking):
    return sh + Vector((0.140, 0.040, -0.180))


def _chisel_hand(sh, a, walking):
    return sh + Vector((0.140, -0.050, -0.170))


def pose(m, t):
    p = H.pose(m, t, hands={"l": _tablet_hand, "r": _chisel_hand})
    up, head, a, walking = p["up"], p["head"], p["a"], p["walking"]
    s = m.spec
    m.objects["beard"].location = head + Vector((0.080, 0, -0.090))
    sway = 0.02 * math.sin(a) if walking else 0.0
    pts = [head + Vector((0.100 + sway * i / 3, 0, -0.150 - 0.040 * i)) for i in range(4)]
    m.set_tube("braid", [tuple(q) for q in pts], [0.022, 0.018, 0.014, 0.010])
    m.objects["bead"].location = pts[-1]
    flap = 0.18 * abs(math.sin(a)) if walking else 0.0
    for side, x in (("f", 0.106), ("b", -0.106)):
        o = m.objects[f"tunic_{side}"]
        o.rotation_mode = "XYZ"
        o.rotation_euler = Euler((0, flap if side == "f" else -flap, 0))
        o.location = Vector((x, 0, 0.470)) + up
    for i, (y, z) in enumerate(((0.060, 0.760), (-0.040, 0.690), (0.020, 0.620))):
        m.objects[f"dust{i}"].location = Vector((s["torso_r"][0] * 1.04, y, z)) + up
    hand = p["hand_l"]
    for name, dx in (("tablet", 0.0), ("rune", 0.006)):
        o = m.objects[name]
        o.rotation_mode = "XYZ"
        o.rotation_euler = Euler((0, -0.35, 0))           # tipped toward the viewer
        o.location = hand + Vector((0.030 + dx, -0.040, 0.050))
    hand = p["hand_r"]
    m.put_segment("chisel", hand, hand + Vector((0.060, 0.050, 0.050)), 0.010, 0.006)
    belt = Vector((s["torso_r"][0] * 0.4, -s["torso_r"][1] * 0.98, s["belt_z"])) + up
    m.put_segment("mallet", belt, belt + Vector((0.010, -0.010, -0.110)), 0.018)
    for k in ("l", "r"):
        e, h = p[f"elbow_{k}"], p[f"hand_{k}"]
        d = (h - e).normalized()
        w = m.objects[f"wrap_{k}"]
        w.location = e + (h - e) * 0.55
        w.rotation_mode = "QUATERNION"
        w.rotation_quaternion = d.to_track_quat("Z", "Y")
        w.scale = (s["arm_r"] * 1.12, s["arm_r"] * 1.12, 0.060)


def assign_depth_parts(m, depth_of):
    return None
