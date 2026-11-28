"""Shrinekeeper's Pendant (Floor 1 amulet): item icon, art/ITEM_RULES.md.

  Silhouette: a round stone medallion on a short loop of chain, the chain coiling up to the top-left: reads as
              "amulet" like Tibia's amulets, which always show their chain.
  Colours:    grey shrine stone, a gold rim and chain, one warm accent: a glowing doorway carved in the stone
              (the shrine's lit door).
  Details:    a raised gold rim, an arched doorway cut into the face with a gold glow inside, chunky chain links.
Size: small on its tile (an amulet, not a shield), like Tibia's amulets.
Look-alike: Tibia's ancient amulet (3025): ours is stone with a glowing door, not a gold torc.
"""
from __future__ import annotations

import math

from item_kit import *  # noqa: F401,F403
from item_kit import lathe, place, torus, BANDS, LIGHT

NAME = "item_shrinekeepers_pendant"
PALETTE = NAME
PARTS = ["none", "stone", "rim", "door", "glow", "chain"]
PIXEL_RULES = {
    "weight": {"glow": 4.0, "door": 2.5, "rim": 2.0, "chain": 2.5},
    "thin": {"glow": 3, "chain": 3, "rim": 3},
    "soft": [["door", "glow"]],
    "no_outline": [],
    "selout": ["stone", "rim"],
    "texture": {"stone": [0.10, 0.10]},
    "bands": BANDS,
    "light": LIGHT,
}
SIZE = 1.35
TILT = 30                      # the medallion leans up towards the viewer, so its face catches the light


def build(model_cls, facing):
    m = model_cls(facing, PARTS)
    lathe(m, "stone", "stone", [(0, 0), (0.17, 0), (0.18, 0.02), (0.17, 0.045), (0, 0.05)], segments=28)
    torus(m, "rim", "rim", major=0.175, minor=0.02, segments=32, rings=8)
    m.box("door", "door", size=(0.13, 0.17, 0.02))
    m.ellipsoid("arch", "door", radii=(0.065, 0.065, 0.012), segments=14, rings=6)
    m.box("glow", "glow", size=(0.09, 0.13, 0.022))
    m.ellipsoid("glowtop", "glow", radii=(0.045, 0.045, 0.013), segments=12, rings=6)
    for i in range(5):
        torus(m, f"link{i}", "chain", major=0.028, minor=0.010, segments=12, rings=6)
    return m


def pose(m, t):
    o = m.objects
    c = (0.03, -0.05, 0.03)
    tilt = (TILT, 0, 0)            # around x: the face turns to the south (towards the viewer)
    place(o["stone"], c, tilt)
    place(o["rim"], (c[0], c[1], c[2] + 0.025), tilt)
    ty = math.sin(math.radians(TILT))
    tz = math.cos(math.radians(TILT))

    def on_face(dx, dy, h):        # a point on the tilted face
        return (c[0] + dx, c[1] + dy * tz - h * ty, c[2] + dy * ty + h * tz)

    place(o["door"], on_face(0, -0.03, 0.05), tilt)
    place(o["arch"], on_face(0, 0.05, 0.05), tilt)
    place(o["glow"], on_face(0, -0.035, 0.056), tilt)
    place(o["glowtop"], on_face(0, 0.025, 0.056), tilt)
    # chain: links going up-left from the top of the medallion, alternating flat and on edge
    top = on_face(0, 0.2, 0.03)
    for i in range(5):
        p = (top[0] - 0.045 * i - 0.01, top[1] + 0.035 * i + 0.02, 0.02 + 0.03 * (1 - i / 4))
        place(o[f"link{i}"], p, (0 if i % 2 else 80, 0, 35))
