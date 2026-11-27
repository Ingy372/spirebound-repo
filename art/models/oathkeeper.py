"""The Oathkeeper (Floor 1, the Oathroom under the Old Quarry, FD3): the boss of the Healer's hall, for four at level
30. "Hold the stair. The oath is kept." Built on art/models/humanoid.py (first draft, 2026-11-27).

Story (docs/superpowers/specs/2026-11-27-floor1-depth-design.md 4.3): the First Climb swore their oath in a sealed hall
under the Old Quarry; four halls, one for each who swore. The Oathkeeper is the oath's warden, still standing in the
Healer's hall, drawing life from four braziers. Undead: an empty suit kept walking by the oath, its light the warm gold
of the braziers.

ART_REQUESTS.md (Session C): "a tall armoured knight in faded blue and bronze with an unlit lantern on his belt;
compare with Tibia's knight-type bosses and make him clearly ours (no helmet crest, a cracked oath-stone on his chest)".

Identity (art/OUTFIT_RULES.md step 1; a monster, so O20: no class-outfit signature):
  Silhouette: a tall knight, a head taller than the Stairwardens and broader (the Axe-Lord stays the giant): a rounded
              crestless great-helm with a cross-shaped visor, big round pauldrons, a long faded-blue cape, a tall shield
              on the left arm and a flanged mace in the right hand.
  Colours:    pale tarnished silver plate (the Stairwardens are blackened iron; the Axe-Lord rusted bronze), a faded
              cornflower-blue tabard, cape and shield field, bronze trim, a warm gold light in the visor and in the
              crack of the oath-stone (the Stairwardens' light is cold blue).
  Details:    the pale oath-stone on the breastplate with a glowing crack across it, the shield's ivory raised hand
              (the oath sign) and bronze rim, bronze pauldron rims and rivets, a gorget, knee and elbow cops, a tabard
              hem in bronze, the unlit lantern hanging at the left hip, the mace's flanges.
  Attitude:   the guardian: upright, shield forward, mace ready, a slow heavy step; he holds the line, he does not chase.
Look-alike: Tibia's Lich (an undead boss in robes with a staff) and Skeleton Warrior (an undead armed guard); ours is
a whole knight in pale plate with a shield, a cape and warm light inside, never bone or robes.
Addons: none (a monster, rule A1).
"""
from __future__ import annotations

import math

from mathutils import Euler, Matrix, Vector

import humanoid as H

NAME = "oathkeeper"
WALK_FRAMES = 8
PALETTE = "oathkeeper"
REFERENCE = "look_99.png"     # Tibia's Lich (comparison only, never shipped)
SIZE = 1.32
HEIGHT_SHEAR = 0.30           # the tilted monster camera, like the Axe-Lord: a boss shows its whole front
LEAN = 0.0
AUTO_PLACE = (1, 1)
SIGNATURE = ["cloth", "trim", "helm"]
HEAD_PARTS = ["helm", "visor", "eye", "nose", "brow"]
LEG_PARTS = ["leg_a", "leg_b", "boot_a", "boot_b"]
# a party boss: tall, but under the Axe-Lord; the closed helm is a small share of a big figure
CHECK = {"size": (0.85, 1.40), "head": 0.06, "legs_side": 0.03, "legs_updown": 0.02, "eye": 1}

PARTS = H.PARTS + ["helm", "visor", "trim", "cloth", "stone", "crack", "glow", "shield", "sign", "haft", "steel",
                   "lantern", "rivet"]
PIXEL_RULES = H.pixel_rules(
    weight={"eye": 9.0, "glow": 6.0, "crack": 7.0, "trim": 2.6, "rivet": 4.0, "visor": 3.0, "stone": 3.0,
            "sign": 3.5, "haft": 1.8, "steel": 2.2, "lantern": 2.6, "shield": 1.6},
    thin={"trim": 2, "rivet": 2, "visor": 2, "crack": 2, "sign": 2, "haft": 3, "glow": 2, "lantern": 2},
    soft=[["helm", "visor", "eye", "nose", "brow", "strand", "hair"], ["torso", "stone", "crack", "rivet"],
          ["cloth", "trim"], ["shield", "sign", "trim"], ["haft", "steel"], ["lantern", "glow"]],
    texture={"torso": [0.25, 0.25], "helm": [0.22, 0.20], "cloth": [0.45, 0.20], "shield": [0.35, 0.20],
             "arm_a": [0.25, 0.2], "arm_b": [0.25, 0.2], "leg_a": [0.25, 0.1], "leg_b": [0.25, 0.1], "haft": [0.5, 0.0]},
    selout=["cloth", "helm", "shield"],
    no_outline=["glow", "crack"],            # the gold light shows THROUGH the plate: no dark rim round it
)

SPEC = H.spec(
    body_scale=(1.34, 1.38, 1.22), beast=True,
    torso_r=(0.120, 0.172, 0.200), arm_r=0.054, leg_r=0.056,
    head_z=0.975, head_r=(0.118, 0.110, 0.126),                          # the rounded great-helm, no crest
    eye=(0.036, 0.014), eye_r=(0.012, 0.022, 0.010),                    # two warm slits behind the visor
    cap=(-0.010, 0.060), cap_r=(0.100, 0.096, 0.070), strands=(0.0,),   # the helm's dome; its one strand is tucked away
    boot_h=0.13, boot_r=0.064, foot_r=(0.086, 0.054, 0.048),
    stride=0.10, lift=0.045, bob=0.012, arm_swing=0.06, belt_z=0.540,
)


def build(model_cls, facing):
    m = H.build(model_cls, facing, SPEC, PARTS)
    for name in ("head", "neck", "cap"):
        m.set_part(name, "helm")
    for k in ("l", "r"):
        m.set_part(f"brow_{k}", "visor")
    for i in range(len(SPEC["strands"])):
        m.set_part(f"strand{i}", "trim")
    m.box("visor_h", "visor", size=(1, 1, 1))           # the cross-shaped visor: a slit and a breathing bar
    m.box("visor_v", "visor", size=(1, 1, 1))
    m.frustum("gorget", "trim", top_ratio=0.80, segments=16)
    m.ellipsoid("gap_neck", "glow", radii=(1, 1, 1), segments=10, rings=6)
    for k in ("l", "r"):
        m.ellipsoid(f"pauldron_{k}", "torso", radii=(0.080, 0.092, 0.048), segments=14, rings=8)
        m.frustum(f"prim_{k}", "trim", top_ratio=1.0, segments=14)
        m.ellipsoid(f"rivet_{k}", "rivet", radii=(0.013, 0.013, 0.013), segments=6, rings=4)
        m.ellipsoid(f"kneecop_{k}", "steel", radii=(0.048, 0.052, 0.048), segments=10, rings=6)
        m.ellipsoid(f"couter_{k}", "steel", radii=(0.038, 0.040, 0.038), segments=8, rings=6)
    for k in ("f", "b"):
        m.box(f"tabard_{k}", "cloth", size=(1, 1, 1))
        m.box(f"hem_{k}", "trim", size=(1, 1, 1))
    for k in ("l", "r"):                                 # the cape in two panels with a fold down the middle
        m.box(f"cape_{k}", "cloth", size=(1, 1, 1))
        m.box(f"cape_hem_{k}", "trim", size=(1, 1, 1))
    for i in range(2):
        m.capsule(f"fold{i}", "brow", segments=5)
    m.ellipsoid("stone", "stone", radii=(1, 1, 1), segments=14, rings=8)
    m.ellipsoid("stone_rim", "trim", radii=(1, 1, 1), segments=14, rings=8)
    for i in range(3):
        m.capsule(f"crack{i}", "crack", segments=5)
    # the tall shield on the left arm, with a bronze rim and the ivory raised hand
    m.ellipsoid("shield", "shield", radii=(1, 1, 1), segments=18, rings=10)
    m.ellipsoid("shield_rim", "trim", radii=(1, 1, 1), segments=18, rings=10)
    m.ellipsoid("palm", "sign", radii=(1, 1, 1), segments=10, rings=6)
    for i in range(4):
        m.capsule(f"finger{i}", "sign", segments=5)
    m.capsule("thumb", "sign", segments=5)
    # the flanged mace in the right hand
    m.capsule("haft", "haft", segments=10)
    m.ellipsoid("mace", "steel", radii=(1, 1, 1), segments=12, rings=8)
    for i in range(4):
        m.box(f"flange{i}", "steel", size=(1, 1, 1))
    # the unlit lantern at the left hip
    m.box("lantern", "lantern", size=(1, 1, 1))
    m.cone("lantern_top", "lantern", segments=8)
    m.capsule("lantern_ring", "lantern", segments=6)
    return m


def _shield_hand(sh, a, walking):
    return sh + Vector((0.150, 0.050, -0.230))          # the shield held forward on the left


def _mace_hand(sh, a, walking):
    swing = 0.04 * math.sin(a) if walking else 0.0
    return sh + Vector((0.110 + swing, -0.060, -0.270))


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


def _disc(obj, centre, normal, radii):
    """A flat ellipsoid facing `normal`, radii = (across, up, thickness)."""
    obj.location = centre
    n = normal.normalized()
    up = Vector((0, 0, 1))
    across = up.cross(n).normalized()
    upv = n.cross(across).normalized()
    _orient(obj, across, upv, n)
    obj.scale = radii


def pose(m, t):
    p = H.pose(m, t, hands={"l": _shield_hand, "r": _mace_hand})
    up, head, torso, a, walking = p["up"], p["head"], p["torso"], p["a"], p["walking"]
    hr, tr = SPEC["head_r"], SPEC["torso_r"]
    m.set_tube("strand0", [(0, 0, 0.30)] * 5, [0.0001] * 5)     # no crest line on the helm (Session C's brief)
    # the cross-shaped visor on the helm's face; the warm eyes glow just in front of the slit
    face = head + Vector((hr[0] * 0.92, 0, SPEC["eye"][1] + 0.002))
    for name, sc, off in (("visor_h", (0.030, hr[1] * 1.40, 0.034), 0.0), ("visor_v", (0.030, 0.030, 0.110), -0.050)):
        v = m.objects[name]
        v.location = face + Vector((0, 0, off))
        v.rotation_mode = "XYZ"
        v.rotation_euler = Euler((0, 0, 0))
        v.scale = sc
    for k in ("l", "r"):
        m.objects[f"eye_{k}"].location += Vector((0.024, 0, 0))
    H.frustum(m, "gorget", torso + Vector((0, 0, tr[2] * 0.80)), (0.100, 0.124), 0.066)
    m.objects["gap_neck"].location = head + Vector((0.020, 0, -hr[2] * 0.95))
    m.objects["gap_neck"].scale = (0.070, 0.090, 0.024)
    for sign, k in ((1, "l"), (-1, "r")):
        sh = p[f"shoulder_{k}"]
        pa = m.objects[f"pauldron_{k}"]
        pa.location = sh + Vector((-0.005, 0.024 * sign, 0.046))
        pa.rotation_mode = "XYZ"
        pa.rotation_euler = Euler((0.45 * sign, 0, 0))
        H.frustum(m, f"prim_{k}", pa.location + Vector((0, 0.024 * sign, -0.030)), (0.078, 0.086), 0.014, rot=(0.45 * sign, 0, 0))
        m.objects[f"rivet_{k}"].location = pa.location + Vector((0.046, 0.054 * sign, 0.022))
        m.objects[f"kneecop_{k}"].location = p[f"knee_{k}"] + Vector((0.044, 0, 0.012))
        m.objects[f"couter_{k}"].location = p[f"elbow_{k}"] + Vector((-0.022, 0.010 * sign, 0.010))
    # tabard front and back with a bronze hem; a long cape from the shoulders, swaying behind
    sway = 0.06 * math.sin(a) if walking else 0.0
    for k, x, lean in (("f", tr[0] * 0.98, 0.06), ("b", -tr[0] * 0.98, -0.06)):
        top = Vector((x, 0, SPEC["belt_z"] + 0.200)) + up
        tilt = lean + (sway if k == "f" else -sway)
        bottom = top + Vector((0.200 * math.sin(tilt), 0, -0.440))
        _slab(m.objects[f"tabard_{k}"], bottom, top, Vector((0, 1, 0)), 0.190, 0.022)
        _slab(m.objects[f"hem_{k}"], bottom, bottom + (top - bottom).normalized() * 0.030, Vector((0, 1, 0)), 0.196, 0.028)
    flutter = 0.025 * math.sin(a + 0.9) if walking else 0.0
    for k, sgn in (("l", 1), ("r", -1)):
        # each panel hangs from a shoulder, angled back from the middle fold so the cape has depth
        ctop = Vector((-tr[0] - 0.012, 0.085 * sgn, SPEC["shoulder_z"] + 0.010)) + up
        cbot = Vector((-tr[0] - 0.070 - flutter, 0.110 * sgn, 0.330)) + up * 0.5
        wdir = Vector((0.30, sgn * 1.0, 0)).normalized()
        _slab(m.objects[f"cape_{k}"], cbot, ctop, wdir, 0.180, 0.020)
        _slab(m.objects[f"cape_hem_{k}"], cbot, cbot + (ctop - cbot).normalized() * 0.030, wdir, 0.184, 0.026)
    for i, (y, z0) in enumerate(((0.000, 0.700), (0.000, 0.480))):
        q0 = Vector((-tr[0] - 0.030 - 0.020 * (1 - z0), y, z0 + 0.120)) + up
        q1 = Vector((-tr[0] - 0.050 - 0.040 * (1 - z0) - flutter, y, z0 - 0.150)) + up
        m.put_segment(f"fold{i}", q0, q1, 0.007)
    # the oath-stone on the breastplate, cracked across, the crack glowing gold
    chest = torso + Vector((tr[0] * 0.98 + 0.012, 0, 0.060))
    _disc(m.objects["stone_rim"], chest, Vector((1, 0, 0.15)), (0.080, 0.080, 0.016))
    _disc(m.objects["stone"], chest + Vector((0.006, 0, 0)), Vector((1, 0, 0.15)), (0.068, 0.068, 0.018))
    zig = [Vector((0.026, -0.044, 0.040)), Vector((0.028, -0.010, 0.008)), Vector((0.028, 0.012, 0.016)), Vector((0.026, 0.044, -0.030))]
    for i in range(3):
        m.put_segment(f"crack{i}", chest + zig[i], chest + zig[i + 1], 0.008)
    # the shield: tall, held forward on the left arm, its face turned out and forward
    hand = p["hand_l"]
    normal = Vector((0.85, 0.50, 0.05))
    sc = hand + Vector((0.050, 0.040, 0.030))
    _disc(m.objects["shield_rim"], sc, normal, (0.150, 0.215, 0.022))
    _disc(m.objects["shield"], sc + normal.normalized() * 0.010, normal, (0.135, 0.200, 0.024))
    n = normal.normalized()
    across = Vector((0, 0, 1)).cross(n).normalized()
    upv = n.cross(across).normalized()
    face = sc + n * 0.034
    _disc(m.objects["palm"], face + upv * (-0.020), normal, (0.034, 0.040, 0.010))
    for i in range(4):
        x = (i - 1.5) * 0.017
        base = face + upv * 0.012 + across * x
        m.put_segment(f"finger{i}", base, base + upv * (0.060 - 0.010 * abs(i - 1.5)), 0.008)
    tb = face + upv * (-0.020) + across * 0.034
    m.put_segment("thumb", tb, tb + across * 0.030 + upv * 0.026, 0.008)
    # the flanged mace, held low in the right hand, head forward
    hand = p["hand_r"]
    axis = Vector((0.55, -0.15, 0.82)).normalized()
    m.put_segment("haft", hand - axis * 0.080, hand + axis * 0.300, 0.016)
    mh = hand + axis * 0.320
    mo = m.objects["mace"]
    mo.location = mh
    mo.scale = (0.040, 0.040, 0.052)
    side = axis.cross(Vector((0, 0, 1))).normalized()
    up2 = side.cross(axis).normalized()
    for i in range(4):
        ang = i * math.pi / 2 + 0.4
        d = side * math.cos(ang) + up2 * math.sin(ang)
        _slab(m.objects[f"flange{i}"], mh - axis * 0.050 + d * 0.040, mh + axis * 0.050 + d * 0.040, d, 0.040, 0.012)
    # the unlit lantern hanging at the left hip, swinging a little
    belt = Vector((0.020, SPEC["torso_r"][1] * 1.02, SPEC["belt_z"] - 0.010)) + up
    swing = 0.020 * math.sin(a + 0.6) if walking else 0.0
    lc = belt + Vector((0.020 + swing, 0.030, -0.090))
    lo = m.objects["lantern"]
    lo.location = lc
    lo.rotation_mode = "XYZ"
    lo.rotation_euler = Euler((0, 0, 0.3))
    lo.scale = (0.046, 0.046, 0.070)
    m.put_segment("lantern_top", lc + Vector((0, 0, 0.035)), lc + Vector((0, 0, 0.065)), 0.034, 0.006)
    m.put_segment("lantern_ring", belt + Vector((0.010, 0.020, 0)), lc + Vector((0, 0, 0.065)), 0.006)


def assign_depth_parts(m, depth_of):
    return None
