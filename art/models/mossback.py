"""Mossback Snapper (Floor 1, Reedmarsh elite): the Reed Snapper (snapper.py) grown old enough for the marsh to
grow on it. Until now it wore the Reed Snapper's sprite with a glow.

Identity (art/CRAWLER_RULES.md step 1):
  Coat:      a peat-brown shell almost hidden under a thick cushion of moss (Tibia's thornback tortoise is tan; our
             Reed Snapper is bog-green plates with slate-blue skin), olive-brown leathery skin, a red eye.
  Signature: lumpy mounds of bright moss over the whole shell, ragged moss strands hanging over the rim, and two
             orange-capped toadstools growing out of the moss; the horn knobs poke through.
  Attitude:  slow and ancient: the snapper's low, wide stance, a heavier shell, the head thrust out.

Detail (art/DETAIL_RULES.md): the snapper's anatomy (plated shell, rim, hooked beak, clawed legs, ridged tail);
big marks: moss mounds; medium: hanging strands and the rim; small: toadstool caps with pale spots, knobs.
"""
from __future__ import annotations

import math

from mathutils import Vector

import snapper as S

NAME = "mossback"
WALK_FRAMES = 8
PALETTE = "mossback"
HEIGHT_SHEAR = 0.30
LEAN = 10.0
REFERENCE = "look_198.png"   # Tibia's Thornback Tortoise (comparison only)
SIZE = 2.12
GROUND_STRETCH = 1.0
AUTO_PLACE = (1, 1)
SIGNATURE = ["moss"]
HEAD_PARTS = ["head", "beak", "eye"]
LEG_PARTS = ["leg", "claw"]
PIXEL_RULES = {
    **S.PIXEL_RULES,
    "weight": {**S.PIXEL_RULES["weight"], "moss": 1.8, "drape": 2.4, "cap": 4.0, "stem": 3.0, "spot": 6.0},
    "thin": {**S.PIXEL_RULES["thin"], "drape": 2, "cap": 2, "stem": 2, "spot": 1},
    "soft": S.PIXEL_RULES["soft"] + [["moss", "drape", "shell"], ["cap", "spot"]],
    "texture": {**S.PIXEL_RULES["texture"], "moss": [1.2, 0.5], "drape": [0.6, 0.2]},
    "selout": S.PIXEL_RULES["selout"] + ["moss"],
}

PARTS = S.PARTS + ["moss", "drape", "stem", "cap", "spot"]
MOUNDS = [(0.060, 0.000, 0.060), (-0.050, 0.050, 0.056), (-0.050, -0.055, 0.058), (0.040, 0.085, 0.048),
          (0.040, -0.088, 0.048), (-0.120, 0.000, 0.052), (-0.010, 0.000, 0.064), (0.120, 0.040, 0.040),
          (0.120, -0.045, 0.040), (-0.115, 0.095, 0.040), (-0.115, -0.100, 0.040)]
DRAPES = [(th, 0.040 + 0.020 * (i % 3)) for i, th in enumerate([0.5, 1.1, 1.7, 2.3, 2.9, 3.5, 4.1, 4.7, 5.3, 5.9])]
SHROOMS = [(-0.070, 0.060, 0.080), (0.010, -0.075, 0.060)]


def build(model_cls, facing):
    S.PARTS = PARTS                       # the base builder reads its module's PARTS
    try:
        m = S.build(model_cls, facing)
    finally:
        S.PARTS = PARTS[:len(PARTS) - 5]
    for i in range(len(MOUNDS)):
        m.ellipsoid(f"moss{i}", "moss", radii=(0.060, 0.052, 0.030), segments=12, rings=8)
    for i in range(len(DRAPES)):
        m.cone(f"drape{i}", "drape", segments=5)
    for i in range(len(SHROOMS)):
        m.capsule(f"stem{i}", "stem", segments=6)
        m.ellipsoid(f"cap{i}", "cap", radii=(0.034, 0.034, 0.016), segments=10, rings=6)
        m.ellipsoid(f"spot{i}", "spot", radii=(0.009, 0.009, 0.005), segments=6, rings=4)
    return m


def pose(m, t):
    S.pose(m, t)
    a = 0.0 if t is None else 2 * math.pi * t
    walking = t is not None
    bob = 0.008 * abs(math.sin(2 * a)) if walking else 0.0
    rock = 0.05 * math.sin(2 * a) if walking else 0.0
    shell = S.SHELL + Vector((0, 0, bob))

    def top(x, y, lift=0.004):
        p = S.on_shell(x, y, lift)
        return shell + Vector((p.x, p.y, p.z + rock * y * 0.6))

    for i, (x, y, r) in enumerate(MOUNDS):
        ob = m.objects[f"moss{i}"]
        ob.location = top(x, y, -0.010)
        ob.scale = (r, r * 0.88, 0.028 + 0.006 * (i % 2))   # an ellipsoid's scale is its radii
    # ragged strands hanging over the rim, swinging a little as it waddles
    for i, (th, length) in enumerate(DRAPES):
        root = shell + Vector((S.SHELL_R[0] * 1.02 * math.cos(th), S.SHELL_R[1] * 1.04 * math.sin(th), -0.030))
        sway = 0.010 * math.sin(a + i) if walking else 0.0
        out = Vector((math.cos(th), math.sin(th), 0)) * 0.012
        m.put_segment(f"drape{i}", root, root + out + Vector((sway, 0, -length)), 0.020, 0.006)
    # two toadstools growing out of the moss, orange caps with a pale spot
    for i, (x, y, h) in enumerate(SHROOMS):
        base = top(x, y, 0.010)
        cap = base + Vector((0.006, 0, h))
        m.put_segment(f"stem{i}", base, cap, 0.010)
        m.objects[f"cap{i}"].location = cap + Vector((0, 0, 0.004))
        m.objects[f"spot{i}"].location = cap + Vector((-0.010, 0.006, 0.018))


def assign_depth_parts(m, depth_of):
    return None
