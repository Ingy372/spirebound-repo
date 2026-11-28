"""Wand of Ember Script (Floor 1 rare Arcanist weapon): item icon, art/ITEM_RULES.md.

  Silhouette: the wand is a tightly ROLLED SHEET OF SCRIPT, bound with brass bands, its tip unrolling into a curl of
              paper whose edge burns: a paper wand, which no Tibia wand is (rule I0); Tibia's are sticks with gems or
              flames.
  Colours:    warm parchment, a glowing orange line of script spiralling round it, brass bands and cap, one hot
              accent: the burning curl and the sparks lifting off it.
  Details:    the paper's spiral seam, three bands, a brass butt cap, three embers rising from the burning end.
Look-alike checked: Tibia's wand of inferno (3071) and the other wands are rods with a head; ours is a scroll.
"""
from __future__ import annotations

import math

from item_kit import *  # noqa: F401,F403
from item_kit import lathe, place, set_tube_pts, BANDS, LIGHT

NAME = "item_wand_of_ember_script"
PALETTE = NAME
SIZE = 1.3
PARTS = ["none", "paper", "script", "band", "curl", "burn", "spark"]
PIXEL_RULES = {
    "weight": {"script": 3.0, "band": 2.5, "burn": 3.5, "spark": 5.0, "curl": 1.5},
    "thin": {"script": 2, "band": 3, "spark": 2, "burn": 2},
    "soft": [["paper", "script"], ["curl", "burn"]],
    "no_outline": ["script", "spark"],
    "selout": ["paper", "curl"],
    "texture": {"paper": [0.05, 0.06]},
    "bands": BANDS,
    "light": LIGHT,
}

A = math.radians(45)
U = (math.cos(A), math.sin(A))
N = (-math.sin(A), math.cos(A))
LO, HI = -0.42, 0.12
R = 0.050


def at(s, n=0.0):
    return (U[0] * s + N[0] * n, U[1] * s + N[1] * n)


def build(model_cls, facing):
    m = model_cls(facing, PARTS)
    L = HI - LO
    lathe(m, "paper", "paper", [(0, 0), (R * 0.9, 0), (R, 0.02), (R * 0.85, L), (0, L)], segments=16)
    m.tube("script", "script", points=30)
    for i in range(3):
        lathe(m, f"band{i}", "band", [(0, 0), (R + 0.008, 0), (R + 0.008, 0.03), (0, 0.03)], segments=16)
    lathe(m, "cap", "band", [(0, -0.03), (R * 0.7, -0.03), (R + 0.01, 0.0), (0, 0.0)], segments=16)
    m.tube("curl", "curl", points=12)
    m.tube("burn", "burn", points=12)
    for i in range(3):
        m.ellipsoid(f"spark{i}", "spark", radii=(1, 1, 1), segments=8, rings=6)
    return m


def pose(m, t):
    o = m.objects
    start = (*at(LO), 0.045)
    place(o["paper"], start, (0, 90, 45))
    L = HI - LO
    for i, s in enumerate((0.05, 0.30, 0.55)):
        place(o[f"band{i}"], (*at(LO + s * L), 0.045), (0, 90, 45))
    place(o["cap"], start, (0, 90, 45))
    sc = []
    for i in range(30):
        u = i / 29
        s = LO + 0.08 * L + 0.88 * L * u
        a = u * 4.5 * 2 * math.pi
        r = R * (1 - 0.15 * u) + 0.003
        sc.append((*at(s, r * math.cos(a)), 0.045 + r * math.sin(a)))
    set_tube_pts(m, "script", sc, 0.0085)
    # the tip unrolls: a curl of paper spiralling out to the top-right, its outer edge burning
    curl, burn = [], []
    for i in range(12):
        u = i / 11
        ang = math.radians(-60 + 300 * u)
        rad = 0.04 + 0.13 * u
        c = at(HI + 0.06)
        x, y = c[0] + math.cos(ang) * rad * 0.8, c[1] + math.sin(ang) * rad * 0.8
        curl.append((x, y, 0.04 + 0.03 * u))
        burn.append((x + 0.004, y + 0.004, 0.05 + 0.03 * u))
    set_tube_pts(m, "curl", curl, [0.042 - 0.018 * (i / 11) for i in range(12)])
    set_tube_pts(m, "burn", burn[5:] + [burn[-1]] * 5, [0.026 - 0.010 * (i / 11) for i in range(12)])
    for i, (dx, dy, r) in enumerate(((0.10, 0.20, 0.022), (0.20, 0.13, 0.017), (0.16, 0.27, 0.013))):
        c = at(HI)
        place(o[f"spark{i}"], (c[0] + dx * 0.9, c[1] + dy * 0.9, 0.09), scale=(r, r, r))
