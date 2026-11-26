"""Vault Wraith (Floor 1 vault guardian, undead): model + hover cycle.

gen_monsters.py: undead, 6,500 health, energy bolts from range 3, weak to holy. Until now it borrowed Tibia look 152
(a person's outfit). A money monster (ART_REQUESTS.md Batch 11).

Identity (art/CRAWLER_RULES.md step 1):
  Coat:      a spectral violet shroud trailing into ragged tatters, no legs (Tibia's Ghost is white and smoky).
  Signature: a deep hood with two amber eyes burning in the dark, and a ghostly chain binding its wrist to a floating
             iron strongbox banded with gold, with three gold coins circling it: a wraith that cannot leave its treasure.
  Attitude:  hovering, hunched over the strongbox, both clawed hands reaching forward; it bobs, the tatters stream back.

Detail (art/DETAIL_RULES.md): a hood with a rim, a black face hollow, tatters as separate tapering strips (never one
cone), two-part arms with long pale claws, the box's gold bands and lock, chain links, coins.
"""
from __future__ import annotations

import math

from mathutils import Euler, Vector

NAME = "vault_wraith"
WALK_FRAMES = 8
PALETTE = "vault_wraith"
HEIGHT_SHEAR = 0.30
LEAN = 10.0
REFERENCE = "look_48.png"     # Tibia's Ghost (comparison only, never shipped)
SIZE = 2.0
GROUND_STRETCH = 0.7
AUTO_PLACE = (1, 1)
SIGNATURE = ["hood", "box"]     # the chain is a detail: too thin to promise from every side
HEAD_PARTS = ["hood", "face", "eye"]
LEG_PARTS = []                # it floats
CHECK = {"size": (1.10, 1.80), "eye": 1}      # an elite: bigger than a common ghost

PARTS = ["none", "shroud", "hood", "face", "eye", "claw", "box", "gold", "chain", "coin"]
PIXEL_RULES = {
    "weight": {"eye": 9.0, "claw": 3.0, "gold": 3.0, "coin": 4.0, "chain": 2.6, "face": 2.0, "hood": 1.4},
    "thin": {"eye": 2, "claw": 2, "gold": 2, "coin": 2, "chain": 2},
    "soft": [["hood", "face", "eye"], ["box", "gold"], ["shroud", "hood"]],
    "no_outline": [],
    "fur": [],
    "texture": {"shroud": [0.7, 0.35], "hood": [0.5, 0.2], "box": [0.4, 0.2]},
    "bands": [0.40, 0.52, 0.62, 0.71, 0.80, 0.88, 0.95],
    "selout": ["shroud", "hood", "box"],
}
TATTERS = 7
COINS = 3


def build(model_cls, facing):
    m = model_cls(facing, PARTS)
    m.ellipsoid("chest", "shroud", radii=(0.110, 0.130, 0.130), segments=16, rings=10)
    m.ellipsoid("hood", "hood", radii=(0.100, 0.095, 0.105), segments=16, rings=10)
    m.ellipsoid("hoodrim", "hood", radii=(0.040, 0.090, 0.095), segments=14, rings=8)
    m.ellipsoid("face", "face", radii=(0.040, 0.060, 0.065), segments=12, rings=8)
    for k in ("l", "r"):
        m.ellipsoid(f"eye_{k}", "eye", radii=(0.014, 0.014, 0.012), segments=8, rings=6)
        m.capsule(f"upper_{k}", "shroud", segments=8)
        m.capsule(f"fore_{k}", "shroud", segments=8)
        for j in range(3):
            m.cone(f"claw_{k}{j}", "claw", segments=5)
    for i in range(TATTERS):
        m.cone(f"tatter{i}", "shroud", segments=6)
    m.box("box", "box", size=(0.180, 0.140, 0.120))
    for i in range(2):
        m.box(f"band{i}", "gold", size=(0.030, 0.150, 0.128))
    m.box("lock", "gold", size=(0.020, 0.040, 0.040))
    m.tube("chain", "chain", points=7)
    for i in range(COINS):
        m.ellipsoid(f"coin{i}", "coin", radii=(0.024, 0.024, 0.008), segments=10, rings=6)
    return m


def pose(m, t):
    a = 0.0 if t is None else 2 * math.pi * t
    walking = t is not None
    bob = 0.030 * math.sin(a) if walking else 0.0
    hover = Vector((0, 0, 0.300 + bob))                          # floats well above the floor
    chest = hover + Vector((0.000, 0, 0.040))
    m.objects["chest"].location = chest
    head = chest + Vector((0.080, 0, 0.150))                     # hunched forward over the box
    m.objects["hood"].location = head
    m.objects["hoodrim"].location = head + Vector((0.070, 0, 0.000))
    m.objects["face"].location = head + Vector((0.085, 0, -0.010))
    for sign, k in ((1, "l"), (-1, "r")):
        m.objects[f"eye_{k}"].location = head + Vector((0.112, 0.024 * sign, 0.000))
        sh = chest + Vector((0.040, 0.110 * sign, 0.080))
        reach = 0.020 * math.sin(a * 2 + (0 if k == "l" else math.pi)) if walking else 0.0
        el = sh + Vector((0.080 + reach, 0.040 * sign, -0.080))
        hand = el + Vector((0.120 + reach, -0.010 * sign, -0.020))
        m.put_segment(f"upper_{k}", sh, el, 0.040, 0.032)
        m.put_segment(f"fore_{k}", el, hand, 0.032, 0.024)
        for j in range(3):                                       # long pale claws reaching forward
            off = Vector((0, (j - 1) * 0.020, 0))
            m.put_segment(f"claw_{k}{j}", hand + off, hand + off + Vector((0.070, (j - 1) * 0.012, -0.030)), 0.010, 0.002)
    # ragged tatters streaming back and down from the shroud, waving as it drifts
    for i in range(TATTERS):
        ang = -1.3 + 2.6 * i / (TATTERS - 1)
        root = chest + Vector((-0.020, math.sin(ang) * 0.110, -0.090))
        wave = 0.030 * math.sin(a * 2 + i * 0.9) if walking else 0.0
        tip = root + Vector((-0.150 - 0.030 * (i % 2), math.sin(ang) * 0.040, -0.180 + wave))
        m.put_segment(f"tatter{i}", root, tip, 0.050 - 0.008 * (i % 2), 0.004)
    # the strongbox floating below and in front, banded with gold, the chain from its wrist
    box = hover + Vector((0.200, -0.020, -0.200 + 0.5 * bob))
    b = m.objects["box"]
    b.location = box
    b.rotation_mode = "XYZ"
    b.rotation_euler = Euler((0, 0, 0.35))
    for i, x in enumerate((-0.050, 0.050)):
        o = m.objects[f"band{i}"]
        o.location = box + Vector((x * math.cos(0.35), x * math.sin(0.35), 0))
        o.rotation_mode = "XYZ"
        o.rotation_euler = Euler((0, 0, 0.35))
    m.objects["lock"].location = box + Vector((0.090 * math.cos(0.35), 0.090 * math.sin(0.35) + 0.0, 0.010))
    m.objects["lock"].rotation_mode = "XYZ"
    m.objects["lock"].rotation_euler = Euler((0, 0, 0.35))
    wrist = chest + Vector((0.160, -0.120, 0.000))
    pts = []
    for i in range(7):
        u = i / 6
        q = wrist.lerp(box + Vector((0, 0, 0.060)), u) + Vector((0, 0, -0.050 * math.sin(math.pi * u)))
        pts.append(tuple(q))
    m.set_tube("chain", pts, [0.018] * 7)
    for i in range(COINS):                                       # gold coins circling the box
        ang = a + i * 2 * math.pi / COINS
        o = m.objects[f"coin{i}"]
        o.location = box + Vector((math.cos(ang) * 0.150, math.sin(ang) * 0.150, 0.040 + 0.020 * math.sin(ang * 2)))
        o.rotation_mode = "XYZ"
        o.rotation_euler = Euler((1.2, 0, ang))


def assign_depth_parts(m, depth_of):
    return None
