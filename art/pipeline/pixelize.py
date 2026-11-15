#!/usr/bin/env python3
"""Turn a creature's raw Blender passes into finished pixel-art sprites (normal Python + Pillow + numpy).

  python art/pipeline/pixelize.py rat

Reads  art/output/<name>/passes/*.png and meta.json (written by render_creature.py)
Writes art/output/<name>/frames/<dir>_<frame>.png   32x32 tiles (frame 0 = standing, 1..8 = walk)
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

WEIGHT = {"eye": 9.0, "nose": 4.0, "tail_tip": 5.0, "tail_base": 2.5, "paw_near": 2.2, "paw_far": 1.6,
          "leg_near": 1.7, "leg_far": 1.2, "ear": 2.2, "snout": 1.3}
MIN_COVER = 6                                 # of 16 sub-pixels, to count as filled
MIN_COVER_THIN = {"eye": 3, "tail_tip": 2, "tail_base": 3, "nose": 3, "leg_near": 4, "leg_far": 4,
                  "paw_near": 3, "paw_far": 4, "ear": 4}
SOFT_PARTS = {"body", "head", "snout", "nose", "ear"}   # no depth lines between these (one smooth animal)
NO_OUTLINE = {"tail_tip"}
FUR_PARTS = ("body", "head")
SELOUT_PARTS = {"body", "head", "snout", "ear"}
SELOUT_STEP = 3
DEPTH_LINE = 0.045                            # tiles; a bigger step between neighbours draws a dark line


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
        n[..., 1] *= self.meta["y_stretch"]        # undo the oblique stretch so light hits the real shape
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
        wts = np.array([0.0] + [WEIGHT.get(p, 1.0) for p in self.parts[1:]])
        score = cnt * wts
        part = score.argmax(-1)
        total = cnt[..., 1:].sum(-1)
        need = np.array([99] + [MIN_COVER_THIN.get(p, MIN_COVER) for p in self.parts[1:]])
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
                    if pn in SOFT_PARTS and qn in SOFT_PARTS:
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
                    if 0 <= yy < h and 0 <= xx < w and part[yy, xx] and name(part[yy, xx]) not in NO_OUTLINE:
                        hit = True
                        # lit-side outline: on the top/left edge of a brightly lit fur area the outline is a
                        # dark brown (the part's darkest step) instead of near-black, like hand-made sprites
                        pn = name(part[yy, xx])
                        if (dy, dx) in ((1, 0), (0, 1)) and pn in SELOUT_PARTS and step[yy, xx] >= SELOUT_STEP \
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
        fur_ids = {self.parts.index(p) for p in FUR_PARTS if p in self.parts}
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
        img = self.paint(*self.shrink(*self.load(d, f)))
        h = img.shape[0]
        m = (h - 32) // 2                            # the render window is 1.5 tiles; keep the centre tile
        outside = img[..., 3].copy()
        outside[m:m + 32, m:m + 32] = 0
        if outside.any():
            print(f"  warning: {d}{f} draws outside its 32x32 tile")
        return Image.fromarray(img[m:m + 32, m:m + 32])

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
        self.sheet(self.dir / f"{self.name}_sheet.png")
        for d in SHEET_ROWS:
            self.gif(d, self.dir / f"walk_{d}.gif", 1)
            self.gif(d, self.dir / f"walk_{d}_4x.gif", 4)
        refs = load_refs()
        if refs:
            self.compare(refs)
        print(f"wrote {self.dir}")

    def sheet(self, path, refs=None, zoom=4, ground=None):
        cell = 32 * zoom
        pad = 6
        cols = self.n_frames
        width = cols * (cell + pad) + 40
        if refs:
            width += 30 + refs["cols"] * (cell + pad)
        img = Image.new("RGB", (width, 4 * (cell + pad) + 34), (40, 44, 40))
        dr = ImageDraw.Draw(img)
        dr.text((40, 6), f"{self.name}: stand + {cols - 1} walk frames, 4x", fill=(230, 230, 220))
        if refs:
            dr.text((40 + cols * (cell + pad) + 30, 6), "REFERENCE ONLY (Tibia, not shipped)", fill=(255, 190, 120))
        for r, d in enumerate(SHEET_ROWS):
            y = 26 + r * (cell + pad)
            dr.text((12, y + cell // 2 - 6), d, fill=(230, 230, 220))
            for f in range(cols):
                x = 40 + f * (cell + pad)
                self._cell(img, (x, y), self.frames[d, f], zoom, ground)
            if refs:
                for f, im in enumerate(refs[d]):
                    x = 40 + cols * (cell + pad) + 30 + f * (cell + pad)
                    self._cell(img, (x, y), im, zoom, ground)
        img.save(path)

    @staticmethod
    def _cell(img, xy, sprite, zoom, ground=None):
        cell = 32 * zoom
        bg = Image.new("RGBA", (32, 32), (*BG, 255)) if ground is None else ground.copy()
        bg.alpha_composite(sprite)
        img.paste(bg.resize((cell, cell), Image.NEAREST), xy)

    def gif(self, d, path, zoom, ground=None):
        frames = []
        for f in range(1, self.n_frames):
            bg = Image.new("RGBA", (32, 32), (*BG, 255)) if ground is None else ground.copy()
            bg.alpha_composite(self.frames[d, f])
            frames.append(bg.resize((32 * zoom, 32 * zoom), Image.NEAREST).convert("RGB"))
        frames[0].save(path, save_all=True, append_images=frames[1:], duration=GIF_MS, loop=0)

    def compare(self, refs):
        cdir = self.dir / "compare"
        cdir.mkdir(exist_ok=True)
        ground = refs.get("ground")
        self.sheet(cdir / f"{self.name}_vs_refs.png", refs)
        if ground is not None:
            self.sheet(cdir / f"{self.name}_vs_refs_ground.png", refs, ground=ground)
        # side-by-side 1x and 3x walk loops: ours | reference, each direction
        for zoom in (1, 3):
            frames = []
            ground = None                            # walk loops on a plain background: easier to see the legs
            for i in range(1, self.n_frames):
                img = Image.new("RGBA", (4 * 2 * 34 * zoom, 34 * zoom), (40, 44, 40, 255))
                for r, d in enumerate(SHEET_ROWS):
                    for j, spr in enumerate((self.frames[d, i], refs[d][min(i, len(refs[d]) - 1)])):
                        bg = Image.new("RGBA", (32, 32), (*BG, 255)) if ground is None else ground.copy()
                        bg.alpha_composite(spr)
                        img.paste(bg.resize((32 * zoom, 32 * zoom), Image.NEAREST), ((r * 2 + j) * 34 * zoom, zoom))
                frames.append(img.convert("RGB"))
            frames[0].save(cdir / f"walk_ours_vs_ref_{zoom}x.gif", save_all=True, append_images=frames[1:],
                           duration=GIF_MS, loop=0)


def load_refs():
    """Reference rat frames pulled from the Tibia client files on this PC (tools/art_refs.py). Never committed."""
    p = ROOT / ".local" / "artref" / "rat_client.png"
    if not p.exists():
        return None
    im = Image.open(p).convert("RGBA")
    client_order = ["N", "E", "S", "W"]
    refs = {"cols": 9}
    for r, d in enumerate(client_order):
        refs[d] = [im.crop((f * 64 + 32, r * 64 + 32, f * 64 + 64, r * 64 + 64)) for f in range(9)]
    g = ROOT / ".local" / "artref" / "ground.png"
    if g.exists():
        refs["ground"] = Image.open(g).convert("RGBA")
    return refs


if __name__ == "__main__":
    Creature(sys.argv[1] if len(sys.argv) > 1 else "rat").run()
