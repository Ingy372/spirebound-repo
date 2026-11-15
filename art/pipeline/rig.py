"""Spirebound sprite rig: the ONE camera, scale and render setup every creature uses.

Runs inside Blender (imported by render_creature.py). Never change these numbers for a single creature:
change them on purpose for all sprites, re-render everything, and log why in PROGRESS.md.

World units: 1 Blender unit = 1 game tile = 32 pixels at 1x.
+X = east, +Y = north, +Z = up. A creature model faces +X (east) in its own space; the rig turns it.

Projection: an orthographic camera tilted down by ELEVATION degrees, looking north. Measured against hand-made
Tibia creatures, their north/south bodies are shortened a little (about 0.9 of the east/west length), so creatures
use GROUND_STRETCH = 0.75, between the plain tilted camera (0) and the unshortened oblique map view (1)
(the world is stretched along Y by 1/sin(ELEVATION) before rendering; pixelize.py un-stretches the normals);
keep it for big objects such as buildings if they ever get rendered here.
"""
from __future__ import annotations

import math

import bpy

ELEVATION = 45.0                       # camera tilt above the horizon, degrees
HEIGHT_FACTOR = math.cos(math.radians(ELEVATION))
GROUND_STRETCH = 0.75
Y_STRETCH = 1.0 + GROUND_STRETCH * (1.0 / math.sin(math.radians(ELEVATION)) - 1.0)
SUPERSAMPLE = 4                         # render at 4x, pixelize.py shrinks to 1x
VIEW_TILES = 1.5                        # the render window is 1.5 x 1.5 tiles around the creature's tile
PIXELS_PER_TILE = 32
CAM_DISTANCE = 10.0
DEPTH_NEAR = CAM_DISTANCE - 1.0         # depth pass maps [DEPTH_NEAR, DEPTH_NEAR + DEPTH_RANGE] to 0..1
DEPTH_RANGE = 2.0
CAM_SHIFT_Y = 3.0 / 48.0               # creatures stand ~3 px below the tile centre, like hand-made sprites

# Facing: rotation of the model (which faces east) for each game direction, plus the small Tibia "lean":
# north/south bodies are drawn slightly diagonal, never perfectly vertical.
DIRECTIONS = {"S": 270.0 - 12.0, "E": 0.0, "N": 90.0 + 12.0, "W": 180.0}
ORDER = ["N", "E", "S", "W"]           # the client's order (pattern x = 0..3)


def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 1
    scene.cycles.use_denoising = False
    scene.cycles.use_adaptive_sampling = False
    scene.cycles.max_bounces = 0
    scene.cycles.pixel_filter_type = "BOX"
    scene.cycles.filter_width = 0.01     # one sharp sample per pixel: exact flat colors, no blending
    scene.render.film_transparent = True
    size = int(round(VIEW_TILES * PIXELS_PER_TILE * SUPERSAMPLE))
    scene.render.resolution_x = scene.render.resolution_y = size
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.image_settings.color_depth = "8"
    names = [i.identifier for i in scene.view_settings.bl_rna.properties["view_transform"].enum_items]
    scene.view_settings.view_transform = "Raw" if "Raw" in names else "Standard"
    scene.view_settings.look = "None"
    scene.view_settings.exposure = 0.0
    scene.view_settings.gamma = 1.0
    scene.display_settings.display_device = "sRGB"
    world = bpy.data.worlds.new("World")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs[1].default_value = 0.0
    scene.world = world
    return scene


def add_camera(scene):
    cam_data = bpy.data.cameras.new("SpriteCam")
    cam_data.type = "ORTHO"
    cam_data.ortho_scale = VIEW_TILES
    cam_data.shift_y = CAM_SHIFT_Y
    cam_data.clip_start = 0.1
    cam_data.clip_end = 50.0
    cam = bpy.data.objects.new("SpriteCam", cam_data)
    e = math.radians(ELEVATION)
    cam.location = (0.0, -CAM_DISTANCE * math.cos(e), CAM_DISTANCE * math.sin(e))
    cam.rotation_euler = (math.pi / 2 - e, 0.0, 0.0)
    scene.collection.objects.link(cam)
    scene.camera = cam
    return cam


def add_world_root(scene):
    """Everything a creature is made of hangs under this empty; it applies the oblique Y stretch."""
    world_root = bpy.data.objects.new("WorldStretch", None)
    world_root.scale = (1.0, Y_STRETCH, 1.0)
    scene.collection.objects.link(world_root)
    facing = bpy.data.objects.new("Facing", None)
    facing.parent = world_root
    scene.collection.objects.link(facing)
    return world_root, facing


def set_direction(facing, d: str):
    facing.rotation_euler = (0.0, 0.0, math.radians(DIRECTIONS[d]))


# ---------------------------------------------------------------- pass materials
def emission_material(name, color):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (*color, 1.0)
    em.inputs["Strength"].default_value = 1.0
    nt.links.new(em.outputs[0], out.inputs["Surface"])
    return m


def id_material(index: int):
    """Part id k is stored as red = 8k/255 (decoded in pixelize.py)."""
    return emission_material(f"ID_{index}", (index * 8 / 255.0, 0.0, 0.0))


def normal_material():
    """World-space normal, packed 0..1 into RGB."""
    m = bpy.data.materials.new("PassNormal")
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    mul = nt.nodes.new("ShaderNodeVectorMath"); mul.operation = "MULTIPLY_ADD"
    mul.inputs[1].default_value = (0.5, 0.5, 0.5)
    mul.inputs[2].default_value = (0.5, 0.5, 0.5)
    nt.links.new(geo.outputs["Normal"], mul.inputs[0])
    nt.links.new(mul.outputs[0], em.inputs["Color"])
    nt.links.new(em.outputs[0], out.inputs["Surface"])
    return m


def depth_material():
    """Distance from the camera along its view axis, mapped into the red channel."""
    m = bpy.data.materials.new("PassDepth")
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    cd = nt.nodes.new("ShaderNodeCameraData")
    sub = nt.nodes.new("ShaderNodeMath"); sub.operation = "SUBTRACT"
    sub.inputs[1].default_value = DEPTH_NEAR
    div = nt.nodes.new("ShaderNodeMath"); div.operation = "DIVIDE"
    div.inputs[1].default_value = DEPTH_RANGE
    div.use_clamp = True
    nt.links.new(cd.outputs["View Z Depth"], sub.inputs[0])
    nt.links.new(sub.outputs[0], div.inputs[0])
    comb = nt.nodes.new("ShaderNodeCombineColor")
    nt.links.new(div.outputs[0], comb.inputs[0])
    nt.links.new(comb.outputs[0], em.inputs["Color"])
    nt.links.new(em.outputs[0], out.inputs["Surface"])
    return m
