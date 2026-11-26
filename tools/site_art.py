#!/usr/bin/env python3
"""Website pictures from our own approved art (art/APPROVED.txt): a walking loop (facing east) and a standing pose
(facing south) for each approved creature, outfit and NPC, at 2x, with a see-through background.

  python tools/site_art.py        writes website/public/img/walk_<name>.gif and stand_<name>.png

Only approved Blender-pipeline art goes in (never Tibia's). tools/gen_site.py copies website/public/img into any
other site it builds. Needs Pillow (Windows Python); run it again when new art is approved.
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "website" / "public" / "img"
SCALE = 2


def approved() -> list[str]:
    lines = (ROOT / "art" / "APPROVED.txt").read_text(encoding="utf-8").splitlines()
    return [l.strip() for l in lines if l.strip() and not l.startswith("#")]


def crisp(im: Image.Image) -> Image.Image:
    """Pixel art at 2x with hard edges: half-see-through pixels become solid or clear (GIFs have no soft edges)."""
    im = im.convert("RGBA").resize((im.width * SCALE, im.height * SCALE), Image.NEAREST)
    r, g, b, a = im.split()
    return Image.merge("RGBA", (r, g, b, a.point(lambda v: 255 if v >= 110 else 0)))


def to_gif_frame(im: Image.Image) -> Image.Image:
    p = im.convert("RGB").quantize(colors=255, method=Image.Quantize.MEDIANCUT)
    p.paste(255, mask=im.split()[3].point(lambda v: 255 if v == 0 else 0))
    p.info["transparency"] = 255
    return p


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    made = []
    for name in approved():
        frames_dir = ROOT / "art" / "output" / name / "frames"
        walk = [frames_dir / f"E_{i}.png" for i in range(1, 9)]
        if not all(f.exists() for f in walk) or not (frames_dir / "S_0.png").exists():
            continue
        frames = [to_gif_frame(crisp(Image.open(f))) for f in walk]
        frames[0].save(OUT / f"walk_{name}.gif", save_all=True, append_images=frames[1:], duration=110, loop=0,
                       transparency=255, disposal=2, optimize=False)
        crisp(Image.open(frames_dir / "S_0.png")).save(OUT / f"stand_{name}.png", optimize=True)
        made.append(name)
    print(f"site_art: {len(made)} approved sprites -> {OUT.relative_to(ROOT)}: {', '.join(made)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
