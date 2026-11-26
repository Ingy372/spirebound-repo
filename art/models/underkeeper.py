"""The Underkeeper: the boss of the Underkeep, the dungeon under Hearthgate (2x2 tiles), built on humanoid.py.

gen_monsters.py: undead, 180,000 health, melee, a cleave and a howl; "You dug too deep." DESIGN.md 3.4: a dark stone
dungeon under the city, entered by a drain grate. A money monster (ART_REQUESTS.md Batch 11).

Identity (art/OUTFIT_RULES.md step 1; a monster, so O20: no class-outfit signature):
  Silhouette: a towering, gaunt skeletal jailer stooped forward under a low ceiling, in a long tattered robe, his
              skull locked inside an iron cage-helm; a lantern held out in front of him on a bony arm, and a heavy
              chain in the other fist dragging along the floor behind him to a huge padlock.
  Colours:    old bone, black iron, rotted grey-brown cloth, ghost-teal fire in the lantern and his eye sockets,
              tarnished brass keys, a rust-red padlock. (Tibia's skeletons are bare bone; Azhrakkar is blue, the
              Axe-Lord bronze: the Underkeeper is the grey-and-teal one.)
  Details:    cage-helm bars and brow band, glowing eye sockets, a jaw, ribs showing through the torn robe front,
              iron shackles on both wrists, a ring of keys hanging at the belt, the lantern's frame, handle and flame,
              chain links and the padlock, a frayed hem.
  Attitude:   patient and terrible: stooped, slow and heavy, the lantern swinging and the chain scraping behind.
Look-alike: Tibia's Demon for the size of a 2x2 boss, its Skeleton for "undead"; ours is a robed jailer, not a bare
skeleton or a fiend.
"""
from __future__ import annotations

import math

from mathutils import Euler, Vector

import humanoid as H

NAME = "underkeeper"
WALK_FRAMES = 8
PALETTE = "underkeeper"
REFERENCE = "look_35.png"     # Tibia's Demon: the size bar for a 2x2 boss (comparison only, never shipped)
HEIGHT_SHEAR = 0.30
LEAN = 0.0
AUTO_PLACE = (1, 1)
SIGNATURE = ["flame", "chain", "iron"]   # the lantern reads by its glowing flame; its frame is a few pixels
HEAD_PARTS = ["skin", "eye", "brow", "nose", "iron", "hair"]
LEG_PARTS = ["leg_a", "leg_b", "boot_a", "boot_b"]
# a robed giant: the legs are under the robe (rule O10), the caged skull is a modest share of a tall figure
CHECK = {"size": (0.80, 1.05), "head": 0.06, "legs_side": 0.0, "legs_updown": 0.0, "eye": 1}

PARTS = H.PARTS + ["bone", "robe", "hem", "iron", "chain", "lock", "lantern", "flame", "key", "rib"]
PIXEL_RULES = H.pixel_rules(
    weight={"eye": 9.0, "flame": 4.0, "iron": 2.2, "chain": 2.4, "lock": 3.0, "lantern": 2.6, "key": 3.5, "rib": 3.0,
            "hem": 2.0, "bone": 1.4},
    thin={"flame": 2, "chain": 2, "key": 2, "rib": 2, "iron": 2, "hem": 2},
    soft=[["torso", "robe", "hem", "rib", "bone"], ["skin", "eye", "brow", "nose"], ["lantern", "flame"], ["chain", "lock"]],
    texture={"torso": [0.45, 0.30], "robe": [0.45, 0.30], "hem": [0.4, 0.2], "skin": [0.35, 0.15], "bone": [0.35, 0.15],
             "arm_a": [0.35, 0.15], "arm_b": [0.35, 0.15], "iron": [0.3, 0.15], "chain": [0.2, 0.0]},
    selout=["robe", "iron", "lantern"],
    no_outline=["flame"],
)

SPEC = H.spec(
    body_scale=(1.24, 1.24, 1.42), beast=True,
    hip_z=0.46, hip_y=0.090, thigh=0.24, shin=0.24, leg_r=0.050,
    torso_z=0.73, torso_r=(0.150, 0.215, 0.215),
    shoulder_y=0.240, shoulder_z=0.900, upper_arm=0.25, forearm=0.25, arm_r=0.045,       # long, bony arms
    head_z=1.020, head_r=(0.115, 0.105, 0.125),
    eye=(0.044, 0.020), eye_r=(0.020, 0.020, 0.018),                                  # glowing sockets
    cap=(-0.010, 0.060), cap_r=(0.080, 0.060, 0.040), strands=(-0.8, 0.8),           # the cage's crown bar
    boot_h=0.07, boot_r=0.055, foot_r=(0.080, 0.050, 0.040),
    stride=0.10, lift=0.040, bob=0.016, arm_swing=0.05, belt_z=0.560,
    robe=("robe", "hem", 0.200),
)
BARS = 5
KEYS = 4
LINKS = 9


def build(model_cls, facing):
    m = H.build(model_cls, facing, SPEC, PARTS)
    m.set_part("cap", "iron")
    for i in range(len(SPEC["strands"])):
        m.set_part(f"strand{i}", "iron")
    m.set_part("neck", "bone")
    m.ellipsoid("jaw", "bone", radii=(0.070, 0.080, 0.035), segments=12, rings=6)
    m.frustum("band", "iron", top_ratio=1.0, segments=16)                          # the cage's brow band
    for i in range(BARS):
        m.capsule(f"bar{i}", "iron", segments=6)
    m.ellipsoid("mantle", "robe", radii=(0.190, 0.270, 0.090), segments=16, rings=8)   # ragged shoulder cloth
    m.ellipsoid("chest", "bone", radii=(0.040, 0.110, 0.110), segments=12, rings=8)    # the ribcage through the rent
    for i in range(3):
        m.capsule(f"rib{i}", "rib", segments=6)
    for k in ("l", "r"):
        m.frustum(f"shackle_{k}", "iron", top_ratio=1.0, segments=10)
    m.frustum("keyring", "key", top_ratio=1.0, segments=12)
    for i in range(KEYS):
        m.capsule(f"key{i}", "key", segments=6)
    # the lantern: an iron cage around a teal flame, on a handle
    m.frustum("lantern", "lantern", top_ratio=0.75, segments=8)
    m.cone("lantern_top", "lantern", segments=8)
    m.ellipsoid("flame", "flame", radii=(0.058, 0.058, 0.074), segments=10, rings=6)   # bigger than the frame: the fire glows out
    m.capsule("handle", "iron", segments=6)
    # the chain and its padlock
    m.tube("chain", "chain", points=LINKS)
    for i in range(LINKS // 2):
        m.ellipsoid(f"link{i}", "chain", radii=(0.030, 0.012, 0.022), segments=8, rings=4)
    m.box("lock", "lock", size=(0.090, 0.050, 0.080))
    m.frustum("shackle_lock", "iron", top_ratio=1.0, segments=10)
    return m


def _lantern_hand(sh, a, walking):
    swing = 0.020 * math.sin(a) if walking else 0.0          # held out in front, swinging a little
    return Vector((0.100 + swing, 0.450, 0.560)) + Vector((0, 0, sh.z - SPEC["shoulder_z"]))   # out to his side: seen from every direction


def _chain_hand(sh, a, walking):
    heft = 0.015 * math.sin(2 * a) if walking else 0.0
    return Vector((0.040, -0.300, 0.500 + heft)) + Vector((0, 0, sh.z - SPEC["shoulder_z"]))


def pose(m, t):
    p = H.pose(m, t, hands={"l": _lantern_hand, "r": _chain_hand})
    up, head, torso, a, walking = p["up"], p["head"], p["torso"], p["a"], p["walking"]
    hr, tr = SPEC["head_r"], SPEC["torso_r"]
    # stooped: the head pushed forward and down under the low ceiling
    fwd = Vector((0.110, 0, -0.050))
    for name in ("head", "cap", "nose", "eye_l", "eye_r", "brow_l", "brow_r"):
        m.objects[name].location = m.objects[name].location + fwd
    for i in range(len(SPEC["strands"])):
        sp = m.objects[f"strand{i}"].data.splines[0]
        for pt in sp.points:
            pt.co = (pt.co[0] + fwd.x, pt.co[1], pt.co[2] + fwd.z, 1.0)
    head = head + fwd
    m.put_segment("neck", torso + Vector((0.050, 0, tr[2] * 0.70)), head - Vector((0.020, 0, 0.040)), 0.040)
    m.objects["jaw"].location = head + Vector((0.050, 0, -0.100))
    # the cage-helm: a band round the brow and bars over the skull
    H.frustum(m, "band", head + Vector((0, 0, 0.020)), (hr[0] * 1.10, hr[1] * 1.10), 0.030)
    for i in range(BARS):
        ang = -1.3 + 2.6 * i / (BARS - 1)
        side = math.sin(ang)
        front = math.cos(ang)
        base = head + Vector((front * hr[0] * 1.05 * 0.6, side * hr[1] * 1.08, 0.030))
        m.put_segment(f"bar{i}", base + Vector((0, 0, -0.080)), base + Vector((-0.040 * front, -0.010 * side, hr[2] * 0.95)), 0.010)
    # ragged mantle on the shoulders, the ribcage showing through the torn robe front
    m.objects["mantle"].location = torso + Vector((-0.010, 0, tr[2] * 0.70))
    m.objects["chest"].location = torso + Vector((tr[0] * 0.92, 0, 0.040))
    for i in range(3):
        q = torso + Vector((tr[0] * 1.02, 0, 0.110 - 0.050 * i))
        m.put_segment(f"rib{i}", q + Vector((0, -0.080, -0.010)), q + Vector((0, 0.080, -0.010)), 0.010)
    # iron shackles on both wrists
    for k in ("l", "r"):
        hand, d = p[f"hand_{k}"], p[f"arm_dir_{k}"]
        sh = m.objects[f"shackle_{k}"]
        sh.location = hand - d * 0.060
        sh.rotation_mode = "QUATERNION"
        sh.rotation_quaternion = d.to_track_quat("Z", "Y")
        sh.scale = (0.055, 0.055, 0.040)
    # the ring of keys at his left hip, swinging
    ring = Vector((0.040, 0.200, SPEC["belt_z"] - 0.020)) + up
    H.frustum(m, "keyring", ring, (0.050, 0.050), 0.012, rot=(1.57, 0, 0))
    for i in range(KEYS):
        sw = 0.020 * math.sin(a * 2 + i) if walking else 0.0
        q = ring + Vector((-0.030 + 0.020 * i, 0.010, -0.040))
        m.put_segment(f"key{i}", q, q + Vector((sw, 0.005, -0.090)), 0.012)
    # the lantern hanging from the left fist
    hand = p["hand_l"]
    sway = 0.040 * math.sin(a + 0.6) if walking else 0.0
    top = hand + Vector((0.020, 0, -0.050))
    low = top + Vector((sway, 0, -0.130))
    m.put_segment("handle", hand, top, 0.010)
    H.frustum(m, "lantern", low, (0.050, 0.050), 0.030)                      # only a base: an open cage, not a box
    m.put_segment("lantern_top", low + Vector((0, 0, 0.130)), low + Vector((0, 0, 0.175)), 0.050, 0.010)
    m.objects["flame"].location = low + Vector((0.006, 0, 0.075))
    # the chain from the right fist down to the floor and trailing behind to the padlock
    hand = p["hand_r"]
    drag = 0.030 * math.sin(a) if walking else 0.0
    pts = []
    for i in range(LINKS):
        u = i / (LINKS - 1)
        pts.append(hand + Vector((-0.380 * u * u - drag * u, -0.060 * u, -hand.z * min(1.0, u * 1.6) + 0.020)))
        pts[-1].z = max(pts[-1].z, 0.020)
    m.set_tube("chain", [tuple(q) for q in pts], [0.016] * LINKS)
    for i in range(LINKS // 2):
        q = Vector(pts[2 * i + 1])
        ob = m.objects[f"link{i}"]
        ob.location = q
        ob.rotation_mode = "XYZ"
        ob.rotation_euler = Euler((0.0, 0.6 * (1 if i % 2 else -1), 0.3))
    end = Vector(pts[-1])
    lock = m.objects["lock"]
    lock.location = end + Vector((-0.050, 0, 0.040))
    lock.rotation_mode = "XYZ"
    lock.rotation_euler = Euler((0, 0, 0.2))
    H.frustum(m, "shackle_lock", end + Vector((-0.050, 0, 0.080)), (0.032, 0.032), 0.010, rot=(1.57, 0, 0))


def assign_depth_parts(m, depth_of):
    return None
