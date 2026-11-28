"""Plains Map (Floor 1 quest/tool item): item icon, art/ITEM_RULES.md.

  Silhouette: a parchment sheet lying flat with both ends rolled up into scrolls, tied with a red ribbon on the
              left roll: reads as "map" like Tibia's maps.
  Colours:    warm parchment, a green patch of plains drawn on it, one red accent (the ribbon and an X).
  Details:    rolled ends with shadowed undersides, a dotted brown road crossing the green, a tiny grey tower,
              a red X where the road ends.
Look-alike: Tibia's treasure map (5090): ours is a clean rolled sheet with green plains, not a torn brown scrap.
"""
from __future__ import annotations

from item_kit import *  # noqa: F401,F403
from item_kit import place, slab, BANDS, LIGHT

NAME = "item_plains_map"
PALETTE = NAME
PARTS = ["none", "paper", "roll", "plains", "road", "tower", "ribbon", "mark"]
PIXEL_RULES = {
    "weight": {"road": 3.0, "tower": 4.0, "mark": 4.0, "ribbon": 2.5, "plains": 1.5},
    "thin": {"road": 2, "tower": 2, "mark": 2, "ribbon": 3},
    "soft": [["paper", "plains", "road", "mark"]],
    "no_outline": ["plains", "road", "mark", "tower"],
    "selout": ["paper", "roll"],
    "texture": {"paper": [0.06, 0.08], "plains": [0.12, 0.10]},
    "bands": BANDS,
    "light": LIGHT,
}
SIZE = 1.15
W, D = 0.56, 0.44               # the flat sheet between the rolls (x), depth (y)


def build(model_cls, facing):
    m = model_cls(facing, PARTS)
    sheet = [(-W / 2, -D / 2), (W / 2, -D / 2), (W / 2, D / 2), (-W / 2, D / 2)]
    slab(m, "paper", "paper", sheet, 0.012)
    for i in range(2):
        m.capsule(f"roll{i}", "roll", segments=14)
    slab(m, "plains", "plains", [(-0.17, -0.12), (0.05, -0.15), (0.20, -0.06), (0.17, 0.12), (-0.02, 0.16),
                                 (-0.19, 0.08)], 0.004)
    for i in range(5):
        m.box(f"road{i}", "road", size=(0.035, 0.016, 0.006))
    m.box("tower", "tower", size=(0.04, 0.04, 0.09))
    m.cone("towertop", "tower", segments=4)
    m.box("x1", "mark", size=(0.06, 0.016, 0.006))
    m.box("x2", "mark", size=(0.06, 0.016, 0.006))
    m.capsule("ribbon", "ribbon", segments=10)
    m.box("ribbon_end", "ribbon", size=(0.03, 0.10, 0.008))
    return m


def pose(m, t):
    o = m.objects
    place(o["paper"], (0, -0.02, 0.0))
    for i, x in enumerate((-W / 2, W / 2)):
        m.put_segment(f"roll{i}", (x, -D / 2 - 0.03, 0.045), (x, D / 2 + 0.01, 0.045), 0.045)
    place(o["plains"], (0, -0.02, 0.012))
    for i in range(5):
        place(o[f"road{i}"], (-0.16 + 0.065 * i, -0.12 + 0.045 * i + 0.02 * (i % 2), 0.018), (0, 0, 35))
    place(o["tower"], (-0.05, 0.06, 0.06))
    m.put_segment("towertop", (-0.05, 0.06, 0.105), (-0.05, 0.06, 0.15), 0.03)
    place(o["x1"], (0.18, 0.11, 0.018), (0, 0, 45))
    place(o["x2"], (0.18, 0.11, 0.018), (0, 0, -45))
    m.put_segment("ribbon", (-W / 2, 0.05, 0.045), (-W / 2, 0.09, 0.045), 0.052)
    place(o["ribbon_end"], (-W / 2 + 0.02, -0.02, 0.02), (0, 0, 20))
