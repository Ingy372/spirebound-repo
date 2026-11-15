#!/usr/bin/env python3
"""Turn a creature's raw Blender passes into finished pixel-art sprites (normal Python + Pillow + numpy).

  python art/pipeline/pixelize.py rat

Reads  art/output/<name>/passes/*.png and meta.json (written by render_creature.py)
Writes art/output/<name>/frames/<dir>_<frame>.png   64x64, client layout (frame 0 = standing, 1..8 = walk)
       art/output/<name>/<name>_sheet.png            all frames at 4x, rows S/E/N/W
       art/output/<name>/walk_<dir>.gif (1x) and walk_<dir>_4x.gif
       art/output/<name>/compare/...                 the same beside the reference sprites (git-ignored, never shipped)

The cleanup rules (same for every creature):
  1. Shrink 4x -> 1x by "who owns most of this pixel", with small important parts (eye, nose, tail) winning ties,
     so a 1-pixel tail or eye never disappears.
  2. Light every pixel from the surface direction and snap it to the part's palette ramp (3-4 clean steps).
  3. Remove lone speckles (a pixel whose step matches none of its neighbours), then add sparse fur tufts
     along the edges between light steps (rule-based, so they are tidy, not noise).
  4. Dark 1-px outline around the whole silhouette (dark brown instead of near-black on the lit top/left edge); a dark line where a part sits behind another (legs read apart).
  5. The thin end of a tail is drawn as a dark line with no extra outline, like hand-made sprites.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
ART = HERE.parent
ROOT = ART.parent
PALETTE = json.loads((HERE / "palette.json").read_text())
SHEET_ROWS = ["S", "E", "N", "W"]            # contact sheet order Jay asked for
BG = (196, 194, 188)                          # plain light grey: the dark outline and legs read clearly on it
GIF_MS = 110

MIN_COVER = 6                                 # of 16 sub-pixels, to count as filled
SELOUT_STEP = 3
DEPTH_LINE = 0.045                            # tiles; a bigger step between neighbours draws a dark line
# Per-creature rules come from PIXEL_RULES in the model file (via meta.json):
#   weight   part -> how strongly a small part wins a shared pixel (eyes, tails...)
#   thin     part -> sub-pixels (of 16) enough for that part alone to fill a pixel
#   soft     groups of parts with no dark depth line between them (one smooth surface)
#   no_outline, fur, selout   parts drawn without outline / with fur tufts / with the lit-side outline
RULE_DEFAULTS = {"weight": {}, "thin": {}, "soft": [], "no_outline": [], "fur": [], "selout": []}


def srgb_to_lin(a):
    a = a.astype(np.float64) / 255.0
    return np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4)


class Creature:
    def __init__(self, name):
        self.name = name
        self.dir = ART / "output" / name
        self.meta = json.loads((self.dir / "meta.json").read_text())
        self.parts = self.meta["parts"]
        self.ramps = {k: [tuple(c) for c in v] for k, v in PALETTE["ramps"][self.meta["palette"]].items()}
        self.ss = self.meta["supersample"]
        self.n_frames = self.meta["walk_frames"] + 1
        r = {**RULE_DEFAULTS, **self.meta.get("rules", {})}
        self.weight, self.thin = r["weight"], r["thin"]
        self.soft = [set(g) for g in r["soft"]]
        self.no_outline, self.fur_parts, self.selout = set(r["no_outline"]), set(r["fur"]), set(r["selout"])

    def is_soft(self, a, b):
        return any(a in g and b in g for g in self.soft)

    # ------------------------------------------------------------ one frame
    def load(self, d, f):
        p = self.dir / "passes"
        idp = np.array(Image.open(p / f"{d}_{f}_id.png"))
        nrm = np.array(Image.open(p / f"{d}_{f}_normal.png"))
        dep = np.array(Image.open(p / f"{d}_{f}_depth.png"))
        alpha = idp[..., 3] > 127
        ids = np.rint(srgb_to_lin(idp[..., 0]) * 255 / 8).astype(int)
        ids[~alpha] = 0
        n = srgb_to_lin(nrm[..., :3]) * 2 - 1
        M = np.array(self.meta.get("world_linear", [[1, 0, 0], [0, self.meta["y_stretch"], 0], [0, 0, 1]]))
        n = n @ M                                    # n_real ~ M^T n_seen: undo the stretch and lean for lighting
        n /= np.maximum(np.linalg.norm(n, axis=-1, keepdims=True), 1e-6)
        depth = srgb_to_lin(dep[..., 0]) * self.meta["depth_range"]
        light = PALETTE["light"]
        L = np.array(light["direction"], float); L /= np.linalg.norm(L)
        lam = np.clip(n @ L, 0, 1)
        tb = light["top_bias"]
        value = (1 - tb) * lam + tb * (0.5 + 0.5 * n[..., 2])
        return ids, value, depth

    def shrink(self, ids, value, depth):
        s = self.ss
        h, w = ids.shape[0] // s, ids.shape[1] // s
        blocks = lambda a: a[:h * s, :w * s].reshape(h, s, w, s).swapaxes(1, 2).reshape(h, w, s * s)
        bid, bval, bdep = blocks(ids), blocks(value), blocks(depth)
        npart = len(self.parts)
        cnt = np.stack([(bid == k).sum(-1) for k in range(npart)], -1)
        wts = np.array([0.0] + [self.weight.get(p, 1.0) for p in self.parts[1:]])
        score = cnt * wts
        part = score.argmax(-1)
        total = cnt[..., 1:].sum(-1)
        need = np.array([99] + [self.thin.get(p, MIN_COVER) for p in self.parts[1:]])
        own = np.take_along_axis(cnt, part[..., None], -1)[..., 0]
        filled = (total >= MIN_COVER) | (own >= need[part])
        part = np.where(filled & (score.max(-1) > 0), part, 0)
        mask = bid == part[..., None]
        k = np.maximum(mask.sum(-1), 1)
        val = (bval * mask).sum(-1) / k
        dep = (bdep * mask).sum(-1) / k
        return part, val, dep

    def paint(self, part, val, dep):
        h, w = part.shape
        bands = np.array(PALETTE["light"]["bands"])
        step = (val[..., None] > bands).sum(-1)
        step = self.despeckle(part, step)
        step = self.fur(part, step)
        name = lambda k: self.parts[k]
        out = np.zeros((h, w, 4), np.uint8)
        outline = PALETTE["shared"]["outline"]
        line = np.zeros((h, w), bool)
        for y in range(h):
            for x in range(w):
                k = part[y, x]
                if not k:
                    continue
                pn = name(k)
                if pn == "eye":
                    continue
                for dy, dx in ((0, 1), (1, 0), (0, -1), (-1, 0)):
                    yy, xx = y + dy, x + dx
                    if not (0 <= yy < h and 0 <= xx < w):
                        continue
                    q = part[yy, xx]
                    if not q or q == k:
                        continue
                    qn = name(q)
                    if self.is_soft(pn, qn):
                        continue
                    if pn == "tail_tip" or qn == "eye":
                        continue
                    if dep[y, x] > dep[yy, xx] + DEPTH_LINE:
                        line[y, x] = True
        for y in range(h):
            for x in range(w):
                k = part[y, x]
                if k:
                    ramp = self.ramps[name(k)]
                    c = outline if line[y, x] else ramp[min(step[y, x], len(ramp) - 1)]
                    out[y, x] = (*c, 255)
                    continue
                lit = None
                hit = False
                for dy, dx in ((0, 1), (1, 0), (0, -1), (-1, 0)):
                    yy, xx = y + dy, x + dx
                    if 0 <= yy < h and 0 <= xx < w and part[yy, xx] and name(part[yy, xx]) not in self.no_outline:
                        hit = True
                        # lit-side outline: on the top/left edge of a brightly lit fur area the outline is a
                        # dark brown (the part's darkest step) instead of near-black, like hand-made sprites
                        pn = name(part[yy, xx])
                        if (dy, dx) in ((1, 0), (0, 1)) and pn in self.selout and step[yy, xx] >= SELOUT_STEP \
                                and not line[yy, xx]:
                            lit = self.ramps[pn][0]
                if hit:
                    out[y, x] = (*(lit or outline), 255)
        return out

    def fur(self, part, step):
        """A few hand-placed-looking fur hints: where a lighter step sits just above a darker one on fur parts,
        every fourth pixel along that edge pokes 1 px down into the darker area (a tuft), never isolated noise."""
        h, w = part.shape
        s2 = step.copy()
        fur_ids = {self.parts.index(p) for p in self.fur_parts if p in self.parts}
        for y in range(1, h - 1):
            for x in range(w):
                k = part[y, x]
                if k not in fur_ids or part[y - 1, x] != k or part[y + 1, x] != k:
                    continue
                if step[y - 1, x] == step[y, x] + 1 and (x * 3 + y) % 4 == 0:
                    s2[y, x] = step[y - 1, x]
        return s2

    def despeckle(self, part, step):
        h, w = part.shape
        s2 = step.copy()
        for y in range(h):
            for x in range(w):
                k = part[y, x]
                if not k:
                    continue
                same, other = 0, {}
                for dy, dx in ((0, 1), (1, 0), (0, -1), (-1, 0)):
                    yy, xx = y + dy, x + dx
                    if 0 <= yy < h and 0 <= xx < w and part[yy, xx] == k:
                        if step[yy, xx] == step[y, x]:
                            same += 1
                        else:
                            other[step[yy, xx]] = other.get(step[yy, xx], 0) + 1
                if same == 0 and other:
                    b, c = max(other.items(), key=lambda kv: kv[1])
                    if c >= 2:
                        s2[y, x] = b
        return s2

    def frame(self, d, f):
        """A finished 64x64 frame in the client's layout (the creature's tile is the bottom-right quarter)."""
        img = self.paint(*self.shrink(*self.load(d, f)))
        dx, dy = self.meta.get("canvas_offset", [0, 0])
        if dx or dy:                                  # standing figures sit low-right on the canvas, like Tibia's
            shifted = np.zeros_like(img)
            shifted[max(dy, 0):img.shape[0] + min(dy, 0), max(dx, 0):img.shape[1] + min(dx, 0)] =                 img[max(-dy, 0):img.shape[0] - max(dy, 0), max(-dx, 0):img.shape[1] - max(dx, 0)]
            img = shifted
        a = img[..., 3]
        if a[0].any() or a[:, 0].any() or a[-1].any() or a[:, -1].any():
            print(f"  warning: {d}{f} touches the edge of the 64x64 canvas")
        return Image.fromarray(img)

    # ------------------------------------------------------------ outputs
    def run(self):
        fdir = self.dir / "frames"
        fdir.mkdir(exist_ok=True)
        self.frames = {}
        for d in self.meta["order"]:
            for f in range(self.n_frames):
                im = self.frame(d, f)
                im.save(fdir / f"{d}_{f}.png")
                self.frames[d, f] = im
        # show just the creature's own tile when everything fits in it (small animals), else the whole canvas
        boxes = [im.getbbox() for im in self.frames.values() if im.getbbox()]
        fits = all(b[0] >= 32 and b[1] >= 32 for b in boxes)
        self.view = (32, 32, 64, 64) if fits else (0, 0, 64, 64)
        self.vsize = self.view[2] - self.view[0]
        self.zoom = 4 if fits else 3
        self.sheet(self.dir / f"{self.name}_sheet.png")
        for d in SHEET_ROWS:
            self.gif(d, self.dir / f"walk_{d}.gif", 1)
            self.gif(d, self.dir / f"walk_{d}_4x.gif", 4)
        refs = load_refs(self.meta.get("ref"))
        if refs:
            self.compare(refs)
        print(f"wrote {self.dir}")

    def backdrop(self, ground=None):
        n = self.vsize
        if ground is None:
            return Image.new("RGBA", (n, n), (*BG, 255))
        bg = Image.new("RGBA", (n, n))
        for x in range(0, n, 32):
            for y in range(0, n, 32):
                bg.paste(ground, (x, y))
        return bg

    def cell(self, sprite, zoom, ground=None):
        bg = self.backdrop(ground)
        bg.alpha_composite(sprite.crop(self.view))
        return bg.resize((self.vsize * zoom, self.vsize * zoom), Image.NEAREST)

    def sheet(self, path, refs=None, ground=None):
        zoom = self.zoom
        cell = self.vsize * zoom
        pad = 6
        cols = self.n_frames
        width = cols * (cell + pad) + 40
        if refs:
            width += 30 + refs["cols"] * (cell + pad)
        img = Image.new("RGB", (width, 4 * (cell + pad) + 34), (40, 44, 40))
        dr = ImageDraw.Draw(img)
        dr.text((40, 6), f"{self.name}: stand + {cols - 1} walk frames, {zoom}x", fill=(230, 230, 220))
        if refs:
            dr.text((40 + cols * (cell + pad) + 30, 6), "REFERENCE ONLY (Tibia, not shipped)", fill=(255, 190, 120))
        for r, d in enumerate(SHEET_ROWS):
            y = 26 + r * (cell + pad)
            dr.text((12, y + cell // 2 - 6), d, fill=(230, 230, 220))
            for f in range(cols):
                img.paste(self.cell(self.frames[d, f], zoom, ground), (40 + f * (cell + pad), y))
            if refs:
                for f, im in enumerate(refs[d]):
                    img.paste(self.cell(im, zoom, ground), (40 + cols * (cell + pad) + 30 + f * (cell + pad), y))
        img.save(path)

    def gif(self, d, path, zoom):
        frames = [self.cell(self.frames[d, f], zoom).convert("RGB") for f in range(1, self.n_frames)]
        frames[0].save(path, save_all=True, append_images=frames[1:], duration=GIF_MS, loop=0)

    def compare(self, refs):
        cdir = self.dir / "compare"
        cdir.mkdir(exist_ok=True)
        ground = refs.get("ground")
        self.sheet(cdir / f"{self.name}_vs_refs.png", refs)
        if ground is not None:
            self.sheet(cdir / f"{self.name}_vs_refs_ground.png", refs, ground=ground)
        # side-by-side walk loops on plain grey: ours | reference, for each direction
        n = self.vsize
        for zoom in (1, 3):
            frames = []
            for i in range(1, self.n_frames):
                img = Image.new("RGBA", (4 * 2 * (n + 2) * zoom, (n + 2) * zoom), (40, 44, 40, 255))
                for r, d in enumerate(SHEET_ROWS):
                    for j, spr in enumerate((self.frames[d, i], refs[d][min(i, len(refs[d]) - 1)])):
                        img.paste(self.cell(spr, zoom), ((r * 2 + j) * (n + 2) * zoom, zoom))
                frames.append(img.convert("RGB"))
            frames[0].save(cdir / f"walk_ours_vs_ref_{zoom}x.gif", save_all=True, append_images=frames[1:],
                           duration=GIF_MS, loop=0)


def load_refs(name):
    """Reference frames pulled from the Tibia client files on this PC (tools/art_refs.py): rows N/E/S/W,
    columns stand + 8 walk, 64x64 cells. Comparison only; .local/ is never committed."""
    if not name:
        return None
    p = ROOT / ".local" / "artref" / name
    if not p.exists():
        return None
    im = Image.open(p).convert("RGBA")
    refs = {"cols": 9}
    for r, d in enumerate(["N", "E", "S", "W"]):
        refs[d] = [im.crop((f * 64, r * 64, f * 64 + 64, r * 64 + 64)) for f in range(9)]
    g = ROOT / ".local" / "artref" / "ground.png"
    if g.exists():
        refs["ground"] = Image.open(g).convert("RGBA")
    return refs


if __name__ == "__main__":
    Creature(sys.argv[1] if len(sys.argv) > 1 else "rat").run()
