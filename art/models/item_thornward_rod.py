"""Thornward Rod (Floor 1 healer weapon): item icon, art/ITEM_RULES.md.

  Silhouette: a gnarled wooden rod lying diagonally, a big glowing white flower bud at its head (the eye-catcher,
              like the snake head on Tibia's rods), a green vine spiralling down the shaft.
  Colours:    warm brown wood, green vine and leaves, one bright accent: the pale glowing bud.
  Details:    knobbly shaft (thicker at the head), vine wound three times round it, two leaves cupping the bud,
              thorns on the vine.
Look-alike: Tibia's snakebite rod (3066): ours is a flowering branch, not a snake.
"""
from __future__ import annotations

import math

from item_kit import *  # noqa: F401,F403
from item_kit import place, set_tube_pts, BANDS, LIGHT

NAME = "item_thornward_rod"
PALETTE = NAME
PARTS = ["none", "shaft", "vine", "leaf", "bud", "petal", "thorn", "knob"]
PIXEL_RULES = {
    "weight": {"vine": 2.5, "thorn": 3.0, "leaf": 2.0, "bud": 2.0, "petal": 2.0, "knob": 2.0},
    "thin": {"vine": 3, "thorn": 2},
    "soft": [["bud", "petal"]],
    "no_outline": ["thorn"],
    "selout": ["shaft", "bud", "petal"],
    "texture": {"shaft": [0.10, 0.08]},
    "bands": BANDS,
    "light": LIGHT,
}

A = math.radians(45)
U = (math.cos(A), math.sin(A))
N = (-math.sin(A), math.cos(A))
LO, HI = -0.42, 0.20
K = 9


def at(s, n=0.0):
    return (U[0] * s + N[0] * n, U[1] * s + N[1] * n)


def build(model_cls, facing):
    m = model_cls(facing, PARTS)
    m.tube("shaft", "shaft", points=K)
    m.tube("vine", "vine", points=25)
    for i in range(3):
        m.ellipsoid(f"knob{i}", "knob", radii=(0.03, 0.026, 0.02), segments=10, rings=6)
    for i in range(4):
        m.ellipsoid(f"leaf{i}", "leaf", radii=(0.06, 0.026, 0.012), segments=10, rings=6)
    for i in range(3):
        m.cone(f"thorn{i}", "thorn", segments=6)
    m.ellipsoid("bud", "bud", radii=(0.095, 0.085, 0.07), segments=14, rings=10)
    for i in range(3):
        m.ellipsoid(f"petal{i}", "petal", radii=(0.075, 0.045, 0.035), segments=12, rings=8)
    return m


def pose(m, t):
    o = m.objects
    shaft, radii = [], []
    for i in range(K):
        u = i / (K - 1)
        wob = 0.012 * math.sin(u * 9.0)
        shaft.append((*at(LO + (HI - LO) * u, wob), 0.035))
        radii.append(0.020 + 0.012 * u + 0.004 * math.sin(u * 13))
    set_tube_pts(m, "shaft", shaft, radii)
    vine = []
    for i in range(25):
        u = i / 24
        s = LO + 0.06 + (HI - LO - 0.08) * u
        ang = u * 3 * 2 * math.pi
        r = 0.026 + 0.012 * u
        vine.append((*at(s, r * math.cos(ang)), 0.035 + r * math.sin(ang)))
    set_tube_pts(m, "vine", vine, 0.0095)
    for i, u in enumerate((0.2, 0.45, 0.7)):
        p = at(LO + (HI - LO) * u, 0.02 * (1 if i % 2 else -1))
        place(o[f"knob{i}"], (p[0], p[1], 0.04))
    tip = at(HI + 0.08)
    place(o["bud"], (tip[0], tip[1], 0.07), (0, 0, 45))
    for i, ang in enumerate((45, 105, -15)):
        a = math.radians(ang)
        place(o[f"petal{i}"], (tip[0] + math.cos(a) * 0.04, tip[1] + math.sin(a) * 0.05, 0.09), (0, 0, ang))
    for i, (s, side, ang) in enumerate(((HI - 0.02, 1, 135), (HI - 0.02, -1, -45), (LO + 0.25, 1, 150),
                                        (LO + 0.12, -1, -60))):
        p = at(s, side * 0.05)
        place(o[f"leaf{i}"], (p[0], p[1], 0.06), (0, 0, ang))
    for i, u in enumerate((0.3, 0.55, 0.8)):
        k = int(u * 24)
        p = vine[k]
        q = at(0.0, 0.05 * (1 if i % 2 else -1))
        m.put_segment(f"thorn{i}", p, (p[0] + q[0], p[1] + q[1], p[2] + 0.01), 0.010)
