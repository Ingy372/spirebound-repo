"""Inn Tankard (Floor 1 food/drink): item icon, art/ITEM_RULES.md.

  Silhouette: a tall pewter tankard standing upright, a big handle on the right, a dome of foam over the rim with
              one drip down the front: reads as "beer" at once, like Tibia's beer mug.
  Colours:    cool pewter, creamy white foam, warm amber where the beer shows at the rim.
  Details:    two raised bands round the body, a thick foot, a dark hammered anvil mark (the inn's sign) on the front.
First try (2026-11-27): a hinged lid and heaped foam covered the whole front and it read as a pot with a hat;
the lid is gone and the foam stays on top.
Look-alike: Tibia's beer mug (32072): ours is pewter, taller, with bands and an anvil mark.
"""
from __future__ import annotations

from item_kit import *  # noqa: F401,F403
from item_kit import STANDING, lathe, place, torus, BANDS

NAME = "item_inn_tankard"
PALETTE = NAME
globals().update(STANDING)    # stands upright: the tilted camera, the creatures' light
SIZE = 1.3
PARTS = ["none", "body", "bandring", "handle", "foam", "beer", "mark"]
PIXEL_RULES = {
    "weight": {"mark": 3.0, "bandring": 2.0, "beer": 2.5},
    "thin": {"mark": 3, "bandring": 3, "beer": 3},
    "soft": [["foam", "beer"]],
    "no_outline": ["mark"],
    "selout": ["body", "foam"],
    "texture": {"body": [0.05, 0.06], "foam": [0.10, 0.04]},
    "bands": BANDS,
}
H = 0.46
R = 0.135


def build(model_cls, facing):
    m = model_cls(facing, PARTS)
    lathe(m, "body", "body", [(0, 0), (R + 0.025, 0), (R + 0.03, 0.035), (R + 0.005, 0.05), (R, H - 0.02),
                             (R + 0.01, H), (R - 0.02, H), (R - 0.02, H - 0.03), (0, H - 0.03)], segments=28)
    for i in range(2):
        torus(m, f"band{i}", "bandring", major=R + 0.003, minor=0.012, segments=28, rings=6)
    torus(m, "handle", "handle", major=0.11, minor=0.03, segments=20, rings=8)
    lathe(m, "beer", "beer", [(0, H - 0.03), (R - 0.015, H - 0.03), (R - 0.015, H + 0.005), (0, H + 0.005)], segments=24)
    for i in range(4):
        m.ellipsoid(f"foam{i}", "foam", radii=(1, 1, 1), segments=12, rings=8)
    m.box("mark", "mark", size=(0.02, 0.10, 0.025))
    m.box("mark2", "mark", size=(0.02, 0.045, 0.05))
    return m


def pose(m, t):
    o = m.objects
    place(o["body"], (0, 0, 0))
    place(o["band0"], (0, 0, 0.10))
    place(o["band1"], (0, 0, H - 0.09))
    place(o["handle"], (R + 0.02, 0, H * 0.52), (90, 0, 0), scale=(0.9, 1.3, 1.0))
    place(o["beer"], (0, 0, 0))
    for i, (x, y, z, rx, rz) in enumerate(((0.0, 0.02, H + 0.03, 0.11, 0.06), (-0.06, -0.03, H + 0.01, 0.07, 0.05),
                                           (0.06, -0.04, H + 0.01, 0.07, 0.045), (-0.07, -0.115, H - 0.06, 0.03, 0.06))):
        place(o[f"foam{i}"], (x, y, z), scale=(rx, rx * 0.9, rz))
    place(o["mark"], (0.0, -R - 0.004, H * 0.50), (0, 0, 90))
    place(o["mark2"], (0.0, -R - 0.004, H * 0.42), (0, 0, 90))
