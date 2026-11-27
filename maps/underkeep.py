"""The Underkeep, Wing 1 (DESIGN.md 3.4; Jay said yes to a real dungeon, Q89, 2026-11-26; map review M2, review A2-1).

A built dungeon under Hearthgate at z 8 in the same 70 x 50 box as before, so every fixed spot keeps its place: the
entry and the way out (north-west), the daily strongbox room (north-east), the doors to Wings 2 (east), 3 (south-west)
and 4 (south-east). Between them: rooms joined by corridors two or three tiles wide, with two loops, a flooded hall, a
collapsed stretch, a row of cells, a column hall, the mini-boss's den and a dead end that hides the wing's secret.

How it is drawn: every room and corridor is floor; the walls are the one-tile shell round all of it, laid in ONE
Map.autowall call so every corner and junction is chosen from its neighbours (the map quality rules). Outside the shell
there is no ground at all (solid rock, black in the client).
"""
import dungeon as DG
import scenery as S
import wilds
from floor1_plan import spawn_time

W, H = 70, 50
# rooms (x, y, w, h) inside the box, relative to its top-left corner
ROOMS = {
    "entry":     (1, 1, 11, 9),     # the way in from the drain grate, a storeroom corner
    "guard":     (16, 2, 13, 8),    # the old guard room
    "cells":     (33, 4, 21, 7),    # a corridor with a row of cells to the north
    "chest":     (59, 2, 9, 5),     # the daily strongbox (the altar stays at +64, +4)
    "flooded":   (2, 15, 17, 15),   # a hall the water took
    "columns":   (24, 15, 21, 16),  # the column hall in the middle
    "collapsed": (50, 13, 14, 11),  # half fallen in: rubble you have to walk round
    "east":      (55, 23, 13, 6),   # the hall before Wing 2's door (+66, +25)
    "southwest": (2, 35, 13, 13),   # Wing 3's door (+5, +45)
    "den":       (20, 36, 17, 12),  # the mini-boss's den
    "vault":     (41, 40, 7, 7),    # a dead end: the walled-up cell (the secret)
    "southeast": (51, 34, 17, 13),  # Wing 4's door (+60, +44)
}
# corridors: straight strips (x, y, w, h); together with the rooms they make two loops (entry-guard-columns-flooded and
# columns-collapsed-east-southeast-den) and two dead ends (the vault, the cells' far end)
CORRIDORS = [
    (12, 4, 4, 2), (29, 4, 4, 2), (54, 3, 5, 2),          # entry - guard - cells - chest
    (5, 10, 3, 5),                                         # entry - flooded
    (19, 21, 5, 3),                                        # flooded - columns
    (21, 10, 3, 5), (21, 13, 5, 2),                        # guard - columns (a bend)
    (45, 18, 5, 3),                                        # columns - collapsed (collapsed and east share a row)
    (33, 31, 3, 5),                                        # columns - den
    (15, 40, 5, 3),                                        # den - southwest
    (37, 42, 4, 2),                                        # den - vault (dead end)
    (60, 29, 3, 5),                                        # east - southeast
    (37, 36, 14, 2),                                       # den - southeast (the second loop)
]
CELL_COLS = (35, 39, 43, 47)        # the cells: small rooms off the north of the cells corridor
PACKS = [                           # about fifty monsters in packs, three kinds (+ the mini-boss)
    ("guard", [("Black Crawler", 2), ("Mire Toad", 1)]),
    ("cells", [("Vault Rat", 3)]),
    ("cells", [("Black Crawler", 2)]),
    ("flooded", [("Mire Toad", 3)]),
    ("flooded", [("Mire Toad", 2), ("Vault Rat", 1)]),
    ("columns", [("Black Crawler", 2), ("Vault Rat", 1)]),
    ("columns", [("Mire Toad", 2), ("Black Crawler", 1)]),
    ("columns", [("Vault Rat", 3)]),
    ("collapsed", [("Black Crawler", 3)]),
    ("east", [("Mire Toad", 2), ("Vault Rat", 1)]),
    ("southwest", [("Vault Rat", 2), ("Black Crawler", 1)]),
    ("southwest", [("Mire Toad", 3)]),
    ("den", [("Black Crawler", 2), ("Vault Rat", 2)]),
    ("southeast", [("Mire Toad", 2), ("Black Crawler", 2)]),
    ("southeast", [("Vault Rat", 3)]),
    ("vault", [("Vault Rat", 2)]),
]
RESPAWN = 120
MINIBOSS = "Sluice Warden"


def floor_tiles(ux, uy):
    out = set()
    for x, y, w, h in list(ROOMS.values()) + CORRIDORS:
        out |= {(ux + x + i, uy + y + j) for i in range(w) for j in range(h)}
    for cx in CELL_COLS:                                   # the cells: 3 x 2, a one-tile opening onto the corridor
        out |= {(ux + cx + i, uy + 1 + j) for i in range(3) for j in range(2)} | {(ux + cx + 1, uy + 3)}
    # the collapsed hall and the east hall meet through a short passage, and the fixed spots must be floor
    out |= {(ux + 58 + i, uy + 24) for i in range(4)} | {(ux + 58 + i, uy + 23) for i in range(4)}
    out |= {(ux + 2, uy + 2), (ux + 3, uy + 3), (ux + 4, uy + 4), (ux + 64, uy + 4), (ux + 64, uy + 25), (ux + 66, uy + 25),
            (ux + 5, uy + 45), (ux + 3, uy + 45), (ux + 58, uy + 44), (ux + 60, uy + 44)}
    return out


def build_wing1(m, ux, uy, uz):
    fl = floor_tiles(ux, uy)
    shell = {(x + dx, y + dy) for x, y in fl for dx in (-1, 0, 1) for dy in (-1, 0, 1)} - fl
    shell = {(x, y) for x, y in shell if ux <= x < ux + W and uy <= y < uy + H}
    for x, y in fl | shell:
        m.ground[(x, y, uz)] = m.pick("stonetile")
        m.clear_items(x, y, uz)
    m.autowall(sorted(shell), uz, "pale")
    # the flooded hall: water with two crossings
    fx, fy, fw, fh = ROOMS["flooded"]
    for yy in range(uy + fy + 1, uy + fy + fh - 1):
        for xx in (ux + fx + 8, ux + fx + 9):
            if yy not in (uy + fy + 4, uy + fy + 10):
                m.ground[(xx, yy, uz)] = m.pick("water")
    # fixed spots (as before)
    m.points["underkeep_entry"] = (ux + 4, uy + 4, uz)
    m.points["underkeep_chest"] = (ux + 64, uy + 4, uz)
    S.carpet(m, ux + 60, uy + 3, 7, 3, uz, 5572)
    m.put(ux + 64, uy + 4, uz, 3515)                       # an old stone altar used as the daily strongbox (scripted)
    m.points["underkeep_wing2_door"] = (ux + 69, uy + 25, uz)
    m.points["uk1_vault"] = (ux + 44, uy + 43, uz)         # the walled-up cell's secret (s13)
    m.points["uk1_miniboss"] = (ux + 28, uy + 41, uz)
    # monsters: packs placed in their rooms, as far from each other and the doors as the room allows
    quiet = [(ux + 4, uy + 4), (ux + 2, uy + 2), (ux + 64, uy + 25), (ux + 5, uy + 45), (ux + 60, uy + 44), (ux + 64, uy + 4)]
    used = {}
    for room, pack in PACKS:
        x, y, w, h = ROOMS[room]
        n = used.get(room, 0)
        spots = wilds.spread(m, ux + x + 1, uy + y + 1, max(1, w - 2), max(1, h - 2), uz, n + 1, 3, avoid=quiet)
        spot = spots[-1]
        quiet.append(spot[:2])
        used[room] = n + 1
        wilds.group(m, spot, pack, RESPAWN)
    bx, by, bz = m.points["uk1_miniboss"]
    m.monsters.append((MINIBOSS, (bx, by, bz), 1, 1, spawn_time(1800)))
    # dressing: crates in the entry, chains and bones in the cells, rubble in the collapsed hall, pillars in the column
    # hall, braziers in the den; lamps only on north and west walls
    out = DG.keep_clear(m, uz) | {(ux + 2, uy + 2), (ux + 3, uy + 3)} | {(x, y) for x, y in quiet}
    for qx, qy, pid in ((ux + 6, uy + 1, 2519), (ux + 7, uy + 1, 2523), (ux + 9, uy + 1, 2519), (ux + 1, uy + 7, 2523)):
        S.prop(m, qx, qy, uz, pid)
    cx, cy, cw, ch = ROOMS["columns"]
    for px in range(ux + cx + 3, ux + cx + cw - 2, 5):
        for py in (uy + cy + 3, uy + cy + ch - 4):
            if (px, py) not in out:
                S.prop(m, px, py, uz, DG.PILLAR)
    lx, ly, lw, lh = ROOMS["collapsed"]
    DG.scatter(m, ux + lx, uy + ly, lw, lh, uz, DG.RUBBLE, 14, solid=True, avoid=out)
    DG.scatter(m, ux + lx, uy + ly, lw, lh, uz, DG.DEBRIS, 10, avoid=out)
    dx_, dy_, dw, dh = ROOMS["den"]
    for qx, qy in ((ux + dx_ + 1, uy + dy_ + 1), (ux + dx_ + dw - 2, uy + dy_ + 1)):
        S.prop(m, qx, qy, uz, DG.COAL_BASIN)
    DG.hang(m, ux, uy, W, H, uz, every=6)
    DG.scatter(m, ux, uy, W, H, uz, DG.COBWEBS, 30, avoid=out)
    DG.scatter(m, ux, uy, W, H, uz, DG.BONES + DG.DEBRIS, 30, avoid=out)
    return fl
