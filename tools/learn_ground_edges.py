#!/usr/bin/env python3
"""Learns the edge pieces real maps put where two kinds of ground meet, and writes tools/ground_edges.json.
tools/mapgen.py uses it to smooth every border on the map (Map.edge_grounds), so grass meets dirt, roads and gravel with
a soft grass edge and water meets land with a shoreline, instead of hard square tile edges.

Learned from Canary's hand-made map (unpacked into .local/scratch/ref on Jay's PC; never committed):
  * "grass": the grass edge pieces that sit on a dirt or sand tile next to grass;
  * "water": the shoreline pieces that sit on a land tile next to water;
  * "mountain": the rock-face pieces that sit on a grass tile next to mountain ground (1128). They block walking.
Each set has 12 pieces: a side (N, E, S, W: the overlay is on that side), an outer corner (dNW...: only that diagonal
neighbour is overlay) and an inner corner (iNW...: both sides of that corner are overlay).
Run: python tools/learn_ground_edges.py [path/to/map.otbm]
"""
import collections
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

GRASS = {4526, 4515, 4517, 4518, 4519, 4520, 4521, 4522, 106}
WATER = set(range(4597, 4626))
LOWER = {103, 104, 231}                       # dirt and sand: where the grass edge pieces were counted
D8 = {"N": (0, -1), "E": (1, 0), "S": (0, 1), "W": (-1, 0), "NW": (-1, -1), "NE": (1, -1), "SE": (1, 1), "SW": (-1, 1)}
ADJ = {"NW": ("N", "W"), "NE": ("N", "E"), "SW": ("S", "W"), "SE": ("S", "E")}


def classify(nb):
    """The single edge piece a tile needs, or None if it needs several (those are skipped while learning)."""
    orth = [d for d in "NESW" if d in nb]
    if len(orth) == 1:
        side = orth[0]
        if all(d in "NESW" or side in ADJ[d] for d in nb):
            return side
        return None
    if len(orth) == 2:
        for c, (a, b) in ADJ.items():
            if set(orth) == {a, b}:
                return "i" + c
        return None
    if not orth and len(nb) == 1:
        return "d" + next(iter(nb))
    return None


def learn(ground, items, overlay, on):
    votes = collections.defaultdict(collections.Counter)
    for (x, y, z), g in ground.items():
        if g not in on:
            continue
        nb = {d for d, (dx, dy) in D8.items() if ground.get((x + dx, y + dy, z)) in overlay}
        if not nb:
            continue
        cls = classify(nb)
        if cls:
            for i in items.get((x, y, z), []):
                votes[cls][i] += 1
    out = {}
    for cls, c in votes.items():
        iid, n = c.most_common(1)[0]
        out[cls] = iid
    return out


if __name__ == "__main__":
    from learn_object_parts import read_otbm
    import struct
    src = Path(sys.argv[1] if len(sys.argv) > 1 else ROOT / ".local/scratch/ref/canary.otbm")
    # read_otbm gives items only; read grounds too
    data = src.read_bytes()
    sys.setrecursionlimit(100000)

    def parse(i):
        i += 1
        typ = data[i]
        i += 1
        props, ch = bytearray(), []
        while True:
            b = data[i]
            if b == 0xFD:
                props.append(data[i + 1]); i += 2
            elif b == 0xFE:
                c, i = parse(i); ch.append(c)
            elif b == 0xFF:
                return (typ, bytes(props), ch), i + 1
            else:
                props.append(b); i += 1

    root, _ = parse(4)
    ground, items = {}, {}

    def walk(node):
        typ, props, ch = node
        if typ == 4:
            bx, by, bz = struct.unpack("<HHB", props[:5])
            for ttyp, tp, tch in ch:
                if ttyp not in (5, 14):
                    continue
                p = (bx + tp[0], by + tp[1], bz)
                j = 2 + (4 if ttyp == 14 else 0)
                while j < len(tp):
                    a = tp[j]; j += 1
                    if a == 3:
                        j += 4
                    elif a == 9:
                        ground[p] = struct.unpack("<H", tp[j:j + 2])[0]; j += 2
                    else:
                        break
                for it in tch:
                    if it[0] == 6:
                        items.setdefault(p, []).append(struct.unpack("<H", it[1][:2])[0])
        else:
            for c in ch:
                walk(c)

    walk(root)
    sets = {"grass": learn(ground, items, GRASS, LOWER), "water": learn(ground, items, WATER, GRASS)}
    # rock faces round mountain ground (1128). Canary's map uses two piece sets about equally; 4445-4456 are grass
    # overlays, 4457-4468 the solid rock faces, which is what we want (they block walking like the rock itself)
    rock = {i: [j for j in v if 4457 <= j <= 4468] for i, v in items.items()}
    sets["mountain"] = learn(ground, rock, {1128}, GRASS)
    for k, v in sets.items():
        print(k, len(v), dict(sorted(v.items())))
    out = ROOT / "tools" / "ground_edges.json"
    out.write_text(json.dumps({"_about": "edge pieces where grounds meet; learned by tools/learn_ground_edges.py", **sets}, indent=1))
    print("->", out)
