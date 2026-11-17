"""2D painting for spell effects: glows, bolts, rings, arcs and shapes on a 64x64 canvas (drawn at 4x, shrunk later).

Coordinates are in final pixels (0..64, y down). The spell's own tile is the bottom-right 32x32 quarter, so the
tile centre is TILE = (48, 48); anything tall rises toward the top-left, like every tall thing in the game.
Colours are (r, g, b) 0..255. Everything is light: layers add up and brighten, they never darken.
"""
from __future__ import annotations

import math

import numpy as np
from PIL import Image, ImageDraw

SS = 4                      # supersampling
SIZE = 64
TILE = (48.0, 48.0)         # centre of the spell's own tile
UP = (-0.38, -0.925)        # the on-screen direction of "up into the air" (a little to the left, as in Tibia)

# One palette per vocation (docs/design/spells.md 3.3), light to dark
GOLD = [(255, 250, 214), (255, 222, 120), (242, 176, 52), (196, 112, 28), (120, 60, 18)]
CRIMSON = [(255, 214, 200), (246, 120, 96), (212, 48, 44), (140, 22, 34), (78, 12, 28)]
STEEL = [(250, 252, 255), (206, 216, 230), (150, 164, 186), (96, 108, 134), (54, 62, 84)]
EMBER = [(255, 246, 196), (255, 204, 92), (250, 136, 36), (206, 66, 20), (120, 30, 16)]
VIOLET = [(246, 232, 255), (214, 170, 255), (164, 104, 246), (104, 56, 196), (56, 28, 120)]
FROST = [(240, 254, 255), (176, 240, 250), (98, 204, 232), (48, 140, 196), (28, 78, 140)]
LEAF = [(236, 255, 206), (176, 236, 110), (104, 196, 64), (48, 136, 52), (24, 80, 44)]
DAY = [(255, 255, 240), (255, 244, 176), (255, 220, 104), (232, 176, 56), (170, 112, 30)]
ROSE = [(255, 240, 246), (255, 190, 214), (244, 128, 172)]
STONE = [(214, 204, 188), (168, 154, 136), (120, 106, 92), (80, 68, 60), (48, 40, 38)]


def up(x, y, h):
    """the point h pixels 'above' (x, y)"""
    return x + UP[0] * h, y + UP[1] * h


class Canvas:
    def __init__(self):
        n = SIZE * SS
        self.rgb = np.zeros((n, n, 3), np.float32)      # premultiplied
        self.a = np.zeros((n, n), np.float32)
        ys, xs = np.mgrid[0:n, 0:n].astype(np.float32)
        self.x = (xs + 0.5) / SS
        self.y = (ys + 0.5) / SS

    # ---- compositing
    def add(self, mask, color, strength=1.0):
        """light: brightens what is there"""
        m = np.clip(mask * strength, 0.0, 1.0)
        c = np.asarray(color, np.float32) / 255.0
        self.rgb += m[..., None] * c
        self.a = 1.0 - (1.0 - self.a) * (1.0 - m)

    def over(self, mask, color, strength=1.0):
        """paint: covers what is there (for solid shapes)"""
        m = np.clip(mask * strength, 0.0, 1.0)
        c = np.asarray(color, np.float32) / 255.0
        self.rgb = self.rgb * (1.0 - m[..., None]) + m[..., None] * c
        self.a = self.a * (1.0 - m) + m

    def under(self, other: "Canvas"):
        """put this canvas on top of `other`; returns the result"""
        out = Canvas.__new__(Canvas)
        out.x, out.y = self.x, self.y
        out.rgb = self.rgb + other.rgb * (1.0 - self.a[..., None])
        out.a = self.a + other.a * (1.0 - self.a)
        return out

    # ---- distance helpers
    def _dist(self, x, y):
        return np.hypot(self.x - x, self.y - y)

    def _seg(self, x0, y0, x1, y1):
        dx, dy = x1 - x0, y1 - y0
        L2 = dx * dx + dy * dy or 1e-6
        t = np.clip(((self.x - x0) * dx + (self.y - y0) * dy) / L2, 0.0, 1.0)
        return np.hypot(self.x - (x0 + t * dx), self.y - (y0 + t * dy)), t

    # ---- primitives (all "add" unless paint=True)
    def glow(self, x, y, r, color, strength=1.0, power=2.0, sy=1.0):
        d = np.hypot(self.x - x, (self.y - y) / sy) / max(r, 1e-3)
        self.add(np.clip(1.0 - d, 0.0, 1.0) ** power, color, strength)

    def dot(self, x, y, r, color, strength=1.0, paint=False):
        m = np.clip((r - self._dist(x, y)) * SS * 0.5 + 0.5, 0.0, 1.0)
        (self.over if paint else self.add)(m, color, strength)

    def line(self, x0, y0, x1, y1, width, color, strength=1.0, taper=0.0, paint=False):
        """taper 0..1: the line thins toward its end (1 = to a point)"""
        d, t = self._seg(x0, y0, x1, y1)
        w = width * 0.5 * (1.0 - taper * t)
        m = np.clip((w - d) * SS * 0.5 + 0.5, 0.0, 1.0)
        (self.over if paint else self.add)(m, color, strength)

    def beam(self, x0, y0, x1, y1, width, color, strength=1.0, power=2.0, taper=0.0):
        """a soft-edged line (glow around a segment)"""
        d, t = self._seg(x0, y0, x1, y1)
        w = width * 0.5 * (1.0 - taper * t)
        self.add(np.clip(1.0 - d / np.maximum(w, 1e-3), 0.0, 1.0) ** power, color, strength)

    def ring(self, x, y, r, width, color, strength=1.0, sy=1.0, a0=None, a1=None, soft=False):
        """a circle outline; sy squashes it (ground rings seen from the game camera are full circles: sy=1).
        a0..a1 (degrees, 0 = east, counter-clockwise) keep only an arc."""
        d = np.hypot(self.x - x, (self.y - y) / sy)
        e = np.abs(d - r)
        if soft:
            m = np.clip(1.0 - e / max(width, 1e-3), 0.0, 1.0) ** 1.6
        else:
            m = np.clip((width * 0.5 - e) * SS * 0.5 + 0.5, 0.0, 1.0)
        if a0 is not None:
            ang = np.degrees(np.arctan2(-(self.y - y) / sy, self.x - x)) % 360.0
            span = (a1 - a0) % 360.0 or 360.0
            rel = (ang - a0) % 360.0
            edge = np.clip(np.minimum(rel, span - rel) / 8.0 + 0.5, 0.0, 1.0)
            m = m * np.where(rel <= span, edge, 0.0)
        self.add(m, color, strength)

    def disc(self, x, y, r, color, strength=1.0, sy=1.0, paint=False):
        d = np.hypot(self.x - x, (self.y - y) / sy)
        m = np.clip((r - d) * SS * 0.5 + 0.5, 0.0, 1.0)
        (self.over if paint else self.add)(m, color, strength)

    def poly(self, points, color, strength=1.0, paint=True):
        n = SIZE * SS
        img = Image.new("L", (n, n), 0)
        ImageDraw.Draw(img).polygon([(px * SS, py * SS) for px, py in points], fill=255)
        m = np.asarray(img, np.float32) / 255.0
        (self.over if paint else self.add)(m, color, strength)

    def star(self, x, y, r_out, r_in, points, color, strength=1.0, rot=0.0, paint=False):
        pts = []
        for i in range(points * 2):
            r = r_out if i % 2 == 0 else r_in
            a = math.radians(rot + i * 180.0 / points)
            pts.append((x + r * math.cos(a), y - r * math.sin(a)))
        self.poly(pts, color, strength, paint=paint)

    # ---- banded shapes: hard-edged steps of one palette (light to dark), which is what reads as pixel art.
    #      pal = one of the palettes above; k = how strong (0..1).
    def orb(self, x, y, r, pal, k=1.0, sy=1.0):
        """a ball of light: dark halo outside, brightest in the middle"""
        self.disc(x, y, r, pal[3], 0.5 * k, sy=sy, paint=True)
        self.disc(x, y, r * 0.74, pal[2], 0.9 * k, sy=sy, paint=True)
        self.disc(x, y, r * 0.5, pal[1], k, sy=sy, paint=True)
        self.disc(x, y, r * 0.26, pal[0], k, sy=sy, paint=True)

    def flame(self, x0, y0, x1, y1, width, pal, k=1.0, taper=0.9):
        """a tongue of flame / streak of light from (x0, y0) thinning toward (x1, y1)"""
        self.line(x0, y0, x1, y1, width, pal[3], 0.75 * k, taper=taper, paint=True)
        self.line(x0, y0, x0 + (x1 - x0) * 0.86, y0 + (y1 - y0) * 0.86, width * 0.66, pal[2], 0.95 * k, taper=taper, paint=True)
        self.line(x0, y0, x0 + (x1 - x0) * 0.68, y0 + (y1 - y0) * 0.68, width * 0.38, pal[1], k, taper=taper, paint=True)
        self.line(x0, y0, x0 + (x1 - x0) * 0.42, y0 + (y1 - y0) * 0.42, width * 0.16, pal[0], k, taper=taper, paint=True)

    def band(self, x, y, r, width, pal, k=1.0, sy=1.0, a0=None, a1=None):
        """a ring with a dark edge, a coloured body and a light middle"""
        self._ring_paint(x, y, r, width + 2.2, pal[3], 0.8 * k, sy, a0, a1)
        self._ring_paint(x, y, r, width, pal[1], k, sy, a0, a1)
        self._ring_paint(x, y, r, width * 0.4, pal[0], k, sy, a0, a1)

    def _ring_paint(self, x, y, r, width, color, strength, sy, a0, a1):
        d = np.hypot(self.x - x, (self.y - y) / sy)
        m = np.clip((width * 0.5 - np.abs(d - r)) * SS * 0.5 + 0.5, 0.0, 1.0)
        if a0 is not None:
            ang = np.degrees(np.arctan2(-(self.y - y) / sy, self.x - x)) % 360.0
            span = (a1 - a0) % 360.0 or 360.0
            rel = (ang - a0) % 360.0
            m = m * np.where(rel <= span, np.clip(np.minimum(rel, span - rel) / 6.0 + 0.5, 0.0, 1.0), 0.0)
        self.over(m, color, strength)

    def bolt(self, pts, width, pal, k=1.0):
        """a jagged lightning path: white-hot core inside two steps of colour"""
        for w, c, a in ((width * 3.4, pal[3], 0.6), (width * 2.2, pal[2], 0.95), (width, pal[0], 1.0)):
            for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
                self.line(x0, y0, x1, y1, w, c, a * k, paint=True)

    def sparkle(self, x, y, r, color, strength=1.0):
        """a four-pointed glint"""
        self.beam(x - r, y, x + r, y, 1.4, color, strength, power=1.2)
        self.beam(x, y - r, x, y + r, 1.4, color, strength, power=1.2)
        self.glow(x, y, r * 0.6, color, strength)

    def layer(self, rgba):
        """put a rendered picture (H, W, 4 floats 0..1, straight alpha, at 4x) over this canvas"""
        a = rgba[..., 3]
        self.rgb = self.rgb * (1.0 - a[..., None]) + rgba[..., :3] * a[..., None]
        self.a = self.a * (1.0 - a) + a


def ease_out(t):
    return 1.0 - (1.0 - t) ** 2


def ease_in(t):
    return t * t


def bump(t, peak=0.3):
    """0 at t=0, 1 at t=peak, back to 0 at t=1"""
    if t <= peak:
        return t / peak
    return max(0.0, 1.0 - (t - peak) / (1.0 - peak))


def jitter(seed):
    """a small repeatable random generator for an effect (so re-renders are identical)"""
    return np.random.RandomState(seed)
