"""Hunter Brannoch (Floor 1, the Hunters' Hall), built on art/models/humanoid.py (second draft, 2026-11-25).

ART_REQUESTS.md: "a weathered hunter in brown leathers with a wolf-pelt mantle, a bow across his back, a scar
over one eye". The first draft (2026-11-15) had its own copied body; this one follows art/OUTFIT_RULES.md.

Identity (art/OUTFIT_RULES.md step 1):
  Silhouette: broad; a grey wolf pelt over the shoulders whose head sits on top of his own like a cap (snout
              forward above the brow, ears up: the face still shows, O3), a longbow slung across his back, swept
              back so it shows from the side (O17).
  Colours:    brown leathers, grey wolf pelt with a pale muzzle, dark beard; the bow dark wood.
  Details:    pelt ears and snout, two dark eye slits on the wolf, pale claws hanging at the chest, a scar across his
              left brow, a belt with a knife, bracers, the bowstring.
Addons: none (an NPC, rule A1).
"""
from __future__ import annotations

import math

from mathutils import Euler, Vector

import humanoid as H

NAME = "brannoch"
WALK_FRAMES = 8
PALETTE = "brannoch"
REFERENCE = "outfit_128.png"
PROJECTION = "oblique"
CANVAS_OFFSET = H.CANVAS_OFFSET
SIGNATURE = ["pelt", "bow"]
HEAD_PARTS = ["skin", "hair", "strand", "eye", "brow", "nose", "beard", "pelt", "muzzle", "scar"]
LEG_PARTS = ["leg_a", "leg_b", "boot_a", "boot_b"]
CHECK = {"size": (0.85, 1.45), "head": 0.08, "legs_side": 0.05, "eye": 1}

PARTS = H.PARTS + ["pelt", "muzzle", "wolfeye", "claw", "beard", "scar", "bow", "string", "bracer", "knife"]
PIXEL_RULES = H.pixel_rules(
    weight={"pelt": 1.4, "muzzle": 2.0, "wolfeye": 6.0, "claw": 4.0, "beard": 1.4, "scar": 4.0, "bow": 3.0,
            "string": 3.0, "bracer": 2.2, "knife": 3.0},
    thin={"wolfeye": 2, "claw": 2, "scar": 2, "bow": 2, "string": 2, "bracer": 3, "knife": 2},
    soft=[["pelt", "muzzle", "wolfeye", "claw"], ["skin", "beard", "scar"], ["bow", "string"], ["belt", "knife"]],
    texture={"pelt": [0.6, 0.3], "beard": [0.35, 0.15]},
    fur=["pelt"],
    selout=["pelt", "bow"],
)

SPEC = H.spec(torso_r=(0.110, 0.164, 0.186), arm_r=0.054, leg_r=0.054, stride=0.12, lift=0.055, bob=0.016,
              strands=(-1.2, -0.3, 0.6))


def build(model_cls, facing):
    m = H.build(model_cls, facing, SPEC, PARTS)
    m.ellipsoid("beard", "beard", radii=(0.058, 0.080, 0.050), segments=12, rings=8)
    m.capsule("scar", "scar")
    # the pelt: a cape over the shoulders and back, the wolf's head on top of his head
    m.ellipsoid("pelt_back", "pelt", radii=(0.070, 0.200, 0.200), segments=16, rings=10)
    m.ellipsoid("pelt_sh", "pelt", radii=(0.120, 0.200, 0.060), segments=16, rings=8)
    m.ellipsoid("wolfhead", "pelt", radii=(0.110, 0.104, 0.054), segments=16, rings=8)
    m.ellipsoid("snout", "muzzle", radii=(0.060, 0.040, 0.030), segments=10, rings=6)
    for k in ("l", "r"):
        m.cone(f"ear_{k}", "pelt", segments=6)
        m.ellipsoid(f"weye_{k}", "wolfeye", radii=(0.010, 0.012, 0.006), segments=6, rings=4)
        m.capsule(f"paw_{k}", "pelt")
        m.ellipsoid(f"claw_{k}", "claw", radii=(0.014, 0.020, 0.012), segments=6, rings=4)
        m.frustum(f"bracer_{k}", "bracer", top_ratio=1.0, segments=10)
    m.capsule("knife", "knife")
    m.tube("bow", "bow", points=7)
    m.capsule("bowstring", "string")
    return m


def pose(m, t):
    p = H.pose(m, t)
    up, head, a, walking = p["up"], p["head"], p["a"], p["walking"]
    s = m.spec
    m.objects["beard"].location = head + Vector((0.074, 0, -0.068))
    eye = m.objects["eye_l"].location
    m.put_segment("scar", eye + Vector((0.004, -0.012, 0.050)), eye + Vector((0.004, 0.020, 0.018)), 0.006)   # across the brow, never through the eye pixel
    m.objects["pelt_back"].location = Vector((-0.110, 0, 0.700)) + up
    m.objects["pelt_sh"].location = Vector((-0.010, 0, 0.860)) + up
    wh = head + Vector((-0.010, 0, 0.118))
    o = m.objects["wolfhead"]
    o.rotation_mode = "XYZ"
    o.rotation_euler = Euler((0, -0.12, 0))
    o.location = wh
    m.objects["snout"].location = wh + Vector((0.120, 0, 0.004))
    for sign, k in ((1, "l"), (-1, "r")):
        m.put_segment(f"ear_{k}", wh + Vector((-0.020, 0.060 * sign, 0.030)), wh + Vector((-0.040, 0.070 * sign, 0.090)), 0.026, 0.0)
        m.objects[f"weye_{k}"].location = wh + Vector((0.075, 0.040 * sign, 0.030))
        # forelegs of the pelt hanging over the chest, claws at the ends
        top = Vector((0.060, 0.100 * sign, 0.880)) + up
        low = Vector((0.118, 0.040 * sign, 0.740)) + up
        m.put_segment(f"paw_{k}", top, low, 0.024)
        m.objects[f"claw_{k}"].location = low + Vector((0.010, 0, -0.018))
        e, h = p[f"elbow_{k}"], p[f"hand_{k}"]
        d = (h - e).normalized()
        b = m.objects[f"bracer_{k}"]
        b.location = e + (h - e) * 0.35
        b.rotation_mode = "QUATERNION"
        b.rotation_quaternion = d.to_track_quat("Z", "Y")
        b.scale = (s["arm_r"] * 1.10, s["arm_r"] * 1.10, 0.080)
    belt = Vector((s["torso_r"][0] * 0.6, -s["torso_r"][1] * 0.95, s["belt_z"])) + up
    m.put_segment("knife", belt, belt + Vector((0.020, -0.006, -0.110)), 0.012)
    # longbow across the back: from behind the right hip up past the left shoulder, ends swept back (O17)
    back = Vector((-s["torso_r"][0] * 1.55, 0, 0)) + up
    lo, hi = back + Vector((-0.020, -0.200, 0.420)), back + Vector((-0.040, 0.190, 1.030))
    mid = (lo + hi) / 2 + Vector((-0.090, 0, 0))
    pts = [lo + (hi - lo) * (k / 6) + (mid - (lo + hi) / 2) * math.sin(math.pi * k / 6) for k in range(7)]
    m.set_tube("bow", [tuple(q) for q in pts], [0.010, 0.016, 0.019, 0.020, 0.019, 0.016, 0.010])
    m.put_segment("bowstring", lo, hi, 0.005)


def assign_depth_parts(m, depth_of):
    return None
