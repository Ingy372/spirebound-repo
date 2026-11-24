#!/usr/bin/env python3
"""Fails when an NPC line puts ')', '%' or '[' right after a {keyword}.

The client's chat window (OTClient Redemption, modules/game_console/console.lua, around line 1850) turns the text after
each {keyword} into a Lua search pattern. If that text starts with ')', '%' or '[' the pattern is broken, the client
throws an error and the whole NPC reply disappears: the player sees nothing at all. Found on 2026-11-23, when
Weaponsmith Garrick's "...say {upgrade armour}), and..." never reached the screen.
Rule: never put ')', '%' or '[' straight after a closing brace in anything an NPC says.
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
BAD = re.compile(r"\{[A-Za-z' <>-]+\}[)%\[]")


def main():
    problems = []
    for path in list((ROOT / "server" / "data-spirebound").rglob("*.lua")) + [ROOT / "tools" / "gen_npcs.py"]:
        if "i18n_" in path.name or "tests" in path.parts:
            continue
        for n, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            if BAD.search(line):
                problems.append(f"{path.relative_to(ROOT)}:{n}: a {{keyword}} is followed by ')', '%' or '[': {line.strip()[:120]}")
    for p in problems:
        print(p)
    print(f"npc text: {len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
