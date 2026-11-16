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


def outfit_info(outfit_id):
    """[(sprite_info_fields, sprite_ids)] per frame group (0 = standing, 1 = walking)."""
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
                        info, spr = {}, []
                        for n4, w4, v4 in fields(v3):
                            if n4 == 5:
                                spr += packed(v4) if w4 == 2 else [v4]
                            elif w4 == 0:
                                info[n4] = v4
                        groups.append((info, spr))
        if oid == outfit_id:
            return groups
    raise SystemExit(f"outfit {outfit_id} not found")


def outfit_color(c):
    """Tibia's 133-colour outfit table (hue/saturation/intensity steps), as the client computes it."""
    steps, si = 19, 7
    if c >= steps * si:
        c = 0
    if c % steps == 0:
        v = int(255 * (1 - c / steps / si))
        return v, v, v
    h = (c % steps) / 18.0
    s, i = [(0.25, 1.0), (0.25, 0.75), (0.5, 0.75), (0.667, 0.75), (1.0, 1.0), (1.0, 0.75), (1.0, 0.5)][c // steps]
    lo = i * (1 - s)
    if h < 1 / 6:
        r, b = i, lo; g = b + (i - b) * 6 * h
    elif h < 2 / 6:
        g, b = i, lo; r = g - (i - b) * (6 * h - 1)
    elif h < 3 / 6:
        g, r = i, lo; b = r + (i - r) * (6 * h - 2)
    elif h < 4 / 6:
        b, r = i, lo; g = b - (i - r) * (6 * h - 3)
    elif h < 5 / 6:
        b, g = i, lo; r = g + (i - g) * (6 * h - 4)
    else:
        r, g = i, lo; b = r - (i - g) * (6 * h - 5)
    return int(r * 255), int(g * 255), int(b * 255)


def tint(base, mask, colors):
    """Multiply the grey base by the outfit colours where the mask is yellow (head), red (body), green (legs),
    blue (feet), the way the client does."""
    import numpy as np
    b = np.array(base.convert("RGBA")).astype(float)
    m = np.array(mask.convert("RGBA"))
    keys = {(255, 255, 0): 0, (255, 0, 0): 1, (0, 255, 0): 2, (0, 0, 255): 3}
    for key, slot in keys.items():
        sel = (m[..., 0] == key[0]) & (m[..., 1] == key[1]) & (m[..., 2] == key[2]) & (m[..., 3] > 0)
        col = np.array(outfit_color(colors[slot])) / 255.0
        b[sel, :3] *= col
    return Image.fromarray(b.clip(0, 255).astype("uint8"))


def dump_outfit(sprites, outfit_id, out_name, colors=None):
    """Base look only (no addons, no mount): rows N/E/S/W, stand + 8 walk. With colors (head, body, legs, feet)
    the grey sprite is tinted through its colour-mask layer, otherwise it stays grey."""
    groups = outfit_info(outfit_id)
    sheet = Image.new("RGBA", (9 * 64, 4 * 64))
    for g, (info, spr) in enumerate(groups[:2]):
        width, height, depth, layers = info.get(1, 1), info.get(2, 1), info.get(3, 1), info.get(4, 1)
        phases = len(spr) // (width * height * depth * layers)
        for d in range(4):
            for p in range(phases if g else 1):
                idx = ((((p * depth + 0) * height + 0) * width + d) * layers + 0)
                col = 0 if g == 0 else p + 1
                im = sprites.get(spr[idx]).convert("RGBA")
                if colors and layers > 1:
                    im = tint(im, sprites.get(spr[idx + 1]), colors)
                sheet.alpha_composite(im, (col * 64, d * 64))
    sheet.save(OUT / out_name)


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


# Our monster -> the closest creature that already exists in Tibia (comparison only: size, silhouette, how much
# detail fits, how the walk reads). Jay, 2026-11-15: compare monsters with a real Tibia look-alike, not the rat.
LOOKALIKES = {
    "mole": [(1048, "Mole"), (105, "Badger")],
    "wasp": [(44, "Wasp")],
    "snapper": [(198, "Thornback Tortoise"), (112, "Crab")],
    "toad": [(222, "Toad"), (412, "Bog Frog")],
    "wolf": [(27, "Wolf")],
    "alpha": [(3, "War Wolf"), (52, "Winter Wolf")],
    "sproutling": [(535, "Swampling"), (567, "Leaf Golem")],
    "boar": [(380, "Boar")],
    "sentinel": [(67, "Stone Golem"), (95, "Gargoyle")],
    "ram": [(14, "Sheep"), (13, "Black Sheep")],
    "archer": [(33, "Skeleton"), (298, "Skeleton Warrior")],
    "shardling": [(294, "Wisp"), (263, "Crystal Spider")],
    "thornsnap": [(120, "Carniphila"), (221, "Spit Nettle")],
    "azhrakkar": [(35, "Demon"), (55, "Behemoth")],
}


def dump_creature(sprites, outfit_id, out_name):
    """A plain monster look: rows N/E/S/W, stand + 8 walk (shorter walk cycles are spread over the 8 columns)."""
    groups = outfit_info(outfit_id)
    sheet = Image.new("RGBA", (9 * 64, 4 * 64))
    stand, walk = groups[0][1], groups[-1][1]
    wph = max(1, len(walk) // 4)
    for d in range(4):
        cells = [stand[d]] + [walk[(c * wph // 8) * 4 + d] for c in range(8)]
        for col, sid in enumerate(cells):
            im = sprites.get(sid).convert("RGBA")
            sheet.alpha_composite(im, (col * 64 + 64 - im.width, d * 64 + 64 - im.height))
    sheet.save(OUT / out_name)


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
    for oid in (128, 133, 136):                 # citizen, summoner (Vesper's borrowed look), a female citizen
        dump_outfit(sprites, oid, f"outfit_{oid}.png")
    dump_outfit(sprites, 133, "vesper_current.png", colors=(95, 113, 114, 95))   # Vesper's look in-game today
    for ours, refs in LOOKALIKES.items():
        for oid, _label in refs:
            dump_creature(sprites, oid, f"look_{oid}.png")
    grass = load_items()[4526]
    sprites.get(grass["sprites"][0]).save(OUT / "ground.png")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
