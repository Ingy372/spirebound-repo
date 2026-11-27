"""Wolf Companion (the Mystic's level-50 summon, "summon wolf companion", green smoke): a four-legged creature built on
art/models/quadruped.py, wearing the approved meadow wolf's coat pieces (wolf.build_fur / pose_fur) like the grey alpha.
It fights at its Mystic's side, so it must never be mistaken for a wild wolf.

Identity (art/QUADRUPED_RULES.md step 1):
  Coat:      pale silver-sage flanks with a dark slate-teal saddle (Tibia's wolf is plain grey; the meadow wolf tawny
             ochre; the grey alpha teal-silver with a black mane), a cream belly, bib and cheeks.
  Signature: a garland of green leaves round its neck (the Mystic's grove bond, seen from every direction) and jade
             spirit runes glowing on both shoulders; glowing jade eyes.
  Attitude:  a loyal friend, not a hunter: head carried up, ears up, tail raised and swinging, an easy trot.

Detail (art/DETAIL_RULES.md): the wolf's anatomy from the frozen coat (neck ruff, cheek tufts, brows, mouth line, dark ear
tips, the saddle of separate fur tufts, hackles, a bushy tail); on top: the leaf garland (big), the shoulder runes
(medium), the leaf tips and bright eyes (small).
Real proportion: a grey wolf stands about 0.8 m at the shoulder and is about 1.3 m long without the tail; head held up,
the muzzle is level with the back.
"""
from __future__ import annotations

import math

from mathutils import Vector

import quadruped as Q
import wolf

NAME = "wolf_companion"
WALK_FRAMES = 8
PALETTE = "wolf_companion"
HEIGHT_SHEAR = 0.30
LEAN = 14.0
REFERENCE = "look_27.png"     # Tibia's Wolf (comparison only, never shipped)
SIZE = 1.8
GROUND_STRETCH = 1.3
AUTO_PLACE = (1, 1)
SIGNATURE = ["leaf", "saddle"]
CHECK = {"eye": 1}

PARTS = Q.PARTS + wolf.FUR_PARTS + ["leaf", "rune"]
PIXEL_RULES = wolf.fur_rules(weight={"leaf": 3.0, "rune": 6.0}, thin={"leaf": 2, "rune": 2},
                             soft=[["body", "rune"]], selout=["leaf"])
PIXEL_RULES["no_outline"] = ["rune"]

SPEC = Q.spec(
    hip=(-0.105, 0.300), hip_r=(0.115, 0.086, 0.074),
    chest=(0.050, 0.322), chest_r=(0.118, 0.096, 0.094),
    belly_r=(0.150, 0.070, 0.045), belly_drop=0.055,
    head=(0.225, 0.360), head_r=(0.098, 0.086, 0.074),              # head up: a friend, not prowling
    snout_tip=(0.385, 0.335), snout_r=(0.044, 0.030),
    nose_r=(0.018, 0.018, 0.016),
    eye=(0.050, 0.052, 0.036), eye_r=0.011,
    ear_root=(-0.030, 0.046, 0.050), ear_tip=(-0.020, 0.058, 0.150), ear_r=0.028,
    front_x=0.080, hind_x=-0.135, leg_top_z=0.262,
    front_y=0.060, hind_y=0.060, front_feet_y=0.090, hind_feet_y=0.086,
    upper=0.150, lower=0.140, leg_r=0.027, paw_r=(0.030, 0.021, 0.015),
    shoulder_r=(0.054, 0.034, 0.074), haunch_r=(0.064, 0.036, 0.078),
    stride=0.115, lift=0.065, bob=0.012, nod=0.010,
    tail_len=0.240, tail_r=(0.030, 0.020), tail_raise=1.45, tail_curl=0.08, tail_split=0.72,
)
GARLAND = 11


def build(model_cls, facing):
    m = Q.build(model_cls, facing, SPEC, PARTS)
    wolf.build_fur(m)
    for i in range(GARLAND):
        m.ellipsoid(f"leaf{i}", "leaf", radii=(0.036, 0.018, 0.010), segments=8, rings=4)
    for k in ("l", "r"):
        m.tube(f"rune_{k}", "rune", points=6)
    return m


def pose(m, t):
    p = Q.pose(m, t)
    wolf.pose_fur(m, p, SPEC)
    chest, head = p["chest"], p["head"]
    # the leaf garland: a ring of leaves round the neck, tilted like a collar
    neck = chest.lerp(head, 0.48) + Vector((0, 0, 0.006))
    for i in range(GARLAND):
        ang = 2 * math.pi * i / GARLAND
        d = Vector((0.45 * math.cos(ang), math.sin(ang), 0.85 * math.cos(ang)))
        c = neck + Vector((d.x * 0.060, d.y * 0.082, d.z * 0.060 - 0.010))
        ob = m.objects[f"leaf{i}"]
        ob.location = c
        ob.rotation_mode = "XYZ"
        ob.rotation_euler = (0.6 * math.sin(ang), 0.5, ang + 0.8)
    # the jade spirit runes: a small hooked spiral on each shoulder
    for sign, k in ((1, "l"), (-1, "r")):
        c = chest + Vector((-0.010, SPEC["chest_r"][1] * 0.86 * sign, 0.040))
        pts = [c + Vector((0.030 * math.cos(u * 4.4) * (1 - u * 0.5), 0.010 * sign, 0.030 * math.sin(u * 4.4) * (1 - u * 0.5)))
               for u in (0.0, 0.2, 0.4, 0.6, 0.8, 1.0)]
        m.set_tube(f"rune_{k}", [tuple(q) for q in pts], [0.007] * 6)


def assign_depth_parts(m, depth_of):
    Q.assign_depth_parts(m, depth_of)
