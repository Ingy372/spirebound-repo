"""Render one creature's raw passes with the shared rig. Runs inside Blender (headless):

  blender -b --factory-startup --python art/pipeline/render_creature.py -- rat

Writes art/output/<name>/passes/<dir>_<frame>_<pass>.png (frame 0 = standing, 1..N = walk) and saves the
posed model as art/models/<name>.blend. Then run pixelize.py (normal Python) to make the final sprites.
Passes: id (which part each pixel belongs to), normal (which way the surface faces), depth (distance).
"""
from __future__ import annotations

import importlib
import os
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ART = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ART / "models"))

import bpy  # noqa: E402

import rig  # noqa: E402
from shapes import Model  # noqa: E402


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    name = argv[0] if argv else "rat"
    only = argv[1] if len(argv) > 1 else None          # optional: one direction, for quick tests
    creature = importlib.import_module(name)
    out = ART / "output" / name / "passes"
    out.mkdir(parents=True, exist_ok=True)

    scene = rig.reset_scene()
    projection = getattr(creature, "PROJECTION", "tilt")
    cam = rig.add_camera(scene, projection)
    shear = getattr(creature, "HEIGHT_SHEAR", rig.HEIGHT_SHEAR)
    _root, facing = rig.add_world_root(scene, shear, projection)
    model = creature.build(Model, facing)
    mat_normal, mat_depth = rig.normal_material(), rig.depth_material()
    layer = scene.view_layers[0]

    cam_inv = None

    def depth_of(world_point):
        return -(cam_inv @ world_point).z

    t0 = time.time()
    frames = [None] + [i / creature.WALK_FRAMES for i in range(creature.WALK_FRAMES)]
    for d in rig.ORDER:
        if only and d != only:
            continue
        rig.set_direction(facing, d, getattr(creature, "LEAN", 0.0))
        for f, t in enumerate(frames):
            creature.pose(model, t)
            bpy.context.view_layer.update()
            cam_inv = cam.matrix_world.inverted()
            creature.assign_depth_parts(model, depth_of)
            for pname, mat in (("id", None), ("normal", mat_normal), ("depth", mat_depth)):
                layer.material_override = mat
                scene.render.filepath = str(out / f"{d}_{f}_{pname}.png")
                bpy.ops.render.render(write_still=True)
            layer.material_override = None
    print(f"rendered {name} in {time.time() - t0:.1f}s -> {out}")
    import json
    meta = {"name": name, "parts": creature.PARTS, "palette": creature.PALETTE, "walk_frames": creature.WALK_FRAMES,
            "order": rig.ORDER, "supersample": rig.SUPERSAMPLE, "view_tiles": rig.VIEW_TILES,
            "y_stretch": rig.Y_STRETCH, "world_linear": rig.world_linear(shear, projection), "depth_range": rig.DEPTH_RANGE,
            "rules": getattr(creature, "PIXEL_RULES", {}), "ref": getattr(creature, "REFERENCE", None),
            "canvas_offset": list(getattr(creature, "CANVAS_OFFSET", (0, 0)))}
    (out.parent / "meta.json").write_text(json.dumps(meta, indent=1))

    if not only:
        rig.set_direction(facing, "E")
        creature.pose(model, None)
        blend = ART / "models" / f"{name}.blend"
        bpy.ops.wm.save_as_mainfile(filepath=str(blend), compress=True)


main()
