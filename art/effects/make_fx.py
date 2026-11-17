#!/usr/bin/env python3
"""Make Spirebound's own spell effects: Blender renders the solid parts, this paints the light and shrinks it all
to game pixels.

  python art/effects/make_fx.py                 # every effect
  python art/effects/make_fx.py meteor bloom    # only these

Output, per effect, in art/effects/output/<name>/:
  frame_<n>.png        64x64 game frames (the spell's tile is the bottom-right quarter)
  <name>_sheet.png     every frame in a row at 4x on plain grey (top) and on dark grey (bottom)
  <name>.gif           the animation at 4x on plain grey
and art/effects/output/all_effects.png, one row per effect.
tools/install_effects.py then puts the frames into the game.
Needs Blender 5.3 (BLENDER= to point elsewhere), Pillow and numpy.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import fx2d  # noqa: E402
import paints  # noqa: E402

OUT = HERE / "output"
BLENDER = os.environ.get("BLENDER", r"C:\Program Files\Blender Foundation\Blender 5.3\blender.exe")
GREY, DARK = (128, 128, 128), (52, 56, 60)
ALPHA_STEPS = np.array([0.0, 0.34, 0.6, 0.82, 1.0], np.float32)


def render_solids(name, frames, folder):
    subprocess.run([BLENDER, "-b", "--factory-startup", "--python", str(HERE / "render_fx.py"), "--", name,
                    str(frames), str(folder)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def load_solid(path):
    return np.asarray(Image.open(path).convert("RGBA"), np.float32) / 255.0


def pixelize(canvas, solid_alpha=None):
    """4x canvas -> 64x64 game frame. Colours are rounded to a small set and the edge is cut clean, so the result
    reads as pixel art; soft light keeps a few steps of see-through. Solid parts get a dark outline."""
    n, ss = fx2d.SIZE, fx2d.SS
    a = canvas.a.reshape(n, ss, n, ss).mean(axis=(1, 3))
    rgb = canvas.rgb.reshape(n, ss, n, ss, 3).mean(axis=(1, 3))
    rgb = np.where(a[..., None] > 1e-4, rgb / np.maximum(a[..., None], 1e-4), 0.0)
    rgb = np.clip(rgb, 0.0, 1.0)
    rgb = np.round(rgb * 15.0) / 15.0                       # 16 steps per channel
    a = np.clip(a, 0.0, 1.0) ** 0.8                           # soft light a little bolder
    a = np.where(a < 0.16, 0.0, a)
    idx = np.abs(a[..., None] - ALPHA_STEPS[None, None, :]).argmin(axis=2)
    a = ALPHA_STEPS[idx]
    out = np.dstack([rgb, a])
    if solid_alpha is not None:
        s = solid_alpha.reshape(n, ss, n, ss).mean(axis=(1, 3)) > 0.5
        grown = s.copy()
        grown[1:, :] |= s[:-1, :]
        grown[:-1, :] |= s[1:, :]
        grown[:, 1:] |= s[:, :-1]
        grown[:, :-1] |= s[:, 1:]
        edge = grown & ~s & (out[..., 3] < 0.7)
        out[edge] = (0.10, 0.08, 0.12, 0.82)
    return Image.fromarray((out * 255.0 + 0.5).astype(np.uint8), "RGBA")


def on(bg, frame, scale=4):
    im = Image.new("RGBA", frame.size, bg + (255,))
    im.alpha_composite(frame)
    return im.resize((frame.width * scale, frame.height * scale), Image.NEAREST).convert("RGB")


def make(name, eid, frames, ms, has_solid):
    folder = OUT / name
    folder.mkdir(parents=True, exist_ok=True)
    for old in folder.glob("frame_*.png"):
        old.unlink()
    if has_solid:
        render_solids(name, frames, folder / "solid")
    out = []
    for i in range(frames):
        t = paints.frame_time(name, i, frames)
        back, front = fx2d.Canvas(), fx2d.Canvas()
        paints.PAINTERS[name](back, front, t, i, frames)
        solid_alpha = None
        if has_solid:
            solid = load_solid(folder / "solid" / ("solid_%02d.png" % i))
            solid_alpha = solid[..., 3]
            back.layer(solid)
        frame = pixelize(front.under(back), solid_alpha)
        frame.save(folder / ("frame_%02d.png" % i))
        out.append(frame)
    w = 256
    sheet = Image.new("RGB", (w * frames, w * 2), GREY)
    for i, f in enumerate(out):
        sheet.paste(on(GREY, f), (i * w, 0))
        sheet.paste(on(DARK, f), (i * w, w))
    sheet.save(folder / f"{name}_sheet.png")
    gif = [on(GREY, f) for f in out]
    gif[0].save(folder / f"{name}.gif", save_all=True, append_images=gif[1:], duration=ms, loop=0)
    if has_solid:                                   # the raw renders are not needed afterwards
        for p in (folder / "solid").glob("*.png"):
            p.unlink()
        (folder / "solid").rmdir()
    print(f"{name}: {frames} frames")
    return out


def overview():
    rows = []
    for name, eid, frames, ms, has_solid in paints.EFFECTS:
        fs = sorted((OUT / name).glob("frame_*.png"))
        if fs:
            rows.append([Image.open(f).convert("RGBA") for f in fs])
    if not rows:
        return
    cols = max(len(r) for r in rows)
    sheet = Image.new("RGB", (cols * 128, len(rows) * 128), GREY)
    for y, r in enumerate(rows):
        for x, f in enumerate(r):
            sheet.paste(on(GREY, f, 2), (x * 128, y * 128))
    sheet.save(OUT / "all_effects.png")


def main(argv):
    wanted = set(argv)
    for name, eid, frames, ms, has_solid in paints.EFFECTS:
        if not wanted or name in wanted:
            make(name, eid, frames, ms, has_solid)
    overview()


if __name__ == "__main__":
    main(sys.argv[1:])
