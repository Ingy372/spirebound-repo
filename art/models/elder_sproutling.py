"""Elder Sproutling (Floor 1, Sproutling Glade ground feature, FD2): a seedling left alone for two minutes grows into
one. Tougher than a sproutling and it heals itself. Model + walk cycle, a plant body of its own (art/CRAWLER_RULES.md),
the approved sproutling (sproutling.py) grown old.

ART_REQUESTS.md: "a bigger, older sproutling with a woody trunk and a crown of leaves".

Identity (art/CRAWLER_RULES.md step 1):
  Coat:      a sage-olive bulb face (the young sproutling is pale spring green) sitting on a grey-brown bark trunk with
             moss patches; deep emerald leaves (bluer and darker than the meadow grass, rule C1).
  Signature: a crown of broad leaves on its head like a little tree, with pale-pink blossoms; twig arms that end in
             leaves; heavy bark brows.
  Attitude:  old and grumpy: slow, heavy, rooted; amber eyes glaring under the brows, a cracked frown, a waddle.

Detail (art/DETAIL_RULES.md): a tree-sapling creature's anatomy: a bark trunk with vertical ridges, a bulb head with
a crack of a mouth, deep-set eyes under bark brows, a crown of leaves with pale midribs, blossoms, two-part twig arms
with leaf hands, gnarled root feet with root toes. Marks: big = the bark trunk against the olive bulb; medium = the
moss patches and the leaf crown; small = the blossoms, the midribs, the eyes.
Real proportion: like a young tree, the trunk is as wide as the crown is tall; the crown spreads a little wider than
the body.
"""
from __future__ import annotations

import math

from mathutils import Euler, Vector

NAME = "elder_sproutling"
WALK_FRAMES = 8
PALETTE = "elder_sproutling"
HEIGHT_SHEAR = 0.30
LEAN = 0.0
REFERENCE = "look_535.png"   # Tibia's Swampling (comparison only, never shipped)
SIZE = 2.20
GROUND_STRETCH = 1.0
AUTO_PLACE = (1, 1)
SIGNATURE = ["leaf", "bark"]
HEAD_PARTS = ["bulb", "eye", "brow", "mouth"]
LEG_PARTS = ["root"]
CHECK = {"legs_side": 0.035, "legs_updown": 0.03}   # stubby root feet under a wide trunk (like a tree stump)

PARTS = ["none", "bulb", "bark", "ridge", "eye", "brow", "mouth", "leaf", "vein", "twig", "root", "moss", "blossom"]
PIXEL_RULES = {
    "weight": {"eye": 9.0, "brow": 3.0, "mouth": 3.0, "ridge": 2.6, "vein": 2.6, "twig": 1.8, "root": 1.8,
               "moss": 1.6, "blossom": 4.5, "leaf": 1.5},
    "thin": {"eye": 2, "brow": 2, "mouth": 2, "ridge": 2, "vein": 2, "twig": 3, "root": 3, "blossom": 2},
    "soft": [["bark", "ridge", "moss"], ["bulb", "eye", "brow", "mouth"], ["leaf", "vein", "blossom"], ["twig", "leaf"]],
    "no_outline": [],
    "fur": [],
    "texture": {"bark": [0.9, 0.35], "bulb": [0.6, 0.15], "leaf": [0.6, 0.15], "moss": [1.0, 0.3], "root": [0.6, 0.2]},
    "bands": [0.34, 0.45, 0.55, 0.64, 0.73, 0.82, 0.90],
    "selout": ["bark", "bulb", "leaf"],
}

CROWN = 7
RIDGES = [(-0.9, 0.9), (-0.35, 1.0), (0.25, 0.95), (0.85, 0.9), (2.4, 0.9), (3.4, 0.9)]   # (angle round the trunk, height)
MOSS = [(0.4, 0.10), (-1.6, 0.16), (2.6, 0.12)]
BLOSSOMS = [(0.6, 0.12), (2.7, 0.10), (-1.9, 0.11)]


def build(model_cls, facing):
    m = model_cls(facing, PARTS)
    m.ellipsoid("trunk", "bark", radii=(0.140, 0.150, 0.130), segments=20, rings=10)
    m.ellipsoid("hip", "bark", radii=(0.150, 0.160, 0.070), segments=18, rings=8)
    m.ellipsoid("bulb", "bulb", radii=(0.120, 0.132, 0.105), segments=20, rings=10)
    m.ellipsoid("collar", "bark", radii=(0.128, 0.140, 0.040), segments=18, rings=6)
    for k in ("l", "r"):
        m.ellipsoid(f"cheek_{k}", "bulb", radii=(0.050, 0.044, 0.042), segments=10, rings=6)
    m.tube("mouth", "mouth", points=6)
    for k in ("l", "r"):
        m.ellipsoid(f"eye_{k}", "eye", radii=(0.022, 0.020, 0.020), segments=8, rings=6)
        m.capsule(f"brow_{k}", "brow", segments=6)
        m.capsule(f"upper_{k}", "twig", segments=8)
        m.capsule(f"fore_{k}", "twig", segments=8)
        m.ellipsoid(f"hand_{k}", "leaf", radii=(0.050, 0.024, 0.012), segments=10, rings=6)
        m.cone(f"finger_{k}", "twig", segments=5)
        m.capsule(f"leg_{k}", "root", segments=8)
        for j in range(3):
            m.cone(f"toe{j}_{k}", "root", segments=5)
    for i in range(len(RIDGES)):
        m.capsule(f"ridge{i}", "ridge", segments=5)
    for i in range(len(MOSS)):
        m.ellipsoid(f"moss{i}", "moss", radii=(0.048, 0.040, 0.020), segments=10, rings=6)
    m.capsule("stem", "twig", segments=6)
    for i in range(CROWN):
        m.ellipsoid(f"leaf{i}", "leaf", radii=(1, 1, 1), segments=12, rings=6)
        m.capsule(f"vein{i}", "vein", segments=4)
    m.ellipsoid("leafcap", "leaf", radii=(0.050, 0.050, 0.040), segments=12, rings=6)
    for i in range(len(BLOSSOMS)):
        m.ellipsoid(f"blossom{i}", "blossom", radii=(0.018, 0.018, 0.014), segments=8, rings=4)
    return m


def pose(m, t):
    a = 0.0 if t is None else 2 * math.pi * t
    walking = t is not None
    hop = 0.016 * abs(math.sin(a)) if walking else 0.0
    rock = 0.09 * math.sin(a) if walking else 0.0          # a heavy waddle
    up = Vector((0, 0, 0.110 + hop))
    trunk = Vector((0, 0, 0.120)) + up
    rot = Euler((rock, 0, 0))

    def at(off):
        v = Vector(off)
        v.rotate(rot)
        return trunk + v

    for name, off in (("trunk", (0, 0, 0)), ("hip", (0, 0, -0.070)), ("bulb", (0.010, 0, 0.165))):
        ob = m.objects[name]
        ob.location = at(off)
        ob.rotation_mode = "XYZ"
        ob.rotation_euler = rot
    bulb = at((0.010, 0, 0.165))
    m.objects["collar"].location = at((0.010, 0, 0.085))
    for s, k in ((1, "l"), (-1, "r")):
        m.objects[f"cheek_{k}"].location = at((0.080, 0.080 * s, 0.140))
    # a cracked frown across the bulb's front, corners turned down
    mouth = [at((0.010 + 0.124 * math.cos(th), 0.136 * math.sin(th), 0.150 - 0.016 * abs(math.sin(th)) * 2.2))
             for th in [-0.55 + 1.1 * i / 5 for i in range(6)]]
    m.set_tube("mouth", [tuple(q) for q in mouth], [0.007] * 6)
    for s, k in ((1, "l"), (-1, "r")):
        eye = at((0.112, 0.052 * s, 0.218))
        m.objects[f"eye_{k}"].location = eye
        m.put_segment(f"brow_{k}", eye + Vector((-0.004, 0.034 * s, 0.026)), eye + Vector((0.012, -0.020 * s, 0.010)), 0.014)
        # twig arms: out from the trunk's sides, elbow, leaf hand; they swing as it waddles
        swing = 0.05 * math.sin(a + (0 if s > 0 else math.pi)) if walking else 0.0
        sh = at((0.000, 0.140 * s, 0.070))
        elbow = sh + Vector((0.030 + swing, 0.090 * s, -0.030))
        hand = elbow + Vector((0.070 + swing, 0.030 * s, -0.050))
        m.put_segment(f"upper_{k}", sh, elbow, 0.020)
        m.put_segment(f"fore_{k}", elbow, hand, 0.015)
        h = m.objects[f"hand_{k}"]
        h.location = hand + Vector((0.030, 0.006 * s, -0.004))
        h.rotation_mode = "XYZ"
        h.rotation_euler = Euler((0.4 * s, 0.5, 0.2 * s))
        m.put_segment(f"finger_{k}", hand, hand + Vector((0.020, 0.040 * s, 0.030)), 0.008, 0.003)
        # gnarled root feet, stepping in turn
        ph = a + (0 if s > 0 else math.pi)
        fx = 0.040 * math.cos(ph) if walking else 0.0
        fz = 0.022 * max(0.0, math.sin(ph)) if walking else 0.0
        hipj = at((0.0, 0.095 * s, -0.110))
        foot = Vector((fx + 0.030, 0.135 * s, 0.018 + fz))
        m.put_segment(f"leg_{k}", hipj, foot, 0.040, 0.032)
        for j in range(3):
            fan = (j - 1) * 0.65 + 0.20 * s
            m.put_segment(f"toe{j}_{k}", foot, foot + Vector((0.065 * math.cos(fan), 0.060 * math.sin(fan), -0.010)), 0.017, 0.005)
    # bark ridges running up the trunk, moss patches on it
    for i, (ang, hgt) in enumerate(RIDGES):
        base = at((0.142 * math.cos(ang), 0.152 * math.sin(ang), -0.080))
        top = at((0.128 * math.cos(ang), 0.138 * math.sin(ang), -0.080 + 0.150 * hgt))
        m.put_segment(f"ridge{i}", base, top, 0.007)
    for i, (ang, z) in enumerate(MOSS):
        ob = m.objects[f"moss{i}"]
        ob.location = at((0.130 * math.cos(ang), 0.140 * math.sin(ang), z - 0.080))
        ob.rotation_mode = "XYZ"
        ob.rotation_euler = Euler((0, 0, ang))
    # the crown: a short stem, then broad leaves fanned round and up like a little tree, swaying as it walks
    top = bulb + Vector((-0.040, 0, 0.115))
    sway = 0.025 * math.sin(a + 0.8) if walking else 0.0
    m.put_segment("stem", bulb + Vector((0, 0, 0.060)), top + Vector((sway, 0, 0.020)), 0.022)
    m.objects["leafcap"].location = top + Vector((sway, 0, 0.030))
    for i in range(CROWN):
        ang = 2 * math.pi * i / CROWN + 0.3
        d = Vector((math.cos(ang), math.sin(ang), 0))
        lift = 0.95 + 0.20 * (i % 2)
        c = top + Vector((sway, 0, 0.030)) + d * 0.060 + Vector((0, 0, 0.050 * lift))
        lf = m.objects[f"leaf{i}"]
        lf.location = c
        lf.rotation_mode = "XYZ"
        lf.rotation_euler = Euler((0, -lift, ang))
        lf.scale = (0.085, 0.036, 0.013)
        m.put_segment(f"vein{i}", c - d * 0.040 - Vector((0, 0, 0.040)), c + d * 0.040 + Vector((0, 0, 0.060)), 0.005)
    for i, (ang, r) in enumerate(BLOSSOMS):
        m.objects[f"blossom{i}"].location = top + Vector((sway + r * 0.7 * math.cos(ang), r * 0.7 * math.sin(ang), 0.115))


def assign_depth_parts(m, depth_of):
    return None
