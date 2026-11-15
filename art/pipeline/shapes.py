"""Small building blocks for creature models (runs inside Blender).

Creatures are built from a few smooth low-poly shapes. Each shape carries a "part" name; the part decides its
flat id color in the id pass and therefore its palette ramp in pixelize.py.
"""
from __future__ import annotations

import bpy
from mathutils import Vector


class Model:
    def __init__(self, facing, parts: list[str]):
        self.facing = facing
        self.parts = parts                       # index 0 is reserved for "nothing"
        self.objects: dict[str, bpy.types.Object] = {}
        self.part_of: dict[str, str] = {}
        self.id_mats = {}

    def part_id(self, part):
        return self.parts.index(part)

    def id_mat(self, part):
        from rig import id_material
        if part not in self.id_mats:
            self.id_mats[part] = id_material(self.part_id(part))
        return self.id_mats[part]

    def _register(self, name, obj, part):
        obj.name = name
        obj.parent = self.facing
        bpy.context.scene.collection.objects.link(obj) if obj.name not in bpy.context.scene.collection.objects else None
        self.objects[name] = obj
        self.set_part(name, part)
        return obj

    def set_part(self, name, part):
        obj = self.objects[name]
        self.part_of[name] = part
        obj.data.materials.clear()
        obj.data.materials.append(self.id_mat(part))

    def ellipsoid(self, name, part, loc=(0, 0, 0), radii=(1, 1, 1), segments=16, rings=10):
        mesh = bpy.data.meshes.new(name)
        import bmesh
        bm = bmesh.new()
        bmesh.ops.create_uvsphere(bm, u_segments=segments, v_segments=rings, radius=1.0)
        bm.to_mesh(mesh)
        bm.free()
        for p in mesh.polygons:
            p.use_smooth = True
        obj = bpy.data.objects.new(name, mesh)
        obj.location = loc
        obj.scale = radii
        return self._register(name, obj, part)

    def cone(self, name, part, segments=12):
        """Unit cone along +Z from base (z=0, radius 1) to tip (z=1). Place it with put_segment()."""
        import bmesh
        mesh = bpy.data.meshes.new(name)
        bm = bmesh.new()
        bmesh.ops.create_cone(bm, cap_ends=True, segments=segments, radius1=1.0, radius2=0.0, depth=1.0)
        bmesh.ops.translate(bm, verts=bm.verts, vec=(0, 0, 0.5))
        bm.to_mesh(mesh)
        bm.free()
        for p in mesh.polygons:
            p.use_smooth = True
        obj = bpy.data.objects.new(name, mesh)
        return self._register(name, obj, part)

    def capsule(self, name, part, segments=10):
        """Unit tube along +Z from 0 to 1 with round ends (radius 1 before scaling). Place it with put_segment()."""
        import bmesh
        mesh = bpy.data.meshes.new(name)
        bm = bmesh.new()
        bmesh.ops.create_cone(bm, cap_ends=True, segments=segments, radius1=1.0, radius2=1.0, depth=1.0)
        bmesh.ops.translate(bm, verts=bm.verts, vec=(0, 0, 0.5))
        bm.to_mesh(mesh)
        bm.free()
        for p in mesh.polygons:
            p.use_smooth = True
        obj = bpy.data.objects.new(name, mesh)
        return self._register(name, obj, part)

    def tube(self, name, part, points: int = 10):
        """A bevelled poly curve (tails, whiskers). Shape it every frame with set_tube()."""
        cu = bpy.data.curves.new(name, "CURVE")
        cu.dimensions = "3D"
        cu.bevel_depth = 1.0
        cu.bevel_resolution = 3
        cu.use_fill_caps = True
        sp = cu.splines.new("POLY")
        sp.points.add(points - 1)
        obj = bpy.data.objects.new(name, cu)
        return self._register(name, obj, part)

    # ------------------------------------------------------------ posing helpers
    def put_segment(self, name, p0, p1, r0, r1=None):
        """Stretch a unit cone/capsule between points p0 and p1 with radius r0 (and r1 across the other axis)."""
        obj = self.objects[name]
        p0, p1 = Vector(p0), Vector(p1)
        d = p1 - p0
        obj.location = p0
        obj.rotation_mode = "QUATERNION"
        obj.rotation_quaternion = d.to_track_quat("Z", "Y")
        obj.scale = (r0, r1 if r1 is not None else r0, max(d.length, 1e-4))

    def set_tube(self, name, pts, radii):
        sp = self.objects[name].data.splines[0]
        for p, co, r in zip(sp.points, pts, radii):
            p.co = (co[0], co[1], co[2], 1.0)
            p.radius = r
