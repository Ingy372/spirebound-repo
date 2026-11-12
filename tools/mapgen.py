#!/usr/bin/env python3
"""Spirebound placeholder map generator (roadmap 1.7 / 1.8). No map editor needed.

Builds the world from Python layout code (maps/layout_floor1.py etc.) and writes, into .build/maps/:
  spirebound.otbm            the map (Canary / Tibia 15.11 item ids)
  spirebound-monster.xml     monster spawns
  spirebound-npc.xml         NPC spawns
  spirebound-house.xml       houses
  spirebound-zones.xml       (empty; PvP zone tiers come in task 2.2)
  world_points.lua           named positions for scripts (gates, boss rooms, landings)
  preview_z<N>.png           a quick top-down preview per floor level (needs Pillow; skipped if missing)

Placeholder art rules: only ids that exist in Canary's appearances.dat are used (checked on every build).
Walls use one family with a best-guess orientation; real maps replace all of this (MAP_REQUESTS.md).

Usage: python3 tools/mapgen.py [--check-ids path/to/appearances.dat]
"""
from __future__ import annotations

import random
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "maps"))
import otformats as otf  # noqa: E402

OUT = ROOT / "server" / "data-spirebound" / "world"
LIB = ROOT / "server" / "data-spirebound" / "lib" / "spirebound"
PREVIEWS = ROOT / "docs" / "previews"

# ---------------------------------------------------------------- item palette (Tibia 15.11 client ids)
ID = {
    "grass": [4526, 4526, 4526, 4526, 4515, 4517, 4518, 4519, 4520, 4521, 4522],
    "dark_grass": [106],
    "pave": [416],
    "mud": [17238],
    "dirt": [103],
    "cobble": [870],
    "wood": [408],
    "marble": [409],
    "stonefloor": [416],
    "cavefloor": [351],
    "sand": [104],
    "water": [4597, 4609],  # deep-ish water, blocks walking
    "dried": [970, 971, 972],
    "jungle": [1019],
    "gravel": [4584],
    "rocksoil": [4394, 4395],
    "earth": [280],
    "swamp": [6352],
    "snow": [799, 6594, 6595],
    "blackmarble": [410],
    "wall_v": 1270, "wall_h": 1271, "wall_c": 1272, "wall_p": 1273,  # brick wall family (orientation is a best guess)
    "tree": [3614],
    "bush": [3681],
    "boulder": [1772],
    "flowers": [108, 109],
    "altar": 3515,
    "locker": 3497,
    "mailbox": 3501,
    "teleport": 1949,  # magic forcefield, carries a destination
    "grate": 435,
    "sign": 2012,
    "torch": 2921,
    "table": 2322,
    "fountain": 1922,
}

# Wall families: v = vertical piece, h = horizontal, pole = single post, corner = L piece, wh / wv = window pieces,
# door_h / door_v = an open door set in a doorway of a horizontal / vertical wall. Ids checked visually (tools/spriteview.py).
FAMILIES = {
    "brick":  dict(v=1270, h=1271, pole=1272, corner=1273, wh=1736, wv=1737, door_h=1649, door_v=1647),
    "stone":  dict(v=1294, h=1295, pole=1296, corner=1298, wh=1738, wv=1739, door_h=1649, door_v=1647),
    "timber": dict(v=1281, h=1282, pole=1283, corner=1285, wh=1734, wv=1735, door_h=1649, door_v=1647),
    "sand":   dict(v=1305, h=1306, pole=1307, corner=1309, wh=1744, wv=1745, door_h=1649, door_v=1647),
    "white":  dict(v=1356, h=1357, pole=1358, corner=1360, wh=1740, wv=1741, door_h=1673, door_v=1670),
    "pale":   dict(v=1450, h=1451, pole=1452, corner=1454, wh=None, wv=None, door_h=1673, door_v=1670),
}

WALL_IDS = {i for f in FAMILIES.values() for i in f.values() if i}
TILE_PZ = 0x0001
TILE_NOPVP = 0x0004


class Map:
    def __init__(self, seed=7):
        self.ground = {}  # (x,y,z) -> id
        self.items = {}  # (x,y,z) -> [(id, attrs bytes)]
        self.flags = {}  # (x,y,z) -> int
        self.house = {}  # (x,y,z) -> house id
        self.houses = {}  # id -> dict
        self.towns = []  # (id, name, (x,y,z))
        self.monsters = []  # (name, (x,y,z), radius, count, interval)
        self.npcs = []  # (name, (x,y,z))
        self.points = {}  # name -> (x,y,z)
        self.zones = []  # (tier, x1, y1, x2, y2, z or None for all levels); later entries win
        self.rng = random.Random(seed)

    # -- basic painting
    def pick(self, key):
        v = ID[key]
        return self.rng.choice(v) if isinstance(v, list) else v

    def fill(self, x0, y0, w, h, z, key):
        for y in range(y0, y0 + h):
            for x in range(x0, x0 + w):
                self.ground[(x, y, z)] = self.pick(key)

    def put(self, x, y, z, iid, attrs=b""):
        if (x, y, z) not in self.ground:
            raise ValueError(f"item {iid} at {(x, y, z)} has no ground")
        self.items.setdefault((x, y, z), []).append((iid, attrs))

    def clear_items(self, x, y, z):
        self.items.pop((x, y, z), None)

    def flag(self, x0, y0, w, h, z, f):
        for y in range(y0, y0 + h):
            for x in range(x0, x0 + w):
                self.flags[(x, y, z)] = self.flags.get((x, y, z), 0) | f

    def blocked(self, x, y, z):
        return any(i in (ID["wall_v"], ID["wall_h"], ID["wall_c"], ID["wall_p"]) or i in WALL_IDS or i in ID["tree"] or i in ID["boulder"]
                   for i, _ in self.items.get((x, y, z), []))

    # -- structures
    def walls(self, x0, y0, w, h, z, gaps=(), style="brick", windows=False, doors=False):
        """Rectangle outline of wall in a family (FAMILIES). gaps = set of (x,y) left open (doorways); with doors=True an
        open door is set in each gap. windows=True swaps some plain pieces for window pieces. The SE corner gets a post."""
        f = FAMILIES[style]
        gaps = set(gaps)

        def near_gap(x, y):
            return any(abs(x - gx) <= 1 and abs(y - gy) <= 1 for gx, gy in gaps)

        for x in range(x0, x0 + w):
            for y in (y0, y0 + h - 1):
                if (x, y) in gaps:
                    if doors:
                        self.put(x, y, z, f["door_h"])
                    continue
                piece = f["h"]
                if x == x0 and y == y0:
                    piece = f["corner"]
                elif windows and f["wh"] and 2 <= x - x0 <= w - 3 and (x - x0) % 4 == 2 and not near_gap(x, y):
                    piece = f["wh"]
                self.put(x, y, z, piece)
        self.put(x0 + w - 1, y0 + h - 1, z, f["pole"]) if (x0 + w - 1, y0 + h - 1) not in gaps else None
        for y in range(y0 + 1, y0 + h - 1):
            for x in (x0, x0 + w - 1):
                if (x, y) in gaps:
                    if doors:
                        self.put(x, y, z, f["door_v"])
                    continue
                piece = f["v"]
                if windows and f["wv"] and 2 <= y - y0 <= h - 3 and (y - y0) % 4 == 2 and not near_gap(x, y):
                    piece = f["wv"]
                self.put(x, y, z, piece)

    def building(self, x0, y0, w, h, z, floor="wood", door_side="s", pz=True, style="brick", windows=True, doors=False):
        self.fill(x0, y0, w, h, z, floor)
        for yy in range(y0, y0 + h):
            for xx in range(x0, x0 + w):
                self.clear_items(xx, yy, z)  # nothing the plain grew may stand inside a building
        if door_side == "s":
            door = (x0 + w // 2, y0 + h - 1)
        elif door_side == "n":
            door = (x0 + w // 2, y0)
        elif door_side == "e":
            door = (x0 + w - 1, y0 + h // 2)
        else:
            door = (x0, y0 + h // 2)
        self.walls(x0, y0, w, h, z, gaps={door}, style=style, windows=windows, doors=doors)
        if pz:
            self.flag(x0, y0, w, h, z, TILE_PZ)
        return door

    def house_building(self, hid, name, x0, y0, w, h, z, town, rent, door_side="s", style="brick", floor="wood"):
        door = self.building(x0, y0, w, h, z, floor=floor, door_side=door_side, style=style)
        tiles = []
        for y in range(y0 + 1, y0 + h - 1):
            for x in range(x0 + 1, x0 + w - 1):
                self.house[(x, y, z)] = hid
                tiles.append((x, y, z))
        # the doorway is part of the house, so "!buyhouse" works when you stand outside and face it
        self.house[(door[0], door[1], z)] = hid
        tiles.append((door[0], door[1], z))
        entry = {"s": (door[0], door[1] + 1), "n": (door[0], door[1] - 1), "e": (door[0] + 1, door[1]), "w": (door[0] - 1, door[1])}[door_side]
        self.houses[hid] = {"name": name, "town": town, "rent": rent, "entry": (entry[0], entry[1], z), "size": len(tiles)}

    def scatter(self, x0, y0, w, h, z, key, density, avoid=None):
        for y in range(y0, y0 + h):
            for x in range(x0, x0 + w):
                p = (x, y, z)
                if p in self.ground and p not in self.items and self.rng.random() < density:
                    if avoid and avoid(x, y):
                        continue
                    self.put(x, y, z, self.pick(key))

    def road(self, a, b, z, width=3, key="dirt", wind=True):
        """A road from a to b: first along x, then along y. Long stretches wind a little (zero wobble at both ends, so
        junctions meet). Where it crosses water the road becomes a wooden bridge."""
        import math
        (x1, y1), (x2, y2) = a, b

        def lay(x, y):
            for d in range(width):
                for e in range(width):
                    pass
            p = (x, y, z)
            if p in self.ground:
                self.ground[p] = 408 if self.ground[p] in (4597, 4609, 4610) else self.pick(key)
                self.clear_items(*p)

        def wob(length, t, seed):
            if not wind or length < 40:
                return 0
            amp = min(4.0, length / 22.0)
            return int(round(amp * math.sin(math.pi * t) * math.sin((2 + seed % 3) * math.pi * t)))

        n = abs(x2 - x1)
        for i in range(n + 1):
            x = min(x1, x2) + i
            off = wob(n, i / max(n, 1), x1 + y1)
            for d in range(width):
                lay(x, y1 + d - width // 2 + off)
        n = abs(y2 - y1)
        for i in range(n + 1):
            y = min(y1, y2) + i
            off = wob(n, i / max(n, 1), x2 + y2)
            for d in range(width):
                lay(x2 + d - width // 2 + off, y)

    def zone(self, tier, x, y, w, h, z=None):
        self.zones.append((tier, x, y, x + w - 1, y + h - 1, z))

    def teleport(self, src, dst, name=None):
        attrs = bytes([8]) + struct.pack("<HHB", *dst)
        self.put(*src, ID["teleport"], attrs)
        if name:
            self.points[name] = src

    def sign(self, x, y, z, text):
        self.put(x, y, z, ID["sign"], bytes([6]) + otf.pstr(text))

    def depot(self, x, y, z, town):
        self.put(x, y, z, ID["locker"], bytes([10]) + struct.pack("<H", town))  # OTBM_ATTR_DEPOT_ID = 10

    def maze(self, x0, y0, cells_w, cells_h, z, floor="stonefloor", seed=1):
        """Perfect maze with 2-tile corridors. Returns (entry, exit) tile positions."""
        rng = random.Random(seed)
        W, H = cells_w * 3 + 1, cells_h * 3 + 1
        self.fill(x0, y0, W, H, z, floor)
        open_ = set()
        for cy in range(cells_h):
            for cx in range(cells_w):
                for dy in (1, 2):
                    for dx in (1, 2):
                        open_.add((cx * 3 + dx, cy * 3 + dy))
        seen = {(0, 0)}
        stack = [(0, 0)]
        while stack:
            cx, cy = stack[-1]
            nbrs = [(cx + dx, cy + dy, dx, dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
                    if 0 <= cx + dx < cells_w and 0 <= cy + dy < cells_h and (cx + dx, cy + dy) not in seen]
            if not nbrs:
                stack.pop(); continue
            nx, ny, dx, dy = rng.choice(nbrs)
            # knock down the wall between (cx,cy) and (nx,ny)
            if dx:
                wx = (max(cx, nx)) * 3
                open_.update({(wx, cy * 3 + 1), (wx, cy * 3 + 2)})
            else:
                wy = (max(cy, ny)) * 3
                open_.update({(cx * 3 + 1, wy), (cx * 3 + 2, wy)})
            seen.add((nx, ny)); stack.append((nx, ny))
        for y in range(H):
            for x in range(W):
                if (x, y) not in open_:
                    self.put(x0 + x, y0 + y, z, ID["wall_p"])
        entry = (x0 + 1, y0 + 1, z)
        exit_ = (x0 + W - 3, y0 + H - 3, z)
        return entry, exit_

    # ---------------------------------------------------------------- output
    def write(self, out=OUT):
        out.mkdir(parents=True, exist_ok=True)
        root = otf.Node(0, struct.pack("<IHHII", 2, 65000, 65000, 3, 62))
        props = bytearray()
        for a, s in ((1, "Spirebound placeholder map (tools/mapgen.py)"), (11, "spirebound-monster.xml"),
                     (23, "spirebound-npc.xml"), (13, "spirebound-house.xml"), (24, "spirebound-zones.xml")):
            props += bytes([a]) + otf.pstr(s)
        md = root.add(otf.Node(2, bytes(props)))
        areas = {}
        for (x, y, z) in self.ground:
            areas.setdefault((x & ~0xFF, y & ~0xFF, z), []).append((x, y))
        for (ax, ay, z), tiles in sorted(areas.items()):
            area = md.add(otf.Node(4, struct.pack("<HHB", ax, ay, z)))
            for (x, y) in sorted(tiles):
                p = (x, y, z)
                hid = self.house.get(p)
                head = struct.pack("<BB", x & 0xFF, y & 0xFF)
                if hid:
                    head += struct.pack("<I", hid)
                attrs = b""
                if self.flags.get(p):
                    attrs += bytes([3]) + struct.pack("<I", self.flags[p])
                attrs += bytes([9]) + struct.pack("<H", self.ground[p])
                tnode = area.add(otf.Node(14 if hid else 5, head + attrs))
                for iid, a in self.items.get(p, []):
                    tnode.add(otf.Node(6, struct.pack("<H", iid) + a))
        towns = md.add(otf.Node(12))
        for tid, name, (x, y, z) in self.towns:
            towns.add(otf.Node(13, struct.pack("<I", tid) + otf.pstr(name) + struct.pack("<HHB", x, y, z)))
        md.add(otf.Node(15))  # waypoints
        (out / "spirebound.otbm").write_bytes(otf.write_tree(b"OTBM", root))

        # spawns: one spawn block per monster group
        lines = ['<?xml version="1.0"?>', "<monsters>"]
        for name, (x, y, z), radius, count, interval in self.monsters:
            lines.append(f'\t<monster centerx="{x}" centery="{y}" centerz="{z}" radius="{radius}">')
            for i in range(count):
                dx = (i % 3) - 1 if radius else 0
                dy = (i // 3) - 1 if radius else 0
                lines.append(f'\t\t<monster name="{name}" x="{dx}" y="{dy}" z="{z}" spawntime="{interval}" />')
            lines.append("\t</monster>")
        lines.append("</monsters>")
        (out / "spirebound-monster.xml").write_text("\n".join(lines) + "\n")

        lines = ['<?xml version="1.0"?>', "<npcs>"]
        for name, (x, y, z) in self.npcs:
            lines.append(f'\t<npc centerx="{x}" centery="{y}" centerz="{z}" radius="1">')
            lines.append(f'\t\t<npc name="{name}" x="0" y="0" z="{z}" spawntime="60" />')
            lines.append("\t</npc>")
        lines.append("</npcs>")
        (out / "spirebound-npc.xml").write_text("\n".join(lines) + "\n")

        lines = ['<?xml version="1.0"?>', "<houses>"]
        for hid, h in sorted(self.houses.items()):
            ex, ey, ez = h["entry"]
            lines.append(f'\t<house name="{h["name"]}" houseid="{hid}" entryx="{ex}" entryy="{ey}" entryz="{ez}" '
                         f'rent="{h["rent"]}" townid="{h["town"]}" size="{h["size"]}" clientid="{hid}" guildhall="false" beds="2" />')
        lines.append("</houses>")
        (out / "spirebound-house.xml").write_text("\n".join(lines) + "\n")
        (out / "spirebound-zones.xml").write_text('<?xml version="1.0"?>\n<zones />\n')

        lua = ["-- Generated by tools/mapgen.py. Named map positions for scripts. Do not edit by hand.", "WorldPoints = {"]
        for name, (x, y, z) in sorted(self.points.items()):
            lua.append(f'\t["{name}"] = Position({x}, {y}, {z}),')
        lua.append("}")
        lua.append("-- PvP zone tiers (DESIGN.md 6.3). Later rectangles win. z = -1 means every level.")
        lua.append("WorldZones = {")
        for tier, x1, y1, x2, y2, z in self.zones:
            lua.append(f'\t{{ tier = "{tier}", x1 = {x1}, y1 = {y1}, x2 = {x2}, y2 = {y2}, z = {-1 if z is None else z} }},')
        lua.append("}")
        (LIB / "world_points.lua").write_text("\n".join(lua) + "\n")
        return out

    def preview(self, out=PREVIEWS):
        try:
            from PIL import Image
        except ImportError:
            print("preview skipped (pip install pillow)")
            return
        out.mkdir(parents=True, exist_ok=True)
        zs = sorted({z for (_, _, z) in self.ground})
        for z in zs:
            pts = [(x, y) for (x, y, zz) in self.ground if zz == z]
            x0, y0 = min(p[0] for p in pts), min(p[1] for p in pts)
            x1, y1 = max(p[0] for p in pts), max(p[1] for p in pts)
            img = Image.new("RGB", (x1 - x0 + 1, y1 - y0 + 1), (0, 0, 0))
            px = img.load()
            for (x, y) in pts:
                p = (x, y, z)
                g = self.ground[p]
                col = {**{i: (70, 140, 60) for i in ID["grass"]}, **{i: (150, 110, 70) for i in ID["dirt"]},
                       **{i: (150, 150, 150) for i in ID["cobble"]}, **{i: (170, 120, 60) for i in ID["wood"]},
                       **{i: (230, 230, 230) for i in ID["marble"]}, **{i: (110, 110, 120) for i in ID["stonefloor"]},
                       **{i: (90, 70, 50) for i in ID["cavefloor"]}, **{i: (40, 80, 200) for i in ID["water"]},
                       **{i: (220, 200, 140) for i in ID["sand"]}, **{i: (150, 160, 70) for i in ID["dried"]},
                       **{i: (40, 110, 50) for i in ID["jungle"]}, **{i: (140, 135, 125) for i in ID["gravel"]},
                       **{i: (110, 80, 60) for i in ID["rocksoil"]}, **{i: (120, 90, 60) for i in ID["earth"]},
                       **{i: (70, 90, 60) for i in ID["swamp"]}, **{i: (90, 75, 55) for i in ID["mud"]},
                       **{i: (235, 240, 250) for i in ID["snow"]}, **{i: (40, 40, 50) for i in ID["blackmarble"]}}.get(g, (255, 0, 255))
                ids = [i for i, _ in self.items.get(p, [])]
                if any(i in (ID["wall_v"], ID["wall_h"], ID["wall_c"], ID["wall_p"]) for i in ids):
                    col = (60, 40, 30)
                elif any(i in ID["tree"] or i in ID["bush"] for i in ids):
                    col = (20, 80, 20)
                elif ID["teleport"] in ids:
                    col = (0, 255, 255)
                elif any(i in ID["boulder"] for i in ids):
                    col = (100, 100, 100)
                if self.flags.get(p, 0) & TILE_PZ and col not in ((60, 40, 30),):
                    col = tuple(min(255, c + 40) for c in col)
                px[x - x0, y - y0] = col
            scale = 2
            img = img.resize((img.width * scale, img.height * scale))
            if z == 7:  # one picture per floor on the main level
                for n in [1] + list(BUILT_FLOORS):
                    fx0 = 0 if n == 1 else (2000 + (n - 2) * 400 - x0)
                    w = 400 if n == 1 else 300
                    img.crop((fx0 * scale, 0, (fx0 + w) * scale, w * scale)).save(out / f"floor{n}_z7.png")
            else:
                img.save(out / f"all_floors_z{z}.png")


def check_ids(m: Map, appearances_path: str):
    import appearances
    items = appearances.load(appearances_path)
    bad = []
    for p, g in m.ground.items():
        if g not in items or "bank" not in items[g][0]:
            bad.append(f"ground {g} at {p} is not a ground tile")
    for p, lst in m.items.items():
        for iid, _ in lst:
            if iid not in items:
                bad.append(f"item {iid} at {p} does not exist")
    return sorted(set(bad))[:50]


BUILT_FLOORS = range(2, 11)  # floors 2-10 have generated maps (phase 4: 2-5, phase 5: 6-10)


def link_floors(m):
    """Stairs up from each boss room to the next floor's landing, and portals back down from each floor town."""
    for n in [1] + list(BUILT_FLOORS):
        src, dst = m.points.get(f"stair_floor{n + 1}_src"), m.points.get(f"floor{n + 1}_landing")
        if src and dst:
            m.teleport(src, dst, f"stair_floor{n + 1}")
    for n in BUILT_FLOORS:
        down = m.points.get(f"f{n}_down_src")
        back = m.points["temple_hearthgate"] if n == 2 else m.points.get(f"f{n - 1}_temple")
        if down and back:
            m.teleport(down, (back[0], back[1] + 2, back[2]), f"f{n}_down")


def main(argv):
    import layout_floor1
    import layout_floor
    m = Map()
    layout_floor1.build(m)
    for n in BUILT_FLOORS:
        layout_floor.build(m, n)
    link_floors(m)
    out = m.write()
    m.preview()
    print(f"map: {len(m.ground)} tiles, {sum(len(v) for v in m.items.values())} items, {len(m.houses)} houses, "
          f"{len(m.monsters)} spawn groups, {len(m.npcs)} npcs -> {out}")
    if "--check-ids" in argv:
        path = argv[argv.index("--check-ids") + 1]
        bad = check_ids(m, path)
        if bad:
            print("\n".join(bad)); sys.exit("FAIL: bad item ids")
        print("item ids: all valid")


if __name__ == "__main__":
    main(sys.argv[1:])
