#!/usr/bin/env python3
"""Generate procedural ground, wall and simple nature tiles from the style palette (18_ART_AND_ASSETS).

Output goes to assets/generated/ (git-ignored, rebuilt on demand). Deterministic: same seed, same pixels.
Hand-made or Grok art placed at the same relative path under assets/png/ always wins (see build_assets.py).

Usage: python3 tools/procedural_tiles.py
"""
from __future__ import annotations

import random
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "generated"
S = 32

# Style lock palette: warm stone, moss green, dull gold, faded red, dark iron, river blue.
PAL = {
    "moss": [(78, 104, 52), (92, 120, 60), (104, 132, 66), (66, 90, 46)],
    "dirt": [(120, 92, 62), (132, 102, 70), (108, 82, 56), (142, 112, 78)],
    "stone": [(150, 140, 124), (136, 126, 112), (164, 154, 136), (122, 112, 100)],
    "river": [(52, 92, 132), (60, 104, 146), (46, 82, 120), (70, 116, 156)],
    "wood": [(126, 88, 54), (112, 78, 48), (138, 98, 60), (100, 70, 44)],
    "marble": [(198, 190, 176), (186, 178, 164), (210, 202, 188), (176, 168, 156)],
    "iron": [(52, 52, 58), (64, 62, 68), (44, 44, 50)],
    "gold": [(176, 146, 72)],
}


def noise_tile(colors, seed, speckle=0.18, accent=None):
    rnd = random.Random(seed)
    im = Image.new("RGBA", (S, S))
    px = im.load()
    base = colors[0]
    for y in range(S):
        for x in range(S):
            c = base if rnd.random() > speckle else rnd.choice(colors[1:])
            px[x, y] = (*c, 255)
    if accent:
        for _ in range(accent[1]):
            x, y = rnd.randrange(S), rnd.randrange(S)
            px[x, y] = (*accent[0], 255)
    return im


def cobble(seed, colors):
    rnd = random.Random(seed)
    im = noise_tile(colors, seed, 0.1)
    d = ImageDraw.Draw(im)
    dark = tuple(max(0, c - 40) for c in colors[0])
    for row in range(4):
        y = row * 8
        off = (row % 2) * 6 + rnd.randrange(3)
        d.line([(0, y), (S, y)], fill=(*dark, 255))
        for x in range(off, S, 12):
            d.line([(x, y), (x, y + 7)], fill=(*dark, 255))
    return im


def planks(seed, colors):
    im = noise_tile(colors, seed, 0.12)
    d = ImageDraw.Draw(im)
    dark = tuple(max(0, c - 36) for c in colors[0])
    for y in range(0, S, 8):
        d.line([(0, y), (S, y)], fill=(*dark, 255))
    return im


def water(seed, colors):
    rnd = random.Random(seed)
    im = noise_tile(colors, seed, 0.08)
    d = ImageDraw.Draw(im)
    hl = (110, 150, 186, 255)
    for _ in range(3):
        x, y = rnd.randrange(2, 24), rnd.randrange(2, 30)
        d.line([(x, y), (x + rnd.randrange(4, 8), y)], fill=hl)
    return im


def wall(kind):
    """Wall placeholder: a dark-iron framed warm-stone block. h/v/c/p are drawn so orientation is readable."""
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    stone, edge = PAL["stone"][1], PAL["iron"][0]
    if kind == "h":
        d.rectangle([0, 10, 31, 31], fill=(*stone, 255), outline=(*edge, 255))
    elif kind == "v":
        d.rectangle([10, 0, 31, 31], fill=(*stone, 255), outline=(*edge, 255))
    elif kind == "c":
        d.rectangle([0, 10, 31, 31], fill=(*stone, 255), outline=(*edge, 255))
        d.rectangle([10, 0, 31, 31], fill=(*stone, 255), outline=(*edge, 255))
    else:
        d.rectangle([12, 4, 27, 31], fill=(*stone, 255), outline=(*edge, 255))
    return im


def fence():
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    w = (*PAL["wood"][3], 255)
    for x in (4, 16, 28):
        d.rectangle([x - 1, 12, x + 1, 30], fill=w)
    d.rectangle([0, 16, 31, 18], fill=w)
    d.rectangle([0, 24, 31, 26], fill=w)
    return im


def tree():
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle([14, 20, 18, 31], fill=(*PAL["wood"][3], 255))
    d.ellipse([3, 1, 29, 25], fill=(*PAL["moss"][3], 255), outline=(30, 44, 24, 255))
    d.ellipse([8, 5, 20, 15], fill=(*PAL["moss"][2], 255))
    return im


def bush():
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([5, 12, 27, 30], fill=(*PAL["moss"][1], 255), outline=(30, 44, 24, 255))
    return im


def rock():
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.polygon([(6, 28), (4, 18), (12, 8), (24, 9), (29, 20), (26, 29)], fill=(*PAL["stone"][3], 255),
              outline=(*PAL["iron"][0], 255))
    return im


def main():
    (OUT / "ground").mkdir(parents=True, exist_ok=True)
    (OUT / "wall").mkdir(parents=True, exist_ok=True)
    (OUT / "nature").mkdir(parents=True, exist_ok=True)
    n = 0
    for v in range(6):
        noise_tile(PAL["moss"], 1000 + v, accent=((176, 146, 72), 2)).save(OUT / f"ground/grass_{v}.png"); n += 1
        noise_tile(PAL["dirt"], 2000 + v).save(OUT / f"ground/dirt_{v}.png"); n += 1
        cobble(3000 + v, PAL["stone"]).save(OUT / f"ground/cobble_{v}.png"); n += 1
        water(4000 + v, PAL["river"]).save(OUT / f"ground/water_{v}.png"); n += 1
        planks(5000 + v, PAL["wood"]).save(OUT / f"ground/planks_{v}.png"); n += 1
        noise_tile(PAL["marble"], 6000 + v, 0.06).save(OUT / f"ground/marble_{v}.png"); n += 1
    Image.new("RGBA", (S, S), (0, 0, 0, 255)).save(OUT / "ground/void.png"); n += 1
    for k in "hvcp":
        wall(k).save(OUT / f"wall/stone_{k}.png"); n += 1
    fence().save(OUT / "wall/fence.png"); n += 1
    tree().save(OUT / "nature/tree.png"); bush().save(OUT / "nature/bush.png"); rock().save(OUT / "nature/rock.png"); n += 3
    print(f"procedural_tiles: wrote {n} PNGs to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
