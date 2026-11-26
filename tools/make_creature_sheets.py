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

# approved people (NPCs and player outfits) -> a NEW look number of their own (roadmap 6.5). Many NPCs share one borrowed
# Tibia look, so reskinning it would change every NPC wearing it; instead each gets a look Tibia never used.
# Rules (art/README.md "Own look numbers"): numbers start at 2001, above the client's highest outfit (1875), and only
# ever grow; the NPC and outfit files use these numbers (tools/gen_npcs.py, server/data-spirebound/npc/*.lua,
# lib/spirebound/class_outfits.lua). Never renumber one that is in use: saved characters keep their look number.
#   2001-2009 player class outfits, 2010-2099 NPCs, 2100-2199 shop outfits, 2200-2499 monsters on the humanoid body.
NEW_LOOKS = {"vanguard": 2001, "ranger": 2002, "arcanist": 2003, "mystic": 2004,
             "vesper": 2010, "priest": 2011, "registrar": 2012, "banker": 2013, "merchant": 2014, "bess": 2015,
             "corwin": 2016, "pell": 2017, "veyra": 2018, "warden": 2019,
             "guildwarden": 2020, "quartermaster": 2021, "brannoch": 2022,
             # monsters on the humanoid body (2201+): they shared borrowed look 129/131 with NPCs, so no reskin
             "bandit": 2201, "captain": 2202, "archer": 2203, "sentinel": 2204,
             # Floor 1 bosses (approved via the art-count session): placed like the animals, so no people shift
             "gate_hound": 2205, "axe_lord": 2206, "axe_lord_blade": 2207}


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
    jobs = [(n, l, None) for n, l in CREATURES.items()] + [(n, [], look) for n, look in NEW_LOOKS.items()]
    for name, looks, new_look in jobs:
        if name not in approved:
            sys.exit(f"make_creature_sheets: {name} is not approved (art/APPROVED.txt)")
        frames = ROOT / "art" / "output" / name / "frames"
        # addons (Jay, 2026-11-25: base, addon 1, addon 2): approved overlays from art/pipeline/addon_overlay.py.
        # Addon 2 only goes in with addon 1 (the client ties pattern row 1 to addon 1 and row 2 to addon 2).
        layers = [frames]
        for k in (1, 2):
            ov = ROOT / "art" / "output" / f"{name}_a{k}" / "overlay"
            if new_look and f"{name}_a{k}" in approved and len(layers) == k and ov.exists():
                layers.append(ov)
        # client order: for each frame group / step, every addon row (base, addon 1, addon 2), each N E S W
        order = [(layer, fid) for group in ([f"{d}_0" for d in DIRS],) + tuple([f"{d}_{k}" for d in DIRS] for k in range(1, 9))
                 for layer in layers for fid in group]
        sheets, boxes = [], []
        for k, (layer, fid) in enumerate(order):
            if k % 36 == 0:
                sheets.append(Image.new("RGBA", (SHEET, SHEET), (0, 0, 0, 0)))
            f = Image.open(layer / f"{fid}.png").convert("RGBA")
            assert f.size == (64, 64), f"{name} {fid}: {f.size}, want 64x64"
            sheets[-1].paste(f, ((k % 36 % 6) * 64, (k % 36 // 6) * 64))
            if layer == frames and fid.endswith("_0"):     # standing N E S W: the drawn area, like Tibia's own entries
                x0, y0, x1, y1 = f.getchannel("A").getbbox()
                boxes.append([x0, y0, x1 - x0, y1 - y0])
        files = [f"{name}.bmp.lzma"] + [f"{name}_{i + 1}.bmp.lzma" for i in range(1, len(sheets))]
        for file, img in zip(files, sheets):
            (OUT / file).write_bytes(cip_sheet(img))
        for old in OUT.glob(f"{name}_*.bmp.lzma"):          # sheets from an earlier, bigger layout
            if old.name not in files:
                old.unlink()
        entry = {"name": name, "file": files[0], "count": 36, "looks": looks}
        if len(files) > 1:
            entry.update({"files": files, "count": len(order)})
        if new_look:
            # people are drawn 8 px low-right on the canvas like Tibia's own outfits (CANVAS_OFFSET), and Tibia's
            # people carry an 8 px shift up-left in the client: the new look gets the same shift
            # ...but only figures placed like people (humanoid CANVAS_OFFSET 8, 8); AUTO_PLACE creatures such as the
            # Floor 1 bosses sit like the animals and get no shift, or they would stand 8 px off their tile
            meta = json.loads((ROOT / "art" / "output" / name / "meta.json").read_text(encoding="utf-8"))
            shift = [0, 0] if meta.get("auto_place") is not None else [8, 8]   # older renders keep the offset in "canvas_offset"
            entry.update({"new_look": new_look, "shift": shift, "boxes": boxes, "addons": len(layers) - 1,
                          "size": max(max(b[2], b[3]) for b in boxes)})
        manifest.append(entry)
    (OUT / "creatures.json").write_text(json.dumps({
        "about": "Spirebound creature sprites (Blender pipeline, approved by Jay); made by tools/make_creature_sheets.py, "
                 "installed in the client by tools/install_effects.py in place of the listed placeholder looks",
        "creatures": manifest}, indent=1))
    print(f"make_creature_sheets: {len(manifest)} creature sheet(s): " + ", ".join(m["name"] for m in manifest))


if __name__ == "__main__":
    main()
