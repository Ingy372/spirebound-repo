"""Dead bodies for our own monsters (art/CORPSE_RULES.md). Runs inside Blender, like the model files.

A corpse model is a two-line file, art/models/corpse_<monster>.py:

    import corpse_kit
    corpse_kit.make(globals(), "ridgecat")

It reuses the approved monster model untouched (same parts, palette and pixel rules, so the body matches the living
monster exactly) and lays it down:
  - frame 0 (t=None): fresh, lying on its side (animals) or on its back (people), resting on the ground;
  - frame 1 (t=0.0):  rotting, the same body sunk flatter; pixelize's output is then darkened and greyed by
    tools/make_corpse_sheets.py (rule C4);
  - frame 2 (t=0.5):  a dried husk, flatter still and darker: the last step for monsters with no bones (C5).
Bones (the last decay step) are a separate shared model (corpse_bones.py), so they are not made here.
"""
from __future__ import annotations

import importlib
import math

import bpy
from mathutils import Vector

COPY = ("PARTS", "PALETTE", "PIXEL_RULES", "SIZE", "HEIGHT_SHEAR", "PROJECTION", "GROUND_STRETCH", "REFERENCE",
        "CANVAS_OFFSET")


def make(g, base_name, lie="side", flatten=0.72, tilt=0.0, pose_t=None):
    """lie: "side" (rolled over; seen from the W its legs stick up), "back" (people: face up), "belly_up" (insects:
    flipped over, legs in the air), "flat" (plants, floating things simply sink to the ground). flatten: thickness kept by the rotting body. tilt: extra
    turn (degrees) on the ground, so a long body lies a little diagonal like Tibia's corpses."""
    base = importlib.import_module(base_name)
    for k in COPY:
        if hasattr(base, k):
            g[k] = getattr(base, k)
    g["AUTO_PLACE"] = (1, 1)         # C2: every corpse sits against the tile's right and bottom edges
    g["LEAN"] = 0.0
    g["WALK_FRAMES"] = 2             # frames: None = fresh, 0.0 = rotting, 0.5 = dried husk (C5, no-bone monsters)
    g["NAME"] = "corpse_" + base_name
    g["BASE"] = base_name

    def build(model_cls, facing):
        lying = bpy.data.objects.new("Lying", None)
        lying.parent = facing
        bpy.context.scene.collection.objects.link(lying)
        m = base.build(model_cls, lying)
        m._lying = lying
        return m

    def pose(m, t):
        base.pose(m, pose_t)
        lying = m._lying
        rot = {"side": (math.radians(-90), 0.0, 0.0), "back": (0.0, math.radians(-90), 0.0),
               "belly_up": (math.radians(180), 0.0, 0.0), "flat": (0.0, 0.0, 0.0)}[lie]
        lying.rotation_euler = (rot[0], rot[1], rot[2] + math.radians(tilt))
        lying.location = (0.0, 0.0, 0.0)
        squash = 1.0 if t is None else flatten if t < 0.25 else flatten * 0.7
        # thin the body along the axis that ends up vertical (C3: rot sinks, it does not shrink sideways)
        lying.scale = {"side": (1.0, squash, 1.0), "back": (squash, 1.0, 1.0), "belly_up": (1.0, 1.0, squash),
                       "flat": (1.0, 1.0, squash)}[lie]
        bpy.context.view_layer.update()
        inv = lying.parent.matrix_world.inverted()
        pts = [inv @ (o.matrix_world @ Vector(c)) for o in lying.children_recursive if o.type == "MESH"
               and not o.hide_render for c in o.bound_box]
        lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
        hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
        # C1: resting on the ground (nothing floats, nothing sinks below it), centred on its tile
        lying.location = (-(lo.x + hi.x) / 2, -(lo.y + hi.y) / 2, -lo.z)
        bpy.context.view_layer.update()

    g["build"] = build
    g["pose"] = pose
    g["assign_depth_parts"] = getattr(base, "assign_depth_parts", lambda m, depth_of: None)
