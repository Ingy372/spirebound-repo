"""Floor 1 layout (roadmap 1.8, redesigned 2026-11-11): Hearthgate Plains. DESIGN.md 3.1-3.5, 9.1-9.2.
Coordinates: Floor 1 occupies x 1000-1399, y 1000-1399, z 7 (labyrinth climbs to z 6, 5, boss room z 4;
the apex cave is z 8). Floor 2's landing is at x 2000+.
Camps and their monsters come from maps/floor1_plan.py (also read by tools/gen_bestiary.py).
Scenery helpers: maps/scenery.py. Look at the result with tools/maprender.py (real sprites, no server needed)."""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import scenery as S  # noqa: E402
import dungeon as DG  # noqa: E402
from floor1_plan import CAMPS, MILLCROSS, TOWN  # noqa: E402

X0, Y0, Z = 1000, 1000, 7
ID_PILLAR = 2152  # a tall stone pillar: free-standing columns in the Underkeep and cover in the arena
SIZE = 400
PILLAR, PILLAR_VINE, MARBLE_PILLAR, HERO_STATUE, ANGEL_STATUE = 24001, 24003, 2153, 2027, 2031


def build(m):
    rng = m.rng
    claimed = []

    def claim(name, x, y, w, h):
        """Refuse overlapping buildings: a typo in a coordinate should fail the build, not hide a wall inside a house."""
        for n, a, b, c, d in claimed:
            if x < a + c and a < x + w and y < b + d and b < y + h:
                raise ValueError(f"{name} overlaps {n}")
        claimed.append((name, x, y, w, h))

    # ------------------------------------------------ the plain, river, border of trees
    m.fill(X0, Y0, SIZE, SIZE, Z, "grass")
    for y in range(Y0, Y0 + SIZE):
        for x in range(X0, X0 + SIZE):
            if x < X0 + 3 or y < Y0 + 3 or x >= X0 + SIZE - 3 or y >= Y0 + SIZE - 3:
                m.put(x, y, Z, rng.choice(S.TREES_FIR + S.TREES_BROAD))
    # the open plain: soft clumps of trees, bushes, flowers and stones everywhere (camps add their own on top)
    S.sprinkle(m, X0 + 4, Y0 + 4, SIZE - 8, SIZE - 8, Z, S.TREES_BROAD + S.TREES_FIR, 0.05, seed=1, lo=0.62)
    S.sprinkle(m, X0 + 4, Y0 + 4, SIZE - 8, SIZE - 8, Z, S.BUSHES, 0.02, seed=2, lo=0.5)
    S.sprinkle(m, X0 + 4, Y0 + 4, SIZE - 8, SIZE - 8, Z, S.FLOWERS + S.FERNS, 0.025, seed=3, lo=0.45)
    S.sprinkle(m, X0 + 4, Y0 + 4, SIZE - 8, SIZE - 8, Z, S.STONES, 0.008, seed=4)
    river_x = X0 + 120
    for y in range(Y0 + 3, Y0 + SIZE - 3):
        wobble = int(round(7 * math.sin((y - Y0) / 26.0) + 3 * math.sin((y - Y0) / 9.0)))
        for x in range(river_x + wobble - 2, river_x + wobble + 7):  # a muddy bank either side of the water
            if (x, y, Z) in m.ground and not (river_x + wobble <= x < river_x + wobble + 5):
                m.ground[(x, y, Z)] = m.pick("mud") if rng.random() < 0.5 else 103
                m.clear_items(x, y, Z)
        m.fill(river_x + wobble, y, 5, 1, Z, "water")
        for x in range(river_x + wobble, river_x + wobble + 5):
            m.clear_items(x, y, Z)

    # ------------------------------------------------ hunting camps first (roads and towns are drawn over them)
    def theme(name, cx, cy, w, h):
        sp = S.sprinkle
        if name == "rats":                                  # the Ratwarren: dirt mounds, stones, a few bushes
            for _ in range(7):
                S.patch(m, cx + rng.randint(4, w - 5), cy + rng.randint(4, h - 5), rng.randint(2, 4), rng.randint(2, 3), Z, "dirt")
            sp(m, cx, cy, w, h, Z, S.STONES, 0.04, seed=11)
            sp(m, cx, cy, w, h, Z, S.BUSHES + S.FLOWERS, 0.03, seed=12)
        elif name == "pond":                                # Toad Pond: a pond, ferns and flowers
            S.pond(m, cx + w // 2, cy + h // 2 + 2, 7, 4, Z)
            sp(m, cx, cy, w, h, Z, S.FERNS + S.FLOWERS, 0.12, seed=13)
            sp(m, cx, cy, w, h, Z, S.BUSHES + S.TREES_BROAD, 0.03, seed=14, lo=0.5)
        elif name == "glade":                               # Sproutling Glade: lush ferns, bushes, little trees
            sp(m, cx, cy, w, h, Z, S.FERNS, 0.12, seed=15)
            sp(m, cx, cy, w, h, Z, S.BUSHES + S.FLOWERS, 0.07, seed=16)
            sp(m, cx, cy, w, h, Z, S.TREES_BROAD, 0.05, seed=17, lo=0.5)
        elif name == "wasps":                               # Waspgrass Fields: a flower meadow
            sp(m, cx, cy, w, h, Z, S.FLOWERS, 0.2, seed=18)
            sp(m, cx, cy, w, h, Z, [3625, 957], 0.015, seed=19, lo=0.6)
        elif name == "boars":                               # Boar Meadow: oak groves, bushes, mud wallows
            for _ in range(4):
                S.patch(m, cx + rng.randint(5, w - 6), cy + rng.randint(5, h - 6), rng.randint(2, 4), rng.randint(2, 3), Z, "mud")
            sp(m, cx, cy, w, h, Z, S.TREES_BROAD, 0.2, seed=20, lo=0.55)
            sp(m, cx, cy, w, h, Z, S.BUSHES + S.STONES, 0.04, seed=21)
        elif name == "hills":                               # Burrow Hills: bare dirt, stones, boulders, a little wheat
            for _ in range(10):
                S.patch(m, cx + rng.randint(3, w - 4), cy + rng.randint(3, h - 4), rng.randint(2, 5), rng.randint(2, 4), Z, "dirt")
            sp(m, cx, cy, w, h, Z, S.STONES + S.BOULDERS[:2], 0.06, seed=22, grass_only=True)
            sp(m, cx, cy, w, h, Z, [3605], 0.03, seed=23)
        elif name == "copse":                               # Wolf Copse: dark fir forest
            sp(m, cx, cy, w, h, Z, S.TREES_FIR, 0.45, seed=24, lo=0.4)
            sp(m, cx, cy, w, h, Z, S.FERNS + [7957], 0.05, seed=25)
        elif name == "thorns":                              # Thornsnap Hollow: thicket of thorn bushes and dead trees
            sp(m, cx, cy, w, h, Z, S.THORNS, 0.28, seed=26, lo=0.35)
            sp(m, cx, cy, w, h, Z, S.TREES_DEAD + S.FERNS, 0.04, seed=27)
        elif name == "marsh":                               # Reedmarsh: pools ringed with mud, ferns, dead trees
            for _ in range(6):
                S.pond(m, cx + rng.randint(6, w - 7), cy + rng.randint(6, h - 7), rng.randint(2, 4), rng.randint(2, 3), Z)
            sp(m, cx, cy, w, h, Z, S.FERNS, 0.1, seed=28)
            sp(m, cx, cy, w, h, Z, S.TREES_DEAD, 0.025, seed=29)
        elif name == "shards":                              # Shard Fields: grey gravel, boulders
            for _ in range(8):
                S.patch(m, cx + rng.randint(4, w - 5), cy + rng.randint(4, h - 5), rng.randint(3, 6), rng.randint(3, 5), Z, "gravel")
            sp(m, cx, cy, w, h, Z, S.BOULDERS, 0.018, seed=30, grass_only=False)  # each is a 2x2 rock
            sp(m, cx, cy, w, h, Z, S.STONES, 0.05, seed=31, grass_only=False)
        elif name == "bandits":                             # the Bandit Road: a ruined camp with carts, barrels, fires
            sp(m, cx, cy, w, h, Z, S.BUSHES + S.STONES, 0.04, seed=32)
            sp(m, cx, cy, w, h, Z, S.TREES_BROAD, 0.04, seed=33, lo=0.5)
            for _ in range(5):
                px, py = cx + rng.randint(6, w - 7), cy + rng.randint(6, h - 7)
                S.prop(m, px, py, Z, 5543)
                S.prop(m, px + 2, py + 1, Z, rng.choice([2519, 2523, 116, 118]))
                S.prop(m, px - 2, py, Z, rng.choice([116, 2519]))
                S.prop(m, px + 1, py + 3, Z, 1996)
        elif name == "quarry":                              # the Old Quarry: bare rock, rubble, broken pillars
            for _ in range(7):
                S.patch(m, cx + rng.randint(4, w - 5), cy + rng.randint(4, h - 5), rng.randint(3, 6), rng.randint(3, 5), Z, "gravel")
            sp(m, cx, cy, w, h, Z, S.BOULDERS + [1822, 1822], 0.1, seed=34, grass_only=False)
            sp(m, cx, cy, w, h, Z, [2264, 2290, 2152], 0.012, seed=35, grass_only=False)
        else:
            sp(m, cx, cy, w, h, Z, S.FLOWERS + S.BUSHES, 0.04, seed=36)

    def camp(c):
        cx, cy, w, h = X0 + c["x"], Y0 + c["y"], c["w"], c["h"]
        theme(c["decor"], cx, cy, w, h)
        total = int(w * h / 30)  # about one monster per 30 tiles: room for 20 players, still monsters for 500
        placed = []
        for mon, size, share in c["mix"]:
            for _ in range(max(1, round(total * share / size))):
                for _try in range(60):
                    sx, sy = cx + rng.randint(4, w - 5), cy + rng.randint(4, h - 5)
                    if all(abs(sx - px) + abs(sy - py) >= 8 for px, py in placed):
                        break
                placed.append((sx, sy))
                for p in [(sx + a, sy + b, Z) for a in (-1, 0, 1) for b in (-1, 0, 1)]:
                    m.clear_items(*p)
                    if p in m.ground and m.ground[p] in (4597, 4609, 4610):
                        m.ground[p] = m.pick("grass")
                m.monsters.append((mon, (sx, sy, Z), 3, size, c["respawn"]))
        m.points["camp_" + c["id"]] = (cx + w // 2, cy + h // 2, Z)

    for c in CAMPS:
        camp(c)

    # ------------------------------------------------ Hearthgate: the walled city (112 x 96), redesigned 2026-11-11
    # Plan (x across, y down; drawn in FLOOR1.md). Every block is a building, a street or a square; nothing is left over.
    #   y  2-10  ten shops along the north wall, five either side of the north avenue
    #   y 14-28  the Market Square, the Ascendancy west of it, the Guild Hall east
    #   y 30-45  the workshop | the Hearth (temple, depot, bank, market; 3 levels) | the Hunters' Hall
    #   y 47-51  the high road, west gate to east gate
    #   y 53-68  the inn, the training yard, Spire Manor (the showcase house) and the carriage station
    #   y 72-90  two streets of houses along the south wall (22 houses); the avenue runs on to the south gate
    tx, ty, tw, th = X0 + TOWN["x"], Y0 + TOWN["y"], TOWN["w"], TOWN["h"]
    m.fill(tx, ty, tw, th, Z, "cobble")
    for x in range(tx, tx + tw):
        for y in range(ty, ty + th):
            m.clear_items(x, y, Z)
    gates = {(tx + tw // 2 + d, ty) for d in (-1, 0, 1, 2)} | {(tx + tw // 2 + d, ty + th - 1) for d in (-1, 0, 1, 2)}
    gates |= {(tx, ty + th // 2 + d) for d in (0, 1, 2)} | {(tx + tw - 1, ty + th // 2 + d) for d in (0, 1, 2)}
    m.walls(tx, ty, tw, th, Z, gaps=gates, style="pale")          # pale stone: stands out against the grey streets
    m.flag(tx + 1, ty + 1, tw - 2, th - 2, Z, 0x0001)  # whole town is a safe zone (DESIGN 6.2)
    gate_n = (tx + tw // 2, ty)

    def R(x, y):
        return tx + x, ty + y

    # paving: marble avenues north and south, the flagstone high road east-west, the Market Square
    for y in list(range(1, 14)) + list(range(45, 53)) + list(range(69, 95)):   # (Spire Manor ends the avenue's middle)
        for x in range(55, 59):
            m.ground[(tx + x, ty + y, Z)] = 409
    for y in range(47, 52):
        for x in range(1, 111):
            m.ground[(tx + x, ty + y, Z)] = 416
    for y in range(14, 29):
        for x in range(20, 92):
            m.ground[(tx + x, ty + y, Z)] = 409 if (20 < x < 91 and 14 < y < 28) else 416

    # ---- the shop row along the north wall (9 x 9 each, door south, NPC behind the counter)
    shops = [("General Store", 2, "Merchant Wenna", "brick", "general"), ("Weaponsmith", 12, "Weaponsmith Garrick", "brick", "weapons"),
             ("Armorer", 22, "Armorer Hesta", "brick", "armor"), ("Fletcher", 32, "Fletcher Tamsin", "timber", "fletcher"),
             ("Alchemist", 42, "Alchemist Ivo", "sand", "alchemist"),
             ("Runewright", 61, "Runewright Mael", "stone", "runes"), ("Quartermaster's Stores", 71, "Quartermaster Bryn", "brick", "general"),
             ("Tailor", 81, "Tailor Quill", "timber", "tailor"), ("Bank", 91, "Banker Ansel", "white", "bank"),
             ("Post Office", 101, "Postmaster Hobb", "sand", "post")]
    for name, rx, npc, style, kind in shops:
        sx, sy = tx + rx, ty + 2
        claim(name, sx, sy, 9, 9)
        m.building(sx, sy, 9, 9, Z, floor="marble" if kind == "bank" else "wood", door_side="s", style=style, doors=True)
        m.sign(sx + 3, sy + 9, Z, name)
        S.prop(m, sx + 1, sy + 9, Z, 316)
        S.prop(m, sx + 7, sy + 9, Z, 321)
        m.points["shop_" + name.lower().replace("'", "").replace(" ", "_")] = (sx + 4, sy + 5, Z)
        m.npcs.append((npc, (sx + 4, sy + 3, Z)))
        if kind != "post":
            S.counter(m, sx + 1, sy + 4, 7, Z)
        props = {"general": ((1, 1, 2519), (2, 1, 2523), (6, 1, 116), (7, 1, 117), (7, 3, 2523)),
                 "weapons": ((1, 2, 3458), (6, 1, 116), (7, 1, 118), (7, 3, 2472)),
                 "armor": ((1, 1, 2429), (6, 1, 2429), (7, 3, 2480), (1, 3, 2472)),
                 "fletcher": ((1, 1, 2519), (7, 1, 116), (7, 3, 2523)),
                 "alchemist": ((1, 1, 2472), (7, 1, 2472), (1, 3, 2480)),
                 "runes": ((1, 1, 2480), (7, 1, 2480), (7, 3, 2472)),
                 "tailor": ((1, 1, 2429), (7, 1, 2429), (1, 3, 2480)),
                 "bank": ((1, 1, 2480), (7, 1, 2480)),
                 "post": ((1, 6, 3501), (7, 6, 3501), (1, 1, 2523), (7, 1, 2523))}[kind]
        for px, py, pid in props:
            S.prop(m, sx + px, sy + py, Z, pid)
        if kind == "bank":
            S.carpet(m, sx + 2, sy + 5, 5, 3, Z, 5572)
    m.npcs.append(("Captain Dorrow", R(59, 3) + (Z,)))

    # ---- the Market Square (x 20-91, y 14-28): fountain, the Monument, benches, trees, and stalls where players trade
    m.put(*R(38, 21), Z, 1922)
    for bx_, by_ in ((35, 18), (39, 18), (35, 24), (39, 24)):
        S.prop(m, *R(bx_, by_), Z, 2370)
    S.prop(m, *R(72, 21), Z, HERO_STATUE)
    S.prop(m, *R(47, 21), Z, ANGEL_STATUE)
    m.sign(*R(72, 24), Z, "The Monument. Names of those who opened the tower's floors are carved here. Say !top for the climbers, !memorial for the fallen.")
    m.points["monument"] = R(72, 23) + (Z,)
    m.sign(*R(57, 15), Z, "Hearthgate. Shops along the north wall; the temple, depot and Trade Hall south of this square; "
           "the inn, training yard and carriages past the high road; houses by the south wall. Say !guide for your first steps.")
    for px, py in ((22, 16), (89, 16), (22, 26), (89, 26)):
        S.prop(m, *R(px, py), Z, 3619)
    for k, sx_ in enumerate((26, 31, 79, 84)):           # four open stalls: counters players can stand behind to trade
        S.counter(m, *R(sx_, 16), 3, Z)
        S.prop(m, *R(sx_, 15), Z, (2519, 116, 2523, 117)[k])
    for sx_ in (26, 31, 79, 84):
        S.counter(m, *R(sx_, 26), 3, Z)
    m.sign(*R(30, 21), Z, "The Market Square. Stalls are free: stand behind one and trade with other climbers. "
           "For lasting offers use the market in the Trade Hall or any depot.")
    m.npcs.append(("Vesper", R(66, 25) + (Z,)))
    lamps = [(54, 15), (59, 15), (54, 27), (59, 27), (24, 21), (88, 21), (54, 5), (59, 5), (54, 12), (59, 12),
             (54, 46), (59, 46), (54, 75), (59, 75), (54, 90), (59, 90), (10, 46), (30, 46), (80, 46), (100, 46)]
    for px, py in lamps:
        S.lamp(m, *R(px, py), Z)

    # ---- the Ascendancy (west of the square) and the Guild Hall (east, with a meeting room upstairs)
    claim("ascendancy", *R(3, 15), 15, 11)
    m.building(*R(3, 15), 15, 11, Z, floor="marble", door_side="e", style="sand", doors=True)
    S.carpet(m, *R(5, 19), 10, 3, Z, 2576)
    for px, py in ((5, 17), (14, 17), (5, 23), (14, 23)):
        S.prop(m, *R(px, py), Z, MARBLE_PILLAR)
    m.sign(*R(19, 19), Z, "The Ascendancy. Climbers of level 20 and above may be promoted here.")
    m.npcs.append(("Ascendant Veyra", R(9, 20) + (Z,)))
    gx_, gy_ = R(94, 15)
    claim("guildhall", gx_, gy_, 15, 11)
    m.building(gx_, gy_, 15, 11, Z, floor="wood", door_side="w", style="timber", doors=True)
    S.carpet(m, gx_ + 2, gy_ + 2, 10, 7, Z, 5572)
    S.prop(m, gx_ + 10, gy_ + 1, Z, 2322)
    S.prop(m, gx_ + 11, gy_ + 1, Z, 2358)
    m.sign(gx_ - 1, gy_ + 3, Z, "Guild Hall. Found a guild, read the recruiting board.")
    m.npcs.append(("Guildwarden Sela", (gx_ + 7, gy_ + 5, Z)))
    m.storey(gx_, gy_, 15, 11, Z - 1, floor="wood", style="timber")
    m.stairs(gx_ + 13, gy_ + 3, Z, name="guild_hall")
    S.carpet(m, gx_ + 2, gy_ + 3, 9, 5, Z - 1, 5572)
    for px in (3, 5, 7, 9):
        S.prop(m, gx_ + px, gy_ + 5, Z - 1, 2322)
        S.prop(m, gx_ + px, gy_ + 6, Z - 1, 2358)

    # ---- The Hearth: Hearthgate's home hall (Jay, 2026-11-12: a "temple" or "home" area where players gather, with
    # banks, trading, the respawn point, 2-3 levels, a junk buyer and a banker). Like the depot squares of the big servers:
    # temple, depot, bank and market under one roof, every service a few steps from where you appear.
    #   level 1 (z 7): the temple nave in the middle (spawn and respawn point, Priest Odran), the depot west (18 lockers,
    #                  mailboxes), the bank and exchange east (Banker Tolliver, Trader Osric the junk buyer, Broker Nell)
    #   level 2 (z 6): the trading gallery: 20 more lockers, trade tables and benches, where players meet to trade
    #   level 3 (z 5): the Hall of Climbers: statues, boards, a quiet place to group up
    hx0, hy0 = R(25, 30)
    HW, HH = 62, 16
    claim("the hearth", hx0, hy0, HW, HH)
    m.building(hx0, hy0, HW, HH, Z, floor="marble", door_side="n", style="white", doors=True)
    m.storey(hx0, hy0, HW, HH, Z - 1, floor="wood", style="white")
    m.storey(hx0, hy0, HW, HH, Z - 2, floor="marble", style="white")
    # the nave and its two wings, joined by wide archways
    for lvl in (Z, Z - 1, Z - 2):
        for wx in (20, 41):
            m.autowall([(hx0 + wx, hy0 + y) for y in range(1, 15) if not 5 <= y <= 9], lvl, "white")
    for yy in range(hy0 + 1, hy0 + HH - 1):
        for xx in range(hx0 + 1, hx0 + 20):
            m.ground[(xx, yy, Z)] = 408                   # the depot wing has a wooden floor
        for xx in range(hx0 + 42, hx0 + HW - 1):
            m.ground[(xx, yy, Z)] = 410                   # the bank wing black marble
    temple = (hx0 + 31, hy0 + 8, Z)
    S.carpet(m, hx0 + 30, hy0 + 1, 3, 11, Z, 2576)
    m.put(hx0 + 31, hy0 + 12, Z, 3515)                   # the altar
    for px, py in ((23, 3), (38, 3), (23, 12), (38, 12), (26, 3), (35, 3)):
        S.prop(m, hx0 + px, hy0 + py, Z, MARBLE_PILLAR)
    for px, py in ((24, 7), (36, 7)):
        S.prop(m, hx0 + px, hy0 + py, Z, 2370)           # benches either side of the aisle
    m.towns.append((1, "Hearthgate", temple))
    m.points["temple_hearthgate"] = temple
    m.npcs.append(("Priest Odran", (hx0 + 34, hy0 + 11, Z)))
    m.sign(hx0 + 33, hy0 - 1, Z, "The Hearth. Temple, depot, bank and market under one roof: you wake here when you fall. "
           "The trading gallery is upstairs.")
    # west wing: the depot
    for x in range(2, 20, 2):
        m.depot(hx0 + x, hy0 + 1, Z, 1)
        m.depot(hx0 + x, hy0 + 14, Z, 1)
    for px in (6, 14):
        m.put(hx0 + px, hy0 + 7, Z, 3501)                # mailboxes
    m.sign(hx0 + 10, hy0 + 8, Z, "Depot. Your lockers are shared by every depot in the tower. Open the market from any locker.")
    m.points["depot_hearthgate"] = (hx0 + 10, hy0 + 5, Z)
    # east wing: the bank and exchange
    S.counter(m, hx0 + 43, hy0 + 5, 17, Z)
    m.npcs.append(("Banker Tolliver", (hx0 + 46, hy0 + 3, Z)))
    m.npcs.append(("Trader Osric", (hx0 + 52, hy0 + 3, Z)))
    m.npcs.append(("Broker Nell", (hx0 + 57, hy0 + 3, Z)))
    for px, pid in ((43, 2480), (49, 2472), (55, 2480), (59, 2472)):
        S.prop(m, hx0 + px, hy0 + 1, Z, pid)
    m.sign(hx0 + 50, hy0 + 7, Z, "Bank and Exchange. Banker Tolliver keeps your gold and your account vault; Trader Osric buys "
           "your loot; Broker Nell explains the market.")
    m.points["trade_hall"] = (hx0 + 51, hy0 + 9, Z)
    m.points["hearth_bank"] = (hx0 + 46, hy0 + 6, Z)
    m.points["hearth_trader"] = (hx0 + 52, hy0 + 6, Z)
    # level 2: the trading gallery
    for x in range(2, 60, 3):
        if not 19 <= x <= 22 and not 40 <= x <= 43:
            m.depot(hx0 + x, hy0 + 1, Z - 1, 1)
    for row in (6, 10):
        for x0_ in (4, 24, 45):
            S.counter(m, hx0 + x0_, hy0 + row, 11, Z - 1)  # trade tables: stand either side and deal
    for px, py in ((10, 13), (29, 13), (51, 13)):
        S.prop(m, hx0 + px, hy0 + py, Z - 1, 2370)
    m.sign(hx0 + 31, hy0 + 4, Z - 1, "The Trading Gallery. Meet, haggle, and trade face to face. Lockers along the north wall.")
    DG.hang(m, hx0, hy0, HW, HH, Z - 1, every=5, offset=4)
    # level 3: the Hall of Climbers
    for px, py, pid in ((8, 4, HERO_STATUE), (54, 4, ANGEL_STATUE), (8, 11, ANGEL_STATUE), (54, 11, HERO_STATUE)):
        S.prop(m, hx0 + px, hy0 + py, Z - 2, pid)
    for px, py in ((25, 4), (37, 4), (25, 11), (37, 11)):
        S.prop(m, hx0 + px, hy0 + py, Z - 2, MARBLE_PILLAR)
    S.carpet(m, hx0 + 24, hy0 + 6, 15, 4, Z - 2, 2576)
    m.sign(hx0 + 31, hy0 + 4, Z - 2, "The Hall of Climbers. Look for a party here before you climb. Say !top for the climbers.")
    DG.hang(m, hx0, hy0, HW, HH, Z - 2, every=5, offset=4)
    # stairs: from each wing up to the gallery, and from the gallery's middle up to the hall
    m.stairs(hx0 + 19, hy0 + 4, Z, floor="wood", name="hearth_west")
    m.stairs(hx0 + 42, hy0 + 11, Z, floor="wood", name="hearth_east")
    m.stairs(hx0 + 31, hy0 + 3, Z - 1, floor="marble", name="hearth_hall")
    DG.hang(m, hx0, hy0, HW, HH, Z, every=5, offset=3)

    # the Housewright's workshop moved into the old depot building, west of the Hearth
    wx_, wy_ = R(2, 31)
    claim("workshop", wx_, wy_, 17, 12)
    m.building(wx_, wy_, 17, 12, Z, floor="wood", door_side="e", style="stone", doors=True)
    for px, py, pid in ((2, 3, 3458), (4, 1, 116), (5, 1, 118), (12, 1, 2519), (13, 1, 2523), (14, 1, 2472), (10, 1, 2429)):
        S.prop(m, wx_ + px, wy_ + py, Z, pid)
    S.counter(m, wx_ + 3, wy_ + 5, 10, Z)
    m.sign(wx_ + 17, wy_ + 4, Z, "Housewright's Workshop: furniture kits and tapestries.")
    m.npcs.append(("Housewright Orla", (wx_ + 8, wy_ + 4, Z)))

    hhx, hhy = R(89, 30)
    claim("Hunters' Hall", hhx, hhy, 20, 15)
    m.building(hhx, hhy, 20, 15, Z, floor="wood", door_side="w", style="stone", doors=True)
    m.points["shop_hunters_hall"] = (hhx + 6, hhy + 7, Z)
    S.carpet(m, hhx + 3, hhy + 8, 12, 4, Z, 2576)
    S.prop(m, hhx + 1, hhy + 12, Z, 2033)
    S.prop(m, hhx + 17, hhy + 12, Z, 2030)
    S.prop(m, hhx + 2, hhy + 1, Z, 2322)
    S.prop(m, hhx + 1, hhy + 1, Z, 2358)
    m.sign(hhx - 1, hhy + 6, Z, "Hunters' Hall. Hunting tasks, bounties and the trophy loft.")
    m.npcs.append(("Taskmaster Ren", (hhx + 6, hhy + 4, Z)))
    m.npcs.append(("Bounty Warden Cass", (hhx + 11, hhy + 4, Z)))
    m.npcs.append(("Hunter Brannoch", (hhx + 15, hhy + 4, Z)))
    m.storey(hhx, hhy, 20, 15, Z - 1, floor="wood", style="stone")
    m.ladder(hhx + 18, hhy + 1, Z, name="hunters_hall")
    for px, py, pid in ((3, 3, 2519), (4, 3, 2523), (3, 10, 2472), (12, 10, 2429), (8, 6, 2322)):
        S.prop(m, hhx + px, hhy + py, Z - 1, pid)

    # ---- south of the high road: the inn, the training yard, Spire Manor (reserved) and the carriage station
    ix, iy = R(2, 53)
    claim("inn", ix, iy, 17, 15)
    m.building(ix, iy, 17, 15, Z, floor="wood", door_side="e", style="timber", doors=True)
    S.counter(m, ix + 2, iy + 3, 8, Z)
    for px, py in ((3, 8), (8, 8), (3, 12), (8, 12), (12, 10)):
        S.prop(m, ix + px, iy + py, Z, 2322)
        S.prop(m, ix + px + 1, iy + py, Z, 2358)
    S.prop(m, ix + 1, iy + 1, Z, 2519)
    S.prop(m, ix + 2, iy + 1, Z, 2523)
    m.sign(ix + 17, iy + 6, Z, "The Lantern & Lark. Food, drink, and rooms upstairs. Innkeeper Roan.")
    m.npcs.append(("Innkeeper Roan", (ix + 6, iy + 2, Z)))
    m.storey(ix, iy, 17, 15, Z - 1, floor="wood", style="timber")
    m.stairs(ix + 15, iy + 3, Z, name="hearthgate_inn")
    m.autowall([(ix + 8, iy + y) for y in range(1, 14) if y not in (6, 7, 8)], Z - 1, "timber")
    for px, py, pid in ((2, 2, 2322), (3, 2, 2358), (11, 2, 2322), (12, 2, 2358), (2, 12, 2519), (11, 12, 2523)):
        S.prop(m, ix + px, iy + py, Z - 1, pid)

    yx_, yy_ = R(21, 53)
    claim("training yard", yx_, yy_, 24, 15)
    m.fill(yx_, yy_, 24, 15, Z, "dirt")
    m.walls(yx_, yy_, 24, 15, Z, gaps={(yx_ + 23, yy_ + 6), (yx_ + 23, yy_ + 7), (yx_ + 12, yy_), (yx_ + 13, yy_)}, style="timber")
    for i, sid in enumerate(range(16198, 16203)):        # offline training statues: log out and train that skill slowly
        m.put(yx_ + 3 + i * 4, yy_ + 2, Z, sid)
    m.sign(yx_ + 21, yy_ + 4, Z, "Training Yard. Use a statue to log out and train that skill slowly while you're away.")
    for px, py in ((4, 9), (9, 9), (14, 9), (19, 9)):     # practice posts
        S.prop(m, yx_ + px, yy_ + py, Z, 2263)
    m.points["training_yard"] = (yx_ + 12, yy_ + 6, Z)

    claim("spire manor", *R(46, 53), 22, 16)              # Spire Manor, the showcase house, ends the avenue (built below)
    m.points["spire_manor_plot"] = R(46, 53) + (Z,)

    cx_, cy_ = R(74, 53)
    claim("carriage station", cx_, cy_, 35, 15)
    m.fill(cx_, cy_, 35, 15, Z, "dirt")
    m.building(cx_ + 22, cy_, 13, 10, Z, floor="wood", door_side="w", style="timber", doors=True)   # the coach house
    m.sign(cx_ + 21, cy_ + 3, Z, "Carriage Station. Coachman Ferro drives to Millcross and the Arrival Yard.")
    m.npcs.append(("Coachman Ferro", (cx_ + 18, cy_ + 5, Z)))
    m.points["carriage_hearthgate"] = (cx_ + 16, cy_ + 6, Z)
    for px, py, pid in ((3, 2, 2519), (4, 2, 2523), (3, 12, 2519), (9, 12, 2523), (14, 12, 2472)):
        S.prop(m, cx_ + px, cy_ + py, Z, pid)
    for px in (2, 6, 10, 14):                              # hitching posts
        S.prop(m, cx_ + px, cy_ + 8, Z, 2264)


    # ---- Spire Manor (Jay, 2026-11-11: "a beautiful house that will be pay to obtain only ... at least 3 levels high").
    # Four levels on the avenue's south end: the Grand Hall (display counters, statues, indoor fountain), the Trophy
    # Gallery (display rows, bookcases, weapon and armour racks), the private quarters (bedroom, study) and a rooftop
    # garden with a fountain and a telescope. Obtained only from the shop (!shop); !buyhouse refuses it. Cosmetic only.
    mx0, my0 = R(46, 53)
    MW, MH, MID = 22, 16, 99      # house 99: clear of every other floor's numbers
    m.building(mx0, my0, MW, MH, Z, floor="marble", door_side="n", style="white", doors=True)
    m.buildings[-1]["roof"] = None                       # the roof is the garden terrace instead
    for yy in range(my0 + 1, my0 + MH - 1):
        for xx in range(mx0 + 1, mx0 + MW - 1):
            if xx in (mx0 + 1, mx0 + MW - 2) or yy in (my0 + 1, my0 + MH - 2):
                m.ground[(xx, yy, Z)] = 410               # a black marble border round the hall
    m.put(mx0 + 10, my0 + 8, Z, 1922)                    # indoor fountain
    for px, py in ((3, 3), (18, 3), (3, 12), (18, 12)):
        S.prop(m, mx0 + px, my0 + py, Z, MARBLE_PILLAR)
    S.counter(m, mx0 + 2, my0 + 5, 6, Z, vertical=True)  # display counters along both side walls
    S.counter(m, mx0 + 19, my0 + 5, 6, Z, vertical=True)
    S.prop(m, mx0 + 6, my0 + 12, Z, ANGEL_STATUE)
    S.prop(m, mx0 + 15, my0 + 12, Z, HERO_STATUE)
    DG.hang(m, mx0, my0, MW, MH, Z, every=3, h_item=2670, v_item=DG.LAMP_V, offset=2)   # trophies on the north wall
    m.stairs(mx0 + 20, my0 + 3, Z, floor="wood", name="spire_manor_1")
    # level 2: the Trophy Gallery
    m.storey(mx0, my0, MW, MH, Z - 1, floor="wood", style="white")
    for row in (6, 10):
        S.counter(m, mx0 + 4, my0 + row, 13, Z - 1)      # two long display rows
    for px in (5, 7, 13, 15):
        S.prop(m, mx0 + px, my0 + 1, Z - 1, 2437)          # bookcases along the north wall
    DG.hang(m, mx0, my0, MW, MH, Z - 1, every=4, h_item=6110, v_item=DG.LAMP_V, offset=3)
    for px in (2, 10, 18):
        if (mx0 + px, my0, Z - 1) in m.items:
            m.put(mx0 + px, my0, Z - 1, 6112)              # armour racks between the weapon racks
    m.stairs(mx0 + 1, my0 + 3, Z - 1, floor="wood", name="spire_manor_2")
    # level 3: private quarters (bedroom west, study east)
    m.storey(mx0, my0, MW, MH, Z - 2, floor="wood", style="white")
    m.autowall([(mx0 + 11, my0 + y) for y in range(1, 15) if y not in (7, 8)], Z - 2, "white")
    for px, py, pid in ((3, 3, 2487), (6, 3, 2487), (2, 12, 2427), (8, 1, 2435), (15, 7, 2310), (17, 10, 2357), (13, 12, 2435)):
        S.prop(m, mx0 + px, my0 + py, Z - 2, pid)
    S.prop(m, mx0 + 2, my0 + 0, Z - 2, 2630)             # a mirror in the bedroom
    DG.hang(m, mx0, my0, MW, MH, Z - 2, every=5, offset=4)
    m.stairs(mx0 + 20, my0 + 3, Z - 2, floor="wood", name="spire_manor_3")
    # level 4: the rooftop garden (no roof: open to the sky)
    tz = Z - 3
    for yy in range(my0 + 1, my0 + MH):
        for xx in range(mx0 + 1, mx0 + MW):
            if (xx, yy, tz) not in m.ground:
                edge = xx in (mx0 + 1, mx0 + MW - 1) or yy in (my0 + 1, my0 + MH - 1)
                m.ground[(xx, yy, tz)] = 416 if edge or not (mx0 + 3 <= xx <= mx0 + MW - 3 and my0 + 3 <= yy <= my0 + MH - 3) else m.pick("grass")
    for xx in range(mx0 + 1, mx0 + MW):                  # a limestone balustrade round the edge
        for yy in (my0 + 1, my0 + MH - 1):
            if (xx, yy) != (mx0 + 20, my0 + 2):
                m.put(xx, yy, tz, 9273)
    for yy in range(my0 + 2, my0 + MH - 1):
        for xx in (mx0 + 1, mx0 + MW - 1):
            m.put(xx, yy, tz, 9272)
    m.put(mx0 + 10, my0 + 7, tz, 1922)                   # garden fountain
    for px, py in ((6, 5), (14, 5), (6, 11), (14, 11)):
        S.prop(m, mx0 + px, my0 + py, tz, 2370)
    for px, py in ((4, 4), (17, 4), (4, 12), (17, 12)):
        S.prop(m, mx0 + px, my0 + py, tz, 3619)
    S.prop(m, mx0 + 18, my0 + 13, tz, 3488)              # a telescope over the city
    m.flag(mx0 + 1, my0 + 1, MW - 1, MH - 1, tz, 0x0001)
    # the house itself: every floor tile on every level, plus the doorway
    tiles = []
    for zz in (Z, Z - 1, Z - 2, tz):
        for yy in range(my0 + 1, my0 + MH):
            for xx in range(mx0 + 1, mx0 + MW):
                if (xx, yy, zz) in m.ground and not (zz == Z and (xx == mx0 + MW - 1 or yy == my0 + MH - 1)):
                    m.house[(xx, yy, zz)] = MID
                    tiles.append((xx, yy, zz))
    m.house[(mx0 + 11, my0, Z)] = MID
    m.houses[MID] = {"name": "Spire Manor", "town": 1, "rent": 0, "entry": (mx0 + 11, my0 - 1, Z), "size": len(tiles) + 1}
    m.points["spire_manor"] = (mx0 + 10, my0 + 4, Z)
    m.sign(mx0 + 9, my0 - 1, Z, "Spire Manor. Four floors, a trophy gallery and a rooftop garden. Its deed is sold in the Spire Shop (!shop).")

    # ---- the houses: two streets along the south wall, the avenue down the middle to the south gate
    hid = 1
    styles = ["timber", "sand", "timber", "white", "brick", "timber", "sand"]
    west_xs, east_xs = (2, 11, 20, 29, 38, 47), (60, 69, 78, 87, 96)
    for row_y, side in ((72, "n"), (83, "s")):
        xs = west_xs + east_xs
        for k, hx_rel in enumerate(xs):
            hx, hy = tx + hx_rel, ty + row_y
            claim(f"house {hid}", hx, hy, 8, 8)
            st = styles[(k + (3 if side == "s" else 0)) % len(styles)]
            two = k in (0, len(west_xs) - 1, len(west_xs), len(xs) - 1)   # the houses at each end of a street have an upstairs
            m.house_building(hid, f"Lantern Row {hid}", hx, hy, 8, 8, Z, town=1, rent=2800 if two else 1500, door_side=side,
                             style=st, floor="marble" if st == "white" else "wood", storeys=2 if two else 1)
            fy = hy - 1 if side == "n" else hy + 8
            S.prop(m, hx + 2, fy, Z, 316)
            S.prop(m, hx + 6, fy, Z, 321)
            hid += 1
    # Underkeep grate (sealed; it becomes a secret in task 2.10)
    grate = R(3, 93) + (Z,)
    m.put(*grate, 435)
    m.sign(*R(5, 93), Z, "An old drain grate. Something echoes far below.")
    m.points["underkeep_grate"] = grate


    # ------------------------------------------------ housing outside the walls (cheaper, less safe)
    # Wallside Cabins: two clusters of ten small cabins beside the west and east roads. Fisher's Huts: ten on the river bank.
    for cluster, x_start in (("West", tx - 44), ("East", tx + tw + 5)):
        for row_y in (60, 69):
            for i in range(5):
                hx, hy = x_start + i * 8, ty + row_y
                claim(f"{cluster} cabin {hid}", hx, hy, 7, 6)
                m.house_building(hid, f"Wallside Cabin {hid}", hx, hy, 7, 6, Z, town=1, rent=600, door_side="n", style="brick")
                S.prop(m, hx + 1, hy - 1, Z, 316)
                S.prop(m, hx + 5, hy - 1, Z, rng.choice([2519, 116]))
                hid += 1
        lane0 = x_start - 2
        m.road((lane0, ty + 59), (lane0 + 43, ty + 59), Z, width=2, wind=False)
        m.road((lane0, ty + 68), (lane0 + 43, ty + 68), Z, width=2, wind=False)
    fisher = []
    for col_x in (X0 + 134, X0 + 146):
        for j in range(5):
            hx, hy = col_x, Y0 + 192 + j * 8
            claim(f"fisher hut {hid}", hx, hy, 7, 6)
            m.house_building(hid, f"Fisher's Hut {hid}", hx, hy, 7, 6, Z, town=1, rent=500, door_side="w", style="sand")
            S.prop(m, hx - 1, hy + 1, Z, rng.choice([2519, 116, 2523]))
            fisher.append((hx, hy))
            hid += 1
    m.npcs.append(("Fisher Corwin", (X0 + 143, Y0 + 190, Z)))
    m.sign(X0 + 143, Y0 + 192, Z, "Fisher's Huts. Cheap homes on the river bank, outside the city walls.")

    # ------------------------------------------------ roads
    m.road((tx - 60, ty + th // 2 + 1), (tx - 1, ty + th // 2 + 1), Z)      # west road (crosses the river: bridge)
    m.road((tx + tw, ty + th // 2 + 1), (tx + tw + 60, ty + th // 2 + 1), Z) # east road
    m.road((tx + tw // 2 + 1, Y0 + 90), (tx + tw // 2 + 1, ty - 1), Z)       # north road to the Pass (gate road)
    m.road((tx + tw // 2 + 1, ty + th), (tx + tw // 2 + 1, Y0 + 372), Z)     # south road
    m.road((X0 + 60, Y0 + 220), (X0 + 130, Y0 + 220), Z)                    # Millcross to the river bank
    m.road((X0 + 130, Y0 + 220), (tx - 60, ty + th // 2 + 1), Z)            # river bank to the west road
    m.road((tx + tw // 2, Y0 + 205), (X0 + 280, Y0 + 205), Z)               # north road east to the Burrow Hills
    m.road((X0 + 280, Y0 + 205), (X0 + 280, Y0 + 150), Z)                   # ... and on to the quarry
    m.road((tx + tw + 60, ty + th // 2 + 1), (X0 + 345, ty + th // 2 + 1), Z) # east road on towards the bandits and shards
    m.road((X0 + 345, ty + th // 2 + 1), (X0 + 345, Y0 + 232), Z)
    m.road((tx + tw // 2, Y0 + 368), (X0 + 175, Y0 + 368), Z)               # south road west to the Boar Meadow
    m.road((tx + tw // 2, Y0 + 368), (X0 + 345, Y0 + 368), Z)               # south road east to the Shard Fields
    m.road((X0 + 345, ty + th // 2 + 1), (X0 + 345, Y0 + 368), Z)
    m.road((X0 + 70, Y0 + 235), (X0 + 70, Y0 + 330), Z)                     # Millcross south to the Wolf Copse and Reedmarsh
    m.road((tx + tw // 2, Y0 + 110), (X0 + 160, Y0 + 110), Z)               # north road west to the Thornsnap Hollow
    m.road((X0 + 160, Y0 + 110), (X0 + 160, Y0 + 140), Z)

    # ------------------------------------------------ Millcross village (town 2 on floor 1)
    mx, my = X0 + MILLCROSS["x"], Y0 + MILLCROSS["y"]
    mw, mh = MILLCROSS["w"], MILLCROSS["h"]
    m.fill(mx, my, mw, mh, Z, "grass")
    for yy in range(my, my + mh):
        for xx in range(mx, mx + mw):
            m.clear_items(xx, yy, Z)
    m.fill(mx + 1, my + 16, mw - 2, 5, Z, "dirt")                      # the main street
    for i in range(4):
        m.fill(mx + 6 + i * 15, my + 21, 3, 3, Z, "dirt")             # paths to the front-row cottage doors
    m.fill(mx + 1, my + 32, mw - 2, 2, Z, "dirt")                     # the back lane, for the back-row cottage doors
    m.fill(mx + 1, my + 21, 2, 13, Z, "dirt")                         # ... joined to the main street at both ends
    m.fill(mx + 59, my + 21, 2, 13, Z, "dirt")
    m.fill(mx + 23, my + 14, 4, 3, Z, "dirt")                         # the inn's front path
    S.sprinkle(m, mx, my, mw, mh, Z, S.FLOWERS, 0.05, seed=50)                # flowers only: bushes block the way
    m.flag(mx, my, mw, mh, Z, 0x0001)
    m.building(mx + 18, my + 4, 14, 10, Z, floor="wood", door_side="s", style="white", doors=True)  # inn
    m.storey(mx + 18, my + 4, 14, 10, Z - 1, floor="wood", style="white")                          # guest rooms upstairs
    m.stairs(mx + 30, my + 6, Z, name="millcross_inn")
    m.autowall([(mx + 24, my + y) for y in range(5, 13) if y not in (8, 9)], Z - 1, "white")       # two rooms, a gap between
    for px, py, pid in ((20, 6, 2322), (21, 6, 2358), (27, 11, 2322), (28, 11, 2358), (20, 11, 2519), (28, 7, 2523)):
        S.prop(m, mx + px, my + py, Z - 1, pid)
    S.counter(m, mx + 20, my + 7, 8, Z)
    for px, py in ((mx + 20, my + 11), (mx + 24, my + 11), (mx + 28, my + 11)):
        S.prop(m, px, py, Z, 2322)
        S.prop(m, px + 1, py, Z, 2358)
    S.prop(m, mx + 20, my + 5, Z, 2519)
    S.prop(m, mx + 21, my + 5, Z, 2523)
    m.sign(mx + 25, my + 15, Z, "Millcross Inn")
    m.npcs.append(("Miller Agna", (mx + 24, my + 9, Z)))
    m.npcs.append(("Innkeeper Bess", (mx + 28, my + 9, Z)))
    for row_y in (24, 34):
        for i in range(4):
            claim(f"cottage {hid}", mx + 3 + i * 15, my + row_y, 9, 8)
            m.house_building(hid, f"Millcross Cottage {hid}", mx + 3 + i * 15, my + row_y, 9, 8, Z, town=2, rent=800, door_side="n",
                             style=["timber", "sand", "timber", "brick"][(i + (row_y // 10)) % 4])
            S.prop(m, mx + 5 + i * 15, my + row_y - 1, Z, 316)
            hid += 1
    for px, py in ((mx + 10, my + 14), (mx + 40, my + 14)):                       # shade trees beside the street
        S.prop(m, px, py, Z, 3619)
    S.prop(m, mx + 25, my + 19, Z, 1922)
    m.towns.append((2, "Millcross", (mx + 25, my + 18, Z)))
    m.npcs.append(("Coachwoman Dara", (mx + 50, my + 19, Z)))                      # carriages to Hearthgate
    m.points["carriage_millcross"] = (mx + 48, my + 18, Z)
    m.sign(mx + 52, my + 17, Z, "Carriage stop. Coachwoman Dara drives to Hearthgate.")
    # the mill fields north of the village: wheat inside a fence
    fx, fy, fw, fh = mx + 4, my - 26, 30, 18
    S.patch(m, fx + fw // 2, fy + fh // 2, fw // 2, fh // 2, Z, "dirt", wobble=0.1)
    for yy in range(fy + 2, fy + fh - 2):
        for xx in range(fx + 2, fx + fw - 2):
            if (xx + yy) % 2 == 0 and rng.random() < 0.75 and S.free(m, xx, yy, Z):
                m.put(xx, yy, Z, 3605)
    for xx in range(fx, fx + fw):
        for yy in (fy, fy + fh - 1):
            if S.free(m, xx, yy, Z):
                m.put(xx, yy, Z, 17233)
    for yy in range(fy + 1, fy + fh - 1):
        for xx in (fx, fx + fw - 1):
            if S.free(m, xx, yy, Z):
                m.put(xx, yy, Z, 17232)

    # ------------------------------------------------ the Arrival Yard (town 50): where every new character starts
    yx, yy = X0 + 270, Y0 + 336
    m.fill(yx, yy, 40, 24, Z, "grass")
    for xx in range(yx, yx + 40):
        for y2 in range(yy, yy + 24):
            m.clear_items(xx, y2, Z)
    m.fill(yx + 1, yy + 10, 38, 4, Z, "pave")  # the path, west to east
    m.walls(yx, yy, 40, 24, Z, style="white")
    m.flag(yx + 1, yy + 9, 8, 6, Z, 0x0001)    # the arrival square is safe; the rat pen is not
    spawn = (yx + 4, yy + 11, Z)
    m.towns.append((50, "Arrival Yard", spawn))
    m.points["tutorial_spawn"] = spawn
    m.sign(yx + 3, yy + 9, Z, "Welcome to the Spirebound tower. Click the ground to walk. Follow the stone path east: each stop teaches one thing. Guide Pell will help.")
    m.npcs.append(("Guide Pell", (yx + 6, yy + 11, Z)))
    S.sprinkle(m, yx + 1, yy + 1, 38, 8, Z, S.FLOWERS + S.BUSHES, 0.12, seed=40)
    S.sprinkle(m, yx + 1, yy + 14, 38, 9, Z, S.FLOWERS + S.BUSHES, 0.12, seed=41)
    for px in (yx + 10, yx + 20, yx + 26):
        S.lamp(m, px, yy + 9, Z)
        S.lamp(m, px, yy + 14, Z)
    pen = (yx + 13, yy + 2, 11, 6)
    m.walls(pen[0], pen[1], pen[2], pen[3], Z, gaps={(pen[0] + 5, pen[1] + 5)}, style="timber")
    m.fill(pen[0] + 1, pen[1] + 1, pen[2] - 2, pen[3] - 2, Z, "dirt")
    m.clear_items(pen[0] + 5, pen[1] + 5, Z)
    m.flag(pen[0] + 5, pen[1] + 5, 1, 1, Z, 0x0001)  # the pen's gap is a safe tile: rats can't cross it, players can
    m.fill(pen[0] + 5, pen[1] + 6, 1, 4, Z, "pave")  # little path from the gap down to the main path
    m.monsters.append(("Pen Rat", (pen[0] + 5, pen[1] + 3, Z), 3, 3, 15))
    m.points["tutorial_pen"] = (pen[0] + 5, pen[1] + 4, Z)
    m.sign(yx + 11, yy + 9, Z, "Stop 1: Fighting. Click a rat in the pen to attack it. Rats are weak. When it falls, open the body (right-click) and take what it carries.")
    m.sign(yx + 21, yy + 9, Z, "Stop 2: Sword skills and spells. The bar on the right holds your skills (Shift+1..6). Say !spells to see what you will learn. Press J for your Journal.")
    m.sign(yx + 27, yy + 9, Z, "Stop 3: The Registrar's hall is ahead. Choose your path and how hard you want to live. Then you are sent to Hearthgate.")
    m.building(yx + 29, yy + 7, 10, 10, Z, floor="marble", door_side="w", style="white", doors=True)
    S.carpet(m, yx + 31, yy + 9, 6, 6, Z, 2576)
    m.npcs.append(("Registrar Maelis", (yx + 34, yy + 12, Z)))
    m.points["tutorial_registrar"] = (yx + 34, yy + 12, Z)
    yard_x, yard_y = yx, yy                       # kept for the zones below (yx/yy are reused as loop names later)

    # ------------------------------------------------ apex spawn: the Old Watchtower (Contested from task 2.2)
    ax, ay = X0 + 30, Y0 + 30
    m.fill(ax, ay, 44, 44, Z, "stonefloor")
    for yy in range(ay, ay + 44):
        for xx in range(ax, ax + 44):
            m.clear_items(xx, yy, Z)
    m.walls(ax, ay, 44, 44, Z, gaps={(ax + 22, ay + 43), (ax + 23, ay + 43)}, style="stone")
    m.walls(ax + 12, ay + 12, 20, 20, Z, gaps={(ax + 22, ay + 31)}, style="stone")  # the packed inner room
    m.monsters.append(("Stonehorn Ram", (ax + 8, ay + 36, Z), 3, 3, 90))
    m.monsters.append(("Stonehorn Ram", (ax + 36, ay + 36, Z), 3, 3, 90))
    m.monsters.append(("Stonehorn Ram", (ax + 22, ay + 22, Z), 4, 8, 90))
    # dressing: an overgrown courtyard around a paved keep, broken masonry, braziers in the keep
    for yy in range(ay + 1, ay + 43):
        for xx in range(ax + 1, ax + 43):
            if not (ax + 12 <= xx < ax + 32 and ay + 12 <= yy < ay + 32) and not m.items.get((xx, yy, Z)):
                m.ground[(xx, yy, Z)] = m.pick("grass")
    m.fill(ax + 21, ay + 32, 4, 11, Z, "stonefloor")                  # flagstone path from the gate to the keep
    keep_out = DG.keep_clear(m, Z) | {(ax + 40, ay + 3), (ax + 39, ay + 4)}
    S.patch(m, ax + 10, ay + 8, 4, 3, Z, "dirt")
    S.patch(m, ax + 34, ay + 30, 4, 3, Z, "dirt")
    DG.scatter(m, ax + 1, ay + 1, 42, 42, Z, DG.DEBRIS + [2264, 2290], 40, avoid=keep_out)
    DG.scatter(m, ax + 1, ay + 1, 42, 42, Z, DG.RUBBLE + DG.PILLARS, 14, solid=True, avoid=keep_out)
    DG.scatter(m, ax + 1, ay + 1, 42, 42, Z, S.BUSHES + S.FERNS, 25, avoid=keep_out)
    for bx_, by_ in ((ax + 14, ay + 14), (ax + 29, ay + 14), (ax + 14, ay + 29), (ax + 29, ay + 29)):
        S.prop(m, bx_, by_, Z, DG.COAL_BASIN)
    DG.scatter(m, ax + 13, ay + 13, 18, 18, Z, DG.BONES, 14, avoid=keep_out)
    DG.hang(m, ax + 12, ay + 12, 20, 20, Z, every=4, h_item=DG.TORCH_H, v_item=DG.TORCH_V)
    for rx_, ry_ in ((ax + 41, ay + 3), (ax + 41, ay + 2)):         # the rope spot hides behind rubble
        S.replace(m, rx_, ry_, Z, DG.RUBBLE[0])
    # semi-hidden rope spot to the cliff caves (z 8), a Deadzone later
    cx, cy, cz = ax, ay, 8
    DG.cave(m, DG.blob(cx, cy, 44, 44, [(cx + 4, cy + 4), (cx + 3, cy + 3), (cx + 22, cy + 22)], m.rng, seed=3), cz)
    m.teleport((ax + 40, ay + 3, Z), (cx + 4, cy + 4, cz), "apex_rope_spot")
    m.teleport((cx + 3, cy + 3, cz), (ax + 39, ay + 4, Z), "apex_cave_exit")
    m.monsters.append(("Stonehorn Ram", (cx + 22, cy + 22, cz), 5, 9, 90))
    cave_out = DG.keep_clear(m, cz)
    DG.scatter(m, cx, cy, 44, 44, cz, DG.STALAGMITES, 45, solid=True, avoid=cave_out)
    DG.scatter(m, cx, cy, 44, 44, cz, DG.CRYSTALS, 6, solid=True, avoid=cave_out)
    DG.scatter(m, cx, cy, 44, 44, cz, DG.BONES + DG.DEBRIS, 30, avoid=cave_out)
    m.points["apex_watchtower"] = (ax + 22, ay + 40, Z)

    # ------------------------------------------------ the Pass (field boss arena) and the labyrinth
    px, py = gate_n[0] - 12, Y0 + 70
    m.fill(px, py, 24, 20, Z, "stonefloor")
    for yy in range(py, py + 20):
        for xx in range(px, px + 24):
            m.clear_items(xx, yy, Z)
    m.walls(px, py, 24, 20, Z, gaps={(px + 12, py + 19), (px + 13, py + 19), (px + 12, py), (px + 13, py)}, style="stone")
    DG.flagstones(m, px + 3, py + 3, 18, 14, Z, 351)                  # a trampled dirt pit inside a flagstone ring
    m.points["gate_hound_spawn"] = (px + 12, py + 9, Z)  # spawned by script (it never returns once dead)
    m.points["pass_arena"] = (px + 12, py + 10, Z)
    # sealed until the Gate Hound dies once (scripts remove the boulders)
    for i, gx in enumerate((px + 12, px + 13)):
        m.put(gx, py, Z, 1772)
        m.points[f"gate_pass_{i + 1}"] = (gx, py, Z)
    pass_out = DG.keep_clear(m, Z) | {(px + 12, py + 18), (px + 13, py + 18), (px + 12, py + 1), (px + 13, py + 1)}
    for qx, qy in ((px + 3, py + 3), (px + 20, py + 3), (px + 3, py + 16), (px + 20, py + 16)):
        S.prop(m, qx, qy, Z, DG.PILLAR)
    for qx, qy in ((px + 10, py + 2), (px + 15, py + 2), (px + 10, py + 17), (px + 15, py + 17)):
        S.prop(m, qx, qy, Z, DG.COAL_BASIN)
    DG.scatter(m, px + 4, py + 4, 16, 12, Z, DG.BONES + DG.DEBRIS, 22, avoid=pass_out)
    DG.hang(m, px, py, 24, 20, Z, every=4, h_item=DG.TORCH_H, v_item=DG.TORCH_V)
    # labyrinth level 1 (z 7) north of the Pass
    lx, ly = px - 10, Y0 + 12
    m.fill(px + 11, ly + 31, 4, py - (ly + 31), Z, "stonefloor")  # corridor from the Pass to the maze
    e1, x1 = m.maze(lx, ly, 14, 10, Z, seed=11)
    m.ground[(lx + 22, ly + 31, Z)] = 416; m.ground[(lx + 23, ly + 31, Z)] = 416
    for p in [(lx + 22, ly + 30, Z), (lx + 23, ly + 30, Z), (lx + 22, ly + 31, Z), (lx + 23, ly + 31, Z)]:
        m.clear_items(*p)
    # levels 2 and 3 (z 6, z 5) and the boss room (z 4) stacked above
    e2, x2 = m.maze(lx, ly, 14, 10, 6, floor="stonetile", seed=22)
    e3, x3 = m.maze(lx, ly, 14, 10, 5, floor="blackmarble", seed=33)
    m.teleport(x1, (e2[0] + 1, e2[1], 6), "lab1_up")
    m.teleport(x2, (e3[0] + 1, e3[1], 5), "lab2_up")
    m.teleport(e2, (x1[0] + 1, x1[1], Z), "lab2_down")
    m.teleport(e3, (x2[0] + 1, x2[1], 6), "lab3_down")
    m.monsters.append(("Ruin Sentinel", (lx + 20, ly + 15, Z), 4, 4, 90))
    m.monsters.append(("Ruin Archer", (lx + 20, ly + 15, 6), 4, 4, 90))
    m.monsters.append(("Ruin Sentinel", (lx + 20, ly + 15, 5), 4, 5, 90))
    for lz in (Z, 6, 5):                  # lamps on the corridor walls, cobwebs and old bones (nothing that blocks)
        lab_out = DG.keep_clear(m, lz)
        DG.hang_maze(m, lx, ly, 43, 31, lz, share=0.07)
        DG.scatter(m, lx, ly, 43, 31, lz, DG.COBWEBS, 40, avoid=lab_out)
        DG.scatter(m, lx, ly, 43, 31, lz, DG.BONES + DG.DEBRIS, 30, avoid=lab_out)
    # boss room (z 4) with a back chamber holding the stair to floor 2
    bx, by, bz = lx + 6, ly + 2, 4
    m.fill(bx, by, 30, 24, bz, "blackmarble")
    m.walls(bx, by, 30, 24, bz, style="stone")
    m.teleport(x3, (bx + 15, by + 21, bz), "lab3_up")
    m.teleport((bx + 15, by + 22, bz), (x3[0] + 1, x3[1], 5), "boss_room_exit")
    m.points["axe_lord_spawn"] = (bx + 15, by + 10, bz)  # spawned by script
    m.points["boss_room_floor1"] = (bx + 15, by + 12, bz)
    m.points["boss_room_floor1_nw"] = (bx + 1, by + 1, bz)
    m.points["boss_room_floor1_se"] = (bx + 28, by + 22, bz)
    m.sign(bx + 13, by + 21, bz, "Beyond this door the tower's protection ends.")
    # stair to floor 2 (sealed by a boulder until the first clear)
    m.put(bx + 15, by + 2, bz, 1772)
    m.points["gate_floor2"] = (bx + 15, by + 2, bz)
    # the stair sits in a walled back chamber: the boulder tile is the only way in (no walking around it)
    m.autowall([(wx, by + 2) for wx in range(bx + 1, bx + 29) if wx != bx + 15], bz, "stone")
    # dressing: a throne hall. Red runner from the door to the sealed stair, two rows of pillars, braziers, the throne
    hall_out = DG.keep_clear(m, bz) | {(bx + 15, by + 3), (bx + 14, by + 3), (bx + 16, by + 3)}
    DG.carpet_path(m, bx + 14, by + 3, 3, 19, bz, 2576)
    for qy in range(by + 6, by + 20, 4):
        for qx in (bx + 7, bx + 22):
            S.prop(m, qx, qy, bz, DG.PILLAR)
    for qx, qy in ((bx + 3, by + 4), (bx + 26, by + 4), (bx + 3, by + 20), (bx + 26, by + 20), (bx + 12, by + 4), (bx + 18, by + 4)):
        S.prop(m, qx, qy, bz, DG.COAL_BASIN)
    S.prop(m, bx + 17, by + 5, bz, DG.THRONE)
    DG.scatter(m, bx + 2, by + 4, 26, 18, bz, DG.BONES, 18, avoid=hall_out)
    DG.hang(m, bx, by + 2, 30, 22, bz, every=4, h_item=DG.CHAINS_H, v_item=DG.TORCH_V)

    # stair to floor 2: linked to Floor 2's landing by tools/mapgen.py (link_floors)
    m.points["stair_floor2_src"] = (bx + 15, by + 1, bz)

    # ------------------------------------------------ PvP zone tiers (DESIGN.md 6.3). Default everywhere: Open.
    m.zone("open", X0, Y0, SIZE, SIZE)
    # guarded ring: the city, its cabins and roads, the four starter camps, the fisher huts and the Arrival Yard
    m.zone("guarded", tx - 60, ty - 12, tw + 120, th + 24, 7)
    for c in CAMPS:
        if c["zone"] == "guarded":
            m.zone("guarded", X0 + c["x"] - 6, Y0 + c["y"] - 6, c["w"] + 12, c["h"] + 12, 7)
    m.zone("guarded", tx + 10, Y0 + 195, 70, 55, 7)                  # the gate road up to the Waspgrass Fields
    m.zone("guarded", X0 + 128, Y0 + 186, 30, 50, 7)                 # the fisher huts
    m.zone("guarded", yard_x - 2, yard_y - 2, 44, 28, 7)              # the Arrival Yard
    m.zone("guarded", mx - 20, my - 20, mw + 40, mh + 40, 7)         # around Millcross
    m.zone("contested", ax - 5, ay - 5, 54, 54, 7)                   # the Old Watchtower approach and outer layer
    m.zone("deadzone", ax + 12, ay + 12, 20, 20, 7)                  # the packed inner room
    m.zone("deadzone", cx, cy, 44, 44, 8)                            # the cliff caves below
    m.zone("bossroom", px, py, 24, 20, 7)                            # the Pass arena
    m.zone("bossroom", bx, by, 30, 24, 4)                            # the Axe-Lord's room
    for lvl in (7, 6, 5):                                             # the towns' upstairs rooms are town too
        m.zone("town", tx, ty, tw, th, lvl)
        m.zone("town", mx, my, mw, mh, lvl)

    # ------------------------------------------------ Floor 1 secrets (DESIGN.md 8.1). Trigger tiles only; no markers.
    def secret(sid, x, y, z=Z):
        if (x, y, z) not in m.ground:
            raise ValueError(f"secret {sid} has no ground at {(x, y, z)}")
        m.clear_items(x, y, z)  # trigger tiles must be walkable
        m.points["secret_" + sid] = (x, y, z)
    secret("s1", tx + 6, ty + 68)                       # beside the drain grate
    bm = m.points["camp_boar_meadow"]
    secret("s2", bm[0] + 18, bm[1] + 2)                 # mud wallow east of the boar meadow
    m.points["old_tusk_spawn"] = (bm[0] + 15, bm[1] + 4, Z)
    secret("s3", mx + 30, my + 8)                       # under the Millcross mill (inn back room)
    secret("s4", mx + 21, my + 6)                       # false pantry shelf in the inn
    secret("s5", X0 + 225, Y0 + 132)                    # cracked wall in the old quarry
    m.points["north_crack_exit"] = (mx + 25, my + 20, Z)
    secret("s6", mx + 44, my + 2)                       # hollow behind the Millcross well (night only)
    secret("s7", X0 + 352, Y0 + 186)                    # ruined shrine on the bandit road
    secret("s8", X0 + 330, Y0 + 330)                    # plates in the shard fields
    secret("s9", X0 + 44, Y0 + 300)                     # abandoned bedroll in the wolf copse
    secret("s10", X0 + 380, Y0 + 380)                   # ruined well in the south-east corner
    secret("s11", X0 + 160, Y0 + 170)                   # bramble ring in the thornsnap hollow
    secret("s12", X0 + 296, Y0 + 60)                    # broken stair of a ruined side tower near the Pass

    # ------------------------------------------------ The Underkeep, Wing 1 (DESIGN.md 3.4), under Hearthgate at z 8
    ux, uy, uz = tx, ty + 10, 8
    m.fill(ux, uy, 70, 50, uz, "stonetile")
    m.walls(ux, uy, 70, 50, uz, style="pale")
    # a water channel and column hall
    for y in range(uy + 3, uy + 47):
        m.ground[(ux + 20, y, uz)] = m.pick("water")
        m.ground[(ux + 21, y, uz)] = m.pick("water")
    for y in (uy + 15, uy + 16, uy + 30, uy + 31):  # crossings
        m.ground[(ux + 20, y, uz)] = 351
        m.ground[(ux + 21, y, uz)] = 351
    for cx_ in range(ux + 30, ux + 66, 6):
        for cy_ in range(uy + 6, uy + 46, 8):
            m.put(cx_, cy_, uz, ID_PILLAR)
    m.points["underkeep_entry"] = (ux + 4, uy + 4, uz)
    m.teleport((ux + 2, uy + 2, uz), (tx + 4, ty + 92, Z), "underkeep_exit")
    m.monsters.append(("Mire Toad", (ux + 10, uy + 25, uz), 4, 5, 90))
    m.monsters.append(("Mire Toad", (ux + 40, uy + 12, uz), 4, 4, 90))
    m.monsters.append(("Black Crawler", (ux + 45, uy + 30, uz), 4, 5, 90))
    m.monsters.append(("Black Crawler", (ux + 58, uy + 40, uz), 4, 4, 90))
    # daily chest room (scripted reward, task 2.10) and the sealed door to Wing 2
    m.points["underkeep_chest"] = (ux + 64, uy + 4, uz)
    m.walls(ux + 58, uy + 1, 11, 8, uz, gaps={(ux + 58, uy + 4)}, style="pale")
    S.carpet(m, ux + 60, uy + 3, 8, 3, uz, 5572)
    m.put(ux + 64, uy + 4, uz, 3515)  # an old stone altar used as the daily strongbox (scripted)
    m.points["underkeep_wing2_door"] = (ux + 69, uy + 25, uz)
    m.sign(ux + 67, uy + 25, uz, "A black iron door. Sealed until the tower reaches Floor 2.")
    # dressing: lamps, a storeroom by the entrance, damp and old bones, braziers in the column hall
    uk_out = DG.keep_clear(m, uz) | {(ux + 2, uy + 2), (ux + 3, uy + 3)}
    for qx, qy, pid in ((ux + 6, uy + 2, 2519), (ux + 7, uy + 2, 2523), (ux + 9, uy + 2, 2519), (ux + 2, uy + 7, 2523),
                        (ux + 2, uy + 8, 2519)):
        S.prop(m, qx, qy, uz, pid)
    DG.hang(m, ux, uy, 70, 50, uz, every=6)
    DG.scatter(m, ux + 1, uy + 1, 68, 48, uz, DG.COBWEBS, 35, avoid=uk_out)
    DG.scatter(m, ux + 1, uy + 1, 68, 48, uz, DG.BONES + DG.DEBRIS, 35, avoid=uk_out)
    DG.scatter(m, ux + 23, uy + 1, 34, 48, uz, [DG.COAL_BASIN], 6, solid=True, avoid=uk_out)

    # ------------------------------------------------ Underkeep Wings 2-6 (DESIGN.md 3.4): one per two floors cleared
    # wing: (x, y, z, w, h, monsters, opens when floor N is open, boss)
    wings = [
        (2, ux + 70, uy + 5, uz, 60, 40, ["Vault Rat", "Chain Ghoul"], 2, "Drain Matron"),
        (3, ux, uy, 9, 60, 50, ["Trap Mimic", "Iron Shade"], 4, None),
        (4, ux - 55, uy + 5, 9, 50, 40, ["Keep Warden", "Iron Shade"], 6, None),
        (5, ux, uy, 10, 40, 40, ["Keep Warden", "Chain Ghoul"], 8, "Vault Warden"),
        (6, ux + 45, uy, 10, 45, 40, ["Deep Sentinel", "Vault Wraith"], 10, "The Underkeeper"),
    ]
    prev_exit = {2: (ux + 69, uy + 25, uz)}
    for wid, wx, wy, wz, ww, wh, mons, req, boss in wings:
        m.fill(wx, wy, ww, wh, wz, "stonetile" if wid % 2 == 0 else "cavefloor")
        m.walls(wx, wy, ww, wh, wz, style="pale")
        for i, mon in enumerate(mons):
            for j in range(2):
                m.monsters.append((mon, (wx + 10 + j * (ww // 2), wy + 10 + i * (wh // 3), wz), 4, 4, 90))
        if boss:
            m.monsters.append((boss, (wx + ww - 8, wy + wh - 8, wz), 1, 1, 1800))
        entry = (wx + 3, wy + 3, wz)
        m.points[f"uk_wing{wid}_entry"] = entry
        m.points[f"uk_wing{wid}_req"] = (req, 0, 0)  # floor that opens it (read by scripts/spirebound/underkeep.lua)
        m.sign(wx + 4, wy + 1, wz, f"Underkeep, Wing {wid}.")
        wing_out = DG.keep_clear(m, wz) | {(wx + 3, wy + 3), (wx + 4, wy + 4), (wx + 2, wy + 2)}
        DG.hang(m, wx, wy, ww, wh, wz, every=6)
        DG.scatter(m, wx + 1, wy + 1, ww - 2, wh - 2, wz, DG.PILLARS + [DG.COAL_BASIN], ww * wh // 160, solid=True, avoid=wing_out)
        DG.scatter(m, wx + 1, wy + 1, ww - 2, wh - 2, wz, DG.COBWEBS + DG.BONES + DG.DEBRIS, ww * wh // 60, avoid=wing_out)
    # doors between wings: a portal guarded by a boulder until the wing opens
    links = [(2, (ux + 66, uy + 25, uz)), (3, (ux + 5, uy + 45, uz)), (4, (ux + 60, uy + 44, uz)),
             (5, (ux + 6, uy + 44, 9)), (6, (ux + 30, uy + 35, 10))]
    for wid, src in links:
        if src not in m.ground:
            continue
        m.clear_items(*src)
        e = m.points[f"uk_wing{wid}_entry"]
        m.teleport(src, (e[0] + 1, e[1] + 1, e[2]), f"uk_door{wid}")  # sealed by script until the wing opens
        m.points[f"uk_door{wid}_dest"] = (e[0] + 1, e[1] + 1, e[2])
        back = (e[0] - 1, e[1] - 1, e[2])
        m.teleport(back, (src[0] - 2, src[1], src[2]), f"uk_back{wid}")


    # ------------------------------------------------ The Arena (DESIGN.md 15, roadmap 5.7c): z 11, reached only by
    # event teleport. Engine PvP-zone flag (0x10): no skulls, no death loss. Two team starts and a banner tile.
    ax0, ay0, az = X0 + 10, Y0 + 10, 11
    m.fill(ax0, ay0, 40, 30, az, "sand")
    m.walls(ax0, ay0, 40, 30, az, style="pale")
    DG.flagstones(m, ax0 + 1, ay0 + 1, 38, 2, az, 416)
    DG.flagstones(m, ax0 + 1, ay0 + 27, 38, 2, az, 416)
    m.flag(ax0 + 1, ay0 + 1, 38, 28, az, 0x0010)
    for px_, py_ in ((ax0 + 12, ay0 + 9), (ax0 + 27, ay0 + 9), (ax0 + 12, ay0 + 20), (ax0 + 27, ay0 + 20)):
        m.put(px_, py_, az, ID_PILLAR)  # cover
    m.fill(ax0 + 18, ay0 + 13, 4, 4, az, "stonefloor")  # the banner square
    m.points["arena_a"] = (ax0 + 4, ay0 + 15, az)
    m.points["arena_b"] = (ax0 + 35, ay0 + 15, az)
    m.points["arena_center"] = (ax0 + 20, ay0 + 15, az)
    m.points["arena_nw"] = (ax0 + 1, ay0 + 1, az)
    m.points["arena_se"] = (ax0 + 38, ay0 + 28, az)
    m.zone("arena", ax0, ay0, 40, 30, az)
    S.carpet(m, ax0 + 3, ay0 + 14, 3, 3, az, 2576)                     # team starts: red and blue
    S.carpet(m, ax0 + 34, ay0 + 14, 3, 3, az, 5572)
    for qx, qy in ((ax0 + 2, ay0 + 3), (ax0 + 37, ay0 + 3), (ax0 + 2, ay0 + 26), (ax0 + 37, ay0 + 26)):
        S.prop(m, qx, qy, az, DG.COAL_BASIN)
    DG.hang(m, ax0, ay0, 40, 30, az, every=5, h_item=DG.TORCH_H, v_item=DG.TORCH_V)

    # ------------------------------------------------ Spire Siege keep (DESIGN.md 15, roadmap 5.7d): z 11, event
    # teleport only. Courtyard with four guild gates and the throne room in the middle (PvP-zone flag).
    sx0, sy0, sz = X0 + 70, Y0 + 10, 11
    m.fill(sx0, sy0, 60, 50, sz, "grass")
    m.walls(sx0, sy0, 60, 50, sz, style="pale")
    m.flag(sx0 + 1, sy0 + 1, 58, 48, sz, 0x0010)
    kx, ky = sx0 + 22, sy0 + 17
    for gx_, gy_ in ((sx0 + 4, sy0 + 4), (sx0 + 55, sy0 + 4), (sx0 + 4, sy0 + 45), (sx0 + 55, sy0 + 45)):
        m.road((gx_, gy_), (kx + 8, ky + 8), sz, width=3, key="cobble", wind=False)  # paved roads from each gate
    m.fill(kx, ky, 16, 16, sz, "marble")
    m.walls(kx, ky, 16, 16, sz, gaps={(kx + 8, ky), (kx + 8, ky + 15), (kx, ky + 8), (kx + 15, ky + 8)}, style="white", doors=True)
    m.points["siege_throne"] = (kx + 8, ky + 8, sz)
    m.points["siege_throne_nw"] = (kx + 1, ky + 1, sz)
    m.points["siege_throne_se"] = (kx + 14, ky + 14, sz)
    m.points["siege_gate_1"] = (sx0 + 4, sy0 + 4, sz)
    m.points["siege_gate_2"] = (sx0 + 55, sy0 + 4, sz)
    m.points["siege_gate_3"] = (sx0 + 4, sy0 + 45, sz)
    m.points["siege_gate_4"] = (sx0 + 55, sy0 + 45, sz)
    m.zone("siege", sx0, sy0, 60, 50, sz)
    DG.carpet_path(m, kx + 7, ky + 1, 3, 14, sz, 2576)
    DG.carpet_path(m, kx + 1, ky + 7, 14, 3, sz, 2576)
    S.prop(m, kx + 8, ky + 3, sz, DG.THRONE)
    for qx, qy in ((kx + 2, ky + 2), (kx + 13, ky + 2), (kx + 2, ky + 13), (kx + 13, ky + 13)):
        S.prop(m, qx, qy, sz, DG.PILLAR)
    DG.hang(m, kx, ky, 16, 16, sz, every=3)
    siege_out = DG.keep_clear(m, sz) | {(x, y) for x in range(kx - 1, kx + 17) for y in range(ky - 1, ky + 17)}
    for gx_, gy_ in ((sx0 + 4, sy0 + 4), (sx0 + 55, sy0 + 4), (sx0 + 4, sy0 + 45), (sx0 + 55, sy0 + 45)):
        for qx, qy in ((gx_ - 2, gy_ - 2), (gx_ + 2, gy_ - 2)):
            if (qx, qy) not in siege_out and (qx, qy, sz) in m.ground:
                S.prop(m, qx, qy, sz, DG.COAL_BASIN)
    DG.scatter(m, sx0 + 1, sy0 + 1, 58, 48, sz, S.BUSHES, 30, solid=True, avoid=siege_out)
    DG.scatter(m, sx0 + 1, sy0 + 1, 58, 48, sz, S.FLOWERS, 40, avoid=siege_out)

    # ------------------------------------------------ landmarks, lakes and forests (the world between the camps)
    S.pond(m, X0 + 330, Y0 + 92, 20, 12, Z, ring="mud")           # a lake in the north-east
    S.pond(m, X0 + 96, Y0 + 130, 11, 7, Z, ring="mud")            # a pond across the river
    S.ruin(m, X0 + 312, Y0 + 125, 14, 11, Z)                       # ruined watchtower by the lake
    S.ruin(m, X0 + 60, Y0 + 150, 11, 9, Z)                         # a roofless farmhouse across the river
    S.ruin(m, X0 + 300, Y0 + 372, 10, 8, Z)                        # a toppled shrine in the south-east
    S.standing_stones(m, X0 + 305, Y0 + 240, Z)                    # a ring of standing stones east of the city
    S.standing_stones(m, X0 + 30, Y0 + 350, Z)
    keep = [p for p in m.points.values() if p[2] == Z] + [pos for _n, pos, *_r in m.monsters if pos[2] == Z] + [pos for _n, pos in m.npcs if pos[2] == Z]
    S.forest(m, X0 + 4, Y0 + 4, SIZE - 8, SIZE - 8, Z, keep=keep)
