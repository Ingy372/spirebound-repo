"""Dead bodies for our own monsters (art/CORPSE_RULES.md). Runs inside Blender, like the model files.

A corpse model is a two-line file, art/models/corpse_<monster>.py:

    import corpse_kit
    corpse_kit.make(globals(), "ridgecat")

It reuses the approved monster model (same parts and pixel rules, so the body matches the living monster) and
re-poses it the way Tibia's own corpses are drawn (rules C1-C6), seen from the same camera as the living sprite:
  - corpse_<monster>.py: the dead body. Four-legged animals slump forward: chest and belly on the ground, the
    legs buckled under and splayed out, the head dropped to the ground ahead of the chest, the tail limp.
    (Blood and wounds are painted afterwards by tools/make_corpse_sheets.py, C4.)
    The rotting step is this body greyed, its wounds opened and ribs showing (2D, C5).
  - corpse_<monster>_bones.py (bones=True): the skeleton in the same pose (C6): fur, ears and soft parts gone, every limb thinned to
    bone, a ribcage over the spine, the skull and any horns or tusks kept so the animal can still be named.
    Coloured with the "<palette>_bones" ramp set (art/pipeline/corpse_palettes.py).
"""
from __future__ import annotations

import importlib
import math

import bpy
from mathutils import Matrix, Vector

COPY = ("PARTS", "PALETTE", "PIXEL_RULES", "SIZE", "HEIGHT_SHEAR", "PROJECTION", "GROUND_STRETCH", "REFERENCE",
        "CANVAS_OFFSET")
SOFT = ("ear", "muscle", "belly", "crest", "mane", "fur", "tuft", "brow", "stripe", "band", "spot",
        "blotch", "pouch", "bristle", "wool", "line", "scarf", "hair", "strand")
SOCKETS = ("eye", "nose")
KEEP = ("head", "snout", "horn", "tusk", "tooth", "fang", "claw", "jaw", "skull", "spike", "spine_", "beak")
RIBS = 4
CLOTH = ("robe", "hem", "shroud", "hood", "cloak", "cape", "tatter", "jerkin")


def _n_of(m, o):
    return next((n for n, x in m.objects.items() if x is o), "")


def is_quadruped(m):
    return hasattr(m, "spec") and "fl_up" in m.objects


def make(g, base_name, drop=0.62, head_drop=1.0, splay=1.0, lie_tilt=0.0, bones=False, mode="slump", fall=0.8,
         seed=1, keep=(1.0, 0.7, 0.4), pile=(1.35, 0.28), scatter=0.25,
         cloth=(1.25, 0.22), hide=(), soft=()):
    """mode: "slump" (an animal with no fitting Tibia corpse: dies in its own pose, see slump()), "shatter" (golems,
    constructs and skeletons fall apart into their own pieces, C7), "pile" (spirits leave their robe crumpled flat).
    shatter/pile render three decay steps as frames 0-2: keep = share of the pieces still there at each step;
    fall = how far the pieces land from where they stood (in tiles per tile of height); pile = (spread, height).
    drop: how far the torso sinks (share of its standing height above the ground it keeps: lower = flatter).
    head_drop: 1 = chin on the ground. splay: how far the folded legs stick out. lie_tilt: roll toward the viewer."""
    base = importlib.import_module(base_name)
    for k in COPY:
        if hasattr(base, k):
            g[k] = getattr(base, k)
    g["AUTO_PLACE"] = (1, 1)         # C2: against the tile's right and bottom edges, like Tibia's corpses
    g["LEAN"] = 0.0
    g["WALK_FRAMES"] = 1 if mode == "slump" else 2   # shatter/pile: frames 0, 1, 2 = the three decay steps
    g["NAME"] = "corpse_" + base_name + ("_bones" if bones else "")
    if bones:                        # corpse_<monster>_bones.py: the skeleton, coloured as bone
        g["PALETTE"] = base.PALETTE + "_bones"
    g["BASE"] = base_name

    def build(model_cls, facing):
        lying = bpy.data.objects.new("Lying", None)
        lying.parent = facing
        bpy.context.scene.collection.objects.link(lying)
        m = base.build(model_cls, lying)
        m._lying = lying
        m._spec0 = dict(m.spec) if hasattr(m, "spec") else None
        m._basis0 = {n: o.matrix_basis.copy() for n, o in m.objects.items()}
        if is_quadruped(m):
            for i in range(RIBS):
                for k in ("l", "r"):
                    m.tube(f"crib{i}{k}", "body", points=6)
            m.tube("cspine", "body", points=8)
        return m

    def slump(m):
        """C3: re-pose a quadruped as a dead body. Changes the spec the base pose reads, so the creature's own
        extras (tusks, crest, horns) follow the head and body anchors down."""
        s0 = m._spec0
        s = dict(s0)
        ground = s0["paw_r"][2]
        sink = lambda z, r: r + (z - r) * (1 - drop) if z > r else z      # keep (1-drop) of the height above r
        s["chest"] = (s0["chest"][0], sink(s0["chest"][1], s0["chest_r"][2] * 0.9))
        s["hip"] = (s0["hip"][0] - 0.01, sink(s0["hip"][1], s0["hip_r"][2] * 0.95))
        hz = s0["head_r"][2] * (1.0 + 0.4 * (1 - head_drop))
        s["head"] = (s0["head"][0] + 0.03, sink(s0["head"][1], hz) if head_drop < 1 else hz)
        s["snout_tip"] = (s0["snout_tip"][0] + 0.035, max(s0["snout_r"][0] * 0.9, s["head"][1] - 0.03))
        dz = s0["chest"][1] - s["chest"][1]
        s["leg_top_z"] = s0["leg_top_z"] - dz
        s["tail_raise"] = min(s0["tail_raise"], 0.95)          # limp, along the ground
        s["tail_curl"] = 0.06
        m.spec = s
        return s, ground

    def legs_folded(m, s, ground):
        """front legs stretched forward along the ground, hind legs tucked forward under the hip, both splayed"""
        Q = importlib.import_module("quadruped")
        for leg in Q.LEG_PHASE:
            front, sign = leg[0] == "f", (-1 if leg[1] == "l" else 1)
            top = m.objects[f"{leg}_muscle"].location - Vector((0, sign * 0.004, 0.015))
            reach = (s["upper"] + s["lower"]) * 0.92
            if front:
                foot = top + Vector((reach * 0.85, sign * 0.05 * splay, 0))
            else:
                foot = top + Vector((reach * 0.55, sign * 0.07 * splay, 0))
            foot.z = ground
            d = foot - top
            if d.length > reach:                               # stay reachable: pull the foot in along the ground
                flat = Vector((d.x, d.y, 0))
                need = math.sqrt(max(reach ** 2 - (top.z - ground) ** 2, 1e-6))
                foot = Vector((top.x, top.y, ground)) + flat.normalized() * need
            Q._leg(m, s, leg, top, foot, front)

    def to_bones(m, s):
        """C6: the same pose as a skeleton"""
        chest, hip = m.objects["chest"].location.copy(), m.objects["hip"].location.copy()
        for name, o in m.objects.items():
            if name.startswith(("crib", "cspine")):
                o.hide_render = False
                continue
            n = name.lower()
            if n.startswith(SOCKETS):                          # dark sockets in the skull (bone palette)
                o.scale = tuple(c * 1.3 for c in o.scale)
                continue
            if any(k in n for k in SOFT) and not any(k in n for k in KEEP):
                o.hide_render = True
                continue
            if name in ("chest", "hip"):
                o.hide_render = True                           # the ribcage and spine take their place
                continue
            if o.type == "MESH" and not any(k in n for k in KEEP):
                sc = list(o.scale)
                if name.endswith(("_up", "_lo")):              # put_segment: (r0, r1, length)
                    o.scale = (sc[0] * 0.45, sc[1] * 0.45, sc[2])
                else:                                          # ellipsoid: keep the longest axis
                    big = max(range(3), key=lambda i: abs(sc[i]))
                    o.scale = tuple(sc[i] if i == big else sc[i] * 0.4 for i in range(3))
            elif o.type == "MESH" and name == "head":
                o.scale = tuple(c * 0.85 for c in o.scale)     # a skull is a little smaller than the head
        # spine from the skull to the hip, ribs hanging from it over the chest
        top_c = chest + Vector((0, 0, s["chest_r"][2] * 0.85))
        top_h = hip + Vector((0, 0, s["hip_r"][2] * 0.8))
        head = m.objects["head"].location
        pts = [head.lerp(top_c, 0.5)] + [top_c.lerp(top_h, i / 6) for i in range(7)]
        m.set_tube("cspine", [tuple(p) for p in pts], [0.014] * 8)
        for i in range(RIBS):
            u = 0.1 + 0.8 * i / (RIBS - 1)
            root = top_c.lerp(top_h, u * 0.75)
            depth = s["chest_r"][2] * (1.6 - 0.6 * u)
            width = s["chest_r"][1] * (1.05 - 0.35 * u)
            for sign, k in ((1, "l"), (-1, "r")):
                rp = []
                for j in range(6):
                    a = j / 5 * math.pi * 0.62
                    rp.append(tuple(root + Vector((-0.01 * j, sign * width * math.sin(a), -depth * (1 - math.cos(a)) * 0.9))))
                rp = [(x, y, max(z, 0.008)) for x, y, z in rp]
                m.set_tube(f"crib{i}{k}", rp, [0.012] * 6)

    def shatter(m, t):
        """C7: the figure falls apart where it stood. Every piece lands on the ground, thrown up-left by its height
        (Tibia's broken golems spread over the tile and the ones up-left of it), long pieces lying flat."""
        import random
        rng = random.Random(seed)
        P = m._lying
        Pw = P.matrix_world.copy()
        Pinv = Pw.inverted()
        objs = [o for _n, o in sorted(m.objects.items()) if o.type in ("MESH", "CURVE")]
        bpy.context.view_layer.update()
        ranks = list(range(len(objs)))
        rng.shuffle(ranks)
        step = 0 if t is None else (1 if t < 0.25 else 2)
        for k, o in enumerate(objs):
            box = [Pinv @ (o.matrix_world @ Vector(c)) for c in o.bound_box]
            lo = Vector((min(p.x for p in box), min(p.y for p in box), min(p.z for p in box)))
            hi = Vector((max(p.x for p in box), max(p.y for p in box), max(p.z for p in box)))
            c, e = (lo + hi) / 2, hi - lo
            part = m.part_of.get(_n_of(m, o), "")
            if any(k in part for k in CLOTH + tuple(soft)):                  # cloth sinks into a crumpled heap where it was
                spin = Matrix.Rotation(math.radians(rng.uniform(-20, 20)), 4, "Z")
                land = Vector((c.x - 0.2 * c.z * fall, c.y + 0.15 * c.z * fall, 0.0))
                M = Matrix.Translation(land) @ spin @ Matrix.Diagonal((cloth[0], cloth[0], cloth[1], 1.0)) @ Matrix.Translation(-c)
            else:                                              # solid pieces are thrown apart and lie flat
                tall = e.z > 1.4 * max(e.x, e.y)
                tip = Matrix.Rotation(math.radians(90 if tall else rng.uniform(-25, 25)), 4, "X")
                spin = Matrix.Rotation(math.radians(rng.uniform(0, 360)), 4, "Z")
                a, r = rng.uniform(0, 2 * math.pi), rng.uniform(0.3, 1.0) * scatter
                land = Vector((c.x - 0.55 * c.z * fall + r * math.cos(a),
                               c.y + 0.45 * c.z * fall + r * math.sin(a), 0.0))
                M = Matrix.Translation(land) @ spin @ tip @ Matrix.Translation(-c)
            o.matrix_world = Pw @ M @ Pinv @ o.matrix_world
            bpy.context.view_layer.update()
            zs = [(Pinv @ (o.matrix_world @ Vector(cc))).z for cc in o.bound_box]
            o.matrix_world = Pw @ Matrix.Translation((0, 0, -min(zs))) @ Pinv @ o.matrix_world
            o.hide_render = ranks[k] >= keep[step] * len(objs) or part in hide
        for n, o in m.objects.items():                         # dead: no glow left in the eyes
            if n.startswith(("eye", "visor", "flame")) and step > 0:
                o.hide_render = True

    def crumple(m, t):
        """C8: a spirit's robe sinks into a crumpled heap where it hovered; it shrinks to a rag as it fades"""
        step = 0 if t is None else (1 if t < 0.25 else 2)
        spread, height = pile
        sx = spread * (1.0, 1.05, 0.8)[step]
        m._lying.scale = (sx, sx, height * (1.0, 0.85, 0.7)[step])
        for n, o in m.objects.items():
            if n.startswith(("eye", "face")):
                o.hide_render = True

    def pose(m, t):
        quad = is_quadruped(m)
        lying = m._lying
        lying.rotation_euler = (math.radians(lie_tilt), 0.0, 0.0)
        lying.location = (0.0, 0.0, 0.0)
        lying.scale = (1.0, 1.0, 1.0)
        for name, o in m.objects.items():
            o.hide_render = name.startswith(("crib", "cspine"))
            if name in m._basis0:                              # undo the last frame's shatter before re-posing
                o.matrix_basis = m._basis0[name]
        if mode == "shatter":
            base.pose(m, None)
            shatter(m, t)
        elif mode == "pile":
            base.pose(m, None)
            crumple(m, t)
        elif quad:
            s, ground = slump(m)
            base.pose(m, None)
            legs_folded(m, s, ground)
            if not bones:                                      # C3: dead eyes are shut (no bright eye)
                for name, o in m.objects.items():
                    if name.startswith("eye"):
                        o.hide_render = True
        else:
            base.pose(m, None)
        bpy.context.view_layer.update()
        inv = lying.parent.matrix_world.inverted()
        pts = [inv @ (o.matrix_world @ Vector(c)) for o in lying.children_recursive if o.type == "MESH"
               and not o.hide_render for c in o.bound_box]
        lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
        hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
        # C1: resting on the ground, centred on its tile
        lying.location = (-(lo.x + hi.x) / 2, -(lo.y + hi.y) / 2, -lo.z)
        if quad and bones:            # after placing the body, so the skeleton lies exactly where the body lay
            to_bones(m, s)
        if quad:
            m.spec = m._spec0
        bpy.context.view_layer.update()

    g["build"] = build
    g["pose"] = pose
    g["assign_depth_parts"] = getattr(base, "assign_depth_parts", lambda m, depth_of: None)
