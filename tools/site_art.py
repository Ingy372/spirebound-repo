#!/usr/bin/env python3
"""Website pictures from our own approved art (art/APPROVED.txt): a walking loop (facing east) and a standing pose
(facing south) for each approved creature, outfit and NPC, at their true size (Jay, 2026-11-25: "the monsters look a
bit bad blown up like that"), with soft see-through edges (animated PNG; GIFs only have hard edges).

  python tools/site_art.py        writes website/public/img/walk_<name>.png (animated) and stand_<name>.png

Only approved Blender-pipeline art goes in (never Tibia's). tools/gen_site.py copies website/public/img into any
other site it builds. Needs Pillow (Windows Python); run it again when new art is approved.
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "website" / "public" / "img"
SCALE = 1


def approved() -> list[str]:
    lines = (ROOT / "art" / "APPROVED.txt").read_text(encoding="utf-8").splitlines()
    return [l.strip() for l in lines if l.strip() and not l.startswith("#")]


def sprite(im: Image.Image) -> Image.Image:
    im = im.convert("RGBA")
    return im if SCALE == 1 else im.resize((im.width * SCALE, im.height * SCALE), Image.NEAREST)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob("walk_*.gif"):           # the first, 2x GIF version
        old.unlink()
    made = []
    for name in approved():
        frames_dir = ROOT / "art" / "output" / name / "frames"
        walk = [frames_dir / f"E_{i}.png" for i in range(1, 9)]
        if not all(f.exists() for f in walk) or not (frames_dir / "S_0.png").exists():
            continue
        frames = [sprite(Image.open(f)) for f in walk]
        frames[0].save(OUT / f"walk_{name}.png", save_all=True, append_images=frames[1:], duration=110, loop=0,
                       disposal=1, blend=0)
        sprite(Image.open(frames_dir / "S_0.png")).save(OUT / f"stand_{name}.png", optimize=True)
        made.append(name)
    print(f"site_art: {len(made)} approved sprites -> {OUT.relative_to(ROOT)}: {', '.join(made)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
