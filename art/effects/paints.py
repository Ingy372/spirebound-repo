"""The painted (2D) part of every spell effect, and the list of effects.

Each painter is f(back, front, t, i, n): `back` is drawn under the solid 3D part (if the effect has one), `front`
over it. t runs 0..1 across the effect, i is the frame number, n the number of frames.
EFFECTS lists every effect: its id in the game (SpireFx in lib/spirebound/spells.lua), frames, milliseconds per
frame, and whether it has a solid part in solids.py.

House style (keep to it for new effects):
  - banded shapes (Canvas.orb / flame / band / bolt), not soft fog: three or four hard steps of one palette;
  - one palette per vocation, plus white-hot cores; nothing pastel;
  - big and readable at 1x: the main shape is at least a third of the tile;
  - tall things rise up-left along fx2d.UP; ground marks are true circles;
  - a clear beginning (anticipation), a peak, and a quick fade.
"""
from __future__ import annotations

import math

from fx2d import (CRIMSON, DAY, EMBER, FROST, GOLD, LEAF, ROSE, STEEL, STONE, TILE, VIOLET, bump, ease_in,
                  ease_out, jitter, up)

CX, CY = TILE
WHITE = (255, 255, 255)
DIRT = [(150, 116, 78), (116, 84, 54), (86, 60, 40), (58, 40, 30), (38, 28, 24)]


LOOPS = ("war_banner",)        # effects that repeat seamlessly; must match solids.LOOPS


def frame_time(name, i, n):
    """t for frame i: loops run 0..1 evenly; one-shot effects start a little in, so the first frame shows something"""
    return i / n if name in LOOPS else (i + 0.7) / n


def fade(t, a=0.15, b=0.75):
    """1 in the middle, rising before a and falling after b"""
    if t < a:
        return t / a
    if t > b:
        return max(0.0, (1.0 - t) / (1.0 - b))
    return 1.0


# ------------------------------------------------------------------------------------------------ Vanguard
def steel_arc(back, front, t, i, n):
    """a crescent of steel sweeping round, crimson on its trailing edge"""
    k = min(1.0, (1.0 - t) * 2.2)
    head = 210.0 - 300.0 * ease_out(t)
    tail = 170.0 * (1.0 - 0.4 * t)
    r = 11.5 + 2.0 * t
    front.band(CX, CY, r - 2.2, 4.5, CRIMSON, 0.9 * k, a0=head + 12, a1=head + tail)
    front.band(CX, CY, r, 5.6, STEEL, k, a0=head, a1=head + tail * 0.82)
    front._ring_paint(CX, CY, r + 1.2, 1.6, WHITE, k, 1.0, head, head + tail * 0.4)
    hx, hy = CX + r * math.cos(math.radians(head)), CY - r * math.sin(math.radians(head))
    front.sparkle(hx, hy, 6.0 * k + 1.0, WHITE, k)
    rnd = jitter(3)
    for j in range(4):
        a = math.radians(head + tail * rnd.uniform(0.2, 1.0))
        d = r + rnd.uniform(2.0, 5.0)
        front.dot(CX + d * math.cos(a), CY - d * math.sin(a), 0.9, CRIMSON[1], k)


def skyrend(back, front, t, i, n):
    """light behind the falling sword, then the blow: a white-gold flash and a crimson shock ring"""
    if t < 0.36:
        p = t / 0.36
        h = 61.0 * (1.0 - p * p) + 8.0
        x0, y0 = up(CX, CY, h + 44.0)
        x1, y1 = up(CX, CY, h + 90.0)
        back.flame(x0, y0, x1, y1, 12.0, GOLD, 0.9, taper=0.85)
        back.band(CX, CY, 12.0 - 6.0 * p, 1.4, GOLD, 0.8 * p)
    else:
        p = (t - 0.36) / 0.64
        k = min(1.0, (1.0 - p) * 1.8)
        r = 5.0 + 15.0 * ease_out(p)
        back.orb(CX, CY, 9.0 + 9.0 * ease_out(p), [GOLD[0], GOLD[1], GOLD[2], CRIMSON[2]], 0.85 * k)
        back.band(CX, CY, r, 2.6, CRIMSON, k)
        x1, y1 = up(CX, CY, 62.0)
        back.flame(CX, CY, x1, y1, 20.0 * k + 3.0, [GOLD[1], GOLD[1], GOLD[2], CRIMSON[2]], 0.75 * k, taper=0.35)
        front.orb(CX, CY, 6.0 * k + 1.5, GOLD, k)
        if p < 0.2:
            front.disc(CX, CY, 8.0, WHITE, 0.95, paint=True)
        rnd = jitter(21)
        for _ in range(9):
            a = rnd.uniform(0, 6.28)
            d = 6.0 + 15.0 * ease_out(p) * rnd.uniform(0.6, 1.0)
            x, y = up(CX + math.cos(a) * d, CY + math.sin(a) * d * 0.8, 9.0 * math.sin(p * 3.14))
            front.dot(x, y, 1.3, GOLD[0] if rnd.rand() < 0.5 else CRIMSON[1], k, paint=True)


def oath_halo(back, front, t, i, n):
    """a golden ring turning around a character, with motes of light rising"""
    k = fade(t, 0.12, 0.72)
    x, y = up(CX, CY + 3.0, 15.0)
    R = 15.5
    back.disc(CX - 1.0, CY + 2.0, 12.0, GOLD[3], 0.34 * k, sy=0.6, paint=True)                              # light on the ground
    back.band(x, y, R, 2.2, [GOLD[2], GOLD[3], GOLD[3], GOLD[4]], 0.9 * k, sy=0.42, a0=0, a1=180)          # far side
    front.band(x, y, R, 3.6, GOLD, k, sy=0.42, a0=180, a1=360)
    for j in range(4):
        a = math.radians(360.0 * t + j * 90.0)
        px, py = x + R * math.cos(a), y - R * 0.42 * math.sin(a)
        if math.sin(a) > 0:
            back.dot(px, py, 1.6, GOLD[1], k, paint=True)
        else:
            front.orb(px, py, 3.6, GOLD, k)
            front.sparkle(px, py, 5.0, WHITE, k)
    rnd = jitter(4)
    for j in range(9):
        ph = (t + rnd.rand()) % 1.0
        bx = x + rnd.uniform(-14, 14)
        mx, my = up(bx, y + 12.0, 38.0 * ph)
        front.dot(mx, my, 1.2, GOLD[0] if j % 2 else GOLD[1], k * (1.0 - ph * 0.7), paint=True)


def ground_crack(back, front, t, i, n):
    """cracks in the ground and dust around the rising rock"""
    k = fade(t, 0.06, 0.62)
    rnd = jitter(9)
    for j in range(7):
        a = j * 0.9 + rnd.uniform(-0.2, 0.2)
        L = (10.0 + rnd.uniform(0, 6.0)) * min(1.0, t * 5.0)
        mx, my = CX + math.cos(a) * L * 0.5 + rnd.uniform(-1.5, 1.5), CY + math.sin(a) * L * 0.5 + rnd.uniform(-1.5, 1.5)
        ex, ey = CX + math.cos(a) * L, CY + math.sin(a) * L
        back.line(CX, CY, mx, my, 2.2, DIRT[4], 0.9 * k, paint=True)
        back.line(mx, my, ex, ey, 1.6, DIRT[4], 0.9 * k, taper=0.8, paint=True)
    p = min(1.0, t / 0.75)
    for j in range(9):
        a = rnd.uniform(0, 6.28)
        d = 6.0 + 14.0 * ease_out(p)
        x, y = up(CX + math.cos(a) * d, CY + math.sin(a) * d, 6.0 * p)
        front.orb(x, y, 3.2 + 2.6 * p, [STONE[0], STONE[0], STONE[1], STONE[2]], 0.7 * (1.0 - p))


def war_banner(back, front, t, i, n):
    """a warm ring on the ground around the banner's foot"""
    pulse = 0.8 + 0.2 * math.sin(2 * math.pi * t)
    back.band(CX, CY, 13.0, 1.8, [GOLD[0], GOLD[1], GOLD[2], CRIMSON[3]], 0.9 * pulse)
    for j in range(6):
        a = math.radians(j * 60.0 + 360.0 * t / 6.0)
        back.dot(CX + 13.0 * math.cos(a), CY - 13.0 * math.sin(a), 1.6, CRIMSON[1], pulse, paint=True)


# ------------------------------------------------------------------------------------------------ Ranger
def light_needles(back, front, t, i, n):
    """needles of daylight fall onto the tile; each lands with a flash"""
    rnd = jitter(17)
    for j in range(6):
        gx, gy = CX + rnd.uniform(-11, 11), CY + rnd.uniform(-10, 11)
        start = j * 0.10
        p = (t - start) / 0.36
        if p < 0:
            continue
        if p < 1.0:
            h = 64.0 * (1.0 - p)
            x0, y0 = up(gx, gy, h)
            x1, y1 = up(gx, gy, h + 30.0)
            front.flame(x0, y0, x1, y1, 6.0, DAY, 1.0, taper=0.9)
        else:
            q = min(1.0, (p - 1.0) / 1.0)
            kk = min(1.0, (1.0 - q) * 1.6)
            back.band(gx, gy, 2.0 + 6.0 * ease_out(q), 1.3, DAY, kk)
            front.orb(gx, gy, 4.6 * (1.0 - 0.5 * q), DAY, kk)
            front.sparkle(gx, gy, 6.0 * (1.0 - q) + 0.5, WHITE, kk)


def _sigil(back, front, t, pal, motif):
    """a magic circle on the ground: appears, turns, fades"""
    k = fade(t, 0.2, 0.78)
    rot = 90.0 * t
    r = 15.0 - 5.0 * ease_out(min(1.0, t * 1.4)) if motif == "ember" else 13.0   # the ember one closes in
    back.disc(CX, CY, r, pal[4], 0.42 * k, paint=True)
    back.band(CX, CY, r, 2.0, pal, k)
    back.band(CX, CY, r * 0.6, 1.2, pal, 0.9 * k)
    if motif == "sun":
        for j in range(8):
            a = math.radians(rot + j * 45.0)
            back.line(CX + math.cos(a) * r * 0.66, CY - math.sin(a) * r * 0.66, CX + math.cos(a) * r * 0.95,
                      CY - math.sin(a) * r * 0.95, 1.6, pal[1], k, paint=True)
        back.star(CX, CY, r * 0.56, r * 0.2, 4, pal[2], k, rot=rot * 2)
        back.star(CX, CY, r * 0.36, r * 0.12, 4, pal[0], k, rot=rot * 2)
    elif motif == "ember":
        for j in range(4):
            a = math.radians(rot * 2 + j * 90.0)
            back.line(CX + math.cos(a) * (r - 4.0), CY - math.sin(a) * (r - 4.0), CX + math.cos(a) * (r + 4.0),
                      CY - math.sin(a) * (r + 4.0), 2.0, pal[0], k, paint=True)
        back.star(CX, CY, r * 0.56, r * 0.26, 3, pal[2], k, rot=-rot * 3 + 90)
        back.orb(CX, CY, 2.5 + 3.0 * t, pal, k * (0.5 + 0.5 * t))
    else:  # frost
        for j in range(6):
            a = math.radians(rot + j * 60.0)
            ex, ey = CX + math.cos(a) * r * 0.92, CY - math.sin(a) * r * 0.92
            back.line(CX, CY, ex, ey, 1.5, pal[1], k, paint=True)
            for s in (-1, 1):
                b = a + s * 0.75
                mx, my = CX + math.cos(a) * r * 0.55, CY - math.sin(a) * r * 0.55
                back.line(mx, my, mx + math.cos(b) * 3.8, my - math.sin(b) * 3.8, 1.2, pal[0], k, paint=True)
        back.orb(CX, CY, 3.2, pal, k)


def sun_sigil(back, front, t, i, n):
    _sigil(back, front, t, DAY, "sun")


def ember_sigil(back, front, t, i, n):
    _sigil(back, front, t, EMBER, "ember")


def frost_sigil(back, front, t, i, n):
    _sigil(back, front, t, FROST, "frost")


# ------------------------------------------------------------------------------------------------ Arcanist
def _bolt_path(rnd, x0, y0, x1, y1, steps, wobble):
    pts = [(x0, y0)]
    nx, ny = -(y1 - y0), (x1 - x0)
    L = math.hypot(nx, ny) or 1.0
    for s in range(1, steps):
        f = s / steps
        off = rnd.uniform(-wobble, wobble) * (1.0 - abs(f - 0.5))
        pts.append((x0 + (x1 - x0) * f + nx / L * off, y0 + (y1 - y0) * f + ny / L * off))
    pts.append((x1, y1))
    return pts


def violet_bolt(back, front, t, i, n):
    """lightning strikes the tile from above: two flickers, then the glow dies"""
    stage = min(2, i * 3 // n)                      # 0: first strike, 1: second strike, 2: afterglow
    rnd = jitter(31 + stage)
    sx, sy = up(CX + rnd.uniform(-6, 6), CY, 66.0)
    k = [1.0, 0.85, 0.0][stage]
    glow = [1.0, 0.85, 0.5][stage] * (1.0 - 0.3 * (i % 2))
    back.orb(CX, CY, 15.0 * glow + 2.0, [VIOLET[1], VIOLET[2], VIOLET[3], VIOLET[4]], 0.8 * glow)
    back.band(CX, CY, 5.0 + 11.0 * t, 1.6, VIOLET, min(1.0, (1.0 - t) * 1.5))
    if k > 0:
        pts = _bolt_path(rnd, sx, sy, CX, CY, 7, 10.0)
        w = 2.4 if i % 2 == 0 else 1.7
        front.bolt(pts, w, VIOLET, k)
        mid = pts[3]
        bx, by = mid[0] + rnd.uniform(7, 14), mid[1] + rnd.uniform(5, 13)
        front.bolt(_bolt_path(rnd, mid[0], mid[1], bx, by, 3, 4.0), 1.2, VIOLET, k)
        mid = pts[5]
        bx, by = mid[0] - rnd.uniform(6, 11), mid[1] + rnd.uniform(3, 9)
        front.bolt(_bolt_path(rnd, mid[0], mid[1], bx, by, 3, 3.0), 1.0, VIOLET, k)
    front.orb(CX, CY, 7.0 * glow + 1.0, VIOLET, glow)
    for _ in range(6):
        a = rnd.uniform(0, 6.28)
        d = rnd.uniform(6, 15)
        x, y = CX + math.cos(a) * d, CY + math.sin(a) * d * 0.8
        front.bolt(_bolt_path(rnd, CX, CY, x, y, 3, 3.5), 0.9, VIOLET, 0.9 * glow)


def meteor(back, front, t, i, n):
    """the meteor's tail of fire, then the blast"""
    if t < 0.44:
        p = t / 0.44
        h = 56.0 * (1.0 - p) + 4.0
        x0, y0 = up(CX, CY, h)
        x1, y1 = up(CX, CY, h + 40.0)
        back.flame(x0, y0, x1, y1, 17.0, EMBER, 1.0, taper=0.85)
        back.orb(x0, y0, 10.0, [EMBER[1], EMBER[2], EMBER[3], EMBER[4]], 0.9)
        back.band(CX, CY, 13.0 - 6.0 * p, 1.5, EMBER, 0.9 * p)                # where it will land
    else:
        p = (t - 0.44) / 0.56
        k = min(1.0, (1.0 - p) * 1.7)
        back.orb(CX, CY, 12.0 + 10.0 * ease_out(p), [EMBER[1], EMBER[2], EMBER[3], EMBER[4]], 0.9 * k)
        back.band(CX, CY, 5.0 + 17.0 * ease_out(p), 3.0, EMBER, k)
        rnd = jitter(13)
        for j in range(8):                                                    # flames leaping up from the crater
            bx = CX + rnd.uniform(-11, 11)
            by = CY + rnd.uniform(-7, 8)
            hh = (14.0 + rnd.uniform(0, 14.0)) * bump(p, 0.25)
            x1, y1 = up(bx, by, hh)
            front.flame(bx, by, x1, y1, 7.5, EMBER, k, taper=0.9)
        front.orb(CX, CY, 12.0 * (1.0 - 0.6 * p), EMBER, k)
        if p < 0.25:
            front.disc(CX, CY, 9.0, WHITE, 0.9, paint=True)


def ember_pillar(back, front, t, i, n):
    """a column of flame roaring up out of the tile"""
    k = fade(t, 0.08, 0.7)
    grow = ease_out(min(1.0, t / 0.3))
    height = 40.0 * grow * (1.0 if t < 0.65 else 1.0 - 0.6 * (t - 0.65) / 0.35)
    rnd = jitter(40 + i)
    back.orb(CX, CY, 14.0, [EMBER[2], EMBER[3], EMBER[4], EMBER[4]], 0.8 * k, sy=0.85)
    back.band(CX, CY, 10.0 + 3.0 * t, 1.5, EMBER, 0.9 * k)
    outer = [EMBER[2], EMBER[2], EMBER[3], EMBER[4]]
    for j in range(3):                                                        # the body: wide at the foot, swaying
        bx = CX + (j - 1) * 4.0 + rnd.uniform(-1.5, 1.5)
        x1, y1 = up(bx + rnd.uniform(-4, 4), CY + 1.0, height * rnd.uniform(0.75, 0.95))
        front.line(bx, CY + 1.0, x1, y1, 17.0, EMBER[4], 0.75 * k, taper=0.8, paint=True)
        front.line(bx, CY + 1.0, x1, y1, 14.0, EMBER[3], k, taper=0.8, paint=True)
    for j in range(7):                                                        # tongues licking out of it
        f = rnd.uniform(0.15, 0.8)
        bx, by = up(CX + rnd.uniform(-6, 6), CY + 1.0, height * f * 0.8)
        side = rnd.choice([-1.0, 1.0])
        x1, y1 = up(bx + side * rnd.uniform(3, 8), by, rnd.uniform(8, 15) * grow)
        front.flame(bx, by, x1, y1, 6.5, outer, k, taper=0.95)
    for j in range(2):                                                        # the bright heart
        bx = CX + (j - 0.5) * 3.0
        x1, y1 = up(bx + rnd.uniform(-3, 3), CY + 2.0, height * rnd.uniform(0.55, 0.7))
        front.line(bx, CY + 2.0, x1, y1, 11.0, EMBER[2], k, taper=0.85, paint=True)
        front.line(bx, CY + 2.0, x1, y1, 7.0, EMBER[1], k, taper=0.9, paint=True)
    x1, y1 = up(CX + rnd.uniform(-2, 2), CY + 2.0, height * 0.36)
    front.line(CX, CY + 2.5, x1, y1, 4.0, EMBER[0], k, taper=0.9, paint=True)
    tx, ty = up(CX, CY, height * 0.8)
    x1, y1 = up(CX + rnd.uniform(-3, 3), CY, height * 1.12)
    front.flame(tx, ty, x1, y1, 7.0, EMBER, k, taper=0.95)                    # the tip
    for j in range(8):                                                        # sparks above
        ph = (t * 1.5 + rnd.rand()) % 1.0
        x, y = up(CX + rnd.uniform(-11, 11), CY, height * 0.5 + 30.0 * ph)
        front.dot(x, y, 1.2, EMBER[1], k * (1.0 - ph), paint=True)


def void_pull(back, front, t, i, n):
    """violet arms spiralling inward to a point"""
    k = fade(t, 0.1, 0.8)
    shrink = 1.0 - 0.5 * ease_in(t)
    x, y = up(CX, CY, 6.0)
    back.disc(x, y, 17.0 * shrink, VIOLET[4], 0.6 * k, paint=True)
    back.band(x, y, 17.0 * shrink, 1.4, [VIOLET[1], VIOLET[2], VIOLET[3], VIOLET[4]], 0.9 * k)
    for arm in range(3):
        base = arm * 120.0 + 420.0 * t
        prev = None
        for s in range(14):
            f = s / 13.0
            a = math.radians(base + f * 230.0)
            r = (2.0 + 15.0 * f) * shrink
            px, py = x + r * math.cos(a), y - r * math.sin(a) * 0.9
            if prev:
                front.line(prev[0], prev[1], px, py, 4.4 * (1.0 - 0.6 * f), VIOLET[3], 0.85 * k, paint=True)
                front.line(prev[0], prev[1], px, py, 2.6 * (1.0 - 0.6 * f), VIOLET[1], k, paint=True)
                if f < 0.55:
                    front.line(prev[0], prev[1], px, py, 1.1, VIOLET[0], k, paint=True)
            prev = (px, py)
    front.orb(x, y, 4.0 + 3.0 * t, VIOLET, k)
    front.sparkle(x, y, 6.0 * t + 1.0, WHITE, k * t)


# ------------------------------------------------------------------------------------------------ Mystic
def thorn_burst(back, front, t, i, n):
    """torn earth under the thorns and green sparks at their height"""
    k = fade(t, 0.08, 0.68)
    back.disc(CX, CY, 13.0, DIRT[3], 0.6 * k, paint=True)
    back.band(CX, CY, 9.0 + 4.0 * ease_out(min(1.0, t * 2.5)), 2.0, DIRT, 0.9 * k)
    rnd = jitter(8)
    for j in range(8):
        a = rnd.uniform(0, 6.28)
        d = 5.0 + 12.0 * ease_out(min(1.0, t * 2.0))
        x, y = up(CX + math.cos(a) * d, CY + math.sin(a) * d, 10.0 * bump(min(1.0, t * 1.6), 0.4))
        back.dot(x, y, 1.4, DIRT[1 + j % 2], k, paint=True)
    g = bump(t, 0.35)
    for j in range(5):
        x, y = up(CX + rnd.uniform(-10, 10), CY + rnd.uniform(-6, 6), 14.0 + rnd.uniform(0, 14.0))
        front.sparkle(x, y, 3.4 * g + 0.3, LEAF[0], g)


def leaf_ward(back, front, t, i, n):
    """a leaf-green bubble around a character, with leaves circling it"""
    k = fade(t, 0.18, 0.7)
    x, y = up(CX, CY + 3.0, 13.0)
    back.disc(x, y, 15.0, LEAF[3], 0.34 * k, sy=1.15, paint=True)
    front.band(x, y, 15.0, 1.8, LEAF, 0.95 * k, sy=1.15)
    front._ring_paint(x, y, 11.5, 2.4, LEAF[0], 0.95 * k, 1.15, 105, 165)                 # highlight
    front.dot(x - 6.5, y - 9.5, 1.6, WHITE, k, paint=True)
    for j in range(5):
        a = math.radians(360.0 * t + j * 72.0)
        px, py = x + 17.5 * math.cos(a), y + 2.0 - 7.0 * math.sin(a) + (j - 2) * 3.0
        layer = back if math.sin(a) > 0 else front
        tilt = a + 1.2
        dx, dy = math.cos(tilt) * 4.2, math.sin(tilt) * 4.2
        nx, ny = -dy * 0.45, dx * 0.45
        layer.poly([(px - dx, py - dy), (px + nx, py + ny), (px + dx, py + dy), (px - nx, py - ny)],
                   LEAF[1] if math.sin(a) <= 0 else LEAF[3], k)
        layer.line(px - dx, py - dy, px + dx, py + dy, 0.8, LEAF[4], 0.9 * k, paint=True)


def ice_spires(back, front, t, i, n):
    """frost spreading on the ground, glints on the crystals, a cold burst as they break"""
    k = fade(t, 0.06, 0.78)
    back.disc(CX, CY, 14.0, FROST[4], 0.5 * k, paint=True)
    back.band(CX, CY, 6.0 + 9.0 * ease_out(min(1.0, t * 2.2)), 1.8, FROST, 0.9 * k)
    rnd = jitter(6)
    g = bump(t, 0.4)
    for j in range(4):
        x, y = up(CX + rnd.uniform(-9, 9), CY + rnd.uniform(-5, 5), 12.0 + rnd.uniform(0, 16.0))
        if (i + j) % 2 == 0:
            front.sparkle(x, y, 5.0 * g + 0.3, WHITE, g)
    if t > 0.66:
        p = (t - 0.66) / 0.34
        for j in range(7):
            a = rnd.uniform(0, 6.28)
            d = 4.0 + 13.0 * p
            x, y = up(CX + math.cos(a) * d, CY + math.sin(a) * d, 8.0)
            front.orb(x, y, 3.6, [WHITE, FROST[0], FROST[1], FROST[2]], 0.8 * (1.0 - p))


def bloom(back, front, t, i, n):
    """a flower of light opens on the tile and lets its sparks go"""
    k = fade(t, 0.1, 0.72)
    open_ = ease_out(min(1.0, t / 0.42))
    x, y = up(CX, CY, 5.0)
    back.disc(x, y, 6.0 + 9.0 * open_, LEAF[4], 0.45 * k, paint=True)
    back.band(x, y, 5.0 + 10.0 * open_, 1.4, LEAF, 0.9 * k)
    rings = ((6, 14.5, [LEAF[0], LEAF[1], LEAF[2], LEAF[3]], 0.0), (6, 10.0, [WHITE, ROSE[1], ROSE[2], (190, 70, 120)], 30.0),
             (5, 5.8, [WHITE, ROSE[0], ROSE[1], ROSE[2]], 12.0))
    for ringn, (count, length, pal, rot0) in enumerate(rings):
        L = length * open_
        for j in range(count):
            a = math.radians(rot0 + j * 360.0 / count + 40.0 * t)
            side = 0.46 - 0.05 * ringn
            for scale, col in ((1.0, pal[3]), (0.86, pal[1]), (0.5, pal[0])):
                LL = L * scale
                tip = (x + math.cos(a) * LL, y - math.sin(a) * LL * 0.88)
                p1 = (x + math.cos(a - side) * LL * 0.58, y - math.sin(a - side) * LL * 0.58 * 0.88)
                p2 = (x + math.cos(a + side) * LL * 0.58, y - math.sin(a + side) * LL * 0.58 * 0.88)
                front.poly([(x, y), p1, tip, p2], col, k)
    front.orb(x, y, 3.4, GOLD, k)
    rnd = jitter(12)
    for j in range(9):
        ph = (t * 1.2 + rnd.rand()) % 1.0
        mx, my = up(x + rnd.uniform(-14, 14), y + rnd.uniform(-4, 6), 32.0 * ph)
        front.dot(mx, my, 1.2, LEAF[0] if j % 2 else ROSE[0], k * (1.0 - 0.6 * ph), paint=True)


# ------------------------------------------------------------------------------------------------ everyone
def clash(back, front, t, i, n):
    """two elements meeting: a white star that bursts into three colours"""
    k = min(1.0, (1.0 - t) * 2.0)
    x, y = up(CX, CY, 10.0)
    r = 6.0 + 16.0 * ease_out(t)
    back.band(x, y, 3.0 + 15.0 * ease_out(t), 2.0, VIOLET, 0.9 * k)
    front.star(x, y, r, r * 0.2, 4, GOLD[2], k, rot=45.0 + 50.0 * t)
    front.star(x, y, r * 0.92, r * 0.2, 4, FROST[2], k, rot=0.0 - 30.0 * t)
    front.star(x, y, r * 0.66, r * 0.22, 8, VIOLET[1], k, rot=22.0)
    front.star(x, y, r * 0.5, r * 0.14, 4, WHITE, k, rot=45.0 * t)
    front.star(x, y, r * 0.5, r * 0.14, 4, WHITE, k, rot=45.0 + 45.0 * t)
    front.disc(x, y, 3.4 * k + 1.0, WHITE, k, paint=True)
    rnd = jitter(2)
    for j in range(9):
        a = rnd.uniform(0, 6.28)
        d = r * rnd.uniform(0.75, 1.25)
        front.dot(x + math.cos(a) * d, y + math.sin(a) * d, 1.2, [GOLD[1], FROST[1], VIOLET[1]][j % 3], k, paint=True)


#        name            id  frames  ms   solid part?
EFFECTS = [
    ("steel_arc", 401, 6, 60, False),
    ("skyrend", 402, 9, 65, True),
    ("oath_halo", 403, 8, 90, False),
    ("ground_crack", 404, 8, 70, True),
    ("war_banner", 405, 8, 125, True),
    ("light_needles", 406, 9, 60, False),
    ("sun_sigil", 407, 10, 110, False),
    ("violet_bolt", 408, 6, 60, False),
    ("meteor", 409, 10, 65, True),
    ("ember_pillar", 410, 8, 75, False),
    ("thorn_burst", 411, 8, 80, True),
    ("leaf_ward", 412, 8, 95, False),
    ("ice_spires", 413, 9, 75, True),
    ("bloom", 414, 9, 85, False),
    ("clash", 415, 6, 60, False),
    ("void_pull", 416, 8, 70, False),
    ("ember_sigil", 417, 10, 110, False),
    ("frost_sigil", 418, 10, 100, False),
]
PAINTERS = {name: globals()[name] for name, *_ in EFFECTS}
