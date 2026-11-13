#!/usr/bin/env python3
"""Spirebound balance tables for the real 10-floor game (roadmap R10, REVIEW 2.8 / 6.1 / 3.7 / 3.12).

ONE place for the per-floor targets. tools/gen_monsters.py reads them (floor 2-10 experience and coin drops are scaled
from them) and the hunting tasks are generated from them, so the game and the model can't disagree.

    python tools/balance.py            -> writes BALANCE.md, data/balance_floors.csv and lib/spirebound/tasks_floors.lua
    python tools/balance.py --check    -> the same, and exits with an error on any bad number (run on GitHub too)
    python tools/balance.py --selftest -> proves the check really fails on a bad price

The model (Claude's call, Jay can veto): a hunter at the middle level of the floor's band, damage per second 4 + level,
8 seconds to reach the next monster, at most 300 kills an hour; experience stages from server/core-overrides/stages.lua.
Floor 1 has its own detailed model (tools/gen_economy.py, ECONOMY.md); here it is one row so the curve can be checked.
"""
import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------- targets (one row per floor)
# hours: hand-hunting hours to climb the floor's level band; gold: gross coins per hour at the middle level
# (before supplies). Floor 1 comes from ECONOMY.md (about 9.5 model hours to level 35, about 7k gold/h at the top).
TARGETS = {
    1: dict(hours=12, gold=7000),
    2: dict(hours=14, gold=11000),
    3: dict(hours=16, gold=14000),
    4: dict(hours=18, gold=18000),
    5: dict(hours=22, gold=22000),
    6: dict(hours=26, gold=27000),
    7: dict(hours=30, gold=32000),
    8: dict(hours=35, gold=38000),
    9: dict(hours=40, gold=44000),
    10: dict(hours=45, gold=50000),
}
SUPPLY_MAX_SHARE = 0.6        # supplies may eat at most 60% of the coins (else hunting there is a loss)
TASK_GOLD_SHARE = 0.3         # a hunting task pays at most 30% of what the hunting time it takes earns on its floor
TASK_POINTS = {"camp": 1, "elite": 2, "apex": 3}
HOUSE_HOURS = (2, 20)         # a typical house in a floor's town should cost 2-20 hours of that floor's coins
TOWN_OF_FLOOR = {1: 1}        # floor -> town id (floors 2-10: town n + 1, see maps/layout_floor.py)
ELITE_GOLD, APEX_GOLD = 2.0, 3.0   # elites and apex monsters carry this many times a camp monster's coins
GOLD, PLAT = 3031, 3035


def stage(level):
    """Experience stage for a level, read from the real stages file."""
    text = (ROOT / "server/core-overrides/stages.lua").read_text(encoding="utf-8")
    block = text.split("experienceStages", 1)[1].split("}\n", 1)[0]
    for lo, hi, mult in re.findall(r"minlevel = (\d+),(?: maxlevel = (\d+),)? multiplier = (\d+)", block):
        if int(lo) <= level and (not hi or level <= int(hi)):
            return int(mult)
    return 1


def xp_for(level):
    return int(50 / 3 * (level ** 3 - 6 * level ** 2 + 17 * level - 12))


def dps(level):
    return 4 + level


def kills_per_hour(hp, level):
    return min(3600 / (hp / dps(level) + 8), 300)


def band_hours(xp_per_kill, hp, lo, hi):
    """Hand-hunting hours from level lo to hi at this floor's monsters."""
    return sum((xp_for(l + 1) - xp_for(l)) / (xp_per_kill * kills_per_hour(hp, l) * stage(l)) for l in range(lo, hi))


def xp_scale(n, base_xp_per_kill, hp, band):
    """By how much floor n's monster experience must be multiplied to hit its hours target."""
    return band_hours(base_xp_per_kill, hp, *band) / TARGETS[n]["hours"]


def coin_loot(gold_per_kill):
    """Coin loot rows (gold, then platinum) that drop about gold_per_kill on average."""
    rows = [(GOLD, 100000, 100)]                          # 50.5 gold on average
    rest = gold_per_kill - 50.5
    if rest > 0:
        if rest <= 100:
            rows.append((PLAT, int(round(rest / 100 * 100000)), 1))
        else:
            mx = max(1, int(round(2 * rest / 100 - 1)))
            rows.append((PLAT, 100000, mx))
    return rows


def coin_value(loot):
    v = 0.0
    for iid, chance, mx in loot:
        if iid == GOLD:
            v += chance / 100000 * (mx + 1) / 2
        elif iid == PLAT:
            v += chance / 100000 * (mx + 1) / 2 * 100
    return v


def task_cap(n, monster, count, band):
    """The most a task may pay: 30% of the floor's gold target over the time its kills take."""
    lo, hi = band
    hours = count / kills_per_hour(monster["hp"], (lo + hi) // 2)
    return TASK_GOLD_SHARE * TARGETS[n]["gold"] * hours


def floor_gold_per_kill(n, hp, band):
    lo, hi = band
    return TARGETS[n]["gold"] / kills_per_hour(hp, (lo + hi) // 2)


# ---------------------------------------------------------------- the report and the checks
def potion_for(level, prices):
    """The health potion a hunter of this level drinks: (heal, price). Prices come from the real shops."""
    table = [(7643, 875, 130), (239, 600, 80), (236, 350, 50), (266, 150, 0)]  # ultimate, great, strong, plain
    for iid, heal, min_level in table:
        if level >= min_level and iid in prices:
            return heal, prices[iid]
    return 150, prices.get(266, 50)


def rows_and_problems(monsters, floors, prices, houses, tasks):
    rows, problems = [], []
    for n in sorted(floors):
        f = floors[n]
        lo, hi = f["band"]
        mid = (lo + hi) // 2
        camp = [monsters[c] for c in f["camp"]]
        hp = sum(m["hp"] for m in camp) / len(camp)
        xp = sum(m["xp"] for m in camp) / len(camp)
        gold = sum(coin_value(m["loot"]) for m in camp) / len(camp)
        kph = kills_per_hour(hp, mid)
        hours = band_hours(xp, hp, lo, hi)
        melee = sum(max((-a[2] for a in m["attacks"] if a[0] == "melee"), default=0) for m in camp) / len(camp)
        taken = melee / 2 * 0.6 * 0.8 * (hp / dps(mid)) / 2 * kph
        heal, price = potion_for(mid, prices)
        supplies = taken * 0.35 / heal * price
        town = TOWN_OF_FLOOR.get(n, n + 1)
        sizes = sorted(houses.get(town, []))
        house = sizes[len(sizes) // 2] * 1000 if sizes else 0
        house_h = house / max(1, gold * kph - supplies) if house else 0
        row = dict(floor=n, levels=f"{lo}-{hi}", kills_h=round(kph), base_xp_h=round(xp * kph), gold_h=round(gold * kph),
                   supplies_h=round(supplies), band_hours=round(hours, 1), house_price=house, house_hours=round(house_h, 1))
        rows.append(row)
        t = TARGETS[n]
        if n >= 2 and abs(hours - t["hours"]) > 0.15 * t["hours"]:
            problems.append(f"Floor {n}: {hours:.1f} hours to climb its levels, target {t['hours']}")
        if n >= 2 and abs(gold * kph - t["gold"]) > 0.15 * t["gold"]:
            problems.append(f"Floor {n}: {gold * kph:.0f} gold an hour, target {t['gold']} (a gold flood or a drought)")
        if supplies > SUPPLY_MAX_SHARE * gold * kph:
            problems.append(f"Floor {n}: supplies ({supplies:.0f}/h) eat more than {SUPPLY_MAX_SHARE:.0%} of the coins ({gold * kph:.0f}/h)")
        if n <= 2 and house and not (HOUSE_HOURS[0] <= house_h <= HOUSE_HOURS[1]):
            problems.append(f"Floor {n}: a typical house costs {house_h:.1f} hours of hunting (want {HOUSE_HOURS[0]}-{HOUSE_HOURS[1]})")
    for t in tasks:
        m = monsters.get(t["monster"])
        if not m:
            problems.append(f"task {t['id']}: no monster called {t['monster']}")
            continue
        n = t.get("floor", 1)
        cap = task_cap(n, m, t["count"], floors[n]["band"])
        if t["gold"] > cap + 1:
            problems.append(f"task {t['id']}: pays {t['gold']} gold, more than {TASK_GOLD_SHARE:.0%} of what its hunting time earns ({cap:.0f})")
    for name, (buy, sell) in prices.get("_pairs", {}).items():
        if sell and buy and sell >= buy:
            problems.append(f"price loop: {name} sells for {sell} but can be bought for {buy}")
    return rows, problems


def load_game():
    sys.path.insert(0, str(ROOT / "tools"))
    sys.path.insert(0, str(ROOT / "maps"))
    from gen_monsters import MONSTERS, floor_monsters
    from floors import FLOORS
    from floor1_plan import CAMPS
    from gen_npcs import NPCS
    monsters = {**MONSTERS, **floor_monsters()}
    floors = dict(FLOORS)
    # floor 1 as one row: its experience grounds from level 9 up (the early ones are minutes long)
    f1 = [c for c in CAMPS if c["role"] == "xp" and c["levels"][0] >= 9]
    floors[1] = dict(band=(9, 35), camp=[c["mix"][0][0] for c in f1])
    prices, pairs = {}, {}
    for d in NPCS.values():
        for name, cid, buy, sell in d.get("shop", []):
            if buy:
                prices[cid] = min(prices.get(cid, buy), buy)
            b, s = pairs.get(name, (None, None))
            pairs[name] = (min(b, buy) if b and buy else (b or buy), max(s, sell) if s and sell else (s or sell))
    prices["_pairs"] = pairs
    houses = {}
    xml = (ROOT / "server/data-spirebound/world/spirebound-house.xml").read_text()
    for town, size in re.findall(r'townid="(\d+)" size="(\d+)"', xml):
        houses.setdefault(int(town), []).append(int(size))
    tasks = floor_tasks(monsters, floors) + floor1_tasks()
    return monsters, floors, prices, houses, tasks


def floor1_tasks():
    text = (ROOT / "server/data-spirebound/lib/spirebound/tasks.lua").read_text(encoding="utf-8")
    out = []
    for tid, mon, count, gold in re.findall(r'id = "([^"]+)", floor = 1, monster = "([^"]+)", count = (\d+), gold = (\d+)', text):
        out.append(dict(id=tid, floor=1, monster=mon, count=int(count), gold=int(gold)))
    return out


def floor_tasks(monsters, floors):
    """Hunting tasks for floors 2-10: two camp monsters, the elite and the apex; gold = 25% of what the kills drop."""
    out = []
    for n in sorted(floors):
        if n < 2:
            continue
        f = floors[n]
        picks = [(f["camp"][0], "camp", 80), (f["camp"][2], "camp", 80), (f["elite"], "elite", 40), (f["apex"], "apex", 25)]
        for name, kind, count in picks:
            m = monsters[name]
            gold = int(task_cap(n, m, count, f["band"]) * 0.8) // 100 * 100
            out.append(dict(id=f"t{n}_{re.sub(r'[^a-z]', '', name.lower())}", floor=n, monster=name, count=count, gold=gold,
                            points=TASK_POINTS[kind] + n // 3))
    return out


def write(rows, problems, tasks):
    (ROOT / "data").mkdir(exist_ok=True)
    with open(ROOT / "data/balance_floors.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    lua = ["-- GENERATED by tools/balance.py (roadmap R10). Do not edit by hand.",
           "-- Hunting tasks for floors 2-10: each pays 80% of the most the balance check allows.",
           "SpireTasks.floorList = {"]
    for t in tasks:
        if t.get("floor", 1) >= 2:
            lua.append(f'\t{{ id = "{t["id"]}", floor = {t["floor"]}, monster = "{t["monster"]}", count = {t["count"]}, '
                       f'gold = {t["gold"]}, points = {t["points"]} }},')
    lua.append("}")
    lua.append("for _, t in ipairs(SpireTasks.floorList) do\n\ttable.insert(SpireTasks.list, t)\nend")
    (ROOT / "server/data-spirebound/lib/spirebound/tasks_floors.lua").write_text("\n".join(lua) + "\n", encoding="utf-8")
    L = ["# Spirebound balance: all ten floors", "",
         "*Generated by `python tools/balance.py` (roadmap R10). Do not edit by hand: change the targets at the top of "
         "that file and rerun. The monster generator reads the same targets.*", "",
         "For a hunter at the middle level of each floor, hunting by hand. Floor 1 in detail is in ECONOMY.md.", "",
         "| Floor | Levels | Kills/h | Base XP/h | Gold/h | Supplies/h | Hours to climb | Typical house | Hours to afford it |",
         "|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        L.append(f"| {r['floor']} | {r['levels']} | {r['kills_h']} | {r['base_xp_h']:,} | {r['gold_h']:,} | {r['supplies_h']:,} | "
                 f"{r['band_hours']} | {r['house_price']:,} | {r['house_hours']} |")
    total = sum(r["band_hours"] for r in rows)
    L += ["", f"Climbing all ten floors by hand: about {total:.0f} hours by the model (real play is slower).", "",
          "## Rules the check enforces", f"- Each floor's climb within 15% of its hours target, and its coins within 15% of its gold target.",
          f"- Supplies never eat more than {SUPPLY_MAX_SHARE:.0%} of the coins.",
          f"- A typical house on Floors 1-2 costs {HOUSE_HOURS[0]}-{HOUSE_HOURS[1]} hours of hunting.",
          f"- A hunting task pays at most {TASK_GOLD_SHARE:.0%} of what the hunting time it takes earns on its floor.",
          "- No shop sells anything back for as much as it charges.", "",
          "## Checks", "All checks pass." if not problems else "**Problems:**\n" + "\n".join("- " + p for p in problems)]
    (ROOT / "BALANCE.md").write_text("\n".join(L) + "\n", encoding="utf-8")


def main(argv):
    monsters, floors, prices, houses, tasks = load_game()
    if "--selftest" in argv:
        bad = dict(prices)
        bad["_pairs"] = {**prices["_pairs"], "test potion": (100, 150)}
        _rows, probs = rows_and_problems(monsters, floors, bad, houses, tasks)
        assert any("price loop: test potion" in p for p in probs), "the check must fail on a bad price"
        greedy = tasks + [dict(id="t_greedy", monster=floors[2]["camp"][0], count=10, gold=10 ** 6)]
        _rows, probs = rows_and_problems(monsters, floors, prices, houses, greedy)
        assert any("t_greedy" in p for p in probs), "the check must fail on an overpaid task"
        print("balance selftest: OK (a bad price and an overpaid task both fail the check)")
        return 0
    rows, problems = rows_and_problems(monsters, floors, prices, houses, tasks)
    write(rows, problems, tasks)
    print(f"wrote BALANCE.md, data/balance_floors.csv and tasks_floors.lua ({len(rows)} floors, {len(tasks)} tasks)")
    if problems:
        print("BALANCE PROBLEMS:\n" + "\n".join(problems))
        if "--check" in argv:
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
