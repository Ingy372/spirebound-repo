"""Granite Warden (Floor 1, Old Quarry elite on the Upper Cut), built on art/models/humanoid.py: the Ruin Sentinel
(sentinel.py) cut from speckled granite and trimmed in gold, holding the shield wall it is known for
(gen_monsters.py: "The works are closed.", SpireShieldWall). Until now it wore the Ruin Sentinel's look.

Identity (art/OUTFIT_RULES.md step 1):
  Silhouette: the sentinel's blocky guard, plus a tall round-topped granite tower shield on the left arm that covers
              most of its front, spear upright on the right.
  Colours:    warm pink-grey speckled granite (the Ruin Sentinel is cold weathered grey with moss), gold crest, bands,
              belt and shield rim, ochre lichen instead of moss, amber eyes in the visor.
  Details:    a jagged crack across the shield (the "cracked granite shield"), a gold boss, the helm crack and ridge,
              the chest crack, the spear's binding band.
Look-alike: Tibia's Stone Golem and Gargoyle (as the sentinel): ours is a man-shaped shield-bearer, not a lump of rock.
Addons: none (a monster, rule A1).
"""
from __future__ import annotations

from mathutils import Euler, Vector

import humanoid as H
import sentinel as SN

NAME = "granite_warden"
WALK_FRAMES = 8
PALETTE = "granite_warden"
REFERENCE = "outfit_128.png"
PROJECTION = "oblique"
CANVAS_OFFSET = H.CANVAS_OFFSET
SIGNATURE = ["shield", "rim"]
HEAD_PARTS = ["skin", "hair", "strand", "eye", "brow", "nose", "helm", "visor", "crest"]
LEG_PARTS = ["leg_a", "leg_b", "boot_a", "boot_b"]
CHECK = {"size": (0.85, 1.55), "head": 0.08, "legs_side": 0.05, "eye": 1}

PARTS = SN.PARTS + ["shield", "rim"]
PIXEL_RULES = H.pixel_rules(
    weight={**SN.PIXEL_RULES["weight"], "shield": 1.5, "rim": 3.0},
    thin={**SN.PIXEL_RULES["thin"], "rim": 2},
    soft=SN.PIXEL_RULES["soft"][len(H.pixel_rules()["soft"]):] + [["shield", "rim", "crack"]],
    texture={**SN.PIXEL_RULES["texture"], "shield": [0.6, 0.4]},
    selout=["helm", "block", "shield"],
)
SPEC = SN.SPEC


def build(model_cls, facing):
    base_parts = SN.PARTS
    SN.PARTS = PARTS                      # the base builder reads its module's PARTS
    try:
        m = SN.build(model_cls, facing)
    finally:
        SN.PARTS = base_parts
    m.ellipsoid("shield", "shield", radii=(0.150, 0.034, 0.215), segments=18, rings=10)
    m.ellipsoid("shield_rim", "rim", radii=(0.164, 0.014, 0.232), segments=18, rings=10)
    m.ellipsoid("boss", "rim", radii=(0.036, 0.030, 0.036), segments=10, rings=6)
    m.tube("crack_shield", "crack", points=5)
    return m


def _shield_hand(sh, a, walking):
    return sh + Vector((0.120, 0.040, -0.240))


def pose(m, t):
    # the sentinel's pose (helm, visor, crest, cracks, shoulder blocks, spear), with the left hand raised to a shield
    real = H.pose
    H.pose = lambda mm, tt, hands=None: real(mm, tt, hands={**(hands or {}), "l": _shield_hand})
    try:
        SN.pose(m, t)
        p = real(m, t, hands={"l": _shield_hand, "r": SN._spear_hand})
    finally:
        H.pose = real
    hand = p["hand_l"]
    centre = hand + Vector((0.000, 0.060, 0.060))
    rot = Euler((0.0, 0.06, 0.18))
    for name in ("shield_rim", "shield", "boss"):
        o = m.objects[name]
        o.rotation_mode = "XYZ"
        o.rotation_euler = rot
        o.location = centre + (rot.to_matrix() @ Vector((0, 0.034, 0.010)) if name == "boss" else Vector((0, 0, 0)))
    # a jagged crack across the shield's face, from the top rim down past the boss
    mat = rot.to_matrix()
    zig = [(-0.040, 0.180), (0.020, 0.110), (-0.030, 0.050), (0.050, -0.040), (0.010, -0.120)]
    m.set_tube("crack_shield", [tuple(centre + mat @ Vector((x, 0.036, z))) for x, z in zig], [0.007] * 5)


def assign_depth_parts(m, depth_of):
    return None
