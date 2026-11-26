"""Old Tusk (Floor 1 secret boss, hidden in a wallow in the Boar Meadow): a huge four-legged creature built on
art/models/quadruped.py, the Bristle Boar (boar.py) grown ancient.

BESTIARY.md: "a huge boar that charges. Found through a secret." A money monster (ART_REQUESTS.md Batch 11):
veterans should recognise him at a glance as the boar every boar wishes it were.

Identity (art/QUADRUPED_RULES.md step 1):
  Coat:      the boar's charcoal gone grizzled with age, frosted grey along the back and on the muzzle; the ember crest
             burnt down to red roots with pale frosted tips (Tibia's boar is orange-brown; ours stays dark).
  Signature: ONE enormous yellowed tusk sweeping high and out, the other snapped to a stump; three broken arrow shafts
             with faded fletchings standing out of his back (hunters who failed).
  Attitude:  an old brute about to charge: the boar's low head and tall hump, heavier everywhere, twice the size.

Detail (art/DETAIL_RULES.md): grizzled frost patches on the back and muzzle (big marks), the crest and pale snout disc
(medium), arrow shafts and fletchings, scars, a tusk stump (small); brows in a scowl; real proportion: a boar's
body is about 1.6x as long as it is tall at the hump, the head a third of the body.
"""
from __future__ import annotations

import math

from mathutils import Vector

import quadruped as Q

NAME = "old_tusk"
WALK_FRAMES = 8
PALETTE = "old_tusk"
HEIGHT_SHEAR = 0.30
LEAN = 13.0
REFERENCE = "look_380.png"    # Tibia's Boar (comparison only, never shipped)
SIZE = 2.35
GROUND_STRETCH = 0.50
AUTO_PLACE = (1, 1)
SIGNATURE = ["tusk", "shaft", "crest"]
CHECK = {"size": (1.15, 1.90)}          # a secret boss: deliberately far bigger than a normal boar

PARTS = Q.PARTS + ["tusk", "crest", "brow", "frost", "shaft", "fletch", "scar"]
PIXEL_RULES = Q.pixel_rules(
    dark=True,
    bands=[0.38, 0.50, 0.60, 0.69, 0.78, 0.86, 0.93],
    weight={"tusk": 5.0, "crest": 2.4, "nose": 2.0, "brow": 4.0, "frost": 1.4, "shaft": 3.5, "fletch": 4.0, "scar": 4.0},
    thin={"tusk": 2, "crest": 3, "brow": 3, "shaft": 2, "fletch": 2, "scar": 2},
    soft=[["head", "brow", "eye", "frost"], ["body", "frost", "belly"], ["shaft", "fletch"]],
    texture={"crest": [0.5, 0.0], "frost": [0.9, 0.3], "body": [0.8, 0.12]},
    selout=["crest"],
)

SPEC = Q.spec(
    hip=(-0.120, 0.255), hip_r=(0.118, 0.124, 0.108),
    chest=(0.045, 0.310), chest_r=(0.150, 0.150, 0.158),          # the hump: tallest point, heavier than the boar
    belly_r=(0.172, 0.106, 0.064), belly_drop=0.078,
    head=(0.222, 0.224), head_r=(0.112, 0.108, 0.094),
    snout_tip=(0.385, 0.170), snout_r=(0.062, 0.054), snout_blunt=True,
    nose_r=(0.020, 0.058, 0.052),
    eye=(0.068, 0.088, 0.044), eye_r=0.016,
    ear_root=(-0.040, 0.070, 0.062), ear_tip=(-0.108, 0.108, 0.108), ear_r=0.029,
    front_x=0.075, hind_x=-0.138, leg_top_z=0.205,
    front_y=0.100, hind_y=0.088, front_feet_y=0.140, hind_feet_y=0.122,
    upper=0.112, lower=0.105, leg_r=0.040, paw_r=(0.040, 0.031, 0.021),
    shoulder_r=(0.070, 0.046, 0.094), haunch_r=(0.068, 0.044, 0.080),
    stride=0.090, lift=0.058, bob=0.012, nod=0.014,
    tail_len=0.140, tail_r=(0.016, 0.020), tail_raise=1.70, tail_curl=0.0, tail_split=0.55,
)
CREST = 9
# (along the back 0..1, sideways, lean back, lean out): three old arrows, where hunters hit him and ran
ARROWS = [(0.30, 0.050, 0.45, 0.30), (0.55, -0.070, 0.20, -0.45), (0.78, 0.030, 0.60, 0.15)]


def build(model_cls, facing):
    m = Q.build(model_cls, facing, SPEC, PARTS)
    m.tube("tusk_l", "tusk", points=7)
    m.cone("stump_r", "tusk", segments=6)
    for i in range(CREST):
        m.cone(f"crest{i}", "crest", segments=6)
    for k in ("l", "r"):
        m.capsule(f"brow_{k}", "brow", segments=6)
        m.ellipsoid(f"frostmuzzle_{k}", "frost", radii=(0.060, 0.040, 0.050), segments=10, rings=6)
    for i in range(3):
        m.ellipsoid(f"frost{i}", "frost", radii=(0.070, 0.050, 0.024), segments=12, rings=6)
        m.capsule(f"shaft{i}", "shaft", segments=6)
        m.cone(f"fletch{i}", "fletch", segments=4)
        m.capsule(f"scar{i}", "scar", segments=6)
    return m


def pose(m, t):
    p = Q.pose(m, t)
    head, chest, hip, tip, a, walking = p["head"], p["chest"], p["hip"], p["snout_tip"], p["a"], p["walking"]
    # the one great tusk: out of the left jaw, sweeping out and high past the snout (shows from every side)
    root = tip + Vector((-0.050, 0.050, -0.034))
    pts, radii = [], []
    for i in range(7):
        u = i / 6
        pts.append(tuple(root + Vector((0.055 * math.sin(u * 1.6), 0.085 * u, 0.175 * u * u))))   # up more than forward
        radii.append(0.026 * (1 - 0.70 * u))
    m.set_tube("tusk_l", pts, radii)
    r = tip + Vector((-0.050, -0.050, -0.034))                    # the right one, snapped off short
    m.put_segment("stump_r", r, r + Vector((0.030, -0.022, 0.026)), 0.022, 0.012)
    for sign, k in ((1, "l"), (-1, "r")):
        eye = m.objects[f"eye_{k}"].location
        m.put_segment(f"brow_{k}", eye + Vector((-0.040, 0.004 * sign, 0.034)), eye + Vector((0.034, -0.010 * sign, 0.014)), 0.014)
        m.objects[f"frostmuzzle_{k}"].location = head + Vector((0.090, 0.060 * sign, -0.030))
    # the crest, burnt down: shorter than the young boar's, red at the root and frosted pale at the tips
    brow = head + Vector((0.020, 0, SPEC["head_r"][2] * 0.92))
    hump = chest + Vector((-0.010, 0, SPEC["chest_r"][2] * 0.97))
    rump = hip + Vector((-0.020, 0, SPEC["hip_r"][2] * 0.95))
    for i in range(CREST):
        u = i / (CREST - 1)
        q = brow.lerp(hump, u / 0.42) if u < 0.42 else hump.lerp(rump, (u - 0.42) / 0.58)
        tall = (0.070 + 0.060 * math.sin(math.pi * min(1.0, u / 0.55) * 0.5)) * (1.0 - 0.55 * max(0.0, u - 0.45) / 0.55)
        tall *= 1.0 if i % 2 else 0.75
        flick = 0.012 * math.sin(a * 2 + i * 0.9) if walking else 0.0
        m.put_segment(f"crest{i}", q - Vector((0, 0, 0.025)), q + Vector((-0.045 - flick, 0.014 * (1 if i % 2 else -1), tall)), 0.032, 0.020)
    # frost (grizzle) patches along the back, either side of the crest
    for i, (u, side) in enumerate(((0.25, 0.060), (0.50, -0.070), (0.75, 0.055))):
        q = hump.lerp(rump, u) if u > 0.42 else brow.lerp(hump, u / 0.42)
        m.objects[f"frost{i}"].location = q + Vector((0, side, -0.030))
    # three old arrows standing out of his back, shafts snapped, faded fletchings
    for i, (u, side, back, out) in enumerate(ARROWS):
        q = hump.lerp(rump, u) + Vector((0, side, -0.020))
        sway = 0.008 * math.sin(a * 2 + i) if walking else 0.0
        end = q + Vector((-0.070 * back + sway, 0.060 * out, 0.120))
        m.put_segment(f"shaft{i}", q, end, 0.009)
        m.put_segment(f"fletch{i}", end - (end - q).normalized() * 0.040, end + (end - q).normalized() * 0.010, 0.020, 0.004)
    # scars raked across the shoulder that faces the camera walking east
    for i in range(3):
        s = chest + Vector((-0.030 + 0.030 * i, -0.130, 0.060))
        m.put_segment(f"scar{i}", s, s + Vector((0.030, -0.006, -0.060)), 0.007)


def assign_depth_parts(m, depth_of):
    Q.assign_depth_parts(m, depth_of)
