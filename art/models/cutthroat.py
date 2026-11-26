"""Hill Cutthroat (Floor 2, Highrest Highlands camps), built from the approved Road Bandit (frozen).

It wore the shardling's sprite (ART_COUNT.md: wrong body entirely). A highland outlaw who "hurts everyone near with a
war cry" (gen_monsters.py):
  Silhouette: the bandit's body and round hood, but the hood pushed back off the head onto the shoulders and no mask
              (a bare, war-painted face, mouth open in the war cry), a curved long knife in EACH hand held low and out.
  Colours:    sun-faded ochre hood and cape (the road bandit's are mud brown, the crossbowman's olive), a charcoal
              jerkin, a red war-paint stripe under the eyes; bright steel knives.
  Details:    the war-paint stripe, the knives' curve and grips, the hood folded on the shoulders, a bone fetish on a
              cord, the jerkin laces.
Addons: none (a monster, rule A1).
"""
from __future__ import annotations

import math

from mathutils import Vector

import addon_kit as K
import bandit as B
from bandit import WALK_FRAMES, REFERENCE, PROJECTION, CANVAS_OFFSET, SPEC, assign_depth_parts  # noqa: F401

NAME = "cutthroat"
PALETTE = "cutthroat"
# literal values: check_creature.py reads these lines without importing the model
SIGNATURE = ["knife", "cape"]
HEAD_PARTS = ["skin", "hair", "strand", "eye", "brow", "nose", "paint"]
LEG_PARTS = ["leg_a", "leg_b", "boot_a", "boot_b"]
CHECK = {"size": (0.85, 1.45), "head": 0.08, "legs_side": 0.05, "eye": 1}
PARTS = B.PARTS + ["knife", "paint", "fetish"]
PIXEL_RULES = {**B.PIXEL_RULES,
               "weight": {**B.PIXEL_RULES["weight"], "knife": 3.0, "paint": 4.0, "fetish": 4.0},
               "thin": {**B.PIXEL_RULES["thin"], "knife": 2, "paint": 2, "fetish": 2},
               "soft": B.PIXEL_RULES["soft"] + [["skin", "paint"]]}
HIDDEN = ["blade", "guard", "grip", "buckler", "buckler_rim", "boss", "scarf", "tail0", "tail1", "hood", "hood_rim"]


def _knife_r(sh, a, walking):
    swing = 0.05 * math.sin(a) if walking else 0.0
    return sh + Vector((0.120 + swing, -0.080, -0.250))


def _knife_l(sh, a, walking):
    swing = -0.05 * math.sin(a) if walking else 0.0
    return sh + Vector((0.120 + swing, 0.080, -0.250))


B._sword_hand, B._buckler_hand = _knife_r, _knife_l


def build(model_cls, facing):
    m = B.build(model_cls, facing)
    m.parts = PARTS                      # the base parts first, so their numbers do not change
    m.ellipsoid("hood_back", "hood", radii=(0.080, 0.150, 0.060), segments=14, rings=8)   # folded on the shoulders
    m.capsule("paint", "paint")
    m.capsule("fetish_cord", "lace")
    m.ellipsoid("fetish", "fetish", radii=(0.012, 0.010, 0.020), segments=6, rings=4)
    for k in ("l", "r"):
        m.tube(f"knife_{k}", "knife", points=5)
        m.capsule(f"kgrip_{k}", "hilt")
    return m


def pose(m, t):
    B.pose(m, t)
    for name in HIDDEN:
        K.hide(m, name)
    a = K.anchors(m)
    up, head = a["up"], a["head"]
    m.objects["hood_back"].location = Vector((-0.080, 0, 0.900)) + up
    eye_l, eye_r = m.objects["eye_l"].location, m.objects["eye_r"].location
    m.put_segment("paint", eye_r + Vector((0.004, -0.020, -0.022)), eye_l + Vector((0.004, 0.020, -0.022)), 0.010)   # under the eyes, never over them
    m.put_segment("fetish_cord", Vector((0.100, 0.060, 0.880)) + up, Vector((0.112, 0.020, 0.790)) + up, 0.004)
    m.objects["fetish"].location = Vector((0.114, 0.020, 0.778)) + up
    for k, sgn in (("r", -1), ("l", 1)):
        hand = a[f"hand_{k}"]
        fwd = Vector((0.80, 0.30 * sgn, -0.15)).normalized()
        side = Vector((0, 0, 1)).cross(fwd).normalized() * sgn
        pts = [hand + fwd * (0.030 + 0.045 * i) + side * (0.004 * i * i) for i in range(5)]
        m.set_tube(f"knife_{k}", [tuple(p) for p in pts], [0.016, 0.016, 0.014, 0.010, 0.004])
        m.put_segment(f"kgrip_{k}", hand - fwd * 0.030, hand + fwd * 0.028, 0.012)
