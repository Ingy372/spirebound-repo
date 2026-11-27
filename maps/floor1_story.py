"""Floor 1's story places (roadmap FD1 and FD3; design docs/superpowers/specs/2026-11-27-floor1-depth-design.md 4.1, 4.3).

- Archivist Maren, the First Climb's NPC, beside the Monument in Hearthgate's plaza.
- The Oathroom: Floor 1's one hand-made group quest. Its door stands in the Old Quarry (four oath tiles, a lever and
  the garrison's standing order carved on a stone beside them); the hall itself lies on level 10, far from every other
  dungeon, and is reached only through the lever (scripts/spirebound/oathroom.lua moves the team in and out).
  Four halls in a row, one for each of the four who swore, then the reward room:
    the Vestibule -> 1 the Captain's hall (hold the line) -> 2 the Scout's hall (two corridors, four levers)
    -> 3 the Keeper's hall (a floor of rune tiles) -> 4 the Healer's hall (the Oathkeeper, four braziers) -> the chests.
  Gates are open floor in the map; the script closes them at start-up and opens them as the team goes on.
The small story objects (supply stones, the flour bin, Brother Tam's grave, the field desk, the records) are put down
at start-up by scripts/spirebound/first_climb.lua, beside named points, as the builders' stones are.

How it is drawn (map quality rules): rooms and corridors are floor; the walls are the one-tile shell round all of it,
laid in ONE Map.autowall call; lamps only on north and west walls; nothing solid on a point, gate, tile or lever.
"""
import dungeon as DG
import scenery as S

Z = 10
LEVER = 2772
STONE = 2199                 # an obelisk: the standing order, carved
OATH_GROUND = 429            # stone tiles: the four oath tiles stand out from the quarry floor
BRAZIER = 2113               # coal basin (lit); the script swaps it for the cold one while it is out
TABLE = 2523                 # a crate, for the lectern's table
AID_LEVER, AID_ORDER = 48201, 48202
ROCK = {1128, 101, None}     # mountain ground and cave rock (cliffs), or no ground at all

# ---------------------------------------------------------------- the Oathroom plan (relative to its corner)
OW, OH = 102, 17
ROOMS = {
    "vestibule": (1, 5, 8, 7),
    "captain":   (9, 6, 25, 5),        # the held corridor; the line is 6 tiles in from the west end
    "junction":  (35, 3, 4, 11),
    "north_a":   (39, 4, 9, 3), "north_b": (49, 4, 9, 3),
    "south_a":   (39, 11, 9, 3), "south_b": (49, 11, 9, 3),
    "keeper_ante": (59, 3, 6, 11),
    "runes":     (65, 6, 9, 5),        # nine rows of five rune tiles, west to east
    "healer":    (75, 2, 15, 13),
    "reward":    (91, 6, 9, 5),
}
# gates: (name, x, y top, height); one-tile-wide openings the script closes and opens
GATES = [("g1", 34, 7, 3), ("ng1", 48, 4, 3), ("sg1", 48, 11, 3), ("ng2", 58, 4, 3), ("sg2", 58, 11, 3),
         ("g3", 74, 7, 3), ("g4", 90, 7, 3)]
LINE_X = 15                            # the Captain's line, across the corridor
LEVERS = [("l1", 43, 4), ("l2", 43, 13), ("l3", 53, 4), ("l4", 53, 13)]
BRAZIERS = [(77, 4), (87, 4), (77, 12), (87, 12)]       # the stand tile is one step toward the middle (row 5 / 11)
CHESTS = [("captain", 93, 6), ("scout", 95, 6), ("keeper", 97, 6), ("healer", 99, 6)]


def _floor(ox, oy):
    out = set()
    for x, y, w, h in ROOMS.values():
        out |= {(ox + x + i, oy + y + j) for i in range(w) for j in range(h)}
    for _n, gx, gy, gh in GATES:
        out |= {(ox + gx, oy + gy + j) for j in range(gh)}
    return out


def _shell(fl):
    return {(x + dx, y + dy) for x, y in fl for dx in (-1, 0, 1) for dy in (-1, 0, 1)} - fl


def _box_free(m, x0, y0, w, h, z):
    return not any((x, y, z) in m.ground or m.items.get((x, y, z)) for x in range(x0, x0 + w) for y in range(y0, y0 + h))


def _hall_corner(m):
    """an empty corner of level 10 for the hall: tried in a fixed order, so the map never shifts between builds"""
    for ox, oy in ((1420, 1020), (1420, 1060), (1420, 1100), (1420, 1140), (1520, 1020)):
        if _box_free(m, ox - 2, oy - 2, OW + 4, OH + 4, Z):
            return ox, oy
    raise ValueError("Oathroom: no empty room for the hall on level 10")


def build_hall(m):
    ox, oy = _hall_corner(m)
    fl = _floor(ox, oy)
    shell = _shell(fl)
    for x, y in fl | shell:
        m.ground[(x, y, Z)] = m.pick("stonetile")
        m.clear_items(x, y, Z)
    m.autowall(sorted(shell), Z, "stone")
    P = m.points
    P["oath_nw"] = (ox, oy, Z)
    P["oath_se"] = (ox + OW - 1, oy + OH - 1, Z)
    P["oath_arrival"] = (ox + 5, oy + 8, Z)
    P["oath_captain_spawn"] = (ox + 31, oy + 8, Z)
    P["oath_line"] = (ox + LINE_X, oy + 6, Z)            # top tile of the line (five tiles down)
    P["oath_runes"] = (ox + 65, oy + 6, Z)               # first row, top lane
    P["oath_rune_back"] = (ox + 62, oy + 8, Z)           # where a wrong step throws you
    P["oath_boss"] = (ox + 82, oy + 8, Z)
    P["oath_reward"] = (ox + 92, oy + 8, Z)
    for name, gx, gy, gh in GATES:
        P["oath_gate_" + name] = (ox + gx, oy + gy, Z)
    for name, lx, ly in LEVERS:
        P["oath_lever_" + name] = (ox + lx, oy + ly, Z)
        m.put(ox + lx, oy + ly, Z, LEVER, bytes([4]) + (48210 + int(name[1])).to_bytes(2, "little"))
    for i, (bx, by) in enumerate(BRAZIERS, 1):
        P[f"oath_brazier_{i}"] = (ox + bx, oy + by, Z)
        m.put(ox + bx, oy + by, Z, BRAZIER)
    for name, cx, cy in CHESTS:
        P["oath_chest_" + name] = (ox + cx, oy + cy, Z)      # the chests are put down by the script (named, scripted)
    # the way out: from the Vestibule, and from the reward room
    exit_to = P["oath_door_out"]
    m.teleport((ox + 2, oy + 6, Z), exit_to, "oath_exit_vestibule")
    m.teleport((ox + 99, oy + 10, Z), exit_to, "oath_exit_reward")
    m.sign(ox + 1, oy + 5, Z, "The oath hall of the First Climb. Step on the light to climb back out to the quarry.")
    # the Scout's hall: the order of the levers, carved at its entrance
    m.sign(ox + 35, oy + 3, Z, "Carved over the two passages: SUN, then MOON, then STAR, then FLAME. One pair walks north, one walks south.")
    # the Keeper's lectern: the safe path is written in a book on it, new for every team (the script writes it)
    P["oath_lectern"] = (ox + 61, oy + 4, Z)
    m.put(ox + 61, oy + 4, Z, TABLE)
    # dressing, kept off every point, gate, line, rune and lever
    out = DG.keep_clear(m, Z)
    out |= {(ox + gx, oy + gy + j) for _n, gx, gy, gh in GATES for j in range(-1, gh + 1)}
    out |= {(ox + LINE_X + d, oy + 6 + j) for d in (-1, 0, 1) for j in range(5)}
    out |= {(ox + 65 + i, oy + 6 + j) for i in range(-1, 10) for j in range(5)}
    out |= {(ox + bx, oy + by + d) for bx, by in BRAZIERS for d in (-1, 0, 1)}
    S.carpet(m, ox + 79, oy + 6, 7, 5, Z, 2576)                      # a red carpet before the Oathkeeper
    for px, py in ((ox + 11, oy + 6), (ox + 11, oy + 10), (ox + 60, oy + 12), (ox + 92, oy + 10)):
        if (px, py) not in out:
            S.prop(m, px, py, Z, DG.COAL_BASIN)
    DG.hang(m, ox, oy, OW, OH, Z, every=6)
    DG.scatter(m, ox, oy, OW, OH, Z, DG.COBWEBS + DG.DEBRIS + DG.BONES, 18, avoid=out)
    return ox, oy


def _quarry_spot(m):
    """a free 6 x 3 block of quarry ground with a free ring round it (the stone and the lever never close a path), far
    from the gate, the secrets and the spawns, nearest the south loop. The oath tiles may lie on the trail itself."""
    qL = next(L for L in m.wilds if L["id"] == "old_quarry")
    near, gate = m.points["loop_old_quarry_b"], m.points["gate_old_quarry"]
    avoid = [p for k, p in m.points.items() if p[2] == 7 and (k.startswith("secret_") or k.startswith("sealed_cut"))]
    spawns = [pos for _n, pos, *_r in m.monsters if pos[2] == 7]
    best = None
    for (x, y) in sorted(qL["rect"]):
        ring = [(x + i, y + j) for i in range(-1, 7) for j in range(-1, 4)]
        if not all((bx, by, 7) in m.ground and not m.items.get((bx, by, 7)) and (bx, by) in qL["rect"]
                   and m.ground[(bx, by, 7)] not in ROCK for bx, by in ring):
            continue
        if not all(m.ground.get((bx, by, 7)) not in ROCK for bx in range(x - 2, x + 8) for by in range(y - 2, y + 5)):
            continue                      # not even beside a cliff: its rock faces are added later, on the floor next to it
        if max(abs(x - gate[0]), abs(y - gate[1])) < 12:
            continue                      # the gate side stays quiet
        if any(max(abs(x - p[0]), abs(y - p[1])) < 10 for p in avoid):
            continue
        if any(max(abs(x + 3 - p[0]), abs(y + 1 - p[1])) < 5 for p in spawns):
            continue
        d = (x - near[0]) ** 2 + (y - near[1]) ** 2
        if best is None or d < best[0]:
            best = (d, (x, y))
    if not best:
        raise ValueError("Oathroom: no free 6 x 3 block in the Old Quarry for the door")
    return best[1]


def build_door(m):
    x, y = _quarry_spot(m)
    # row 1: the standing order stone, then the four oath tiles; row 2: the lever under the last tile
    m.put(x, y + 1, 7, STONE, bytes([4]) + AID_ORDER.to_bytes(2, "little"))
    m.points["oath_order"] = (x, y + 1, 7)
    for i in range(4):
        m.ground[(x + 1 + i, y + 1, 7)] = OATH_GROUND
        m.points[f"oath_tile_{i + 1}"] = (x + 1 + i, y + 1, 7)
    m.put(x + 5, y + 1, 7, LEVER, bytes([4]) + AID_LEVER.to_bytes(2, "little"))
    m.points["oath_lever"] = (x + 5, y + 1, 7)
    m.points["oath_door_out"] = (x + 2, y, 7)        # where the hall lets you out (the trail side of the tiles)
    m.sign(x, y + 2, 7, "The oath stones of the First Climb. Four climbers of level 30 stand on the four stones and one pulls "
                        "the lever. Inside: 25 minutes, one team at a time. Death Game characters die for good in there.")


def place_maren(m):
    mx, my, mz = m.points["monument"]
    for dx, dy in ((2, 1), (2, 0), (3, 1), (-2, 1), (2, 2)):
        p = (mx + dx, my + dy, mz)
        if p in m.ground and not m.items.get(p) and not any(pos == p for _n, pos in m.npcs):
            m.npcs.append(("Archivist Maren", p))
            m.points["archivist_maren"] = p
            return p
    raise ValueError("Archivist Maren: no free tile beside the Monument")


def build(m):
    place_maren(m)
    build_door(m)
    build_hall(m)
