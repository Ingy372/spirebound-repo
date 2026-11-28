"""Copsewood Bow (Floor 1 weapon): item icon, art/ITEM_RULES.md.

  Silhouette: a short hunting bow lying diagonally, limbs bowing towards the top-left, string straight across:
              the classic bow shape players recognise at a glance.
  Colours:    pale birch-white limbs with dark knots, a dark leather grip, one green accent (the string and a
              sprig of leaves growing at each tip: a bow cut from a living copse).
  Details:    thick limbs that taper to the tips, gold-capped nocks, leather grip wrap, knots in the bark.
Look-alike: Tibia's bow (3350): ours is white birch, not brown, with leaves and a green string.
"""
from __future__ import annotations

import math

from item_kit import *  # noqa: F401,F403
from item_kit import place, set_tube_pts, BANDS, LIGHT

NAME = "item_copsewood_bow"
PALETTE = NAME
PARTS = ["none", "limb", "knot", "grip", "string", "leaf", "nock"]
PIXEL_RULES = {
    "weight": {"string": 3.0, "knot": 3.0, "leaf": 2.5, "nock": 3.0, "grip": 1.5},
    "thin": {"string": 2, "knot": 3, "nock": 3, "leaf": 3},
    "soft": [["limb", "knot"]],
    "no_outline": ["knot"],
    "selout": ["limb"],
    "texture": {"limb": [0.08, 0.06], "grip": [0.05, 0.0]},
    "bands": BANDS,
    "light": LIGHT,
}

A = math.radians(45)
U = (math.cos(A), math.sin(A))
N = (-math.sin(A), math.cos(A))
HALF = 0.46                     # half the bow's length along the diagonal
BOW = 0.20                      # how far the middle of the limbs bows out (towards the top-left)
K = 13


def at(s, n=0.0):
    return (U[0] * s + N[0] * n, U[1] * s + N[1] * n)


def limb_pts():
    pts = []
    for i in range(K):
        t = i / (K - 1) * 2 - 1                    # -1 .. 1 along the bow
        bend = BOW * (1 - t * t) - 0.03 * t ** 4   # recurved tips flick back a little
        pts.append((*at(HALF * t, bend), 0.035))
    return pts


def build(model_cls, facing):
    m = model_cls(facing, PARTS)
    m.tube("limb", "limb", points=K)
    m.tube("string", "string", points=2)
    m.capsule("grip", "grip", segments=10)
    for i in range(4):
        m.ellipsoid(f"knot{i}", "knot", radii=(0.014, 0.011, 0.006), segments=8, rings=6)
    for i in range(2):
        m.ellipsoid(f"nock{i}", "nock", radii=(0.02, 0.02, 0.02), segments=8, rings=6)
        for j in range(3):
            m.ellipsoid(f"leaf{i}{j}", "leaf", radii=(0.045, 0.02, 0.01), segments=10, rings=6)
    return m


def pose(m, t):
    o = m.objects
    pts = limb_pts()
    radii = [0.016 + 0.020 * (1 - abs(i / (K - 1) * 2 - 1)) ** 0.7 for i in range(K)]
    set_tube_pts(m, "limb", pts, radii)
    a, b = pts[0], pts[-1]
    set_tube_pts(m, "string", [(a[0], a[1], 0.03), (b[0], b[1], 0.03)], 0.0065)
    mid = pts[K // 2]
    d = at(0.075)
    m.put_segment("grip", (mid[0] - d[0], mid[1] - d[1], 0.04), (mid[0] + d[0], mid[1] + d[1], 0.04), 0.032)
    for i, k in enumerate((2, 4, 8, 10)):
        p = pts[k]
        q = at(0, 0.006 * (1 if i % 2 else -1))
        place(o[f"knot{i}"], (p[0] + q[0], p[1] + q[1], 0.035 + radii[k] * 0.9), (0, 0, 45))
    for i, p in enumerate((pts[0], pts[-1])):
        place(o[f"nock{i}"], (p[0], p[1], 0.04))
        sgn = -1 if i == 0 else 1
        for j, (ang, off) in enumerate(((20, 0.035), (75, 0.03), (-30, 0.04))):
            ang_r = math.radians(45 + (180 if i == 0 else 0) + ang)
            c = (p[0] + math.cos(ang_r) * off, p[1] + math.sin(ang_r) * off)
            place(o[f"leaf{i}{j}"], (c[0], c[1], 0.045 + 0.005 * j), (0, 0, math.degrees(ang_r)))
