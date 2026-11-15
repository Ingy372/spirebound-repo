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

Height also leans LEFT: Tibia draws anything tall going up-and-left at 45 degrees (a standing person's head is
up-left of their feet; TibiaWiki's citizen shows it). HEIGHT_SHEAR moves a point left by that much per unit of
height, so on screen height runs diagonally, exactly like hand-made sprites. Standing figures use the full lean;
low animals may use less (HEIGHT_SHEAR in the model file): Tibia's own rat is drawn almost without it, and our
approved rat uses none.

Two projections (PROJECTION in the model file):
  "tilt"    the camera above for low animals (the approved rat): ORTHO camera tilted 45 deg + GROUND_STRETCH.
  "oblique" Tibia's real drawing rule, for standing figures: the camera looks straight down at a slanted world
            (x' = x - k*z, y' = y + k*z, k = HEIGHT_SHEAR). The ground stays full size, the front of a figure is
            seen at full size (faces stay visible under hats), and height slides up-left at 45 degrees. It is the
            same as viewing from the south-east and above, which is why the south and east sides show.

Canvas: like the client, every frame is 64x64 and the creature's own tile is the bottom-right 32x32 quarter;
tall creatures spill up and left into the rest.
"""
from __future__ import annotations

import math

import bpy

ELEVATION = 45.0                       # camera tilt above the horizon, degrees
HEIGHT_FACTOR = math.cos(math.radians(ELEVATION))
GROUND_STRETCH = 0.75
Y_STRETCH = 1.0 + GROUND_STRETCH * (1.0 / math.sin(math.radians(ELEVATION)) - 1.0)
SUPERSAMPLE = 4                         # render at 4x, pixelize.py shrinks to 1x
HEIGHT_SHEAR = HEIGHT_FACTOR           # screen-left shift per unit of height = screen-up shift: a 45 degree lean
VIEW_TILES = 2.0                        # 64x64 canvas; the creature's tile is its bottom-right quarter
PIXELS_PER_TILE = 32
CAM_DISTANCE = 10.0
DEPTH_NEAR = CAM_DISTANCE - 1.5         # depth pass maps [DEPTH_NEAR, DEPTH_NEAR + DEPTH_RANGE] to 0..1
DEPTH_RANGE = 3.0
CAM_SHIFT_X = -0.25                     # moves the creature's tile into the right half of the canvas
CAM_SHIFT_Y = 0.25 + 3.0 / 64.0         # ...and the bottom half, standing ~3 px below the tile centre
TEX_FINE = 48.0                         # surface grain per tile: fine (fur strands, stone chips)...
TEX_STREAK = 0.45                       # fine grain is stretched along each part's length (x), so fur reads as strokes
TEX_COARSE = 5.0                        # ...and coarse (patches, mottling)

# Facing: rotation of the model (which faces east) for each game direction. A creature may add a small "lean"
# (LEAN in its model file): long low animals are drawn slightly diagonal when walking north/south.
DIRECTIONS = {"S": 270.0, "E": 0.0, "N": 90.0, "W": 180.0}
LEAN_SIGN = {"S": -1.0, "E": 0.0, "N": 1.0, "W": 0.0}
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


def add_camera(scene, projection="tilt"):
    cam_data = bpy.data.cameras.new("SpriteCam")
    cam_data.type = "ORTHO"
    cam_data.ortho_scale = VIEW_TILES
    cam_data.shift_x = CAM_SHIFT_X
    cam_data.shift_y = CAM_SHIFT_Y
    cam_data.clip_start = 0.1
    cam_data.clip_end = 50.0
    cam = bpy.data.objects.new("SpriteCam", cam_data)
    if projection == "oblique":
        cam.location = (0.0, 0.0, CAM_DISTANCE)
        cam.rotation_euler = (0.0, 0.0, 0.0)
    else:
        e = math.radians(ELEVATION)
        cam.location = (0.0, -CAM_DISTANCE * math.cos(e), CAM_DISTANCE * math.sin(e))
        cam.rotation_euler = (math.pi / 2 - e, 0.0, 0.0)
    scene.collection.objects.link(cam)
    scene.camera = cam
    return cam


def add_world_root(scene, shear=HEIGHT_SHEAR, projection="tilt"):
    """Everything a creature is made of hangs under these empties: the root applies the Y stretch, and the
    parent-inverse matrix of 'Facing' (a raw matrix, so it can hold a shear) applies the height lean."""
    from mathutils import Matrix
    world_root = bpy.data.objects.new("WorldStretch", None)
    world_root.scale = (1.0, 1.0 if projection == "oblique" else Y_STRETCH, 1.0)
    scene.collection.objects.link(world_root)
    facing = bpy.data.objects.new("Facing", None)
    facing.parent = world_root
    facing.matrix_parent_inverse = Matrix(((1, 0, -HEIGHT_SHEAR, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1)))
    facing.matrix_parent_inverse[0][2] = -shear
    if projection == "oblique":
        facing.matrix_parent_inverse[1][2] = shear
    scene.collection.objects.link(facing)
    return world_root, facing


def world_linear(shear=HEIGHT_SHEAR, projection="tilt"):
    """The 3x3 matrix applied after the creature is turned (stretch @ shear); pixelize.py undoes it for normals."""
    if projection == "oblique":
        return [[1.0, 0.0, -shear], [0.0, 1.0, shear], [0.0, 0.0, 1.0]]
    return [[1.0, 0.0, -shear], [0.0, Y_STRETCH, 0.0], [0.0, 0.0, 1.0]]


def set_direction(facing, d: str, lean: float = 0.0):
    facing.rotation_euler = (0.0, 0.0, math.radians(DIRECTIONS[d] + LEAN_SIGN[d] * lean))


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


def texture_material():
    """Surface grain that sticks to each part as it moves (fur, stone, scales). Red = fine grain, green = coarse.
    Coordinates are the part's own (object) space times its real size (the "tex_scale" property set per frame by
    render_creature.py), so a grain step is about the same number of pixels on every part."""
    m = bpy.data.materials.new("PassTex")
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    at = nt.nodes.new("ShaderNodeAttribute"); at.attribute_type = "OBJECT"; at.attribute_name = "tex_scale"
    mul = nt.nodes.new("ShaderNodeVectorMath"); mul.operation = "MULTIPLY"
    nt.links.new(tc.outputs["Object"], mul.inputs[0])
    nt.links.new(at.outputs["Vector"], mul.inputs[1])
    comb = nt.nodes.new("ShaderNodeCombineColor")
    for i, scale in enumerate((TEX_FINE, TEX_COARSE)):
        nz = nt.nodes.new("ShaderNodeTexNoise")
        nz.inputs["Scale"].default_value = scale
        nz.inputs["Detail"].default_value = 1.0
        src = mul.outputs[0]
        if i == 0:
            st = nt.nodes.new("ShaderNodeVectorMath"); st.operation = "MULTIPLY"
            st.inputs[1].default_value = (TEX_STREAK, 1.0, 1.0)
            nt.links.new(mul.outputs[0], st.inputs[0])
            src = st.outputs[0]
        nt.links.new(src, nz.inputs["Vector"])
        nt.links.new(nz.outputs["Fac"], comb.inputs[i])
    nt.links.new(comb.outputs[0], em.inputs["Color"])
    nt.links.new(em.outputs[0], out.inputs["Surface"])
    return m
