"""Close-up of outfits in all four directions at 6x, one row each, optionally with a local Tibia outfit beside it.

  python tools/art_outfits.py vanguard ranger arcanist mystic

Writes .local/review/outfits.png. Tibia outfits (ref_*.png from tools/art_refs.py) are local comparison only."""
import sys
from pathlib import Path
from PIL import Image
R = Path(__file__).resolve().parents[1]
REFS = {"vanguard": "ref_knight", "ranger": "ref_hunter", "arcanist": "ref_mage", "mystic": "ref_druid"}
names = sys.argv[1:]
Z, C = 5, 48
out = Image.new("RGB", (8 * C * Z, len(names) * C * Z), (196, 194, 188))
for r, n in enumerate(names):
    rp = R / f".local/artref/{REFS.get(n, '')}.png"
    ref = Image.open(rp).convert("RGBA") if rp.exists() else None
    for c, d in enumerate("SENW"):
        a = Image.open(R / f"art/output/{n}/frames/{d}_0.png").convert("RGBA").crop((64 - C, 64 - C, 64, 64)).resize((C * Z, C * Z), Image.NEAREST)
        out.paste(a, (c * C * Z, r * C * Z), a)
        if ref:
            k = "NESW".index(d)
            b = ref.crop((64 - C, k * 64 + 64 - C, 64, k * 64 + 64)).resize((C * Z, C * Z), Image.NEAREST)
            out.paste(b, ((4 + c) * C * Z, r * C * Z), b)
(R / ".local/review").mkdir(parents=True, exist_ok=True)
out.save(R / ".local/review/outfits.png"); print(R / ".local/review/outfits.png")
