"""Sync art/APPROVED.txt with the sprites Jay moved into ART_FOR_JAY/approved, and list what is still waiting.

  python tools/art_approved.py

Approved sprites are frozen (art/pipeline/render.sh refuses to re-render them without FORCE=1)."""
from pathlib import Path
R = Path(__file__).resolve().parents[1]
folder = R / "ART_FOR_JAY" / "approved"
listed = R / "art" / "APPROVED.txt"
head = [l for l in listed.read_text(encoding="utf-8").splitlines() if l.startswith("#")]
already = [l.strip() for l in listed.read_text(encoding="utf-8").splitlines() if l.strip() and not l.startswith("#")]
# never drops an approval: addons (<outfit>_a1/_a2) are approved in chat and have no folder in ART_FOR_JAY
names = sorted(set(already) | {p.name for p in folder.iterdir() if p.is_dir()}) if folder.exists() else already
listed.write_text("\n".join(head + names) + "\n", encoding="utf-8")
models = sorted(p.stem for p in (R / "art" / "models").glob("*.py") if p.stem not in ("quadruped", "humanoid"))
print("approved (frozen):", ", ".join(names))
print("still waiting:    ", ", ".join(m for m in models if m not in names))
