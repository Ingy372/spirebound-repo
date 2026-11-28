"""Warden's Signet (Floor 1 ring): item icon, art/ITEM_RULES.md.

  Silhouette: a thick gold ring lying tilted towards the viewer, a big square bezel on top holding one stone: a
              small object in the middle of its tile, like Tibia's rings (Grok's signet filled the tile and read
              as a camera).
  Colours:    gold band, one cool accent: a large blue stone.
  Details:    the band thickens into shoulders under the bezel, a raised gold rim round the stone, a glint.
Look-alike: Tibia's signet ring (31592): ours is chunkier with a big blue stone.
"""
from __future__ import annotations

from item_kit import *  # noqa: F401,F403
from item_kit import place, torus, BANDS, LIGHT

NAME = "item_wardens_signet"
PALETTE = NAME
PARTS = ["none", "band", "bezel", "stone", "glint"]
PIXEL_RULES = {
    "weight": {"stone": 3.0, "glint": 5.0, "bezel": 1.5},
    "thin": {"glint": 2},
    "soft": [["band", "bezel"]],
    "no_outline": ["glint"],
    "selout": ["band", "bezel"],
    "bands": BANDS,
    "light": LIGHT,
}
SIZE = 1.3
TILT = 55                      # the ring stands half up, so we see the stone on top and the hole through the band


def build(model_cls, facing):
    m = model_cls(facing, PARTS)
    torus(m, "band", "band", major=0.12, minor=0.032, segments=32, rings=10, squash=0.8)
    m.box("bezel", "bezel", size=(0.15, 0.15, 0.05))
    m.ellipsoid("stone", "stone", radii=(0.066, 0.066, 0.042), segments=14, rings=8)
    m.ellipsoid("glint", "glint", radii=(0.014, 0.014, 0.006), segments=8, rings=6)
    return m


def pose(m, t):
    o = m.objects
    import math
    c = (0.0, -0.04, 0.12)
    a = math.radians(TILT)
    place(o["band"], c, (TILT, 0, 0))
    # the top of the ring (where the bezel sits): up along the tilted ring's own y axis
    top = (c[0], c[1] + 0.13 * math.cos(a), c[2] + 0.13 * math.sin(a))
    place(o["bezel"], top, (TILT - 90, 0, 0))
    n = (0.0, -math.sin(a) * -0.0 + math.cos(a) * 0.0, 0.0)
    out = (0, math.cos(a - math.pi / 2), math.sin(a - math.pi / 2))      # the bezel's face normal
    out = (0, -out[1], -out[2]) if out[2] < 0 else out
    place(o["stone"], (top[0], top[1] + out[1] * 0.03, top[2] + out[2] * 0.03), (TILT - 90, 0, 0))
    place(o["glint"], (top[0] - 0.02, top[1] + out[1] * 0.06 + 0.015, top[2] + out[2] * 0.06), (TILT - 90, 0, 0))
