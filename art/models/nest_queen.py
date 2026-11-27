"""Nest Queen (Floor 1, Waspgrass Fields ground feature, FD2): she comes out of a wasp nest burnt with a torch, with
her wasps. Model + hover cycle, an insect body of its own (art/CRAWLER_RULES.md), the meadow wasp's (wasp.py) big
mother.

ART_REQUESTS.md: "a long-bodied wasp with a gold-striped abdomen and torn wings".

Identity (art/CRAWLER_RULES.md step 1):
  Coat:      a long honey-gold abdomen ringed with burgundy-black bands (her wasps are amber and blue-black; Tibia's
             wasp is lemon yellow and brown-black), a russet fuzzy thorax.
  Signature: an ivory crown of horn spikes on her head, and smoky amber wings torn into ragged strips; a glowing
             amber drop of venom on the stinger.
  Attitude:  heavy and furious: the egg-heavy abdomen hangs low and curls the stinger forward, the head is raised.

Detail (art/DETAIL_RULES.md): a queen wasp's anatomy: head, thorax and a long abdomen joined by a thin waist; eight
bands tapering to a hooked stinger; torn wings with a dark leading vein; elbowed antennae; jaws; big compound eyes;
three pairs of two-part legs. Marks: big = the burgundy bands; medium = the russet thorax and the wings; small = the
crown spikes and the venom drop.
Real proportion: a queen's abdomen is about twice as long as her thorax and head together; her wings reach only a
little past the middle of it (here torn shorter still).
"""
from __future__ import annotations

import math

from mathutils import Vector

NAME = "nest_queen"
WALK_FRAMES = 8
PALETTE = "nest_queen"
HEIGHT_SHEAR = 0.30
LEAN = 10.0
REFERENCE = "look_44.png"   # Tibia's Wasp (comparison only, never shipped)
SIZE = 1.60
GROUND_STRETCH = 1.0
AUTO_PLACE = (1, 1)
SIGNATURE = ["crown", "wing"]
HEAD_PARTS = ["head", "face", "eye", "crown"]
LEG_PARTS = ["leg"]
# a queen, bigger than the wasps she leads (and long wings add to the measured size); a flier's legs dangle thin
CHECK = {"size": (1.10, 2.30), "legs_side": 0.02, "legs_updown": 0.0, "head": 0.06}
PIXEL_RULES = {
    "weight": {"eye": 4.5, "stinger": 4.0, "leg": 2.4, "antenna": 3.0, "wing": 0.35, "vein": 0.9, "stripe": 1.2,
               "head": 1.4, "face": 2.0, "waist": 2.0, "crown": 4.5, "venom": 6.0},
    "thin": {"eye": 3, "stinger": 2, "leg": 2, "antenna": 2, "wing": 3, "vein": 2, "waist": 3, "face": 3, "crown": 2,
             "venom": 2},
    "soft": [["thorax", "waist"], ["abdomen", "stripe", "waist", "stinger"], ["head", "eye", "face", "crown"],
             ["wing", "vein"]],
    "no_outline": ["antenna", "venom"],
    "fur": ["thorax"],
    "selout": ["abdomen", "thorax"],
    "texture": {"thorax": [1.2, 0.2], "abdomen": [0.4, 0.1], "stripe": [0.3, 0.0], "head": [0.5, 0.0], "wing": [0.6, 0.3]},
    "bands": [0.34, 0.45, 0.55, 0.64, 0.73, 0.82, 0.90],
}

PARTS = ["none", "thorax", "abdomen", "stripe", "head", "face", "eye", "stinger", "wing", "leg", "antenna",
         "vein", "waist", "crown", "venom"]

FLY_Z = 0.30
SEGS = 8
CROWN = 5
# each wing is torn into strips: (length, width, sweep back, hinge x) per strip; the gaps between strips are the tears
STRIPS = {"f": [(0.250, 0.030, 0.88, 0.022), (0.180, 0.026, 1.02, 0.020), (0.120, 0.022, 0.80, 0.024)],
          "b": [(0.170, 0.028, 1.25, -0.020), (0.110, 0.022, 1.40, -0.022)]}
LEGS = [(0.050, (0.055, 0.075, -0.030), (0.090, 0.090, -0.140)),
        (0.000, (0.000, 0.090, -0.030), (-0.010, 0.110, -0.155)),
        (-0.045, (-0.075, 0.080, -0.010), (-0.175, 0.095, -0.150))]


def build(model_cls, facing):
    m = model_cls(facing, PARTS)
    m.ellipsoid("thorax", "thorax", radii=(0.088, 0.078, 0.076))
    m.ellipsoid("head", "head", radii=(0.060, 0.076, 0.064))
    m.ellipsoid("face", "face", radii=(0.026, 0.046, 0.042), segments=10, rings=8)
    m.capsule("waist", "waist", segments=8)
    for k in ("l", "r"):
        m.ellipsoid(f"eye_{k}", "eye", radii=(0.034, 0.024, 0.042), segments=10, rings=8)
        m.tube(f"antenna_{k}", "antenna", points=5)
        m.cone(f"jaw_{k}", "face", segments=5)
    for i in range(CROWN):
        m.cone(f"crown{i}", "crown", segments=6)
    for i in range(SEGS):
        m.ellipsoid(f"seg{i}", "abdomen" if i % 2 == 0 else "stripe", radii=(0.040, 0.075, 0.068))
    m.cone("stinger", "stinger", segments=8)
    m.ellipsoid("venom", "venom", radii=(0.020, 0.020, 0.026), segments=8, rings=6)
    for k in ("l", "r"):
        for w, strips in STRIPS.items():
            for j in range(len(strips)):
                m.ellipsoid(f"wing_{w}{j}{k}", "wing", radii=(0.1, 0.03, 0.005), segments=14, rings=6)
            m.tube(f"vein_{w}{k}", "vein", points=4)
        for j in range(3):
            m.capsule(f"femur{j}_{k}", "leg", segments=6)
            m.capsule(f"tibia{j}_{k}", "leg", segments=6)
    return m


def pose(m, t):
    a = 0.0 if t is None else 2 * math.pi * t
    hover = t is not None
    bob = 0.022 * math.sin(a) if hover else 0.0
    beat = math.sin(2 * a) if hover else 0.15
    curl = 0.08 * math.cos(a) if hover else 0.0
    thorax = Vector((0.14, 0, FLY_Z + bob))
    m.objects["thorax"].location = thorax
    head = thorax + Vector((0.124, 0, 0.022))                  # head raised
    m.objects["head"].location = head
    m.objects["face"].location = head + Vector((0.042, 0, -0.012))
    for i in range(CROWN):
        u = (i - (CROWN - 1) / 2) / ((CROWN - 1) / 2)
        base = head + Vector((-0.010 - 0.012 * abs(u), 0.048 * u, 0.050 - 0.010 * abs(u)))
        m.put_segment(f"crown{i}", base, base + Vector((-0.010, 0.024 * u, 0.085 - 0.025 * abs(u))), 0.017, 0.004)
    for s, k in ((1, "l"), (-1, "r")):
        m.objects[f"eye_{k}"].location = head + Vector((0.016, 0.058 * s, 0.010))
        m.put_segment(f"jaw_{k}", head + Vector((0.054, 0.022 * s, -0.030)), head + Vector((0.074, 0.004 * s, -0.074)), 0.013)
        base = head + Vector((0.030, 0.026 * s, 0.046))
        elbow = base + Vector((0.026, 0.018 * s, 0.040))
        sway = 0.010 * math.sin(a + s) if hover else 0.0
        pts = [base, elbow, elbow + Vector((0.050, 0.016 * s, 0.010 + sway)), elbow + Vector((0.090, 0.024 * s, -0.014 + sway)),
               elbow + Vector((0.120, 0.028 * s, -0.048 + sway))]
        m.set_tube(f"antenna_{k}", [tuple(p) for p in pts], [0.007, 0.007, 0.006, 0.006, 0.005])
    # a thin waist, then eight bands: a long egg-heavy abdomen hanging low, curling the stinger forward
    waist = thorax + Vector((-0.080, 0, -0.010))
    first = waist + Vector((-0.070, 0, -0.024))
    m.put_segment("waist", waist, first, 0.022)
    p = first
    for i in range(SEGS):
        u = i / (SEGS - 1)
        r = 0.032 + 0.068 * math.sin(math.pi * (0.16 + 0.80 * u)) ** 0.7
        seg = m.objects[f"seg{i}"]
        seg.location = p
        seg.scale = (0.042, r, r * 0.90)
        drop = 0.016 + 0.026 * u + curl * 0.04 * u
        p = p + Vector((-0.052 + 0.030 * u * u, 0, -drop))
    tip = p + Vector((0.030, 0, -0.080))                        # the stinger hooks down and forward
    m.put_segment("stinger", p + Vector((-0.010, 0, 0.012)), tip, 0.026)
    m.objects["venom"].location = tip + Vector((0.004, 0, -0.012))
    for s, k in ((1, "l"), (-1, "r")):
        for w, strips in STRIPS.items():
            for j, (length, width, sweep, hx) in enumerate(strips):
                ang = 0.30 + 0.70 * beat + 0.06 * j
                d = Vector((-math.sin(sweep), s * math.cos(sweep) * math.cos(ang), math.sin(ang) * math.cos(sweep) + 0.05)).normalized()
                hinge = thorax + Vector((hx, 0.032 * s, 0.062))
                wing = m.objects[f"wing_{w}{j}{k}"]
                wing.location = hinge + d * (length * 0.52)
                wing.rotation_mode = "QUATERNION"
                wing.rotation_quaternion = d.to_track_quat("X", "Z")
                wing.scale = (length * 0.5, width, 0.005)
                if j == 0:
                    lead = Vector((0, 0, 1)).cross(d).normalized() * (width * 0.55 * s)
                    vpts = [hinge + d * (length * f) + lead * g for f, g in ((0.0, 0.2), (0.35, 0.95), (0.70, 0.90), (0.95, 0.25))]
                    m.set_tube(f"vein_{w}{k}", [tuple(v) for v in vpts], [0.008, 0.007, 0.006, 0.005])
        for j, (hx, knee_o, foot_o) in enumerate(LEGS):
            hip = thorax + Vector((hx, 0.040 * s, -0.055))
            swing = 0.020 * math.sin(a + j * 1.2) if hover else 0.0
            knee = hip + Vector((knee_o[0], knee_o[1] * s, knee_o[2]))
            foot = hip + Vector((foot_o[0] + swing, foot_o[1] * s, foot_o[2]))
            m.put_segment(f"femur{j}_{k}", hip, knee, 0.011)
            m.put_segment(f"tibia{j}_{k}", knee, foot, 0.008)


def assign_depth_parts(m, depth_of):
    return None
