#!/usr/bin/env python3
"""Every material says where it drops (gear progression spec 4.4 and 4.10; Jay's playtest 2026-11-23: players hear they
need "venomous slime" with no idea where it drops).

Fails (exit 1) when:
- a crafting recipe needs an item that no Floor 1 hunting-ground monster drops;
- a crafting material or a junk-buyer item that Floor 1 monsters drop has no "where it drops" text
  (data/item_descriptions.json, written by tools/gen_material_sources.py);
- the junk buyer lists an item that no Spirebound monster drops at all (leftover stock Tibia items).
Run: python tools/check_materials.py
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT / "tools"), str(ROOT / "maps")]


def main():
    from gen_monsters import MONSTERS, floor_monsters, GOLD, PLAT
    from junk_prices import JUNK
    from floor1_plan import CAMPS
    every = {**MONSTERS, **floor_monsters()}
    floor1 = {m[0] for c in CAMPS for m in c.get("mix", [])}
    dropped_f1, dropped_any = set(), set()
    for name, d in every.items():
        for iid, _c, _m in d.get("loot", []):
            if iid in (GOLD, PLAT):
                continue
            dropped_any.add(iid)
            if name in floor1:
                dropped_f1.add(iid)
    text = (ROOT / "server/data-spirebound/lib/spirebound/crafting.lua").read_text(encoding="utf-8")
    needs = {int(x) for blk in re.findall(r"needs = \{ ((?:\{ \d+, \d+ \},? ?)+) \}", text) for x in re.findall(r"\{ (\d+), \d+ \}", blk)}
    desc_file = ROOT / "data/item_descriptions.json"
    described = set(int(k) for k in json.loads(desc_file.read_text(encoding="utf-8"))) if desc_file.exists() else set()
    problems = []
    for iid in sorted(needs):
        if iid not in dropped_f1:
            problems.append(f"recipe material {iid} is not dropped on any Floor 1 hunting ground")
    junk_ids = {iid for _n, iid, _p in JUNK}
    from gen_material_sources import NOT_MATERIAL
    for iid in sorted(((needs | junk_ids) - NOT_MATERIAL) & dropped_f1):
        if iid not in described:
            problems.append(f"material {iid} drops on Floor 1 but its description does not say where")
    for name, iid, _p in JUNK:
        if iid not in dropped_any:
            problems.append(f"junk buyer lists {name} ({iid}) but no Spirebound monster drops it")
    if problems:
        print("check_materials:\n  " + "\n  ".join(problems))
        return 1
    print(f"check_materials: {len(needs)} recipe materials and {len(junk_ids)} junk items all have a source")
    return 0


if __name__ == "__main__":
    sys.exit(main())
