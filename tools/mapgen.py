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

import collections
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
    "stonetile": [429],
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
# door_h / door_v = the family's own OPEN door (walkable) for a horizontal / vertical wall: the pairings real maps use
# (counted in Canary's own map) and checked for "walkable" in the appearances file.
FAMILIES = {
    "brick":  dict(v=1270, h=1271, pole=1272, corner=1274, wh=1736, wv=1737, door_h=5099, door_v=5108),
    "stone":  dict(v=1294, h=1295, pole=1296, corner=1298, wh=1738, wv=1739, door_h=6253, door_v=6255),
    "timber": dict(v=1281, h=1282, pole=1283, corner=1285, wh=1734, wv=1735, door_h=1649, door_v=1647),
    "sand":   dict(v=1305, h=1306, pole=1307, corner=1309, wh=1744, wv=1745, door_h=1655, door_v=1657),
    "white":  dict(v=1356, h=1357, pole=1358, corner=1360, wh=1740, wv=1741, door_h=1673, door_v=1670),
    "pale":   dict(v=1450, h=1451, pole=1452, corner=1454, wh=None, wv=None, door_h=1482, door_v=1484),
}

WALL_IDS = {i for f in FAMILIES.values() for i in f.values() if i}

# Roofs, learned from Canary's hand-made map (2026-11-11). g = the roof tile. The edge pieces hang on the empty tiles
# around the roof and are named by where the roof is, seen from that tile: "N" = the roof is to the north (the piece
# under the roof's south edge), "SE" = the roof is only diagonally south-east (the piece off its north-west corner).
ROOFS = {
    "straw":  dict(g=1152, N=5052, S=1153, E=1154, W=5049, NW=5050, NE=5054, SE=1155, SW=5048),
    "shingle": dict(g=1197, N=1202, S=1199, E=1204, W=1205, NW=1203, NE=1201, SE=1198, SW=1200),
    "moss":   dict(g=6171, N=6163, S=6160, E=6165, W=6166, NW=6164, NE=6162, SE=6159, SW=6161),
    "red":    dict(g=8620, N=8637, S=8634, E=8639, W=8640, NW=8638, NE=8636, SE=8633, SW=8635),
}
ROOF_IDS = {i for r in ROOFS.values() for i in r.values()}
# the roof each wall style gets unless a building asks for another (checked by eye in tools/maprender.py)
ROOF_FOR = {"brick": "shingle", "stone": "shingle", "timber": "straw", "sand": "straw", "white": "red", "pale": "red"}
STAIRS_UP, STAIRS_DOWN = 5258, 413      # stairs item on the lower level (walk on: up and north); stair tile above it
LADDER, TRAPDOOR = 1948, 369            # ladder on the lower level (use it: up); trapdoor tile above it (walk on: down)
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
        self.buildings = []  # dict(rect=(x0, y0, w, h), z, style, top, roof): every building, for roofs and storeys

    # -- basic painting
    def pick(self, key):
        v = ID[key]
        return self.rng.choice(v) if isinstance(v, list) else v

    def fill(self, x0, y0, w, h, z, key):
        for y in range(y0, y0 + h):
            for x in range(x0, x0 + w):
                self.ground[(x, y, z)] = self.pick(key)

    def put(self, x, y, z, iid, attrs=b""):
        if (x, y, z) not in self.ground and z >= 7:
            raise ValueError(f"item {iid} at {(x, y, z)} has no ground")   # above ground level, items may hang in the air
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
        open door is set in each gap. windows=True swaps some plain pieces for window pieces.

        Corner pieces follow the hand-made maps (counted in Canary's own map, 2026-11-11): top-left = the post,
        top-right = horizontal, bottom-left = vertical, bottom-right = the L-shaped corner piece.
        """
        f = FAMILIES[style]
        gaps = set(gaps)
        x1, y1 = x0 + w - 1, y0 + h - 1

        def near_gap(x, y):
            return any(abs(x - gx) <= 1 and abs(y - gy) <= 1 for gx, gy in gaps)

        def place(x, y, piece, door):
            if (x, y) in gaps:
                if doors:
                    self.put(x, y, z, door)
                return
            self.put(x, y, z, piece)

        for x in range(x0, x1 + 1):
            for y in (y0, y1):
                if y == y0 and x == x0:
                    piece = f["pole"]
                elif y == y1 and x == x0:
                    piece = f["v"]
                elif y == y1 and x == x1:
                    piece = f["corner"]
                elif windows and f["wh"] and 2 <= x - x0 <= w - 3 and (x - x0) % 4 == 2 and not near_gap(x, y):
                    piece = f["wh"]
                else:
                    piece = f["h"]
                place(x, y, piece, f["door_h"])
        for y in range(y0 + 1, y1):
            for x in (x0, x1):
                piece = f["v"]
                if windows and f["wv"] and 2 <= y - y0 <= h - 3 and (y - y0) % 4 == 2 and not near_gap(x, y):
                    piece = f["wv"]
                place(x, y, piece, f["door_v"])

    def roof(self, x0, y0, w, h, z, style="red"):
        """A roof over the building whose walls are the rectangle x0, y0, w, h on level z. As in the hand-made maps the
        roof sits one level up, one tile in from the top and left walls and over the bottom and right walls (the game
        draws each higher level one tile up-left, so on screen it lines up with the tops of the walls). Edge pieces
        hang on the empty tiles around it. The game hides the roof when a player walks inside."""
        r = ROOFS[style]
        rz = z - 1
        rx0, ry0, rx1, ry1 = x0 + 1, y0 + 1, x0 + w - 1, y0 + h - 1
        for y in range(ry0, ry1 + 1):
            for x in range(rx0, rx1 + 1):
                if (x, y, rz) not in self.ground:
                    self.ground[(x, y, rz)] = r["g"]
                    self.flags[(x, y, rz)] = self.flags.get((x, y, z), 0)
        inside = lambda x, y: rx0 <= x <= rx1 and ry0 <= y <= ry1
        for y in range(ry0 - 1, ry1 + 2):
            for x in range(rx0 - 1, rx1 + 2):
                if inside(x, y) or (x, y, rz) in self.ground:
                    continue
                n, s_, e, w_ = inside(x, y - 1), inside(x, y + 1), inside(x + 1, y), inside(x - 1, y)
                key = ("N" if n else "S" if s_ else "") + ("E" if e else "W" if w_ else "")
                if len(key) == 2:      # beside a straight edge, never two at once for a rectangle
                    key = key[0]
                if not key:
                    key = ("N" if inside(x, y - 1) or inside(x - 1, y - 1) or inside(x + 1, y - 1) else "S") +                           ("W" if inside(x - 1, y - 1) or inside(x - 1, y + 1) else "E")
                self.put(x, y, rz, r[key])
        return True

    def storey(self, x0, y0, w, h, z, floor="wood", style="brick", windows=True):
        """An upper storey on level z over the building whose walls are x0, y0, w, h one level below: the same wall
        rectangle, standing in the air on its top and left side (as the hand-made maps do), with a floor inside."""
        for y in range(y0 + 1, y0 + h):
            for x in range(x0 + 1, x0 + w):
                if self.ground.get((x, y, z)) in (STAIRS_DOWN, TRAPDOOR):
                    continue                  # a stairwell or trapdoor already opened from below stays open
                self.ground[(x, y, z)] = self.pick(floor)
                self.clear_items(x, y, z)
        self.walls(x0, y0, w, h, z, style=style, windows=windows)
        self.flag(x0 + 1, y0 + 1, w - 1, h - 1, z, TILE_PZ)
        for b in self.buildings:
            if b["rect"] == (x0, y0, w, h) and b["z"] > z:
                b["top"] = min(b["top"], z)

    def stairs(self, x, y, z, floor="wood", name=None):
        """Stairs up from level z: step on (x, y, z) to arrive at (x, y - 1, z - 1); the stair tile above at (x, y, z - 1)
        takes you back down to (x, y + 1, z). Both landings must stay clear."""
        if name:
            self.points["stairs_" + name] = (x, y, z)
        self.clear_items(x, y, z)
        self.put(x, y, z, STAIRS_UP)
        self.ground[(x, y, z - 1)] = STAIRS_DOWN
        self.clear_items(x, y, z - 1)
        if (x, y - 1, z - 1) not in self.ground:
            self.ground[(x, y - 1, z - 1)] = self.pick(floor)

    def ladder(self, x, y, z, floor="wood", name=None):
        """A ladder up from level z (use it to climb, arriving beside the trapdoor); the trapdoor above at
        (x, y, z - 1) takes you back down."""
        if name:
            self.points["ladder_" + name] = (x, y, z)
        self.clear_items(x, y, z)
        self.put(x, y, z, LADDER)
        self.ground[(x, y, z - 1)] = TRAPDOOR
        self.clear_items(x, y, z - 1)

    def building(self, x0, y0, w, h, z, floor="wood", door_side="s", pz=True, style="brick", windows=True, doors=False, door=None,
                 extra_gaps=()):
        # as in the hand-made maps, the top row and the left-hand column of walls stand on the OUTSIDE ground and the
        # bottom row and right-hand column on the floor (otherwise a little triangle of floor shows past the corners)
        outside = {(xx, y0): self.ground.get((xx, y0, z)) for xx in range(x0, x0 + w)}
        outside.update({(x0, yy): self.ground.get((x0, yy, z)) for yy in range(y0, y0 + h)})
        self.fill(x0, y0, w, h, z, floor)
        for (xx, yy), g in outside.items():
            if g is not None and g not in (4597, 4609, 4610):
                self.ground[(xx, yy, z)] = g
        for yy in range(y0, y0 + h):
            for xx in range(x0, x0 + w):
                self.clear_items(xx, yy, z)  # nothing the plain grew may stand inside a building
        if door is None and door_side == "s":
            door = (x0 + w // 2, y0 + h - 1)
        elif door is None and door_side == "n":
            door = (x0 + w // 2, y0)
        elif door is None and door_side == "e":
            door = (x0 + w - 1, y0 + h // 2)
        elif door is None and door_side == "w":
            door = (x0, y0 + h // 2)
        # door_side None and no door: a hall with no main door, only the extra open archways (the Hearth)
        if door is not None:
            self.ground[(door[0], door[1], z)] = self.pick(floor)   # the doorway shows the floor, not the street
        # an open door is thinner than a wall piece, so the wall tile before it (above a west door, left of a north
        # door) shows a corner of its ground: give it the floor too
        if door is not None and door_side == "w":
            self.ground[(door[0], door[1] - 1, z)] = self.pick(floor)
        elif door is not None and door_side == "n":
            self.ground[(door[0] - 1, door[1], z)] = self.pick(floor)
        # no tree, bush or rock hugging the walls or standing in front of the door
        try:
            from scenery import SCENERY
        except ImportError:
            SCENERY = set()
        ring = [(xx, yy) for xx in range(x0 - 1, x0 + w + 1) for yy in (y0 - 1, y0 + h)]
        ring += [(xx, yy) for yy in range(y0, y0 + h) for xx in (x0 - 1, x0 + w)]
        if door is not None:
            step = {"s": (0, 1), "n": (0, -1), "e": (1, 0), "w": (-1, 0)}[door_side]
            ring += [(door[0] + step[0] * k + step[1] * d, door[1] + step[1] * k + step[0] * d) for k in (1, 2) for d in (-1, 0, 1)]
        for xx, yy in ring:
            its = self.items.get((xx, yy, z))
            if its and all(i in SCENERY for i, _a in its):
                self.clear_items(xx, yy, z)
        self.walls(x0, y0, w, h, z, gaps=({door} if door is not None else set()) | set(extra_gaps), style=style, windows=windows,
                   doors=doors)
        self.buildings.append(dict(rect=(x0, y0, w, h), z=z, style=style, top=z, roof=ROOF_FOR.get(style, "red")))
        if pz:
            self.flag(x0, y0, w, h, z, TILE_PZ)
        return door

    def house_building(self, hid, name, x0, y0, w, h, z, town, rent, door_side="s", style="brick", floor="wood", storeys=1):
        door = self.building(x0, y0, w, h, z, floor=floor, door_side=door_side, style=style, doors=True)
        tiles = []
        for y in range(y0 + 1, y0 + h - 1):
            for x in range(x0 + 1, x0 + w - 1):
                self.house[(x, y, z)] = hid
                tiles.append((x, y, z))
        if storeys > 1:                       # an upstairs, reached by stairs in the back right corner; part of the house
            self.storey(x0, y0, w, h, z - 1, floor=floor, style=style)
            # stairs in the back right corner, away from the door (a north door puts them at the south end)
            sx, sy = x0 + w - 2, (y0 + h - 3 if door_side == "n" else y0 + 2)
            self.stairs(sx, sy, z, floor=floor, name=f"house_{hid}")
            for y in range(y0 + 1, y0 + h - 1):
                for x in range(x0 + 1, x0 + w - 1):
                    if (x, y, z - 1) in self.ground:
                        self.house[(x, y, z - 1)] = hid
                        tiles.append((x, y, z - 1))
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
            if any(i in WALL_IDS for i, _a in self.items.get(p, [])):
                return                      # a road never eats a building's wall or door
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

    def depot(self, x, y, z, town, locker=None):
        self.put(x, y, z, locker or ID["locker"], bytes([10]) + struct.pack("<H", town))  # OTBM_ATTR_DEPOT_ID = 10

    # depot booths as in every Tibia depot (learned from Canary's hand-made map): a row of counters, a locker standing on
    # every other counter, and two-tile wooden railings between the lockers, so each player gets a little booth to stand
    # in. Players drop items on the counters to trade across them. face = the side the player stands on.
    BOOTH = {"s": (3499, 2321, 5315, (0, 1)), "n": (3497, 2321, 5315, (0, -1)),
             "e": (3498, 2317, 5314, (1, 0)), "w": (3500, 2320, 5314, (-1, 0))}

    def depot_booths(self, x0, y0, n, z, town, face="s", depth=2, switch=10145):
        """n booths in a row starting with the first locker at (x0, y0); railings sit before, between and after them.
        The tile in front of each locker is a depot switch (red 10145; also 452 wooden, 431 stone): it lights up when you step on it
        and tells you what your depot holds. Keep depth at 2 so nobody can be pushed out of a booth."""
        locker, counter, rail, (fx, fy) = self.BOOTH[face]
        ax, ay = (0, 1) if fx else (1, 0)                       # along the row
        for i in range(2 * n + 1):
            x, y = x0 + (i - 1) * ax, y0 + (i - 1) * ay
            self.put(x, y, z, counter)
            if i % 2:
                self.depot(x, y, z, town, locker)
                if switch:
                    self.ground[(x + fx, y + fy, z)] = switch
                continue
            for d in range(1, depth + 1):
                self.put(x + d * fx, y + d * fy, z, rail)

    def autowall(self, tiles, z, style="stone"):
        """Lay wall on every (x, y) in tiles, each piece chosen from which neighbours are wall too, by the rules the
        hand-made maps follow (counted in Canary's own map): wall to the north and west = the L corner; only east and
        south = the post; otherwise vertical runs use the vertical piece and horizontal runs the horizontal one."""
        f = FAMILIES[style]
        t = set(tiles)
        for x, y in t:
            n, e, s, w = (x, y - 1) in t, (x + 1, y) in t, (x, y + 1) in t, (x - 1, y) in t
            if n and w:
                piece = f["corner"]
            elif e and s and not n:
                piece = f["pole"] if not w else f["h"]
            elif n:
                piece = f["v"]
            elif w or e:
                piece = f["h"]
            elif s:
                piece = f["v"]
            else:
                piece = f["pole"]
            self.put(x, y, z, piece)

    def maze(self, x0, y0, cells_w, cells_h, z, floor="stonefloor", seed=1, style="stone"):
        """Perfect maze with 2-tile corridors. Returns (entry, exit) tile positions."""
        rng = random.Random(seed)
        W, H = cells_w * 3 + 1, cells_h * 3 + 1
        self.fill(x0, y0, W, H, z, floor)
        for y in range(y0, y0 + H):
            for x in range(x0, x0 + W):
                self.clear_items(x, y, z)  # nothing the plain grew may stand in the corridors
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
        self.autowall([(x0 + x, y0 + y) for y in range(H) for x in range(W) if (x, y) not in open_], z, style)
        entry = (x0 + 1, y0 + 1, z)
        exit_ = (x0 + W - 3, y0 + H - 3, z)
        return entry, exit_

    def complete_objects(self):
        """Big objects (2x2 boulders, fountains, benches, beds, stalls...) are made of several pieces on neighbouring
        tiles. Every piece placed anywhere gets its other pieces added (tools/object_parts.json, learned from a
        hand-made map). If an object does not fit (a wall, a road, water or something solid in the way) the piece is
        removed instead: never half an object. Runs automatically before the map is written."""
        import json
        path = Path(__file__).resolve().parent / "object_parts.json"
        if not path.exists():
            return 0
        parts = {int(k): v for k, v in json.loads(path.read_text())["parts"].items()}
        soft = set(ID["flowers"]) | {102, 6225, 6226, 6227, 6228, 6229, 6230, 3656, 3737, 3751, 3754}
        kind = {}
        for key, v in ID.items():                      # ground variants of one kind (all the grasses, all the dirts...)
            for gid in (v if isinstance(v, list) else [v]):
                kind.setdefault(gid, key)
        for gid in (4526, 4515, 4517, 4518, 4519, 4520, 4521, 4522, 106):
            kind[gid] = "grass"
        removed = 0
        for _ in range(4):
            changed = False
            for p in list(self.items):
                for iid, _a in list(self.items.get(p, [])):
                    if iid not in parts:
                        continue
                    x, y, z = p
                    g0 = self.ground.get(p)
                    need, fits = [], True
                    for dx, dy, piece in parts[iid]:
                        q = (x + dx, y + dy, z)
                        here = [i for i, _b in self.items.get(q, [])]
                        if piece in here:
                            continue
                        g = self.ground.get(q)
                        same_ground = g is not None and (g == g0 or kind.get(g, g) == kind.get(g0, g0))
                        if not same_ground or any(i not in soft for i in here) or self.house.get(q) != self.house.get(p):
                            fits = False
                            break
                        need.append((q, piece))
                    if not fits:
                        self.items[p] = [t for t in self.items[p] if t[0] != iid]
                        if not self.items[p]:
                            del self.items[p]
                        removed += 1
                        changed = True
                    elif need:
                        for q, piece in need:
                            self.clear_items(*q)
                            self.put(*q, piece)
                        changed = True
            if not changed:
                break
        return removed

    # ---------------------------------------------------------------- output
    def edge_grounds(self):
        """Soft edges where grounds meet, the way the hand-made maps do it (tools/ground_edges.json, learned by
        tools/learn_ground_edges.py): grass spills over the edge of dirt, mud, gravel, sand, roads and paving next to it,
        and every bit of land next to water gets a shoreline. Indoor floors, bridges and walls are left alone."""
        import json
        path = Path(__file__).resolve().parent / "ground_edges.json"
        if not path.exists():
            return
        sets = json.loads(path.read_text())
        grass = set(ID["grass"]) | set(ID["dark_grass"])
        water = set(ID["water"]) | set(range(4597, 4626))
        under_grass = {g for k in ("dirt", "mud", "gravel", "sand", "cobble", "pave", "earth", "rocksoil", "dried", "swamp")
                       for g in ID[k]}
        no_shore = {408, 409} | water            # bridges, marble and water itself never get a shoreline
        # tidy the coastline first: a bit of land almost surrounded by water becomes water, a lone water tile becomes
        # land (shorelines cannot be drawn around single-tile islands and puddles)
        for _ in range(2):
            flips = []
            for (x, y, z), g in self.ground.items():
                if (x, y, z) in self.items and g not in water:
                    continue
                nbs = [self.ground.get((x + dx, y + dy, z)) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if dx or dy]
                wet = sum(1 for n in nbs if n in water)
                if g not in water and g not in (408, 409) and wet >= 6 and (x, y, z) not in self.house:
                    flips.append(((x, y, z), ID["water"][0]))
                elif g in water and wet <= 2:
                    dry = collections.Counter(n for n in nbs if n is not None and n not in water)
                    if dry:
                        flips.append(((x, y, z), dry.most_common(1)[0][0]))
            for q, ng in flips:
                self.ground[q] = ng
        d8 = {"N": (0, -1), "E": (1, 0), "S": (0, 1), "W": (-1, 0), "NW": (-1, -1), "NE": (1, -1), "SE": (1, 1), "SW": (-1, 1)}
        adj = {"NW": ("N", "W"), "NE": ("N", "E"), "SW": ("S", "W"), "SE": ("S", "E")}

        def pieces(nb, edge):
            out, covered = [], set()
            for c, (a, b) in adj.items():
                if a in nb and b in nb:
                    out.append(edge["i" + c])
                    covered |= {a, b}
            out += [edge[d] for d in "NESW" if d in nb and d not in covered]
            out += [edge["d" + c] for c, (a, b) in adj.items() if c in nb and a not in nb and b not in nb]
            return out

        for (x, y, z), g in list(self.ground.items()):
            here = self.items.get((x, y, z), [])
            if any(i in WALL_IDS for i, _a in here) or (x, y, z) in self.house:
                continue
            add = []
            if g in under_grass:
                nb = {d for d, (dx, dy) in d8.items() if self.ground.get((x + dx, y + dy, z)) in grass}
                if nb:
                    add += pieces(nb, sets["grass"])
            if g not in no_shore:
                nb = {d for d, (dx, dy) in d8.items() if self.ground.get((x + dx, y + dy, z)) in water}
                if nb:
                    add += pieces(nb, sets["water"])
            if add:
                self.items[(x, y, z)] = [(i, b"") for i in add] + list(here)

    def finish(self):
        """Last steps before writing: a roof on every building at ground level (over its top storey), then complete
        every multi-piece object."""
        if not getattr(self, "_finished", False):
            self.edge_grounds()
            for b in self.buildings:
                if b["z"] == 7 and b.get("roof"):
                    x0, y0, w, h = b["rect"]
                    self.roof(x0, y0, w, h, b["top"], b["roof"])
            self.complete_objects()
            self._finished = True

    def write(self, out=OUT):
        self.finish()
        out.mkdir(parents=True, exist_ok=True)
        root = otf.Node(0, struct.pack("<IHHII", 2, 65000, 65000, 3, 62))
        props = bytearray()
        for a, s in ((1, "Spirebound placeholder map (tools/mapgen.py)"), (11, "spirebound-monster.xml"),
                     (23, "spirebound-npc.xml"), (13, "spirebound-house.xml"), (24, "spirebound-zones.xml")):
            props += bytes([a]) + otf.pstr(s)
        md = root.add(otf.Node(2, bytes(props)))
        areas = {}
        for (x, y, z) in set(self.ground) | {p for p, l in self.items.items() if l}:
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
                if p in self.ground:
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
