#!/usr/bin/env python3
"""Checks and draws the Floor 1 wilds plan (FLOOR1_WILDS_PLAN.md). It builds nothing and changes nothing in the game.

Run:  python tools/wilds_plan_check.py        -> prints problems (must be 0) and writes docs/FLOOR1_WILDS_PLAN.png

Coordinates are Floor 1 tiles (0..399); the map builder adds 1000 to both. The tables here are the same numbers as in
the plan document: if you change one, change the other.
"""
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

SIZE = 400
ROOT = Path(__file__).resolve().parent.parent

# ---- things that already exist and stay where they are: name -> (x, y, w, h)
FIXED = {
    "Hearthgate": (176, 236, 112, 96), "Millcross": (35, 195, 64, 44), "Fisher's Huts": (132, 188, 24, 48),
    "West cabins": (130, 294, 45, 19), "East cabins": (291, 294, 45, 19), "Arrival Yard": (270, 336, 46, 30),
    "Pass + labyrinth": (205, 8, 52, 84), "Old Watchtower": (25, 25, 55, 55), "Lake": (308, 78, 44, 28),
    "West pond": (83, 121, 26, 18), "Ruined tower": (312, 125, 14, 11), "Ruined farm": (60, 150, 11, 9),
    "Toppled shrine": (300, 372, 10, 8),
}

# ---- hunting grounds: read from maps/floor1_plan.py (the same table the map builder uses), so they can't drift apart.
# id -> (title, x, y, w, h, hub side, size, levels, role, zone, den name or None)
# size "small" = four small loops (18 x 16); "std" = four standard loops (24 x 18); "tall" = four standard loops
# turned on end (18 x 24, hub 6 deep). Hub side = where the entrance is.
import sys as _sys
_sys.path.insert(0, str(ROOT / "maps"))
from floor1_plan import CAMPS  # noqa: E402
GROUNDS = {c["id"]: (c["title"], c["x"], c["y"], c["w"], c["h"], c["gate"], c["size"], c["levels"], c["role"], c["zone"], c["den"])
           for c in CAMPS}

# ---- roads and trails: name -> list of points (straight legs between them); width 3 for roads, 2 for trails
ROADS = {
    "Pass Road": [(232, 235), (232, 92)],
    "South Road": [(232, 332), (232, 368)],
    "Mill Road": [(175, 285), (118, 285)],
    "River Path": [(130, 220), (118, 285)],
    "Millcross Road": [(99, 220), (130, 220)],
    "East Road": [(288, 285), (338, 285)],
    "Shrine Path": [(232, 368), (300, 368)],
}
TRAILS = {
    "Ratwarren gate": [(153, 284), (153, 282)],
    "Toad Pond gate": [(315, 284), (315, 282)],
    "Glade trail": [(231, 335), (209, 335), (209, 337)],
    "Wasp gate": [(230, 211), (228, 211)],
    "Cabin Lane": [(152, 313), (159, 326), (159, 337)],
    "Burrow trail": [(234, 208), (239, 208)],
    "Quarry trail": [(234, 144), (239, 144)],
    "Thornsnap trail": [(230, 152), (218, 152)],
    "Bandit Track": [(338, 285), (338, 240), (354, 224), (354, 220)],
    "Shard Track": [(338, 285), (338, 292), (366, 296), (366, 299)],
    "Copse Road": [(70, 239), (92, 250), (92, 310), (70, 318), (70, 321)],
    "Copse gate": [(92, 282), (88, 282)],
    "Watch Road": [(76, 194), (76, 110), (52, 84), (52, 80)],
}
MOVED = {"Standing stones (east)": (356, 262)}


def river_x(y):
    return 120 + int(round(7 * math.sin(y / 26.0) + 3 * math.sin(y / 9.0)))


def overlap(a, b, gap=0):
    return a[0] < b[0] + b[2] + gap and b[0] < a[0] + a[2] + gap and a[1] < b[1] + b[3] + gap and b[1] < a[1] + a[3] + gap


def legs(path):
    return list(zip(path, path[1:]))


def near_segment(rect, p, q, margin):
    """True if the leg p-q passes within `margin` tiles of the inside of rect (the last 3 tiles of a leg may touch)."""
    x, y, w, h = rect
    steps = max(abs(q[0] - p[0]), abs(q[1] - p[1]), 1)
    for i in range(steps + 1):
        px, py = p[0] + (q[0] - p[0]) * i / steps, p[1] + (q[1] - p[1]) * i / steps
        if x - margin <= px < x + w + margin and y - margin <= py < y + h + margin:
            return True
    return False


def check():
    bad = 0
    rects = {**FIXED, **{g[0]: g[1:5] for g in GROUNDS.values()}}
    names = list(rects)
    for i, a in enumerate(names):
        x, y, w, h = rects[a]
        if x < 4 or y < 4 or x + w > SIZE - 4 or y + h > SIZE - 4:
            print("OUT OF BOUNDS", a); bad += 1
        for b in names[i + 1:]:
            if overlap(rects[a], rects[b], gap=2 if a in FIXED and b in FIXED else 2):
                if not (a in FIXED and b in FIXED):
                    print("TOO CLOSE", a, "/", b); bad += 1
    for gid, (title, x, y, w, h, *_r) in GROUNDS.items():
        for yy in range(y, y + h):
            rx = river_x(yy)
            if x - 2 < rx + 7 and rx - 2 < x + w + 2:
                print("IN THE RIVER", title, "at y", yy); bad += 1
                break
        want = {("small", True): (38, 40), ("small", False): (44, 34), ("std", True): (52, 48), ("std", False): (60, 40), ("tall", True): (39, 57)}[(_r[1], _r[0] in "ns")]
        if (w, h) != want:
            print("WRONG SIZE", title, (w, h), "should be", want); bad += 1
    # roads never run through a ground or a fixed place (their ends may touch an edge)
    for rname, path in {**ROADS, **TRAILS}.items():
        for p, q in legs(path):
            for name, r in rects.items():
                inner = (r[0] + 2, r[1] + 2, r[2] - 4, r[3] - 4)
                if name in ("Hearthgate", "Millcross", "Old Watchtower", "Pass + labyrinth"):
                    inner = (r[0] + 6, r[1] + 6, r[2] - 12, r[3] - 12)
                if inner[2] > 0 and near_segment(inner, p, q, 0):
                    print("ROAD THROUGH", rname, "->", name); bad += 1
    # every ground has a trail or road ending within 3 tiles of the middle of its hub side
    for gid, (title, x, y, w, h, side, *_r) in GROUNDS.items():
        gate = {"n": (x + w // 2, y - 1), "s": (x + w // 2, y + h), "w": (x - 1, y + h // 2), "e": (x + w, y + h // 2)}[side]
        ends = [pt for path in {**ROADS, **TRAILS}.values() for pt in (path[0], path[-1])]
        if not any(abs(e[0] - gate[0]) <= 4 and abs(e[1] - gate[1]) <= 4 for e in ends):
            print("NO TRAIL TO", title, "gate", gate); bad += 1
    print("problems", bad)
    return bad


def draw():
    S = 4
    img = Image.new("RGB", (SIZE * S, SIZE * S), (66, 124, 58))
    d = ImageDraw.Draw(img)
    try:
        f = ImageFont.truetype("arialbd.ttf", 15); fs = ImageFont.truetype("arial.ttf", 12)
    except OSError:
        f = fs = ImageFont.load_default()
    for y in range(3, SIZE - 3):
        rx = river_x(y)
        d.rectangle([(rx - 2) * S, y * S, (rx + 7) * S, y * S + S], fill=(120, 96, 60))
        d.rectangle([rx * S, y * S, (rx + 5) * S, y * S + S], fill=(46, 92, 200))
    for name, path in ROADS.items():
        d.line([(x * S, y * S) for x, y in path], fill=(150, 108, 66), width=3 * S)
    for name, path in TRAILS.items():
        d.line([(x * S, y * S) for x, y in path], fill=(196, 160, 110), width=2 * S)
    for name, (x, y, w, h) in FIXED.items():
        col = (236, 236, 228) if name == "Hearthgate" else (236, 170, 190) if name == "Millcross" else (46, 92, 200) if "ond" in name or name == "Lake" else (128, 128, 134)
        d.rectangle([x * S, y * S, (x + w) * S, (y + h) * S], fill=col, outline=(30, 30, 30))
        d.text((x * S + 4, y * S + 3), name, fill=(0, 0, 0), font=fs)
    for gid, (title, x, y, w, h, side, size, lv, role, zone, den) in GROUNDS.items():
        col = (70, 170, 230) if role == "xp" else (236, 190, 60)
        d.rectangle([x * S, y * S, (x + w) * S, (y + h) * S], fill=(52, 100, 50), outline=col, width=3)
        rw, rh = {"small": (18, 16), "std": (24, 18), "tall": (18, 24)}[size]
        cross = 2 if size == "small" else 3
        hub = 8 if size == "std" else 6
        ox, oy = x, y
        if side == "n":
            oy += hub
        if side == "w":
            ox += hub
        for i in (0, 1):
            for j in (0, 1):
                lx, ly = ox + i * (rw + cross), oy + j * (rh + cross)
                d.rounded_rectangle([(lx + 3) * S, (ly + 3) * S, (lx + rw - 3) * S, (ly + rh - 3) * S], radius=10, outline=(214, 190, 140), width=2 * S)
                d.rounded_rectangle([(lx + 6) * S, (ly + 6) * S, (lx + rw - 6) * S, (ly + rh - 6) * S], radius=6, fill=(30, 70, 34))
        hx, hy, hw, hh = {"n": (x, y, w, hub), "s": (x, y + h - hub, w, hub), "w": (x, y, hub, h), "e": (x + w - hub, y, hub, h)}[side]
        d.rectangle([hx * S, hy * S, (hx + hw) * S, (hy + hh) * S], fill=(196, 160, 110))
        if den:
            d.ellipse([(x + w // 2 - 3) * S, (y + h // 2 - 3) * S, (x + w // 2 + 3) * S, (y + h // 2 + 3) * S], fill=(20, 20, 20), outline=(255, 255, 255))
        ty = y * S - 34 if y > 20 else (y + h) * S + 2
        d.text((x * S, ty), title, fill=(255, 255, 255), font=f, stroke_width=2, stroke_fill=(0, 0, 0))
        d.text((x * S, ty + 17), f"levels {lv[0]}-{lv[1]}, {'experience' if role == 'xp' else 'money'}" + (", cave below" if den else ""), fill=(255, 255, 255), font=fs, stroke_width=2, stroke_fill=(0, 0, 0))
    for name, (x, y) in MOVED.items():
        d.ellipse([(x - 3) * S, (y - 3) * S, (x + 3) * S, (y + 3) * S], outline=(220, 220, 220), width=3)
    d.text((10, 8), "Floor 1 wilds plan   blue = experience ground, gold = money ground, tan strip = entrance hub, rings = hunting loops, black dot = cave below", fill=(255, 255, 255), font=fs, stroke_width=2, stroke_fill=(0, 0, 0))
    out = ROOT / "docs" / "FLOOR1_WILDS_PLAN.png"
    img.save(out)
    print("saved", out)


if __name__ == "__main__":
    check()
    draw()
