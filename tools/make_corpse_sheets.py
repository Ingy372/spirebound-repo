#!/usr/bin/env python3
"""Dead bodies for our own monsters (art/CORPSE_RULES.md): finish the corpse renders and make the review sheet.

    sh art/pipeline/render.sh corpse_<monster>          the dead body (art/pipeline/corpse_kit.py)
    sh art/pipeline/render.sh corpse_<monster>_bones    its skeleton, in the same pose
    python tools/make_corpse_sheets.py                  art/output/corpse_<monster>/item/{1_fresh,2_rot,3_bones}.png
                                                        + ART_FOR_JAY/corpses_sheet.png (plain grey, for approval)

Tibia's own corpses (rules C1-C8) go: fresh body with wounds and a blood pool (Tibia shows it twice: the 10 s and
the first 300 s item), then rotting (duller, darker, the wounds opened and the ribs showing through), then the
skeleton in the same pose. The blood and rot are painted here in 2D, on top of the Blender render, the way a pixel
artist adds them to a finished body.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "art" / "output"
BG = (196, 194, 188)          # plain grey (Jay: sprite sheets on plain grey, never grass)

# monster model -> (shown as, view, kind). Only monsters with no fitting Tibia corpse get one (Jay, 2026-11-26:
# "corpses that already exist in tibia do not need to be re-drawn"). View: the render direction that reads best.
# kind: "pieces" = shatter/pile renders, frames 0-2 are the three steps (darken = colour kept at steps 2 and 3);
#       "flesh"  = a slumped body (+ corpse_<m>_bones render): blood, rot and bones are added here.
CORPSES = {
    "sentinel": ("Ruin Sentinel / Granite Warden", "S", "pieces", (1.0, 0.92)),
    "underkeeper": ("The Underkeeper", "S", "pieces", (0.88, 0.78)),
    "vault_wraith": ("Vault Wraith", "E", "pieces", (0.85, 0.72)),
    # Tibia's dead hellhound has three heads too, but it is red, yellow and green; ours is slate-blue (Jay, 2026-11-26)
    "gate_hound": ("Gate Hound", "W", "flesh", None),
}

# blood (C4): Tibia's corpse blood is a deep red with a brighter wet line, never orange
BLOOD = [(70, 8, 8), (112, 14, 12), (150, 24, 20), (186, 44, 36)]


def body_mask(a: np.ndarray) -> np.ndarray:
    return a[..., 3] > 0


def wounds(img: np.ndarray, rng, n=3, length=4, open_=False) -> np.ndarray:
    """C4: short diagonal gashes on the upper flank (inside the body, away from its outline)"""
    out = img.copy()
    m = body_mask(img)
    ys, xs = np.nonzero(m)
    if not len(xs):
        return out
    x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    inner = m & np.roll(m, 1, 0) & np.roll(m, -1, 0) & np.roll(m, 1, 1) & np.roll(m, -1, 1)
    inner &= np.roll(inner, 1, 0) & np.roll(inner, -1, 0)
    cx = x0 + (x1 - x0) * 0.55
    for k in range(n):
        for _try in range(40):
            x = int(rng.uniform(cx - (x1 - x0) * 0.3, cx + (x1 - x0) * 0.25))
            y = int(rng.uniform(y0 + (y1 - y0) * 0.2, y0 + (y1 - y0) * 0.6))
            if inner[y, x]:
                break
        else:
            continue
        for i in range(length + (2 if open_ else 0)):
            px, py = x + i, y - i // 2
            if 0 <= py < 64 and 0 <= px < 64 and inner[py, px]:
                out[py, px, :3] = BLOOD[2]
                if py + 1 < 64 and inner[py + 1, px]:
                    out[py + 1, px, :3] = BLOOD[0] if not open_ else BLOOD[1]
                if open_ and py + 2 < 64 and inner[py + 2, px]:
                    out[py + 2, px, :3] = BLOOD[0]
                if i % 2 == 0 and py - 1 >= 0 and inner[py - 1, px]:
                    out[py - 1, px, :3] = BLOOD[3]
    return out


def pool(img: np.ndarray, rng, size=1.0, dry=False) -> np.ndarray:
    """C4: a small pool of blood on the ground under the head end (left), drawn behind the body"""
    m = body_mask(img)
    ys, xs = np.nonzero(m)
    x0, x1, y1 = xs.min(), xs.max(), ys.max()
    w = max(6, int((x1 - x0) * 0.42 * size))
    h = max(3, w // 3)
    cx, cy = x0 + w // 2 + 1, y1 - h // 2
    layer = Image.new("RGBA", (64, 64))
    d = ImageDraw.Draw(layer)
    c0, c1, c2 = (BLOOD[0], BLOOD[1], BLOOD[2]) if not dry else ((52, 10, 8), (70, 16, 12), (84, 22, 16))
    d.ellipse([cx - w // 2, cy - h // 2, cx + w // 2, cy + h // 2], fill=c0 + (255,))
    d.ellipse([cx - w // 2 + 1, cy - h // 2 + 1, cx + w // 2 - 1, cy + h // 2 - 1], fill=c1 + (255,))
    d.ellipse([cx - w // 4, cy - h // 4, cx, cy], fill=c2 + (255,))
    # a couple of drips beside the pool, so it is not a perfect ellipse
    for _ in range(2):
        dx, dy = int(rng.uniform(-w * 0.7, w * 0.7)), int(rng.uniform(-h, h))
        d.rectangle([cx + dx, cy + dy, cx + dx + 1, cy + dy], fill=c1 + (255,))
    base = layer
    base.alpha_composite(Image.fromarray(img, "RGBA"))
    return np.asarray(base).copy()


def decay(img: np.ndarray, grey: float, dark: float) -> np.ndarray:
    """C5: rot greys the colours toward a dull green-brown and darkens them; blood turns dark brown-red"""
    a = img.astype(float)
    rgb = a[..., :3]
    lum = rgb @ np.array([0.30, 0.59, 0.11])
    tint = np.stack([lum * 1.02, lum * 1.0, lum * 0.82], -1)
    out = (rgb * (1 - grey) + tint * grey) * dark
    a[..., :3] = np.clip(out, 0, 255)
    return a.astype(np.uint8)


def ribs_through(body: np.ndarray, bones: np.ndarray, rng) -> np.ndarray:
    """C5: an opened flank on the rotting body: a dark-red hole with the skeleton's ribs showing in it"""
    out = body.copy()
    m = body_mask(body)
    ys, xs = np.nonzero(m)
    x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    cx, cy = x0 + (x1 - x0) * 0.56, y0 + (y1 - y0) * 0.42
    rx, ry = (x1 - x0) * 0.17, (y1 - y0) * 0.17
    yy, xx = np.mgrid[0:64, 0:64]
    hole = ((xx - cx) / max(rx, 1)) ** 2 + ((yy - cy) / max(ry, 1)) ** 2 <= 1
    noise = rng.random((64, 64)) < 0.18
    edge = hole & ~(((xx - cx) / max(rx - 1, 1)) ** 2 + ((yy - cy) / max(ry - 1, 1)) ** 2 <= 1)
    hole &= m
    out[hole, :3] = BLOOD[0]
    out[edge & m & ~noise, :3] = BLOOD[1]
    bone = body_mask(bones) & hole & (bones[..., :3].sum(-1) > 330)
    out[bone, :3] = (bones[bone, :3].astype(float) * 0.82).astype(np.uint8)
    return out


def steps(name: str) -> list[Image.Image]:
    _label, d, kind, darken = CORPSES[name]
    fr = OUT / f"corpse_{name}" / "frames"
    load = lambda f: np.asarray(Image.open(fr / f"{d}_{f}.png").convert("RGBA")).copy()
    if kind == "pieces":
        out = [load(0), decay(load(1), 0.25, darken[0]), decay(load(2), 0.4, darken[1])]
        return [Image.fromarray(a, "RGBA") for a in out]
    rng = np.random.default_rng(sum(map(ord, name)))
    body = load(0)
    bones = np.asarray(Image.open(OUT / f"corpse_{name}_bones" / "frames" / f"{d}_0.png").convert("RGBA")).copy()
    fresh = pool(wounds(body, rng), rng)
    rot_body = ribs_through(decay(wounds(body, np.random.default_rng(7), n=4, length=5, open_=True), 0.5, 0.78),
                            bones, rng)
    rot = pool(rot_body, rng, size=1.15, dry=True)
    return [Image.fromarray(fresh, "RGBA"), Image.fromarray(rot, "RGBA"), Image.fromarray(bones, "RGBA")]


def board(names, cell=128, refs=None) -> Image.Image:
    cols, head, lab = 1, 34, 16
    rows = (len(names) + cols - 1) // cols
    W, H = cols * 4 * cell + (cols - 1) * 24 + 16, head + rows * (cell + lab + 8) + 8
    sheet = Image.new("RGB", (W, H), BG)
    dr = ImageDraw.Draw(sheet)
    dr.text((8, 8), "Corpses (2x): living monster | 1 fresh | 2 older | 3 last remains   -   plain grey", fill=(30, 30, 30))
    for i, n in enumerate(names):
        imgs = steps(n)
        item = OUT / f"corpse_{n}" / "item"
        item.mkdir(parents=True, exist_ok=True)
        for im, tag in zip(imgs, ("1_fresh", "2_rot", "3_end")):
            im.save(item / f"{tag}.png")
        alive = OUT / n / "frames" / "S_0.png"
        row = [Image.open(alive).convert("RGBA") if alive.exists() else Image.new("RGBA", (64, 64))] + imgs
        x0 = 8 + (i % cols) * (4 * cell + 24)
        y0 = head + (i // cols) * (cell + lab + 8)
        dr.text((x0, y0), CORPSES[n][0], fill=(30, 30, 30))
        for k, im in enumerate(row):
            big = im.resize((cell, cell), Image.NEAREST)
            sheet.paste(big, (x0 + k * cell, y0 + lab), big)
    return sheet


def main() -> None:
    names = [n for n in CORPSES if (OUT / f"corpse_{n}" / "frames").exists()]
    dest = ROOT / "ART_FOR_JAY" / "corpses_sheet.png"
    board(names).save(dest)
    print(f"make_corpse_sheets: {len(names)} corpses -> {dest}")


if __name__ == "__main__":
    main()
