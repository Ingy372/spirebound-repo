"""Blender side of the spell-effect pipeline: renders the SOLID parts of an effect (swords, rocks, thorns, crystals,
a banner) frame by frame. The light, glow and sparks are painted afterwards by make_fx.py.

  blender -b --factory-startup --python art/effects/render_fx.py -- <effect> <frames> <out_dir>

Camera: the game's own drawing rule. The camera looks straight down at the tile; height slides up and a little
to the left (fx2d.UP), so a tall thing rises toward the top-left exactly like every tall sprite in the game.
1 unit = 1 tile = 32 pixels; the picture is 64x64 (drawn at 4x) and the spell's tile is its bottom-right quarter.
"""
from __future__ import annotations

import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

SS = 4
UP = (-0.38, -0.925)            # must match fx2d.UP


def _lin(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


class Fx:
    """Builders for one frame. Every shape hangs under one root that applies the height lean."""

    def __init__(self, scene):
        self.scene = scene
        self.mats = {}
        self.shear = Matrix(((1, 0, UP[0], 0), (0, 1, -UP[1], 0), (0, 0, 1, 0), (0, 0, 0, 1)))
        self.objects = []

    def clear(self):
        for o in self.objects:
            me = o.data
            bpy.data.objects.remove(o, do_unlink=True)
            if me and me.users == 0:
                bpy.data.meshes.remove(me)
        self.objects = []

    def mat(self, color, emit=0.0):
        key = (tuple(color), round(emit, 2))
        if key in self.mats:
            return self.mats[key]
        m = bpy.data.materials.new("fx")
        m.use_nodes = True
        b = m.node_tree.nodes["Principled BSDF"]
        rgba = (_lin(color[0]), _lin(color[1]), _lin(color[2]), 1.0)
        b.inputs["Base Color"].default_value = rgba
        b.inputs["Roughness"].default_value = 1.0
        for name in ("Specular IOR Level", "Specular"):
            if name in b.inputs:
                b.inputs[name].default_value = 0.0
        for name in ("Emission Color", "Emission"):
            if name in b.inputs:
                b.inputs[name].default_value = rgba
        if "Emission Strength" in b.inputs:
            b.inputs["Emission Strength"].default_value = emit
        self.mats[key] = m
        return m

    def mesh(self, verts, faces, color, emit=0.0, smooth=False):
        me = bpy.data.meshes.new("fx")
        # the height lean is baked into the points: up = up the screen and a little left
        me.from_pydata([(x + UP[0] * z, y - UP[1] * z, z) for x, y, z in verts], [], faces)
        me.update()
        if smooth:
            for p in me.polygons:
                p.use_smooth = True
        o = bpy.data.objects.new("fx", me)
        me.materials.append(self.mat(color, emit))
        self.scene.collection.objects.link(o)
        self.objects.append(o)
        return o

    def cone(self, base, height, radius, color, sides=6, lean=(0.0, 0.0), top=0.0, emit=0.0, rot=0.0):
        """a cone or (top > 0) a cut-off cone standing on `base`; lean = how far the top is pushed sideways"""
        bx, by, bz = base
        v, f = [], []
        for i in range(sides):
            a = rot + 2 * math.pi * i / sides
            v.append((bx + radius * math.cos(a), by + radius * math.sin(a), bz))
        if top <= 0.0:
            v.append((bx + lean[0], by + lean[1], bz + height))
            for i in range(sides):
                f.append((i, (i + 1) % sides, sides))
        else:
            for i in range(sides):
                a = rot + 2 * math.pi * i / sides
                v.append((bx + lean[0] + top * math.cos(a), by + lean[1] + top * math.sin(a), bz + height))
            for i in range(sides):
                j = (i + 1) % sides
                f.append((i, j, sides + j, sides + i))
            f.append(tuple(range(sides, 2 * sides)))
        f.append(tuple(reversed(range(sides))))
        return self.mesh(v, f, color, emit)

    def box(self, center, size, color, yaw=0.0, emit=0.0):
        cx, cy, cz = center
        sx, sy, sz = size[0] / 2, size[1] / 2, size[2] / 2
        c, s = math.cos(yaw), math.sin(yaw)
        v = []
        for dz in (-sz, sz):
            for dx, dy in ((-sx, -sy), (sx, -sy), (sx, sy), (-sx, sy)):
                v.append((cx + dx * c - dy * s, cy + dx * s + dy * c, cz + dz))
        f = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
        return self.mesh(v, f, color, emit)

    def ball(self, center, radius, color, emit=0.0, rings=6, squash=1.0):
        cx, cy, cz = center
        seg = rings * 2
        v, f = [(cx, cy, cz + radius * squash)], []
        for r in range(1, rings):
            phi = math.pi * r / rings
            for s in range(seg):
                th = 2 * math.pi * s / seg
                v.append((cx + radius * math.sin(phi) * math.cos(th), cy + radius * math.sin(phi) * math.sin(th),
                          cz + radius * squash * math.cos(phi)))
        v.append((cx, cy, cz - radius * squash))
        last = len(v) - 1
        for s in range(seg):
            f.append((0, 1 + s, 1 + (s + 1) % seg))
            f.append((last, last - seg + (s + 1) % seg, last - seg + s))
        for r in range(rings - 2):
            for s in range(seg):
                a = 1 + r * seg + s
                b = 1 + r * seg + (s + 1) % seg
                f.append((a, a + seg, b + seg, b))
        return self.mesh(v, f, color, emit, smooth=True)


def setup():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 16
    scene.cycles.use_denoising = False
    scene.cycles.use_adaptive_sampling = False
    scene.cycles.max_bounces = 0
    scene.render.film_transparent = True
    scene.render.resolution_x = scene.render.resolution_y = 64 * SS
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "None"
    world = bpy.data.worlds.new("World")
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (0.42, 0.42, 0.5, 1.0)     # soft fill light, slightly cool
    bg.inputs[1].default_value = 1.0
    scene.world = world
    cam_data = bpy.data.cameras.new("FxCam")
    cam_data.type = "ORTHO"
    cam_data.ortho_scale = 2.0
    cam = bpy.data.objects.new("FxCam", cam_data)
    cam.location = (-0.5, 0.5, 20.0)            # the tile centre (0, 0) lands at pixel (48, 48)
    scene.collection.objects.link(cam)
    scene.camera = cam
    sun_data = bpy.data.lights.new("Sun", "SUN")
    sun_data.energy = 3.2
    sun = bpy.data.objects.new("Sun", sun_data)
    # light from the top-left of the screen and above, like the rest of the game's art
    sun.rotation_euler = Vector((0.55, -0.45, -0.7)).to_track_quat("-Z", "Y").to_euler()
    scene.collection.objects.link(sun)
    return scene


def main():
    argv = sys.argv[sys.argv.index("--") + 1:]
    name, frames, out = argv[0], int(argv[1]), argv[2]
    import solids
    build = getattr(solids, name)
    scene = setup()
    fx = Fx(scene)
    os.makedirs(out, exist_ok=True)
    for i in range(frames):
        fx.clear()
        build(fx, solids.frame_time(name, i, frames), i, frames)
        scene.render.filepath = os.path.join(out, "solid_%02d.png" % i)
        bpy.ops.render.render(write_still=True)
    print("rendered", name, frames)


main()
