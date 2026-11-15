"""Grey alpha (Floor 1, Wolf Copse elite): the meadow wolf's body and walk, bigger and fiercer.

ART_REQUESTS.md: "a bigger silver-grey wolf with a scarred face and a darker mane (elite version of the
wolf)". Reuses art/models/wolf.py (so every wolf fix reaches the alpha too) and adds: a silver-grey coat, a heavy
dark mane round the neck and shoulders, a pale scar across the face, and a bigger size. Compared with Tibia's
War Wolf (the closest look-alike).
"""
from __future__ import annotations

from mathutils import Vector

import wolf

NAME = "alpha"
WALK_FRAMES = wolf.WALK_FRAMES
PALETTE = "alpha"
HEIGHT_SHEAR = wolf.HEIGHT_SHEAR
LEAN = wolf.LEAN
REFERENCE = "look_3.png"     # Tibia's War Wolf (comparison only, never shipped)
GROUND_STRETCH = wolf.GROUND_STRETCH
SIZE = 2.25                  # a head taller than the meadow wolf, like Tibia's war wolf next to its wolf
CANVAS_OFFSET = (0, 2)
PIXEL_RULES = {
    **wolf.PIXEL_RULES,
    "weight": {**wolf.PIXEL_RULES["weight"], "scar": 2.5, "mane": 1.3},
    "thin": {**wolf.PIXEL_RULES["thin"], "scar": 2, "mane": 4},
    "texture": {**wolf.PIXEL_RULES["texture"], "mane": [1.4, 0.2]},
    "soft": [wolf.PIXEL_RULES["soft"][0] + ["mane", "scar"]],
}
PARTS = wolf.PARTS + ["mane", "scar"]
OX = -0.09


def build(model_cls, facing):
    wolf.PARTS, wolf.OX = PARTS, OX
    m = wolf.build(model_cls, facing)
    m.facing.scale = (1.18, 1.0, 0.88)          # longer and lower than the meadow wolf, like a war wolf
    m.set_part("ruff", "mane")
    m.objects["ruff"].scale = (0.095, 0.112, 0.088)
    m.capsule("scar", "scar")
    return m


def pose(m, t):
    wolf.pose(m, t)
    head = m.objects["head"].location
    m.objects["ruff"].location = m.objects["chest"].location + Vector((0.035, 0, 0.022))
    m.put_segment("scar", head + Vector((0.050, -0.040, 0.062)), head + Vector((0.100, -0.062, 0.010)), 0.008)


def assign_depth_parts(m, depth_of):
    wolf.assign_depth_parts(m, depth_of)
