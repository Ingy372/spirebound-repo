"""Briar Mother (Floor 1 hidden mini-boss, woken at a secret in Thornsnap Hollow): model + creep cycle.

gen_monsters.py: "Sssssleep in the thorns." Poison, very slow (speed 80). Until now she borrowed the Thornsnap's sprite.
A money monster (ART_REQUESTS.md Batch 11): the mother of every thornsnap.

Identity (art/CRAWLER_RULES.md step 1):
  Coat:      a squat mound of woven wine-purple bramble on dragging roots, olive leaves, pale ivory thorns (never grass
             green: rule C1; Tibia's carniphila is grass green).
  Signature: THREE thorny stalks rising from the mound, each ending in a snapping bud whose jaws open SIDEWAYS (rule C2)
             on a glowing magenta throat (C3); the middle stalk is the tallest and crowned with a ring of rose petals.
             Small rose-pink blossoms dot the mound.
  Attitude:  rooted and protective: the three heads sway out over her young, slow and patient, jaws snapping in turn.

Detail (art/DETAIL_RULES.md): a mound of overlapping lumps (never one ball) wrapped in bramble strands, thorns in
three sizes, blossoms (big ring, small dots), leaves with pale midribs, roots in two segments dragging the ground.
"""
from __future__ import annotations

import math

from mathutils import Euler, Matrix, Vector

NAME = "briar_mother"
WALK_FRAMES = 8
PALETTE = "briar_mother"
HEIGHT_SHEAR = 0.30
LEAN = 10.0
REFERENCE = "look_120.png"    # Tibia's Carniphila (comparison only, never shipped)
SIZE = 2.1
GROUND_STRETCH = 0.55
AUTO_PLACE = (1, 1)
SIGNATURE = ["bud", "throat", "petal"]
HEAD_PARTS = ["bud", "throat", "petal", "thorn"]
LEG_PARTS = ["root"]
# a rooted plant: her roots are short and mostly under the mound; a mini-boss, so bigger than the look-alike
CHECK = {"size": (0.95, 1.80), "legs_side": 0.02, "legs_updown": 0.01, "eye": 0}

PARTS = ["none", "briar", "vine", "root", "bud", "throat", "petal", "bloom", "thorn", "leaf", "rib", "eye"]
PIXEL_RULES = {
    "weight": {"thorn": 3.2, "throat": 3.4, "bud": 1.7, "petal": 2.0, "bloom": 3.0, "leaf": 1.2, "rib": 2.4,
               "vine": 1.6, "root": 1.4},
    "thin": {"thorn": 2, "throat": 3, "bloom": 2, "leaf": 3, "rib": 2, "vine": 3, "root": 3},
    "soft": [["bud", "throat"], ["leaf", "rib"], ["briar", "bloom"]],
    "no_outline": [],
    "fur": [],
    "texture": {"briar": [0.9, 0.25], "vine": [0.8, 0.1], "bud": [0.6, 0.1], "leaf": [0.6, 0.0], "root": [0.6, 0.0]},
    "bands": [0.42, 0.55, 0.66, 0.75, 0.83, 0.90, 0.96],
    "selout": ["briar", "bud", "petal", "leaf"],
}

MOUND = [((0.00, 0.00, 0.11), (0.20, 0.19, 0.12)), ((0.10, 0.09, 0.09), (0.13, 0.12, 0.09)),
         ((0.08, -0.10, 0.09), (0.13, 0.12, 0.09)), ((-0.12, 0.02, 0.09), (0.14, 0.15, 0.09))]
# the three stalks: (turn outward in radians, height of the head, reach out from the centre, size)
STALKS = {"m": (0.00, 0.37, 0.19, 1.20), "l": (1.05, 0.27, 0.27, 1.0), "r": (-1.05, 0.29, 0.27, 1.0)}   # stems reach out past the mound
ROOTS = [0.6, 1.8, 3.0, 4.2, 5.4]
BLOOMS = [(0.05, 0.13, 0.17), (-0.10, -0.10, 0.17), (0.14, -0.04, 0.16), (-0.16, 0.10, 0.13), (0.02, -0.17, 0.12)]
THORNS = 12
PETALS = 7
LEAVES = {"a": (0.10, 0.20, 0.6), "b": (-0.05, -0.21, -0.5), "c": (-0.20, -0.05, 2.9)}


def build(model_cls, facing):
    m = model_cls(facing, PARTS)
    for i, (_c, r) in enumerate(MOUND):
        m.ellipsoid(f"mound{i}", "briar", radii=r, segments=16, rings=10)
    for i in range(4):
        m.tube(f"strand{i}", "vine", points=7)                          # bramble wrapped over the mound
    for i in range(len(ROOTS)):
        m.tube(f"root{i}", "root", points=5)
    for k in STALKS:
        m.tube(f"stalk_{k}", "vine", points=7)
        for h in ("a", "b"):
            m.ellipsoid(f"jaw_{k}{h}", "bud", radii=(1, 1, 1), segments=14, rings=8)
        m.ellipsoid(f"throat_{k}", "throat", radii=(1, 1, 1), segments=12, rings=6)
        for j in range(4):
            m.cone(f"tooth_{k}{j}", "thorn", segments=5)
        for j in range(2):
            m.cone(f"sthorn_{k}{j}", "thorn", segments=5)
    for j in range(PETALS):
        m.ellipsoid(f"petal{j}", "petal", radii=(0.060, 0.030, 0.012), segments=10, rings=6)
    for j in range(len(BLOOMS)):
        m.ellipsoid(f"bloom{j}", "bloom", radii=(0.030, 0.030, 0.016), segments=8, rings=6)
    for j in range(THORNS):
        m.cone(f"thorn{j}", "thorn", segments=5)
    for k in LEAVES:
        m.ellipsoid(f"leaf_{k}", "leaf", radii=(0.100, 0.040, 0.012), segments=12, rings=6)
        m.ellipsoid(f"rib_{k}", "rib", radii=(0.094, 0.007, 0.015), segments=8, rings=6)
    return m


def _orient(obj, u, w, z):
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = Matrix((u, w, z)).transposed().to_quaternion()


def pose(m, t):
    a = 0.0 if t is None else 2 * math.pi * t
    walking = t is not None
    creep = 0.010 * math.sin(a) if walking else 0.0                # the mound heaves as she drags herself
    for i, (c, r) in enumerate(MOUND):
        m.objects[f"mound{i}"].location = Vector(c) + Vector((creep * (1 if i % 2 else -1), 0, 0.006 * math.sin(a * 2 + i) if walking else 0))
    # bramble strands looping over the mound
    for i in range(4):
        ang = i * math.pi / 4
        d = Vector((math.cos(ang), math.sin(ang), 0))
        pts = [tuple(d * (0.21 * (u - 0.5) * 2) + Vector((0, 0, 0.05 + 0.17 * math.sin(math.pi * u)))) for u in [j / 6 for j in range(7)]]
        m.set_tube(f"strand{i}", pts, [0.016] * 7)
    # roots: out from under the mound to the ground, shuffling forward in turn
    for i, ang in enumerate(ROOTS):
        d = Vector((math.cos(ang), math.sin(ang), 0))
        step = 0.030 * math.sin(a + i * 1.3) if walking else 0.0
        base = d * 0.15 + Vector((0, 0, 0.06))
        knee = d * 0.25 + Vector((step, 0, 0.05))
        foot = d * 0.33 + Vector((step * 1.4, 0, 0.012))
        pts = [tuple(base.lerp(knee, u)) for u in (0, 0.5, 1)] + [tuple(knee.lerp(foot, u)) for u in (0.5, 1)]
        m.set_tube(f"root{i}", pts, [0.030, 0.026, 0.022, 0.016, 0.010])
    # the three stalks and their snapping buds
    for idx, (k, (turn, height, reach, size)) in enumerate(STALKS.items()):
        f = Vector((math.cos(turn), math.sin(turn), 0))
        sway = 0.025 * math.sin(a + idx * 2.1) if walking else 0.0
        base = Vector((0.02, 0, 0.16)) + f * 0.04
        head = f * (reach + sway) + Vector((0, 0, height + 0.010 * math.sin(a * 2 + idx) if walking else height))
        pts = []
        for j in range(7):
            u = j / 6
            q = base.lerp(head, u) + Vector((0, 0, 0.06 * math.sin(math.pi * u))) - f * 0.03 * math.sin(math.pi * u)
            pts.append(tuple(q))
        m.set_tube(f"stalk_{k}", pts, [0.032 - 0.010 * j / 6 for j in range(7)])
        for j in range(2):
            q = Vector(pts[2 + 2 * j])
            side = Vector((-f.y, f.x, 0)) * (1 if j % 2 else -1)
            m.put_segment(f"sthorn_{k}{j}", q, q + side * 0.040 + Vector((0, 0, 0.020)), 0.010, 0.002)
        # jaws open sideways, snapping in turn (one bud after another)
        snap = 0.5 + 0.5 * math.sin(a * 2 + idx * 2.0) if walking else 0.6
        open_ = (0.028 + 0.040 * snap) * size        # wide open: the throat is the point
        side = Vector((-f.y, f.x, 0))
        jaw_r = (0.085 * size, 0.030 * size, 0.064 * size)
        for h, sgn in (("a", 1), ("b", -1)):
            ob = m.objects[f"jaw_{k}{h}"]
            ob.location = head + side * open_ * sgn + f * 0.020
            yaw = sgn * 0.35 * snap
            u = (f * math.cos(yaw) + side * math.sin(yaw)).normalized()
            _orient(ob, u, Vector((0, 0, 1)).cross(u).normalized(), Vector((0, 0, 1)))
            ob.scale = jaw_r
            for j in range(2):                                   # thorn teeth along each jaw rim
                q = ob.location + u * (0.020 + 0.040 * j) * size - side * sgn * jaw_r[1] * 0.6 + Vector((0, 0, 0.020 * size))
                m.put_segment(f"tooth_{k}{j + 2 * (h == 'b')}", q, q - side * sgn * 0.030 * size + Vector((0, 0, 0.010)), 0.010 * size, 0.002)
        th = m.objects[f"throat_{k}"]
        th.location = head + f * 0.020 + Vector((0, 0, 0.012 * size))
        _orient(th, f, side, Vector((0, 0, 1)))
        th.scale = (0.070 * size, max(open_ * 0.9, 0.018), 0.040 * size)
        if k == "m":                                             # the mother's crown: a ring of rose petals
            for j in range(PETALS):
                ang = 2 * math.pi * j / PETALS
                d = side * math.cos(ang) + Vector((0, 0, 1)) * math.sin(ang) * 0.6 - f * 0.4
                ob = m.objects[f"petal{j}"]
                ob.location = head - f * 0.060 * size + d.normalized() * 0.080 * size
                _orient(ob, d.normalized(), f.cross(d.normalized()).normalized() if f.cross(d.normalized()).length > 1e-6 else side,
                        d.normalized().cross(f.cross(d.normalized()).normalized()) if f.cross(d.normalized()).length > 1e-6 else Vector((0, 0, 1)))
    for j, b in enumerate(BLOOMS):
        m.objects[f"bloom{j}"].location = Vector(b)
    for j in range(THORNS):                                      # thorns all over the mound, pointing out
        ang = 2.399 * j
        el = 0.35 + 0.5 * ((j * 7) % 5) / 5
        d = Vector((math.cos(ang) * math.cos(el), math.sin(ang) * math.cos(el), math.sin(el)))
        q = Vector((d.x * 0.19, d.y * 0.18, 0.10 + d.z * 0.12))
        m.put_segment(f"thorn{j}", q, q + d * (0.040 + 0.020 * (j % 3)), 0.012, 0.002)
    for k, (x, y, turn) in LEAVES.items():
        for name in (f"leaf_{k}", f"rib_{k}"):
            ob = m.objects[name]
            ob.location = Vector((x, y, 0.13 + (0.004 if name.startswith("rib") else 0)))
            ob.rotation_mode = "XYZ"
            ob.rotation_euler = Euler((0, -0.35, turn))


def assign_depth_parts(m, depth_of):
    return None
