#!/usr/bin/env python3
"""ASCII map source -> spirebound.otbm + spawns.xml + houses.xml (11_FLOORS_AND_MAPS). No GUI map editor.

Source layout (one directory per area under maps/src/):
  maps/src/legend.csv                 char,layer,item,notes   item: "100", "100-105" (deterministic variant),
                                                               "112+1000" (ground plus item), or "wall:112"
  maps/src/<area>/meta.csv            key,value               origin_x, origin_y, name
  maps/src/<area>/zNN_ground.txt      one char per tile, ground layer for z level NN
  maps/src/<area>/zNN_objects.txt     same grid; objects ('.' or ' ' = nothing)
  maps/src/<area>/points.csv          type,x,y,z,ref,params   (x, y relative to the area origin)

points.csv types: town, npc, spawn, house_rect, door, zone_rect, sign, trigger.
  town        ref=town id, params name=...            (x,y,z is the temple position)
  npc         ref=NPC name                            (placed in spawns.xml with radius 0)
  spawn       ref=monster name, params count=;radius=;interval=
  house_rect  ref=house id, params w=;h=;name=;rent=;town=
  door        ref=house id                            (the door tile under objects must be a house door)
  zone_rect   ref=zone type, params w=;h=             (pz | town | house | camp | labyrinth | bossroom | pass |
                                                       underkeep_wing_N | secret_gate | instance | guarded | open |
                                                       contested | deadzone)
  sign        params text=...
  trigger     ref=secret id                           (checked against road/plaza visibility)

Validation (fails the build):
  - every walkable tile reachable from a temple (except instance and secret_gate zones)
  - every house has at least one door tile, and every door tile belongs to a house
  - every spawn and NPC stands on walkable ground
  - no secret trigger within 8x6 tiles (same z) of a road, plaza, depot, temple, or camp-heart tile (23)

Usage: python3 tools/compile_map.py [--install]
"""
from __future__ import annotations

import csv
import hashlib
import shutil
import struct
import sys
from collections import deque
from pathlib import Path
from xml.sax.saxutils import quoteattr

sys.path.insert(0, str(Path(__file__).resolve().parent))
import otformats as otf  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "maps" / "src"
BUILD = ROOT / "maps" / "build"

# OTBM node types / attributes (TFS iomap.h)
OTBM_ROOT, OTBM_MAP_DATA, OTBM_TILE_AREA, OTBM_TILE, OTBM_ITEM = 0, 2, 4, 5, 6
OTBM_TOWNS, OTBM_TOWN, OTBM_HOUSETILE = 12, 13, 14
A_DESC, A_TILE_FLAGS, A_ACTION_ID, A_TEXT, A_ITEM, A_DEPOT_ID = 1, 3, 4, 6, 9, 10
A_SPAWN_FILE, A_HOUSE_FILE, A_HOUSEDOORID = 11, 13, 14
FLAG_PZ, FLAG_NOPVP, FLAG_NOLOGOUT, FLAG_PVP = 1, 4, 8, 16

PZ_ZONES = {"pz", "town", "house"}


def load_assets():
    items = {}
    with open(ROOT / "assets" / "assets.csv", newline="") as f:
        for r in csv.DictReader(f):
            if r["category"] == "item":
                items[int(r["id"])] = {"name": r["name"], "flags": {t.split(":")[0] for t in r["flags"].split(";") if t},
                                       "xml": r["xml"]}
    return items


def parse_params(s):
    out = {}
    for kv in filter(None, (s or "").split(";")):
        k, _, v = kv.partition("=")
        out[k.strip()] = v.strip()
    return out


def variant(spec: str, x: int, y: int, z: int) -> int:
    if "-" in spec:
        a, b = (int(v) for v in spec.split("-"))
        h = hashlib.md5(f"{x},{y},{z}".encode()).digest()[0]
        return a + h % (b - a + 1)
    return int(spec)


class Area:
    def __init__(self, path: Path):
        self.path = path
        self.name = path.name
        meta = {}
        with open(path / "meta.csv", newline="") as f:
            for r in csv.DictReader(f):
                meta[r["key"]] = r["value"]
        self.ox, self.oy = int(meta["origin_x"]), int(meta["origin_y"])
        self.title = meta.get("name", self.name)
        self.layers = {}
        for g in sorted(path.glob("z*_ground.txt")):
            z = int(g.name[1:3])
            ground = g.read_text().rstrip("\n").split("\n")
            op = path / f"z{z:02d}_objects.txt"
            objects = op.read_text().rstrip("\n").split("\n") if op.exists() else []
            self.layers[z] = (ground, objects)
        self.points = []
        pp = path / "points.csv"
        if pp.exists():
            with open(pp, newline="") as f:
                for r in csv.DictReader(f):
                    r["x"], r["y"], r["z"] = int(r["x"]), int(r["y"]), int(r["z"])
                    r["p"] = parse_params(r.get("params"))
                    self.points.append(r)


def compile_all(install=False):
    items = load_assets()
    legend = {}
    with open(SRC / "legend.csv", newline="") as f:
        for r in csv.DictReader(f):
            legend[(r["char"], r["layer"])] = r["item"]

    errors = []
    tiles = {}      # (x,y,z) -> dict(ground=id, items=[(id, attrs)], flags=int, house=id)
    towns, spawns, houses, triggers, special = [], [], {}, [], []
    zones = []      # (type, x0, y0, z, w, h)

    def need(iid, where):
        if iid not in items:
            errors.append(f"{where}: item {iid} not in assets.csv")

    areas = [Area(p) for p in sorted(SRC.iterdir()) if p.is_dir() and (p / "meta.csv").exists()]
    if not areas:
        raise SystemExit("no map areas under maps/src")

    for a in areas:
        for z, (ground, objects) in a.layers.items():
            # wall autotile needs the char grid
            def ch(grid, x, y):
                return grid[y][x] if 0 <= y < len(grid) and 0 <= x < len(grid[y]) else " "
            for y, row in enumerate(ground):
                for x, c in enumerate(row):
                    if c == " ":
                        continue
                    spec = legend.get((c, "ground"))
                    if spec is None:
                        errors.append(f"{a.name} z{z} ({x},{y}): ground char {c!r} not in legend"); continue
                    pos = (a.ox + x, a.oy + y, z)
                    t = tiles.setdefault(pos, {"ground": None, "items": [], "flags": 0, "house": None})
                    parts = spec.split("+")
                    if parts[0].startswith("wall:"):
                        base = parts[0][5:]
                        t["ground"] = variant(base, *pos)
                        horiz = ch(ground, x - 1, y) == c or ch(ground, x + 1, y) == c
                        vert = ch(ground, x, y - 1) == c or ch(ground, x, y + 1) == c
                        wid = 1002 if horiz and vert else 1000 if horiz else 1001 if vert else 1003
                        t["items"].append((wid, {}))
                    else:
                        t["ground"] = variant(parts[0], *pos)
                        for extra in parts[1:]:
                            t["items"].append((variant(extra, *pos), {}))
                    need(t["ground"], f"{a.name} {pos}")
            for y, row in enumerate(objects):
                for x, c in enumerate(row):
                    if c in ". ":
                        continue
                    spec = legend.get((c, "objects"))
                    if spec is None:
                        errors.append(f"{a.name} z{z} ({x},{y}): object char {c!r} not in legend"); continue
                    pos = (a.ox + x, a.oy + y, z)
                    if pos not in tiles:
                        errors.append(f"{a.name} {pos}: object {c!r} has no ground"); continue
                    iid = variant(spec, *pos)
                    need(iid, f"{a.name} {pos}")
                    tiles[pos]["items"].append((iid, {}))
        for p in a.points:
            pos = (a.ox + p["x"], a.oy + p["y"], p["z"])
            typ = p["type"]
            if typ == "town":
                towns.append((int(p["ref"]), p["p"].get("name", f"Town {p['ref']}"), pos))
            elif typ in ("npc", "spawn"):
                spawns.append((typ, p["ref"], pos, p["p"]))
            elif typ == "house_rect":
                hid = int(p["ref"])
                w, h = int(p["p"]["w"]), int(p["p"]["h"])
                houses[hid] = {"name": p["p"].get("name", f"House {hid}"), "rent": int(p["p"].get("rent", 0)),
                               "town": int(p["p"].get("town", 1)), "entry": None, "tiles": [], "doors": []}
                for yy in range(pos[1], pos[1] + h):
                    for xx in range(pos[0], pos[0] + w):
                        tp = (xx, yy, pos[2])
                        if tp in tiles:
                            tiles[tp]["house"] = hid
                            houses[hid]["tiles"].append(tp)
                zones.append(("house", pos[0], pos[1], pos[2], w, h))
            elif typ == "door":
                special.append(("door", int(p["ref"]), pos))
            elif typ == "zone_rect":
                zones.append((p["ref"], pos[0], pos[1], pos[2], int(p["p"]["w"]), int(p["p"]["h"])))
            elif typ == "sign":
                special.append(("sign", p["p"].get("text", ""), pos))
            elif typ == "trigger":
                triggers.append((p["ref"], pos))
            else:
                errors.append(f"{a.name}: unknown point type {typ}")

    # zones -> tile flags
    for ztype, x0, y0, z, w, h in zones:
        for yy in range(y0, y0 + h):
            for xx in range(x0, x0 + w):
                t = tiles.get((xx, yy, z))
                if t is None:
                    continue
                if ztype in PZ_ZONES:
                    t["flags"] |= FLAG_PZ
                t.setdefault("zones", set()).add(ztype)

    # doors, signs, lockers
    for kind, ref, pos in special:
        t = tiles.get(pos)
        if t is None:
            errors.append(f"{kind} at {pos} has no tile"); continue
        if kind == "door":
            door = next(((i, at) for i, at in t["items"] if "house door" in items[i]["name"]), None)
            if door is None:
                errors.append(f"house {ref} door at {pos}: no house door item on that tile"); continue
            door[1]["housedoor"] = ref
            houses.setdefault(ref, {"tiles": [], "doors": []})["doors"].append(pos)
            t["house"] = ref
            if pos not in houses[ref]["tiles"]:
                houses[ref]["tiles"].append(pos)
        elif kind == "sign":
            sign = next(((i, at) for i, at in t["items"] if "readable=1" in items[i]["xml"]), None)
            if sign is None:
                errors.append(f"sign at {pos}: no readable item"); continue
            sign[1]["text"] = ref
    town_ids = [tid for tid, _, _ in towns] or [1]
    for pos, t in tiles.items():
        for iid, at in t["items"]:
            if "type=depot" in items[iid]["xml"]:
                at["depot"] = town_ids[0]

    # walkability
    def walkable(pos):
        t = tiles.get(pos)
        if not t or t["ground"] is None:
            return False
        ids = [t["ground"]] + [i for i, _ in t["items"]]
        for i in ids:
            fl = items[i]["flags"]
            if "block" in fl and not ("door" in items[i]["name"]):
                return False
        return True

    for kind, ref, pos, _ in spawns:
        if not walkable(pos):
            errors.append(f"{kind} {ref} at {pos} is not on walkable ground")
    for hid, h in houses.items():
        if not h["doors"]:
            errors.append(f"house {hid} has no door")
        inside = [p for p in h["tiles"] if walkable(p) and p not in h["doors"]]
        h["entry"] = h["doors"][0] if h["doors"] else (inside[0] if inside else None)
        if h["doors"]:
            d = h["doors"][0]
            outside = [(d[0] + dx, d[1] + dy, d[2]) for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0))]
            outside = [p for p in outside if walkable(p) and tiles[p]["house"] != hid]
            h["entry"] = outside[0] if outside else d

    # reachability from temples (same z only in phase 0; stairs join levels from phase 2)
    seen = set()
    for _, _, tpos in towns:
        if not walkable(tpos):
            errors.append(f"temple at {tpos} is not walkable"); continue
        q = deque([tpos]); seen.add(tpos)
        while q:
            x, y, z = q.popleft()
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                n = (x + dx, y + dy, z)
                if n not in seen and walkable(n):
                    seen.add(n); q.append(n)
    exempt = {"instance", "secret_gate"}
    unreachable = [p for p, t in tiles.items() if walkable(p) and p not in seen and not (t.get("zones", set()) & exempt)]
    if unreachable:
        errors.append(f"{len(unreachable)} walkable tiles unreachable from any temple, e.g. {sorted(unreachable)[:5]}")

    # secret trigger visibility rule (23)
    public_zones = {"town", "pz"}
    public = [p for p, t in tiles.items() if t.get("zones", set()) & public_zones or
              any(items[i]["name"] in ("cobblestone", "dirt") for i in [t["ground"]])]
    for sid, tp in triggers:
        for p in public:
            if p[2] == tp[2] and abs(p[0] - tp[0]) <= 8 and abs(p[1] - tp[1]) <= 6:
                errors.append(f"secret trigger {sid} at {tp} is visible from public tile {p}"); break

    if errors:
        print("compile_map: FAIL")
        for e in errors[:40]:
            print("  -", e)
        return 1

    # ---------------------------------------------------------------- OTBM
    xs = [p[0] for p in tiles]; ys = [p[1] for p in tiles]
    width, height = max(xs) + 1, max(ys) + 1
    root = otf.Node(OTBM_ROOT, struct.pack("<IHHII", 2, width, height, otf.OTB_MAJOR, otf.OTB_MINOR_1098))
    md = root.add(otf.Node(OTBM_MAP_DATA, bytes([A_DESC]) + otf.pstr("Spirebound - generated by tools/compile_map.py") +
                           bytes([A_SPAWN_FILE]) + otf.pstr("spirebound-spawn.xml") +
                           bytes([A_HOUSE_FILE]) + otf.pstr("spirebound-house.xml")))
    areas_nodes = {}
    for pos in sorted(tiles, key=lambda p: (p[2], p[1], p[0])):
        x, y, z = pos
        key = (x & 0xFF00, y & 0xFF00, z)
        if key not in areas_nodes:
            areas_nodes[key] = md.add(otf.Node(OTBM_TILE_AREA, struct.pack("<HHB", *key)))
        t = tiles[pos]
        if t["house"]:
            props = struct.pack("<BBI", x & 0xFF, y & 0xFF, t["house"])
            ntype = OTBM_HOUSETILE
        else:
            props = struct.pack("<BB", x & 0xFF, y & 0xFF)
            ntype = OTBM_TILE
        if t["flags"]:
            props += bytes([A_TILE_FLAGS]) + struct.pack("<I", t["flags"])
        if t["ground"] is not None:
            props += bytes([A_ITEM]) + struct.pack("<H", t["ground"])
        tn = areas_nodes[key].add(otf.Node(ntype, props))
        for iid, at in t["items"]:
            ip = struct.pack("<H", iid)
            if "housedoor" in at:
                ip += bytes([A_HOUSEDOORID, at["housedoor"] & 0xFF])
            if "depot" in at:
                ip += bytes([A_DEPOT_ID]) + struct.pack("<H", at["depot"])
            if "text" in at:
                ip += bytes([A_TEXT]) + otf.pstr(at["text"])
            tn.add(otf.Node(OTBM_ITEM, ip))
    tw = md.add(otf.Node(OTBM_TOWNS))
    for tid, name, (x, y, z) in towns:
        tw.add(otf.Node(OTBM_TOWN, struct.pack("<I", tid) + otf.pstr(name) + struct.pack("<HHB", x, y, z)))
    otbm = otf.write_tree(b"OTBM", root)

    # spawns.xml: each monster spawn is its own spawn block; NPCs radius 0
    sx = ['<?xml version="1.0"?>', "<!-- generated by tools/compile_map.py; do not edit -->", "<spawns>"]
    for kind, ref, (x, y, z), p in spawns:
        if kind == "npc":
            sx.append(f'\t<spawn centerx="{x}" centery="{y}" centerz="{z}" radius="1">')
            sx.append(f'\t\t<npc name={quoteattr(ref)} x="0" y="0" z="{z}" spawntime="60" />')
        else:
            r = int(p.get("radius", 3)); n = int(p.get("count", 1)); iv = int(p.get("interval", 60))
            sx.append(f'\t<spawn centerx="{x}" centery="{y}" centerz="{z}" radius="{r}">')
            offs = [(0, 0), (r, 0), (-r, 0), (0, r), (0, -r), (r, r), (-r, -r), (r, -r), (-r, r)]
            for k in range(n):
                dx, dy = offs[k % len(offs)]
                if not walkable((x + dx, y + dy, z)):
                    dx, dy = 0, 0
                sx.append(f'\t\t<monster name={quoteattr(ref)} x="{dx}" y="{dy}" z="{z}" spawntime="{iv}" />')
        sx.append("\t</spawn>")
    sx.append("</spawns>")

    hx = ['<?xml version="1.0"?>', "<!-- generated by tools/compile_map.py; do not edit -->", "<houses>"]
    for hid in sorted(houses):
        h = houses[hid]
        ex, ey, ez = h["entry"]
        hx.append(f'\t<house name={quoteattr(h["name"])} houseid="{hid}" entryx="{ex}" entryy="{ey}" entryz="{ez}" '
                  f'rent="{h["rent"]}" townid="{h["town"]}" size="{len(h["tiles"])}" />')
    hx.append("</houses>")

    BUILD.mkdir(parents=True, exist_ok=True)
    (BUILD / "spirebound.otbm").write_bytes(otbm)
    (BUILD / "spirebound-spawn.xml").write_text("\n".join(sx) + "\n")
    (BUILD / "spirebound-house.xml").write_text("\n".join(hx) + "\n")

    # round trip: parse the tree back and count tiles
    back = otf.read_tree(otbm, b"OTBM")
    ntiles = sum(len(a.children) for a in back.children[0].children if a.type == OTBM_TILE_AREA)
    if ntiles != len(tiles):
        print(f"compile_map: round-trip FAIL ({ntiles} tiles read back, {len(tiles)} written)"); return 1

    if install:
        world = ROOT / "server" / "data" / "world"
        world.mkdir(parents=True, exist_ok=True)
        for f in ("spirebound.otbm", "spirebound-spawn.xml", "spirebound-house.xml"):
            shutil.copy(BUILD / f, world / f)
    print(f"compile_map: {len(areas)} area(s), {len(tiles)} tiles, {len(towns)} town(s), "
          f"{sum(1 for s in spawns if s[0] == 'spawn')} spawn(s), {sum(1 for s in spawns if s[0] == 'npc')} NPC(s), "
          f"{len(houses)} house(s); validation and round-trip pass")
    return 0


if __name__ == "__main__":
    sys.exit(compile_all(install="--install" in sys.argv))
