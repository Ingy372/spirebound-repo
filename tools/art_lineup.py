"""Line up several creatures on grass at game size (2x): one row each, S/E/N/W standing + two walk frames.

  python tools/art_lineup.py boar wolf alpha mole ram

Writes .local/review/lineup.png (the grass tile comes from .local/artref, so this stays local)."""
import sys
from pathlib import Path
from PIL import Image
R = Path(__file__).resolve().parents[1]
names = sys.argv[1:]
g = Image.open(R / ".local/artref/ground.png").convert("RGBA")
bg = Image.new("RGBA", (64, 64))
for x in (0, 32):
    for y in (0, 32):
        bg.paste(g, (x, y))
cells = [("S", 0), ("E", 0), ("N", 0), ("W", 0), ("E", 2), ("E", 6)]
Z = 2
out = Image.new("RGB", (len(cells) * 64 * Z, len(names) * 64 * Z))
for r, n in enumerate(names):
    for c, (d, f) in enumerate(cells):
        im = bg.copy()
        im.alpha_composite(Image.open(R / f"art/output/{n}/frames/{d}_{f}.png").convert("RGBA"))
        out.paste(im.resize((64 * Z, 64 * Z), Image.NEAREST), (c * 64 * Z, r * 64 * Z))
(R / ".local/review").mkdir(parents=True, exist_ok=True)
out.save(R / ".local/review/lineup.png"); print(R / ".local/review/lineup.png")
