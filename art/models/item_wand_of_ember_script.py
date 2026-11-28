"""Wand of Ember Script (Floor 1 caster weapon): item icon, art/ITEM_RULES.md.

  Silhouette: a short straight wand lying diagonally, a big flame bursting from its tip (the eye-catcher, like
              Tibia's fire wands), a metal cap at the butt.
  Colours:    charred black wood, one hot accent: glowing orange runes (the "script") and the flame.
  Details:    a ring of brass at each end, four runes burning into the shaft, a flame of three tongues around a
              white-hot core.
Look-alike: Tibia's wand of inferno (3071): ours is plain charred wood with runes, no ornate head.
"""
from __future__ import annotations

import math

from item_kit import *  # noqa: F401,F403
from item_kit import place, BANDS, LIGHT

NAME = "item_wand_of_ember_script"
PALETTE = NAME
PARTS = ["none", "shaft", "rune", "band", "flame", "core", "cap"]
PIXEL_RULES = {
    "weight": {"rune": 4.0, "core": 4.0, "flame": 2.0, "band": 2.5, "cap": 2.0},
    "thin": {"rune": 2, "core": 3, "band": 3},
    "soft": [["flame", "core"]],
    "no_outline": ["rune", "core"],
    "selout": ["shaft"],
    "texture": {"shaft": [0.10, 0.04]},
    "bands": BANDS,
    "light": LIGHT,
}

A = math.radians(45)
U = (math.cos(A), math.sin(A))
N = (-math.sin(A), math.cos(A))
LO, HI = -0.44, 0.12             # the shaft along the diagonal; the flame takes the rest


def at(s, n=0.0):
    return (U[0] * s + N[0] * n, U[1] * s + N[1] * n)


def build(model_cls, facing):
    m = model_cls(facing, PARTS)
    m.frustum("shaft", "shaft", top_ratio=0.65, segments=12)
    for i in range(4):
        m.box(f"rune{i}", "rune", size=(0.035, 0.012, 0.01))
    for i in range(2):
        m.frustum(f"band{i}", "band", top_ratio=1.0, segments=12)
    m.ellipsoid("cap", "cap", radii=(0.034, 0.034, 0.03), segments=12, rings=8)
    for i in range(3):
        m.cone(f"flame{i}", "flame", segments=10)
    m.ellipsoid("flamebody", "flame", radii=(0.09, 0.08, 0.06), segments=12, rings=8)
    m.ellipsoid("core", "core", radii=(0.05, 0.042, 0.035), segments=10, rings=8)
    return m


def lie(obj, s0, s1, r, z):
    """A frustum lying along the diagonal from s0 to s1 (radius r at s0)."""
    p = at(s0)
    place(obj, (p[0], p[1], z), (0, 90, 45), scale=(r, r, s1 - s0))


def pose(m, t):
    o = m.objects
    lie(o["shaft"], LO, HI, 0.030, 0.032)
    for i in range(4):
        p = at(LO + 0.14 + 0.11 * i, 0.0)
        ang = 45 + (70 if i % 2 else 20)
        place(o[f"rune{i}"], (p[0], p[1], 0.058 - 0.003 * i), (0, 0, ang))
    lie(o["band0"], LO + 0.02, LO + 0.06, 0.033, 0.032)
    lie(o["band1"], HI - 0.04, HI, 0.024, 0.032)
    p = at(LO)
    place(o["cap"], (p[0], p[1], 0.032))
    tip = at(HI + 0.07)
    place(o["flamebody"], (tip[0], tip[1], 0.05), (0, 0, 45))
    place(o["core"], (tip[0] - 0.008, tip[1] - 0.008, 0.075))
    for i, (ang, ln) in enumerate(((45, 0.27), (90, 0.19), (0, 0.18))):
        a = math.radians(ang)
        base = (tip[0], tip[1], 0.05)
        end = (tip[0] + math.cos(a) * ln, tip[1] + math.sin(a) * ln, 0.07)
        m.put_segment(f"flame{i}", base, end, 0.075 - 0.012 * i)
