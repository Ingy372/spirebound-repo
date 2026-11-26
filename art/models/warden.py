"""Bounty Warden (Hearthgate town NPC), built on art/models/humanoid.py (second draft, 2026-11-25).

ART_REQUESTS.md: "a stern bounty warden in a dark red coat with a wanted-poster scroll".
The first draft (2026-11-15) was a recoloured copy of Vesper's old body; this one follows art/OUTFIT_RULES.md.

Identity (art/OUTFIT_RULES.md step 1):
  Silhouette: a long coat flaring to the knees with split skirts, bare grey head, a crossbow slung across the
              back (its bow sticks out past the shoulders), a rolled wanted poster held out in the right hand, iron
              manacles hanging at the left hip. No hat: Vesper owns the coat-and-hat outline (rule O5).
  Colours:    oxblood coat, brass trim and buttons, black boots, slate trousers; iron-grey hair and beard; dark wood.
  Details:    brass hem on every coat skirt, a row of brass buttons, a standing collar with brass piping, turned-back
              cuffs, a belt with a brass buckle, a strap across the chest, a red wax seal on the poster, manacles on
              the belt, a short grey beard (stern, older than the other townsfolk).
Detail (art/DETAIL_RULES.md step 1): long coat, skirts, buttons, collar, cuffs, crossbow (stock, bow, string),
              strap, beard, poster, manacles, boots with cuffs.
"""
from __future__ import annotations

import math

from mathutils import Euler, Vector

import humanoid as H

NAME = "warden"
WALK_FRAMES = 8
PALETTE = "warden"
REFERENCE = "outfit_128.png"
PROJECTION = "oblique"
CANVAS_OFFSET = H.CANVAS_OFFSET
SIGNATURE = ["skirt", "bow"]
HEAD_PARTS = ["skin", "hair", "strand", "eye", "brow", "nose", "beard"]
LEG_PARTS = ["leg_a", "leg_b", "boot_a", "boot_b"]
CHECK = {"size": (0.85, 1.45), "head": 0.08, "legs_side": 0.05, "eye": 1}   # the crossbow adds to the measured size

PARTS = H.PARTS + ["skirt", "trim", "button", "collar", "stock", "bow", "string", "strap", "beard", "poster", "seal", "iron"]
PIXEL_RULES = H.pixel_rules(
    weight={"trim": 2.4, "button": 4.0, "collar": 1.6, "bow": 2.6, "string": 3.0, "strap": 2.0, "stock": 1.6, "beard": 1.4, "poster": 2.6,
            "seal": 4.0, "iron": 3.0},
    thin={"trim": 2, "button": 2, "bow": 2, "string": 2, "strap": 3, "poster": 3, "seal": 2, "iron": 2},
    soft=[["skirt", "trim"], ["torso", "button", "collar"], ["stock", "bow", "string"], ["torso", "strap"], ["poster", "seal"],
          ["skin", "beard"]],
    texture={"skirt": [0.38, 0.16], "stock": [0.3, 0.1], "beard": [0.35, 0.15]},
    selout=["skirt", "collar", "stock"],
)

SPEC = H.spec(torso_r=(0.104, 0.152, 0.186), arm_r=0.046, leg_r=0.050, stride=0.11, lift=0.050, bob=0.014,
              strands=(-1.5, -0.8, -0.1, 0.6, 1.3), cap_r=(0.112, 0.116, 0.096))   # more strands, a closer crop


def build(model_cls, facing):
    m = H.build(model_cls, facing, SPEC, PARTS)
    m.ellipsoid("nape", "hair", radii=(0.048, 0.092, 0.056), segments=12, rings=6)
    m.ellipsoid("sideburn_l", "hair", radii=(0.028, 0.020, 0.050), segments=8, rings=6)
    m.ellipsoid("sideburn_r", "hair", radii=(0.028, 0.020, 0.050), segments=8, rings=6)
    m.ellipsoid("beard", "beard", radii=(0.060, 0.082, 0.050), segments=12, rings=8)
    # coat skirts: four panels from the waist to the knee, each with a brass hem (split coat, like a frock coat)
    for k in ("f_l", "f_r", "b", "s_l", "s_r"):
        wide = 0.115 if k.startswith("f") else (0.290 if k == "b" else 0.026)
        deep = 0.026 if not k.startswith("s") else 0.170
        m.box(f"skirt_{k}", "skirt", size=(deep, wide, 0.260))
        m.box(f"hem_{k}", "trim", size=(deep * 1.10 + 0.004, wide * 1.04 + 0.004, 0.030))
    for i in range(4):
        m.ellipsoid(f"button{i}", "button", radii=(0.014, 0.014, 0.014), segments=8, rings=6)
    m.frustum("collar", "collar", top_ratio=1.08, segments=16)
    m.frustum("collar_pipe", "trim", top_ratio=1.0, segments=16)
    # crossbow slung across the back, the bow end up behind the left shoulder (O8: tall things behind the head)
    m.box("stock", "stock", size=(0.040, 0.050, 0.330))
    m.capsule("bow_l", "bow")
    m.capsule("bow_r", "bow")
    m.capsule("bowstring", "string")
    m.capsule("strap", "strap")
    m.ellipsoid("short_hair", "hair", radii=(0.040, 0.070, 0.026), segments=10, rings=6)
    m.capsule("poster", "poster")
    m.ellipsoid("seal", "seal", radii=(0.016, 0.020, 0.020), segments=8, rings=6)
    for i in range(2):
        m.frustum(f"manacle{i}", "iron", top_ratio=1.0, segments=12)
    m.capsule("chain", "iron")
    return m


def _poster_hand(sh, a, walking):
    return sh + Vector((0.135, 0.030, -0.235))          # held out at the chest, reading off the wanted list


def pose(m, t):
    p = H.pose(m, t, hands={"r": _poster_hand})
    up, head, cap, a, walking = p["up"], p["head"], p["cap"], p["a"], p["walking"]
    s = m.spec
    m.objects["nape"].location = head + Vector((-0.084, 0, -0.028))
    m.objects["sideburn_l"].location = head + Vector((0.020, 0.100, -0.010))
    m.objects["sideburn_r"].location = head + Vector((0.020, -0.100, -0.010))
    m.objects["beard"].location = head + Vector((0.070, 0, -0.072))
    # skirts swing out with whichever leg is forward, so no knee pokes through
    flap = 0.24 * abs(math.sin(a)) if walking else 0.0
    panels = {"f_l": (0.098, 0.062, flap), "f_r": (0.098, -0.062, flap), "b": (-0.100, 0.0, -flap),
              "s_l": (0.0, 0.150, 0.0), "s_r": (0.0, -0.150, 0.0)}
    for k, (x, y, rot_y) in panels.items():
        roll = 0.10 if k == "s_l" else (-0.10 if k == "s_r" else 0.0)
        for name, z in ((f"skirt_{k}", 0.425), (f"hem_{k}", 0.305)):
            o = m.objects[name]
            o.rotation_mode = "XYZ"
            o.rotation_euler = Euler((roll, rot_y, 0.0))
            o.location = Vector((x * (1.02 if name.startswith("hem") else 1.0), y, z)) + up
    for i in range(4):
        m.objects[f"button{i}"].location = Vector((s["torso_r"][0] * 1.02, 0.0, 0.795 - i * 0.070)) + up
    H.frustum(m, "collar", Vector((-0.012, 0, 0.840)) + up, (0.090, 0.112), 0.062, rot=(0.0, -0.18, 0.0))
    H.frustum(m, "collar_pipe", Vector((-0.020, 0, 0.900)) + up, (0.094, 0.118), 0.010, rot=(0.0, -0.18, 0.0))
    m.objects["short_hair"].location = head + Vector((0.040, 0, 0.122))       # a short swept-back fringe
    # crossbow on the back: stock diagonal from the right hip up to behind the left shoulder
    back = Vector((-s["torso_r"][0] * 1.45, 0, 0.0)) + up
    low, high = back + Vector((0.0, -0.110, 0.520)), back + Vector((-0.030, 0.130, 0.800))
    stock = m.objects["stock"]
    d = (high - low).normalized()
    stock.rotation_mode = "QUATERNION"
    stock.rotation_quaternion = d.to_track_quat("Z", "X")
    stock.location = (low + high) / 2
    side = d.cross(Vector((1, 0, 0))).normalized()
    tip = high + d * 0.020
    for k, sgn in (("l", 1), ("r", -1)):
        end = tip + side * 0.175 * sgn - d * 0.070 + Vector((-0.095, 0, 0))   # swept back: seen from the side too
        m.put_segment(f"bow_{k}", tip, end, 0.022, 0.013)
    m.put_segment("bowstring", tip + side * 0.172 - d * 0.072 + Vector((-0.085, 0, 0)),
                  tip - side * 0.172 - d * 0.072 + Vector((-0.085, 0, 0)), 0.006)
    # strap across the chest from the right hip to the left shoulder
    m.put_segment("strap", Vector((s["torso_r"][0] * 0.95, -0.090, 0.600)) + up,
                  Vector((s["torso_r"][0] * 0.55, 0.120, 0.860)) + up, 0.012)
    # rolled poster across the right hand, the wax seal facing out
    hand = p["hand_r"]
    m.put_segment("poster", hand + Vector((0.010, -0.075, -0.010)), hand + Vector((0.020, 0.070, 0.020)), 0.024)
    m.objects["seal"].location = hand + Vector((0.040, 0.000, 0.006))
    # manacles hanging from the belt at the left hip, swinging a little
    swing = 0.03 * math.sin(a) if walking else 0.0
    belt = Vector((0.010, s["torso_r"][1] * 0.98, s["belt_z"])) + up
    for i, dx in enumerate((0.030, -0.030)):
        H.frustum(m, f"manacle{i}", belt + Vector((dx + swing, 0.020, -0.070 - 0.012 * i)), (0.026, 0.026), 0.014,
                  rot=(math.pi / 2, 0.0, 0.0))
    m.put_segment("chain", belt + Vector((0.030 + swing, 0.020, -0.060)), belt + Vector((-0.030 + swing, 0.020, -0.070)), 0.006)


def assign_depth_parts(m, depth_of):
    return None
