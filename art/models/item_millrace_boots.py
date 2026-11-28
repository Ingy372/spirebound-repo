"""Millrace Boots (Floor 1 armour): item icon, art/ITEM_RULES.md.

  Silhouette: a pair of ankle boots, one behind the other, toes to the right: each shows its L-shaped side
              (shaft, foot, toe), like Tibia's boots, which come as a pair.
  Colours:    light tan leather (dark boots vanished into their outline in Grok's batch), dark soles, a dark opening
              at the top of each shaft, one accent: a brass buckle on each strap (the mill's brass fittings).
  Details:    folded-over lighter cuff, a strap across the instep, thick heel, a rounded toe cap.
Look-alike: Tibia's leather boots (3552): ours are lighter tan with cuffs and brass buckles.
Tries (2026-11-27): standing boots seen from the tilted camera showed the lit round tops of their shafts (a row
of balls, then a row of pipes). Now each boot is built standing and then laid on its side under the flat-item
camera (`LAY`), so we see its side profile straight on, which is how Tibia draws boots.
"""
from __future__ import annotations

import math

from item_kit import *  # noqa: F401,F403
from item_kit import place, BANDS, LIGHT

NAME = "item_millrace_boots"
PALETTE = NAME
SIZE = 1.12
PARTS = ["none", "leather", "cuff", "sole", "strap", "buckle", "toecap", "inside"]
PIXEL_RULES = {
    "weight": {"buckle": 4.0, "strap": 2.0, "cuff": 1.5, "toecap": 1.5, "inside": 2.0},
    "thin": {"buckle": 2, "strap": 3},
    "soft": [["leather", "toecap"]],
    "no_outline": ["inside"],
    "selout": ["leather", "cuff", "toecap"],
    "texture": {"leather": [0.06, 0.05], "cuff": [0.05, 0.0]},
    "bands": BANDS,
    "light": LIGHT,
}

# (name, x, up, depth, yaw): in the boot's standing frame (toe = +x, up = +z, the viewer's side = -y). The back
# boot sits higher on screen (up) and behind (depth); yaw turns the toes a little towards the viewer.
BOOTS = (("b", -0.13, 0.11, 0.12, -10), ("a", 0.07, -0.09, -0.12, -18))


def build(model_cls, facing):
    import bpy
    lay = bpy.data.objects.new("Lay", None)       # standing frame -> lying on its side, profile facing the camera
    lay.parent = facing
    lay.rotation_euler = (math.radians(-90), 0, 0)
    bpy.context.scene.collection.objects.link(lay)
    m = model_cls(lay, PARTS)
    for b, *_ in BOOTS:
        m.frustum(f"shaft_{b}", "leather", top_ratio=1.08, segments=16)
        m.frustum(f"cuff_{b}", "cuff", top_ratio=1.06, segments=16)
        m.ellipsoid(f"open_{b}", "inside", radii=(0.064, 0.058, 0.008), segments=14, rings=6)
        m.ellipsoid(f"foot_{b}", "leather", radii=(0.15, 0.072, 0.068), segments=16, rings=10)
        m.ellipsoid(f"toe_{b}", "toecap", radii=(0.07, 0.068, 0.055), segments=14, rings=8)
        m.box(f"sole_{b}", "sole", size=(0.37, 0.15, 0.03))
        m.box(f"heel_{b}", "sole", size=(0.09, 0.14, 0.05))
        m.frustum(f"strap_{b}", "strap", top_ratio=1.0, segments=16)
        m.box(f"buckle_{b}", "buckle", size=(0.03, 0.02, 0.045))
    return m


def pose(m, t):
    o = m.objects
    for b, x, up, depth, yaw in BOOTS:
        a = math.radians(yaw)

        def p(lx, ly, z):          # a point in the boot's own frame (toe along +x) -> the standing frame
            return (x + lx * math.cos(a) - ly * math.sin(a), depth + lx * math.sin(a) + ly * math.cos(a), z + up)

        place(o[f"sole_{b}"], p(0.05, 0, 0.015), (0, 0, yaw))
        place(o[f"heel_{b}"], p(-0.07, 0, 0.045), (0, 0, yaw))
        place(o[f"foot_{b}"], p(0.06, 0, 0.075), (0, 0, yaw))
        place(o[f"toe_{b}"], p(0.16, 0, 0.065), (0, 0, yaw))
        place(o[f"shaft_{b}"], p(-0.04, 0, 0.05), (0, 0, yaw), scale=(0.08, 0.072, 0.29))
        place(o[f"cuff_{b}"], p(-0.04, 0, 0.31), (0, 0, yaw), scale=(0.090, 0.082, 0.065))
        place(o[f"open_{b}"], p(-0.04, 0, 0.377), (0, 0, yaw))
        place(o[f"strap_{b}"], p(0.04, 0, 0.11), (0, -50, yaw), scale=(0.066, 0.08, 0.03))
        place(o[f"buckle_{b}"], p(0.05, -0.08, 0.13), (0, 0, yaw))
