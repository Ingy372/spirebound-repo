"""Briarguard Sabre (Floor 1 weapon): item icon, art/ITEM_RULES.md.

  Silhouette: a curved one-handed sabre lying diagonally, hilt bottom-left, tip top-right (Tibia's weapon pose),
              the blade widening a little before the tip like a falchion, so it reads as "sabre", not "sword".
  Colours:    green-cast steel, dark leather grip, bark-brown briar guard, one red accent (the berry pommel and
              a red gleam on the cutting edge: the "briar" in its name).
  Details:    a raised spine down the blade (lit half / shaded half), a guard of twisted briar with three thorns
              and a leaf, a criss-cross wrapped grip.
Look-alike: Tibia's sabre (3273): ours is greener, curved the other way and wrapped in briar.
"""
from __future__ import annotations

import math

from item_kit import *  # noqa: F401,F403
from item_kit import curve_outline, place, slab, set_tube_pts, BANDS, LIGHT

NAME = "item_briarguard_sabre"
PALETTE = NAME
PARTS = ["none", "blade", "guard", "thorn", "grip", "wrap", "pommel", "leaf"]
PIXEL_RULES = {
    "weight": {"thorn": 3.0, "pommel": 3.0, "wrap": 2.0, "leaf": 2.0},
    "thin": {"thorn": 3, "wrap": 3},
    "soft": [["grip", "wrap"]],
    "no_outline": [],
    "selout": ["blade"],
    "texture": {"guard": [0.10, 0.05], "grip": [0.06, 0.0]},
    "bands": BANDS,
    "light": LIGHT,
}

A = math.radians(45)
U = (math.cos(A), math.sin(A))                 # along the weapon
N = (-math.sin(A), math.cos(A))                # across it (towards the top-left: the blade's back)
HILT = -0.30                                   # where blade meets guard, along U from the tile centre
BLADE = 0.86
SIZE = 0.98


def at(s, n=0.0):
    return (U[0] * s + N[0] * n, U[1] * s + N[1] * n)


def blade_spine(k=12):
    pts, widths = [], []
    for i in range(k + 1):
        t = i / k
        back = 0.13 * t * t                    # curves back towards the blade's spine near the tip
        pts.append(at(HILT + BLADE * t, back))
        w = 0.040 + 0.016 * math.sin(math.pi * min(t / 0.85, 1.0)) if t < 0.9 else 0.044 * (1 - t) / 0.10
        widths.append(max(w, 0.0) if i < k else 0.0)
    return pts, widths


def build(model_cls, facing):
    m = model_cls(facing, PARTS)
    pts, widths = blade_spine()
    slab(m, "blade", "blade", curve_outline(pts, widths), thickness=0.015, ridge=0.05)
    m.tube("guard_a", "guard", points=7)
    m.tube("guard_b", "guard", points=6)
    for i in range(3):
        m.cone(f"thorn{i}", "thorn", segments=6)
    m.capsule("grip", "grip", segments=10)
    for i in range(3):
        m.box(f"wrap{i}", "wrap", size=(0.028, 0.085, 0.03))
    m.ellipsoid("pommel", "pommel", radii=(0.055, 0.055, 0.05), segments=14, rings=10)
    m.ellipsoid("leaf", "leaf", radii=(0.05, 0.022, 0.012), segments=10, rings=6)
    return m


def pose(m, t):
    o = m.objects
    pts, widths = blade_spine()
    # the briar guard: two twisted branches across the hilt
    ga = [(*at(HILT + 0.01 * math.sin(i), -0.20 + 0.066 * i), 0.04 + 0.02 * math.sin(i * 1.7)) for i in range(7)]
    gb = [(*at(HILT - 0.015 + 0.012 * math.cos(i * 1.3), -0.17 + 0.068 * i), 0.05 + 0.02 * math.cos(i * 1.9))
          for i in range(6)]
    set_tube_pts(m, "guard_a", ga, [0.03, 0.036, 0.04, 0.04, 0.036, 0.03, 0.022])
    set_tube_pts(m, "guard_b", gb, [0.016, 0.02, 0.022, 0.022, 0.02, 0.014])
    for i, (s, n, d) in enumerate(((HILT + 0.02, -0.15, (0.5, -1)), (HILT - 0.01, 0.18, (-0.4, 1)),
                                   (HILT + 0.03, 0.02, (1, 0.3)))):
        base = (*at(s, n), 0.05)
        dirv = at(d[0], d[1])
        tip = (base[0] + dirv[0] * 0.07, base[1] + dirv[1] * 0.07, 0.07)
        m.put_segment(f"thorn{i}", base, tip, 0.014)
    # grip and its wrapping
    g0, g1 = at(HILT - 0.02), at(HILT - 0.24)
    m.put_segment("grip", (*g0, 0.035), (*g1, 0.035), 0.028)
    for i in range(3):
        c = at(HILT - 0.06 - 0.055 * i)
        place(o[f"wrap{i}"], (c[0], c[1], 0.045), (0, 0, 45 + (25 if i % 2 else -25)))
    p = at(HILT - 0.285)
    place(o["pommel"], (p[0], p[1], 0.05))
    lf = at(HILT - 0.31, 0.06)
    place(o["leaf"], (lf[0], lf[1], 0.07), (0, 0, 135))
