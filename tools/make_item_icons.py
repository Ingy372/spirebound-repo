#!/usr/bin/env python3
"""Finish item icons made with the creature pipeline (art/ITEM_RULES.md) and build the review sheet.

  sh art/pipeline/render.sh item_<name>        # first: Blender render + pixel cleanup
  python tools/make_item_icons.py              # every art/models/item_*.py that has been rendered
  python tools/make_item_icons.py item_inn_tankard item_plains_map

For each item: takes the east view's standing frame, centres the item on a 32x32 tile (Tibia items sit in the
middle of their tile, a pixel or two low-right) and writes art/output/<name>/icon.png and icon_4x.png.
Review sheet: ART_FOR_JAY/items_review.png, each item at 4x beside the Grok version (if any) and the closest Tibia
item, then all of them at real size on grass. The Tibia items are drawn from the client files on this PC for
comparison only (ART_FOR_JAY/ and .local/ are git-ignored; never commit, ship or trace them).
"""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "art" / "output"
BG = (196, 194, 188)

# our item -> the closest Tibia item (id in the 15.11 client), compared side by side, never copied
LOOKALIKES = {
    "item_briarguard_sabre": 3273,          # sabre
    "item_copsewood_bow": 3350,             # bow
    "item_wand_of_ember_script": 3071,      # wand of inferno
    "item_thornward_rod": 3066,             # snakebite rod
    "item_millrace_boots": 3552,            # leather boots
    "item_shrinekeepers_pendant": 3025,     # ancient amulet
    "item_wardens_signet": 31592,           # signet ring
    "item_inn_tankard": 32072,              # beer mug
    "item_brass_spyglass": 9616,            # bejeweled ship's telescope
    "item_plains_map": 5090,                # treasure map
    "item_message_bottle": 5802,            # message in a bottle
}


def icon(name: str, nudge=(1, 1)) -> Image.Image | None:
    f = OUT / name / "frames" / "E_0.png"
    if not f.exists():
        return None
    im = Image.open(f).convert("RGBA")
    box = im.getbbox()
    if not box:
        return None
    item = im.crop(box)
    if item.width > 32 or item.height > 32:
        print(f"  warning: {name} is {item.width}x{item.height} px: bigger than its 32x32 tile (shrink SIZE)")
    tile = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    x = max(0, min(32 - item.width, (32 - item.width) // 2 + nudge[0]))
    y = max(0, min(32 - item.height, (32 - item.height) // 2 + nudge[1]))
    tile.paste(item, (x, y), item)
    tile.save(OUT / name / "icon.png")
    tile.resize((128, 128), Image.Resampling.NEAREST).save(OUT / name / "icon_4x.png")
    return tile


def tibia_items(ids):
    try:
        sys.path.insert(0, str(ROOT / "tools"))
        from spriteview import Sprites, load_items
        items, spr = load_items(), Sprites()
        out = {}
        for i in ids:
            it = items.get(i)
            if it and it["sprites"]:
                out[i] = (it["name"], spr.get(it["sprites"][0]).convert("RGBA"))
        return out
    except Exception as e:                       # no client files on this machine: sheet without Tibia items
        print(f"  (no Tibia reference items: {e})")
        return {}


def grok_version(name):
    f = ROOT / "ART_FOR_JAY" / "grok_out" / f"{name}.png"
    return Image.open(f).convert("RGBA") if f.exists() else None


def big(im, z=4):
    return im.resize((im.width * z, im.height * z), Image.Resampling.NEAREST)


def sheet(rows, path):
    Z = 4
    cw, ch = 3 * 32 * Z + 70, 32 * Z + 34
    cols = 2
    nrows = (len(rows) + cols - 1) // cols
    grass_f = ROOT / ".local" / "artref" / "ground.png"
    grass = Image.open(grass_f).convert("RGBA").crop((0, 0, 32, 32)) if grass_f.exists() else Image.new("RGBA", (32, 32), (70, 120, 50, 255))
    strip_h = 32 * 2 + 70
    img = Image.new("RGB", (cols * cw + 20, nrows * ch + 40 + strip_h), BG)
    d = ImageDraw.Draw(img)
    d.text((10, 8), "Each item: ours (Claude, pipeline)  |  Grok + clean-up  |  closest Tibia item.  4x.  "
                    "Bottom: real size on grass (ours / Tibia).  Tibia and Grok shown for comparison only.", fill=(40, 34, 30))
    for n, (name, ours, grok, tib) in enumerate(rows):
        x, y = 10 + (n % cols) * cw, 30 + (n // cols) * ch
        for k, im in enumerate((ours, grok, tib[1] if tib else None)):
            if im is not None:
                b = big(im, Z)
                img.paste(b, (x + k * (32 * Z + 20), y), b)
        d.text((x, y + 32 * Z + 4), name.replace("item_", "").replace("_", " "), fill=(20, 60, 30))
        if tib:
            d.text((x + 2 * (32 * Z + 20), y + 32 * Z + 4), tib[0], fill=(100, 40, 30))
    sy = nrows * ch + 40
    d.text((10, sy), "real size: top row ours, bottom row the Tibia item", fill=(40, 34, 30))
    for n, (name, ours, grok, tib) in enumerate(rows):
        for k, im in enumerate((ours, tib[1] if tib else None)):
            g = grass.copy()
            if im is not None:
                g.alpha_composite(im.crop((0, 0, 32, 32)))
            img.paste(g, (10 + n * 36, sy + 16 + k * 36))
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path)
    print(f"wrote {path.relative_to(ROOT)}")


def main():
    names = sys.argv[1:] or sorted(p.stem for p in (ROOT / "art" / "models").glob("item_*.py") if p.stem != "item_kit")
    tib = tibia_items([LOOKALIKES[n] for n in names if n in LOOKALIKES])
    rows = []
    for n in names:
        ic = icon(n)
        if ic is None:
            print(f"  {n}: not rendered yet (sh art/pipeline/render.sh {n})")
            continue
        rows.append((n, ic, grok_version(n), tib.get(LOOKALIKES.get(n))))
        print(f"  {n}: icon.png")
    if rows:
        sheet(rows, ROOT / "ART_FOR_JAY" / "items_review.png")


if __name__ == "__main__":
    main()
