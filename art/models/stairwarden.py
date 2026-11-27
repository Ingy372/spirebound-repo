"""Stairwarden: the Floor 1 labyrinth's own guard (roadmap RV5), built on art/models/humanoid.py (first draft, 2026-11-27).

Story (docs/superpowers/specs/2026-11-27-floor1-depth-design.md): the First Climb left a garrison behind; the Axe-Lord
was their rearguard captain, ordered to let nobody follow. The Stairwardens are that garrison's maze guards: empty suits
of the First Climb's armour that still walk their corridors. Nobody is inside; a cold light is.

Identity (art/OUTFIT_RULES.md step 1; a monster, so O20: no class-outfit signature):
  Silhouette: a soldier-sized upright figure (the Axe-Lord is the giant; this is one of his men), a tall narrow
              sallet helm with a crest ridge, a long halberd held upright at the right side with its axe blade and
              spike above the helm, a faded tabard, and gaps at the neck, elbows and knees where you see into the
              empty armour (cold light, no body).
  Colours:    blackened iron plate with worn grey-steel edges, a faded slate-blue tabard with the First Climb's pale
              spire on the chest, dark leather, a cold blue-white light in the visor and the gaps. (The Axe-Lord is
              rusted bronze, crimson and gold glow; Tibia's skeleton warriors are bone and brown.)
  Details:    visor slit with two cold eyes, a crest ridge on the helm, a gorget, small pauldrons with a rivet,
              elbow and knee cops, a frayed tabard hem, the halberd's axe head, top spike and back hook, a leather
              strap on the haft.
  Attitude:   a patrol's measured step, the halberd kept upright: it guards, it does not hunt.
Look-alike: Tibia's Skeleton Warrior (an undead armed guard) and the Knight outfit (an armoured soldier); ours is an
empty suit of blackened plate with cold light inside and a halberd, never bone.
Addons: none (a monster, rule A1).
"""
from __future__ import annotations

import math

from mathutils import Euler, Matrix, Vector

import humanoid as H

NAME = "stairwarden"
WALK_FRAMES = 8
PALETTE = "stairwarden"
REFERENCE = "outfit_128.png"
PROJECTION = "oblique"
CANVAS_OFFSET = H.CANVAS_OFFSET
SIGNATURE = ["glow", "steel", "cloth"]
HEAD_PARTS = ["helm", "visor", "eye", "crest", "brow", "nose"]
LEG_PARTS = ["leg_a", "leg_b", "boot_a", "boot_b", "knee"]
CHECK = {"size": (0.85, 1.45), "head": 0.07, "legs_side": 0.03, "eye": 1}

PARTS = H.PARTS + ["helm", "visor", "crest", "plate", "edge", "cloth", "hem", "emblem", "rivet", "knee", "glow",
                   "haft", "strap", "steel"]
PIXEL_RULES = H.pixel_rules(
    weight={"eye": 9.0, "glow": 6.0, "crest": 2.4, "edge": 3.0, "hem": 2.4, "emblem": 4.5, "rivet": 4.0,
            "visor": 3.0, "strap": 2.2, "haft": 1.8, "steel": 2.2, "knee": 1.8},
    thin={"crest": 2, "edge": 2, "hem": 2, "emblem": 2, "rivet": 2, "visor": 2, "strap": 2, "haft": 3,
          "glow": 2},
    soft=[["helm", "visor", "eye", "nose", "brow", "strand", "hair", "crest"], ["torso", "plate", "rivet"],
          ["cloth", "hem", "emblem"], ["steel", "edge"], ["haft", "strap"], ["leg_a", "knee"], ["leg_b", "knee"]],
    texture={"torso": [0.30, 0.25], "plate": [0.30, 0.25], "helm": [0.25, 0.20], "cloth": [0.45, 0.20],
             "arm_a": [0.3, 0.2], "arm_b": [0.3, 0.2], "leg_a": [0.3, 0.1], "leg_b": [0.3, 0.1], "haft": [0.5, 0.0]},
    selout=["plate", "cloth", "helm"],
    no_outline=["glow"],                     # the light shows THROUGH the gaps: no dark rim round it
)

SPEC = H.spec(
    body_scale=(1.24, 1.28, 1.06), beast=True,
    torso_r=(0.110, 0.160, 0.190), arm_r=0.048, leg_r=0.052,
    head_z=0.965, head_r=(0.110, 0.102, 0.122),                          # a sallet: a little taller than round
    eye=(0.040, 0.010), eye_r=(0.014, 0.026, 0.012),                    # two cold slits in the visor
    cap=(-0.040, 0.050), cap_r=(0.090, 0.040, 0.045), strands=(-0.8, 0.8),   # the cap is the helm's crest base
    boot_h=0.12, boot_r=0.060, foot_r=(0.080, 0.050, 0.046),
    stride=0.12, lift=0.050, bob=0.014, arm_swing=0.07, belt_z=0.540,
)
GAPS = ["neck", "waist", "elbow_l", "elbow_r", "knee_l", "knee_r"]


def build(model_cls, facing):
    m = H.build(model_cls, facing, SPEC, PARTS)
    for name in ("head", "neck"):
        m.set_part(name, "helm")
    m.set_part("cap", "helm")
    for k in ("l", "r"):
        m.set_part(f"brow_{k}", "visor")
    for i in range(len(SPEC["strands"])):
        m.set_part(f"strand{i}", "crest")                # rivet lines over the helm
    m.box("visor", "visor", size=(1, 1, 1))
    m.tube("crest", "crest", points=6)
    m.frustum("gorget", "plate", top_ratio=0.80, segments=16)
    for g in GAPS:
        m.ellipsoid(f"gap_{g}", "glow", radii=(1, 1, 1), segments=10, rings=6)
    for k in ("l", "r"):
        m.ellipsoid(f"pauldron_{k}", "plate", radii=(0.070, 0.080, 0.034), segments=14, rings=8)
        m.frustum(f"prim_{k}", "edge", top_ratio=1.0, segments=14)
        m.ellipsoid(f"rivet_{k}", "rivet", radii=(0.012, 0.012, 0.012), segments=6, rings=4)
        m.ellipsoid(f"kneecop_{k}", "knee", radii=(0.044, 0.048, 0.044), segments=10, rings=6)
        m.ellipsoid(f"couter_{k}", "plate", radii=(0.034, 0.036, 0.034), segments=8, rings=6)
    for k in ("f", "b"):
        m.box(f"tabard_{k}", "cloth", size=(1, 1, 1))
        m.box(f"hem_{k}", "hem", size=(1, 1, 1))
        m.box(f"rag_{k}", "cloth", size=(1, 1, 1))
    m.box("emblem", "emblem", size=(1, 1, 1))           # the First Climb's pale spire: a tall thin bar on a base
    m.box("emblem_base", "emblem", size=(1, 1, 1))
    m.capsule("haft", "haft", segments=10)
    m.capsule("strap", "strap", segments=10)
    m.box("axehead", "steel", size=(1, 1, 1))
    m.box("axeedge", "edge", size=(1, 1, 1))
    m.cone("topspike", "steel", segments=8)
    m.cone("hook", "steel", segments=6)
    return m


def _halberd_hand(sh, a, walking):
    heft = 0.012 * math.sin(2 * a) if walking else 0.0
    return Vector((-0.070, -0.300, 0.500 + heft))   # out and a little back: the halberd never covers the visor + Vector((0, 0, sh.z - SPEC["shoulder_z"]))


def _orient(obj, u, w, z):
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
    p = H.pose(m, t, hands={"r": _halberd_hand})
    up, head, torso, a, walking = p["up"], p["head"], p["torso"], p["a"], p["walking"]
    hr, tr = SPEC["head_r"], SPEC["torso_r"]
    v = m.objects["visor"]
    v.location = head + Vector((hr[0] * 0.90, 0, SPEC["eye"][1] + 0.002))   # the slit band on the helm's face
    for k in ("l", "r"):                    # the cold eyes glow a little in front of the slit, so every view sees them
        m.objects[f"eye_{k}"].location += Vector((0.026, 0, 0))
    v.rotation_mode = "XYZ"
    v.rotation_euler = Euler((0, 0, 0))
    v.scale = (0.030, hr[1] * 1.55, 0.044)
    # crest ridge front to back over the helm, rising a little at the back (the sallet's tail)
    crest = [head + Vector((0.090 - 0.040 * j, 0, hr[2] * 0.96 + 0.010 * math.sin(j * 0.6))) for j in range(6)]
    m.set_tube("crest", [tuple(q) for q in crest], [0.008, 0.010, 0.012, 0.012, 0.010, 0.008])
    H.frustum(m, "gorget", torso + Vector((0, 0, tr[2] * 0.80)), (0.090, 0.110), 0.060)
    # the empty inside shows at the gaps: a small cold light at the neck, elbows and knees
    m.objects["gap_neck"].location = head + Vector((0.030, 0, -hr[2] * 0.95))
    m.objects["gap_neck"].scale = (0.075, 0.090, 0.030)
    # a band of light between the breastplate and the belt, seen from every side (the tabard covers front and back)
    m.objects["gap_waist"].location = Vector((0, 0, SPEC["belt_z"] + 0.045)) + up
    m.objects["gap_waist"].scale = (tr[0] * 1.06, tr[1] * 1.06, 0.022)
    for sign, k in ((1, "l"), (-1, "r")):
        m.objects[f"gap_elbow_{k}"].location = p[f"elbow_{k}"] + Vector((0.020, 0.010 * sign, -0.012))
        m.objects[f"gap_elbow_{k}"].scale = (0.036, 0.040, 0.024)
        m.objects[f"gap_knee_{k}"].location = p[f"knee_{k}"] + Vector((0.026, 0, -0.030))
        m.objects[f"gap_knee_{k}"].scale = (0.040, 0.044, 0.024)
        sh = p[f"shoulder_{k}"]
        pa = m.objects[f"pauldron_{k}"]
        pa.location = sh + Vector((-0.005, 0.020 * sign, 0.040))
        pa.rotation_mode = "XYZ"
        pa.rotation_euler = Euler((0.50 * sign, 0, 0))
        H.frustum(m, f"prim_{k}", pa.location + Vector((0, 0.020 * sign, -0.026)), (0.068, 0.074), 0.012, rot=(0.50 * sign, 0, 0))
        m.objects[f"rivet_{k}"].location = pa.location + Vector((0.040, 0.050 * sign, 0.020))
        m.objects[f"kneecop_{k}"].location = p[f"knee_{k}"] + Vector((0.040, 0, 0.012))
        m.objects[f"couter_{k}"].location = p[f"elbow_{k}"] + Vector((-0.020, 0.008 * sign, 0.010))
    # faded tabard front and back, swaying a little; frayed hem; the spire on the chest
    sway = 0.08 * math.sin(a) if walking else 0.0
    for k, x, lean in (("f", tr[0] * 0.98, 0.08), ("b", -tr[0] * 0.98, -0.08)):
        top = Vector((x, 0, SPEC["belt_z"] + 0.230)) + up
        tilt = lean + (sway if k == "f" else -sway)
        bottom = top + Vector((0.200 * math.sin(tilt), 0, -0.420))
        _slab(m.objects[f"tabard_{k}"], bottom, top, Vector((0, 1, 0)), 0.200, 0.022)
        _slab(m.objects[f"hem_{k}"], bottom, bottom + (top - bottom).normalized() * 0.028, Vector((0, 1, 0)), 0.204, 0.028)
        rag0 = bottom + Vector((0, -0.055, 0))
        _slab(m.objects[f"rag_{k}"], rag0 + Vector((0.015 * math.sin(tilt), 0, -0.060)), rag0, Vector((0, 1, 0)), 0.050, 0.020)
    chest = torso + Vector((tr[0] * 1.00 + 0.022, 0, 0.040))
    _slab(m.objects["emblem"], chest + Vector((0, 0, -0.070)), chest + Vector((0, 0, 0.080)), Vector((0, 1, 0)), 0.026, 0.010)
    _slab(m.objects["emblem_base"], chest + Vector((0, 0, -0.080)), chest + Vector((0, 0, -0.060)), Vector((0, 1, 0)), 0.080, 0.010)
    # halberd: upright haft, axe head and spike above the helm, a hook at the back, a leather strap at the grip
    hand = p["hand_r"]
    axis = Vector((0.06, 0.0, 1.0)).normalized()
    m.put_segment("haft", hand - axis * 0.420, hand + axis * 0.540, 0.016)
    m.put_segment("strap", hand + axis * 0.020, hand + axis * 0.090, 0.021)
    top = hand + axis * 0.470
    fwd = Vector((0.80, -0.30, 0.0)).normalized()          # the blade faces forward and a little out
    _slab(m.objects["axehead"], top - axis * 0.100 + fwd * 0.085, top + axis * 0.080 + fwd * 0.085, fwd.cross(axis), 0.160, 0.022)
    _slab(m.objects["axeedge"], top - axis * 0.110 + fwd * 0.165, top + axis * 0.090 + fwd * 0.165, fwd.cross(axis), 0.020, 0.024)
    m.put_segment("topspike", hand + axis * 0.530, hand + axis * 0.640, 0.020)
    m.put_segment("hook", top - fwd * 0.020, top - fwd * 0.110 + axis * 0.030, 0.016)


def assign_depth_parts(m, depth_of):
    return None
