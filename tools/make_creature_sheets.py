#!/usr/bin/env python3
"""Pack approved creature sprites (art/output/<name>/frames, made by the Blender pipeline) into the client's sprite
sheet format, so tools/install_effects.py can show them in the game in place of the placeholder Tibia look
(roadmap R22 / 6.4: prove the art pipeline end to end).

    python tools/make_creature_sheets.py          writes art/creatures/game/<name>.bmp.lzma + creatures.json

Each creature: 4 directions (N, E, S, W) x (1 standing frame + 8 walk frames) = 36 sprites of 64 x 64, one 384 x 384
sheet. In the client's outfit the standing group lists N, E, S, W; the walking group lists them again for each of the
8 steps (sprite index = step * 4 + direction).
"""
from __future__ import annotations

import json
import lzma
import struct
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "art" / "creatures" / "game"
SHEET = 384
DIRS = ("N", "E", "S", "W")

# approved sprite -> the placeholder looks it replaces in the client (server/data-spirebound/monster: Field Rat and
# Pen Rat wear look 56). Only sprites listed in art/APPROVED.txt may go in.
# (Floors 2-10 still borrow placeholder looks too, so a few of their stand-in monsters share these until their own art.)
CREATURES = {"rat": [56], "boar": [119], "mole": [26], "toad": [222], "wasp": [44], "snapper": [112], "thornsnap": [28],
             "shardling": [122], "wolf": [27], "alpha": [52], "ram": [607], "sproutling": [19], "azhrakkar": [61]}


def cip_sheet(img: Image.Image) -> bytes:
    """One 384x384 sheet in the client's file format (same writer as art/effects/make_fx.py): a 32-byte header, then
    LZMA ("alone" form, with its end marker) holding a 32-bit bottom-up BMP (BITMAPV4 header, BGRA)."""
    px = np.asarray(img.convert("RGBA"), np.uint8)[::-1]
    bgra = px[..., [2, 1, 0, 3]].tobytes()
    dib = struct.pack("<IiiHHIIiiII", 108, SHEET, SHEET, 1, 32, 3, len(bgra), 3780, 3780, 0, 0)
    dib += struct.pack("<IIII", 0x00FF0000, 0x0000FF00, 0x000000FF, 0xFF000000) + b"BGRs" + bytes(36) + bytes(12)
    bmp = b"BM" + struct.pack("<IHHI", 14 + len(dib) + len(bgra), 0, 0, 14 + len(dib)) + dib + bgra
    comp = lzma.compress(bmp, format=lzma.FORMAT_ALONE,
                         filters=[{"id": lzma.FILTER_LZMA1, "dict_size": 1 << 25, "lc": 3, "lp": 0, "pb": 2}])
    size, vb = len(comp), bytearray()
    while True:
        b = size & 0x7F
        size >>= 7
        vb.append(b | (0x80 if size else 0))
        if not size:
            break
    head = bytes([0x70, 0x0A, 0xFA, 0x80, 0x24]) + bytes(vb)
    return bytes(32 - len(head)) + head + comp


def frame_order() -> list[str]:
    """standing N E S W, then for each walk step 1-8: N E S W"""
    return [f"{d}_0" for d in DIRS] + [f"{d}_{k}" for k in range(1, 9) for d in DIRS]


def main() -> None:
    approved = {l.strip() for l in (ROOT / "art" / "APPROVED.txt").read_text(encoding="utf-8").splitlines()
                if l.strip() and not l.startswith("#")}
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = []
    for name, looks in CREATURES.items():
        if name not in approved:
            sys.exit(f"make_creature_sheets: {name} is not approved (art/APPROVED.txt)")
        frames = ROOT / "art" / "output" / name / "frames"
        img = Image.new("RGBA", (SHEET, SHEET), (0, 0, 0, 0))
        for k, fid in enumerate(frame_order()):
            f = Image.open(frames / f"{fid}.png").convert("RGBA")
            assert f.size == (64, 64), f"{name} {fid}: {f.size}, want 64x64"
            img.paste(f, ((k % 6) * 64, (k // 6) * 64))
        (OUT / f"{name}.bmp.lzma").write_bytes(cip_sheet(img))
        manifest.append({"name": name, "file": f"{name}.bmp.lzma", "count": 36, "looks": looks})
    (OUT / "creatures.json").write_text(json.dumps({
        "about": "Spirebound creature sprites (Blender pipeline, approved by Jay); made by tools/make_creature_sheets.py, "
                 "installed in the client by tools/install_effects.py in place of the listed placeholder looks",
        "creatures": manifest}, indent=1))
    print(f"make_creature_sheets: {len(manifest)} creature sheet(s): " + ", ".join(m["name"] for m in manifest))


if __name__ == "__main__":
    main()
