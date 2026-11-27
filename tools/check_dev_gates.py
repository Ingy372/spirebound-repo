#!/usr/bin/env python3
"""Review A6-2: every test-only script (scripts/spirebound/dev_*.lua) must stop at its top unless the server was started
as a dev or test server (an os.getenv(...) check before anything is registered). Prints the scripts that do not."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
bad = []
for f in sorted((ROOT / "server/data-spirebound/scripts/spirebound").glob("dev_*.lua")):
    text = f.read_text(encoding="utf-8")
    gate = re.search(r'if os\.getenv\("SPIRE_[A-Z_]+"\) ~= "1".*?\n\s*return\n', text, re.S)
    first = re.search(r"(TalkAction|CreatureEvent|GlobalEvent|EventCallback|Action|MoveEvent)\(", text)
    if not gate or (first and first.start() < gate.start()):
        bad.append(f.name)
print("dev script gates: " + ("all gated" if not bad else "NOT gated: " + ", ".join(bad)))
sys.exit(1 if bad else 0)
