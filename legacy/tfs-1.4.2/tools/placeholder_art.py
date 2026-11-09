#!/usr/bin/env python3
"""Labeled placeholder sprites for every client thing that has no art yet (18_ART_AND_ASSETS step 2).

Used by build_assets.py as a library (placeholder_for(row)) and runnable on its own to write the
placeholders to assets/generated/placeholder/ for inspection. Placeholders are flat-colored, carry the
thing's id, and are easy to spot in game so nobody mistakes them for final art.

Usage: python3 tools/placeholder_art.py
"""
from __future__ import annotations

import csv
import hashlib
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
S = 32
FONT = ImageFont.load_default()

CAT_COLORS = {
    "item": (176, 146, 72),      # dull gold
    "outfit": (150, 70, 64),     # faded red
    "effect": (220, 200, 90),
    "missile": (230, 230, 230),
}


def _tint(seed: str, base):
    h = hashlib.sha1(seed.encode()).digest()
    return tuple(max(0, min(255, c + (h[i] % 41) - 20)) for i, c in enumerate(base))


def item_icon(tid: int, name: str, w: int = 1, h: int = 1) -> Image.Image:
    im = Image.new("RGBA", (S * w, S * h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    col = _tint(name, CAT_COLORS["item"])
    d.rectangle([2, 2, S * w - 3, S * h - 3], fill=(*col, 255), outline=(40, 34, 30, 255))
    d.text((4, 4), str(tid), fill=(20, 20, 20, 255), font=FONT)
    d.text((4, 17), name[:5], fill=(20, 20, 20, 255), font=FONT)
    return im


def outfit_frame(tid: int, name: str, direction: int, frame: int) -> Image.Image:
    """A readable figure: body, head, and a facing marker. direction 0=N 1=E 2=S 3=W."""
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    col = _tint(name, CAT_COLORS["outfit"])
    bob = (0, 1, 0, -1)[frame % 4]
    d.rectangle([10, 14 + bob, 22, 29], fill=(*col, 255), outline=(30, 24, 22, 255))
    d.ellipse([11, 4 + bob, 21, 14 + bob], fill=(214, 184, 150, 255), outline=(30, 24, 22, 255))
    mark = [(16, 1), (31, 20), (16, 31), (0, 20)][direction]
    d.line([(16, 20), mark], fill=(240, 230, 120, 255), width=2)
    d.text((1, 0), str(tid), fill=(255, 255, 255, 255), font=FONT)
    return im


def effect_frame(tid: int, frame: int, frames: int) -> Image.Image:
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    col = _tint(f"fx{tid}", CAT_COLORS["effect"])
    r = 4 + int(10 * (frame + 1) / frames)
    d.ellipse([16 - r, 16 - r, 16 + r, 16 + r], outline=(*col, 255), width=2)
    return im


def missile_icon(tid: int) -> Image.Image:
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([12, 12, 20, 20], fill=(*_tint(f"m{tid}", CAT_COLORS["missile"]), 255))
    return im


def main():
    out = ROOT / "assets" / "generated" / "placeholder"
    out.mkdir(parents=True, exist_ok=True)
    n = 0
    with open(ROOT / "assets" / "assets.csv", newline="") as f:
        for row in csv.DictReader(f):
            tid, cat = int(row["id"]), row["category"]
            if cat == "item":
                w, h = (int(x) for x in row["size"].split("x"))
                item_icon(tid, row["name"], w, h).save(out / f"item_{tid}.png")
            elif cat == "outfit":
                outfit_frame(tid, row["name"], 2, 0).save(out / f"outfit_{tid}.png")
            elif cat == "effect":
                effect_frame(tid, 0, int(row["frames"])).save(out / f"effect_{tid}.png")
            else:
                missile_icon(tid).save(out / f"missile_{tid}.png")
            n += 1
    print(f"placeholder_art: wrote {n} previews to {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
