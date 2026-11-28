"""Shrinekeeper's Pendant (Floor 1 keepsake, +3% health and mana): item icon, art/ITEM_RULES.md.

  Silhouette: a tiny SHRINE on a cord: a little stone house with a peaked roof and a lit doorway, hanging from a
              loop of cord with a bead. A house shape is something no Tibia amulet is (rule I0); Tibia's amulets are
              discs, gems, beetles and torcs.
  Colours:    pale shrine stone, a dark slate roof with gold ridge cap, a red cord, one warm accent: the glowing door.
  Details:    the roof overhangs the walls, a gold finial on the peak, the arched door glows from inside, a step.
Size: small on its tile, like Tibia's amulets.
Look-alike checked: Tibia's ancient amulet (3025), star and silver amulets: all round or gem-shaped.
Built standing (front = -y) and laid down under the flat-item camera (rule I5), so the front faces the viewer.
"""
from __future__ import annotations

import math

from item_kit import *  # noqa: F401,F403
from item_kit import place, slab, set_tube_pts, BANDS, LIGHT

NAME = "item_shrinekeepers_pendant"
PALETTE = NAME
SIZE = 1.25
PARTS = ["none", "wall", "roof", "ridge", "door", "glow", "cord", "bead", "step"]
PIXEL_RULES = {
    "weight": {"glow": 4.0, "door": 2.5, "ridge": 3.0, "cord": 2.5, "bead": 3.0, "step": 1.5},
    "thin": {"glow": 3, "cord": 2, "ridge": 2, "bead": 3},
    "soft": [["door", "glow"]],
    "selout": ["wall", "roof"],
    "texture": {"wall": [0.10, 0.08], "roof": [0.08, 0.0]},
    "bands": BANDS,
    "light": LIGHT,
}
W, D, H = 0.20, 0.12, 0.16          # the shrine's walls: width (x), depth (y), height (z)


def build(model_cls, facing):
    import bpy
    lay = bpy.data.objects.new("Lay", None)
    lay.parent = facing
    lay.rotation_euler = (math.radians(-90), 0, 0)
    bpy.context.scene.collection.objects.link(lay)
    m = model_cls(lay, PARTS)
    m.box("wall", "wall", size=(W, D, H))
    m.box("step", "step", size=(W + 0.05, D + 0.04, 0.03))
    gable = [(-W / 2 - 0.035, 0), (W / 2 + 0.035, 0), (0, 0.17)]      # the roof's triangle, overhanging the walls
    slab(m, "roof", "roof", gable, D + 0.05)
    m.capsule("ridge", "ridge", segments=8)
    m.ellipsoid("finial", "ridge", radii=(0.022, 0.022, 0.03), segments=10, rings=6)
    m.box("door", "door", size=(0.085, 0.02, 0.11))
    m.ellipsoid("arch", "door", radii=(0.0425, 0.012, 0.0425), segments=12, rings=8)
    m.box("glow", "glow", size=(0.055, 0.02, 0.085))
    m.ellipsoid("glowtop", "glow", radii=(0.0275, 0.012, 0.0275), segments=12, rings=8)
    m.tube("cord", "cord", points=8)
    m.ellipsoid("bead", "bead", radii=(0.026, 0.026, 0.026), segments=10, rings=8)
    return m


def pose(m, t):
    o = m.objects
    place(o["step"], (0, 0, 0.015))
    place(o["wall"], (0, 0, 0.03 + H / 2))
    top = 0.03 + H
    # the gable triangle lies in the slab's xy plane: stand it up (its y becomes height) and give it depth along y
    place(o["roof"], (0, D / 2 + 0.025, top), (90, 0, 0))
    m.put_segment("ridge", (0, -D / 2 - 0.03, top + 0.17), (0, D / 2 + 0.03, top + 0.17), 0.016)
    place(o["finial"], (0, -D / 2 - 0.02, top + 0.19))
    fy = -D / 2 - 0.004
    place(o["door"], (0, fy, 0.03 + 0.055))
    place(o["arch"], (0, fy, 0.03 + 0.11))
    place(o["glow"], (0, fy - 0.004, 0.03 + 0.05))
    place(o["glowtop"], (0, fy - 0.004, 0.03 + 0.093))
    # the cord loops up from the finial and comes back down, a bead where it meets
    peak = (0, -D / 2 - 0.02, top + 0.21)
    loop = []
    for i in range(8):
        a = math.radians(-90 + 360 * i / 7)
        loop.append((peak[0] + 0.063 * math.cos(a), peak[1], peak[2] + 0.09 + 0.09 * math.sin(a)))
    set_tube_pts(m, "cord", loop, 0.009)
    place(o["bead"], (peak[0], peak[1] - 0.005, peak[2] + 0.005))
