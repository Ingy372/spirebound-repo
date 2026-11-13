#!/usr/bin/env python3
"""Roadmap R19: every chat command a player can use (a "!" TalkAction in our scripts) must also be one click away in
the client's Journal (Commands tab, client/modules/game_spirebound/journal.lua). Exits 1 and names any that is not."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OFF = {"!shop"}            # switched off until launch (SpireShop.ENABLED); it gets its button when it opens
cmds = set()
for f in (ROOT / "server/data-spirebound/scripts").rglob("*.lua"):
    if "tests" in f.parts:
        continue
    cmds |= set(re.findall(r'TalkAction\("(![a-z]+)"\)', f.read_text(encoding="utf-8")))
client = (ROOT / "client/modules/game_spirebound/journal.lua").read_text(encoding="utf-8")
buttons = set(re.findall(r"\{ '(![a-z]+)", client))
missing = sorted(cmds - buttons - OFF)
if missing:
    print("check_commands: no client button for " + ", ".join(missing))
    sys.exit(1)
print(f"check_commands: all {len(cmds - OFF)} player commands have a button in the Journal")
