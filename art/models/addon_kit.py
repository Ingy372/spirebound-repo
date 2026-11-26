"""Helpers for outfit addon models (<outfit>_a1.py / _a2.py; rules A1-A7 in art/OUTFIT_RULES.md).

An addon model builds and poses the frozen base outfit, then adds its own parts. These helpers give it the
base's moving anchors without changing the base files (approved art is frozen)."""
from __future__ import annotations

from mathutils import Vector


def anchors(m):
    """head, cap (hair cap centre), up (walk bob), shoulders, belt sides and hands of the posed base figure"""
    s = m.spec
    up = m.objects["torso"].location - Vector((0, 0, s["torso_z"]))
    head = m.objects["head"].location.copy()
    out = {"up": up, "head": head, "cap": head + Vector((s["cap"][0], 0, s["cap"][1])), "cap_r": s["cap_r"]}
    for sign, k in ((1, "l"), (-1, "r")):
        out[f"shoulder_{k}"] = Vector((0, s["shoulder_y"] * sign, s["shoulder_z"])) + up
        out[f"belt_{k}"] = Vector((0.0, s["torso_r"][1] * 0.98 * sign, s["belt_z"])) + up
        out[f"hand_{k}"] = m.objects[f"hand_{k}"].location.copy()
    return out


def track(o, at, direction, scale):
    """place a frustum/cylinder part at `at`, its axis along `direction`, with (rx, ry, height) scale"""
    o.location = at
    o.rotation_mode = "QUATERNION"
    o.rotation_quaternion = direction.normalized().to_track_quat("Z", "Y")
    o.scale = scale


def hide(m, name):
    """Tuck a base part away (shrunk into the ground under the body): used by a men's or women's version that must
    lose, say, the base's long hair, without editing the frozen base file."""
    o = m.objects[name]
    o.location = (0.0, 0.0, 0.0)
    o.scale = (0.001, 0.001, 0.001)
