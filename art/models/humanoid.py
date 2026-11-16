"""Shared figure for PLAYER OUTFITS and other detailed people (the four class outfits are built on it).

An outfit file describes the costume (a SPEC of proportions, its hair pieces, garments, gear) and calls build() /
pose() from here. The rules that make a figure read as hand-made are built in (see art/OUTFIT_RULES.md):

  * natural proportions: the head is about a fifth of the figure, not a third (no bobble-heads);
  * the two arms, the two legs and the two boots are SEPARATE parts ("arm_a"/"arm_b"...), so a dark line is
    drawn wherever one passes in front of the other or of the body: limbs read apart, like Tibia's outfits;
  * hands are skin, with a cuff at the wrist; boots have a cuff and a sole;
  * the face has eyes placed on the head's surface, a nose highlight, and brows;
  * hair is a cap with drawn strand lines; the outfit adds its own fringe, locks, hood or braid on top;
  * a fixed place on the canvas (CANVAS_OFFSET), so every outfit and later add-on lines up.

Units: tiles before the body scale. The figure faces +X, +Y is its left, +Z is up. Oblique projection.
"""
from __future__ import annotations

import math

from mathutils import Euler, Vector

PARTS = ["none", "skin", "eye", "brow", "nose", "hair", "strand", "hand",
         "torso", "arm_a", "arm_b", "cuff", "leg_a", "leg_b", "boot_a", "boot_b", "sole", "belt", "buckle"]
BANDS = [0.38, 0.50, 0.60, 0.69, 0.78, 0.86, 0.93]
CANVAS_OFFSET = (8, 8)

DEFAULTS = {
    "body_scale": (1.22, 1.26, 1.00),
    "hip_z": 0.50, "hip_y": 0.074, "thigh": 0.25, "shin": 0.25, "leg_r": 0.050,
    "torso_z": 0.70, "torso_r": (0.100, 0.150, 0.185),
    "shoulder_y": 0.160, "shoulder_z": 0.825, "upper_arm": 0.19, "forearm": 0.18, "arm_r": 0.044,
    "head_z": 0.955, "head_r": (0.118, 0.112, 0.126),
    "eye": (0.050, 0.046), "eye_r": (0.010, 0.011, 0.016),          # (side, height) on the face
    "cap": (-0.046, 0.036), "cap_r": (0.118, 0.120, 0.104),          # hair cap (x, z) offset from the head
    "strands": (-1.2, -0.2, 0.9),                                   # directions of the drawn hair strands
    "boot_h": 0.13, "boot_r": 0.058, "foot_r": (0.074, 0.046, 0.044),
    "stride": 0.13, "lift": 0.060, "stance": 0.5, "bob": 0.016, "arm_swing": 0.12,
    "belt_z": 0.555,
    "beast": False,          # True for monsters built on this figure: allows a big beast head (never for outfits)
}


def spec(**overrides):
    unknown = set(overrides) - set(DEFAULTS)
    if unknown:
        raise KeyError(f"unknown humanoid setting(s): {sorted(unknown)}")
    s = {**DEFAULTS, **overrides}
    if s["head_r"][2] > 0.140 and not s["beast"]:
        raise ValueError("head_r is too big: outfit heads stay under 0.140 tall (no bobble-heads; art/OUTFIT_RULES.md)")
    return s


def pixel_rules(weight=None, thin=None, soft=None, texture=None, selout=None, no_outline=None, fur=None):
    """The standard treatment for an outfit; pass extras for its own parts (cape, shield, staff...)."""
    return {
        "weight": {"eye": 9.0, "brow": 3.0, "nose": 2.0, "hand": 2.6, "strand": 1.3, "cuff": 2.2, "buckle": 4.0,
                   "belt": 2.0, "sole": 1.6, "boot_a": 1.4, "boot_b": 1.4, **(weight or {})},
        "thin": {"eye": 3, "brow": 2, "nose": 3, "hand": 3, "strand": 2, "cuff": 3, "buckle": 2, "belt": 3,
                 "sole": 3, **(thin or {})},
        # limbs are NOT soft with the torso or with each other: that is what draws the lines between them
        "soft": [["skin", "eye", "brow", "nose"], ["hair", "strand"], ["hand", "skin"], ["torso", "belt", "buckle"],
                 ["boot_a", "sole"], ["boot_b", "sole"]] + (soft or []),
        "no_outline": no_outline or [],
        "fur": fur or [],
        "texture": {"torso": [0.40, 0.18], "arm_a": [0.35, 0.12], "arm_b": [0.35, 0.12], "leg_a": [0.35, 0.12],
                    "leg_b": [0.35, 0.12], "hair": [0.30, 0.10], "boot_a": [0.3, 0.0], "boot_b": [0.3, 0.0],
                    **(texture or {})},
        "bands": BANDS,
        "selout": ["torso", "skin", "hair"] + (selout or []),
    }


def on_ellipsoid(centre, radii, direction, out=1.02):
    d = Vector(direction).normalized()
    k = 1.0 / math.sqrt((d.x / radii[0]) ** 2 + (d.y / radii[1]) ** 2 + (d.z / radii[2]) ** 2)
    return centre + d * k * out


def frustum(m, name, base, radii, height, rot=(0.0, 0.0, 0.0)):
    """Place a frustum made with model.frustum(): base centre, (x, y) radii at the base, height, lean."""
    o = m.objects[name]
    o.location = base
    o.scale = (radii[0], radii[1], height)
    o.rotation_mode = "XYZ"
    o.rotation_euler = Euler(rot)


def two_bone(a, target, l1, l2, bend_hint):
    d = target - a
    dist = min(d.length, l1 + l2 - 1e-4)
    d.normalize()
    side = d.cross(bend_hint)
    if side.length < 1e-6:
        side = Vector((0, 1, 0))
    bend = side.cross(d).normalized()
    x = (l1 ** 2 + dist ** 2 - l2 ** 2) / (2 * dist)
    h = math.sqrt(max(l1 ** 2 - x ** 2, 0.0))
    return a + d * x + bend * h, a + d * dist


def build(model_cls, facing, s, parts):
    import bpy
    body = bpy.data.objects.new("BodyScale", None)
    body.parent = facing
    body.scale = s["body_scale"]
    bpy.context.scene.collection.objects.link(body)
    m = model_cls(body, parts)
    m.spec = s
    for k, ab in (("l", "a"), ("r", "b")):
        m.capsule(f"thigh_{k}", f"leg_{ab}")
        m.capsule(f"shin_{k}", f"leg_{ab}")
        m.capsule(f"bootleg_{k}", f"boot_{ab}")
        m.ellipsoid(f"foot_{k}", f"boot_{ab}", radii=s["foot_r"], segments=12, rings=8)
        m.ellipsoid(f"sole_{k}", "sole", radii=(s["foot_r"][0] * 1.04, s["foot_r"][1] * 1.04, 0.012), segments=12, rings=6)
        m.frustum(f"bootcuff_{k}", "cuff", top_ratio=1.0, segments=12)
        m.capsule(f"upper_{k}", f"arm_{ab}")
        m.capsule(f"fore_{k}", f"arm_{ab}")
        m.frustum(f"cuff_{k}", "cuff", top_ratio=1.0, segments=10)
        m.ellipsoid(f"hand_{k}", "hand", radii=(0.036, 0.030, 0.038), segments=10, rings=8)
    m.ellipsoid("torso", "torso", radii=s["torso_r"], segments=20, rings=12)
    m.ellipsoid("hips", "torso", radii=(s["torso_r"][0] * 0.95, s["torso_r"][1] * 0.92, 0.075), segments=16, rings=8)
    m.frustum("belt", "belt", top_ratio=1.0, segments=18)
    m.ellipsoid("buckle", "buckle", radii=(0.014, 0.026, 0.022), segments=8, rings=6)
    m.capsule("neck", "skin", segments=8)
    m.ellipsoid("head", "skin", radii=s["head_r"], segments=20, rings=12)
    m.ellipsoid("nose", "nose", radii=(0.016, 0.014, 0.018), segments=8, rings=6)
    for k in ("l", "r"):
        m.ellipsoid(f"eye_{k}", "eye", radii=s["eye_r"], segments=8, rings=6)
        m.capsule(f"brow_{k}", "brow", segments=6)
    m.ellipsoid("cap", "hair", radii=s["cap_r"], segments=18, rings=10)
    for i in range(len(s["strands"])):
        m.tube(f"strand{i}", "strand", points=5)
    return m


def _foot(s, t, phase):
    if t is None:
        return 0.0, 0.0
    u = (t + phase) % 1.0
    if u < s["stance"]:
        return s["stride"] * (1 - 2 * u / s["stance"]), 0.0
    k = (u - s["stance"]) / (1 - s["stance"])
    ease = 0.5 - 0.5 * math.cos(math.pi * k)
    return s["stride"] * (-1 + 2 * ease), s["lift"] * math.sin(math.pi * k)


def pose(m, t, hands=None):
    """t = None standing, else 0..1 through the walk. hands = {"l": fn, "r": fn}: fn(shoulder, a, walking) returns
    where that hand is (for a hand that holds something); a missing side swings normally.
    Returns the moving anchors (up, torso, head, shoulders, elbows, hands, hips, ankles, a, walking)."""
    s = m.spec
    hands = hands or {}
    a = 0.0 if t is None else 2 * math.pi * t
    walking = t is not None
    up = Vector((0, 0, s["bob"] * (0.5 + 0.5 * math.cos(2 * a)) if walking else 0.0))
    twist = 0.10 * math.sin(a) if walking else 0.0         # shoulders turn a little against the legs
    out = {"a": a, "walking": walking, "up": up}
    torso = Vector((0, 0, s["torso_z"])) + up
    m.objects["torso"].location = torso
    m.objects["torso"].rotation_mode = "XYZ"
    m.objects["torso"].rotation_euler = Euler((0, 0, twist))
    m.objects["hips"].location = Vector((0, 0, s["hip_z"] + 0.045)) + up
    frustum(m, "belt", Vector((0, 0, s["belt_z"])) + up, (s["torso_r"][0] * 1.06, s["torso_r"][1] * 1.00), 0.038)
    m.objects["buckle"].location = Vector((s["torso_r"][0] * 1.08, 0, s["belt_z"] + 0.019)) + up
    head = Vector((0.012, 0, s["head_z"])) + up
    m.put_segment("neck", torso + Vector((0, 0, s["torso_r"][2] * 0.80)), head, 0.050)
    m.objects["head"].location = head
    m.objects["nose"].location = on_ellipsoid(head, s["head_r"], (1.0, 0, -0.05), 0.98)
    for sign, k in ((1, "l"), (-1, "r")):
        ey, ez = s["eye"]
        eye = on_ellipsoid(head, s["head_r"], (0.86, 0.44 * sign * ey / 0.046, 0.26 * ez / 0.050), 1.0)
        m.objects[f"eye_{k}"].location = eye
        m.put_segment(f"brow_{k}", eye + Vector((-0.002, -0.014 * sign, 0.028)), eye + Vector((-0.008, 0.024 * sign, 0.032)), 0.007)
    cap = head + Vector((s["cap"][0], 0, s["cap"][1]))
    m.objects["cap"].location = cap
    for i, phi in enumerate(s["strands"]):                 # drawn strand lines from the crown to the hairline
        pts = [on_ellipsoid(cap, s["cap_r"], (math.sin(el) * math.cos(phi) - 0.15, math.sin(el) * math.sin(phi), math.cos(el)), 1.02)
               for el in (0.10, 0.40, 0.70, 1.00, 1.28)]
        m.set_tube(f"strand{i}", [tuple(p) for p in pts], [0.0050] * 5)
    out.update(torso=torso, head=head, cap=cap)
    # legs
    for sign, k, phase in ((1, "l", 0.0), (-1, "r", 0.5)):
        hip = Vector((0.0, s["hip_y"] * sign, s["hip_z"])) + up
        fx, fz = _foot(s, t, phase)
        ankle = Vector((fx, s["hip_y"] * sign * 1.12, 0.058 + fz))
        knee, ankle = two_bone(hip, ankle, s["thigh"], s["shin"], Vector((1, 0, 0)))
        m.put_segment(f"thigh_{k}", hip, knee, s["leg_r"] * 1.08)
        m.put_segment(f"shin_{k}", knee, ankle, s["leg_r"] * 0.88)
        m.put_segment(f"bootleg_{k}", ankle, ankle + Vector((0, 0, s["boot_h"])), s["boot_r"])
        frustum(m, f"bootcuff_{k}", ankle + Vector((0, 0, s["boot_h"] - 0.012)), (s["boot_r"] * 1.14, s["boot_r"] * 1.14), 0.030)
        m.objects[f"foot_{k}"].location = ankle + Vector((0.032, 0, -0.014))
        m.objects[f"sole_{k}"].location = ankle + Vector((0.032, 0, -0.050))
        out[f"hip_{k}"], out[f"knee_{k}"], out[f"ankle_{k}"] = hip, knee, ankle
    # arms swing against the legs unless the outfit gives that hand a job
    for sign, k, phase in ((1, "l", 0.5), (-1, "r", 0.0)):
        sh = Vector((-0.004 * sign * twist * 10, s["shoulder_y"] * sign, s["shoulder_z"])) + up
        if k in hands:
            hand = hands[k](sh, a, walking)
        else:
            swing = s["arm_swing"] * math.sin(a + math.pi * 2 * phase) if walking else 0.0
            hand = sh + Vector((swing + 0.020, 0.036 * sign, -0.335 + 0.03 * abs(swing) / max(s["arm_swing"], 1e-3)))
        elbow, hand = two_bone(sh, hand, s["upper_arm"], s["forearm"], Vector((-1, -0.3 * sign, 0)))
        m.put_segment(f"upper_{k}", sh, elbow, s["arm_r"] * 1.10)
        m.put_segment(f"fore_{k}", elbow, hand, s["arm_r"] * 0.90)
        d = (hand - elbow).normalized()
        cuff = m.objects[f"cuff_{k}"]
        cuff.location = hand - d * 0.040
        cuff.rotation_mode = "QUATERNION"
        cuff.rotation_quaternion = d.to_track_quat("Z", "Y")
        cuff.scale = (s["arm_r"] * 1.12, s["arm_r"] * 1.12, 0.034)
        m.objects[f"hand_{k}"].location = hand + d * 0.022
        out[f"shoulder_{k}"], out[f"elbow_{k}"], out[f"hand_{k}"], out[f"arm_dir_{k}"] = sh, elbow, hand + d * 0.022, d
    return out
