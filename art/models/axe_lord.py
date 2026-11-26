"""Axe-Lord of the Stair: the Floor 1 floor boss (2x2 tiles), built on art/models/humanoid.py.

ART_REQUESTS.md: "a towering armored warlord in rusted bronze plate with a horned helm and a giant double-bladed axe"
and, for his last phase, "the same warlord now holding a long curved blade instead of the axe, battle-damaged armor".
DESIGN.md 10: marked-tile cleaves; at 60% summons captains; below 25% switches to a long curved blade.
This file draws both looks: axe_lord.py (WEAPON = "axe") and axe_lord_blade.py (WEAPON = "blade", DAMAGED).

Identity (art/OUTFIT_RULES.md step 1; a monster, so O20: no class-outfit signature):
  Silhouette: an UPRIGHT armoured giant (Azhrakkar is the hunched beast; the Axe-Lord stands tall like a statue that
              walks), a closed great-helm with two bone horns curving out and forward like a bull's, broad pauldrons,
              a crimson tabard to the knee, and a great double-bladed axe held upright at his right side, its twin
              crescent blades rising beside the helm so they read from every direction.
  Colours:    rusted bronze plate streaked with teal patina, a ragged crimson tabard with gold trim, dark leather,
              bone horns, pale steel blades, and a gold glow through the visor slit. (Tibia's knights are steel and blue.)
  Details:    visor slit with glowing eyes, engraved lines on the helm, horn rings, a gorget, pauldron rims and rivets,
              a breastplate ridge and a gold stair emblem, patina blotches, a belt with a gold buckle, hip tassets, knee
              cops, gauntlets with gold cuffs, a tabard hem and ragged strips, the axe's socket, top spike, bright
              edges and leather-wrapped haft.
  Attitude:   slow and certain: upright, a heavy measured step, the axe hefting with each stride.
Look-alike: Tibia's Behemoth for size (a 2x2 giant) and the Knight outfit for "armoured warrior"; ours is a bronze
warlord with horns and a tabard, not a steel knight.
"""
from __future__ import annotations

import math

from mathutils import Euler, Matrix, Vector

import humanoid as H

NAME = "axe_lord"
WALK_FRAMES = 8
PALETTE = "axe_lord"
WEAPON = "axe"                # axe_lord_blade.py sets "blade"
DAMAGED = False               # ...and True: a broken horn, cracks in the plate
REFERENCE = "look_55.png"     # Tibia's Behemoth: the size bar for a 2x2 giant (comparison only, never shipped)
HEIGHT_SHEAR = 0.30           # the tilted monster camera, like Azhrakkar: a boss shows its whole front
LEAN = 0.0
AUTO_PLACE = (1, 1)
SIGNATURE = ["horn", "steel", "cloth"]
HEAD_PARTS = ["helm", "visor", "eye", "horn", "nose", "brow"]
LEG_PARTS = ["leg_a", "leg_b", "boot_a", "boot_b", "knee"]
# a Floor 1 boss: big, but smaller than Azhrakkar (0.88-1.05 of the Demon); the closed helm is a small share
CHECK = {"size": (0.80, 1.05), "head": 0.07, "legs_side": 0.03, "legs_updown": 0.02, "eye": 1}

PARTS = H.PARTS + ["helm", "visor", "horn", "bronze", "patina", "cloth", "trim", "emblem", "rivet", "knee",
                   "haft", "wrap", "steel", "edge", "line"]
PIXEL_RULES = H.pixel_rules(
    weight={"eye": 9.0, "horn": 2.4, "steel": 2.0, "edge": 3.0, "trim": 2.4, "emblem": 4.0, "rivet": 4.0,
            "patina": 1.6, "visor": 3.0, "line": 2.6, "wrap": 2.2, "haft": 1.8, "knee": 1.8},
    thin={"horn": 3, "edge": 2, "trim": 2, "emblem": 2, "rivet": 2, "visor": 2, "line": 2, "wrap": 2, "haft": 3},
    soft=[["helm", "visor", "eye", "nose", "brow", "strand", "hair"], ["torso", "bronze", "patina", "emblem", "rivet", "line"],
          ["cloth", "trim"], ["steel", "edge"], ["haft", "wrap"], ["leg_a", "knee"], ["leg_b", "knee"]],
    texture={"torso": [0.30, 0.30], "bronze": [0.30, 0.30], "helm": [0.25, 0.25], "patina": [0.4, 0.3],
             "cloth": [0.40, 0.20], "arm_a": [0.3, 0.25], "arm_b": [0.3, 0.25], "leg_a": [0.35, 0.1], "leg_b": [0.35, 0.1],
             "steel": [0.15, 0.1], "haft": [0.5, 0.0], "horn": [0.4, 0.0]},
    selout=["bronze", "cloth", "helm", "horn"],
)

SPEC = H.spec(
    body_scale=(1.20, 1.20, 1.20), beast=True,
    hip_z=0.40, hip_y=0.120, thigh=0.20, shin=0.20, leg_r=0.078,
    torso_z=0.66, torso_r=(0.175, 0.245, 0.225),
    shoulder_y=0.300, shoulder_z=0.830, upper_arm=0.22, forearm=0.22, arm_r=0.078,
    head_z=0.990, head_r=(0.135, 0.130, 0.150),                          # the closed great-helm
    eye=(0.072, 0.010), eye_r=(0.016, 0.034, 0.011),                    # two glowing slits, wrapping round the visor
    cap=(-0.030, 0.090), cap_r=(0.110, 0.070, 0.060), strands=(-0.9, 0.0, 0.9),   # the cap is the helm's crest
    boot_h=0.10, boot_r=0.085, foot_r=(0.105, 0.075, 0.055),
    stride=0.11, lift=0.050, bob=0.018, arm_swing=0.08, belt_z=0.470,
)
HORN_N = 7


def build(model_cls, facing):
    m = H.build(model_cls, facing, SPEC, PARTS)
    for name in ("head", "neck"):
        m.set_part(name, "helm")
    m.set_part("cap", "helm")
    for k in ("l", "r"):
        m.set_part(f"brow_{k}", "visor")
    for i in range(len(SPEC["strands"])):
        m.set_part(f"strand{i}", "line")                 # engraved lines over the helm
    m.box("visor", "visor", size=(1, 1, 1))
    m.frustum("gorget", "bronze", top_ratio=0.75, segments=16)
    for k in ("l", "r"):
        m.tube(f"horn_{k}", "horn", points=HORN_N)
        m.frustum(f"hornring_{k}", "trim", top_ratio=1.0, segments=10)
        m.ellipsoid(f"pauldron_{k}", "bronze", radii=(0.105, 0.115, 0.046), segments=16, rings=8)   # flat plates, not balls
        m.ellipsoid(f"pauldron2_{k}", "bronze", radii=(0.090, 0.100, 0.036), segments=14, rings=8)
        m.frustum(f"prim_{k}", "trim", top_ratio=1.0, segments=16)
        m.ellipsoid(f"ppatina_{k}", "patina", radii=(0.060, 0.050, 0.020), segments=10, rings=6)
        for j in range(3):
            m.ellipsoid(f"rivet{j}_{k}", "rivet", radii=(0.014, 0.014, 0.014), segments=6, rings=4)
        m.box(f"tasset_{k}", "bronze", size=(0.040, 0.120, 0.150))
        m.ellipsoid(f"kneecop_{k}", "knee", radii=(0.060, 0.064, 0.060), segments=10, rings=6)
    for i in range(2):
        m.ellipsoid(f"patina{i}", "patina", radii=(0.060, 0.070, 0.030), segments=10, rings=6)
    m.capsule("ridge", "line", segments=6)
    m.ellipsoid("emblem", "emblem", radii=(0.020, 0.044, 0.040), segments=8, rings=6)
    for k in ("f", "b"):
        m.box(f"tabard_{k}", "cloth", size=(1, 1, 1))
        m.box(f"hem_{k}", "trim", size=(1, 1, 1))
        m.box(f"rag_{k}", "cloth", size=(1, 1, 1))
    if DAMAGED:
        for i in range(3):
            m.capsule(f"crack{i}", "line", segments=6)
    if WEAPON == "axe":
        m.capsule("haft", "haft", segments=10)
        for i in range(3):
            m.capsule(f"wrap{i}", "wrap", segments=10)
        m.frustum("socket", "bronze", top_ratio=0.85, segments=12)
        m.cone("topspike", "steel", segments=8)
        for k in ("a", "b"):
            m.ellipsoid(f"blade_{k}", "steel", radii=(1, 1, 1), segments=18, rings=10)
            m.ellipsoid(f"bedge_{k}", "edge", radii=(1, 1, 1), segments=18, rings=10)
    else:
        for i in range(3):
            m.box(f"cblade{i}", "steel", size=(1, 1, 1))
            m.box(f"cedge{i}", "edge", size=(1, 1, 1))
        m.capsule("grip", "wrap", segments=8)
        m.capsule("guard", "trim", segments=8)
        m.ellipsoid("pommel", "trim", radii=(0.032, 0.032, 0.032), segments=8, rings=6)
    return m


def _axe_hand(sh, a, walking):
    heft = 0.020 * math.sin(2 * a) if walking else 0.0      # the axe hefts with each heavy step
    return Vector((-0.030, -0.400, 0.470 + heft)) + Vector((0, 0, sh.z - SPEC["shoulder_z"]))   # out and a little back: the blades rise beside the helm, never in front of the visor


def _blade_hand(sh, a, walking):
    heft = 0.020 * math.sin(2 * a) if walking else 0.0      # the blade held out and low, ready
    return Vector((0.200, -0.340, 0.520 + heft)) + Vector((0, 0, sh.z - SPEC["shoulder_z"]))


def _orient(obj, u, w, z):
    """Turn an object so its local x/y/z axes point along u/w/z (keeps its scale)."""
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = Matrix((u, w, z)).transposed().to_quaternion()


def _slab(obj, start, end, width_dir, width, thick):
    d = end - start
    obj.location = (start + end) / 2
    z = d.normalized()
    x = (width_dir - z * width_dir.dot(z)).normalized()
    _orient(obj, x, z.cross(x), z)
    obj.scale = (width, thick, d.length)


def pose(m, t):
    p = H.pose(m, t, hands={"r": _axe_hand if WEAPON == "axe" else _blade_hand})
    up, head, torso, a, walking = p["up"], p["head"], p["torso"], p["a"], p["walking"]
    hr, tr = SPEC["head_r"], SPEC["torso_r"]
    # visor: a dark band across the front of the helm at eye height; the eyes glow in it
    v = m.objects["visor"]
    v.location = head + Vector((hr[0] * 0.80, 0, SPEC["eye"][1] + 0.004))
    v.rotation_mode = "XYZ"
    v.rotation_euler = Euler((0, 0, 0))
    v.scale = (0.040, hr[1] * 1.45, 0.040)
    H.frustum(m, "gorget", torso + Vector((0, 0, tr[2] * 0.78)), (0.130, 0.150), 0.080)
    # horns: out from the helm's sides, then forward and up like a bull's (the left one snapped off when DAMAGED)
    for sign, k in ((1, "l"), (-1, "r")):
        root = head + Vector((-0.045, hr[1] * 0.88 * sign, 0.085))   # high and back: clear of the visor in profile
        length = 0.42 if (DAMAGED and k == "l") else 1.0
        pts, radii = [], []
        for j in range(HORN_N):
            u = j / (HORN_N - 1) * length
            pts.append(root + Vector((0.110 * u * u, sign * (0.160 * u - 0.040 * u * u), 0.170 * u * u + 0.030 * u)))
            radii.append(0.042 * (1 - 0.75 * u) + 0.006)
        m.set_tube(f"horn_{k}", [tuple(q) for q in pts], radii)
        H.frustum(m, f"hornring_{k}", root + Vector((0, 0.020 * sign, -0.020)), (0.040, 0.040), 0.030, rot=(1.57 * sign * -1, 0, 0))
        # pauldrons with a gold rim, three rivets and a patina streak
        sh = p[f"shoulder_{k}"]
        pa = m.objects[f"pauldron_{k}"]
        pa.location = sh + Vector((-0.005, 0.030 * sign, 0.055))
        pa.rotation_mode = "XYZ"
        pa.rotation_euler = Euler((0.55 * sign, 0, 0))
        p2 = m.objects[f"pauldron2_{k}"]                      # a second, lower lame: layered plate, not one dome
        p2.location = sh + Vector((0.000, 0.075 * sign, -0.005))
        p2.rotation_mode = "XYZ"
        p2.rotation_euler = Euler((0.85 * sign, 0, 0))
        H.frustum(m, f"prim_{k}", pa.location + Vector((0, 0.030 * sign, -0.034)), (0.100, 0.108), 0.016, rot=(0.55 * sign, 0, 0))
        m.objects[f"ppatina_{k}"].location = pa.location + Vector((0.030, 0.050 * sign, 0.045))
        for j in range(3):
            m.objects[f"rivet{j}_{k}"].location = pa.location + Vector((0.065 - 0.065 * j, 0.072 * sign, 0.020))
        ta = m.objects[f"tasset_{k}"]
        ta.rotation_mode = "XYZ"
        ta.rotation_euler = Euler((0.22 * sign, 0, 0))
        ta.location = Vector((0.020, 0.215 * sign, SPEC["belt_z"] - 0.075)) + up
        m.objects[f"kneecop_{k}"].location = p[f"knee_{k}"] + Vector((0.050, 0, 0.010))
    # breastplate: a centre ridge, the stair emblem, patina blotches
    m.put_segment("ridge", torso + Vector((tr[0] * 0.98, 0, 0.170)), torso + Vector((tr[0] * 1.00, 0, -0.120)), 0.010)
    m.objects["emblem"].location = torso + Vector((tr[0] * 1.00, 0, 0.060))
    m.objects["patina0"].location = torso + Vector((tr[0] * 0.70, 0.150, -0.020))
    m.objects["patina1"].location = torso + Vector((tr[0] * 0.55, -0.170, 0.110))
    # the crimson tabard, front and back, swaying with the stride; a gold hem and a ragged strip on each
    sway = 0.12 * math.sin(a) if walking else 0.0
    for k, x, lean in (("f", tr[0] * 0.95, 0.10), ("b", -tr[0] * 0.95, -0.10)):
        top = Vector((x, 0, SPEC["belt_z"])) + up
        tilt = lean + (sway if k == "f" else -sway)
        bottom = top + Vector((0.250 * math.sin(tilt), 0, -0.270))
        _slab(m.objects[f"tabard_{k}"], bottom, top, Vector((0, 1, 0)), 0.230, 0.026)
        _slab(m.objects[f"hem_{k}"], bottom, bottom + (top - bottom).normalized() * 0.030, Vector((0, 1, 0)), 0.236, 0.032)
        rag0 = bottom + Vector((0, 0.060, 0))
        _slab(m.objects[f"rag_{k}"], rag0 + Vector((0.020 * math.sin(tilt), 0, -0.070)), rag0, Vector((0, 1, 0)), 0.060, 0.024)
    if DAMAGED:
        for i, (y, z) in enumerate(((0.090, 0.130), (-0.060, 0.020), (0.150, -0.060))):
            q = torso + Vector((tr[0] * 0.96, y, z))
            m.put_segment(f"crack{i}", q, q + Vector((0.004, -0.050, -0.060)), 0.007)
    hand = p["hand_r"]
    if WEAPON == "axe":
        # upright haft, a little forward; twin crescent blades rising beside the helm, turned 45 degrees so their
        # flats face the camera from every direction
        axis = Vector((0.10, 0.0, 1.0)).normalized()
        m.put_segment("haft", hand - axis * 0.360, hand + axis * 0.560, 0.026)
        for i, off in enumerate((-0.020, 0.050, -0.240)):
            m.put_segment(f"wrap{i}", hand + axis * (off - 0.020), hand + axis * (off + 0.020), 0.032)
        top = hand + axis * 0.420     # blades at shoulder height: beside him, never over the visor
        H.frustum(m, "socket", top - axis * 0.080, (0.040, 0.040), 0.160)
        m.put_segment("topspike", hand + axis * 0.545, hand + axis * 0.640, 0.024)
        u = Vector((0.55, 0.83, 0.0)).normalized()     # turned toward the front so the flats read facing south too
        w = axis.cross(u).normalized()
        u = w.cross(axis).normalized()
        for sign, k in ((1, "a"), (-1, "b")):
            c = top + u * 0.120 * sign
            for name, rad, push in ((f"bedge_{k}", (0.150, 0.016, 0.150), 0.018), (f"blade_{k}", (0.130, 0.024, 0.135), 0.0)):
                ob = m.objects[name]
                ob.location = c + u * push * sign
                _orient(ob, u, w, axis)
                ob.scale = rad
    else:
        # a long curved blade held out and up from the right hand, curving back toward the point
        fwd = Vector((0.50, -0.22, 0.84)).normalized()      # held high and forward, a heavy falchion
        m.put_segment("grip", hand - fwd * 0.080, hand + fwd * 0.060, 0.024)
        m.objects["pommel"].location = hand - fwd * 0.095
        side = fwd.cross(Vector((0, 0, 1))).normalized()
        m.put_segment("guard", hand + fwd * 0.070 - side * 0.090, hand + fwd * 0.070 + side * 0.090, 0.022)
        pts = [hand + fwd * 0.080]
        d = fwd.copy()
        for i in range(3):
            d = (d + Vector((0.10, 0.0, -0.16))).normalized()       # the curve
            pts.append(pts[-1] + d * 0.165)
        flat = Vector((0.0, 0.70, 0.70))
        for i in range(3):
            width = 0.130 - 0.025 * i                      # broad near the guard, tapering to the point
            _slab(m.objects[f"cblade{i}"], pts[i], pts[i + 1], flat, width, 0.020)
            wdir = (flat - (pts[i + 1] - pts[i]).normalized() * flat.dot((pts[i + 1] - pts[i]).normalized())).normalized()
            _slab(m.objects[f"cedge{i}"], pts[i] - wdir * width * 0.48, pts[i + 1] - wdir * width * 0.40, flat, 0.018, 0.024)


def assign_depth_parts(m, depth_of):
    return None
