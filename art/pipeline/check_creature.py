#!/usr/bin/env python3
"""Automatic quality check for a finished creature sprite (run after render.sh; normal Python).

  python art/pipeline/check_creature.py boar

It measures the things that made the first monster drafts look weak, and prints PASS / FAIL for each with the
number it found and what to change. A creature is not ready to show Jay until every line passes
(art/QUADRUPED_RULES.md explains each rule). It cannot judge taste: after it passes, still LOOK at the sheet.

Optional settings in the model file:
  SIGNATURE = ["crest", "tusk"]   parts that make this creature ours; they must show from all four directions
  CHECK = {"size": (0.8, 1.2)}    override a limit (see LIMITS below)
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pixelize  # noqa: E402

ROOT = HERE.parent.parent
LIMITS = {
    "size": (0.85, 1.20),      # our longest side / the Tibia look-alike's longest side (east view)
    "tones": 14,               # distinct colours in the east standing frame (flat sprites have under 10)
    "contrast": 75,            # brightness spread (5th to 95th percentile, 0..255) inside the sprite
    "different": 0.35,         # share of our pixels whose colour is nowhere in the look-alike's sprite
    "legs_side": 0.06,         # share of the sprite that is legs/feet, east and west views
    "legs_updown": 0.03,       # ...and north and south views (feet must be planted outside the body)
    "head": 0.10,              # share of the sprite that is head+snout, east and west views
    "eye": 2,                  # eye pixels in the south, east and west views
    "signature": 5,            # pixels of each SIGNATURE part, in every direction
    "walk": 0.06,              # share of pixels that change between neighbouring walk frames
    "grass": 0.60,             # share of the sprite whose colour is clearly unlike the grass it walks on
}
LEG_PARTS = {"leg_near", "leg_far", "paw_near", "paw_far", "leg", "foot", "claw"}
HEAD_PARTS = {"head", "snout", "nose", "beak"}
# A model file may set LEG_PARTS / HEAD_PARTS (lists of its own part names) when its parts are named differently;
# LEG_PARTS = [] means it has no legs (a vine, a floating crystal) and skips the leg checks.


def model_attrs(name):
    """Read SIGNATURE / CHECK from the model file without importing Blender."""
    src = (ROOT / "art" / "models" / f"{name}.py").read_text(encoding="utf-8")
    out = {}
    for key in ("SIGNATURE", "CHECK", "LEG_PARTS", "HEAD_PARTS"):
        for line in src.splitlines():
            if line.startswith(f"{key} ="):
                out[key] = eval(line.split("=", 1)[1].split("#")[0].strip())   # noqa: S307 (our own file)
    return out


def lum(rgb):
    return 0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2]


def main(name):
    c = pixelize.Creature(name)
    attrs = model_attrs(name)
    lim = {**LIMITS, **attrs.get("CHECK", {})}
    fr = {(d, f): np.array(Image.open(c.dir / "frames" / f"{d}_{f}.png").convert("RGBA"))
          for d in "NESW" for f in range(c.n_frames)}
    results = []

    def report(ok, label, found, fix):
        results.append(ok)
        print(f"  {'PASS' if ok else 'FAIL'}  {label}: {found}" + ("" if ok else f"\n        -> {fix}"))

    # 1. nothing cut off
    cut = [f"{d}{f}" for (d, f), a in fr.items() if a[0, :, 3].any() or a[:, 0, 3].any()]
    report(not cut, "fits the canvas", "all frames clear of the top/left edge" if not cut else f"cut off in {cut[:6]}",
           "lower SIZE or GROUND_STRETCH, or use AUTO_PLACE = (1, 1)")

    # 2. size against the look-alike
    ref = pixelize.load_refs(c.meta.get("ref"))
    east = fr["E", 0]
    ys, xs = np.nonzero(east[..., 3])
    ours = max(xs.max() - xs.min(), ys.max() - ys.min()) + 1
    if ref:
        r = np.array(ref["E"][0])
        ry, rx = np.nonzero(r[..., 3])
        theirs = max(rx.max() - rx.min(), ry.max() - ry.min()) + 1
        ratio = ours / theirs
        report(lim["size"][0] <= ratio <= lim["size"][1], "size vs the Tibia look-alike",
               f"{ours}px vs {theirs}px ({ratio:.2f}x)", f"change SIZE so the ratio is {lim['size'][0]}-{lim['size'][1]}")
        # 3. obviously our own colours
        mine = east[..., :3][east[..., 3] > 0].astype(float)
        mine = mine[lum(mine) >= 50]          # near-black shadows and outlines are shared by every sprite
        other = np.unique(r[..., :3][r[..., 3] > 0], axis=0).astype(float)
        nearest = np.sqrt(((mine[:, None, :] - other[None, :, :]) ** 2).sum(-1)).min(1)
        own = float((nearest > 20).mean())
        report(own >= lim["different"], "obviously not the Tibia sprite (share of colours Tibia's lacks)", f"{own:.0%}",
               "pick a different coat colour family and add a signature feature Tibia's version lacks")
    else:
        print("  ----  no look-alike set (REFERENCE): size and identity not checked")

    # 4. shading depth
    px = east[..., :3][east[..., 3] > 0]
    tones = len({tuple(p) for p in px})
    report(tones >= lim["tones"], "shading tones", tones, "use 8-colour ramps with PIXEL_RULES['bands'] and texture")
    lo, hi = np.percentile(lum(px.astype(float)), [5, 95])
    report(hi - lo >= lim["contrast"], "light-to-dark contrast", f"{hi - lo:.0f}",
           "widen the ramps (darker darks, lighter lights); dark coats need lighter top tones")

    # 5. parts that must be visible, from the part maps
    sig = attrs.get("SIGNATURE", [])
    for d in "SENW":
        part, _v, _dep = c.shrink(*c.load(d, 0))
        total = max(int((part > 0).sum()), 1)
        count = lambda names: int(sum((part == c.parts.index(n)).sum() for n in names if n in c.parts))
        leg_parts = attrs.get("LEG_PARTS", LEG_PARTS)
        if leg_parts:
            legs = count(leg_parts) / total
            need = lim["legs_side"] if d in "EW" else lim["legs_updown"]
            report(legs >= need, f"legs show, facing {d}", f"{legs:.0%} of the sprite",
                   "plant the feet wider than the body (feet_y), raise the body, or thicken the legs")
        if d in "EW":
            head = count(attrs.get("HEAD_PARTS", HEAD_PARTS)) / total
            report(head >= lim["head"], f"head is big enough, facing {d}", f"{head:.0%}",
                   "enlarge the head and snout; a head under a tenth of the sprite reads as a blob")
        if d != "N" and "eye" in c.parts:
            eyes = count(["eye"])
            report(eyes >= lim["eye"], f"eyes show, facing {d}", f"{eyes}px",
                   "eyes must sit ON the head surface (quadruped.on_surface) with weight 9 and a bright colour")
        for s in sig:
            n = count([s])
            report(n >= lim["signature"], f"signature '{s}' shows, facing {d}", f"{n}px",
                   "make it bigger or move it where the camera sees it (top or outer side)")

    # 6. stands out on grass (green creatures vanish into the meadow)
    gp = ROOT / ".local" / "artref" / "ground.png"
    if gp.exists():
        grass = np.unique(np.array(Image.open(gp).convert("RGB")).reshape(-1, 3), axis=0).astype(float)
        for d in "SENW":
            a = fr[d, 0]
            px = a[..., :3][a[..., 3] > 0].astype(float)
            apart = float((np.sqrt(((px[:, None, :] - grass[None, :, :]) ** 2).sum(-1)).min(1) > 30).mean())
            report(apart >= lim["grass"], f"stands out on grass, facing {d}", f"{apart:.0%} unlike grass",
                   "move the main colour away from mid green: darker, browner, bluer or yellower, or a bright accent")

    # 7. the walk actually moves
    for d in "SE":
        ch = []
        for f in range(1, c.n_frames):
            a, b = fr[d, f], fr[d, f % (c.n_frames - 1) + 1]
            filled = (a[..., 3] > 0) | (b[..., 3] > 0)
            ch.append((np.any(a != b, axis=-1) & filled).sum() / max(filled.sum(), 1))
        report(min(ch) >= lim["walk"], f"walk moves, facing {d}", f"least change {min(ch):.0%} per frame",
               "bigger stride/lift, more body bob, or moving extras (crest, tail, ears)")

    bad = results.count(False)
    print(f"{name}: {'ALL PASS' if not bad else str(bad) + ' FAILED'} ({len(results)} checks)")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "boar"))
