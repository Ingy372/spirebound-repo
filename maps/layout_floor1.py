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
import wilds  # noqa: E402
import designed  # noqa: E402
from floor1_plan import APEX, CAMPS, MILLCROSS, NEW_GROUND_TRAILS, TOWN  # noqa: E402


X0, Y0, Z = 1000, 1000, 7
ID_PILLAR = 2152  # a tall stone pillar: free-standing columns in the Underkeep and cover in the arena
SIZE = 400
PILLAR, PILLAR_VINE, MARBLE_PILLAR, HERO_STATUE, ANGEL_STATUE = 24001, 24003, 2153, 2027, 2031



# the labyrinth's guards (Floor 1 review A1-1): about twelve a level, three kinds mixed
LAB_RESPAWN = 120                     # real seconds (the old spawn file said 90, which the engine doubles)
LAB_PACKS = {
    7: [[("Ruin Sentinel", 1), ("Ruin Archer", 1), ("Hedge Hexer", 1)]] * 4,
    6: [[("Ruin Sentinel", 2), ("Ruin Archer", 1)], [("Ruin Sentinel", 1), ("Ruin Archer", 1), ("Hedge Hexer", 1)]] * 2,
    5: [[("Ruin Sentinel", 2), ("Ruin Archer", 1), ("Hedge Hexer", 1)]] * 3,
}


def _lab_spots(x0, y0, cells_w, cells_h, z, quiet, n, gap_quiet=9):
    """n maze cells (their top-left floor tile), each as far as possible from the quiet tiles (teleports, the way in)
    and from the cells already picked; never closer than gap_quiet to a quiet tile. Same result every build."""
    cells = [(x0 + cx * 3 + 1, y0 + cy * 3 + 1) for cy in range(cells_h) for cx in range(cells_w)]
    cells = [c for c in cells if min(max(abs(c[0] - q[0]), abs(c[1] - q[1])) for q in quiet) >= gap_quiet]
    picked, far = [], list(quiet)
    while len(picked) < n:
        if not cells:
            raise ValueError(f"labyrinth z{z}: only {len(picked)} of {n} pack cells fit")
        best = max(cells, key=lambda t: (min(max(abs(t[0] - p[0]), abs(t[1] - p[1])) for p in far), t))
        picked.append(best); far.append(best); cells.remove(best)
    return [(x, y, z) for x, y in picked]


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

    # ------------------------------------------------ Hearthgate v4 (docs/design/hearthgate_v4_plan.md, 2026-11-27): 112 x 96,
    # an eight-sided wall, the round Hearth Plaza with the Hearthstone at its centre. The tile plan is maps/hearthgate_plan.py,
    # the builder maps/hearthgate.py (it uses its own random numbers, so the town never shifts the rest of the map).
    tx, ty, tw, th = X0 + TOWN["x"], Y0 + TOWN["y"], TOWN["w"], TOWN["h"]
    import hearthgate
    import house_plans as HP
    hid = hearthgate.build(m, tx, ty, Z, claim)
    # The old town drew from the map's random numbers and everything after it (scenery, spawn spots on every floor)
    # depended on where it left them. Put them back exactly there, so the rebuild changes nothing outside the walls
    # (maps/rng_after_town.json was saved from the v3 town once; it never needs updating).
    import json
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "rng_after_town.json")) as f:
        _st = json.load(f)
    m.rng.setstate((_st["version"], tuple(_st["state"]), _st["gauss"]))
    gate_n = (tx + tw // 2, ty)


    # ------------------------------------------------ housing outside the walls (cheaper, less safe)
    # Wallside Cabins: two clusters of ten small cabins beside the west and east roads. Fisher's Huts: ten on the river bank.
    for cluster, x_start in (("West", tx - 44), ("East", tx + tw + 5)):
        for row_y in (60, 69):
            i = 0
            while i < 5:                                       # one double-width longhouse in every row, in a different place
                long_ = i == (0 if row_y == 60 else 3)
                cw = 15 if long_ else 7
                hx, hy = x_start + i * 8, ty + row_y
                claim(f"{cluster} cabin {hid}", hx, hy, cw, 6)
                plan = dict(HP.pick(hid), wall="along") if long_ else HP.pick(hid)
                m.house_building(hid, f"Wallside {'Longhouse' if long_ else 'Cabin'} {hid}", hx, hy, cw, 6, Z, town=1,
                                 rent=HP.rent_for(600, cw, 6, plan, standard=20), door_side="n", style="timber" if long_ else "brick")
                HP.fit(m, hid, hx, hy, cw, 6, Z, "n", "timber" if long_ else "brick", plan)
                S.prop(m, hx + 1, hy - 1, Z, 316)
                S.prop(m, hx + 5, hy - 1, Z, rng.choice([2519, 116]))
                hid += 1
                i += 2 if long_ else 1
        lane0 = x_start - 2
        m.road((lane0, ty + 59), (lane0 + 43, ty + 59), Z, width=2, wind=False)
        m.road((lane0, ty + 68), (lane0 + 43, ty + 68), Z, width=2, wind=False)
    fisher = []
    for col_x in (X0 + 134, X0 + 146):
        j = 0
        while j < 5:                                           # one double-length boathouse in each column
            long_ = j == (1 if col_x == X0 + 134 else 3)
            chh = 14 if long_ else 6
            hx, hy = col_x, Y0 + 192 + j * 8
            claim(f"fisher hut {hid}", hx, hy, 7, chh)
            plan = dict(HP.pick(hid), wall="along") if long_ else HP.pick(hid)
            m.house_building(hid, f"Fisher's {'Boathouse' if long_ else 'Hut'} {hid}", hx, hy, 7, chh, Z, town=1,
                             rent=HP.rent_for(500, 7, chh, plan, standard=20), door_side="w", style="timber" if long_ else "sand")
            HP.fit(m, hid, hx, hy, 7, chh, Z, "w", "timber" if long_ else "sand", plan)
            S.prop(m, hx - 1, hy + 1, Z, rng.choice([2519, 116, 2523]))
            fisher.append((hx, hy))
            hid += 1
            j += 2 if long_ else 1
    m.npcs.append(("Fisher Corwin", (X0 + 143, Y0 + 190, Z)))
    m.sign(X0 + 143, Y0 + 192, Z, "Fisher's Huts. Cheap homes on the river bank, outside the city walls.")

    # ------------------------------------------------ roads
    m.road((tx - 60, ty + th // 2 + 1), (tx - 1, ty + th // 2 + 1), Z)      # west road (crosses the river: bridge)
    m.road((tx + tw, ty + th // 2 + 1), (X0 + 338, ty + th // 2 + 1), Z)     # East Road, gate to East Cross
    m.road((tx + tw // 2 + 1, Y0 + 90), (tx + tw // 2 + 1, ty - 1), Z)       # north road to the Pass (gate road)
    m.road((tx + tw // 2 + 1, ty + th), (tx + tw // 2 + 1, Y0 + 372), Z)     # south road
    m.road((X0 + 60, Y0 + 220), (X0 + 130, Y0 + 220), Z)                    # Millcross to the river bank
    m.road((X0 + 130, Y0 + 220), (tx - 60, ty + th // 2 + 1), Z)            # river bank to the west road
    m.road((tx + tw // 2, Y0 + 368), (X0 + 304, Y0 + 368), Z)               # Shrine Path, to the toppled shrine
    m.road((X0 + 303, Y0 + 368), (X0 + 303, Y0 + 371), Z, width=2, wind=False)   # ... up to its broken north door (M5)
    # from East Cross: the Bandit Track north and the Shard Track south (2-wide trails)
    for a, b in (((338, 285), (368, 285)), ((368, 285), (368, 226)), ((368, 226), (354, 224)), ((354, 224), (354, 220)),
                 ((338, 285), (338, 292)), ((338, 292), (366, 296)), ((366, 296), (366, 299)), ((234, 144), (239, 144))):
        m.road((X0 + a[0], Y0 + a[1]), (X0 + b[0], Y0 + b[1]), Z, width=2, wind=False)
    # gate trails (2 wide) from the roads to the hunting grounds' gates (FLOOR1_WILDS_PLAN.md 4.2)
    for a, b in (((153, 284), (153, 282)), ((323, 284), (323, 282)), ((231, 335), (206, 335)), ((206, 335), (206, 337)), ((230, 205), (228, 205)),
                 ((234, 199), (239, 199)), ((230, 152), (218, 152)), ((92, 282), (88, 282))):
        m.road((X0 + a[0], Y0 + a[1]), (X0 + b[0], Y0 + b[1]), Z, width=2, wind=False)
    # 10.4: trails to the three new grounds (the Bramble Run from the north road; Smugglers' Ridge and the Fallen Bastion
    # down the east edge to the Bandit Track)
    for path in NEW_GROUND_TRAILS.values():
        for a, b in zip(path, path[1:]):
            m.road((X0 + a[0], Y0 + a[1]), (X0 + b[0], Y0 + b[1]), Z, width=2, wind=False)
    # Copse Road: Millcross's south side down past Wolf Copse to the Reedmarsh gate
    for a, b in (((70, 239), (92, 250)), ((92, 250), (92, 310)), ((92, 310), (70, 318)), ((70, 318), (70, 321))):
        m.road((X0 + a[0], Y0 + a[1]), (X0 + b[0], Y0 + b[1]), Z, width=3, wind=False)
    # Cabin Lane: from the west cabins' back lane down to the Boar Meadow gate (a 2-wide trail)
    m.road((X0 + 172, Y0 + 304), (X0 + 172, Y0 + 314), Z, width=2, wind=False)
    m.road((X0 + 172, Y0 + 314), (X0 + 159, Y0 + 337), Z, width=2, wind=False)

    # Watch Road: from Millcross's north side up to the Old Watchtower's gate (the tower had no road before)
    for a, b in (((76, 194), (76, 110)), ((76, 110), (52, 84)), ((52, 84), (52, 74))):
        m.road((X0 + a[0], Y0 + a[1]), (X0 + b[0], Y0 + b[1]), Z, width=2, wind=False)

    # ------------------------------------------------ the rebuilt hunting grounds (maps/wilds.py): walls, hub, four loops
    for c in CAMPS:
        if c.get("design"):                                   # FLOOR1_HUNTING_PLAN.md: drawn from clearings, several levels
            designed.build(m, c)
            continue
        L = wilds.build(m, c)
        if c["den"]:
            wilds.cave(m, L)                                  # the party cave below (z 8)

    # ------------------------------------------------ signposts at the junctions (FLOOR1_WILDS_PLAN.md 4.2)
    def lv(cid):
        c = next(c for c in CAMPS if c["id"] == cid)
        return f"{c['title']}, levels {c['levels'][0]}-{c['levels'][1]}"
    posts = [
        ((233, 213), f"West: {lv('wasp_fields')}. East: {lv('burrow_hills')}. North: the Pass. South: Hearthgate."),
        ((233, 148), f"West: {lv('thornsnap_hollow')}. East: {lv('old_quarry')}. North: the Pass and the Gate Hound."),
        ((231, 338), f"West: {lv('starter_south')}. South: the shrine path. North: Hearthgate."),
        ((153, 288), f"North: {lv('starter_west')}. South: the west cabins and {lv('boar_meadow')}. West: the river and Millcross."),
        ((320, 288), f"North: {lv('starter_east')}. East: East Cross. West: Hearthgate."),
        ((341, 288), f"North: {lv('bandit_road')}. South: {lv('shard_fields')}. West: Hearthgate."),
        ((172, 302), f"South: {lv('boar_meadow')}. North: the Mill Road."),
        ((95, 282), f"West: {lv('wolf_copse')}. South: {lv('reed_marsh')}. North: Millcross."),
        ((73, 242), f"South: {lv('wolf_copse')} and {lv('reed_marsh')}. North: Millcross."),
        ((79, 192), "North: The Old Watchtower, levels 28-40. Contested: other players can attack you there."),
    ]
    roads_ = getattr(m, "road_tiles", set())
    for (sx_, sy_), text in posts:
        spot = min(((X0 + sx_ + a, Y0 + sy_ + b) for a in range(-3, 4) for b in range(-3, 4)
                    if S.free(m, X0 + sx_ + a, Y0 + sy_ + b, Z) and (X0 + sx_ + a, Y0 + sy_ + b, Z) not in roads_),
                   key=lambda t: (abs(t[0] - X0 - sx_) + abs(t[1] - Y0 - sy_), t))
        m.sign(*spot, Z, text)

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
    m.npcs.append(("Innkeeper Bess", (mx + 28, my + 9, Z)))
    for row_y in (24, 34):
        for i in range(4):
            claim(f"cottage {hid}", mx + 3 + i * 15, my + row_y, 9, 8)
            cst = ["timber", "sand", "timber", "brick"][(i + (row_y // 10)) % 4]
            cx0, cy0, cw, ch, plan = HP.footprint(hid, mx + 3 + i * 15, my + row_y, 9, 8, "n")
            m.house_building(hid, f"Millcross Cottage {hid}", cx0, cy0, cw, ch, Z, town=2, rent=HP.rent_for(800, cw, ch, plan, standard=42),
                             door_side="n", style=cst)
            HP.fit(m, hid, cx0, cy0, cw, ch, Z, "n", cst, plan)
            if (cw, ch) != (9, 8):
                HP.yard(m, (mx + 3 + i * 15, my + row_y, 9, 8), (cx0, cy0, cw, ch), Z, S, rng)
            S.prop(m, mx + 5 + i * 15, my + row_y - 1, Z, 316)
            hid += 1
    for px, py in ((mx + 10, my + 14), (mx + 45, my + 14)):                       # shade trees beside the street
        S.prop(m, px, py, Z, 3619)
    # the Watch Road comes down from the north and stopped at the village edge (map review M5): carry it to the street
    m.road((X0 + 76, Y0 + 194), (X0 + 76, my + 16), Z, width=2, wind=False)
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
    # the mill itself (map review M9: Millcross had none; Agna stood in the inn). A stone mill house east of the Watch
    # Road, across from the wheat, door to the road; the millstone in the middle, sacks of flour along the walls.
    lx_, ly_, lw_, lh_ = mx + 44, my - 15, 9, 8
    claim("Agna's mill", lx_, ly_, lw_, lh_)
    for yy in range(ly_ - 2, ly_ + lh_ + 2):
        for xx in range(lx_ - 3, lx_ + lw_ + 2):
            m.clear_items(xx, yy, Z)
    m.building(lx_, ly_, lw_, lh_, Z, floor="wood", door_side="w", style="stone", doors=True)
    door_y = ly_ + lh_ // 2
    m.fill(lx_ - 3, door_y, 3, 1, Z, "dirt")                         # a step of path from the road to the door
    S.prop(m, lx_ + 4, ly_ + 3, Z, 1943)                              # the millstone
    for px_, py_, pid in ((1, 1, 2523), (2, 1, 2519), (7, 1, 2523), (7, 6, 2519), (6, 6, 116), (1, 6, 117)):
        S.prop(m, lx_ + px_, ly_ + py_, Z, pid)
    m.npcs.append(("Miller Agna", (lx_ + 3, ly_ + 5, Z)))
    m.sign(lx_ - 1, door_y - 2, Z, "Agna's Mill")
    mill = (lx_, ly_)

    # ------------------------------------------------ the Arrival Yard (town 50): where every new character starts
    # Roadmap R11: a walled path with four gates; each opens after one small step (kill a rat, loot it, learn about
    # skills and spells, drink a potion), and the Registrar waits at the end. Gate rules: scripts/spirebound/tutorial.lua.
    YW, YH = 64, 24
    yx, yy = X0 + 270, Y0 + 336
    m.fill(yx, yy, YW, YH, Z, "grass")
    for xx in range(yx, yx + YW):
        for y2 in range(yy, yy + YH):
            m.clear_items(xx, y2, Z)
    m.fill(yx + 1, yy + 10, 52, 4, Z, "pave")  # the path, west to east
    m.walls(yx, yy, YW, YH, Z, style="white")
    m.flag(yx + 1, yy + 9, 8, 6, Z, 0x0001)    # the arrival square is safe; the rat pen is not
    spawn = (yx + 4, yy + 11, Z)
    m.towns.append((50, "Arrival Yard", spawn))
    m.points["tutorial_spawn"] = spawn
    m.sign(yx + 3, yy + 9, Z, "Welcome to the Spirebound tower. Click the ground to walk. Follow the stone path east: each "
           "gate opens when you have learned one thing (click a gate to open it). Guide Pell will help.")
    m.npcs.append(("Guide Pell", (yx + 6, yy + 11, Z)))
    gates = [(26, "kill", "Gate 1: beat a rat in the pen, then click the gate."), (32, "loot", "Gate 2: open a rat's body and take what it carried, then click the gate."),
             (38, "spells", "Gate 3: say !spells to see the skills and spells you will learn, then click the gate."),
             (44, "potion", "Gate 4: drink the health potion in your backpack, then click the gate.")]
    for gx, step, text in gates:                        # a timber fence right across the yard, a gap on the path
        line = [(yx + gx, y2) for y2 in range(yy + 1, yy + YH - 1)]
        m.autowall([t for t in line if t[1] not in (yy + 11, yy + 12)], Z, "timber")
        for y2 in (yy + 11, yy + 12):
            # a gap in the map; scripts/spirebound/tutorial.lua puts a click-to-open gate door here at start-up (C1)
            m.points[f"tutorial_gate_{step}_{y2 - yy - 10}"] = (yx + gx, y2, Z)
        m.sign(yx + gx - 1, yy + 9, Z, text)
    m.points["tutorial_yard_nw"] = (yx, yy, Z)
    m.points["tutorial_yard_se"] = (yx + YW - 1, yy + YH - 1, Z)
    S.sprinkle(m, yx + 1, yy + 1, 52, 8, Z, S.FLOWERS + S.BUSHES, 0.12, seed=40)
    S.sprinkle(m, yx + 1, yy + 14, 52, 9, Z, S.FLOWERS + S.BUSHES, 0.12, seed=41)
    for px in (yx + 2, yx + 10, yx + 21, yx + 29, yx + 35, yx + 41, yx + 48):   # yx + 2: the arrival square is lit at night
        S.lamp(m, px, yy + 9, Z)
        S.lamp(m, px, yy + 14, Z)
    # P7 (FLOOR1_REVIEW.md F1-01, Q47): the yard stands at the foot of the Spire. North of the arrival square, the
    # tower's sealed door between two pillars, and the first-clears stone (scripts/spirebound/monument.lua reads it).
    # (placed after the yard's flowers, on cleared tiles, so the shared random scenery elsewhere doesn't shift)
    for t in [(x_, yy + 3) for x_ in range(yx + 2, yx + 11)] + [(yx + 6, yy + 5), (yx + 10, yy + 5)]:
        m.clear_items(t[0], t[1], Z)
    m.autowall([(x_, yy + 3) for x_ in range(yx + 2, yx + 11) if x_ != yx + 6], Z, "stone")   # the tower's foot
    m.put(yx + 6, yy + 3, Z, 1772)                      # the sealed door: a boulder that never moves
    m.points["yard_spire_door"] = (yx + 6, yy + 3, Z)
    m.sign(yx + 6, yy + 5, Z, "The Spire. Its doors stay sealed until someone breaks each floor's guardian. "
           "Read the stone beside it: the names of everyone who opened a floor first.")
    S.prop(m, yx + 10, yy + 5, Z, 2199)                 # the first-clears stone
    m.points["yard_first_clears"] = (yx + 10, yy + 5, Z)
    # Stop 1, the Old Granary (Jay 2026-11-26: the open rat pen was "to basic"; "a house with a basement and the
    # basement is filled with rats", room for "a few new players joining at the same time"). A timber house on the
    # path, stairs down to a stone cellar (z 8) of four rat rooms, 13 rats in all. The stair room at the bottom is safe
    # (protection zone) and its doorway is a safe tile, so rats stay in the cellar and nobody is jumped on arrival.
    # Monsters never take stairs, so no rat reaches the yard. scripts/spirebound/tutorial.lua counts the cellar as
    # part of the yard (tutorial_cellar_nw/se).
    rng_state_granary = m.rng.getstate()                 # rebuilt late: the rest of the map's random scenery must not move
    CZ = Z + 1
    cx0, cy0, cw, ch = yx + 8, yy + 3, 26, 14            # the cellar's outer walls: x 8..33, y 3..16 (yard-relative)
    taken = [(x_, y_) for x_ in range(cx0, cx0 + cw) for y_ in range(cy0, cy0 + ch) if (x_, y_, CZ) in m.ground]
    assert not taken, f"the granary cellar would overlap something already at z {CZ}: {taken[:3]}"
    m.fill(cx0, cy0, cw, ch, CZ, "stonefloor")
    m.walls(cx0, cy0, cw, ch, CZ, style="stone")
    door_c = (yx + 14, yy + 8)                           # the stair room's doorway into the rat rooms
    stair_room = [(x_, yy + 8) for x_ in range(yx + 9, yx + 21) if (x_, yy + 8) != door_c] + \
                 [(yx + 20, y_) for y_ in range(yy + 4, yy + 8)]
    store_wall = [(x_, yy + 8) for x_ in range(yx + 24, yx + 33)]          # the north-east storeroom, open at x 21..23
    stubs = [(x_, y_) for x_ in (yx + 21, yx + 27) for y_ in range(yy + 12, yy + 16)]   # two stub walls: three bays
    m.autowall(stair_room, CZ, "stone")
    m.autowall(store_wall, CZ, "stone")
    m.autowall(stubs, CZ, "stone")
    m.flag(yx + 9, yy + 4, 11, 4, CZ, 0x0001)             # the stair room is safe ...
    m.flag(door_c[0], door_c[1], 1, 1, CZ, 0x0001)       # ... and so is its doorway: rats can't cross it, players can
    # the house above, door to the south (G8: doors a player must find face south or east)
    m.building(yx + 13, yy + 2, 12, 7, Z, floor="wood", door_side="s", style="timber", doors=True)
    m.stairs(yx + 15, yy + 4, CZ, floor="wood", name="granary")   # down: the hole at (15, 4, 7) -> (15, 5, 8); up: -> (15, 3, 7)
    m.fill(yx + 19, yy + 9, 1, 1, Z, "pave")              # a step of path from the door down to the stone path
    m.clear_items(yx + 19, yy + 9, Z)
    for px_, py_, pid in ((22, 3, 2523), (23, 3, 2519), (23, 4, 116), (14, 7, 117), (23, 7, 2519), (22, 7, 2523), (18, 3, 118)):
        S.prop(m, yx + px_, yy + py_, Z, pid)              # sacks and stores along the walls, away from the stairs and door
    m.sign(yx + 17, yy + 9, Z, "The Old Granary. Rats have taken its cellar: go in and take the stairs down.")
    # four rat rooms: the west hall, two bays between the stub walls, the north-east storeroom
    for (rx_, ry_), n_ in (((13, 12), 3), ((24, 13), 3), ((30, 13), 3), ((27, 5), 4)):
        m.monsters.append(("Pen Rat", (yx + rx_, yy + ry_, CZ), 2, n_, 15))    # (radius, count, respawn seconds)
    m.points["tutorial_pen"] = (yx + 24, yy + 12, CZ)    # the middle of the rat rooms (autopilot routes, the guide)
    m.points["tutorial_cellar_door"] = (door_c[0], door_c[1], CZ)
    m.points["tutorial_cellar_nw"] = (cx0, cy0, CZ)
    m.points["tutorial_cellar_se"] = (cx0 + cw - 1, cy0 + ch - 1, CZ)
    m.sign(yx + 10, yy + 6, CZ, "Stop 1 of 4: Fighting. This room is safe: rats can't come through the doorway. Go through and "
           "click a rat to attack it. When it falls, open the body (right-click) and take the cheese it carries.")
    DG.hang(m, cx0, cy0, cw, ch, CZ, every=5, h_item=DG.TORCH_H, v_item=DG.TORCH_V)
    DG.hang(m, cx0, yy + 8, cw, 9, CZ, every=5, h_item=DG.TORCH_H, v_item=DG.TORCH_V)   # the rat rooms' north walls
    # Claude's live walk-through (2026-11-26): the bays were too dark. Torches on the stub walls (the bays' west walls)
    # and a coal basin in the west hall.
    for sx_ in (21, 27):
        m.put(yx + sx_, yy + 13, CZ, DG.TORCH_V)
    S.prop(m, yx + 17, yy + 14, CZ, DG.COAL_BASIN)
    for px_, py_, pid in ((9, 4, 2523), (19, 4, 2519), (9, 7, 117), (19, 7, 116), (32, 4, 2523), (32, 5, 116), (21, 4, 2519),
                          (9, 15, 2519), (32, 15, 2523), (22, 15, 117), (26, 15, 116), (28, 15, 2519), (9, 9, 116)):
        S.prop(m, yx + px_, yy + py_, CZ, pid)             # barrels and crates in the corners
    keep_c = DG.keep_clear(m, CZ, spawn_r=0) | {(yx + 15, yy + y_) for y_ in range(4, 9)} | {(door_c[0], door_c[1] + 1)}
    DG.scatter(m, cx0 + 1, cy0 + 1, cw - 2, ch - 2, CZ, DG.COBWEBS + DG.BONES + DG.DEBRIS, 14, avoid=keep_c)
    m.rng.setstate(rng_state_granary)
    for _ in range(36):                                  # the old pen's dirt floor drew 36 random numbers: keep the count
        m.pick("dirt")
    m.sign(yx + 11, yy + 9, Z, "Stop 1 of 4: Fighting. Rats have taken the cellar of the Old Granary, the house just along the "
           "path. Go in, take the stairs down, and beat a rat. When it falls, open the body (right-click) and take what it carries.")
    m.sign(yx + 33, yy + 9, Z, "Stop 2 of 4: Skills and spells. Once you choose a path, the bar on the right holds the skills of the weapon in your hand (Ctrl+1..6), and !spells lists your spells. Press J for your Journal: its 'How do I' page answers most questions.")
    m.sign(yx + 45, yy + 9, Z, "Stop 3 of 4: The Registrar's hall is ahead, on the left where the path ends. Choose your path and how hard you want to live. Then the Proving, below the hall, before Hearthgate.")
    # G8 (Grok session 3): the hall used to close the path's east end with its door in the west wall, but the client
    # draws a roof one tile up and to the left, so a west (or north) door is hidden under it from outside: Grok saw "a
    # red roof with no door". Doors a player must find face south or east. The hall now stands north of the path's
    # end with its door in the south wall, right above the path, and a sign at the end points to it.
    # (rng saved and restored: added late, the rest of the map's random scenery must not move)
    rng_state_hall = m.rng.getstate()
    m.fill(yx + 53, yy + 10, 6, 4, Z, "pave")                      # the path runs on to the end of the hall
    m.building(yx + 50, yy + 2, 10, 8, Z, floor="marble", door_side="s", style="white", doors=True)
    S.carpet(m, yx + 55, yy + 6, 1, 3, Z, 2576)               # P7: a runner from the door to the Registrar
    m.sign(yx + 57, yy + 11, Z, "The Registrar's hall: its door is two steps west of here, in the wall on the north side of the path.")
    m.rng.setstate(rng_state_hall)
    m.npcs.append(("Registrar Maelis", (yx + 55, yy + 5, Z)))
    m.points["tutorial_registrar"] = (yx + 55, yy + 5, Z)
    import hearthgate_dress                       # P7: the yard dressed (the tower's foot, hedges, trees); nothing moves
    hearthgate_dress.dress_yard(m, yx, yy, YW, YH, Z)
    yard_x, yard_y = yx, yy                       # kept for the zones below (yx/yy are reused as loop names later)

    # ------------------------------------------------ the Proving (G2, Jay 2026-11-24: "continue the tutorial after
    # picking a class" with "a small one person boss fight"). Under the yard, z 9. The Registrar sends every new
    # character here: try your new spells on a few rats, then step on the glowing stone to face Bramblejaw alone in one
    # of three closed pits (scripts/spirebound/proving.lua). A portal skips straight to Hearthgate.
    rng_state = m.rng.getstate()                       # added late: don't re-roll the rest of the map
    PX, PY, PZ = yx + 4, yy + 1, 9
    m.fill(PX, PY, 22, 11, PZ, "stonefloor")
    m.walls(PX, PY, 22, 11, PZ, style="stone")
    m.points["proving_arrival"] = (PX + 3, PY + 5, PZ)
    m.points["proving_entry"] = (PX + 19, PY + 5, PZ)
    m.npcs.append(("Warden Ketta", (PX + 5, PY + 3, PZ)))
    m.monsters.append(("Pen Rat", (PX + 11, PY + 5, PZ), 3, 2, 15))
    m.sign(PX + 2, PY + 1, PZ, "Stop 4 of 4: The Proving. Try your new spells on the rats (they are on your action bar). "
           "When you are ready, step on the red glowing stone in the east to face Bramblejaw alone. The blue swirl in the "
           "north-east corner skips the fight and goes to Hearthgate (it asks first).")
    # the skip is scripted, not a map teleport (Grok session 2: the old portal and the fight stone both glowed blue and a
    # tester skipped the fight by mistake). scripts/spirebound/proving.lua asks once before sending you on.
    m.points["proving_skip"] = (PX + 20, PY + 1, PZ)
    DG.hang(m, PX, PY, 22, 11, PZ, every=5, h_item=DG.TORCH_H, v_item=DG.TORCH_V)
    for i in range(3):                                  # three closed pits, one climber each (no way in or out on foot)
        rx, ry = PX + i * 12, PY + 13
        m.fill(rx, ry, 11, 9, PZ, "stonefloor")
        m.walls(rx, ry, 11, 9, PZ, style="stone")
        m.points[f"proving_pit_{i + 1}_player"] = (rx + 2, ry + 4, PZ)
        m.points[f"proving_pit_{i + 1}_boss"] = (rx + 7, ry + 4, PZ)
        m.points[f"proving_pit_{i + 1}_nw"] = (rx + 1, ry + 1, PZ)
        m.points[f"proving_pit_{i + 1}_se"] = (rx + 9, ry + 7, PZ)
        DG.hang(m, rx, ry, 11, 9, PZ, every=4, h_item=DG.TORCH_H, v_item=DG.TORCH_V)
    keep = DG.keep_clear(m, PZ) | {(x_, y_) for x_ in range(PX + 1, PX + 21) for y_ in range(PY + 4, PY + 7)}  # the walk to the stone
    DG.scatter(m, PX + 1, PY + 1, 20, 9, PZ, DG.DEBRIS, 8, avoid=keep)
    for i in range(3):
        DG.scatter(m, PX + i * 12 + 1, PY + 14, 9, 7, PZ, DG.BONES, 4, avoid=keep)
    m.rng.setstate(rng_state)

    # ------------------------------------------------ apex spawn: the Old Watchtower (Contested from task 2.2)
    ax, ay = X0 + 30, Y0 + 30
    m.fill(ax, ay, 44, 44, Z, "stonefloor")
    for yy in range(ay, ay + 44):
        for xx in range(ax, ax + 44):
            m.clear_items(xx, yy, Z)
    m.walls(ax, ay, 44, 44, Z, gaps={(ax + 22, ay + 43), (ax + 23, ay + 43)}, style="stone")
    m.walls(ax + 12, ay + 12, 20, 20, Z, gaps={(ax + 22, ay + 31)}, style="stone")  # the packed inner room
    # fixed groups (FLOOR1_WILDS_PLAN.md Part 6): six of 3 round the courtyard, four of 4 in the inner room
    for gx_, gy_ in ((6, 6), (37, 6), (6, 22), (37, 22), (8, 37), (36, 37)):
        wilds.group(m, (ax + gx_, ay + gy_, Z), APEX["courtyard"]["groups"][0], APEX["courtyard"]["respawn"])
    for gx_, gy_ in ((16, 16), (27, 16), (16, 27), (27, 27)):
        wilds.group(m, (ax + gx_, ay + gy_, Z), APEX["inner"]["groups"][0], APEX["inner"]["respawn"])
    # dressing: an overgrown courtyard around a paved keep, broken masonry, braziers in the keep
    for yy in range(ay + 1, ay + 43):
        for xx in range(ax + 1, ax + 43):
            if not (ax + 12 <= xx < ax + 32 and ay + 12 <= yy < ay + 32) and not m.items.get((xx, yy, Z)):
                m.ground[(xx, yy, Z)] = m.pick("grass")
    m.fill(ax + 21, ay + 32, 4, 11, Z, "stonefloor")                  # flagstone path from the gate to the keep
    m.points["apex_watchtower"] = (ax + 22, ay + 40, Z)                # set first, so no decoration lands on it
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
    for spot in wilds.spread(m, cx, cy, 44, 44, cz, 8, 9, avoid=[(cx + 4, cy + 4), (cx + 3, cy + 3)]):   # eight groups of 4
        wilds.group(m, spot, APEX["cave"]["groups"][0], APEX["cave"]["respawn"])
    cave_out = DG.keep_clear(m, cz)
    DG.scatter(m, cx, cy, 44, 44, cz, DG.STALAGMITES, 45, solid=True, avoid=cave_out)
    DG.scatter(m, cx, cy, 44, 44, cz, DG.CRYSTALS, 6, solid=True, avoid=cave_out)
    DG.scatter(m, cx, cy, 44, 44, cz, DG.BONES + DG.DEBRIS, 30, avoid=cave_out)

    # ------------------------------------------------ the Pass (field boss arena) and the labyrinth
    px, py = gate_n[0] - 12, Y0 + 70
    m.fill(px, py, 24, 20, Z, "stonefloor")
    for yy in range(py, py + 20):
        for xx in range(px, px + 24):
            m.clear_items(xx, yy, Z)
    m.walls(px, py, 24, 20, Z, gaps={(px + 12, py + 19), (px + 13, py + 19), (px + 12, py), (px + 13, py)}, style="stone")
    DG.flagstones(m, px + 3, py + 3, 18, 14, Z, 351)                  # a trampled dirt pit inside a flagstone ring
    m.points["gate_hound_spawn"] = (px + 12, py + 9, Z)  # spawned by script; it returns 10 minutes after a kill
    m.sign(px + 10, py + 20, Z, "The Pass. The Gate Hound guards the way to the Floor 1 labyrinth. Come with a party of "
           "three or more: alone, it will tear you apart.")       # FLOOR1_REVIEW.md F1-44
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
    # corridor from the Pass to the maze, walled on both sides (map review M1: it was open meadow, so the labyrinth could
    # be entered past the arena without the Gate Hound). Left wall on the meadow, right wall on the floor.
    m.fill(px + 11, ly + 31, 5, py - (ly + 31), Z, "stonefloor")
    for yy in range(ly + 31, py):
        for xx in (px + 10, px + 15):
            m.clear_items(xx, yy, Z)
    m.autowall([(xx, yy) for yy in range(ly + 31, py) for xx in (px + 10, px + 15)], Z, "stone")
    # the seal test (tools/mapgen.py): with the boulders in place, no walk from the temple may reach inside the maze
    m.seals = getattr(m, "seals", []) + [dict(name="Floor 1 Pass", boulders=[(px + 12, py, Z), (px + 13, py, Z)],
                                              inside=(px + 12, ly + 29, Z), box=(lx, ly, lx + 43, py + 20))]
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
    # about twelve guards per level in mixed packs (Floor 1 review A1-1): a melee Ruin Sentinel in front, a Ruin Archer
    # behind, a Hedge Hexer mending them. Packs stand in maze cells far from the teleports, the Pass corridor and each
    # other, so a party can step off a teleport and choose its fight.
    for lz, packs in LAB_PACKS.items():
        quiet = [(px_, py_) for px_, py_, pz_ in m.points.values()
                 if pz_ == lz and lx <= px_ < lx + 43 and ly <= py_ < ly + 31] + [(lx + 22, ly + 30)]
        quiet += [t[:2] for t in (e1, x1, e2, x2, e3, x3) if t[2] == lz]   # lab3_up is placed further down
        for spot, pack in zip(_lab_spots(lx, ly, 14, 10, lz, quiet, len(packs)), packs):
            wilds.group(m, spot, pack, LAB_RESPAWN)
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
    m.sign(bx + 13, by + 21, bz, "Beyond this door the tower's protection ends. Once this floor is cleared, a party of 1 to 5 "
           "can say !private at the top of the labyrinth to face the Axe-Lord in a hall of its own (once a day).")
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

    # the private hall (roadmap R9): the same boss for one party at a time, once a day per character
    qx, qy = bx, by + 30
    m.fill(qx, qy, 30, 24, bz, "blackmarble")
    m.walls(qx, qy, 30, 24, bz, style="stone")
    m.points["boss_private_floor1"] = (qx + 15, qy + 10, bz)
    m.points["boss_private_floor1_nw"] = (qx + 1, qy + 1, bz)
    m.points["boss_private_floor1_se"] = (qx + 28, qy + 22, bz)
    m.teleport((qx + 15, qy + 21, bz), (x3[0] + 1, x3[1], 5), "boss_private_floor1_exit")
    m.sign(qx + 13, qy + 21, bz, "The private hall. When the fight is done, step on the light to leave.")
    priv_out = DG.keep_clear(m, bz)
    for qx_, qy_ in ((qx + 3, qy + 4), (qx + 26, qy + 4), (qx + 3, qy + 20), (qx + 26, qy + 20)):
        S.prop(m, qx_, qy_, bz, DG.COAL_BASIN)
    for yy_ in range(qy + 6, qy + 20, 4):
        for xx_ in (qx + 7, qx + 22):
            S.prop(m, xx_, yy_, bz, DG.PILLAR)
    DG.hang(m, qx, qy, 30, 24, bz, every=4, h_item=DG.CHAINS_H, v_item=DG.TORCH_V)
    private_hall = (qx, qy)

    # stair to floor 2: linked to Floor 2's landing by tools/mapgen.py (link_floors)
    m.points["stair_floor2_src"] = (bx + 15, by + 1, bz)

    # ------------------------------------------------ PvP zone tiers (DESIGN.md 6.3). Default everywhere: Open.
    m.zone("open", X0, Y0, SIZE, SIZE)
    # guarded ring: the city, its cabins and roads, the four starter camps, the fisher huts and the Arrival Yard
    m.zone("guarded", tx - 60, ty - 12, tw + 120, th + 24, 7)
    for c in CAMPS:
        if c["zone"] == "guarded":
            m.zone("guarded", X0 + c["x"] - 6, Y0 + c["y"] - 6, c["w"] + 12, c["h"] + 12, 7)
            for lz in (6, 8, 9):                                  # a designed ground's other levels are guarded too
                nw, se = m.points.get(f"level_{c['id']}_{lz}_nw"), m.points.get(f"level_{c['id']}_{lz}_se")
                if nw:
                    m.zone("guarded", nw[0], nw[1], se[0] - nw[0] + 1, se[1] - nw[1] + 1, lz)
    m.zone("guarded", tx + 10, Y0 + 195, 70, 55, 7)                  # the gate road up to the Waspgrass Fields
    m.zone("guarded", X0 + 128, Y0 + 186, 30, 50, 7)                 # the fisher huts
    m.zone("guarded", yard_x - 2, yard_y - 2, 68, 28, 7)              # the Arrival Yard
    m.zone("guarded", yard_x + 3, yard_y, 38, 25, 9)                 # the Proving under it (G2)
    m.zone("guarded", yard_x + 6, yard_y + 1, 30, 18, 8)              # the Old Granary's rat cellar
    m.zone("guarded", mx - 20, my - 20, mw + 40, mh + 40, 7)         # around Millcross
    for c in CAMPS:                                                   # Open grounds are Open right up to their walls
        if c["zone"] == "open":
            m.zone("open", X0 + c["x"], Y0 + c["y"], c["w"], c["h"], 7)
    m.zone("contested", ax - 5, ay - 5, 54, 54, 7)                   # the Old Watchtower approach and outer layer
    m.zone("deadzone", ax + 12, ay + 12, 20, 20, 7)                  # the packed inner room
    m.zone("deadzone", cx, cy, 44, 44, 8)                            # the cliff caves below
    m.zone("bossroom", px, py, 24, 20, 7)                            # the Pass arena
    m.zone("bossroom", bx, by, 30, 24, 4)                            # the Axe-Lord's room
    m.zone("bossroom", private_hall[0], private_hall[1], 30, 24, 4)    # the Axe-Lord's private hall (R9)
    for lvl in (7, 6, 5):                                             # the towns' upstairs rooms are town too
        m.zone("town", tx, ty, tw, th, lvl)
        m.zone("town", mx, my, mw, mh, lvl)
    m.zone("town", *m.manor_roof)                                     # Spire Manor's roof garden (level 4) is town too

    # ------------------------------------------------ Floor 1 secrets (DESIGN.md 8.1). Trigger tiles only; no markers.
    def secret(sid, x, y, z=Z):
        for L in getattr(m, "wilds", []):                 # inside a walled ground a secret must sit on its trails
            if z == Z and (x, y) in L["rect"] and (x, y) not in L["open"]:
                nx, ny = min(L["open"], key=lambda t: (t[0] - x) ** 2 + (t[1] - y) ** 2)
                print(f"secret {sid} moved from {(x - X0, y - Y0)} to {(nx - X0, ny - Y0)} (onto a trail in {L['id']})")
                x, y = nx, ny
        if (x, y, z) not in m.ground:
            raise ValueError(f"secret {sid} has no ground at {(x, y, z)}")
        m.clear_items(x, y, z)  # trigger tiles must be walkable
        m.points["secret_" + sid] = (x, y, z)
    secret("s1", tx + 6, ty + 67)                       # beside the drain grate
    bm = next(L for L in m.wilds if L["id"] == "boar_meadow")
    if bm.get("wallow"):                                # the old loop layout: a hollow core on the surface
        wx_, wy_ = bm["wallow"]["centre"]
        m.points["old_tusk_spawn"] = (wx_, wy_, Z)
        secret("s2", *max(bm["wallow"]["clear"], key=lambda t: (t[1], t[0])))
    else:                                               # H7: Old Tusk's wallow is a dead-end chamber in the Wallows (z 8)
        tusk = next(p for p, v in bm["clearings"].items() if v[0] == "tusk")
        m.points["old_tusk_spawn"] = tusk
        secret("s2", tusk[0] + 1, tusk[1], tusk[2])      # a step into the mud from the chamber's middle
    secret("s3", mill[0] + 6, mill[1] + 3)              # under the Millcross mill: beside the millstone (M9)
    secret("s4", mx + 21, my + 6)                       # false pantry shelf in the inn
    qL = next(L for L in m.wilds if L["id"] == "old_quarry")
    if qL.get("design"):                                # H8: a dead-end nook off the north-east ledge, never on the trail
        nook = next(p for p, v in qL["clearings"].items() if v[0] == "nook")   # (the crack drops you near Millcross)
        secret("s5", nook[0], nook[1])
    else:
        qne = next(lp for lp in qL["loops"] if lp["name"] == "ne")
        s5 = max(qne["ring"] - qne["patches"], key=lambda t: ((t[0] - qne["mouth_pt"][0]) ** 2 + (t[1] - qne["mouth_pt"][1]) ** 2, t))
        secret("s5", *s5)                               # a cracked stone on the far side of the Quarry's north-east loop
    m.points["north_crack_exit"] = (mx + 25, my + 20, Z)
    secret("s6", mx + 44, my + 2)                       # hollow behind the Millcross well (night only)
    secret("s7", X0 + 352, Y0 + 186)                    # ruined shrine on the bandit road
    secret("s8", X0 + 330, Y0 + 330)                    # plates in the shard fields
    secret("s9", X0 + 44, Y0 + 300)                     # abandoned bedroll in the wolf copse
    secret("s10", X0 + 380, Y0 + 380)                   # ruined well in the south-east corner
    secret("s11", X0 + 160, Y0 + 170)                   # bramble ring in the thornsnap hollow
    secret("s12", X0 + 296, Y0 + 60)                    # broken stair of a ruined side tower near the Pass

    # ------------------------------------------------ The Underkeep, Wing 1 (DESIGN.md 3.4), under Hearthgate at z 8
    # a real dungeon since 2026-11-26 (Jay, Q89): rooms, corridors, loops, a secret and a mini-boss (maps/underkeep.py)
    import underkeep
    ux, uy, uz = tx, ty + 10, 8
    underkeep.build_wing1(m, ux, uy, uz)
    vx, vy, vz = m.points["uk1_vault"]
    secret("s13", vx, vy, vz)                          # the walled-up cell at the end of the dead-end passage
    m.teleport((ux + 2, uy + 2, uz), (tx + 5, ty + 68, Z), "underkeep_exit")
    m.sign(ux + 67, uy + 25, uz, "A black iron door. Sealed until the tower reaches Floor 2.")

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

    # ------------------------------------------------ the Summoning Circle arena (roadmap R16): z 11, reached only from a
    # house's Summoning Circle. A small walled ring; a light in the south wall takes you back to Hearthgate.
    cx0, cy0, cz0 = X0 + 140, Y0 + 10, 11
    m.fill(cx0, cy0, 17, 17, cz0, "blackmarble")
    m.walls(cx0, cy0, 17, 17, cz0, style="pale")
    DG.flagstones(m, cx0 + 3, cy0 + 3, 11, 11, cz0, 351)
    m.points["summon_circle"] = (cx0 + 8, cy0 + 6, cz0)
    m.points["summon_circle_entry"] = (cx0 + 8, cy0 + 12, cz0)
    m.points["summon_circle_nw"] = (cx0 + 1, cy0 + 1, cz0)
    m.points["summon_circle_se"] = (cx0 + 15, cy0 + 15, cz0)
    m.teleport((cx0 + 8, cy0 + 15, cz0), (X0 + 232, Y0 + 287, Z), "summon_circle_exit")
    for qx, qy in ((cx0 + 2, cy0 + 2), (cx0 + 14, cy0 + 2), (cx0 + 2, cy0 + 14), (cx0 + 14, cy0 + 14)):
        S.prop(m, qx, qy, cz0, DG.COAL_BASIN)
    m.sign(cx0 + 7, cy0 + 15, cz0, "The Summoning Circle. When the fight is over, step on the light to go home.")
    DG.hang(m, cx0, cy0, 17, 17, cz0, every=4, h_item=DG.TORCH_H, v_item=DG.TORCH_V)
    m.zone("bossroom", cx0, cy0, 17, 17, cz0)

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

    # ------------------------------------------------ the Outlaw Camp (roadmap R7): where murderers wake after death
    ox, oy = X0 + 10, Y0 + 140
    m.fill(ox, oy, 18, 13, Z, "dirt")
    for yy in range(oy, oy + 13):
        for xx in range(ox, ox + 18):
            m.clear_items(xx, yy, Z)
    m.walls(ox, oy, 18, 13, Z, gaps={(ox + 17, oy + 6), (ox + 17, oy + 7)}, style="timber")   # a timber palisade, gate east
    S.prop(m, ox + 8, oy + 6, Z, 1996)                                 # the camp fire
    for px_, py_, pid in ((2, 2, 5543), (4, 2, 116), (5, 2, 2519), (2, 10, 2523), (14, 2, 116), (14, 10, 2519), (6, 10, 2370)):
        S.prop(m, ox + px_, oy + py_, Z, pid)
    m.sign(ox + 18, oy + 5, Z, "The Outlaw Camp. Murderers wake here instead of in a temple. Nobody here will heal you.")
    m.points["outlaw_camp"] = (ox + 10, oy + 7, Z)
    m.road((ox + 18, oy + 7), (X0 + 76, oy + 7), Z, width=2, wind=False)   # a track east to the Watch Road
    m.zone("open", ox, oy, 18, 13, 7)

    # ------------------------------------------------ landmarks, lakes and forests (the world between the camps)
    S.pond(m, X0 + 330, Y0 + 92, 20, 12, Z, ring="mud")           # a lake in the north-east
    S.pond(m, X0 + 96, Y0 + 130, 11, 7, Z, ring="mud")            # a pond across the river
    S.ruin(m, X0 + 312, Y0 + 125, 14, 11, Z)                       # ruined watchtower by the lake
    S.ruin(m, X0 + 60, Y0 + 150, 11, 9, Z)                         # a roofless farmhouse across the river
    S.ruin(m, X0 + 300, Y0 + 372, 10, 8, Z, door=[(X0 + 302, Y0 + 372), (X0 + 303, Y0 + 372)])   # a toppled shrine (south-east)
    S.standing_stones(m, X0 + 382, Y0 + 262, Z)                    # a ring of standing stones east of the city (moved twice for Toad Pond)
    S.standing_stones(m, X0 + 30, Y0 + 350, Z)
    import small_game                                  # Q94: small game on the empty lawns (maps/small_game.py)
    small_game.place(m, X0, Y0, SIZE, Z, [(X0 + c["x"], Y0 + c["y"], c["w"], c["h"]) for c in CAMPS] + [
        (tx, ty, tw, th), (X0 + MILLCROSS["x"], Y0 + MILLCROSS["y"], MILLCROSS["w"], MILLCROSS["h"])])
    keep = [p for p in m.points.values() if p[2] == Z] + [pos for _n, pos, *_r in m.monsters if pos[2] == Z] + [pos for _n, pos in m.npcs if pos[2] == Z]
    grounds = [(X0 + c["x"] - 2, Y0 + c["y"] - 2, c["w"] + 4, c["h"] + 4) for c in CAMPS]
    S.forest(m, X0 + 4, Y0 + 4, SIZE - 8, SIZE - 8, Z, keep=keep, avoid=grounds)
