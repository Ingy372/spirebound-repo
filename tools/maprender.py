#!/usr/bin/env python3
"""Draws a region of the generated map with the REAL item sprites, the way the client shows it (top-down, 32 px tiles).

A mapper's eyes: lets the map be designed and checked visually without starting the server and client.
Needs the client files in .local/client (CipSoft art, Jay's PC only). Output goes to .local/scratch/ and is never committed.

Usage:  python tools/maprender.py out.png x y w h [z] [scale] [top]   (x y = world coordinates of the top-left tile;
        top = highest level to draw too, e.g. 4, to see upper storeys and roofs from outside)
        python tools/maprender.py out.png town                     (Hearthgate, shortcut)
"""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "maps"))

import spriteview as sv  # noqa: E402


def load_patterns():
    """id -> dict(sprites, pw, ph, pd, layers) from the appearances file (first frame group)."""
    from spriteview import fields, packed, THINGS
    path = next(THINGS.glob("appearances-*.dat"))
    out = {}
    for num, wt, v in fields(path.read_bytes()):
        if num != 1:
            continue
        iid, info = None, None
        for n2, w2, v2 in fields(v):
            if n2 == 1:
                iid = v2
            elif n2 == 2 and w2 == 2 and info is None:
                for n3, w3, v3 in fields(v2):
                    if n3 == 3 and w3 == 2:
                        info = {"sprites": [], "pw": 1, "ph": 1, "pd": 1, "layers": 1}
                        for n4, w4, v4 in fields(v3):
                            if n4 == 1:
                                info["pw"] = v4
                            elif n4 == 2:
                                info["ph"] = v4
                            elif n4 == 3:
                                info["pd"] = v4
                            elif n4 == 4:
                                info["layers"] = v4
                            elif n4 == 5:
                                info["sprites"] += packed(v4) if w4 == 2 else [v4]
        if iid is not None and info:
            out[iid] = info
    return out


class Renderer:
    def __init__(self):
        self.pat = load_patterns()
        self.spr = sv.Sprites()
        self.cache = {}

    def sprite(self, iid, x, y, z):
        info = self.pat.get(iid)
        if not info or not info["sprites"]:
            return None
        idx = ((((z % info["pd"]) * info["ph"] + (y % info["ph"])) * info["pw"] + (x % info["pw"])) * info["layers"])
        if idx >= len(info["sprites"]):
            idx = 0
        sid = info["sprites"][idx]
        img = self.cache.get(sid)
        if img is None:
            img = self.cache[sid] = self.spr.get(sid)
        return img

    def render(self, m, x0, y0, w, h, z, out, scale=1.0, top=None):
        """Draws level z and, if top < z, every level above it up to top, each one shifted one tile up-left per level
        the way the client draws them (that is how roofs and upper storeys line up with the walls below).
        top=None draws z alone: the view from inside a building."""
        top = z if top is None else top
        canvas = Image.new("RGBA", (w * 32 + 64, h * 32 + 64), (0, 0, 0, 255))
        for zf in range(z, top - 1, -1):
            off = (z - zf) * 32
            span = z - zf
            for ty in range(y0, y0 + h + span):
                for tx in range(x0, x0 + w + span):
                    gid = m.ground.get((tx, ty, zf))
                    if gid is None:
                        continue
                    g = self.sprite(gid, tx, ty, zf)
                    if g is not None:
                        self._safe_paste(canvas, g, (tx - x0) * 32 - off + 32 - g.width, (ty - y0) * 32 - off + 32 - g.height)
            # items in a second pass, top to bottom so tall things overlap what is behind them
            for ty in range(y0, y0 + h + span):
                for tx in range(x0, x0 + w + span):
                    px, py = (tx - x0) * 32 - off, (ty - y0) * 32 - off
                    for iid, _attrs in m.items.get((tx, ty, zf), []):
                        s = self.sprite(iid, tx, ty, zf)
                        if s is not None:
                            self._safe_paste(canvas, s, px + 32 - s.width, py + 32 - s.height)
        canvas = canvas.crop((0, 0, w * 32, h * 32))
        if scale != 1.0:
            canvas = canvas.resize((int(canvas.width * scale), int(canvas.height * scale)), Image.LANCZOS)
        Path(out).parent.mkdir(parents=True, exist_ok=True)
        canvas.convert("RGB").save(out)
        print(f"wrote {out} ({canvas.width}x{canvas.height})")

    @staticmethod
    def _safe_paste(canvas, s, x, y):
        # tall sprites near the top/left edge: clip instead of failing
        cx, cy = max(0, -x), max(0, -y)
        if cx >= s.width or cy >= s.height:
            return
        if cx or cy:
            s = s.crop((cx, cy, s.width, s.height))
            x, y = x + cx, y + cy
        canvas.alpha_composite(s, (x, y))


def build_map():
    import mapgen
    import layout_floor1
    m = mapgen.Map()
    layout_floor1.build(m)
    m.finish()
    return m


if __name__ == "__main__":
    out = sys.argv[1]
    m = build_map()
    r = Renderer()
    if sys.argv[2] == "town":
        import layout_floor1 as L
        from floor1_plan import TOWN
        r.render(m, L.X0 + TOWN["x"] - 6, L.Y0 + TOWN["y"] - 6, TOWN["w"] + 12, TOWN["h"] + 12, L.Z, out, scale=0.5)
    else:
        x, y, w, h = (int(a) for a in sys.argv[2:6])
        z = int(sys.argv[6]) if len(sys.argv) > 6 else 7
        scale = float(sys.argv[7]) if len(sys.argv) > 7 else 1.0
        top = int(sys.argv[8]) if len(sys.argv) > 8 else None   # e.g. 4: also draw the upper storeys and roofs
        r.render(m, x, y, w, h, z, out, scale, top)
