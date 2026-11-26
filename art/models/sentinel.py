"""Ruin Sentinel (Floor 1 monster, the Old Watchtower), built on art/models/humanoid.py (second draft, 2026-11-25).

ART_REQUESTS.md: "an old animated stone guard statue, cracked and mossy, holding a stone spear".
The first draft (2026-11-15) had its own copied body; this one follows art/OUTFIT_RULES.md.

Identity (art/OUTFIT_RULES.md step 1):
  Silhouette: a broad, blocky stone guard: a rounded helm with a ridge crest, heavy square shoulder blocks, a tall
              stone spear held upright and out at the right side, a stiff short-stepping walk (a statue, not a man).
  Colours:    weathered grey stone with warm sandy highlights, green moss on the helm and shoulders, two pale-blue
              glowing eyes in a dark visor slit.
  Details:    a crack line down the chest and one on the helm, moss patches, the visor slit, the helm's ridge, a
              stone belt with a carved boss, the spear's leaf-shaped blade and a binding band.
Look-alike: Tibia's Stone Golem and Gargoyle: ours is a man-shaped guard statue with a spear and moss, not a lump
of rock or a winged beast.
Addons: none (a monster, rule A1).
"""
from __future__ import annotations

import math

from mathutils import Euler, Vector

import humanoid as H

NAME = "sentinel"
WALK_FRAMES = 8
PALETTE = "sentinel"
REFERENCE = "outfit_128.png"
PROJECTION = "oblique"
CANVAS_OFFSET = H.CANVAS_OFFSET
SIGNATURE = ["helm", "spear"]
HEAD_PARTS = ["skin", "hair", "strand", "eye", "brow", "nose", "helm", "visor", "crest"]
LEG_PARTS = ["leg_a", "leg_b", "boot_a", "boot_b"]
CHECK = {"size": (0.85, 1.55), "head": 0.08, "legs_side": 0.05, "eye": 1}

PARTS = H.PARTS + ["helm", "visor", "crest", "block", "moss", "crack", "spear", "tip", "band"]
PIXEL_RULES = H.pixel_rules(
    weight={"helm": 1.4, "visor": 3.0, "crest": 2.0, "block": 1.4, "moss": 2.0, "crack": 3.2, "spear": 3.0, "tip": 3.0,
            "band": 3.0},
    thin={"visor": 2, "crack": 2, "spear": 2, "band": 2},
    soft=[["helm", "visor", "crest", "moss", "crack"], ["torso", "crack", "moss"], ["block", "moss"],
          ["spear", "tip", "band"]],
    texture={"helm": [0.5, 0.3], "block": [0.5, 0.3], "torso": [0.5, 0.3], "arm_a": [0.5, 0.3], "arm_b": [0.5, 0.3],
             "leg_a": [0.5, 0.3], "leg_b": [0.5, 0.3], "moss": [0.7, 0.4]},
    selout=["helm", "block"],
)

SPEC = H.spec(torso_r=(0.118, 0.172, 0.190), arm_r=0.060, leg_r=0.062, boot_r=0.068, stride=0.07, lift=0.030,
              bob=0.006, arm_swing=0.03, eye_r=(0.012, 0.014, 0.012), strands=())


def build(model_cls, facing):
    m = H.build(model_cls, facing, SPEC, PARTS)
    m.ellipsoid("helm", "helm", radii=(0.140, 0.138, 0.120), segments=18, rings=10)
    m.box("visor", "visor", size=(0.030, 0.150, 0.022))
    for k in ("l", "r"):
        m.ellipsoid(f"glow_{k}", "eye", radii=(0.014, 0.018, 0.012), segments=6, rings=4)   # the helm hides the face's own eyes
    m.box("crest", "crest", size=(0.200, 0.024, 0.040))
    for k in ("l", "r"):
        m.box(f"block_{k}", "block", size=(0.120, 0.090, 0.080))
        m.ellipsoid(f"moss_sh_{k}", "moss", radii=(0.050, 0.040, 0.020), segments=8, rings=6)
    m.ellipsoid("moss_helm", "moss", radii=(0.060, 0.050, 0.024), segments=8, rings=6)
    m.tube("crack_chest", "crack", points=5)
    m.tube("crack_helm", "crack", points=4)
    m.capsule("spear", "spear")
    m.ellipsoid("tip", "tip", radii=(0.022, 0.034, 0.070), segments=8, rings=8)
    m.capsule("band", "band")
    return m


def _spear_hand(sh, a, walking):
    return sh + Vector((0.070, -0.090, -0.250))


def pose(m, t):
    p = H.pose(m, t, hands={"r": _spear_hand})
    up, head, a, walking = p["up"], p["head"], p["a"], p["walking"]
    s = m.spec
    helm_c = head + Vector((-0.010, 0, 0.020))
    m.objects["helm"].location = helm_c
    m.objects["visor"].location = helm_c + Vector((0.128, 0, -0.012))
    for sign, k in ((1, "l"), (-1, "r")):
        m.objects[f"glow_{k}"].location = helm_c + Vector((0.146, 0.040 * sign, -0.012))
    m.objects["crest"].location = helm_c + Vector((-0.010, 0, 0.122))
    m.objects["moss_helm"].location = helm_c + Vector((-0.050, 0.060, 0.090))
    crack = [H.on_ellipsoid(helm_c, (0.140, 0.138, 0.120), (0.3 - 0.2 * i, -0.6 + 0.1 * (i % 2), 0.7), 1.03) for i in range(4)]
    m.set_tube("crack_helm", [tuple(q) for q in crack], [0.006] * 4)
    for sign, k in ((1, "l"), (-1, "r")):
        sh = p[f"shoulder_{k}"]
        o = m.objects[f"block_{k}"]
        o.location = sh + Vector((0, 0.020 * sign, 0.030))
        m.objects[f"moss_sh_{k}"].location = sh + Vector((-0.020, 0.030 * sign, 0.074))
    chest = [Vector((s["torso_r"][0] * 1.02, 0.030 - 0.020 * (i % 2), 0.860 - 0.060 * i)) + up for i in range(5)]
    m.set_tube("crack_chest", [tuple(q) for q in chest], [0.006] * 5)
    # tall stone spear upright at the right side, blade up
    hand = p["hand_r"]
    d = Vector((0.10, -0.10, 1.0)).normalized()
    foot, top = hand - d * 0.360, hand + d * 0.600
    m.put_segment("spear", foot, top, 0.020)
    tip = m.objects["tip"]
    tip.location = top + d * 0.060
    tip.rotation_mode = "QUATERNION"
    tip.rotation_quaternion = d.to_track_quat("Z", "Y")
    m.put_segment("band", top - d * 0.010, top + d * 0.010, 0.026)


def assign_depth_parts(m, depth_of):
    return None
