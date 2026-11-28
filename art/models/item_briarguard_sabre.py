"""Briarguard Sabre (Floor 1 rare Vanguard weapon): item icon, art/ITEM_RULES.md.

  Silhouette: the blade is ONE giant hooked thorn, wide at the guard, its point hooking back like a rose thorn, on a grip of
              twisted root: no Tibia sword has a thorn for a blade (rule I0). A fan of three leaves is the guard.
  Colours:    deep red-brown thorn with a pale bone-green honed edge, dark root grip, green leaves, one bright accent:
              a red rosehip pommel.
  Details:    a raised spine down the thorn, briar coiled round the grip, two small thorn quillons, the hip's dark tip.
Look-alike checked: Tibia's sabre (3273) and its other curved swords are steel blades with metal guards; ours has
no metal at all.
"""
from __future__ import annotations

import math

from item_kit import *  # noqa: F401,F403
from item_kit import curve_outline, place, slab, set_tube_pts, BANDS, LIGHT

NAME = "item_briarguard_sabre"
PALETTE = NAME
SIZE = 0.98
PARTS = ["none", "blade", "edge", "grip", "coil", "leaf", "quillon", "hip", "hiptip"]
PIXEL_RULES = {
    "weight": {"edge": 2.5, "coil": 2.5, "quillon": 3.0, "hip": 3.0, "hiptip": 5.0, "leaf": 2.0},
    "thin": {"edge": 2, "coil": 3, "quillon": 3, "hiptip": 2},
    "soft": [["blade", "edge"], ["grip", "coil"]],
    "no_outline": ["edge", "hiptip"],
    "selout": ["blade"],
    "texture": {"blade": [0.06, 0.08], "grip": [0.10, 0.04]},
    "bands": BANDS,
    "light": LIGHT,
}

A = math.radians(45)
U = (math.cos(A), math.sin(A))
N = (-math.sin(A), math.cos(A))
HILT = -0.24
BLADE = 0.86            # a long blade: at 0.60 against the grip it read as a dagger (Jay, 2026-11-27)
K = 14


def at(s, n=0.0):
    return (U[0] * s + N[0] * n, U[1] * s + N[1] * n)


def thorn():
    """The thorn's spine and half-widths: wide at the guard, tapering to a point that hooks towards the
    lower-right (the hook is the cutting edge)."""
    pts, widths = [], []
    for i in range(K + 1):
        t = i / K
        hook = 0.11 * t ** 3.0                 # the point hooks back towards the top-left, like a rose thorn
        pts.append(at(HILT + BLADE * t, hook))
        w = 0.115 * (1 - t) ** 0.75
        widths.append(max(w, 0.0) if i < K else 0.0)
    return pts, widths


def build(model_cls, facing):
    m = model_cls(facing, PARTS)
    pts, widths = thorn()
    slab(m, "blade", "blade", curve_outline(pts, widths), thickness=0.02, ridge=0.06)
    m.tube("edge", "edge", points=10)
    m.tube("grip", "grip", points=6)
    m.tube("coil", "coil", points=16)
    for i in range(3):
        slab(m, f"leaf{i}", "leaf", curve_outline([(0, 0), (0.05, 0.0), (0.1, 0.0)], [0.0, 0.03, 0.0]),
             thickness=0.008, ridge=0.012)
    for i in range(2):
        m.cone(f"quillon{i}", "quillon", segments=6)
    m.ellipsoid("hip", "hip", radii=(0.05, 0.042, 0.042), segments=14, rings=10)
    m.cone("hiptip", "hiptip", segments=6)
    return m


def pose(m, t):
    o = m.objects
    pts, widths = thorn()
    edge = []
    for i in range(2, 12):                    # the honed edge along the hooked (lower-right) side
        p, w = pts[i], widths[i]
        d = at(0, -1)
        edge.append((p[0] + d[0] * (w - 0.010), p[1] + d[1] * (w - 0.010), 0.024))
    set_tube_pts(m, "edge", edge, [0.011 * (1 - (i / 9) * 0.6) for i in range(10)])
    grip = [(*at(HILT - 0.045 * i, 0.008 * math.sin(i * 1.9)), 0.035) for i in range(6)]
    set_tube_pts(m, "grip", grip, [0.030, 0.028, 0.026, 0.026, 0.028, 0.03])
    coil = []
    for i in range(16):
        u = i / 15
        s = HILT - 0.03 - 0.19 * u
        a = u * 3.2 * 2 * math.pi
        coil.append((*at(s, 0.032 * math.cos(a)), 0.035 + 0.03 * math.sin(a)))
    set_tube_pts(m, "coil", coil, 0.008)
    for i, ang in enumerate((90, 135, 180)):  # leaves fanning back from the guard on the blade's back side
        c = at(HILT + 0.01, 0.07)
        place(o[f"leaf{i}"], (c[0], c[1], 0.05), (0, 0, ang), scale=(1.0, 1.0, 1))
    for i, side in enumerate((1, -1)):
        b = at(HILT, side * 0.07)
        tip = at(HILT - 0.06, side * 0.13)
        m.put_segment(f"quillon{i}", (b[0], b[1], 0.04), (tip[0], tip[1], 0.045), 0.016)
    p = at(HILT - 0.29)
    place(o["hip"], (p[0], p[1], 0.045), (0, 0, 45))
    q = at(HILT - 0.35)
    m.put_segment("hiptip", (p[0] - 0.02, p[1] - 0.02, 0.05), (q[0], q[1], 0.06), 0.018)
