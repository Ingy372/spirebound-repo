"""Gate Hound (Floor 1 field boss at the pass): a big four-legged creature built on art/models/quadruped.py.

ART_REQUESTS.md: "a huge three-headed hound with black fur and ember-orange eyes, spiked collar on each neck" (64x64).

Identity (art/QUADRUPED_RULES.md step 1):
  Coat:      sooty slate-blue with ash-pale muzzles and throat (Tibia's Hellhound is red-black, and our Bristle Boar
             is already charcoal-and-ember, so the hound goes cool and lets the embers be the only warm colour).
  Signature: THREE heads on their own necks, each in a black iron collar ringed with pale steel spikes; ember eyes
             and an ember glow in every open jaw.
  Attitude:  guarding the pass: a wide, planted stance, the middle head held high and watchful, the two side heads
             lower, turned outward and snarling, tail low and stiff.

Detail (art/DETAIL_RULES.md): the wolf's coat (neck ruff, saddle tufts, hackles, brows, mouth lines, ear tips) on the
middle head, and for each side head its own neck, brow, mouth line, pinned ears and an open lower jaw; spiked collars
(rims and spikes), pale claws, a raked scar on the shoulder.
Real proportion: a mastiff-sized body that is about 1.6x the meadow wolf's, necks a little longer than a dog's so the
three heads part clearly when seen from above.
"""
from __future__ import annotations

import math

from mathutils import Vector

import quadruped as Q
import wolf

NAME = "gate_hound"
WALK_FRAMES = 8
PALETTE = "gate_hound"
HEIGHT_SHEAR = 0.30
LEAN = 11.0
REFERENCE = "look_240.png"    # Tibia's Hellhound (comparison only, never shipped)
SIZE = 2.2
GROUND_STRETCH = 0.50     # shorter front-to-back so the north/south views fit the canvas
AUTO_PLACE = (1, 1)
SIGNATURE = ["collar", "spike"]   # the ember jaws are an accent: from behind no mouth shows
CHECK = {"eye": 2}
HEAD_PARTS = ["head", "snout", "nose", "head2", "snout2"]

PARTS = Q.PARTS + wolf.FUR_PARTS + ["head2", "snout2", "collar", "spike", "maw", "claw", "scar"]
PIXEL_RULES = wolf.fur_rules(
    weight={"collar": 2.6, "spike": 4.0, "maw": 5.0, "claw": 3.5, "scar": 4.0, "head2": 1.0, "snout2": 1.3},
    thin={"collar": 3, "spike": 2, "maw": 2, "claw": 2, "scar": 2},
    # each side head is its own surface (its own outline against the middle head and the body)
    soft=[["head2", "snout2"], ["collar", "spike"]],
    texture={"body": [0.75, 0.08], "head": [0.55, 0.06], "head2": [0.55, 0.06], "saddle": [0.6, 0.08], "collar": [0.3, 0.0]},
    selout=["head2", "snout2", "collar"],
)
# On a body this big, an outline round every back tuft turns the ridge into black spots: tufts blend in instead.
PIXEL_RULES["selout"] = [p for p in PIXEL_RULES["selout"] if p != "saddle"]

SPEC = Q.spec(
    hip=(-0.135, 0.300), hip_r=(0.120, 0.098, 0.084),
    chest=(0.045, 0.335), chest_r=(0.140, 0.128, 0.115),
    belly_r=(0.170, 0.086, 0.052), belly_drop=0.064,
    head=(0.255, 0.378), head_r=(0.090, 0.080, 0.074),             # the middle head, high and watchful
    snout_tip=(0.405, 0.350), snout_r=(0.050, 0.034),
    nose_r=(0.019, 0.019, 0.016),
    eye=(0.050, 0.050, 0.034), eye_r=0.013,
    ear_root=(-0.030, 0.046, 0.052), ear_tip=(-0.070, 0.064, 0.112), ear_r=0.027,   # half laid back: on guard
    front_x=0.085, hind_x=-0.160, leg_top_z=0.270,
    front_y=0.080, hind_y=0.072, front_feet_y=0.128, hind_feet_y=0.108,   # wide, planted stance
    upper=0.152, lower=0.140, leg_r=0.033, paw_r=(0.036, 0.026, 0.018),
    shoulder_r=(0.070, 0.044, 0.088), haunch_r=(0.070, 0.042, 0.082),
    stride=0.082, lift=0.054, bob=0.008, nod=0.010,
    tail_len=0.200, tail_r=(0.034, 0.018), tail_raise=0.55, tail_curl=0.04, tail_split=0.70,
)

# the two side heads: (sideways offset of the head from the body's centre line, turn outward in radians,
# height below the middle head, how far back)
SIDE = {"l": (0.150, 0.42, 0.075, 0.040), "r": (-0.150, -0.42, 0.060, 0.030)}
SIDE_HEAD_R = (0.084, 0.074, 0.068)
SPIKES = 5


def build(model_cls, facing):
    m = Q.build(model_cls, facing, SPEC, PARTS)
    wolf.build_fur(m)
    for k in ("m", "l", "r"):
        m.ellipsoid(f"collar_{k}", "collar", radii=(0.040, 0.094, 0.090), segments=16, rings=8)   # wider than the neck fur
        for i in range(SPIKES):
            m.cone(f"spike_{k}{i}", "spike", segments=6)
        m.ellipsoid(f"maw_{k}", "maw", radii=(0.030, 0.020, 0.012), segments=10, rings=6)
        m.cone(f"jaw_{k}", "snout2" if k != "m" else "snout", segments=8)
    for k in SIDE:
        m.capsule(f"neck_{k}", "body", segments=12)
        m.ellipsoid(f"head_{k}", "head2", radii=SIDE_HEAD_R, segments=16, rings=10)
        m.cone(f"snout_{k}", "snout2", segments=10)
        m.ellipsoid(f"nose_{k}", "nose", radii=(0.017, 0.017, 0.014), segments=8, rings=6)
        for e in ("a", "b"):
            m.ellipsoid(f"eye_{k}{e}", "eye", radii=(0.012,) * 3, segments=8, rings=6)
            m.cone(f"ear_{k}{e}", "ear", segments=8)
            m.capsule(f"brow_{k}{e}", "brow", segments=6)
        m.capsule(f"smouth_{k}", "line", segments=6)   # not mouth_l/r: the wolf coat owns those names
    for leg in Q.LEG_PHASE:
        for c in range(2):
            m.cone(f"claw_{leg}{c}", "claw", segments=5)
    for i in range(3):
        m.capsule(f"scar{i}", "scar", segments=6)
    return m


def _frame(turn):
    """Forward and sideways unit vectors for a head turned by `turn` radians (left is +)."""
    f = Vector((math.cos(turn), math.sin(turn), 0.0))
    return f, Vector((-math.sin(turn), math.cos(turn), 0.0))


def _collar(m, k, centre, forward, walking, a):
    """A black iron collar around the neck just behind the head, ringed with pale spikes pointing out and up."""
    ob = m.objects[f"collar_{k}"]
    ob.location = centre
    ob.rotation_mode = "XYZ"
    ob.rotation_euler = (0.0, -0.35, math.atan2(forward.y, forward.x))
    side = Vector((-forward.y, forward.x, 0.0))
    for i in range(SPIKES):
        ang = -1.35 + 2.7 * i / (SPIKES - 1)                 # round the top half of the collar
        out = side * math.sin(ang) * 0.090 + Vector((0, 0, math.cos(ang) * 0.086))
        root = centre + out
        tip = root + out.normalized() * 0.046 + Vector((0, 0, 0.008))
        m.put_segment(f"spike_{k}{i}", root, tip, 0.014, 0.003)


def _jaw(m, k, head, tip, forward, walking, a, phase):
    """An open lower jaw under the snout with an ember glow between the jaws."""
    gape = 0.018 + (0.008 * math.sin(a * 2 + phase) if walking else 0.0)
    j0 = head + forward * 0.045 + Vector((0, 0, -0.050))
    j1 = tip + Vector((0, 0, -0.030 - gape))
    m.put_segment(f"jaw_{k}", j0, j1, 0.032, 0.014)
    m.objects[f"maw_{k}"].location = j0.lerp(j1, 0.62) + Vector((0, 0, 0.016))
    m.objects[f"maw_{k}"].rotation_mode = "XYZ"
    m.objects[f"maw_{k}"].rotation_euler = (0, 0, math.atan2(forward.y, forward.x))


def pose(m, t):
    p = Q.pose(m, t)
    wolf.pose_fur(m, p, SPEC)
    chest, head, tip, a, walking = p["chest"], p["head"], p["snout_tip"], p["a"], p["walking"]
    fwd = Vector((1, 0, 0))
    # middle head: collar and open jaw
    _collar(m, "m", head + Vector((-0.118, 0, -0.040)), fwd, walking, a)       # on the neck, clear of the head
    _jaw(m, "m", head, tip, fwd, walking, a, 0.0)
    base = chest + Vector((0.070, 0, 0.060))                  # where the three necks leave the shoulders
    for k, (dy, turn, drop, back) in SIDE.items():
        f, s = _frame(turn)
        # the side heads nod out of step with each other and with the middle head: the walk's second motion
        nod = (0.014 * math.sin(a * 2 + (1.6 if k == "l" else -1.6))) if walking else 0.0
        h = Vector((head.x - back, dy, head.z - drop + nod))
        hr = SIDE_HEAD_R
        m.objects[f"head_{k}"].location = h
        m.objects[f"head_{k}"].rotation_mode = "XYZ"
        m.objects[f"head_{k}"].rotation_euler = (0, 0, turn)
        m.put_segment(f"neck_{k}", base + Vector((0, dy * 0.45, 0)), h - f * 0.040 + Vector((0, 0, -0.020)), 0.060, 0.050)
        st = h + f * 0.152 + Vector((0, 0, -0.030))
        m.put_segment(f"snout_{k}", h + f * hr[0] * 0.25 + Vector((0, 0, -hr[2] * 0.15)), st, 0.046, 0.030)
        m.objects[f"nose_{k}"].location = st - f * 0.004
        for sign, e in ((1, "a"), (-1, "b")):
            eye = Q.on_surface(h, (hr[0], hr[0], hr[2]), h + f * 0.048 + s * 0.046 * sign + Vector((0, 0, 0.032)))
            m.objects[f"eye_{k}{e}"].location = eye
            # brows slant down toward the snout: snarling
            m.put_segment(f"brow_{k}{e}", eye - f * 0.028 + s * 0.006 * sign + Vector((0, 0, 0.020)),
                          eye + f * 0.026 - s * 0.006 * sign + Vector((0, 0, 0.006)), 0.011)
            # ears pinned back flat
            r0 = h - f * 0.030 + s * 0.044 * sign + Vector((0, 0, 0.046))
            m.put_segment(f"ear_{k}{e}", r0, r0 - f * 0.085 + s * 0.020 * sign + Vector((0, 0, 0.040)), 0.025, 0.013)
        mouth_side = s * (0.032 if k == "r" else -0.032)          # the mouth line on the side facing out
        m.put_segment(f"smouth_{k}", h + f * 0.060 + mouth_side + Vector((0, 0, -0.040)), st - f * 0.030 + mouth_side * 0.6 + Vector((0, 0, -0.014)), 0.007)
        _collar(m, k, h - f * 0.112 + Vector((0, 0, -0.036)), f, walking, a)
        _jaw(m, k, h, st, f, walking, a, 1.6 if k == "l" else -1.6)
    # pale claws on every paw
    for leg in Q.LEG_PHASE:
        paw = m.objects[f"{leg}_paw"].location
        sign = -1 if leg[1] == "l" else 1
        for c in range(2):
            root = paw + Vector((0.020, (c - 0.5) * 0.024, 0.004))
            m.put_segment(f"claw_{leg}{c}", root, root + Vector((0.026, (c - 0.5) * 0.010, -0.010)), 0.008, 0.002)
    # an old raked scar across the shoulder facing the camera when walking east
    for i in range(3):
        q = chest + Vector((-0.020 + 0.026 * i, -0.118, 0.070))
        m.put_segment(f"scar{i}", q, q + Vector((0.030, -0.006, -0.050)), 0.006)


def assign_depth_parts(m, depth_of):
    Q.assign_depth_parts(m, depth_of)
