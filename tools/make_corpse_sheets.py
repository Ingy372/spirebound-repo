#!/usr/bin/env python3
"""Dead bodies for our own monsters (art/CORPSE_RULES.md): turn the corpse renders into decay steps and a review sheet.

    sh art/pipeline/render.sh corpse_<monster>     (once per monster, plus corpse_bones and corpse_bones_big)
    python tools/make_corpse_sheets.py             writes art/output/corpse_<monster>/item/{1_fresh,2_rot,3_end}.png
                                                   and ART_FOR_JAY/corpses_sheet.png (plain grey, for approval)

Each monster: the living monster standing (for comparison), then its three decay steps:
  1 fresh  - the body lying down (frame 0 of the corpse render, seen from CORPSES[name]["dir"])
  2 rot    - the sunk body (frame 1), darkened and greyed (rule C4)
  3 end    - bones (corpse_bones / corpse_bones_big) for flesh monsters, else the dried husk (frame 2), darker still
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "art" / "output"
BG = (196, 194, 188)          # plain grey (Jay: sprite sheets on plain grey, never grass)

# monster -> how its corpse is seen and how it ends. dir: which render direction reads best lying down
# (animals rolled on their side show their legs in the air from the W; people on their back read from the E).
# end: "bones" / "bones_big" (2x2 bosses) / "husk" (no bones: stone, chitin, plants, spirits).
CORPSES = {
    "bandit": ("Road Bandit", "E", "bones"), "captain": ("Bandit Captain", "E", "bones"),
    "crossbowman": ("Bandit Crossbowman", "E", "bones"), "hexer": ("Hedge Hexer", "E", "bones"),
    "cutthroat": ("Hill Cutthroat", "E", "bones"), "archer": ("Ruin Archer", "E", "bones"),
    "sentinel": ("Ruin Sentinel / Granite Warden", "E", "husk"), "underkeeper": ("The Underkeeper", "E", "bones_big"),
    "ridgecat": ("Ridge Cat", "W", "bones"), "bull": ("Herd Bull", "W", "bones_big"),
    "stonebull": ("Stonehide Bull", "W", "bones_big"), "grazer": ("Horned Grazer", "W", "bones"),
    "strider": ("Dust Strider", "W", "bones"), "old_tusk": ("Old Tusk", "W", "bones_big"),
    "hollowfang": ("Hollowfang", "W", "bones_big"), "gate_hound": ("Gate Hound", "W", "bones_big"),
    "crawler": ("Black Crawler", "E", "husk"), "blightwasp": ("Blight Wasp", "E", "husk"),
    "briar_mother": ("Briar Mother", "E", "husk"), "vault_wraith": ("Vault Wraith", "E", "husk"),
}


def decay(img: Image.Image, grey: float, dark: float) -> Image.Image:
    """C4: rot greys the colours toward a dull green-brown and darkens them; the outline stays as it is."""
    a = np.asarray(img.convert("RGBA")).astype(float)
    rgb, alpha = a[..., :3], a[..., 3:]
    lum = rgb @ np.array([0.30, 0.59, 0.11])
    tint = np.stack([lum * 1.02, lum * 1.0, lum * 0.86], -1)          # dull green-brown, not neutral grey
    out = (rgb * (1 - grey) + tint * grey) * dark
    return Image.fromarray(np.dstack([np.clip(out, 0, 255), alpha]).astype(np.uint8), "RGBA")


def steps(name: str) -> list[Image.Image]:
    _label, d, end = CORPSES[name]
    fr = OUT / f"corpse_{name}" / "frames"
    fresh = Image.open(fr / f"{d}_0.png").convert("RGBA")
    rot = decay(Image.open(fr / f"{d}_1.png"), 0.45, 0.80)
    if end.startswith("bones"):
        last = Image.open(OUT / f"corpse_{end}" / "frames" / "E_0.png").convert("RGBA")
    else:
        last = decay(Image.open(fr / f"{d}_2.png"), 0.70, 0.62)
    return [fresh, rot, last]


def main() -> None:
    cols, zoom, cell = 2, 2, 128
    names = [n for n in CORPSES if (OUT / f"corpse_{n}" / "frames").exists()]
    rows = (len(names) + cols - 1) // cols
    head, lab = 34, 16
    W, H = cols * 4 * cell + (cols - 1) * 24 + 16, head + rows * (cell + lab + 8) + 8
    sheet = Image.new("RGB", (W, H), BG)
    dr = ImageDraw.Draw(sheet)
    dr.text((8, 8), "Corpses (2x): living monster | 1 fresh | 2 rotting | 3 bones or husk   -   plain grey", fill=(30, 30, 30))
    for i, n in enumerate(names):
        imgs = steps(n)
        item = OUT / f"corpse_{n}" / "item"
        item.mkdir(parents=True, exist_ok=True)
        for k, (im, tag) in enumerate(zip(imgs, ("1_fresh", "2_rot", "3_end"))):
            im.save(item / f"{tag}.png")
        alive = OUT / n / "frames" / "S_0.png"
        row = [Image.open(alive).convert("RGBA") if alive.exists() else Image.new("RGBA", (64, 64))] + imgs
        x0 = 8 + (i % cols) * (4 * cell + 24)
        y0 = head + (i // cols) * (cell + lab + 8)
        dr.text((x0, y0), CORPSES[n][0], fill=(30, 30, 30))
        for k, im in enumerate(row):
            big = im.resize((cell, cell), Image.NEAREST)
            sheet.paste(big, (x0 + k * cell, y0 + lab), big)
    dest = ROOT / "ART_FOR_JAY" / "corpses_sheet.png"
    sheet.save(dest)
    print(f"make_corpse_sheets: {len(names)} corpses -> {dest}")


if __name__ == "__main__":
    main()
