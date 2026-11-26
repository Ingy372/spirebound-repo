"""Bandit Captain (Floor 1 boss of the Bandit Road), built on art/models/humanoid.py (second draft, 2026-11-25).

ART_REQUESTS.md: "a bandit leader with a red sash, a feathered hat and a curved sabre".
The first draft (2026-11-15) had its own copied body; this one follows art/OUTFIT_RULES.md.

Identity (art/OUTFIT_RULES.md step 1):
  Silhouette: a three-cornered hat (brim turned up on three sides: Vesper owns the round wide hat, O14) with a red
              plume laid back along it (O15), a long dark coat with flared skirts, a curved sabre held out and up
              in the right hand, the left fist on his hip.
  Colours:    near-black leather coat, a broad red sash at the waist and across the chest, brass buttons; black
              beard; a bright steel sabre with a brass guard.
  Details:    the hat's turned-up brim with a brass edge, the plume, sash ends hanging at the hip, brass buttons,
              coat hem, cuffs, the sabre's curved blade and knuckle guard, a gold earring.
Look-alike: Tibia's Pirate Buccaneer / Pirate Corsair (hat, coat, sabre): ours is a land outlaw in black and red
with a red plume and no eyepatch.
Addons: none (a monster, rule A1).
"""
from __future__ import annotations

import math

from mathutils import Euler, Vector

import humanoid as H

NAME = "captain"
WALK_FRAMES = 8
PALETTE = "captain"
REFERENCE = "outfit_128.png"
PROJECTION = "oblique"
CANVAS_OFFSET = H.CANVAS_OFFSET
SIGNATURE = ["hat", "sash"]
HEAD_PARTS = ["skin", "hair", "strand", "eye", "brow", "nose", "beard", "hat", "brass"]
LEG_PARTS = ["leg_a", "leg_b", "boot_a", "boot_b"]
CHECK = {"size": (0.85, 1.50), "head": 0.08, "legs_side": 0.05, "eye": 1}

PARTS = H.PARTS + ["coat", "trim", "sash", "button", "beard", "hat", "brass", "plume", "blade", "guard", "earring"]
PIXEL_RULES = H.pixel_rules(
    weight={"trim": 2.4, "sash": 1.8, "button": 4.0, "beard": 1.4, "hat": 1.3, "brass": 2.6, "plume": 2.2,
            "blade": 3.0, "guard": 3.0, "earring": 5.0},
    thin={"trim": 2, "button": 2, "brass": 2, "plume": 3, "blade": 2, "guard": 2, "earring": 2},
    soft=[["torso", "coat", "trim", "button", "sash"], ["skin", "beard", "earring"], ["hat", "brass"],
          ["blade", "guard"]],
    texture={"coat": [0.35, 0.15], "sash": [0.35, 0.12], "beard": [0.35, 0.15], "hat": [0.25, 0.0]},
    selout=["coat", "hat", "sash"],
)

SPEC = H.spec(torso_r=(0.108, 0.160, 0.188), arm_r=0.052, leg_r=0.052, stride=0.12, lift=0.055, bob=0.016,
              strands=(-1.2, -0.2, 0.8))


def build(model_cls, facing):
    m = H.build(model_cls, facing, SPEC, PARTS)
    m.ellipsoid("beard", "beard", radii=(0.064, 0.086, 0.056), segments=12, rings=8)
    m.ellipsoid("earring", "earring", radii=(0.010, 0.010, 0.012), segments=6, rings=4)
    for k in ("f_l", "f_r", "b"):
        m.box(f"skirt_{k}", "coat", size=(0.026, 0.120 if k != "b" else 0.290, 0.250))
        m.box(f"hem_{k}", "trim", size=(0.030, 0.124 if k != "b" else 0.294, 0.026))
    m.frustum("sash", "sash", top_ratio=1.0, segments=18)
    m.capsule("baldric", "sash")
    for i in range(2):
        m.capsule(f"sashend{i}", "sash")
    for i in range(3):
        m.ellipsoid(f"button{i}", "button", radii=(0.013, 0.013, 0.013), segments=6, rings=4)
    # three-cornered hat: a flat crown and three upturned brim flaps
    m.frustum("crown", "hat", top_ratio=0.86, segments=16)
    for i in range(3):
        m.box(f"flap{i}", "hat", size=(0.030, 0.150, 0.060))
        m.box(f"edge{i}", "brass", size=(0.034, 0.154, 0.010))
    m.tube("plume", "plume", points=7)
    m.tube("blade", "blade", points=6)
    m.capsule("grip", "guard")
    m.tube("knuckle", "guard", points=5)
    return m


def _sabre_hand(sh, a, walking):
    swing = 0.05 * math.sin(a) if walking else 0.0
    return sh + Vector((0.160 + swing, -0.080, -0.160))


def _hip_hand(sh, a, walking):
    return sh + Vector((0.020, 0.110, -0.300))            # fist on the hip, elbow out: a swaggering outline


def pose(m, t):
    p = H.pose(m, t, hands={"r": _sabre_hand, "l": _hip_hand})
    up, head, a, walking = p["up"], p["head"], p["a"], p["walking"]
    s = m.spec
    m.objects["beard"].location = head + Vector((0.074, 0, -0.072))
    m.objects["earring"].location = head + Vector((0.010, 0.120, -0.040))
    flap = 0.24 * abs(math.sin(a)) if walking else 0.0
    for k, (x, y, rot) in (("f_l", (0.098, 0.070, flap)), ("f_r", (0.098, -0.070, flap)), ("b", (-0.102, 0.0, -flap))):
        for name, z in ((f"skirt_{k}", 0.420), (f"hem_{k}", 0.300)):
            o = m.objects[name]
            o.rotation_mode = "XYZ"
            o.rotation_euler = Euler((0, rot, 0))
            o.location = Vector((x, y, z)) + up
    H.frustum(m, "sash", Vector((0, 0, s["belt_z"] - 0.010)) + up, (s["torso_r"][0] * 1.10, s["torso_r"][1] * 1.04), 0.070)
    m.put_segment("baldric", Vector((s["torso_r"][0] * 0.80, 0.120, 0.870)) + up,
                  Vector((s["torso_r"][0] * 1.05, -0.110, 0.590)) + up, 0.022)
    sway = 0.03 * math.sin(a) if walking else 0.0
    for i in range(2):
        top = Vector((0.020, -s["torso_r"][1] * 1.02, s["belt_z"] - 0.020 - 0.010 * i)) + up
        m.put_segment(f"sashend{i}", top, top + Vector((0.030 - 0.040 * i + sway, -0.020, -0.130 + 0.020 * i)), 0.022, 0.016)
    for i in range(3):
        m.objects[f"button{i}"].location = Vector((s["torso_r"][0] * 1.03, 0.040, 0.800 - 0.065 * i)) + up
    hat = head + Vector((-0.020, 0, 0.130))
    H.frustum(m, "crown", hat, (0.090, 0.088), 0.090, rot=(0, -0.30, 0))
    for i in range(3):
        ang = math.pi / 3 + 2 * math.pi * i / 3                 # corners at front-left, front-right, back
        out = Vector((math.cos(ang + math.pi / 3), math.sin(ang + math.pi / 3), 0))
        for name, dz in ((f"flap{i}", 0.020), (f"edge{i}", 0.052)):
            o = m.objects[name]
            o.rotation_mode = "XYZ"
            o.rotation_euler = Euler((0, -0.50, ang + math.pi / 3))  # each flap leans out and up
            o.location = hat + out * 0.090 + Vector((0, 0, dz))
    pts = [hat + Vector((-0.010 - 0.034 * k, 0.050 + 0.012 * k, 0.060 + 0.012 * k - 0.0030 * k * k + sway * k / 6)) for k in range(7)]
    m.set_tube("plume", [tuple(q) for q in pts], [0.012, 0.022, 0.026, 0.026, 0.022, 0.016, 0.008])
    # curved sabre held out and up from the right hand
    hand = p["hand_r"]
    fwd = Vector((0.70, -0.40, 0.60)).normalized()
    side = fwd.cross(Vector((0, 0, 1))).normalized()
    m.put_segment("grip", hand - fwd * 0.040, hand + fwd * 0.030, 0.014)
    knuckle = [hand + fwd * 0.030 - side * 0.010, hand + fwd * 0.010 - side * 0.040, hand - fwd * 0.020 - side * 0.045,
               hand - fwd * 0.045 - side * 0.030, hand - fwd * 0.045]
    m.set_tube("knuckle", [tuple(q) for q in knuckle], [0.008] * 5)
    curve = [hand + fwd * (0.040 + 0.055 * k) + side * (0.006 * k * k) for k in range(6)]
    m.set_tube("blade", [tuple(q) for q in curve], [0.022, 0.022, 0.020, 0.017, 0.012, 0.005])


def assign_depth_parts(m, depth_of):
    return None
