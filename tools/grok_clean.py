#!/usr/bin/env python3
"""Turn Grok's big item / spell-icon pictures into game-ready 32x32 sprites in Spirebound's style.

Jay (2026-11-27): Grok's first item batch came back thin, pale and flat next to the approved monsters. Grok is good
at big pictures and bad at tiny pixel art, so Grok draws big (512x512, one object on plain grey) and this script
does the pixel work the same way the creature pipeline does:

  1. cut the plain background and Grok's soft drop shadow away (flood fill from the edges; a transparent PNG is used as it is);
  2. split a picture with several objects into one sprite each (--split; small bits such as text labels are dropped);
  3. crop, then shrink to the sprite size with no blur (the object fills --fill pixels, default 28 of 32);
  4. boost colour and contrast, and light it from the top-left like every creature (art/pipeline/palette.json);
  4b. reduce each item to 12 flat colours and remove lone speckles (a shrunk painting is noisy);
  5. only with --palette: recolour with only colours taken from the approved sprites and spell effects (art/pipeline/item_palette.json,
     rebuilt with --rebuild-palette), so items match the monsters;
  6. a 1-px dark outline (the creatures' outline colour; dark brown on the lit top-left edge);
  7. a comparison sheet: Grok's original, the sprite at 4x, and the sprite at real size.

Usage:
    python tools/grok_clean.py                                  ART_FOR_JAY/grok_in  -> ART_FOR_JAY/grok_out
    python tools/grok_clean.py picture.png --split              a sheet with several items
    python tools/grok_clean.py IN_DIR OUT_DIR --size 64         a big (2x2 tile) object
    python tools/grok_clean.py ... --palette                    force the approved sprites' colours (Grok's own looked better in batch 14)
Outputs: <name>.png (the sprite), <name>_4x.png (a preview) and compare.png.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance
from scipy import ndimage

ROOT = Path(__file__).resolve().parent.parent
PIPE = ROOT / "art" / "pipeline"
PALETTE_FILE = PIPE / "item_palette.json"
OUTLINE = tuple(json.loads((PIPE / "palette.json").read_text())["shared"]["outline"])
SHEET_BG = (196, 194, 188)              # the plain grey every preview sheet uses (art/pipeline/pixelize.py BG)
EXTS = {".png", ".jpg", ".jpeg", ".webp"}


# ---------------------------------------------------------------- colour helpers
def to_lab(rgb):
    """sRGB (0-255, shape (..., 3)) to CIE Lab, so 'nearest colour' means nearest to the eye."""
    c = np.asarray(rgb, np.float64) / 255.0
    c = np.where(c > 0.04045, ((c + 0.055) / 1.055) ** 2.4, c / 12.92)
    m = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]])
    xyz = c @ m.T / np.array([0.9505, 1.0, 1.089])
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])], -1)


def build_palette(k=72):
    """Colours of every approved sprite sheet and spell effect, reduced to k by k-means (in Lab).
    Saved to art/pipeline/item_palette.json; rerun with --rebuild-palette after new art is approved."""
    names = [l.strip() for l in (ROOT / "art" / "APPROVED.txt").read_text().splitlines()
             if l.strip() and not l.startswith("#")]
    sheets = [ROOT / "art" / "output" / n / f"{n}_sheet.png" for n in names]
    sheets += sorted((ROOT / "art" / "effects" / "output").glob("*/*_sheet.png"))
    px = []
    for p in sheets:
        if not p.exists():
            continue
        a = np.asarray(Image.open(p).convert("RGBA")).reshape(-1, 4)
        a = a[a[:, 3] > 200][:, :3]
        a = a[np.abs(a.astype(int) - SHEET_BG).sum(1) > 12]       # drop the grey sheet background
        a = a[np.abs(a.astype(int) - OUTLINE).sum(1) > 12]        # the outline colour is added on its own
        px.append(a)
    if not px:
        sys.exit("No approved sheets found under art/output; cannot build the palette.")
    px = np.unique(np.concatenate(px), axis=0)
    lab = to_lab(px)
    rng = np.random.default_rng(1)
    cent = lab[rng.choice(len(lab), k, replace=False)]
    for _ in range(25):
        lbl = ((lab[:, None] - cent[None]) ** 2).sum(-1).argmin(1)
        for i in range(k):
            sel = lab[lbl == i]
            if len(sel):
                cent[i] = sel.mean(0)
    lbl = ((lab[:, None] - cent[None]) ** 2).sum(-1).argmin(1)
    cols = []
    for i in range(k):                     # use a real colour from the art, the one nearest each centre
        sel = np.where(lbl == i)[0]
        if len(sel):
            j = sel[((lab[sel] - cent[i]) ** 2).sum(-1).argmin()]
            cols.append([int(v) for v in px[j]])
    cols.sort(key=lambda c: (to_lab(c)[0]))
    PALETTE_FILE.write_text(json.dumps({"_about": "Colours for cleaned Grok item icons, taken from the approved "
                                        "sprites and spell effects by tools/grok_clean.py --rebuild-palette.",
                                        "colours": cols}, indent=1))
    print(f"palette: {len(cols)} colours from {sum(p.exists() for p in sheets)} sheets -> {PALETTE_FILE.relative_to(ROOT)}")
    return np.array(cols)


def load_palette():
    if not PALETTE_FILE.exists():
        return build_palette()
    return np.array(json.loads(PALETTE_FILE.read_text())["colours"])


# ---------------------------------------------------------------- cutting out
def foreground(img: Image.Image, tol: float) -> np.ndarray:
    """True where the object is. Uses real transparency when the PNG has it, else flood-fills the background
    colour (the median of the border) in from the picture's edges."""
    a = np.asarray(img.convert("RGBA"))
    if (a[..., 3] < 128).mean() > 0.05:
        return a[..., 3] >= 128
    rgb = a[..., :3].astype(np.float64)
    border = np.concatenate([rgb[0], rgb[-1], rgb[:, 0], rgb[:, -1]])
    bg = np.median(border, 0)
    lab, blab = to_lab(rgb), to_lab(bg)
    close = np.abs(lab - blab).sum(-1) < tol
    # Grok paints a soft grey drop shadow under each object (batch 14). It is colourless and lighter than Grok's
    # near-black outline, so colourless pixels down to L 30 also count as background when they touch it; the
    # outline stops the fill, so grey metal inside the object is kept.
    chroma = np.abs(lab[..., 1] - blab[1]) + np.abs(lab[..., 2] - blab[2])
    close |= (chroma < 9) & (lab[..., 0] > 30) & (lab[..., 0] < blab[0] + 8)
    lbl, _ = ndimage.label(close)
    edge = np.unique(np.concatenate([lbl[0], lbl[-1], lbl[:, 0], lbl[:, -1]]))
    bgmask = np.isin(lbl, edge[edge > 0])
    fg = ~bgmask
    return ndimage.binary_opening(fg, iterations=1)


def objects(img: Image.Image, fg: np.ndarray, split: bool):
    """Yield (box) for each object. With split, pieces close together count as one object; small pieces and short
    wide ones (text labels) are dropped."""
    h, w = fg.shape
    if not split:
        ys, xs = np.where(fg)
        if len(ys):
            yield (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)
        return
    gap = max(2, int(min(h, w) * 0.006))
    lbl, n = ndimage.label(ndimage.binary_dilation(fg, iterations=gap))
    boxes = []
    for sl in ndimage.find_objects(lbl):
        y0, y1, x0, x1 = sl[0].start, sl[0].stop, sl[1].start, sl[1].stop
        boxes.append((x0, y0, x1, y1, int(fg[sl].sum())))
    if not boxes:
        return
    big_h = max(b[3] - b[1] for b in boxes)
    big_a = max(b[4] for b in boxes)
    keep = [b for b in boxes if b[4] > big_a * 0.06 and (b[3] - b[1]) > big_h * 0.3]
    rowh = big_h * 0.6
    keep.sort(key=lambda b: (round(((b[1] + b[3]) / 2) / rowh), b[0]))
    for x0, y0, x1, y1, _ in keep:
        yield (x0, y0, x1, y1)


# ---------------------------------------------------------------- the pixel work
def shrink(img: Image.Image, fg: np.ndarray, box, size: int, fill: int) -> np.ndarray:
    x0, y0, x1, y1 = box
    a = np.asarray(img.convert("RGBA")).copy()
    a[..., 3] = np.where(fg, 255, 0)
    crop = Image.fromarray(a[y0:y1, x0:x1])
    s = fill / max(crop.size)
    nw, nh = max(1, round(crop.width * s)), max(1, round(crop.height * s))
    # Pillow premultiplies alpha when resizing RGBA, so the background never bleeds into the edge colours
    small = crop.resize((nw, nh), Image.Resampling.BOX)
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    canvas.paste(small, ((size - nw) // 2, size - nh - (size - fill) // 2), small)
    out = np.asarray(canvas).copy()
    out[..., 3] = np.where(out[..., 3] >= 110, 255, 0)
    return out


def punch(sprite: np.ndarray, sat: float, contrast: float) -> np.ndarray:
    """More colour and contrast, then light from the top-left (brighter up-left, darker down-right, a highlight
    on the lit edge and a shade on the far edge), like the creatures."""
    on = sprite[..., 3] > 0
    rgb = Image.fromarray(sprite[..., :3])
    rgb = ImageEnhance.Color(rgb).enhance(sat)
    rgb = ImageEnhance.Contrast(rgb).enhance(contrast)
    c = np.asarray(rgb).astype(np.float64)
    ys, xs = np.where(on)
    if not len(ys):
        return sprite
    cy, cx = ys.mean(), xs.mean()
    span = max(np.ptp(ys), np.ptp(xs), 1)
    yy, xx = np.mgrid[0:sprite.shape[0], 0:sprite.shape[1]]
    grad = 1.0 - 0.22 * (((yy - cy) + (xx - cx)) / span)         # +/- ~11 % across the object
    c *= grad[..., None]
    pad = np.pad(on, 1)
    lit = on & ~(pad[:-2, 1:-1] & pad[1:-1, :-2])                  # nothing above or nothing to the left
    far = on & ~(pad[2:, 1:-1] & pad[1:-1, 2:])                    # nothing below or nothing to the right
    c[lit] = c[lit] * 1.18 + 14
    c[far & ~lit] *= 0.78
    out = sprite.copy()
    out[..., :3] = np.clip(c, 0, 255).astype(np.uint8)
    return out


def simplify(sprite: np.ndarray, k: int) -> np.ndarray:
    """A shrunk painting is speckled (every pixel a slightly different colour). Hand-made pixel art uses a few flat
    colours, so: reduce the object to its k main colours (k-means in Lab), then replace lone pixels that match none
    of their four neighbours with the most common neighbour colour."""
    on = sprite[..., 3] > 0
    px = sprite[..., :3][on].astype(np.float64)
    if len(px) <= k:
        return sprite
    lab = to_lab(px)
    rng = np.random.default_rng(2)
    cent = lab[rng.choice(len(lab), k, replace=False)]
    for _ in range(15):
        lbl = ((lab[:, None] - cent[None]) ** 2).sum(-1).argmin(1)
        for i in range(k):
            if (lbl == i).any():
                cent[i] = lab[lbl == i].mean(0)
    means = np.array([px[lbl == i].mean(0) if (lbl == i).any() else [0, 0, 0] for i in range(k)])
    idx = np.full(on.shape, -1)
    idx[on] = lbl
    h, w = on.shape
    for y in range(h):
        for x in range(w):
            if idx[y, x] < 0:
                continue
            nb = [idx[y + dy, x + dx] for dy, dx in ((0, 1), (1, 0), (0, -1), (-1, 0))
                  if 0 <= y + dy < h and 0 <= x + dx < w and idx[y + dy, x + dx] >= 0]
            if len(nb) >= 3 and idx[y, x] not in nb:
                idx[y, x] = max(set(nb), key=nb.count)
    out = sprite.copy()
    out[..., :3][on] = np.clip(means[idx[on]], 0, 255).astype(np.uint8)
    return out


def recolour(sprite: np.ndarray, pal: np.ndarray) -> np.ndarray:
    on = sprite[..., 3] > 0
    lab = to_lab(sprite[..., :3][on])
    plab = to_lab(pal)
    idx = ((lab[:, None] - plab[None]) ** 2).sum(-1).argmin(1)
    out = sprite.copy()
    out[..., :3][on] = pal[idx]
    return out


def outline(sprite: np.ndarray) -> np.ndarray:
    """1-px outline in the creatures' outline colour; on the lit top/left side a dark shade of the neighbour's own
    colour instead (the 'lit-side outline' of art/pipeline/pixelize.py)."""
    on = sprite[..., 3] > 0
    h, w = on.shape
    out = sprite.copy()
    for y in range(h):
        for x in range(w):
            if on[y, x]:
                continue
            hit, lit = False, None
            for dy, dx in ((0, 1), (1, 0), (0, -1), (-1, 0)):
                yy, xx = y + dy, x + dx
                if 0 <= yy < h and 0 <= xx < w and on[yy, xx]:
                    hit = True
                    if (dy, dx) in ((1, 0), (0, 1)):                 # the object is below / right: lit side
                        nb = sprite[yy, xx, :3].astype(int)
                        if nb.sum() > 330:
                            lit = tuple(int(v * 0.42) for v in nb)
            if hit:
                out[y, x] = (*(lit or OUTLINE), 255)
    return out


# ---------------------------------------------------------------- sheet
def compare_sheet(rows, path: Path, size: int):
    """rows: (name, original crop RGBA image, sprite array). Original | 4x | 1x, on the usual grey."""
    big = size * 4
    cell_w, cell_h = big * 2 + size + 60, big + 26
    cols = 2 if len(rows) > 6 else 1
    nrows = (len(rows) + cols - 1) // cols
    sheet = Image.new("RGB", (cell_w * cols + 20, cell_h * nrows + 30), SHEET_BG)
    d = ImageDraw.Draw(sheet)
    d.text((10, 8), "Grok original  |  cleaned sprite 4x  |  real size", fill=(40, 34, 30))
    for i, (name, orig, spr) in enumerate(rows):
        ox, oy = 10 + (i % cols) * cell_w, 30 + (i // cols) * cell_h
        o = orig.copy()
        o.thumbnail((big, big))
        sheet.paste(o, (ox + (big - o.width) // 2, oy + (big - o.height) // 2), o)
        s = Image.fromarray(spr)
        s4 = s.resize((big, big), Image.Resampling.NEAREST)
        sheet.paste(s4, (ox + big + 20, oy), s4)
        sheet.paste(s, (ox + big * 2 + 40, oy + (big - size) // 2), s)
        d.text((ox, oy + big + 4), name, fill=(40, 34, 30))
    sheet.save(path)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("src", nargs="?", default=str(ROOT / "ART_FOR_JAY" / "grok_in"), help="a picture or a folder")
    ap.add_argument("out", nargs="?", default=str(ROOT / "ART_FOR_JAY" / "grok_out"))
    ap.add_argument("--size", type=int, default=32)
    ap.add_argument("--fill", type=int, default=None, help="pixels the object fills (default size - 4)")
    ap.add_argument("--split", action="store_true", help="a picture holds several objects")
    ap.add_argument("--tol", type=float, default=22, help="how far from the background colour still counts as background")
    ap.add_argument("--sat", type=float, default=1.35)
    ap.add_argument("--contrast", type=float, default=1.2)
    ap.add_argument("--colours", type=int, default=12, help="flat colours per item before recolouring")
    ap.add_argument("--palette", action="store_true", help="force the approved sprites' colours (off by default: batch 14 looked better in Grok's own)")
    ap.add_argument("--no-palette", action="store_true", help=argparse.SUPPRESS)
    ap.add_argument("--rebuild-palette", action="store_true")
    a = ap.parse_args()

    pal = build_palette() if a.rebuild_palette else (load_palette() if a.palette and not a.no_palette else None)
    src, out = Path(a.src), Path(a.out)
    files = [src] if src.is_file() else sorted(p for p in src.glob("*") if p.suffix.lower() in EXTS) if src.exists() else []
    if not files:
        if a.rebuild_palette:
            return
        sys.exit(f"No pictures found in {src}. Put Grok's images there (PNG/JPG), one object each or use --split.")
    out.mkdir(parents=True, exist_ok=True)
    fill = a.fill or a.size - 4
    rows = []
    for f in files:
        img = Image.open(f).convert("RGBA")
        fg = foreground(img, a.tol)
        boxes = list(objects(img, fg, a.split))
        for n, box in enumerate(boxes, 1):
            name = f.stem if len(boxes) == 1 else f"{f.stem}_{n:02d}"
            spr = shrink(img, fg, box, a.size, fill)
            spr = simplify(spr, a.colours)
            spr = punch(spr, a.sat, a.contrast)
            if pal is not None:
                spr = recolour(spr, pal)
            spr = outline(spr)
            Image.fromarray(spr).save(out / f"{name}.png")
            Image.fromarray(spr).resize((a.size * 4,) * 2, Image.Resampling.NEAREST).save(out / f"{name}_4x.png")
            x0, y0, x1, y1 = box
            crop = np.asarray(img).copy()
            crop[..., 3] = np.where(fg, 255, 0)
            rows.append((name, Image.fromarray(crop[y0:y1, x0:x1]), spr))
            print(f"  {name}.png")
    compare_sheet(rows, out / "compare.png", a.size)
    print(f"{len(rows)} sprite(s) -> {out}  (see compare.png)")


if __name__ == "__main__":
    main()
