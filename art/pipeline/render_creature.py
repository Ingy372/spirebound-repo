"""Render one creature's raw passes with the shared rig. Runs inside Blender (headless):

  blender -b --factory-startup --python art/pipeline/render_creature.py -- rat

Writes art/output/<name>/passes/<dir>_<frame>_<pass>.png (frame 0 = standing, 1..N = walk) and saves the
posed model as art/models/<name>.blend. Then run pixelize.py (normal Python) to make the final sprites.
Passes: id (which part each pixel belongs to), normal (which way the surface faces), depth (distance).
"""
from __future__ import annotations

import importlib
import math
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
    # a part's number is stored as index * 8 in the red channel of the id pass: 0-32 survive, anything above 32
    # is read back as 32 (it silently takes part 32's colours). Found when the Hedge Hexer's glow came out bone-white.
    if len(creature.PARTS) > 33:
        raise SystemExit(f"{name}: {len(creature.PARTS)} parts; at most 33 (reuse a hidden base part, art/README.md)")
    out = ART / "output" / name / "passes"
    out.mkdir(parents=True, exist_ok=True)

    gs = getattr(creature, "GROUND_STRETCH", None)      # how long north/south bodies look (tilt view only)
    if gs is not None:
        rig.Y_STRETCH = 1.0 + gs * (1.0 / math.sin(math.radians(rig.ELEVATION)) - 1.0)
    # AUTO_PLACE = (right margin, bottom margin): render on a bigger canvas, then pixelize.py cuts the 64x64
    # frame for each direction so the creature sits against the tile's right and bottom edges, spilling up-left,
    # the way Tibia's own bigger creatures are placed. Nothing can be clipped by the canvas edge.
    auto_place = getattr(creature, "AUTO_PLACE", None)
    if auto_place is not None:
        rig.VIEW_TILES, rig.CAM_SHIFT_X, rig.CAM_SHIFT_Y = 4.0, 0.0, 0.0
    scene = rig.reset_scene()
    projection = getattr(creature, "PROJECTION", "tilt")
    cam = rig.add_camera(scene, projection)
    # placement on the 64x64 canvas (in pixels): move the camera, so nothing is cut off at the canvas edge
    off = list(getattr(creature, "CANVAS_OFFSET", (0, 0)))
    px = 1.0 / (rig.VIEW_TILES * rig.PIXELS_PER_TILE)
    cam.data.shift_x -= off[0] * px
    cam.data.shift_y += off[1] * px
    shear = getattr(creature, "HEIGHT_SHEAR", rig.HEIGHT_SHEAR)
    _root, facing = rig.add_world_root(scene, shear, projection)
    size = getattr(creature, "SIZE", 1.0)             # whole-creature size, matched to its Tibia look-alike
    holder = facing
    if size != 1.0:
        holder = bpy.data.objects.new("CreatureSize", None)
        holder.parent = facing
        holder.scale = (size, size, size)
        scene.collection.objects.link(holder)
    model = creature.build(Model, holder)
    mat_normal, mat_depth, mat_tex = rig.normal_material(), rig.depth_material(), rig.texture_material()
    meshes = [o for o in scene.objects if o.type == "MESH"]
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
            for o in meshes:                           # real size of each part, for the grain pass
                sc = (holder.matrix_world.inverted() @ o.matrix_world).to_scale()
                o["tex_scale"] = (abs(sc.x) * size, abs(sc.y) * size, abs(sc.z) * size)
            for pname, mat in (("id", None), ("normal", mat_normal), ("depth", mat_depth), ("tex", mat_tex)):
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
            "canvas_offset": [0, 0], "placed": off, "auto_place": list(auto_place) if auto_place is not None else None}
    (out.parent / "meta.json").write_text(json.dumps(meta, indent=1))

    if not only:
        rig.set_direction(facing, "E")
        creature.pose(model, None)
        blend = ART / "models" / f"{name}.blend"
        bpy.ops.wm.save_as_mainfile(filepath=str(blend), compress=True)


main()
