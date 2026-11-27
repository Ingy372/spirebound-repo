"""The Climbers' Monument (Hearthgate, the Hearth's ground floor): our own map object, not a creature (2026-11-27).

Jay, 2026-11-27: "the monument with the player names who have cleared bosses defiantly deserves to be its own custom
object." It stood as Tibia's hero statue on a plain block. Now:
  Silhouette: a broad pale granite memorial slab facing the viewer on a two-step plinth, a small bronze spire on top
              (the tower every climber is climbing), a blue crystal (the Spire's crystal) set above the names. Reads
              as "a memorial", not a person. (A narrow obelisk was tried first: at 64 px its plaque was a sliver.)
  Colours:    cool grey granite, warm bronze for the cap, the name plaque and the laurels, one cerulean crystal.
  Details:    the bronze plaque on the front carries rows of carved names; the plinth's edges are picked out by the
              steps. (A laurel wreath on the step was tried and dropped: at this size it read as a green blob.)
Rendered by art/pipeline/render_creature.py like a creature; only the east view, standing frame, is used
(art/output/monument/frames/E_0.png: Tibia draws east faces upright, so the plaque reads as a board;
from the south it was squashed flat). tools/make_creature_sheets.py packs it, tools/install_effects.py draws Tibia's
item 2028 ("monument", unused on our map) with it, and maps/hearthgate.py places item 2028.
"""
from __future__ import annotations

import math

from mathutils import Euler, Vector

NAME = "monument"
WALK_FRAMES = 1                # a still object: only the standing frame of one view is used
PALETTE = "monument"
PROJECTION = "oblique"         # Tibia's drawing rule for tall things: height leans up-left
AUTO_PLACE = (1, 1)            # against the tile's right and bottom edges, spilling up-left, like Tibia's statues
LEAN = 0.0
SIZE = 1.1                     # a little bigger than one tile's worth, so it stands taller than the pillars beside it

PARTS = ["none", "plinth", "step", "stone", "cap", "plaque", "names", "gem"]
PIXEL_RULES = {
    "weight": {"names": 4.0, "gem": 6.0, "plaque": 2.0, "cap": 2.0},
    "thin": {"names": 2, "gem": 3},
    "soft": [["plinth", "step"]],
    "no_outline": ["names"],
    "selout": ["stone", "plinth", "step"],
}

BASE = (0.96, 0.10)            # plinth: width, height
STEP = (0.78, 0.09)
Z0 = BASE[1] + STEP[1]
SLAB = (0.20, 0.80, 0.86)      # the memorial slab: depth (x, facing the viewer), width (y), height
CREST = (0.10, 0.36)           # the spire on top: base radius, height (the tower every climber is climbing)


def build(model_cls, facing):
    m = model_cls(facing, PARTS)
    m.box("base", "plinth", size=(BASE[0], BASE[0], BASE[1]))
    m.box("step", "step", size=(STEP[0], STEP[0], STEP[1]))
    m.box("slab", "stone", size=SLAB)
    m.box("coping", "step", size=(SLAB[0] + 0.06, SLAB[1] + 0.06, 0.06))      # a moulded top edge
    m.frustum("crest_foot", "cap", top_ratio=0.75, segments=4)
    m.cone("crest", "cap", segments=4)
    m.box("plaque", "plaque", size=(0.02, 0.60, 0.50))
    for i in range(5):
        m.box(f"name{i}", "names", size=(0.012, 0.44 - 0.10 * (i % 2), 0.026))
    m.ellipsoid("gem", "gem", radii=(0.040, 0.060, 0.060), segments=10, rings=8)
    return m


def pose(m, t):
    o = m.objects
    o["base"].location = Vector((0, 0, BASE[1] / 2))
    o["step"].location = Vector((0, 0, BASE[1] + STEP[1] / 2))
    o["slab"].location = Vector((0, 0, Z0 + SLAB[2] / 2))
    top = Z0 + SLAB[2]
    o["coping"].location = Vector((0, 0, top + 0.03))
    top += 0.06
    f = o["crest_foot"]
    f.location = Vector((0, 0, top))
    f.rotation_mode = "XYZ"
    f.rotation_euler = Euler((0, 0, math.pi / 4))
    f.scale = (CREST[0] * 1.15, CREST[0] * 1.15, 0.06)
    m.put_segment("crest", Vector((0, 0, top + 0.06)), Vector((0, 0, top + 0.06 + CREST[1])), CREST[0] * 0.85)
    o["crest"].rotation_quaternion = o["crest"].rotation_quaternion @ Euler((0, 0, math.pi / 4)).to_quaternion()
    front = SLAB[0] / 2
    zc = Z0 + SLAB[2] * 0.46
    o["plaque"].location = Vector((front + 0.010, 0, zc))
    for i in range(5):
        o[f"name{i}"].location = Vector((front + 0.024, 0, zc + 0.17 - i * 0.085))
    o["gem"].location = Vector((front + 0.012, 0, Z0 + SLAB[2] - 0.07))


def assign_depth_parts(m, depth_of):
    return None
