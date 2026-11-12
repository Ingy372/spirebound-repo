"""Draws docs/FLOOR1_PLAN.png: the Floor 1 design plan (schematic colours, no base-game art), labelled with every
hunting ground, its level range and its role. Run: python tools/plan_image.py"""
import os
import sys
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "maps"))
from floor1_plan import APEX, CAMPS, MILLCROSS, TOWN  # noqa: E402

root = os.path.join(os.path.dirname(__file__), "..")
S = 4                                                       # pixels per tile
base = Image.open(os.path.join(root, "docs", "previews", "floor1_z7.png")).convert("RGB")
img = base.resize((400 * S, 400 * S), Image.NEAREST)
d = ImageDraw.Draw(img, "RGBA")
try:
    f = ImageFont.truetype("arialbd.ttf", 22)
    fs = ImageFont.truetype("arial.ttf", 17)
except OSError:
    f = fs = ImageFont.load_default()


def box(x, y, w, h, col, title, sub=""):
    d.rectangle([x * S, y * S, (x + w) * S, (y + h) * S], outline=col + (255,), width=4, fill=col + (45,))
    d.text((x * S + 8, y * S + 6), title, fill=(255, 255, 255, 255), font=f, stroke_width=3, stroke_fill=(0, 0, 0, 255))
    if sub:
        d.text((x * S + 8, y * S + 32), sub, fill=(255, 255, 255, 255), font=fs, stroke_width=2, stroke_fill=(0, 0, 0, 255))


for c in CAMPS:
    col = (255, 200, 40) if c["role"] == "money" else (80, 200, 255)
    box(c["x"], c["y"], c["w"], c["h"], col, c["title"], "levels %d-%d, %s" % (c["levels"][0], c["levels"][1], c["role"]))
box(TOWN["x"], TOWN["y"], TOWN["w"], TOWN["h"], (255, 255, 255), "HEARTHGATE", "walled city, 30 homes inside")
box(MILLCROSS["x"], MILLCROSS["y"], MILLCROSS["w"], MILLCROSS["h"], (255, 160, 200), "Millcross", "village, 8 cottages")
d.text((20, 20), "Floor 1 - Hearthgate Plains   (blue = experience, gold = money; north is up)", fill=(255, 255, 255, 255), font=f, stroke_width=3, stroke_fill=(0, 0, 0, 255))
d.text((20, 52), "Grey blocks: the Old Watchtower (top left), the Pass (centre top) and the labyrinth to Floor 2 (top). Brown squares = homes.", fill=(255, 255, 255, 255), font=fs, stroke_width=2, stroke_fill=(0, 0, 0, 255))
out = os.path.join(root, "docs", "FLOOR1_PLAN.png")
img.save(out)
print("wrote", out)
