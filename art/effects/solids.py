"""The solid (3D) parts of the spell effects, one function per effect: f(fx, t, i, n).

fx = the builder from render_fx.py (cone, box, ball, mesh). t runs 0..1 over the effect, i is the frame, n the
number of frames. The tile centre is (0, 0, 0); +x east, +y north, +z up; 1 unit = 1 tile.
Colours come from fx2d's palettes (copied here because Blender's Python has no Pillow).
"""
from __future__ import annotations

import math
import random

GOLD = [(255, 250, 214), (255, 222, 120), (242, 176, 52), (196, 112, 28), (120, 60, 18)]
CRIMSON = [(255, 214, 200), (246, 120, 96), (212, 48, 44), (140, 22, 34), (78, 12, 28)]
STEEL = [(250, 252, 255), (206, 216, 230), (150, 164, 186), (96, 108, 134), (54, 62, 84)]
EMBER = [(255, 246, 196), (255, 204, 92), (250, 136, 36), (206, 66, 20), (120, 30, 16)]
FROST = [(240, 254, 255), (176, 240, 250), (98, 204, 232), (48, 140, 196), (28, 78, 140)]
LEAF = [(236, 255, 206), (176, 236, 110), (104, 196, 64), (48, 136, 52), (24, 80, 44)]
STONE = [(214, 204, 188), (168, 154, 136), (120, 106, 92), (80, 68, 60), (48, 40, 38)]
WOOD = [(150, 104, 62), (104, 68, 40), (66, 42, 28)]


LOOPS = ("war_banner",)        # effects that repeat seamlessly; must match paints.LOOPS


def frame_time(name, i, n):
    """t for frame i: loops run 0..1 evenly; one-shot effects start a little in, so the first frame shows something"""
    return i / n if name in LOOPS else (i + 0.7) / n


def ease_out(t):
    t = max(0.0, min(1.0, t))
    return 1.0 - (1.0 - t) ** 2


def rise_hold_fall(t, up=0.3, down=0.72):
    """0 -> 1 quickly, hold, then back to 0"""
    if t < up:
        return ease_out(t / up)
    if t < down:
        return 1.0
    return max(0.0, 1.0 - (t - down) / (1.0 - down))


# --------------------------------------------------------------------------------------------- Vanguard
def skyrend(fx, t, i, n):
    """a tall golden sword falls point-first onto the tile and stands there through the flash"""
    if t > 0.86:
        return
    fall = min(1.0, t / 0.36)
    z = 1.9 * (1.0 - fall * fall)             # height of the point above the ground
    if t >= 0.36:
        z = -0.16                             # driven into the ground
    s = 1.08
    fx.cone((0, 0, z + 0.24 * s), -0.24 * s, 0.085 * s, GOLD[0], sides=4, emit=1.2, rot=math.pi / 4)   # point
    fx.box((0, 0, z + (0.24 + 0.40) * s), (0.17 * s, 0.05 * s, 0.80 * s), GOLD[1], emit=0.8)          # blade
    fx.box((0, -0.01, z + (0.24 + 0.40) * s), (0.05 * s, 0.06 * s, 0.80 * s), GOLD[0], emit=1.5)      # bright fuller
    fx.box((0, 0, z + 1.08 * s), (0.50 * s, 0.09 * s, 0.09 * s), CRIMSON[2], emit=0.35)               # guard
    fx.ball((-0.25 * s, 0, z + 1.08 * s), 0.06 * s, GOLD[2], emit=0.6)
    fx.ball((0.25 * s, 0, z + 1.08 * s), 0.06 * s, GOLD[2], emit=0.6)
    fx.box((0, 0, z + 1.22 * s), (0.075 * s, 0.075 * s, 0.22 * s), CRIMSON[3], emit=0.15)             # grip
    fx.ball((0, 0, z + 1.37 * s), 0.08 * s, GOLD[1], emit=0.8)                                        # pommel


def ground_crack(fx, t, i, n):
    """slabs of rock punch up out of the ground and sink back"""
    rnd = random.Random(7)
    k = rise_hold_fall(t, 0.28, 0.62)
    shards = [(0.0, 0.02, 0.62, 0.20), (-0.26, 0.12, 0.44, 0.15), (0.24, -0.10, 0.48, 0.16),
              (0.10, 0.26, 0.36, 0.13), (-0.14, -0.24, 0.34, 0.13), (0.30, 0.20, 0.26, 0.10), (-0.34, -0.08, 0.24, 0.10)]
    for j, (x, y, h, r) in enumerate(shards):
        kk = max(0.0, min(1.0, k * 1.25 - j * 0.04))
        if kk <= 0.02:
            continue
        lean = (x * 0.55 + rnd.uniform(-0.05, 0.05), y * 0.55 + rnd.uniform(-0.05, 0.05))
        col = (STONE[0], STONE[1], (156, 128, 100))[j % 3]
        fx.cone((x, y, -0.02), h * kk, r, col, sides=5, lean=(lean[0] * kk, lean[1] * kk), top=r * 0.18,
                rot=rnd.uniform(0, 6.28))
    # loose chips thrown up at the start
    if 0.1 < t < 0.75:
        p = (t - 0.1) / 0.65
        for j in range(6):
            a = rnd.uniform(0, 6.28)
            d = 0.25 + 0.45 * p
            z = 0.9 * p * (1.0 - p) * 2.2 + 0.03
            fx.box((math.cos(a) * d, math.sin(a) * d, z), (0.08, 0.08, 0.08), STONE[j % 2], yaw=a)


def war_banner(fx, t, i, n):
    """a crimson banner on a pole, its cloth moving in the wind (loops)"""
    fx.cone((0, 0, 0), 1.58, 0.04, WOOD[1], sides=6, top=0.03)                 # pole
    fx.ball((0, 0, 1.63), 0.07, GOLD[1], emit=0.7)                            # finial
    fx.box((0, 0, 1.46), (0.60, 0.05, 0.05), WOOD[0])                         # crossbar
    cols, rows = 6, 7
    w, h = 0.52, 0.86
    ph = 2 * math.pi * t
    verts = []
    for r in range(rows + 1):
        for c in range(cols + 1):
            u, v = c / cols, r / rows
            sway = math.sin(ph + v * 3.2 + u * 1.3) * 0.07 * v
            flap = math.sin(ph * 2 + u * 5.0) * 0.025 * v
            x = (u - 0.5) * w + sway
            y = -0.05 - flap - 0.02 * v
            z = 1.43 - v * h
            if r == rows:                     # swallow-tail cut at the bottom
                z += 0.16 * (1.0 - abs(u - 0.5) * 2.0)
            verts.append((x, y, z))
    faces_main, faces_trim = [], []
    for r in range(rows):
        for c in range(cols):
            a = r * (cols + 1) + c
            quad = (a, a + 1, a + cols + 2, a + cols + 1)
            (faces_trim if (c in (0, cols - 1) or r == rows - 1) else faces_main).append(quad)
    fx.mesh(verts, faces_main, CRIMSON[2], emit=0.25)
    fx.mesh(verts, faces_trim, GOLD[2], emit=0.45)
    # emblem: a small golden diamond that moves with the cloth
    sway = math.sin(ph + 0.4 * 3.2 + 0.5 * 1.3) * 0.07 * 0.4
    fx.cone((sway, -0.09, 1.08), 0.02, 0.12, GOLD[1], sides=4, top=0.11, emit=0.9)


# --------------------------------------------------------------------------------------------- Arcanist
def meteor(fx, t, i, n):
    """a burning rock comes down, then its pieces fly"""
    rnd = random.Random(11)
    if t < 0.44:
        p = t / 0.44
        z = 1.75 * (1.0 - p) + 0.12
        fx.ball((0, 0, z), 0.21, (96, 44, 30), emit=0.25, rings=5)
        fx.ball((0.02, -0.03, z - 0.03), 0.17, EMBER[2], emit=1.6, rings=5)
        for j in range(4):
            a = rnd.uniform(0, 6.28)
            fx.box((math.cos(a) * 0.17, math.sin(a) * 0.17, z + rnd.uniform(-0.08, 0.1)), (0.1, 0.1, 0.1), (70, 36, 28), yaw=a)
    elif t < 0.95:
        p = (t - 0.44) / 0.51
        for j in range(8):
            a = j * 0.785 + rnd.uniform(-0.3, 0.3)
            d = 0.12 + (0.5 + rnd.uniform(0, 0.25)) * p
            z = 0.04 + (0.7 + rnd.uniform(0, 0.5)) * p * (1.0 - p) * 2.0
            s = 0.11 * (1.0 - p * 0.6)
            fx.box((math.cos(a) * d, math.sin(a) * d, z), (s, s, s), (84, 40, 28) if j % 2 else EMBER[3],
                   yaw=a + p * 3, emit=0.0 if j % 2 else 0.9)


# --------------------------------------------------------------------------------------------- Mystic
def thorn_burst(fx, t, i, n):
    """thick hooked thorns shoot out of the ground and pull back"""
    rnd = random.Random(5)
    k = rise_hold_fall(t, 0.26, 0.66)
    thorns = [(0.0, 0.0, 0.78, 0.0), (0.24, 0.10, 0.56, 0.5), (-0.22, 0.16, 0.60, 2.4), (0.12, -0.24, 0.50, 5.2),
              (-0.20, -0.18, 0.46, 3.9), (0.34, -0.12, 0.34, 5.9), (-0.36, 0.0, 0.36, 3.1), (0.04, 0.32, 0.38, 1.5)]
    for j, (x, y, h, a) in enumerate(thorns):
        kk = max(0.0, min(1.0, k * 1.3 - j * 0.05))
        if kk <= 0.03:
            continue
        h *= kk
        out = (math.cos(a) * 0.16 * kk if j else 0.03, math.sin(a) * 0.16 * kk if j else 0.02)
        r = 0.085 if j else 0.11
        dark, mid, tip = LEAF[4], LEAF[3], LEAF[1]
        # stem in two pieces so it bends outward, then a pale sharp tip
        fx.cone((x, y, -0.02), h * 0.5, r, dark, sides=5, lean=(out[0] * 0.3, out[1] * 0.3), top=r * 0.62, rot=a)
        fx.cone((x + out[0] * 0.3, y + out[1] * 0.3, h * 0.5 - 0.02), h * 0.3, r * 0.62, mid, sides=5,
                lean=(out[0] * 0.45, out[1] * 0.45), top=r * 0.3, rot=a)
        fx.cone((x + out[0] * 0.75, y + out[1] * 0.75, h * 0.8 - 0.02), h * 0.24, r * 0.3, tip, sides=5,
                lean=(out[0] * 0.5, out[1] * 0.5), emit=0.35, rot=a)
        # side barbs
        for b in range(2):
            ba = a + (1.6 if b else -1.6) + rnd.uniform(-0.3, 0.3)
            bz = h * (0.3 + 0.25 * b)
            fx.cone((x + out[0] * 0.25, y + out[1] * 0.25, bz), 0.07 * kk, 0.03, tip, sides=4,
                    lean=(math.cos(ba) * 0.11 * kk, math.sin(ba) * 0.11 * kk), emit=0.2)


def ice_spires(fx, t, i, n):
    """a cluster of ice crystals erupts, glints, and breaks apart"""
    rnd = random.Random(3)
    k = rise_hold_fall(t, 0.22, 0.66)
    crystals = [(0.0, 0.02, 0.86, 0.13), (0.24, 0.06, 0.58, 0.10), (-0.22, 0.10, 0.62, 0.10), (0.10, -0.22, 0.46, 0.09),
                (-0.16, -0.20, 0.42, 0.09), (0.36, -0.14, 0.30, 0.07), (-0.38, -0.04, 0.32, 0.07)]
    if t < 0.70:
        for j, (x, y, h, r) in enumerate(crystals):
            kk = max(0.0, min(1.0, k * 1.3 - j * 0.05))
            if kk <= 0.03:
                continue
            h *= kk
            lean = (x * 0.5 * kk, y * 0.5 * kk)
            rot = rnd.uniform(0, 1.0)
            body = FROST[2] if j % 2 == 0 else FROST[3]
            fx.cone((x, y, -0.02), h * 0.72, r, body, sides=6, lean=(lean[0] * 0.72, lean[1] * 0.72), top=r * 0.8,
                    emit=0.22, rot=rot)
            fx.cone((x + lean[0] * 0.72, y + lean[1] * 0.72, h * 0.72 - 0.02), h * 0.28, r * 0.8, FROST[1], sides=6,
                    lean=(lean[0] * 0.28, lean[1] * 0.28), emit=0.5, rot=rot)
    else:
        p = (t - 0.70) / 0.30
        for j in range(10):
            a = rnd.uniform(0, 6.28)
            d = rnd.uniform(0.05, 0.3) + 0.4 * p
            z = rnd.uniform(0.1, 0.7) * (1.0 - p) + 0.02
            s = 0.1 * (1.0 - 0.5 * p)
            fx.cone((math.cos(a) * d, math.sin(a) * d, z), s * 1.6, s * 0.6, FROST[1 + j % 3], sides=4,
                    lean=(math.cos(a) * 0.05, math.sin(a) * 0.05), emit=0.4, rot=a)
