"""Copsewood Bow (Floor 1 rare Ranger weapon): item icon, art/ITEM_RULES.md.

  Silhouette: a bow that is still a living branch: each limb forks part-way up, the side twig sticking out away
              from the string with leaves on it, and a knotted burl for a grip. The forks break the clean D outline
              every Tibia bow has (rule I0).
  Colours:    pale silver birch with dark knots, a dark burl grip, one green accent: the leaves and a vine string.
  Details:    limbs tapering to curled tips, leaf clusters at each tip and on each fork, a leaf tied on the string.
Look-alike checked: Tibia's bow (3350) and its elven/composite bows are smooth D-shaped limbs; ours branches.
"""
from __future__ import annotations

import math

from item_kit import *  # noqa: F401,F403
from item_kit import place, set_tube_pts, BANDS, LIGHT

NAME = "item_copsewood_bow"
PALETTE = NAME
PARTS = ["none", "limb", "knot", "burl", "string", "leaf", "twig"]
PIXEL_RULES = {
    "weight": {"string": 3.0, "knot": 3.0, "leaf": 2.5, "twig": 2.5, "burl": 1.5},
    "thin": {"string": 2, "knot": 3, "leaf": 3, "twig": 2},
    "soft": [["limb", "knot", "twig"]],
    "no_outline": ["knot"],
    "selout": ["limb", "burl"],
    "texture": {"limb": [0.08, 0.06], "burl": [0.12, 0.08]},
    "bands": BANDS,
    "light": LIGHT,
}

A = math.radians(45)
U = (math.cos(A), math.sin(A))
N = (-math.sin(A), math.cos(A))
HALF = 0.45
BOW = 0.17
K = 15


def at(s, n=0.0):
    return (U[0] * s + N[0] * n, U[1] * s + N[1] * n)


def limb_pts():
    pts = []
    for i in range(K):
        t = i / (K - 1) * 2 - 1
        bend = BOW * (1 - t * t) - 0.05 * t ** 6        # tips curl back towards the string
        pts.append((*at(HALF * t, bend), 0.035))
    return pts


def build(model_cls, facing):
    m = model_cls(facing, PARTS)
    m.tube("limb", "limb", points=K)
    m.tube("string", "string", points=2)
    m.ellipsoid("burl", "burl", radii=(0.07, 0.05, 0.045), segments=14, rings=8)
    for i in range(4):
        m.ellipsoid(f"knot{i}", "knot", radii=(0.014, 0.011, 0.006), segments=8, rings=6)
    for i in range(2):
        m.tube(f"twig{i}", "twig", points=4)
    for i in range(10):
        m.ellipsoid(f"leaf{i}", "leaf", radii=(0.042, 0.019, 0.01), segments=10, rings=6)
    return m


def pose(m, t):
    o = m.objects
    pts = limb_pts()
    radii = [0.013 + 0.018 * (1 - abs(i / (K - 1) * 2 - 1)) ** 0.7 for i in range(K)]
    set_tube_pts(m, "limb", pts, radii)
    a, b = pts[0], pts[-1]
    set_tube_pts(m, "string", [(a[0], a[1], 0.03), (b[0], b[1], 0.03)], 0.0065)
    mid = pts[K // 2]
    place(o["burl"], (mid[0], mid[1], 0.05), (0, 0, 45))
    for i, k in enumerate((3, 5, 9, 11)):
        p = pts[k]
        place(o[f"knot{i}"], (p[0], p[1], 0.035 + radii[k] * 0.9), (0, 0, 45))
    leaves = []
    # a forked twig on each limb, sticking out away from the string (towards the top-left)
    for i, (k, sgn) in enumerate(((4, -1), (10, 1))):
        p = pts[k]
        p1 = (p[0] + at(sgn * 0.04, 0.05)[0], p[1] + at(sgn * 0.04, 0.05)[1], 0.035)
        p2 = (p[0] + at(sgn * 0.07, 0.10)[0], p[1] + at(sgn * 0.07, 0.10)[1], 0.035)
        p3 = (p[0] + at(sgn * 0.11, 0.13)[0], p[1] + at(sgn * 0.11, 0.13)[1], 0.035)
        set_tube_pts(m, f"twig{i}", [p, p1, p2, p3], [0.012, 0.010, 0.008, 0.005])
        leaves += [(p3, 45 + sgn * 60), (p2, 45 + sgn * 100)]
    for i, p in enumerate((pts[0], pts[-1])):
        sgn = -1 if i == 0 else 1
        leaves += [(p, 45 + sgn * 90 + 180 * (i == 0)), (p, 45 + sgn * 30 + 180 * (i == 0)),
                   (pts[1 if i == 0 else -2], 45 + sgn * 140)]
    mids = (pts[0][0] + pts[-1][0]) / 2, (pts[0][1] + pts[-1][1]) / 2
    leaves += [((mids[0], mids[1], 0.03), -45)]
    for i, (p, ang) in enumerate(leaves[:10]):
        r = math.radians(ang)
        c = (p[0] + math.cos(r) * 0.035, p[1] + math.sin(r) * 0.035)
        place(o[f"leaf{i}"], (c[0], c[1], 0.05), (0, 0, ang))
