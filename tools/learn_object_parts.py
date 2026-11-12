#!/usr/bin/env python3
"""Learns which items are pieces of one bigger object (a 2x2 boulder, a fountain, a bench, a bed, a stall...) by
looking at a hand-made map, and writes tools/object_parts.json. tools/mapgen.py reads that file and completes every
object it finds only partly placed, so the world never shows half a bench or a quarter of a rock.

Rule: B is a piece of the same object as A at offset (dx, dy) when, in the reference map, B sits at that offset next
to A at least 90% of the time AND A sits at the opposite offset next to B at least 90% of the time (seen 3+ times).

Needs a reference map on Jay's PC (Canary's own sample map, unpacked from the downloaded source into .local/scratch/ref;
never committed). Run: python tools/learn_object_parts.py [path/to/map.otbm]
"""
import collections
import json
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))


def read_otbm(path):
    """Minimal OTBM reader: {(x, y, z): [item ids]} for the items on each tile (ground excluded)."""
    data = Path(path).read_bytes()
    sys.setrecursionlimit(100000)

    def parse(i):
        i += 1
        typ = data[i]
        i += 1
        props, children = bytearray(), []
        while True:
            b = data[i]
            if b == 0xFD:
                props.append(data[i + 1])
                i += 2
            elif b == 0xFE:
                child, i = parse(i)
                children.append(child)
            elif b == 0xFF:
                return (typ, bytes(props), children), i + 1
            else:
                props.append(b)
                i += 1

    root, _ = parse(4)
    items = {}

    def walk(node):
        typ, props, ch = node
        if typ == 4:
            bx, by, bz = struct.unpack("<HHB", props[:5])
            for ttyp, tp, tch in ch:
                if ttyp in (5, 14):
                    p = (bx + tp[0], by + tp[1], bz)
                    for it in tch:
                        if it[0] == 6:
                            items.setdefault(p, []).append(struct.unpack("<H", it[1][:2])[0])
        else:
            for c in ch:
                walk(c)

    walk(root)
    return items


def learn(items, share=0.9, seen=3):
    from mapgen import WALL_IDS
    count = collections.Counter(i for l in items.values() for i in set(l))
    pair = collections.Counter()
    for (x, y, z), l in items.items():
        for a in set(l):
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if dx or dy:
                        for b in set(items.get((x + dx, y + dy, z), ())):
                            if b != a:
                                pair[(a, dx, dy, b)] += 1
    parts = collections.defaultdict(list)
    for (a, dx, dy, b), c in pair.items():
        if a in WALL_IDS or b in WALL_IDS or count[a] < seen or count[b] < seen:
            continue
        if c / count[a] >= share and pair.get((b, -dx, -dy, a), 0) / count[b] >= share:
            parts[a].append([dx, dy, b])
    return {str(a): sorted(v) for a, v in sorted(parts.items())}


if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else ROOT / ".local/scratch/ref/canary.otbm"
    parts = learn(read_otbm(src))
    out = ROOT / "tools" / "object_parts.json"
    out.write_text(json.dumps({"_about": "item id -> [[dx, dy, piece id], ...]: the other pieces of the same object. "
                                         "Made by tools/learn_object_parts.py from a hand-made map.", "parts": parts},
                              indent=0))
    print(f"{len(parts)} items belong to multi-piece objects -> {out}")
