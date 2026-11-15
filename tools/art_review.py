"""Big review sheet for one creature: all four directions, standing + 4 walk frames, on plain grey.

  python tools/art_review.py boar 4        (4 = zoom)
  python tools/art_review.py boar 3 ref    (adds the Tibia look-alike underneath; local comparison only)

Writes .local/review/<name>.png (git-ignored).
"""
import sys, json
from pathlib import Path
from PIL import Image
R = Path(__file__).resolve().parents[1]; n = sys.argv[1]; Z = int(sys.argv[2]) if len(sys.argv) > 2 else 4
cols = [0, 1, 3, 5, 7]; dirs = "SENW"
meta = json.loads((R / f"art/output/{n}/meta.json").read_text()); rf = meta.get("ref")
ref = Image.open(R / f".local/artref/{rf}").convert("RGBA") if rf and len(sys.argv) > 3 else None
rows = 4 * (2 if ref else 1)
out = Image.new("RGB", (len(cols) * 64 * Z, rows * 64 * Z), (196, 194, 188))
for r, d in enumerate(dirs):
    for c, f in enumerate(cols):
        im = Image.open(R / f"art/output/{n}/frames/{d}_{f}.png").convert("RGBA").resize((64 * Z, 64 * Z), Image.NEAREST)
        out.paste(im, (c * 64 * Z, r * 64 * Z), im)
        if ref:
            k = "NESW".index(d)
            im = ref.crop((f * 64, k * 64, f * 64 + 64, k * 64 + 64)).resize((64 * Z, 64 * Z), Image.NEAREST)
            out.paste(im, (c * 64 * Z, (4 + r) * 64 * Z), im)
(R / ".local/review").mkdir(parents=True, exist_ok=True)
out.save(R / f".local/review/{n}.png"); print(R / f".local/review/{n}.png")
