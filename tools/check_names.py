#!/usr/bin/env python3
"""Fail the build if any shipped string uses a banned name (tools/banned_names.txt).

Matching rule: case-insensitive, whole-word (a banned entry must not be part of a longer word on
either side). Pure substring matching would flag ordinary words: "agil" inside "agility", "argo" inside
"cargo", "demon" inside "demonic". Whole-word matching still catches every banned name used as a name,
including inside longer phrases ("Kirito's Blade", "the Aincrad Gate"). Possessives and plurals
("Asunas", "Kirito's") are also caught.

Scanned (shipped content only — design docs are not shipped):
  data/*.csv, tools/secrets_src.csv, assets/assets.csv, maps/src/**, server/data/** (xml, lua, txt),
  client/modules/spire_**, website/** (when present)
Also flags near misses: names one edit away from a banned name that is 6+ letters long
(for example "Lisbet" vs a banned "lisbeth"). Near misses are warnings unless --strict.

Usage: python3 tools/check_names.py [--strict] [paths...]
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

DEFAULT_GLOBS = [
    "data/*.csv", "tools/secrets_src.csv", "assets/assets.csv",
    "maps/src/**/*.txt", "maps/src/**/*.csv",
    "server/data-spirebound/**/*.xml", "server/data-spirebound/**/*.lua",
    "server/data-spirebound/**/*.json", "client/modules/**/*.lua", "client/modules/**/*.otui",
    "DESIGN.md", "ART_REQUESTS.md", "MAP_REQUESTS.md",
    "website/**/*.php", "website/**/*.html", "website/**/*.json",
]
# Upstream engine libraries copied verbatim from TFS (not player-visible content).
SKIP_PARTS = {"migrations", "npcsystem"}


def load_banned():
    out = []
    for line in (ROOT / "tools" / "banned_names.txt").read_text().splitlines():
        line = line.strip().lower()
        if line and not line.startswith("#"):
            out.append(line)
    return out


def one_edit(a: str, b: str) -> bool:
    if a == b or abs(len(a) - len(b)) > 1:
        return False
    if len(a) == len(b):
        return sum(x != y for x, y in zip(a, b)) == 1
    if len(a) > len(b):
        a, b = b, a
    i = j = diff = 0
    while i < len(a) and j < len(b):
        if a[i] != b[j]:
            diff += 1; j += 1
            if diff > 1:
                return False
        else:
            i += 1; j += 1
    return True


def main(argv):
    strict = "--strict" in argv
    paths = [Path(p) for p in argv if not p.startswith("--")]
    if not paths:
        seen = set()
        for g in DEFAULT_GLOBS:
            for p in ROOT.glob(g):
                if p.is_file() and not (set(p.relative_to(ROOT).parts) & SKIP_PARTS) and p not in seen:
                    seen.add(p); paths.append(p)
    banned = load_banned()
    pats = [(b, re.compile(r"(?<![a-z0-9])" + re.escape(b) + r"(?:'s|s)?(?![a-z0-9])", re.I)) for b in banned]
    long_names = [b for b in banned if " " not in b and len(b) >= 6]
    hits, near = [], []
    for p in paths:
        try:
            text = p.read_text(errors="replace")
        except (IsADirectoryError, FileNotFoundError):
            continue
        for ln, line in enumerate(text.splitlines(), 1):
            for b, rx in pats:
                if rx.search(line):
                    hits.append(f"{p.relative_to(ROOT) if p.is_relative_to(ROOT) else p}:{ln}: '{b}' in: {line.strip()[:100]}")
            for word in set(re.findall(r"[A-Za-z']{5,}", line)):
                w = word.lower().strip("'")
                for b in long_names:
                    if one_edit(w, b):
                        near.append(f"{p.relative_to(ROOT) if p.is_relative_to(ROOT) else p}:{ln}: '{word}' is one letter from banned '{b}'")
    for h in hits:
        print("BANNED:", h)
    for n in sorted(set(near)):
        print("NEAR MISS:", n)
    print(f"check_names: scanned {len(paths)} files, {len(hits)} banned hits, {len(set(near))} near misses")
    if hits or (strict and near):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
