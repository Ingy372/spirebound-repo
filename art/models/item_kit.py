"""Shared building blocks for item icons (weapons, jewellery, tools...): still 32x32 sprites made with the creature
pipeline, so items share the monsters' light, palette rules and outline (Jay, 2026-11-27: Grok's items "look like
the art was imported from another game"; "just having you build everything").

An item model file does:   from item_kit import *     then sets NAME, PALETTE, PARTS, PIXEL_RULES and
defines build(model_cls, facing) and pose(m, t). Rules: art/ITEM_RULES.md. Runs inside Blender.

Coordinates (east view, the only one used): x = screen right, y = screen up (north), z = height. 1 unit = 32 px.
Height leans up-left on screen (Tibia's oblique rule), so a thing lying flat is seen straight from above and a
standing thing shows its front and its right side.
"""
from __future__ import annotations

import math

import bmesh
import bpy
from mathutils import Euler, Matrix, Vector

WALK_FRAMES = 1                # a still image: only the standing frame of the east view is used
PROJECTION = "oblique"
AUTO_PLACE = (1, 1)            # render on a big canvas; tools/make_item_icons.py centres it on its 32x32 tile
LEAN = 0.0
SIZE = 1.0
# How far height leans up-left on screen (creatures and the monument use 0.707, a 45 degree lean). With the full lean
# the up-left half of anything lying flat (a blade's lit side) folds out of sight behind its crest, so flat items
# use a gentle 0.3. Standing items (mugs, boots) use STANDING below instead.
HEIGHT_SHEAR = 0.3
BANDS = [0.24, 0.36, 0.47, 0.57, 0.67, 0.77, 0.87]   # 7 thresholds: 8 tones per ramp, like the creatures
# light from the screen's top-left and above (x = right, y = up/north in this view). The shared creature light
# (-0.55, -0.45, 0.7) comes from the south-west, which lights both halves of a flat diagonal blade the same.
LIGHT = [-0.6, 0.5, 0.75]


def assign_depth_parts(m, depth_of):
    return None


# ------------------------------------------------------------------ custom meshes
def _mesh_obj(m, name, part, bm, smooth=True, bevel=0.0, bevel_segments=2):
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    for p in mesh.polygons:
        p.use_smooth = smooth
    obj = bpy.data.objects.new(name, mesh)
    if bevel > 0:
        mod = obj.modifiers.new("bevel", "BEVEL")
        mod.width = bevel
        mod.segments = bevel_segments
        mod.limit_method = "ANGLE"
    return m._register(name, obj, part)


def lathe(m, name, part, profile, segments=24, smooth=True):
    """Revolve a profile [(radius, z), ...] (bottom to top) around the Z axis: mugs, bottles, spyglass tubes,
    knobs. A radius of 0 closes the end."""
    bm = bmesh.new()
    rings = []
    for r, z in profile:
        if r <= 1e-6:
            rings.append([bm.verts.new((0, 0, z))])
            continue
        rings.append([bm.verts.new((r * math.cos(2 * math.pi * i / segments),
                                    r * math.sin(2 * math.pi * i / segments), z)) for i in range(segments)])
    for a, b in zip(rings, rings[1:]):
        if len(a) == 1 and len(b) == 1:
            continue
        if len(a) == 1:
            for i in range(segments):
                bm.faces.new((a[0], b[i], b[(i + 1) % segments]))
        elif len(b) == 1:
            for i in range(segments):
                bm.faces.new((a[i], b[0], a[(i + 1) % segments]))
        else:
            for i in range(segments):
                bm.faces.new((a[i], a[(i + 1) % segments], b[(i + 1) % segments], b[i]))
    for ring in (rings[0], rings[-1]):         # cap open ends
        if len(ring) > 2:
            bm.faces.new(ring if ring is rings[-1] else list(reversed(ring)))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return _mesh_obj(m, name, part, bm, smooth)


def torus(m, name, part, major=0.2, minor=0.05, segments=28, rings=10, squash=1.0):
    """A ring lying flat (in the xy plane). squash < 1 flattens the band's cross-section in z (a signet's band)."""
    bm = bmesh.new()
    grid = []
    for i in range(segments):
        a = 2 * math.pi * i / segments
        row = []
        for j in range(rings):
            b = 2 * math.pi * j / rings
            r = major + minor * math.cos(b)
            row.append(bm.verts.new((r * math.cos(a), r * math.sin(a), minor * math.sin(b) * squash)))
        grid.append(row)
    for i in range(segments):
        for j in range(rings):
            a, b = grid[i], grid[(i + 1) % segments]
            bm.faces.new((a[j], b[j], b[(j + 1) % rings], a[(j + 1) % rings]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return _mesh_obj(m, name, part, bm, True)


def slab(m, name, part, outline, thickness, ridge=0.0, bevel=0.0, smooth=False):
    """A flat shape cut from a 2D outline [(x, y), ...] (counter-clockwise), lying in the xy plane, `thickness`
    thick (z from 0 up). ridge > 0 lifts a crest along the shape's middle (a blade's spine, a leaf's vein): every
    top vertex is raised by ridge * (1 - its distance to the centre line / half width), so the two sides of the
    crest catch the light differently, like a hand-drawn blade with a lit and a shaded half."""
    bm = bmesh.new()
    n = len(outline)
    bot = [bm.verts.new((x, y, 0.0)) for x, y in outline]
    top = [bm.verts.new((x, y, thickness)) for x, y in outline]
    if ridge > 0:
        # centre line = the midpoint between vertex i and its mirror n-1-i (curve_outline goes up one edge and
        # back down the other); a raised vertex there for each pair makes the crest
        mids = []
        for i in range(n // 2):
            j = n - 1 - i
            mx, my = (outline[i][0] + outline[j][0]) / 2, (outline[i][1] + outline[j][1]) / 2
            mids.append(bm.verts.new((mx, my, thickness + ridge)))
        for i in range(n // 2 - 1):
            j = n - 1 - i
            bm.faces.new((top[i], top[i + 1], mids[i + 1], mids[i]))
            bm.faces.new((mids[i], mids[i + 1], top[j - 1], top[j]))
        if n % 2 == 1:                          # odd count: the tip vertex closes the crest
            k = n // 2
            bm.faces.new((top[k - 1], top[k], mids[-1]))
            bm.faces.new((mids[-1], top[k], top[k + 1]))
        else:
            k = n // 2
            bm.faces.new((top[k - 1], top[k], mids[-1]))
        bm.faces.new((top[0], mids[0], top[n - 1]))
    else:
        bm.faces.new(top)
    bm.faces.new(list(reversed(bot)))
    for i in range(n):
        k = (i + 1) % n
        bm.faces.new((bot[i], bot[k], top[k], top[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return _mesh_obj(m, name, part, bm, smooth, bevel)


def curve_outline(spine, widths, steps=None):
    """A blade/leaf outline around a spine [(x, y), ...] with a half-width per spine point: up the left edge,
    back down the right edge (the form slab(ridge=...) expects). The last width 0 makes a point."""
    left, right = [], []
    for i, (p, w) in enumerate(zip(spine, widths)):
        a = spine[min(i + 1, len(spine) - 1)]
        b = spine[max(i - 1, 0)]
        dx, dy = a[0] - b[0], a[1] - b[1]
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        left.append((p[0] + nx * w, p[1] + ny * w))
        right.append((p[0] - nx * w, p[1] - ny * w))
    if widths[-1] == 0:
        right = right[:-1]
    return right + list(reversed(left))


def place(obj, loc=(0, 0, 0), rot=(0, 0, 0), scale=None):
    """Set an object's location, rotation (degrees, XYZ) and optionally scale."""
    obj.location = Vector(loc)
    obj.rotation_mode = "XYZ"
    obj.rotation_euler = Euler(tuple(math.radians(a) for a in rot))
    if scale is not None:
        obj.scale = scale


def diag(t, angle=45.0, length=1.0, origin=(0, 0)):
    """A point a fraction t along a line through origin at `angle` degrees (45 = bottom-left to top-right)."""
    a = math.radians(angle)
    return (origin[0] + math.cos(a) * length * t, origin[1] + math.sin(a) * length * t)


def set_tube_pts(m, name, pts, r):
    """Shape a tube made with m.tube(name, part, points=len(pts)) along pts with radius r (number or list)."""
    radii = r if isinstance(r, (list, tuple)) else [r] * len(pts)
    m.set_tube(name, [(x, y, z) for x, y, z in pts], radii)


# Standing items (mugs, boots): the animals' tilted camera, so we see the front upright and a little of the top,
# lit by the creatures' own light (from the front-left). In the slanted view their visible faces turned away
# from the light and the top filled the picture. A model file does:  globals().update(STANDING)
STANDING = {"PROJECTION": "tilt", "HEIGHT_SHEAR": 0.15, "GROUND_STRETCH": 0.75}
