"""Brass Spyglass (Floor 1 tool / quest item): item icon, art/ITEM_RULES.md.

  Silhouette: a pulled-out telescope lying diagonally, three brass tubes getting thinner towards the eyepiece
              (bottom-left), a wide lens end (top-right): reads as "spyglass" from the stepped outline alone.
  Colours:    warm brass, a dark leather grip on the widest tube, one cool accent: the pale blue lens.
  Details:    raised rings where each tube slides into the next, stitched leather wrap, a dark eyepiece cup.
Look-alike: Tibia's bejeweled ship's telescope (9616): ours is a plain sailor's spyglass, no jewels, lying down.
"""
from __future__ import annotations

from item_kit import *  # noqa: F401,F403
from item_kit import lathe, place, BANDS, LIGHT

NAME = "item_brass_spyglass"
PALETTE = NAME
PARTS = ["none", "tube", "ring", "leather", "stitch", "lens", "glint", "eyecup"]
PIXEL_RULES = {
    "weight": {"ring": 2.5, "lens": 2.5, "glint": 5.0, "stitch": 3.0, "eyecup": 2.0},
    "thin": {"ring": 3, "glint": 2, "stitch": 2},
    "soft": [["lens", "glint"]],
    "no_outline": ["glint", "stitch"],
    "selout": ["tube"],
    "texture": {"leather": [0.06, 0.03]},
    "bands": BANDS,
    "light": LIGHT,
}

# (start, end, radius) of each tube along the spyglass, from the eyepiece end; the whole thing is 0.92 long
TUBES = [(0.00, 0.22, 0.048), (0.20, 0.44, 0.064), (0.42, 0.92, 0.085)]


def build(model_cls, facing):
    m = model_cls(facing, PARTS)
    for i, (a, b, r) in enumerate(TUBES):
        lathe(m, f"tube{i}", "tube", [(0, a), (r, a), (r, b), (0, b)], segments=20)
    for i, (z, r) in enumerate(((0.20, 0.056), (0.42, 0.074), (0.90, 0.098), (0.60, 0.090))):
        lathe(m, f"ring{i}", "ring", [(0, z - 0.012), (r, z - 0.012), (r, z + 0.012), (0, z + 0.012)], segments=20)
    lathe(m, "leather", "leather", [(0, 0.63), (0.089, 0.63), (0.089, 0.86), (0, 0.86)], segments=20)
    for i in range(3):
        lathe(m, f"stitch{i}", "stitch", [(0, 0.67 + 0.07 * i), (0.0915, 0.67 + 0.07 * i),
                                           (0.0915, 0.682 + 0.07 * i), (0, 0.682 + 0.07 * i)], segments=20)
    lathe(m, "lens", "lens", [(0, 0.922), (0.084, 0.922), (0.07, 0.94), (0, 0.938)], segments=20)
    lathe(m, "eyecup", "eyecup", [(0, -0.03), (0.042, -0.03), (0.05, 0.0), (0, 0.0)], segments=16)
    m.ellipsoid("glint", "glint", radii=(0.012, 0.016, 0.006), segments=8, rings=6)
    return m


def pose(m, t):
    o = m.objects
    import math
    start = (-0.31, -0.31, 0.06)            # the eyepiece end, bottom-left, along the diagonal
    lift = 28                               # the lens end tips up towards the viewer, so the glass shows
    for name in o:
        if name != "glint":
            place(o[name], start, (0, 90 - lift, 45))
    a = math.radians(lift)
    L = 0.94
    end = (start[0] + L * math.cos(a) * 0.7071, start[1] + L * math.cos(a) * 0.7071, start[2] + L * math.sin(a))
    place(o["glint"], (end[0] - 0.02, end[1] + 0.01, end[2] + 0.02), (0, 0, 45))
