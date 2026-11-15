#!/usr/bin/env python3
"""Pull REFERENCE sprites out of the Tibia client files on this PC, for side-by-side comparison only.

  python tools/art_refs.py

Writes .local/artref/rat_client.png (outfit 21: rows N/E/S/W, columns stand + 8 walk, 64x64 cells) and
.local/artref/ground.png (a grass tile). .local/ is git-ignored: these are CipSoft files and are NEVER committed,
shipped or traced. They only sit beside our own sprites in art/output/<name>/compare/.
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image

from spriteview import THINGS, Sprites, fields, load_items, packed

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / ".local" / "artref"


def outfit_groups(outfit_id):
    path = next(THINGS.glob("appearances-*.dat"))
    for num, _wt, v in fields(path.read_bytes()):
        if num != 2:
            continue
        oid, groups = None, []
        for n2, _w2, v2 in fields(v):
            if n2 == 1:
                oid = v2
            elif n2 == 2:
                for n3, _w3, v3 in fields(v2):
                    if n3 == 3:
                        spr = []
                        for n4, w4, v4 in fields(v3):
                            if n4 == 5:
                                spr += packed(v4) if w4 == 2 else [v4]
                        groups.append(spr)
        if oid == outfit_id:
            return groups
    raise SystemExit(f"outfit {outfit_id} not found")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    sprites = Sprites()
    idle, walk = outfit_groups(21)[:2]
    sheet = Image.new("RGBA", (9 * 64, 4 * 64))
    for d in range(4):                         # pattern x: 0 N, 1 E, 2 S, 3 W
        sheet.paste(sprites.get(idle[d]), (0, d * 64))
        for p in range(8):
            sheet.paste(sprites.get(walk[p * 4 + d]), ((p + 1) * 64, d * 64))
    sheet.save(OUT / "rat_client.png")
    grass = load_items()[4526]
    sprites.get(grass["sprites"][0]).save(OUT / "ground.png")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
