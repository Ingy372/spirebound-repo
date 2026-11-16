"""Meadow wasp (Floor 1, Waspgrass Fields): model + hover cycle.

ART_REQUESTS.md: "a large striped wasp the size of a dog, yellow and black, translucent wings, a long stinger".

Identity (art/CRAWLER_RULES.md step 1):
  Coat:      deep amber-gold and blue-black bands (Tibia's wasp is lemon yellow and brown-black), a russet fuzzy thorax.
  Signature: a long black hooked stinger, big ember-red compound eyes, long glassy wings the body shows through.
  Attitude:  hunting: long abdomen hanging low with the stinger hooked down, wings a blur.

Detail (art/DETAIL_RULES.md): real insect anatomy: head, thorax and abdomen joined by a thin waist; a six-band
abdomen that tapers to a point; long wings that reach past the middle of the abdomen with a dark leading-edge
vein; elbowed antennae; jaws; three pairs of two-part legs, the hind pair trailing.
It flies, so its "walk" is a hover: two wing beats per cycle, the body bobbing and the legs dangling.
"""
from __future__ import annotations

import math

from mathutils import Vector

NAME = "wasp"
WALK_FRAMES = 8
PALETTE = "wasp"
HEIGHT_SHEAR = 0.30
LEAN = 10.0
REFERENCE = "look_44.png"   # Tibia's Wasp, the closest look-alike (comparison only, never shipped)
SIZE = 1.35
GROUND_STRETCH = 1.2
AUTO_PLACE = (1, 1)
SIGNATURE = ["eye", "wing"]       # the stinger is the third signature, but the body hides it from the front
HEAD_PARTS = ["head", "face", "eye"]
LEG_PARTS = ["leg"]
# "the size of a dog", and long wings add to the measured size; a flier's legs dangle thin
CHECK = {"size": (0.85, 1.75), "legs_side": 0.02, "legs_updown": 0.0, "head": 0.07}
PIXEL_RULES = {
    "weight": {"eye": 4.5, "stinger": 4.0, "leg": 2.4, "antenna": 3.0, "wing": 0.35, "vein": 0.9, "stripe": 1.2,
               "head": 1.4, "face": 2.0, "waist": 2.0},
    "thin": {"eye": 3, "stinger": 2, "leg": 2, "antenna": 2, "wing": 4, "vein": 3, "waist": 3, "face": 3},
    "soft": [["thorax", "waist"], ["abdomen", "stripe", "waist", "stinger"], ["head", "eye", "face"], ["wing", "vein"]],
    "no_outline": ["antenna"],
    "fur": ["thorax"],
    "selout": ["abdomen", "thorax"],
    "texture": {"thorax": [1.2, 0.2], "abdomen": [0.4, 0.1], "stripe": [0.3, 0.0], "head": [0.5, 0.0], "wing": [0.5, 0.3]},
    "bands": [0.34, 0.45, 0.55, 0.64, 0.73, 0.82, 0.90],
}

PARTS = ["none", "thorax", "abdomen", "stripe", "head", "face", "eye", "stinger", "wing", "leg", "antenna",
         "vein", "waist"]

FLY_Z = 0.30                       # hovering height of the body
SEGS = 6                           # abdomen bands
# (length, width, sweep back in radians, hinge x) for the fore and hind wing
WINGS = {"f": (0.300, 0.062, 0.95, 0.020), "b": (0.215, 0.052, 1.22, -0.020)}
# legs: (hip x, knee offset, foot offset) for front, middle, hind
LEGS = [(0.045, (0.050, 0.070, -0.030), (0.085, 0.085, -0.135)),
        (0.000, (0.000, 0.085, -0.030), (-0.010, 0.105, -0.150)),
        (-0.040, (-0.070, 0.075, -0.010), (-0.170, 0.090, -0.150))]


def build(model_cls, facing):
    m = model_cls(facing, PARTS)
    m.ellipsoid("thorax", "thorax", radii=(0.080, 0.070, 0.070))
    m.ellipsoid("head", "head", radii=(0.058, 0.072, 0.062))
    m.ellipsoid("face", "face", radii=(0.026, 0.044, 0.040), segments=10, rings=8)
    m.capsule("waist", "waist", segments=8)
    for k in ("l", "r"):
        m.ellipsoid(f"eye_{k}", "eye", radii=(0.034, 0.024, 0.042), segments=10, rings=8)
        m.tube(f"antenna_{k}", "antenna", points=5)
        m.cone(f"jaw_{k}", "face", segments=5)
    for i in range(SEGS):
        m.ellipsoid(f"seg{i}", "abdomen" if i % 2 == 0 else "stripe", radii=(0.040, 0.075, 0.068))
    m.cone("stinger", "stinger", segments=8)
    for k in ("l", "r"):
        for w in WINGS:
            m.ellipsoid(f"wing_{w}{k}", "wing", radii=(0.1, 0.03, 0.005), segments=16, rings=6)
            m.tube(f"vein_{w}{k}", "vein", points=4)
        for j in range(3):
            m.capsule(f"femur{j}_{k}", "leg", segments=6)
            m.capsule(f"tibia{j}_{k}", "leg", segments=6)
    return m


def pose(m, t):
    a = 0.0 if t is None else 2 * math.pi * t
    hover = t is not None
    bob = 0.025 * math.sin(a) if hover else 0.0
    beat = math.sin(2 * a) if hover else 0.15              # two wing beats per cycle
    tilt = 0.10 * math.cos(a) if hover else 0.0            # the abdomen swings a little
    thorax = Vector((0.10, 0, FLY_Z + bob))
    m.objects["thorax"].location = thorax
    head = thorax + Vector((0.118, 0, 0.004))
    m.objects["head"].location = head
    m.objects["face"].location = head + Vector((0.040, 0, -0.012))
    for s, k in ((1, "l"), (-1, "r")):
        m.objects[f"eye_{k}"].location = head + Vector((0.014, 0.056 * s, 0.012))
        m.put_segment(f"jaw_{k}", head + Vector((0.052, 0.022 * s, -0.030)), head + Vector((0.070, 0.004 * s, -0.072)), 0.012)
        base = head + Vector((0.028, 0.024 * s, 0.050))
        elbow = base + Vector((0.020, 0.016 * s, 0.050))
        sway = 0.010 * math.sin(a + s) if hover else 0.0
        pts = [base, elbow, elbow + Vector((0.050, 0.014 * s, 0.012 + sway)), elbow + Vector((0.095, 0.022 * s, -0.012 + sway)),
               elbow + Vector((0.130, 0.026 * s, -0.045 + sway))]
        m.set_tube(f"antenna_{k}", [tuple(p) for p in pts], [0.007, 0.007, 0.006, 0.006, 0.005])
    # a thin waist, then six bands swelling and tapering to the stinger, hanging back and down
    waist = thorax + Vector((-0.072, 0, -0.008))
    first = waist + Vector((-0.075, 0, -0.026))
    m.put_segment("waist", waist, first, 0.020)
    p = first
    for i in range(SEGS):
        u = i / (SEGS - 1)
        r = 0.030 + 0.062 * math.sin(math.pi * (0.18 + 0.80 * u)) ** 0.8
        seg = m.objects[f"seg{i}"]
        seg.location = p
        seg.scale = (0.044, r, r * 0.92)
        drop = 0.022 + 0.016 * u + tilt * 0.05
        p = p + Vector((-0.058 + 0.012 * u, 0, -drop))
    m.put_segment("stinger", p + Vector((0.030, 0, 0.012)), p + Vector((-0.070, 0, -0.085)), 0.024)
    # wings: hinged on top of the thorax, swept back over the abdomen, beating up and down
    for s, k in ((1, "l"), (-1, "r")):
        for w, (length, width, sweep, hx) in WINGS.items():
            ang = 0.30 + 0.70 * beat
            d = Vector((-math.sin(sweep), s * math.cos(sweep) * math.cos(ang), math.sin(ang) * math.cos(sweep) + 0.05)).normalized()
            hinge = thorax + Vector((hx, 0.030 * s, 0.058))
            wing = m.objects[f"wing_{w}{k}"]
            wing.location = hinge + d * (length * 0.52)
            wing.rotation_mode = "QUATERNION"
            wing.rotation_quaternion = d.to_track_quat("X", "Z")
            wing.scale = (length * 0.5, width, 0.005)
            lead = Vector((0, 0, 1)).cross(d).normalized() * (width * 0.55 * s)      # the front edge of the wing
            vpts = [hinge + d * (length * f) + lead * g for f, g in ((0.0, 0.2), (0.35, 0.95), (0.70, 0.90), (0.98, 0.25))]
            m.set_tube(f"vein_{w}{k}", [tuple(v) for v in vpts], [0.008, 0.007, 0.006, 0.005])
        # legs: two parts each, dangling; the hind pair trails back
        for j, (hx, knee_o, foot_o) in enumerate(LEGS):
            hip = thorax + Vector((hx, 0.036 * s, -0.050))
            swing = 0.020 * math.sin(a + j * 1.2) if hover else 0.0
            knee = hip + Vector((knee_o[0], knee_o[1] * s, knee_o[2]))
            foot = hip + Vector((foot_o[0] + swing, foot_o[1] * s, foot_o[2]))
            m.put_segment(f"femur{j}_{k}", hip, knee, 0.012)
            m.put_segment(f"tibia{j}_{k}", knee, foot, 0.009)


def assign_depth_parts(m, depth_of):
    return None
