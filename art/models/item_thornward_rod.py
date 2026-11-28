"""Thornward Rod (Floor 1 rare Mystic weapon): item icon, art/ITEM_RULES.md.

  Silhouette: a shepherd's CROOK grown from vine: the shaft curls over into a hook at the top, and from the hook
              hangs a glowing seed-pod lantern on a short tendril. A hooked top with something hanging from it is a
              shape no Tibia rod has (rule I0); Tibia's rods are straight with a head.
  Colours:    warm brown wood, green vine and leaves, one bright accent: the pale-gold glowing seed pod.
  Details:    vine wound round the shaft, thorns on the vine, leaves at the hook, ribs on the pod, a knotted foot.
Look-alike checked: Tibia's snakebite rod (3066) and the other rods are straight staves topped with a figure.
"""
from __future__ import annotations

import math

from item_kit import *  # noqa: F401,F403
from item_kit import place, set_tube_pts, BANDS, LIGHT

NAME = "item_thornward_rod"
PALETTE = NAME
SIZE = 1.25
PARTS = ["none", "shaft", "vine", "leaf", "pod", "rib", "tendril", "thorn"]
PIXEL_RULES = {
    "weight": {"vine": 2.5, "thorn": 3.0, "leaf": 2.0, "pod": 2.5, "rib": 3.0, "tendril": 3.0},
    "thin": {"vine": 3, "thorn": 2, "tendril": 2, "rib": 2},
    "soft": [["pod", "rib"]],
    "no_outline": ["thorn", "rib"],
    "selout": ["shaft", "pod"],
    "texture": {"shaft": [0.10, 0.08]},
    "bands": BANDS,
    "light": LIGHT,
}

A = math.radians(45)
U = (math.cos(A), math.sin(A))
N = (-math.sin(A), math.cos(A))
LO, HI = -0.44, 0.16
K = 18
HOOK_R = 0.11


def at(s, n=0.0):
    return (U[0] * s + N[0] * n, U[1] * s + N[1] * n)


def shaft_pts():
    """Straight up the diagonal, then curling over clockwise into the hook."""
    pts = []
    n_straight = 9
    for i in range(n_straight):
        u = i / (n_straight - 1)
        pts.append((*at(LO + (HI - LO) * u, 0.008 * math.sin(u * 8)), 0.035))
    centre = at(HI, -HOOK_R)
    for i in range(1, K - n_straight + 1):
        ang = math.radians(135 - 230 * i / (K - n_straight))      # starts on the shaft's line, turns clockwise
        pts.append((centre[0] + math.cos(ang) * HOOK_R, centre[1] + math.sin(ang) * HOOK_R, 0.035))
    return pts, centre


def build(model_cls, facing):
    m = model_cls(facing, PARTS)
    m.tube("shaft", "shaft", points=K)
    m.tube("vine", "vine", points=22)
    for i in range(3):
        m.ellipsoid(f"leaf{i}", "leaf", radii=(0.055, 0.024, 0.012), segments=10, rings=6)
    for i in range(3):
        m.cone(f"thorn{i}", "thorn", segments=6)
    m.tube("tendril", "tendril", points=4)
    m.ellipsoid("pod", "pod", radii=(0.055, 0.055, 0.07), segments=14, rings=10)
    for i in range(3):
        m.ellipsoid(f"rib{i}", "rib", radii=(0.012, 0.05, 0.06), segments=8, rings=8)
    m.ellipsoid("foot", "shaft", radii=(0.035, 0.03, 0.03), segments=10, rings=6)
    return m


def pose(m, t):
    o = m.objects
    pts, centre = shaft_pts()
    radii = [0.022 + 0.004 * math.sin(i * 1.3) - 0.008 * max(0, i - 9) / 9 for i in range(K)]
    set_tube_pts(m, "shaft", pts, radii)
    vine = []
    for i in range(22):
        u = i / 21
        s = LO + 0.05 + (HI - LO - 0.05) * u
        a = u * 3.5 * 2 * math.pi
        r = 0.027
        vine.append((*at(s, r * math.cos(a)), 0.035 + r * math.sin(a)))
    set_tube_pts(m, "vine", vine, 0.009)
    for i, u in enumerate((0.3, 0.55, 0.8)):
        p = vine[int(u * 21)]
        q = at(0.0, 0.045 * (1 if i % 2 else -1))
        m.put_segment(f"thorn{i}", p, (p[0] + q[0], p[1] + q[1], p[2] + 0.01), 0.010)
    end = pts[-1]
    # the tendril drops from the hook's end towards the bottom of the screen, the pod hangs from it
    t1 = (end[0], end[1] - 0.04, 0.04)
    t2 = (end[0] + 0.005, end[1] - 0.08, 0.045)
    pod = (end[0] + 0.005, end[1] - 0.15, 0.06)
    set_tube_pts(m, "tendril", [end, t1, t2, (pod[0], pod[1] + 0.06, 0.05)], 0.007)
    place(o["pod"], pod, (90, 0, 0))
    for i, ang in enumerate((-35, 0, 35)):
        place(o[f"rib{i}"], (pod[0] + 0.03 * math.sin(math.radians(ang)), pod[1], pod[2] + 0.035),
              (90, 0, ang))
    top = pts[11]
    for i, ang in enumerate((100, 160, 40)):
        r = math.radians(ang)
        place(o[f"leaf{i}"], (top[0] + math.cos(r) * 0.05, top[1] + math.sin(r) * 0.05, 0.05), (0, 0, ang))
    f = at(LO - 0.01)
    place(o["foot"], (f[0], f[1], 0.035))
