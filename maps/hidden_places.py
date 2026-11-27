"""Two hidden places for levels 20-30 (roadmap AD5; adventure design 4.5): new secrets s14 and s15, each with a hidden beast.

The Smugglers' Vault lies on level 9 under the Smugglers' Cellar (the Bandit Road's party cave). In a dead corner of the
cellar an iron grate is barred shut; a Vault Key (2% from Bandit Captains) lifts the bar (scripts/spirebound/
hidden_places.lua) and takes you and your party down. Inside: a short loop of corridors round the counting room, a few
bandit guards, and Ironpurse, the smugglers' banker, woken when you step into his counting room (secret s14).

The Sealed Cut lies on level 9 under the Old Quarry: a working the quarrymen walled up. A rubble-choked mouth stands
just off the Quarry's trail; with the three mason's-mark rubbings (from marked stones in the Old Quarry, the Fallen
Bastion and the Shard Fields) it opens for your party. Inside: one long cut hall of half-carved blocks, and the
Unfinished, a half-carved stone giant, woken at the hall's mouth (secret s15).

How it is drawn (the map quality rules, as maps/underkeep.py): rooms and corridors are floor; the walls are the
one-tile shell round all of it, laid in ONE Map.autowall call; outside the shell there is no ground (solid rock).
Lamps only on north and west walls, solid things only in open space, nothing on the spawns, the trigger or the exits.
GM notes on where they are: docs/gm/floor1_minibosses.md (never in player docs).
"""
import dungeon as DG
import scenery as S
import wilds
from floor1_plan import spawn_time

GRATE = 22795            # a barred iron grate set in the cellar floor (the Vault's way in, scripted)
RUBBLE_MOUTH = 5866      # the rubble that chokes the Sealed Cut's mouth (scripted)
Z = 9

# ---------------------------------------------------------------- the Smugglers' Vault (26 x 18)
VW, VH = 26, 18
V_ROOMS = {
    "landing": (1, 6, 6, 6),       # where the grate's ladder comes down; the way back up
    "top":     (7, 2, 16, 2),      # the loop round the counting room
    "bottom":  (7, 14, 16, 2),
    "left":    (7, 2, 2, 14),
    "right":   (21, 2, 3, 14),
    "count":   (11, 6, 8, 6),      # Ironpurse's counting room
    "strong":  (24, 6, 1, 6),      # a strongroom nook off the loop's far side
}
V_CORRIDORS = [(14, 4, 2, 2), (14, 12, 2, 2)]      # the counting room's two doorways onto the loop
V_PACKS = [("top", [("Road Bandit", 2)]), ("right", [("Bandit Crossbowman", 1), ("Road Bandit", 1)]),
           ("bottom", [("Hedge Hexer", 1), ("Road Bandit", 1)])]

# ---------------------------------------------------------------- the Sealed Cut (24 x 14)
CW, CH = 24, 14
C_ROOMS = {
    "mouth": (1, 5, 6, 4),         # where the party steps in; the way back out
    "hall":  (7, 1, 16, 12),       # the long cut hall
}
RESPAWN = 300


def _floor(ox, oy, rooms, corridors=()):
    out = set()
    for x, y, w, h in list(rooms.values()) + list(corridors):
        out |= {(ox + x + i, oy + y + j) for i in range(w) for j in range(h)}
    return out


def _shell(fl, ox, oy, w, h):
    shell = {(x + dx, y + dy) for x, y in fl for dx in (-1, 0, 1) for dy in (-1, 0, 1)} - fl
    return {(x, y) for x, y in shell if ox <= x < ox + w and oy <= y < oy + h}


def _dead_corner(m, box, z, away_from):
    """the floor tile of a party cave furthest from its stairs, with free floor all round (for the grate)"""
    x1, y1, x2, y2 = box
    best = None
    for (x, y, zz) in m.ground:
        if zz != z or not (x1 <= x <= x2 and y1 <= y <= y2):
            continue
        ring = [(x + dx, y + dy, z) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
        if all(p in m.ground and not m.items.get(p) for p in ring):
            d = (x - away_from[0]) ** 2 + (y - away_from[1]) ** 2
            if best is None or d > best[0]:
                best = (d, (x, y, z))
    return best[1] if best else None


def _trailside(m, L, gate, min_gate=12):
    """a free tile just off a ground's trail (never on it), far from the gate, for the Sealed Cut's mouth"""
    best = None
    # never beside another secret: the first try put the mouth next to the North Crack (s5), and its exit landed
    # players on s5's tile, which threw them out at Millcross (client test 2026-11-27)
    others = [p for k, p in m.points.items() if k.startswith("secret_") and p[2] == 7]
    for (x, y) in sorted(L["rect"]):
        if (x, y) in L["open"] or (x, y, 7) not in m.ground or m.items.get((x, y, 7)):
            continue
        if any(max(abs(x - p[0]), abs(y - p[1])) < 8 for p in others):
            continue
        if not any((x + dx, y + dy) in L["open"] for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
            continue
        g = max(abs(x - gate[0]), abs(y - gate[1]))
        if g < min_gate:
            continue
        # the most out-of-the-way tile: far from the gate, but touching only one trail tile (a nook, not a crossing)
        touching = sum((x + dx, y + dy) in L["open"] for dx in (-1, 0, 1) for dy in (-1, 0, 1))
        score = (touching == 1 or touching == 2, g)
        if best is None or score > best[0]:
            best = (score, (x, y, 7))
    return best[1] if best else None


def build_vault(m):
    nw, se = m.points["den_bandit_road_nw"], m.points["den_bandit_road_se"]
    stairs = m.points["stairs_den_bandit_road"]
    grate = _dead_corner(m, (nw[0] + 1, nw[1] + 1, se[0] - 1, se[1] - 1), nw[2], stairs)
    if not grate:
        raise ValueError("Smugglers' Vault: no free corner in the Smugglers' Cellar for the grate")
    m.ground[grate] = GRATE
    m.points["vault_grate"] = grate
    ox, oy = nw[0] + 8, nw[1] + 6                       # under the cellar's middle
    fl = _floor(ox, oy, V_ROOMS, V_CORRIDORS)
    shell = _shell(fl, ox, oy, VW, VH)
    for x, y in fl | shell:
        m.ground[(x, y, Z)] = m.pick("stonetile")
        m.clear_items(x, y, Z)
    m.autowall(sorted(shell), Z, "stone")
    lx, ly = ox + 3, oy + 8
    m.points["vault_entry"] = (lx, ly, Z)              # where the grate's ladder lands you
    back = (ox + 2, oy + 7, Z)
    m.teleport(back, (grate[0], grate[1] + 1 if (grate[0], grate[1] + 1, grate[2]) in m.ground else grate[1] - 1, grate[2]),
               "vault_exit")
    m.sign(ox + 1, oy + 6, Z, "A rope ladder hangs here. Step on the light to climb back to the cellar.")
    cx, cy, cw, ch = V_ROOMS["count"]
    m.points["ironpurse_spawn"] = (ox + cx + cw - 3, oy + cy + 2, Z)
    trigger = (ox + cx + 3, oy + cy + 1, Z)             # one step into the counting room from its north doorway
    m.points["secret_s14"] = trigger
    quiet = [(lx, ly), back[:2], trigger[:2], m.points["ironpurse_spawn"][:2], (ox + 14, oy + 4), (ox + 15, oy + 12)]
    used = {}
    for room, pack in V_PACKS:
        x, y, w, h = V_ROOMS[room]
        n = used.get(room, 0)
        spots = wilds.spread(m, ox + x, oy + y, w, h, Z, n + 1, 3, avoid=quiet)
        spot = spots[-1]
        quiet.append(spot[:2])
        used[room] = n + 1
        wilds.group(m, spot, pack, RESPAWN)
    # dressing: the counting table, coin chests and crates, braziers; lamps on north and west walls only
    out = DG.keep_clear(m, Z) | set(quiet) | {(ox + 14, oy + 5), (ox + 15, oy + 5), (ox + 14, oy + 11), (ox + 15, oy + 11)}
    S.carpet(m, ox + cx + 2, oy + cy + 2, cw - 4, ch - 4, Z, 2576)   # a red counting-house rug
    for qx, qy, pid in ((ox + cx, oy + cy, 2472), (ox + cx + cw - 1, oy + cy, 2472), (ox + cx, oy + cy + ch - 1, 2519),
                        (ox + cx + cw - 1, oy + cy + ch - 1, 2523), (ox + 24, oy + 6, 2472), (ox + 24, oy + 11, 2519),
                        (ox + 1, oy + 11, 2523), (ox + 6, oy + 11, 2519)):
        if (qx, qy) not in out:
            S.prop(m, qx, qy, Z, pid)
    for qx, qy in ((ox + 7, oy + 2), (ox + 22, oy + 15)):
        S.prop(m, qx, qy, Z, DG.COAL_BASIN)
    DG.hang(m, ox, oy, VW, VH, Z, every=5)
    DG.scatter(m, ox, oy, VW, VH, Z, DG.COBWEBS + DG.DEBRIS, 8, avoid=out)
    return grate


def build_cut(m):
    qL = next(L for L in m.wilds if L["id"] == "old_quarry")
    gate = m.points["gate_old_quarry"]
    mouth = _trailside(m, qL, gate)
    if not mouth:
        raise ValueError("Sealed Cut: no nook beside the Old Quarry's trail for the walled-up mouth")
    m.put(*mouth, RUBBLE_MOUTH)
    m.points["sealed_cut_mouth"] = mouth
    nw = m.points["den_old_quarry_nw"]
    ox, oy = nw[0] + 16, nw[1] + 10
    fl = _floor(ox, oy, C_ROOMS)
    shell = _shell(fl, ox, oy, CW, CH)
    for x, y in fl | shell:
        m.ground[(x, y, Z)] = m.pick("cavefloor")
        m.clear_items(x, y, Z)
    m.autowall(sorted(shell), Z, "pale")
    entry = (ox + 3, oy + 6, Z)
    m.points["sealed_cut_entry"] = entry
    back = (ox + 2, oy + 7, Z)
    near = next(((mouth[0] + dx, mouth[1] + dy, 7) for dx, dy in ((0, 1), (1, 0), (0, -1), (-1, 0))
                 if (mouth[0] + dx, mouth[1] + dy) in qL["open"]), (mouth[0], mouth[1] + 1, 7))
    m.teleport(back, near, "sealed_cut_exit")
    m.sign(ox + 1, oy + 5, Z, "Daylight shows through a gap in the rubble. Step on the light to climb out.")
    hx, hy, hw, hh = C_ROOMS["hall"]
    m.points["unfinished_spawn"] = (ox + hx + hw - 4, oy + hy + hh // 2, Z)
    trigger = (ox + hx + 1, oy + 6, Z)                  # the hall's mouth
    m.points["secret_s15"] = trigger
    out = DG.keep_clear(m, Z) | {entry[:2], back[:2], trigger[:2], m.points["unfinished_spawn"][:2],
                                 (ox + hx, oy + 6), (ox + hx, oy + 7)}
    # spoil heaps of cut stone down both sides of the hall (the pillar pieces read as stairs in the render), loose rocks
    for px in range(ox + hx + 2, ox + hx + hw - 4, 3):
        for py in (oy + hy, oy + hy + hh - 1):
            if (px, py) not in out:
                S.prop(m, px, py, Z, DG.RUBBLE[(px // 3) % 2])
    DG.scatter(m, ox + hx + 2, oy + hy + 2, hw - 4, hh - 4, Z, DG.STALAGMITES, 4, solid=True, avoid=out)
    DG.scatter(m, ox, oy, CW, CH, Z, DG.DEBRIS + DG.BONES, 10, avoid=out)
    DG.hang(m, ox, oy, CW, CH, Z, every=5)
    return mouth


def build(m):
    build_vault(m)
    build_cut(m)
