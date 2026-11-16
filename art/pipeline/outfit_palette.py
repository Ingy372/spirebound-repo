#!/usr/bin/env python3
"""Helpers for outfit palettes: every ramp has 8 tones, built from a dark and a light anchor colour.

  from outfit_palette import ramp, base
  ramps = {**base(hair=((40, 24, 14), (176, 124, 78))), "torso": ramp((40, 46, 58), (226, 232, 240)), ...}

ramp(dark, light, mid=None): 8 tones from dark to light (optionally through a mid colour, for hue shifts:
shadows lean cool/purple, highlights lean warm/yellow, like hand-made pixel art).
base(...): the ramps every humanoid.py figure needs (skin, face, hands, soles), with limbs copied for both sides.
"""
from __future__ import annotations


def ramp(dark, light, mid=None, n=8):
    pts = [dark, mid, light] if mid else [dark, light]
    out = []
    for i in range(n):
        x = i / (n - 1) * (len(pts) - 1)
        k = min(int(x), len(pts) - 2)
        f = x - k
        out.append([round(pts[k][c] + (pts[k + 1][c] - pts[k][c]) * f) for c in range(3)])
    return out


SKIN = ramp((84, 44, 34), (250, 212, 180), (190, 124, 92))


def base(hair, arms, legs, boots, torso, cuff, belt=((40, 24, 14), (150, 102, 60)), buckle=((150, 104, 20), (255, 236, 150)),
         skin=None):
    """All humanoid.py base ramps. Each argument is a (dark, light) or (dark, light, mid) tuple."""
    sk = skin or SKIN
    r = lambda t: ramp(*t)
    return {
        "skin": sk, "hand": sk, "nose": sk[2:] + [sk[-1]] * 2, "eye": [[38, 22, 18]] * 8,
        "brow": [[int(c * 0.7) for c in ramp(*hair)[1]]] * 8,
        "hair": r(hair), "strand": [ramp(*hair)[1]] * 8,
        "torso": r(torso), "arm_a": r(arms), "arm_b": r(arms), "leg_a": r(legs), "leg_b": r(legs),
        "boot_a": r(boots), "boot_b": r(boots), "sole": [[14, 10, 10]] * 8, "cuff": r(cuff),
        "belt": r(belt), "buckle": r(buckle),
    }
