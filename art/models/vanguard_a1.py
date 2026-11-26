"""Vanguard addon 1: the Crested Helm (an overlay on the approved Vanguard, which stays frozen).

Jay, 2026-11-25: outfits have a base, addon 1 and addon 2, as content for quests. This file renders the whole
Vanguard WITH the addon; art/pipeline/addon_overlay.py keeps only the pixels the addon changes, which the client
draws over the base when a player owns the addon.
  Addon:   a rounded steel helm with a gold brow band, a nasal bar and a royal-blue horsehair crest front to back.
  Details: gold brow band (a line, O7), nasal bar, two rivets, crest with a dark centre line, cheek guards.
"""
from __future__ import annotations

import math

from mathutils import Vector

import humanoid as H
import vanguard as V
from vanguard import WALK_FRAMES, PALETTE, REFERENCE, PROJECTION, CANVAS_OFFSET, SPEC, assign_depth_parts  # noqa: F401

NAME = "vanguard_a1"
BASE = "vanguard"
# literal values: check_creature.py reads these lines without importing the model
SIGNATURE = ["helm", "crest"]                 # the addon itself must show
HEAD_PARTS = ["skin", "hair", "strand", "eye", "brow", "nose", "helm", "crest", "seam"]   # a helmet IS the head
LEG_PARTS = ["leg_a", "leg_b", "boot_a", "boot_b", "knee"]
CHECK = {"size": (0.85, 1.45), "head": 0.08, "legs_side": 0.05, "eye": 1}
PARTS = V.PARTS + ["helm", "crest", "seam"]
PIXEL_RULES = {**V.PIXEL_RULES,
               "weight": {**V.PIXEL_RULES["weight"], "helm": 1.5, "crest": 2.0, "seam": 3.0},
               "thin": {**V.PIXEL_RULES["thin"], "seam": 2},
               "soft": V.PIXEL_RULES["soft"] + [["helm", "seam"]],
               "texture": {**V.PIXEL_RULES["texture"], "crest": [0.45, 0.2]},
               "selout": V.PIXEL_RULES["selout"] + ["helm", "crest"]}


def build(model_cls, facing):
    m = V.build(model_cls, facing)
    m.parts = PARTS                      # the base parts first, so their numbers do not change
    s = m.spec
    r = s["cap_r"]
    m.ellipsoid("helm", "helm", radii=(r[0] * 1.10, r[1] * 1.08, r[2] * 1.12), segments=20, rings=10)
    m.tube("brow_band", "trim", points=7)
    m.capsule("nasal", "helm")
    for k in ("l", "r"):
        m.ellipsoid(f"cheek_{k}", "helm", radii=(0.040, 0.016, 0.056), segments=10, rings=6)
        m.ellipsoid(f"rivet_{k}", "trim", radii=(0.012, 0.012, 0.012), segments=6, rings=4)
    m.tube("crest", "crest", points=7)
    m.tube("crest_line", "seam", points=7)
    return m


def pose(m, t):
    V.pose(m, t)
    s = m.spec
    head = m.objects["head"].location.copy()
    cap = head + Vector((s["cap"][0], 0, s["cap"][1]))
    r = s["cap_r"]
    m.objects["helm"].location = cap + Vector((0.004, 0, 0.004))
    band = [H.on_ellipsoid(cap, (r[0] * 1.10, r[1] * 1.08, r[2] * 1.12), (math.cos(a), math.sin(a), -0.05), 1.03)
            for a in (-1.6, -1.05, -0.5, 0.0, 0.5, 1.05, 1.6)]
    m.set_tube("brow_band", [tuple(p) for p in band], [0.010] * 7)
    front = H.on_ellipsoid(cap, (r[0] * 1.10, r[1] * 1.08, r[2] * 1.12), (1, 0, -0.1), 1.02)
    m.put_segment("nasal", front, front + Vector((0.012, 0, -0.070)), 0.010)
    for sign, k in ((1, "l"), (-1, "r")):
        m.objects[f"cheek_{k}"].location = head + Vector((0.030, 0.100 * sign, -0.030))
        m.objects[f"rivet_{k}"].location = H.on_ellipsoid(cap, (r[0] * 1.10, r[1] * 1.08, r[2] * 1.12), (0.5, 0.8 * sign, 0.0), 1.04)
    top = cap + Vector((0, 0, r[2] * 1.12))
    pts = [top + Vector((0.080 - 0.034 * i, 0, 0.028 + 0.014 * i - 0.0030 * i * i)) for i in range(7)]
    m.set_tube("crest", [tuple(p) for p in pts], [0.020, 0.034, 0.040, 0.040, 0.036, 0.028, 0.016])
    m.set_tube("crest_line", [tuple(p + Vector((0, 0, 0.036))) for p in pts], [0.004] * 7)
