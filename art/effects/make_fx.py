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
It then packs every frame into the game's own format in art/effects/game/ (committed: these are our own pictures):
sprite sheets (sheet_<n>.bmp.lzma) and effects.json, which tools/install_effects.py puts into the client and server.
Needs Blender 5.3 (BLENDER= to point elsewhere), Pillow and numpy.
"""
from __future__ import annotations

import json
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


# ------------------------------------------------------------------------------------------- packing for the game
GAME = HERE / "game"
SHEET = 384                    # the client's sheet size
PER_SHEET = (SHEET // 64) ** 2  # 36 frames of 64x64 per sheet
# light around each effect: Tibia's 216-colour index (r*36 + g*6 + b, each 0..5) and a brightness
LIGHT = {"steel_arc": (215, 2), "skyrend": (205, 5), "oath_halo": (205, 3), "ground_crack": (0, 0),
         "war_banner": (186, 2), "light_needles": (213, 4), "sun_sigil": (213, 3), "violet_bolt": (119, 5),
         "meteor": (198, 6), "ember_pillar": (198, 5), "thorn_burst": (103, 2), "leaf_ward": (103, 3),
         "ice_spires": (101, 3), "bloom": (103, 3), "clash": (215, 4), "void_pull": (119, 3),
         "ember_sigil": (198, 3), "frost_sigil": (101, 3)}


def cip_sheet(img: Image.Image) -> bytes:
    """One 384x384 sheet in the client's file format: a 32-byte header, then LZMA ("alone" form, with its end marker)
    holding a 32-bit bottom-up BMP (BITMAPV4 header, BGRA)."""
    import lzma
    import struct
    px = np.asarray(img.convert("RGBA"), np.uint8)[::-1]          # bottom-up
    bgra = px[..., [2, 1, 0, 3]].tobytes()
    dib = struct.pack("<IiiHHIIiiII", 108, SHEET, SHEET, 1, 32, 3, len(bgra), 3780, 3780, 0, 0)
    dib += struct.pack("<IIII", 0x00FF0000, 0x0000FF00, 0x000000FF, 0xFF000000) + b"BGRs" + bytes(36) + bytes(12)
    bmp = b"BM" + struct.pack("<IHHI", 14 + len(dib) + len(bgra), 0, 0, 14 + len(dib)) + dib + bgra
    assert len(bmp) == 122 + SHEET * SHEET * 4
    comp = lzma.compress(bmp, format=lzma.FORMAT_ALONE, filters=[{"id": lzma.FILTER_LZMA1, "dict_size": 1 << 25, "lc": 3, "lp": 0, "pb": 2}])
    size = len(comp)
    vb = bytearray()
    while True:
        b = size & 0x7F
        size >>= 7
        vb.append(b | (0x80 if size else 0))
        if not size:
            break
    head = bytes([0x70, 0x0A, 0xFA, 0x80, 0x24]) + bytes(vb)
    return bytes(32 - len(head)) + head + comp


def pack():
    """every effect's frames -> art/effects/game/sheet_<n>.bmp.lzma + effects.json"""
    GAME.mkdir(exist_ok=True)
    for old in GAME.glob("sheet_*.bmp.lzma"):
        old.unlink()
    frames, manifest = [], []
    for name, eid, n, ms, has_solid in paints.EFFECTS:
        fs = [Image.open(f).convert("RGBA") for f in sorted((OUT / name).glob("frame_*.png"))]
        assert len(fs) == n, f"{name}: expected {n} frames, found {len(fs)} (run make_fx.py {name})"
        box = None
        for f in fs:
            b = f.getbbox()
            if b:
                box = b if box is None else (min(box[0], b[0]), min(box[1], b[1]), max(box[2], b[2]), max(box[3], b[3]))
        box = box or (32, 32, 64, 64)
        color, level = LIGHT.get(name, (215, 2))
        manifest.append({"name": name, "id": eid, "first": len(frames), "frames": n, "ms": ms,
                         "box": [box[0], box[1], box[2] - box[0], box[3] - box[1]], "light": [level, color]})
        frames += fs
    cols = SHEET // 64
    sheets = []
    for s0 in range(0, len(frames), PER_SHEET):
        img = Image.new("RGBA", (SHEET, SHEET), (0, 0, 0, 0))
        for k, f in enumerate(frames[s0:s0 + PER_SHEET]):
            img.paste(f, ((k % cols) * 64, (k // cols) * 64))
        fname = f"sheet_{len(sheets)}.bmp.lzma"
        (GAME / fname).write_bytes(cip_sheet(img))
        sheets.append({"file": fname, "count": min(PER_SHEET, len(frames) - s0)})
    (GAME / "effects.json").write_text(json.dumps({"about": "Spirebound spell effects, made by art/effects/make_fx.py; installed by tools/install_effects.py",
                                                    "sheets": sheets, "effects": manifest}, indent=1))
    print(f"packed {len(frames)} frames into {len(sheets)} sheets")


def main(argv):
    wanted = set(argv)
    for name, eid, frames, ms, has_solid in paints.EFFECTS:
        if not wanted or name in wanted:
            make(name, eid, frames, ms, has_solid)
    overview()
    pack()


if __name__ == "__main__":
    main(sys.argv[1:])
