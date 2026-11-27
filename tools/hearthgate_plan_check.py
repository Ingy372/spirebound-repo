"""Checks the Hearthgate v4 tile plan (maps/hearthgate_plan.py) and measures the walks from the Hearthstone.

  python tools/hearthgate_plan_check.py          plan only: overlaps, the wall, the plaza, doors; straight-line steps
  python tools/hearthgate_plan_check.py --walk   also builds Floor 1 and counts real steps (no diagonals) on the map

Must print "problems 0". Draws docs/HEARTHGATE_PLAN.png (north is up, one square = one tile).
"""
import collections
import os
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.join(ROOT, "maps"))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import hearthgate_plan as P  # noqa: E402

B = {"THE HEARTH": (P.HEARTH, "hub", None)}
for blk in P.SHOP_BLOCKS:
    B[" + ".join(r[0].split("'")[0] for r in blk["rooms"])] = (blk["rect"], "shop", [r[4] for r in blk["rooms"]])
B["Inn"] = (P.INN["rect"], "shop", [P.INN["door"]])
B["Guardhouse"] = (P.GUARDHOUSE["rect"], "civic", [P.GUARDHOUSE["door"]])
for name, d in (("Ascendancy", P.ASCENDANCY), ("Hunters' Hall", P.HUNTERS_HALL), ("Guild Hall", P.GUILD_HALL)):
    B[name] = (d["rect"], "civic", [d["door"]])
B["Training Yard"] = (P.TRAINING_YARD["rect"], "yard", P.TRAINING_YARD["gaps"])
B["MANOR GROUNDS"] = (P.MANOR_GROUNDS["rect"], "manor", P.MANOR_GROUNDS["gate"])
B["Spire Gardens"] = (P.SPIRE_GARDENS, "green", None)
B["Coach Yard"] = (P.COACH_YARD["rect"], "yard", [P.COACH_YARD["gap"]])
B["Old Well"] = (P.OLD_WELL, "green", None)
B["The Green"] = (P.GREEN, "green", None)
B["Pocket garden"] = (P.POCKET_GARDEN, "green", None)
nh = 0
for street, _rent, lots in P.HOUSES:
    for (x, y, w, h, side, storeys, style) in lots:
        nh += 1
        door = {"s": (x + w // 2, y + h - 1), "n": (x + w // 2, y), "e": (x + w - 1, y + h // 2), "w": (x, y + h // 2)}[side]
        B[f"{street} {nh}"] = ((x, y, w, h), "house", [door])
print("houses", nh)


def ov(a, b):
    return a[0] < b[0] + b[2] and b[0] < a[0] + a[2] and a[1] < b[1] + b[3] and b[1] < a[1] + a[3]


def tiles(r):
    return [(x, y) for x in range(r[0], r[0] + r[2]) for y in range(r[1], r[1] + r[3])]


bad = 0
wall = P.wall_tiles()
names = list(B)
OPEN_KINDS = ("green",)          # gardens may touch streets and the plaza
for i, a in enumerate(names):
    ra, kind, doors = B[a]
    for t in tiles(ra):
        if not P.inside_wall(*t) or t in wall:
            print("OUTSIDE OR ON THE WALL", a, t); bad += 1; break
    for t in tiles(ra):
        if kind not in OPEN_KINDS and P.in_plaza(*t) and a != "THE HEARTH":
            print("IN THE PLAZA", a, t); bad += 1; break
    for b in names[i + 1:]:
        if ov(ra, B[b][0]) and not (a == "MANOR GROUNDS" and b == "Spire Gardens"):
            print("OVERLAP", a, b); bad += 1
    for s, (r, _g) in P.STREETS.items():
        if kind not in OPEN_KINDS and a != "THE HEARTH" and ov(ra, r):
            print("ON STREET", a, s); bad += 1
# doors: two clear tiles in front of every door, on no building
occupied = {t for n, (r, k, _d) in B.items() if k not in OPEN_KINDS for t in tiles(r)}
for a, (r, kind, doors) in B.items():
    for (dx, dy) in doors or []:
        x0, y0, w, h = r
        step = (0, 1) if dy == y0 + h - 1 else (0, -1) if dy == y0 else (1, 0) if dx == x0 + w - 1 else (-1, 0)
        for k in (1, 2):
            t = (dx + step[0] * k, dy + step[1] * k)
            if t in occupied or not P.inside_wall(*t) or t in wall:
                print("DOOR BLOCKED", a, (dx, dy), "at", t); bad += 1
print("problems", bad)

hs = P.HEARTHSTONE
straight = {k: (abs(v[0] - hs[0]) + abs(v[1] - hs[1]) if v else None) for k, v in P.SERVICES.items()}

walked = {}
if "--walk" in sys.argv:
    import mapgen
    import layout_floor1
    import wilds
    from floor1_plan import TOWN
    m = mapgen.Map()
    layout_floor1.build(m)
    m.finish()
    block = wilds.blockers()
    tx, ty = 1000 + TOWN["x"], 1000 + TOWN["y"]
    start = (tx + hs[0], ty + hs[1], 7)
    dist = {start: 0}
    q = collections.deque([start])
    while q:
        p = q.popleft()
        for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (p[0] + a, p[1] + b, 7)
            if n not in dist and tx <= n[0] < tx + P.W and ty <= n[1] < ty + P.H and wilds.walkable(m, n, block):
                dist[n] = dist[p] + 1
                q.append(n)
    for k, v in P.SERVICES.items():
        if v is None:            # the nearest locker: the switch tile in front of it
            sw = [p for p, g in m.ground.items() if g == 10145 and p[2] == 7 and tx <= p[0] < tx + P.W and ty <= p[1] < ty + P.H]
            walked[k] = min((dist[p] for p in sw if p in dist), default=None)
        else:
            walked[k] = dist.get((tx + v[0], ty + v[1], 7))
    for g, ts in P.GATES.items():
        walked[f"{g.upper()} gate"] = min((dist.get((tx + x, ty + y, 7), 10 ** 6) for x, y in ts))

fails = 0
print(f"\nsteps from the Hearthstone {hs} (straight line{', then walked on the real map' if walked else ''}):")
for k in list(P.SERVICES) + [g for g in walked if g.endswith("gate")]:
    s, w = straight.get(k), walked.get(k)
    goal = P.SHOP_GOAL if k in P.SHOPS else P.CROWN_GOAL if k in P.CROWN else None
    n = w if walked else s
    flag = ""
    if goal and (n is None or n > goal):
        flag = f"   OVER THE GOAL OF {goal}"; fails += 1
    print(f"  {k:24s} {'' if s is None else s:>4} {'' if not walked else ('unreachable' if w is None else w):>12}{flag}")
print("goals missed", fails)

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    sys.exit(1 if bad or fails else 0)
S = 10
img = Image.new("RGB", (P.W * S, P.H * S), (72, 132, 62))
d = ImageDraw.Draw(img)
try:
    f = ImageFont.truetype("arialbd.ttf", 12); fs = ImageFont.truetype("arial.ttf", 10)
except OSError:
    f = fs = ImageFont.load_default()
for y in range(P.H):
    for x in range(P.W):
        if P.inside_wall(x, y):
            col = (210, 200, 170) if (x, y) in wall else (232, 224, 196) if P.in_plaza(x, y) else (126, 126, 130)
            d.rectangle([x * S, y * S, x * S + S - 1, y * S + S - 1], fill=col)
for s, (r, g) in P.STREETS.items():
    x, y, w, h = r
    col = (232, 224, 196) if g == 409 else (160, 150, 132) if g == 416 else (170, 170, 176)
    d.rectangle([x * S, y * S, (x + w) * S - 1, (y + h) * S - 1], fill=col)
COL = {"hub": (250, 246, 228), "shop": (200, 120, 80), "civic": (150, 120, 200), "house": (214, 190, 140), "yard": (150, 110, 70),
       "green": (96, 170, 84), "manor": (236, 220, 120)}
for name, (r, kind, doors) in B.items():
    x, y, w, h = r
    d.rectangle([x * S, y * S, (x + w) * S - 1, (y + h) * S - 1], fill=COL[kind], outline=(40, 30, 20), width=2)
    if kind != "house":
        font = f if kind in ("hub", "manor") else fs
        tw = d.textlength(name, font=font)
        d.text((x * S + (w * S - tw) / 2, y * S + h * S / 2 - 6), name, fill=(0, 0, 0), font=font)
    for (dx, dy) in doors or []:
        d.rectangle([dx * S + 2, dy * S + 2, dx * S + S - 3, dy * S + S - 3], fill=(255, 255, 255), outline=(0, 0, 0))
mx, my, mw, mh = P.MANOR_AT + (22, 16)
d.rectangle([mx * S, my * S, (mx + mw) * S - 1, (my + mh) * S - 1], fill=(250, 240, 150), outline=(40, 30, 20), width=2)
d.text((mx * S + 60, my * S + 70), "SPIRE MANOR", fill=(0, 0, 0), font=f)
for street, _rent, lots in P.HOUSES:
    x, y = lots[0][0], lots[0][1]
    d.text((x * S + 2, y * S + 34), street, fill=(60, 30, 0), font=fs)
d.ellipse([hs[0] * S - 4, hs[1] * S - 4, hs[0] * S + S + 4, hs[1] * S + S + 4], fill=(220, 60, 30), outline=(0, 0, 0))
d.text((44 * S, 50 * S + 4), "Hearth Plaza", fill=(60, 50, 30), font=f)
d.text((12, P.H * S - 16), "Hearthgate v4 tile plan   red dot = the Hearthstone   white squares = doors   1 square = 1 tile x10",
       fill=(255, 255, 255), font=fs)
img.save(os.path.join(ROOT, "docs", "HEARTHGATE_PLAN.png"))
print("saved docs/HEARTHGATE_PLAN.png")
sys.exit(1 if bad or fails else 0)
