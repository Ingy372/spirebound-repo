"""Message Bottle (Floor 1 quest item): item icon, art/ITEM_RULES.md.

  Silhouette: a round-bellied bottle lying diagonally, neck to the top-left, cork in: reads as "bottle" from the
              outline, like Tibia's message in a bottle.
  Colours:    green glass, a pale rolled letter seen through it (drawn as a lighter, green-tinted shape on the
              glass: the pipeline has no see-through), one red accent (the wax seal on the cork).
  Details:    a bright highlight down the glass, a lip at the neck, twine round the neck.
Look-alike: Tibia's message in a bottle (5802): ours is green glass, not blue, with a red seal.
"""
from __future__ import annotations

from item_kit import *  # noqa: F401,F403
from item_kit import lathe, place, BANDS, LIGHT

NAME = "item_message_bottle"
PALETTE = NAME
SIZE = 1.3
PARTS = ["none", "glass", "letter", "shine", "cork", "seal", "twine"]
PIXEL_RULES = {
    "weight": {"shine": 4.0, "seal": 3.0, "twine": 2.5, "letter": 1.5},
    "thin": {"shine": 2, "twine": 2},
    "soft": [["glass", "letter", "shine"]],
    "no_outline": ["letter", "shine"],
    "selout": ["glass"],
    "bands": BANDS,
    "light": LIGHT,
}


def build(model_cls, facing):
    m = model_cls(facing, PARTS)
    lathe(m, "glass", "glass", [(0, 0), (0.12, 0), (0.135, 0.04), (0.135, 0.28), (0.10, 0.36), (0.05, 0.42),
                               (0.045, 0.50), (0.055, 0.51), (0.055, 0.53), (0, 0.53)], segments=24)
    lathe(m, "letter", "letter", [(0, 0.06), (0.06, 0.06), (0.06, 0.30), (0, 0.30)], segments=16)
    m.capsule("shine", "shine", segments=8)
    lathe(m, "cork", "cork", [(0, 0.52), (0.045, 0.52), (0.05, 0.58), (0, 0.585)], segments=16)
    m.ellipsoid("seal", "seal", radii=(0.035, 0.05, 0.05), segments=12, rings=8)
    lathe(m, "twine", "twine", [(0, 0.45), (0.054, 0.45), (0.054, 0.47), (0, 0.47)], segments=16)
    return m


def pose(m, t):
    o = m.objects
    base = (0.26, -0.20, 0.14)         # bottom of the bottle, lower-right; neck towards the top-left
    rot = (0, 90, 140)
    for n in ("glass", "cork", "twine"):
        place(o[n], base, rot)
    # the letter shows through the glass: the same axis, lifted to the glass's top surface and flattened
    place(o["letter"], (base[0], base[1], base[2] + 0.075), rot, scale=(1.0, 1.0, 1.0))
    o["letter"].scale = (0.35, 1.0, 1.0)
    import math
    a = math.radians(140)
    u = (math.cos(a), math.sin(a))
    s0 = (base[0] + u[0] * 0.06 - 0.04 * u[1], base[1] + u[1] * 0.06 + 0.04 * u[0], base[2] + 0.12)
    s1 = (base[0] + u[0] * 0.30 - 0.04 * u[1], base[1] + u[1] * 0.30 + 0.04 * u[0], base[2] + 0.12)
    m.put_segment("shine", s0, s1, 0.016)
    tip = (base[0] + u[0] * 0.59, base[1] + u[1] * 0.59, base[2])
    place(o["seal"], tip, (0, 0, 140))
