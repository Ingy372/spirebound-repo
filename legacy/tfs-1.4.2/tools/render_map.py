#!/usr/bin/env python3
"""Render the compiled map to PNG previews so the agent and the owner can see it (11_FLOORS_AND_MAPS).

Reads maps/build/spirebound.otbm (run compile_map.py first) and draws every z level of the requested
region with the same art build_assets.py would ship (real art, procedural, or labeled placeholder).
Zone overlays: protection zones tinted white, house tiles tinted gold.

Usage:
  python3 tools/render_map.py                          # every z level, whole map extent, 32 px per tile
  python3 tools/render_map.py --scale 4                # minimap-style, 4 px per tile (large floors)
  python3 tools/render_map.py --region 5000,5000,40,40 --out docs/previews/test_town.png
Output default: maps/preview/z<NN>.png (git-ignored).
"""
from __future__ import annotations

import argparse
import struct
import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_assets as ba  # noqa: E402
import otformats as otf  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
S = 32


def read_map(path: Path):
    root = otf.read_tree(path.read_bytes(), b"OTBM")
    md = root.children[0]
    tiles = {}
    towns = []
    for area in md.children:
        if area.type == 4:
            r = otf.Reader(area.props)
            bx, by, z = r.u16(), r.u16(), r.u8()
            for tn in area.children:
                r = otf.Reader(tn.props)
                x, y = bx + r.u8(), by + r.u8()
                house = r.u32() if tn.type == 14 else 0
                flags, ids = 0, []
                while r.left():
                    a = r.u8()
                    if a == 3:
                        flags = r.u32()
                    elif a == 9:
                        ids.append(r.u16())
                    else:
                        raise ValueError(f"unexpected tile attr {a}")
                for it in tn.children:
                    ids.append(struct.unpack_from("<H", it.props, 0)[0])
                tiles[(x, y, z)] = (ids, flags, house)
        elif area.type == 12:
            for t in area.children:
                r = otf.Reader(t.props)
                tid = r.u32(); name = r.string(); towns.append((tid, name, (r.u16(), r.u16(), r.u8())))
    return tiles, towns


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--map", default=str(ROOT / "maps" / "build" / "spirebound.otbm"))
    ap.add_argument("--scale", type=int, default=32)
    ap.add_argument("--region", help="x,y,w,h")
    ap.add_argument("--z", type=int)
    ap.add_argument("--out")
    a = ap.parse_args()

    tiles, towns = read_map(Path(a.map))
    rows = {r["id"]: r for r in ba.load_rows() if r["category"] == "item"}
    cache = {}

    def sprite(iid):
        if iid not in cache:
            row = rows.get(iid)
            if row is None:
                im = Image.new("RGBA", (S, S), (255, 0, 255, 255))
            else:
                ims, _ = ba.item_images(row)
                im = ims[0]
            cache[iid] = im
        return cache[iid]

    zs = sorted({p[2] for p in tiles}) if a.z is None else [a.z]
    for z in zs:
        pts = [p for p in tiles if p[2] == z]
        if a.region:
            x0, y0, w, h = (int(v) for v in a.region.split(","))
        else:
            x0, y0 = min(p[0] for p in pts), min(p[1] for p in pts)
            w, h = max(p[0] for p in pts) - x0 + 1, max(p[1] for p in pts) - y0 + 1
        img = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 255))
        over = Image.new("RGBA", img.size, (0, 0, 0, 0))
        od = ImageDraw.Draw(over)
        for (x, y, zz), (ids, flags, house) in sorted(tiles.items(), key=lambda kv: (kv[0][1], kv[0][0])):
            if zz != z or not (x0 <= x < x0 + w and y0 <= y < y0 + h):
                continue
            px, py = (x - x0) * S, (y - y0) * S
            for iid in ids:
                sp = sprite(iid)
                img.alpha_composite(sp, (px + S - sp.width, py + S - sp.height) if sp.width > S else (px, py))
            if house:
                od.rectangle([px, py, px + S - 1, py + S - 1], fill=(255, 210, 80, 50))
            elif flags & 1:
                od.rectangle([px, py, px + S - 1, py + S - 1], fill=(255, 255, 255, 28))
        img.alpha_composite(over)
        d = ImageDraw.Draw(img)
        for tid, name, (tx, ty, tz) in towns:
            if tz == z and x0 <= tx < x0 + w and y0 <= ty < y0 + h:
                cx, cy = (tx - x0) * S + S // 2, (ty - y0) * S + S // 2
                d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], outline=(255, 60, 60, 255), width=2)
                d.text((cx + 8, cy - 6), f"temple: {name}", fill=(255, 255, 255, 255))
        if a.scale != S:
            img = img.resize((w * a.scale, h * a.scale), Image.BOX if a.scale < S else Image.NEAREST)
        out = Path(a.out) if a.out and len(zs) == 1 else ROOT / "maps" / "preview" / f"z{z:02d}.png"
        out.parent.mkdir(parents=True, exist_ok=True)
        img.convert("RGB").save(out)
        print(f"render_map: z{z} {w}x{h} tiles -> {out.relative_to(ROOT) if out.is_relative_to(ROOT) else out}")


if __name__ == "__main__":
    main()
