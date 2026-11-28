"""Warden's Signet (Floor 1 keepsake, +1 main skill): item icon, art/ITEM_RULES.md.

  Silhouette: a heavy dark-iron ring with a gold KEY set across its top: the key's round bow sticks out on one side
              and its toothed bit on the other, so the ring wears a crossbar. A ring with a key across it is a shape
              no Tibia ring has (rule I0); Tibia's rings are bands with a stone.
  Colours:    dark iron band, a gold key, one cool accent: a blue stone set in the key's bow.
  Details:    the key's bow is a ring with the stone in it, two teeth on the bit, the band thickens under the key.
Size: small in the middle of its tile, like Tibia's rings.
Look-alike checked: Tibia's signet ring (31592) and the other rings: bands with a stone or a seal.
"""
from __future__ import annotations

import math

from item_kit import *  # noqa: F401,F403
from item_kit import place, torus, BANDS, LIGHT

NAME = "item_wardens_signet"
PALETTE = NAME
SIZE = 1.25
PARTS = ["none", "band", "key", "bow", "stone", "glint"]
PIXEL_RULES = {
    "weight": {"key": 2.5, "bow": 2.5, "stone": 3.0, "glint": 5.0},
    "thin": {"key": 3, "glint": 2},
    "soft": [["key", "bow"]],
    "no_outline": ["glint"],
    "selout": ["band", "key", "bow"],
    "bands": BANDS,
    "light": LIGHT,
}
TILT = 55                      # the ring stands half up, so the key across its top faces the viewer


def build(model_cls, facing):
    m = model_cls(facing, PARTS)
    torus(m, "band", "band", major=0.11, minor=0.030, segments=32, rings=10, squash=0.85)
    m.capsule("shaft", "key", segments=10)
    torus(m, "bow", "bow", major=0.045, minor=0.016, segments=20, rings=8)
    m.ellipsoid("stone", "stone", radii=(0.034, 0.034, 0.022), segments=12, rings=8)
    m.box("tooth0", "key", size=(0.02, 0.022, 0.05))
    m.box("tooth1", "key", size=(0.02, 0.022, 0.035))
    m.ellipsoid("glint", "glint", radii=(0.010, 0.010, 0.006), segments=8, rings=6)
    return m


def pose(m, t):
    o = m.objects
    c = (0.0, -0.06, 0.10)
    a = math.radians(TILT)
    place(o["band"], c, (TILT, 0, 0))
    # the top of the tilted ring: the key lies across it, left-right
    top = (c[0], c[1] + 0.11 * math.cos(a), c[2] + 0.11 * math.sin(a) + 0.03)
    m.put_segment("shaft", (top[0] - 0.12, top[1], top[2]), (top[0] + 0.12, top[1], top[2]), 0.017)
    bow = (top[0] - 0.16, top[1], top[2])
    place(o["bow"], bow, (TILT - 90 + 90, 0, 0))
    place(o["stone"], (bow[0], bow[1] - 0.008, bow[2] + 0.008), (TILT, 0, 0))
    place(o["glint"], (bow[0] - 0.012, bow[1], bow[2] + 0.03))
    place(o["tooth0"], (top[0] + 0.10, top[1], top[2] - 0.03))
    place(o["tooth1"], (top[0] + 0.065, top[1], top[2] - 0.022))
