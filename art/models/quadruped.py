"""Shared body, legs, walk and pixel rules for every FOUR-LEGGED creature (boar, wolf, ram, mole...).

A creature file only describes what makes it that animal (a SPEC of sizes plus its own extras such as tusks,
a crest or horns) and calls build() / pose() / assign_depth_parts() from here. The rules that make a
four-legged sprite read well are built in, so they cannot be forgotten (see art/QUADRUPED_RULES.md):

  * legs are planted OUTSIDE the body's width (feet splay), so they show from above when walking north/south;
  * shoulder and haunch muscles join the legs to the body, so legs never look like sticks stuck underneath;
  * eyes are pushed onto the head's surface, so they can never be buried inside it;
  * the head is NOT blended into the body: it gets its own dark contour where it overlaps the chest;
  * far-side legs use the darker "far" ramp;
  * each direction is placed against the tile's right and bottom edges (AUTO_PLACE), like Tibia's creatures.

Units are tiles (1 tile = 32 px before SIZE). The animal faces +X, +Y is its left side, +Z is up.
"""
from __future__ import annotations

import math

from mathutils import Vector

PARTS = ["none", "body", "belly", "head", "snout", "nose", "ear", "eye",
         "leg_near", "leg_far", "paw_near", "paw_far", "tail_base", "tail_tip"]

# Tone thresholds for 8-colour ramps. DARK coats need the higher set, or the whole animal turns light grey.
BANDS_MID = [0.34, 0.45, 0.55, 0.64, 0.73, 0.82, 0.90]
BANDS_DARK = [0.42, 0.55, 0.66, 0.75, 0.83, 0.90, 0.96]

DEFAULTS = {
    # body: two overlapping blobs (hindquarters and chest) plus a belly that fills the gap underneath
    "hip": (-0.100, 0.265), "hip_r": (0.118, 0.092, 0.080),          # (x, z), radii
    "chest": (0.050, 0.290), "chest_r": (0.120, 0.105, 0.100),
    "belly_r": (0.150, 0.075, 0.050), "belly_drop": 0.050,
    # head
    "head": (0.205, 0.300), "head_r": (0.085, 0.082, 0.072),
    "snout_tip": (0.360, 0.270), "snout_r": (0.050, 0.040), "snout_blunt": False,
    "nose_r": (0.014, 0.014, 0.013),
    "eye": (0.060, 0.050, 0.035), "eye_r": 0.015,                   # offset from the head centre (x, side, z)
    "ear_root": (-0.030, 0.050, 0.055), "ear_tip": (-0.040, 0.065, 0.135), "ear_r": 0.026,
    # legs: where they leave the body, and where the feet stand (feet_y must clear the body's half-width)
    "front_x": 0.085, "hind_x": -0.125, "leg_top_z": 0.250,
    "front_y": 0.070, "hind_y": 0.065, "front_feet_y": 0.105, "hind_feet_y": 0.095,
    "upper": 0.135, "lower": 0.130, "leg_r": 0.027, "paw_r": (0.030, 0.021, 0.015),
    "shoulder_r": (0.055, 0.038, 0.075), "haunch_r": (0.062, 0.040, 0.075),
    # walk: a diagonal trot (front-left with hind-right)
    "stride": 0.105, "lift": 0.060, "stance": 0.55, "bob": 0.010, "nod": 0.010,
    # tail: length, thickness at root and tip, how far it is raised (0 = hangs, 1 = straight back, 2 = upright)
    "tail_len": 0.22, "tail_r": (0.026, 0.012), "tail_raise": 0.6, "tail_curl": 0.07, "tail_split": 0.7,
}
TAIL_N = 12
LEG_PHASE = {"fl": 0.00, "fr": 0.50, "hl": 0.57, "hr": 0.07}


def spec(**overrides):
    unknown = set(overrides) - set(DEFAULTS)
    if unknown:
        raise KeyError(f"unknown quadruped setting(s): {sorted(unknown)}")
    s = {**DEFAULTS, **overrides}
    for feet, r in (("front_feet_y", "chest_r"), ("hind_feet_y", "hip_r")):
        if s[feet] < s[r][1] * 0.85:
            raise ValueError(f"{feet}={s[feet]} is inside the body (half-width {s[r][1]}): the legs would hide "
                             f"under the body when walking north/south. Plant the feet wider.")
    return s


def pixel_rules(dark=False, weight=None, thin=None, soft=None, texture=None, selout=None, no_outline=None,
                bands=None):
    """The standard treatment for a four-legged creature; pass extras for its own parts (tusks, crest...)."""
    return {
        "weight": {"eye": 9.0, "nose": 3.0, "tail_tip": 3.0, "tail_base": 2.0, "paw_near": 2.2, "paw_far": 1.6,
                   "leg_near": 1.7, "leg_far": 1.2, "ear": 2.2, "snout": 1.3, **(weight or {})},
        "thin": {"eye": 3, "tail_tip": 3, "tail_base": 3, "nose": 3, "leg_near": 4, "leg_far": 4,
                 "paw_near": 3, "paw_far": 4, "ear": 4, **(thin or {})},
        # body+belly are one surface and head+snout+nose are another; the head is NOT soft with the body
        "soft": [["body", "belly"], ["head", "snout", "nose", "ear"], ["leg_near", "paw_near"],
                 ["leg_far", "paw_far"], ["tail_base", "tail_tip"]] + (soft or []),
        "no_outline": no_outline or [],
        "fur": ["body", "head"],
        "texture": {"body": [0.75, 0.22], "belly": [0.5, 0.1], "head": [0.55, 0.12], "snout": [0.3, 0.0],
                    "leg_near": [0.35, 0.0], "leg_far": [0.25, 0.0], "tail_base": [0.5, 0.0], **(texture or {})},
        "bands": bands or (BANDS_DARK if dark else BANDS_MID),
        "selout": ["body", "head", "snout", "ear"] + (selout or []),
    }


def on_surface(centre, radii, point, out=1.03):
    """Move a point onto an ellipsoid's surface along the line from its centre (keeps eyes from being buried)."""
    v = Vector(((point.x - centre.x) / radii[0], (point.y - centre.y) / radii[1], (point.z - centre.z) / radii[2]))
    if v.length < 1e-6:
        return point
    v = v / v.length * out
    return Vector((centre.x + v.x * radii[0], centre.y + v.y * radii[1], centre.z + v.z * radii[2]))


def build(model_cls, facing, s, parts):
    m = model_cls(facing, parts)
    m.spec = s
    m.ellipsoid("hip", "body", radii=s["hip_r"], segments=20, rings=12)
    m.ellipsoid("chest", "body", radii=s["chest_r"], segments=20, rings=12)
    m.ellipsoid("belly", "belly", radii=s["belly_r"], segments=16, rings=8)
    m.ellipsoid("head", "head", radii=s["head_r"], segments=18, rings=12)
    (m.capsule if s["snout_blunt"] else m.cone)("snout", "snout")
    m.ellipsoid("nose", "nose", radii=s["nose_r"], segments=10, rings=6)
    for k in ("l", "r"):
        m.ellipsoid(f"eye_{k}", "eye", radii=(s["eye_r"],) * 3, segments=8, rings=6)
        m.cone(f"ear_{k}", "ear", segments=8)
    for leg in LEG_PHASE:
        front = leg[0] == "f"
        m.ellipsoid(f"{leg}_muscle", "body", radii=s["shoulder_r"] if front else s["haunch_r"], segments=12, rings=8)
        m.capsule(f"{leg}_up", "leg_near")
        m.capsule(f"{leg}_lo", "leg_near")
        m.ellipsoid(f"{leg}_paw", "paw_near", radii=s["paw_r"], segments=8, rings=6)
    split = int(TAIL_N * s["tail_split"])
    m.tube("tail_a", "tail_base", points=split + 1)
    m.tube("tail_b", "tail_tip", points=TAIL_N - split + 1)
    return m


def _foot(s, t, phase, rest_x):
    """Stance: planted, slides back. Swing: lifted, comes forward."""
    if t is None:
        return rest_x, 0.0
    u = (t + phase) % 1.0
    if u < s["stance"]:
        return rest_x + s["stride"] * (1 - 2 * u / s["stance"]), 0.0
    k = (u - s["stance"]) / (1 - s["stance"])
    ease = 0.5 - 0.5 * math.cos(math.pi * k)
    return rest_x + s["stride"] * (-1 + 2 * ease), s["lift"] * math.sin(math.pi * k)


def _leg(m, s, leg, top, foot, front):
    d = foot - top
    dist = min(d.length, s["upper"] + s["lower"] - 1e-4)
    d.normalize()
    side = Vector((0, 0, 1)).cross(d) if abs(d.z) < 0.99 else Vector((0, 1, 0))
    bend = d.cross(side).normalized()
    if bend.x * (-1 if front else 1) < 0:            # front elbows point back, hind knees point forward
        bend = -bend
    a = (s["upper"] ** 2 + dist ** 2 - s["lower"] ** 2) / (2 * dist)
    h = math.sqrt(max(s["upper"] ** 2 - a ** 2, 0.0))
    knee = top + d * a + bend * h
    m.put_segment(f"{leg}_up", top, knee, s["leg_r"] * 1.15)
    m.put_segment(f"{leg}_lo", knee, foot, s["leg_r"] * 0.85)
    m.objects[f"{leg}_paw"].location = foot + Vector((0.012, 0, 0))


def pose(m, t):
    """t = None for the standing frame, else 0..1 through the walk. Returns the moving anchor points
    (chest, hip, head, snout_tip, sway, a) so the creature file can hang its own extras on them."""
    s = m.spec
    if t is None:
        a, stretch, bob, sway, nod = 0.0, 0.0, 0.0, 0.0, 0.0
    else:
        a = 2 * math.pi * t
        stretch = 0.35 * math.cos(2 * a)
        bob = s["bob"] * (0.5 + 0.5 * math.cos(2 * a))
        sway = math.sin(a)
        nod = s["nod"] * math.sin(2 * a + 0.6)
    chest = Vector((s["chest"][0] + 0.016 * stretch, 0, s["chest"][1] + bob))
    hip = Vector((s["hip"][0] - 0.016 * stretch, 0, s["hip"][1] + bob * 0.6 + 0.010 * (1 - stretch) / 2))
    head = Vector((s["head"][0] + 0.018 * stretch, 0, s["head"][1] + bob + nod))
    hd = head - Vector((s["head"][0], 0, s["head"][1]))
    m.objects["chest"].location, m.objects["hip"].location, m.objects["head"].location = chest, hip, head
    m.objects["belly"].location = (chest + hip) / 2 + Vector((0.010, 0, -s["belly_drop"]))
    tip = Vector((s["snout_tip"][0], 0, s["snout_tip"][1])) + hd
    m.put_segment("snout", head + Vector((s["head_r"][0] * 0.25, 0, -s["head_r"][2] * 0.15)), tip, *s["snout_r"])
    m.objects["nose"].location = tip + Vector((-0.004 if not s["snout_blunt"] else 0.0, 0, 0.0))
    for sign, k in ((1, "l"), (-1, "r")):
        e = head + Vector((s["eye"][0], s["eye"][1] * sign, s["eye"][2]))
        m.objects[f"eye_{k}"].location = on_surface(head, s["head_r"], e)
        r0, r1 = s["ear_root"], s["ear_tip"]
        m.put_segment(f"ear_{k}", head + Vector((r0[0], r0[1] * sign, r0[2])),
                      head + Vector((r1[0], r1[1] * sign, r1[2])), s["ear_r"], s["ear_r"] * 0.55)
    for leg, phase in LEG_PHASE.items():
        front, sign = leg[0] == "f", (-1 if leg[1] == "l" else 1)
        body = chest if front else hip
        x = s["front_x"] if front else s["hind_x"]
        top = Vector((x + (body.x - (s["chest"][0] if front else s["hip"][0])), sign * (s["front_y"] if front else s["hind_y"]),
                      s["leg_top_z"] + (body.z - (s["chest"][1] if front else s["hip"][1]))))
        fx, fz = _foot(s, t, phase, x + (0.012 if front else -0.004))
        foot = Vector((fx, sign * (s["front_feet_y"] if front else s["hind_feet_y"]), s["paw_r"][2] + fz))
        _leg(m, s, leg, top, foot, front)
        m.objects[f"{leg}_muscle"].location = top + Vector((0, sign * 0.004, 0.015))
    # tail
    base = hip + Vector((-s["hip_r"][0] * 0.85, 0, s["hip_r"][2] * 0.25))
    ang = (s["tail_raise"] - 1.0) * (math.pi / 2)            # -90 deg hangs, 0 straight back, +90 upright
    pts, radii = [], []
    for i in range(TAIL_N + 1):
        u = i / TAIL_N
        bend = ang + (-0.5 * u if s["tail_raise"] < 1.2 else 0.0)
        p = base + Vector((-math.cos(bend) * s["tail_len"] * u, 0, math.sin(bend) * s["tail_len"] * u))
        p.y = s["tail_curl"] * math.sin(math.pi * u * 0.7) + 0.05 * sway * u * u
        p.z = max(p.z, 0.012)
        pts.append(tuple(p))
        radii.append(s["tail_r"][0] + (s["tail_r"][1] - s["tail_r"][0]) * u)
    split = int(TAIL_N * s["tail_split"])
    m.set_tube("tail_a", pts[:split + 1], radii[:split + 1])
    m.set_tube("tail_b", pts[split:], radii[split:])
    return {"chest": chest, "hip": hip, "head": head, "snout_tip": tip, "sway": sway, "a": a,
            "tail_tip": Vector(pts[-1]), "walking": t is not None}


def assign_depth_parts(m, depth_of):
    """Legs on the far side of the body (seen from the camera) use the darker 'far' ramp."""
    body_depth = (depth_of(m.objects["chest"].matrix_world.translation) +
                  depth_of(m.objects["hip"].matrix_world.translation)) / 2
    for leg in LEG_PHASE:
        far = depth_of(m.objects[f"{leg}_up"].matrix_world.translation) > body_depth + 0.005
        for piece in ("up", "lo"):
            m.set_part(f"{leg}_{piece}", "leg_far" if far else "leg_near")
        m.set_part(f"{leg}_paw", "paw_far" if far else "paw_near")
