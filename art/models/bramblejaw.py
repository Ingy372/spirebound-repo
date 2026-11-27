"""Bramblejaw (Floor 1, the Proving's one-person boss): a new character's first fight with its new spells, a slow bite
and a telegraphed stomp. "SNORT! Bramblejaw paws the ground." A four-legged creature built on art/models/quadruped.py.

ART_REQUESTS.md (art batch, 2026-11-25): "an old, scarred yard boar with brambles tangled in its bristles and a torn ear;
bigger and shaggier than the Bristle Boar so it reads as boss ... bramble-green and rust colours, the bramble tangle as
the signature".

Identity (art/QUADRUPED_RULES.md step 1):
  Coat:      a deep oxblood-rust coat with a shaggy darker mane over the hump (Tibia's boar is orange-brown; our herd is
             quilled grey-brown, the elite charcoal with an ember crest, Old Tusk grizzled grey).
  Signature: bramble-green thorny vines tangled round its body and through its mane, pale thorns and a few leaves (seen
             from every direction from above); a torn left ear and a pale scar across the snout.
  Attitude:  an old bruiser pawing the ground: head low, mane up, legs planted wide, small tusks forward.

Detail (art/DETAIL_RULES.md): a boar's anatomy (a tall hump, a wedge head, a snout disc, small tusks, small eyes under a
scowl, short legs with hooves); big marks: the mane and the vine loops; medium: the snout and scar; small: the thorns,
leaves and tusk tips. The torn ear is shorter, with a notch.
Real proportion: a boar's body is about 1.6x as long as it is tall at the hump; the head is a third of the body.
"""
from __future__ import annotations

import math

from mathutils import Vector

import quadruped as Q

NAME = "bramblejaw"
WALK_FRAMES = 8
PALETTE = "bramblejaw"
HEIGHT_SHEAR = 0.30
LEAN = 14.0
REFERENCE = "look_380.png"    # Tibia's Boar (comparison only, never shipped)
SIZE = 2.00
GROUND_STRETCH = 1.0
AUTO_PLACE = (1, 1)
SIGNATURE = ["vine", "mane"]
CHECK = {"size": (0.95, 1.35)}   # the Proving's boss: bigger than the herd

PARTS = Q.PARTS + ["mane", "vine", "thorn", "leaf", "tusk", "scar", "brow"]
PIXEL_RULES = Q.pixel_rules(
    dark=True,
    bands=[0.38, 0.50, 0.60, 0.69, 0.78, 0.86, 0.93],
    weight={"vine": 2.6, "thorn": 4.0, "leaf": 3.0, "tusk": 5.0, "scar": 4.0, "brow": 4.0, "mane": 1.8},
    thin={"vine": 2, "thorn": 2, "leaf": 2, "tusk": 2, "scar": 2, "brow": 3},
    soft=[["head", "brow", "eye", "scar"], ["body", "belly", "mane"], ["vine", "thorn", "leaf"]],
    texture={"body": [1.0, 0.35], "head": [0.7, 0.2], "mane": [1.2, 0.4], "vine": [0.4, 0.0]},
    selout=["mane", "vine"],
)
PIXEL_RULES["fur"] = ["body", "head", "mane"]

SPEC = Q.spec(
    hip=(-0.120, 0.250), hip_r=(0.116, 0.116, 0.100),
    chest=(0.050, 0.296), chest_r=(0.146, 0.140, 0.142),
    belly_r=(0.168, 0.104, 0.062), belly_drop=0.076,
    head=(0.215, 0.222), head_r=(0.110, 0.106, 0.092),
    snout_tip=(0.380, 0.172), snout_r=(0.062, 0.054), snout_blunt=True,
    nose_r=(0.020, 0.056, 0.050),
    eye=(0.066, 0.086, 0.042), eye_r=0.013,
    ear_root=(-0.040, 0.066, 0.062), ear_tip=(-0.070, 0.130, 0.140), ear_r=0.033,
    front_x=0.075, hind_x=-0.135, leg_top_z=0.205,
    front_y=0.102, hind_y=0.090, front_feet_y=0.142, hind_feet_y=0.124,
    upper=0.112, lower=0.105, leg_r=0.039, paw_r=(0.040, 0.031, 0.020),
    shoulder_r=(0.068, 0.046, 0.092), haunch_r=(0.068, 0.044, 0.080),
    stride=0.090, lift=0.060, bob=0.012, nod=0.018,
    tail_len=0.120, tail_r=(0.018, 0.030), tail_raise=1.0, tail_curl=0.04, tail_split=0.55,
)
MANE = 13
VINES = [  # (start angle, turns, x from, x to, lift) of each vine loop round the body
    (0.4, 1.0, 0.140, -0.050, 1.00), (2.6, 0.9, -0.010, -0.210, 0.95)]
VINE_N = 10
THORNS = 10
LEAVES = 4


def build(model_cls, facing):
    m = Q.build(model_cls, facing, SPEC, PARTS)
    for i in range(MANE):
        m.cone(f"mane{i}", "mane", segments=6)
    for i in range(len(VINES)):
        m.tube(f"vine{i}", "vine", points=VINE_N)
    m.tube("tangle", "vine", points=7)                  # a loop of bramble caught in the mane
    for i in range(THORNS):
        m.cone(f"thorn{i}", "thorn", segments=5)
    for i in range(LEAVES):
        m.ellipsoid(f"leaf{i}", "leaf", radii=(0.022, 0.012, 0.006), segments=8, rings=4)
    for k in ("l", "r"):
        m.tube(f"tusk_{k}", "tusk", points=5)
        m.capsule(f"brow_{k}", "brow", segments=6)
    m.capsule("scar", "scar", segments=6)
    m.ellipsoid("notch", "body", radii=(0.020, 0.016, 0.020), segments=8, rings=4)   # the bite out of the torn ear
    return m


def _round_body(chest, hip, x, ang, lift):
    """A point on the body's surface at x, `ang` round the barrel (0 = top, +pi/2 = left side)."""
    span = chest.x - hip.x
    u = max(0.0, min(1.0, (x - hip.x) / span))
    c = hip.lerp(chest, u)
    ry = SPEC["hip_r"][1] + (SPEC["chest_r"][1] - SPEC["hip_r"][1]) * u
    rz = SPEC["hip_r"][2] + (SPEC["chest_r"][2] - SPEC["hip_r"][2]) * u
    return Vector((x, ry * math.sin(ang) * lift * 1.04, c.z + rz * math.cos(ang) * lift * 1.04))


def pose(m, t):
    p = Q.pose(m, t)
    head, chest, hip, tip = p["head"], p["chest"], p["hip"], p["snout_tip"]
    # small yellowed tusks, forward and a little up
    for sign, k in ((1, "l"), (-1, "r")):
        root = tip + Vector((-0.050, 0.044 * sign, -0.030))
        pts = [root + Vector((0.050 * u, sign * 0.075 * u, 0.085 * u * u)) for u in (0, 0.25, 0.5, 0.75, 1.0)]
        m.set_tube(f"tusk_{k}", [tuple(q) for q in pts], [0.020, 0.018, 0.015, 0.010, 0.005])
        eye = m.objects[f"eye_{k}"].location
        m.put_segment(f"brow_{k}", eye + Vector((-0.040, 0.004 * sign, 0.034)), eye + Vector((0.034, -0.010 * sign, 0.012)), 0.014)
    # the torn left ear: shorter, with a dark bite taken out of its edge
    e = m.objects["ear_l"]
    e.scale = (e.scale[0], e.scale[1], e.scale[2] * 0.62)
    r1 = SPEC["ear_tip"]
    m.objects["notch"].location = head + Vector((r1[0] * 0.65, r1[1] * 0.80, r1[2] * 0.60))
    # a pale scar across the snout
    m.put_segment("scar", tip + Vector((-0.080, 0.040, 0.050)), tip + Vector((-0.030, -0.030, 0.038)), 0.008)
    # the shaggy mane: dark tufts standing up along the hump, flicking with the stride
    brow = head + Vector((0.000, 0, SPEC["head_r"][2] * 0.90))
    hump = chest + Vector((-0.010, 0, SPEC["chest_r"][2] * 0.97))
    rump = hip + Vector((0.030, 0, SPEC["hip_r"][2] * 0.92))
    for i in range(MANE):
        u = i / (MANE - 1)
        q = brow.lerp(hump, u / 0.40) if u < 0.40 else hump.lerp(rump, (u - 0.40) / 0.60)
        tall = 0.120 * (1.0 - 0.6 * abs(u - 0.38))
        flick = 0.012 * math.sin(p["a"] * 2 + i * 1.1) if p["walking"] else 0.0
        side = 0.022 * (1 if i % 2 else -1)
        m.put_segment(f"mane{i}", q - Vector((0, 0, 0.030)), q + Vector((-0.050 - flick, side, tall)), 0.036, 0.020)
    # bramble vines wound round the barrel, and a loop tangled in the mane; thorns and leaves along them
    vine_pts = []
    for i, (a0, turns, x0, x1, lift) in enumerate(VINES):
        pts = []
        for j in range(VINE_N):
            u = j / (VINE_N - 1)
            ang = a0 + 2 * math.pi * turns * u
            pts.append(_round_body(chest, hip, x0 + (x1 - x0) * u, ang, lift))
        m.set_tube(f"vine{i}", [tuple(q) for q in pts], [0.012] * VINE_N)
        vine_pts += pts
    tangle = [(brow.lerp(hump, 0.6) if u < 0.2 else hump.lerp(rump, (u - 0.2) / 0.8)) +
              Vector((0, 0.030 * math.sin(u * 9.0), 0.030)) for u in [k / 6 for k in range(7)]]
    m.set_tube("tangle", [tuple(q) for q in tangle], [0.011] * 7)
    vine_pts += tangle
    for i in range(THORNS):
        q = vine_pts[(i * 5 + 2) % len(vine_pts)]
        out = (q - Vector((q.x, 0, (chest.z + hip.z) / 2))).normalized()
        m.put_segment(f"thorn{i}", q, q + out * 0.036 + Vector((0, 0, 0.010)), 0.010, 0.002)
    for i in range(LEAVES):
        q = vine_pts[(i * 7 + 4) % len(vine_pts)]
        ob = m.objects[f"leaf{i}"]
        ob.location = q + Vector((0, 0, 0.012))
        ob.rotation_mode = "XYZ"
        ob.rotation_euler = (0.3, 0.2, i * 1.3)


def assign_depth_parts(m, depth_of):
    Q.assign_depth_parts(m, depth_of)
