#!/usr/bin/env python3
"""Draws contact sheets of Tibia 15.11 items so a mapper can SEE which item id is which.

Reads the client files that setup downloads to .local/client (CipSoft art: for Jay's PC only). The pictures it writes go to
.local/scratch/ and are never committed (CLAUDE.md: no CipSoft files in the repo).

Usage:
  python tools/spriteview.py sheet out.png 1270-1280 1628-1640 3614 ...   # one labelled cell per id (ranges allowed)
  python tools/spriteview.py find wall                                   # list item ids whose name contains a word
This is also the first piece of roadmap 6.4 (custom assets): it decodes the sprite sheets and the appearances file.
"""
from __future__ import annotations

import json
import lzma
import struct
import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
THINGS = ROOT / ".local" / "client" / "data" / "things" / "1511"
SHEET_GEOMETRY = {0: (32, 32, 12, 12), 1: (32, 64, 12, 6), 2: (64, 32, 6, 12), 3: (64, 64, 6, 6)}  # w, h, columns, rows


# ---------------------------------------------------------------- sprite sheets
def decode_sheet(path: Path) -> Image.Image:
    """CipSoft sheets: zero padding, a short custom header, then raw LZMA (props + data, no size field), holding a BMP."""
    data = path.read_bytes()
    i = 0
    while data[i] == 0:
        i += 1
    i += 2                      # constants 0x70 0x0A
    size, i = varint(data, i)   # uncompressed size (the BMP)
    _comp, i = varint(data, i)  # compressed size
    props, rest = data[i:i + 5], data[i + 13:]   # an 8-byte size field follows the props (its value is not trusted)
    dec = lzma.LZMADecompressor(format=lzma.FORMAT_ALONE)
    raw = dec.decompress(props + bytes([255]) * 8 + rest)   # unknown size: the stream has no end marker
    from io import BytesIO
    return Image.open(BytesIO(raw)).convert("RGBA")


class Sprites:
    def __init__(self):
        self.catalog = [e for e in json.loads((THINGS / "catalog-content.json").read_text()) if e.get("type") == "sprite"]
        self.cache: dict[str, Image.Image] = {}

    def entry_for(self, sprite_id: int):
        for e in self.catalog:
            if e["firstspriteid"] <= sprite_id <= e["lastspriteid"]:
                return e

    def get(self, sprite_id: int) -> Image.Image | None:
        e = self.entry_for(sprite_id)
        if not e:
            return None
        sheet = self.cache.get(e["file"])
        if sheet is None:
            sheet = self.cache[e["file"]] = decode_sheet(THINGS / e["file"])
        w, h, cols, rows = SHEET_GEOMETRY[e["spritetype"]]
        n = sprite_id - e["firstspriteid"]
        x, y = (n % cols) * w, (n // cols) * h
        return sheet.crop((x, y, x + w, y + h))


# ---------------------------------------------------------------- appearances (protobuf, read by hand)
def varint(b: bytes, i: int):
    v = shift = 0
    while True:
        c = b[i]
        i += 1
        v |= (c & 0x7F) << shift
        if not c & 0x80:
            return v, i
        shift += 7


def fields(b: bytes):
    i = 0
    while i < len(b):
        key, i = varint(b, i)
        num, wt = key >> 3, key & 7
        if wt == 0:
            v, i = varint(b, i)
        elif wt == 2:
            ln, i = varint(b, i)
            v, i = b[i:i + ln], i + ln
        elif wt == 5:
            v, i = b[i:i + 4], i + 4
        elif wt == 1:
            v, i = b[i:i + 8], i + 8
        else:
            raise ValueError("bad wire type")
        yield num, wt, v


def packed(b: bytes):
    i, out = 0, []
    while i < len(b):
        v, i = varint(b, i)
        out.append(v)
    return out


def load_items():
    """id -> dict(name, sprites=[...], width, height, layers). Object appearances only (field 1 of the file)."""
    path = next(THINGS.glob("appearances-*.dat"))
    items = {}
    for num, wt, v in fields(path.read_bytes()):
        if num != 1:
            continue
        item = {"name": "", "sprites": [], "width": 1, "height": 1, "layers": 1}
        iid = None
        for n2, w2, v2 in fields(v):
            if n2 == 1:
                iid = v2
            elif n2 == 4 and w2 == 2:
                item["name"] = v2.decode("utf-8", "replace")
            elif n2 == 2 and w2 == 2 and not item["sprites"]:  # first frame group
                for n3, w3, v3 in fields(v2):
                    if n3 == 3 and w3 == 2:                     # sprite_info
                        for n4, w4, v4 in fields(v3):
                            if n4 == 1:
                                item["width"] = v4
                            elif n4 == 2:
                                item["height"] = v4
                            elif n4 == 4:
                                item["layers"] = v4
                            elif n4 == 5:
                                item["sprites"] += packed(v4) if w4 == 2 else [v4]
        if iid is not None:
            items[iid] = item
    return items


def parse_ids(args):
    ids = []
    for a in args:
        if "-" in a:
            lo, hi = a.split("-")
            ids += list(range(int(lo), int(hi) + 1))
        else:
            ids.append(int(a))
    return ids


def sheet(out: str, ids: list[int], cols: int = 12, zoom: int = 2):
    items, sprites = load_items(), Sprites()
    cell_w, cell_h = 72 * zoom // 2 * 2, 84 * zoom // 2 * 2
    rows = (len(ids) + cols - 1) // cols
    img = Image.new("RGB", (cols * cell_w, rows * cell_h), (60, 90, 60))
    d = ImageDraw.Draw(img)
    for n, iid in enumerate(ids):
        cx, cy = (n % cols) * cell_w, (n // cols) * cell_h
        d.rectangle((cx, cy, cx + cell_w - 1, cy + cell_h - 1), outline=(30, 50, 30))
        it = items.get(iid)
        if it and it["sprites"]:
            # the first sprite of the first frame: its natural size (a tree may be 64 x 64)
            spr = sprites.get(it["sprites"][0])
            if spr is not None:
                spr = spr.resize((spr.width * zoom, spr.height * zoom), Image.NEAREST)
                img.paste(spr, (cx + 4, cy + 4), spr)
        d.text((cx + 3, cy + cell_h - 24), str(iid), fill=(255, 255, 255))
        if it:
            d.text((cx + 3, cy + cell_h - 12), it["name"][:12], fill=(255, 235, 150))
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    img.save(out)
    print(f"wrote {out}: {len(ids)} items")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "sheet":
        sheet(sys.argv[2], parse_ids(sys.argv[3:]))
    elif cmd == "find":
        for iid, it in sorted(load_items().items()):
            if sys.argv[2].lower() in it["name"].lower():
                print(iid, it["name"])
    else:
        print(__doc__)
