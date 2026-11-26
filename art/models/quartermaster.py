"""Quartermaster (Hearthgate supply post, town NPC), built on art/models/humanoid.py (second draft, 2026-11-25).

ART_REQUESTS.md: "a quartermaster in a leather apron with a crate of arrows and potions".
The first draft (2026-11-15) was the merchant's old body recoloured. The merchant already owns the apron outline
(rule O14), so this one keeps the crate and potions and drops the apron for a working vest and a bandolier.

Identity (art/OUTFIT_RULES.md step 1):
  Silhouette: stocky; a slatted crate strapped on his back with arrow shafts sticking up behind his shoulders, a
              bandolier of potion vials across the chest, a flat leather cap, grey sideburns and a big moustache.
              (A bald head read as a big pink egg; a crate at the hip read as a third leg and on the shoulder it hid his
              face: it went on his back, rule O8.)
  Colours:    olive tunic, dark brown leather vest and bandolier, tan trousers, red and blue vials; grey hair.
  Details:    crate slats and corner straps, pale arrow fletchings, red and blue vial stoppers, vest edge, belt with
              brass buckle, rolled sleeves (bare forearms), boot cuffs.
Addons: none (an NPC, rule A1).
"""
from __future__ import annotations

import math

from mathutils import Euler, Vector

import humanoid as H

NAME = "quartermaster"
WALK_FRAMES = 8
PALETTE = "quartermaster"
REFERENCE = "outfit_128.png"
PROJECTION = "oblique"
CANVAS_OFFSET = H.CANVAS_OFFSET
SIGNATURE = ["crate", "shaft"]                # the vials are on his front: hidden from behind, as they should be
HEAD_PARTS = ["skin", "hair", "strand", "eye", "brow", "nose", "stache", "hat"]
LEG_PARTS = ["leg_a", "leg_b", "boot_a", "boot_b"]
CHECK = {"size": (0.85, 1.45), "head": 0.08, "legs_side": 0.05, "eye": 1}

PARTS = H.PARTS + ["vest", "edge", "bandolier", "vial", "stopper", "stache", "crate", "slat", "shaft", "fletch",
                   "forearm", "hat"]
PIXEL_RULES = H.pixel_rules(
    weight={"edge": 2.4, "bandolier": 2.2, "vial": 4.0, "stopper": 5.0, "stache": 2.0, "slat": 2.6, "shaft": 3.0,
            "fletch": 4.0, "forearm": 2.0},
    thin={"edge": 2, "bandolier": 3, "vial": 2, "stopper": 2, "slat": 2, "shaft": 2, "fletch": 2},
    soft=[["torso", "vest", "edge"], ["bandolier", "vial", "stopper"], ["skin", "stache"], ["crate", "slat"],
          ["shaft", "fletch"]],
    texture={"vest": [0.35, 0.12], "crate": [0.45, 0.2], "hat": [0.3, 0.1]},
    selout=["vest", "crate", "hat"],
)

SPEC = H.spec(torso_r=(0.112, 0.166, 0.180), arm_r=0.054, leg_r=0.054, stride=0.10, lift=0.045, bob=0.016,
              strands=(-1.3, -0.4, 0.5, 1.3))
N_VIALS = 4


def build(model_cls, facing):
    m = H.build(model_cls, facing, SPEC, PARTS)
    m.ellipsoid("stache", "stache", radii=(0.024, 0.070, 0.020), segments=10, rings=6)
    m.ellipsoid("hat", "hat", radii=(0.094, 0.098, 0.030), segments=18, rings=8)     # a flat cap ON the crown, never over the brow
    for k in ("l", "r"):
        m.ellipsoid(f"burn_{k}", "hair", radii=(0.028, 0.020, 0.048), segments=8, rings=6)
    for side in ("f_l", "f_r", "b"):
        m.box(f"vest_{side}", "vest", size=(0.024, 0.110 if side != "b" else 0.250, 0.250))
        m.box(f"vedge_{side}", "edge", size=(0.028, 0.012 if side != "b" else 0.254, 0.254))
    m.capsule("bandolier", "bandolier")
    for i in range(N_VIALS):
        m.capsule(f"vial{i}", "vial")
        m.ellipsoid(f"stopper{i}", "stopper", radii=(0.012, 0.012, 0.010), segments=6, rings=4)
    for k in ("l", "r"):
        m.capsule(f"bare_{k}", "forearm")
    m.box("crate", "crate", size=(0.200, 0.110, 0.220))
    for i in range(3):
        m.box(f"slat{i}", "slat", size=(0.204, 0.114, 0.012))
    for i in range(4):
        m.capsule(f"shaft{i}", "shaft")
        m.ellipsoid(f"fletch{i}", "fletch", radii=(0.010, 0.016, 0.022), segments=6, rings=4)
    return m


def pose(m, t):
    p = H.pose(m, t)
    up, head, a, walking = p["up"], p["head"], p["a"], p["walking"]
    s = m.spec
    m.objects["stache"].location = head + Vector((0.110, 0, -0.040))
    m.objects["hat"].location = head + Vector((-0.046, 0, 0.128))
    for sign, k in ((1, "l"), (-1, "r")):
        m.objects[f"burn_{k}"].location = head + Vector((0.020, 0.104 * sign, -0.010))
    for side, (x, y, w) in (("f_l", (0.106, 0.075, 0)), ("f_r", (0.106, -0.075, 0)), ("b", (-0.108, 0.0, 0))):
        for name, dx in ((f"vest_{side}", 0.0), (f"vedge_{side}", 0.002 if side != "b" else -0.002)):
            o = m.objects[name]
            o.location = Vector((x + dx, y + (0.050 if side == "f_l" and name.startswith("vedge") else
                                             (-0.050 if side == "f_r" and name.startswith("vedge") else 0.0)), 0.700)) + up
    # bandolier from the left shoulder to the right hip, vials along it
    p0 = Vector((s["torso_r"][0] * 0.70, 0.130, 0.860)) + up
    p1 = Vector((s["torso_r"][0] * 1.00, -0.120, 0.570)) + up
    m.put_segment("bandolier", p0, p1, 0.014)
    for i in range(N_VIALS):
        c = p0 + (p1 - p0) * (0.22 + 0.19 * i) + Vector((0.020, 0, 0))
        m.put_segment(f"vial{i}", c - Vector((0, 0, 0.026)), c + Vector((0, 0, 0.018)), 0.014)
        m.objects[f"stopper{i}"].location = c + Vector((0, 0, 0.028))
    # rolled sleeves: bare forearms over the sleeve
    for k in ("l", "r"):
        e, h = p[f"elbow_{k}"], p[f"hand_{k}"]
        m.put_segment(f"bare_{k}", e + (h - e) * 0.25, h - (h - e) * 0.15, s["arm_r"] * 0.86)
    # crate under the right arm, arrows sticking up and back out of it
    c = Vector((-s["torso_r"][0] - 0.070, 0.0, 0.740)) + up      # on his back, a little proud of it (O17)
    tilt = Euler((0.0, -0.12, 1.5708))
    for name, dz in (("crate", 0.0), ("slat0", -0.075), ("slat1", 0.0), ("slat2", 0.075)):
        o = m.objects[name]
        o.rotation_mode = "XYZ"
        o.rotation_euler = tilt
        o.location = c + Vector((0, 0, dz))
    for i, (dx, dy) in enumerate(((0.040, 0.020), (0.010, -0.020), (-0.025, 0.025), (-0.045, -0.010))):
        base = c + Vector((dy * 0.8, dx * 1.6, 0.090))
        tip = base + Vector((-0.050, 0.020 * (i - 1.5), 0.170))
        m.put_segment(f"shaft{i}", base, tip, 0.007)
        m.objects[f"fletch{i}"].location = tip


def assign_depth_parts(m, depth_of):
    return None
