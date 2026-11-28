"""Millrace Boots (Floor 1 keepsake, +5 movement speed): item icon, art/ITEM_RULES.md.

  Silhouette: a pair of boots seen side-on, each with a little WATER-WHEEL turning on its heel like a spur (the
              millrace: fast water that drives a mill). Boots with wheels are a shape no Tibia boots have (rule I0).
  Colours:    tan leather, dark soles, a river-blue cuff, wooden paddle wheels with brass hubs (the accent).
  Details:    six paddles on each wheel, a rim, a brass hub, a strap and buckle across the instep.
Look-alike checked: Tibia's leather boots (3552) and its other boots are plain pairs; none carries a wheel.
Camera (rule I5): each boot is built standing and laid on its side under the flat-item camera (`Lay`), so we see
its side profile straight on; standing boots under the tilted camera read as balls, then pipes (2026-11-27).
"""
from __future__ import annotations

import math

from item_kit import *  # noqa: F401,F403
from item_kit import place, BANDS, LIGHT

NAME = "item_millrace_boots"
PALETTE = NAME
SIZE = 1.12
PARTS = ["none", "leather", "cuff", "sole", "strap", "buckle", "toecap", "inside", "rim", "paddle", "hub"]
PIXEL_RULES = {
    "weight": {"buckle": 4.0, "strap": 2.0, "cuff": 1.5, "toecap": 1.5, "inside": 2.0, "rim": 2.5, "paddle": 2.0, "hub": 4.0},
    "thin": {"buckle": 2, "strap": 3, "rim": 3, "hub": 2},
    "soft": [["leather", "toecap"], ["rim", "paddle"]],
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
        from item_kit import torus
        torus(m, f"rim_{b}", "rim", major=0.085, minor=0.013, segments=24, rings=6)
        for k in range(6):
            m.box(f"paddle_{b}{k}", "paddle", size=(0.028, 0.03, 0.05))
        m.ellipsoid(f"hub_{b}", "hub", radii=(0.022, 0.02, 0.022), segments=10, rings=6)
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
        hx, hz = -0.19, 0.11                       # the wheel turns on the heel, on the viewer's side
        place(o[f"rim_{b}"], p(hx, -0.085, hz), (90, 0, yaw))
        for k in range(6):
            ang = 360 * k / 6 + 15
            r = math.radians(ang)
            place(o[f"paddle_{b}{k}"], p(hx + 0.075 * math.cos(r), -0.085, hz + 0.075 * math.sin(r)), (0, -ang, yaw))
        place(o[f"hub_{b}"], p(hx, -0.10, hz), (0, 0, yaw))
