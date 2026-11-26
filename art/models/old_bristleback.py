"""Old Bristleback (Floor 1, Boar Meadow elite): a four-legged creature built on art/models/quadruped.py.

Jay, 2026-11-26: "i think old bristleback should be the common npc and the darker with red top boar npc should be the
elite. upgrade the darker and red boar just a little more if possible." So the quill boar (bristleback.py) is now the
common Bristle Boar, and the charcoal boar with the ember crest (boar.py, approved, frozen) becomes the elite, redrawn
here a little grander.

Identity (art/QUADRUPED_RULES.md step 1), the approved boar's, pushed one step further:
  Coat:      the same charcoal-black (Tibia's boar is orange-brown; Old Tusk is grizzled grey).
  Signature: a taller, fuller ember-red crest whose tips glow yellow-hot like coals, ember bristles swept back along
             both cheeks, and heavier ivory tusks; burning red eyes.
  Attitude:  the boar about to charge: low head, tall hump, ears pinned, a little bigger and heavier than the herd.

Detail (art/DETAIL_RULES.md): a boar's anatomy (hump, wedge head, snout disc, tusks, small eyes under a scowl, pinned
ears, short legs); big marks: the crest; medium: the cheek bristles and snout disc; small: the glowing crest tips.
Real proportion: a boar's body is about 1.6x as long as it is tall at the hump, the head a third of the body.
"""
from __future__ import annotations

import math

from mathutils import Vector

import quadruped as Q

NAME = "old_bristleback"
WALK_FRAMES = 8
PALETTE = "old_bristleback"
HEIGHT_SHEAR = 0.30
LEAN = 14.0
REFERENCE = "look_380.png"    # Tibia's Boar (comparison only, never shipped)
SIZE = 2.06
GROUND_STRETCH = 1.0
AUTO_PLACE = (1, 1)
SIGNATURE = ["crest", "tusk"]

PARTS = Q.PARTS + ["tusk", "crest", "ember", "brow"]
PIXEL_RULES = Q.pixel_rules(
    dark=True,
    bands=[0.38, 0.50, 0.60, 0.69, 0.78, 0.86, 0.93],
    weight={"tusk": 5.0, "crest": 2.4, "ember": 4.5, "nose": 2.0, "brow": 4.0},
    thin={"tusk": 2, "crest": 3, "ember": 2, "brow": 3},
    soft=[["head", "brow", "eye"], ["crest", "ember"]],
    texture={"crest": [0.5, 0.0]},
    selout=["crest"],
)

SPEC = Q.spec(
    hip=(-0.120, 0.252), hip_r=(0.114, 0.114, 0.100),
    chest=(0.050, 0.300), chest_r=(0.146, 0.142, 0.146),          # a heavier hump than the herd's
    belly_r=(0.168, 0.102, 0.062), belly_drop=0.076,
    head=(0.218, 0.226), head_r=(0.110, 0.108, 0.094),
    snout_tip=(0.385, 0.170), snout_r=(0.061, 0.053), snout_blunt=True,
    nose_r=(0.020, 0.057, 0.051),
    eye=(0.066, 0.087, 0.042), eye_r=0.017,
    ear_root=(-0.040, 0.068, 0.060), ear_tip=(-0.105, 0.105, 0.110), ear_r=0.028,
    front_x=0.075, hind_x=-0.135, leg_top_z=0.205,
    front_y=0.100, hind_y=0.088, front_feet_y=0.138, hind_feet_y=0.120,
    upper=0.112, lower=0.105, leg_r=0.038, paw_r=(0.039, 0.030, 0.020),
    shoulder_r=(0.068, 0.045, 0.092), haunch_r=(0.067, 0.043, 0.079),
    stride=0.100, lift=0.065, bob=0.012, nod=0.014,
    tail_len=0.150, tail_r=(0.016, 0.020), tail_raise=1.85, tail_curl=0.0, tail_split=0.55,
)
CREST = 12
CHEEK = 3


def build(model_cls, facing):
    m = Q.build(model_cls, facing, SPEC, PARTS)
    for k in ("l", "r"):
        m.tube(f"tusk_{k}", "tusk", points=6)
        m.capsule(f"brow_{k}", "brow", segments=6)
        for i in range(CHEEK):
            m.cone(f"cheek{i}_{k}", "crest", segments=5)
    for i in range(CREST):
        m.cone(f"crest{i}", "crest", segments=6)
        m.cone(f"ember{i}", "ember", segments=5)
    return m


def pose(m, t):
    p = Q.pose(m, t)
    head, chest, hip, tip = p["head"], p["chest"], p["hip"], p["snout_tip"]
    # heavier tusks than the herd's, sweeping out and up past the snout
    for sign, k in ((1, "l"), (-1, "r")):
        root = tip + Vector((-0.050, 0.048 * sign, -0.034))
        pts, radii = [], []
        for i in range(6):
            u = i / 5
            pts.append(tuple(root + Vector((0.080 * math.sin(u * 1.8), sign * (0.076 * u), 0.118 * u * u))))
            radii.append(0.025 * (1 - 0.72 * u))
        m.set_tube(f"tusk_{k}", pts, radii)
        eye = m.objects[f"eye_{k}"].location
        m.put_segment(f"brow_{k}", eye + Vector((-0.040, 0.004 * sign, 0.034)), eye + Vector((0.034, -0.010 * sign, 0.014)), 0.013)
        # ember bristles swept back along the cheek, behind the eye
        for i in range(CHEEK):
            root = head + Vector((-0.010 - 0.030 * i, 0.088 * sign, 0.010 - 0.022 * i))
            m.put_segment(f"cheek{i}_{k}", root, root + Vector((-0.075, 0.032 * sign, 0.020 - 0.010 * i)), 0.020, 0.006)
    # the crest: taller and fuller than the herd's, every spike tipped with a glowing coal
    brow = head + Vector((0.020, 0, SPEC["head_r"][2] * 0.92))
    hump = chest + Vector((-0.010, 0, SPEC["chest_r"][2] * 0.97))
    rump = hip + Vector((-0.020, 0, SPEC["hip_r"][2] * 0.95))
    for i in range(CREST):
        u = i / (CREST - 1)
        q = brow.lerp(hump, u / 0.40) if u < 0.40 else hump.lerp(rump, (u - 0.40) / 0.60)
        tall = (0.095 + 0.090 * math.sin(math.pi * min(1.0, u / 0.55) * 0.5)) * (1.0 - 0.50 * max(0.0, u - 0.45) / 0.55)
        tall *= 1.0 if i % 2 else 0.80
        flick = 0.012 * math.sin(p["a"] * 2 + i * 0.9) if p["walking"] else 0.0
        side = 0.016 * (1 if i % 2 else -1)
        base = q - Vector((0, 0, 0.025))
        d = Vector((-0.050 - flick, side, tall))
        m.put_segment(f"crest{i}", base, base + d * 0.78, 0.033, 0.020)
        m.put_segment(f"ember{i}", base + d * 0.72, base + d, 0.018, 0.004)


def assign_depth_parts(m, depth_of):
    Q.assign_depth_parts(m, depth_of)
