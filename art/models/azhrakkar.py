"""Azhrakkar, the Cerulean Ruin: the Floor 10 floor boss (2x2 tiles), built on art/models/humanoid.py.

DESIGN.md 9.3: "a giant blue fiend carrying an enormous sword. Original design: no copied details beyond
'giant blue fiend, huge sword, boss room at the end of a labyrinth'". Jay, 2026-11-16: make him big, a floor boss,
in the spirit of the famous blue anime boss, measured against Tibia's Demon.

OUR design (inspired by the idea, not a copy of that character: no goat face, no serpent tail, no curled ram horns):
  Silhouette: a hunched, ape-shouldered titan: shoulders three heads wide, short thick legs, arms hanging past the knees,
              two great upswept horns, a great cleaver-sword as long as he is tall carried across his body in both hands.
  Colours:    deep cerulean hide with paler muscle, black-iron armour, a bone-white mane, cyan fire.
  Signature:  the horn tips BURN with cyan fire (it flickers as he walks), a glowing cyan rune channel down the
              sword (carried across his body in both hands: on a 64x64 canvas the body must be the mass,
              so the sword lies along his widest side instead of sticking out), burning cyan eyes under a heavy bone brow.
  Details:    tusked lower jaw, chest and belly muscles drawn with lines, spiked iron pauldrons, bracers, a belt
              with a skull buckle and iron tassets, knee plates, cloven hooves, clawed hands, a mane down the spine.
  Attitude:   slow and certain: head low between the shoulders, a heavy rolling walk, the sword hefted.
"""
from __future__ import annotations

import math

from mathutils import Euler, Vector

import humanoid as H

NAME = "azhrakkar"
WALK_FRAMES = 8
PALETTE = "azhrakkar"
REFERENCE = "look_35.png"     # Tibia's Demon: the size and detail bar for a 2x2 boss (comparison only, never shipped)
HEIGHT_SHEAR = 0.30           # the tilted monster camera (like the boar), NOT the sheared view people use:
LEAN = 0.0                    # a hulking monster must show its whole front when it faces the player
AUTO_PLACE = (1, 1)           # a boss fills the whole 64x64 canvas; each direction sits against the bottom-right
SIGNATURE = ["flame", "horn", "blade"]
HEAD_PARTS = ["skin", "hair", "strand", "eye", "brow", "nose", "jaw", "horn", "tusk", "flame"]
LEG_PARTS = ["leg_a", "leg_b", "boot_a", "boot_b", "knee"]
# a hunched titan: the head sits low between huge shoulders, and the short legs are mostly hidden by his bulk
CHECK = {"size": (0.88, 1.05), "head": 0.08, "legs_side": 0.02, "legs_updown": 0.015, "eye": 1}

PARTS = H.PARTS + ["muscle", "line", "jaw", "tusk", "horn", "flame", "iron", "spike", "knee", "claw",
                   "blade", "edge", "rune", "hilt", "tail"]
PIXEL_RULES = H.pixel_rules(
    weight={"eye": 9.0, "flame": 3.5, "rune": 5.0, "tusk": 4.0, "horn": 2.2, "spike": 3.0, "claw": 3.0, "line": 2.4,
            "edge": 2.4, "iron": 1.3, "knee": 1.8, "jaw": 1.4, "hilt": 2.4, "muscle": 1.1},
    thin={"flame": 3, "rune": 2, "tusk": 2, "spike": 2, "claw": 2, "line": 2, "edge": 2, "horn": 3},
    soft=[["torso", "muscle", "line", "arm_a", "arm_b"], ["skin", "jaw", "tusk"], ["horn", "flame"],
          ["iron", "spike"], ["blade", "edge", "rune"], ["leg_a", "knee"], ["leg_b", "knee"], ["hand", "claw"]],
    texture={"torso": [0.55, 0.40], "muscle": [0.45, 0.30], "arm_a": [0.5, 0.35], "arm_b": [0.5, 0.35],
             "leg_a": [0.5, 0.35], "leg_b": [0.5, 0.35], "skin": [0.4, 0.2], "iron": [0.5, 0.3], "blade": [0.35, 0.25],
             "horn": [0.6, 0.0], "hair": [0.6, 0.2]},
    selout=["muscle", "iron", "horn"],
    no_outline=["flame"],
)

SPEC = H.spec(
    body_scale=(1.22, 1.22, 1.30), beast=True,
    hip_z=0.34, hip_y=0.150, thigh=0.17, shin=0.17, leg_r=0.105,          # short thick legs
    torso_z=0.60, torso_r=(0.215, 0.300, 0.235),                           # the mass of the sprite is the torso
    shoulder_y=0.365, shoulder_z=0.770, upper_arm=0.25, forearm=0.26, arm_r=0.100,
    head_z=0.800, head_r=(0.185, 0.180, 0.170),                            # a big beast head sunk between the shoulders
    eye=(0.066, 0.034), eye_r=(0.024, 0.036, 0.024),
    cap=(-0.100, 0.030), cap_r=(0.110, 0.130, 0.130), strands=(-1.2, 1.2),
    boot_h=0.09, boot_r=0.105, foot_r=(0.125, 0.090, 0.062),
    stride=0.10, lift=0.045, bob=0.020, arm_swing=0.07, belt_z=0.400,
)
HORNS = [(1, 0.020, 0.80, 0.30), (-1, 0.020, 0.80, 0.30)]   # side, x, splay, length
HORN_N = 6
TEETH = 6
MANE = 5


def build(model_cls, facing):
    m = H.build(model_cls, facing, SPEC, PARTS)
    # a beast's head: heavy bone brow, a blunt muzzle, an underslung jaw with tusks
    m.ellipsoid("browridge", "brow", radii=(0.060, 0.160, 0.026), segments=12, rings=6)
    m.ellipsoid("muzzle", "skin", radii=(0.120, 0.110, 0.085), segments=14, rings=8)
    m.ellipsoid("jaw", "jaw", radii=(0.115, 0.125, 0.050), segments=14, rings=8)
    for k in ("l", "r"):
        m.cone(f"tusk_{k}", "tusk", segments=6)
    for i in range(len(HORNS)):
        m.tube(f"horn{i}", "horn", points=HORN_N)
        m.cone(f"flame{i}", "flame", segments=6)
        m.cone(f"flicker{i}", "flame", segments=5)
    for i in range(MANE):
        m.ellipsoid(f"mane{i}", "hair", radii=(0.070, 0.085, 0.060), segments=10, rings=6)
    # muscle: chest, belly blocks, shoulders, upper arms, thighs; drawn lines between them
    for k in ("l", "r"):
        m.ellipsoid(f"pec_{k}", "muscle", radii=(0.080, 0.140, 0.100), segments=14, rings=8)
        m.ellipsoid(f"delt_{k}", "muscle", radii=(0.130, 0.130, 0.120), segments=14, rings=8)
        m.ellipsoid(f"bicep_{k}", "muscle", radii=(0.085, 0.085, 0.110), segments=12, rings=8)
        m.ellipsoid(f"quad_{k}", "muscle", radii=(0.095, 0.090, 0.090), segments=12, rings=8)
        for j in range(3):
            m.ellipsoid(f"ab{j}_{k}", "muscle", radii=(0.034, 0.050, 0.036), segments=10, rings=6)
        m.ellipsoid(f"pauldron_{k}", "iron", radii=(0.120, 0.140, 0.060), segments=14, rings=8)
        m.cone(f"spike_{k}", "spike", segments=6)
        m.ellipsoid(f"knee_{k}", "knee", radii=(0.070, 0.075, 0.070), segments=10, rings=6)
        for j in range(3):
            m.cone(f"claw{j}_{k}", "claw", segments=5)
        m.box(f"tasset_{k}", "iron", size=(0.040, 0.130, 0.190))
    m.capsule("sternum", "line", segments=6)
    m.capsule("midline", "line", segments=6)
    m.box("tasset_f", "iron", size=(0.040, 0.150, 0.230))
    m.box("tasset_b", "iron", size=(0.040, 0.220, 0.250))
    m.tube("tail", "tail", points=6)
    m.cone("tailflame", "flame", segments=6)
    # the great cleaver: a broad slab, a bright edge, a glowing rune channel, saw teeth on the back
    m.box("blade", "blade", size=(1, 1, 1))
    m.box("edge", "edge", size=(1, 1, 1))
    m.capsule("rune", "rune", segments=6)
    for i in range(TEETH):
        m.cone(f"tooth{i}", "blade", segments=4)
    m.capsule("grip", "hilt", segments=8)
    m.capsule("guard", "hilt", segments=8)
    m.ellipsoid("pommel", "hilt", radii=(0.040, 0.040, 0.040), segments=8, rings=6)
    return m


def _sword_hand(sh, a, walking):
    heft = 0.015 * math.sin(2 * a) if walking else 0.0     # right fist on the grip, low at his right side
    return Vector((0.250, -0.330, 0.400 + heft)) + Vector((0, 0, sh.z - SPEC["shoulder_z"]))


def _claw_hand(sh, a, walking):
    heft = 0.015 * math.sin(2 * a) if walking else 0.0     # left hand under the flat of the blade
    return Vector((0.270, 0.200, 0.380 + heft)) + Vector((0, 0, sh.z - SPEC["shoulder_z"]))


def _slab(obj, start, end, width_dir, width, thick):
    """Stretch a unit box from start to end: its long side along the line, 'width' across, 'thick' through."""
    d = end - start
    obj.location = (start + end) / 2
    obj.rotation_mode = "QUATERNION"
    z = d.normalized()
    x = width_dir - z * width_dir.dot(z)
    x.normalize()
    y = z.cross(x)
    from mathutils import Matrix
    obj.rotation_quaternion = Matrix((x, y, z)).transposed().to_quaternion()
    obj.scale = (width, thick, d.length)


def pose(m, t):
    p = H.pose(m, t, hands={"l": _claw_hand, "r": _sword_hand})
    up, head, torso, a, walking = p["up"], p["head"], p["torso"], p["a"], p["walking"]
    roll = 0.05 * math.sin(a) if walking else 0.0            # a heavy rolling walk
    # head: pushed forward and down between the shoulders
    fwd = Vector((0.200, 0, 0.000))
    for name in ("head", "cap", "nose", "eye_l", "eye_r", "brow_l", "brow_r"):
        m.objects[name].location = m.objects[name].location + fwd
    for i in range(len(SPEC["strands"])):
        sp = m.objects[f"strand{i}"].data.splines[0]
        for pt in sp.points:
            pt.co = (pt.co[0] + fwd.x, pt.co[1], pt.co[2] + fwd.z, 1.0)
    head = head + fwd
    m.objects["browridge"].location = head + Vector((0.125, 0, 0.098))
    m.objects["muzzle"].location = head + Vector((0.130, 0, -0.060))
    gape = 0.012 * (1 + math.sin(2 * a)) if walking else 0.010
    m.objects["jaw"].location = head + Vector((0.115, 0, -0.140 - gape))
    for sign, k in ((1, "l"), (-1, "r")):
        root = head + Vector((0.170, 0.090 * sign, -0.140 - gape))
        m.put_segment(f"tusk_{k}", root, root + Vector((0.040, 0.020 * sign, 0.150)), 0.030)
    # four horns sweeping up and back; cyan fire burning at each tip
    for i, (sign, hx, splay, length) in enumerate(HORNS):
        root = head + Vector((hx, 0.120 * sign, 0.110))
        pts, radii = [], []
        for j in range(HORN_N):
            u = j / (HORN_N - 1)
            out = math.sin(splay) * sign
            pts.append(root + Vector((-0.060 * u * u + 0.050 * math.sin(math.pi * u) * (1 if hx > 0 else 0.3),
                                      out * length * u, math.cos(splay) * length * u * (0.55 + 0.45 * u) + 0.02 * u)))
            radii.append(0.056 * (1 - 0.72 * u) + 0.006)
        m.set_tube(f"horn{i}", [tuple(q) for q in pts], radii)
        tip = pts[-1]
        fl = 0.030 * math.sin(4 * a + i * 1.7) if walking else 0.010 * (i % 2)
        m.put_segment(f"flame{i}", tip - Vector((0, 0, 0.020)), tip + Vector((-0.020 + fl, fl, 0.090 + abs(fl))), 0.042)
        m.put_segment(f"flicker{i}", tip + Vector((-0.010, 0.015 * sign, 0.020)), tip + Vector((-0.030 - fl, 0.020 * sign, 0.080 - fl)), 0.020)
    # white mane from the crown down the spine
    for i in range(MANE):
        u = i / (MANE - 1)
        q = (head + Vector((-0.170, 0, 0.060))).lerp(torso + Vector((-0.215, 0, 0.060)), u)
        ob = m.objects[f"mane{i}"]
        ob.location = q + Vector((0, 0.020 * math.sin(a + i) if walking else 0.0, 0))
        ob.scale = (0.070 - 0.012 * u, 0.090 - 0.030 * u, 0.062)
    # muscle and its lines
    tr = SPEC["torso_r"]
    for sign, k in ((1, "l"), (-1, "r")):
        m.objects[f"pec_{k}"].location = torso + Vector((tr[0] * 0.80, 0.130 * sign, 0.085))
        for j in range(3):
            m.objects[f"ab{j}_{k}"].location = torso + Vector((tr[0] * 0.94 - 0.012 * j, 0.048 * sign, -0.030 - 0.062 * j))
        sh, el = p[f"shoulder_{k}"], p[f"elbow_{k}"]
        m.objects[f"delt_{k}"].location = sh + Vector((0.0, 0.015 * sign, -0.010))
        m.objects[f"bicep_{k}"].location = sh.lerp(el, 0.55) + Vector((0.030, 0.010 * sign, 0))
        m.objects[f"quad_{k}"].location = p[f"hip_{k}"].lerp(p[f"knee_{k}"], 0.5) + Vector((0.035, 0.012 * sign, 0))
        m.objects[f"knee_{k}"].location = p[f"knee_{k}"] + Vector((0.045, 0, 0.0))
        # black-iron pauldrons with three spikes
        pa = m.objects[f"pauldron_{k}"]
        pa.location = sh + Vector((-0.010, 0.050 * sign, 0.070))
        pa.rotation_mode = "XYZ"
        pa.rotation_euler = Euler((0.35 * sign + roll, 0, 0))
        m.put_segment(f"spike_{k}", pa.location + Vector((0, 0.060 * sign, 0.030)), pa.location + Vector((-0.020, 0.150 * sign, 0.120)), 0.040)
        # clawed hands
        hand, d = p[f"hand_{k}"], p[f"arm_dir_{k}"]
        for j in range(3):                                  # claws curling over the sword
            off = Vector(((j - 1) * 0.034, 0, 0))
            m.put_segment(f"claw{j}_{k}", hand + off + Vector((0, 0, 0.030)), hand + off + Vector((0.050, 0, 0.075)), 0.018)
        ta = m.objects[f"tasset_{k}"]
        ta.rotation_mode = "XYZ"
        ta.rotation_euler = Euler((0.25 * sign, 0, 0))
        ta.location = Vector((0.0, 0.260 * sign, SPEC["belt_z"] - 0.060)) + up
    m.put_segment("sternum", torso + Vector((tr[0] * 0.99, 0, 0.150)), torso + Vector((tr[0] * 1.00, 0, 0.000)), 0.010)
    m.put_segment("midline", torso + Vector((tr[0] * 1.00, 0, -0.010)), torso + Vector((tr[0] * 0.90, 0, -0.190)), 0.009)
    for name, x, lean, z in (("tasset_f", 0.215, 0.18, -0.080), ("tasset_b", -0.215, -0.14, -0.090)):
        o = m.objects[name]
        o.rotation_mode = "XYZ"
        o.rotation_euler = Euler((0, lean + (0.10 * math.sin(a) if walking else 0.0) * (1 if x > 0 else -1), 0))
        o.location = Vector((x, 0, SPEC["belt_z"] + z)) + up
    # a thick tail ending in a tuft of the same cyan fire
    base = Vector((-0.200, 0, SPEC["hip_z"] + 0.060)) + up
    pts = [base + Vector((-0.035 * i, 0.050 * i + (0.030 * math.sin(a + i * 0.9) * i / 5 if walking else 0.0), -0.045 * i + 0.010 * i * i)) for i in range(6)]
    m.set_tube("tail", [tuple(q) for q in pts], [0.055 - 0.008 * i for i in range(6)])
    m.put_segment("tailflame", pts[-1], pts[-1] + Vector((-0.020, 0.040, 0.090)), 0.040)
    # the cleaver, gripped in the right hand, trailing forward and out with its point near the ground
    hand = p["hand_r"]
    axis = Vector((0.06, 1.0, 0.10)).normalized()          # carried ACROSS his body in both hands, point to his left
    flat = Vector((0.7, 0.0, 0.7))                           # the broad side faces up and forward, so it reads from above
    m.put_segment("grip", hand - axis * 0.130, hand + axis * 0.090, 0.030)
    m.objects["pommel"].location = hand - axis * 0.150
    side = axis.cross(Vector((0, 0, 1))).normalized()
    m.put_segment("guard", hand + axis * 0.095 - side * 0.110, hand + axis * 0.095 + side * 0.110, 0.028)
    start, end = hand + axis * 0.110, hand + axis * 0.780
    _slab(m.objects["blade"], start, end, flat, 0.170, 0.030)
    wdir = (flat - axis * flat.dot(axis)).normalized()
    _slab(m.objects["edge"], start - wdir * 0.085, end - wdir * 0.060, flat, 0.030, 0.034)
    m.put_segment("rune", start + axis * 0.050 + wdir * 0.010, end - axis * 0.130 + wdir * 0.010, 0.024)
    for i in range(TEETH):
        q = start.lerp(end, 0.12 + 0.14 * i) + wdir * 0.080
        m.put_segment(f"tooth{i}", q, q + wdir * 0.075 + axis * 0.040, 0.040, 0.016)


def assign_depth_parts(m, depth_of):
    return None
