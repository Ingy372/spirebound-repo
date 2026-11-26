#!/usr/bin/env python3
"""Turn an outfit's addon renders into Tibia-style addon overlays (Jay, 2026-11-25: base outfit, addon 1, addon 2).

  python art/pipeline/addon_overlay.py vanguard

For each addon model <base>_a1 / <base>_a2 (art/models/, rendered like any sprite: the whole figure WITH the addon)
this keeps only the pixels that differ from the approved base frames and writes art/output/<base>_aN/overlay/.
In the game the client draws the base, then the overlay of every addon the player owns, on top.
Also writes art/output/<base>_addons_preview.png (on plain grey) and walk_S/E/N/W_4x.gif with both addons on,
for Jay to judge. The base is never re-rendered (approved sprites are frozen).
"""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageChops

ART = Path(__file__).resolve().parent.parent
OUT = ART / "output"
GREY = (196, 194, 188, 255)
DIRS = ("S", "E", "N", "W")


def overlay(base: Image.Image, full: Image.Image) -> Image.Image:
    diff = ImageChops.difference(base, full).convert("RGBA")
    mask = Image.eval(diff.convert("L").point(lambda v: 255 if v else 0), lambda v: v)
    alpha_diff = ImageChops.difference(base.getchannel("A"), full.getchannel("A"))
    mask = ImageChops.lighter(mask, alpha_diff.point(lambda v: 255 if v else 0))
    out = Image.new("RGBA", full.size, (0, 0, 0, 0))
    out.paste(full, (0, 0), mask)
    return out


def addons_of(base: str) -> list[str]:
    return [f"{base}_a{k}" for k in (1, 2) if (OUT / f"{base}_a{k}" / "frames").exists()]


def main(base: str) -> None:
    names = addons_of(base)
    if not names:
        sys.exit(f"addon_overlay: no rendered addons for {base} (render {base}_a1 / {base}_a2 first)")
    bdir = OUT / base / "frames"
    for name in names:
        (OUT / name / "overlay").mkdir(exist_ok=True)
        lost = 0
        for f in sorted(bdir.glob("*.png")):
            b = Image.open(f).convert("RGBA")
            full = Image.open(OUT / name / "frames" / f.name).convert("RGBA")
            ov = overlay(b, full)
            check = b.copy()
            check.alpha_composite(ov)
            # an overlay can only add pixels: where the addon render is empty but the base is not (an outline pixel
            # that moved), the base pixel stays. A handful is invisible; many means the addon hides part of the base.
            cb, fb = check.tobytes(), full.tobytes()
            wrong = sum(1 for i in range(0, len(cb), 4) if cb[i:i + 4] != fb[i:i + 4])
            lost += wrong
            ov.save(OUT / name / "overlay" / f.name)
        if lost > 12:
            sys.exit(f"addon_overlay: {name} would need to erase {lost} base pixels; an addon can only add on top")
        if lost:
            print(f"addon_overlay: {name}: {lost} stray base pixel(s) kept (an overlay cannot erase)")

    def dressed(fid: str, which: list[str]) -> Image.Image:
        im = Image.open(bdir / f"{fid}.png").convert("RGBA")
        for n in which:
            im.alpha_composite(Image.open(OUT / n / "overlay" / f"{fid}.png").convert("RGBA"))
        return im

    rows = [("base", [])] + [(f"addon {n[-1]}", [n]) for n in names] + ([("both", names)] if len(names) > 1 else [])
    Z, C = 4, 64
    sheet = Image.new("RGBA", (4 * C * Z, len(rows) * C * Z), GREY)
    for r, (_label, which) in enumerate(rows):
        for c, d in enumerate(DIRS):
            im = dressed(f"{d}_0", which).resize((C * Z, C * Z), Image.NEAREST)
            sheet.alpha_composite(im, (c * C * Z, r * C * Z))
    sheet.convert("RGB").save(OUT / f"{base}_addons_preview.png")
    for d in DIRS:
        frames = []
        for k in range(1, 9):
            bg = Image.new("RGBA", (C, C), GREY)
            bg.alpha_composite(dressed(f"{d}_{k}", names))
            frames.append(bg.convert("RGB").resize((C * Z, C * Z), Image.NEAREST))
        frames[0].save(OUT / f"{base}_addons_walk_{d}_4x.gif", save_all=True, append_images=frames[1:], duration=120, loop=0)
    print(f"addon_overlay: {base}: overlays for {', '.join(names)}; preview art/output/{base}_addons_preview.png")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "vanguard")
