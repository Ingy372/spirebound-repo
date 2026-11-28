#!/usr/bin/env python3
"""Spirebound balance tables for the real 10-floor game (roadmap R10, REVIEW 2.8 / 6.1 / 3.7 / 3.12).

ONE place for the per-floor targets. tools/gen_monsters.py reads them (floor 2-10 experience and coin drops are scaled
from them) and the hunting tasks are generated from them, so the game and the model can't disagree.

    python tools/balance.py            -> writes BALANCE.md, data/balance_floors.csv and lib/spirebound/tasks_floors.lua (every floor's tasks)
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
HOUSE_TARGET = 8              # R10c: floors 2-10 price their houses at about this many hours of that floor's coins
TOWN_OF_FLOOR = {1: 1}        # floor -> town id (floors 2-10: town n + 1, see maps/layout_floor.py)
ELITE_GOLD, APEX_GOLD = 2.0, 3.0   # elites and apex monsters carry this many times a camp monster's coins
GOLD, PLAT = 3031, 3035

# ---------------------------------------------------------------- spawn rules (DESIGN.md 9.4, Jay 2026-11-16)
# Every monster has a habit (how it spawns: its group shape) and a weight (how much it counts towards the danger
# budget: 1 = the floor's ordinary monster). First guesses from each monster's health, hit and speed (Claude's call).
HABIT_KINDS = ("loner", "pair", "pack", "swarm", "colony", "sentry")
HABITS = {
    "Field Rat": ("swarm", 0.4), "Hopper Toad": ("pair", 1.0), "Sproutling": ("colony", 0.7),
    "Meadow Wasp": ("colony", 0.5), "Burrow Mole": ("colony", 1.0), "Bristle Boar": ("pair", 1.5),   # QA14 (Q73, Claude's call): ones and twos
   
    "Meadow Wolf": ("pack", 1.0), "Grey Alpha": ("pack", 2.0), "Reed Snapper": ("pair", 1.0),
    "Thornsnap": ("sentry", 1.3), "Field Shardling": ("pair", 1.0), "Road Bandit": ("sentry", 1.0),
    "Bandit Captain": ("sentry", 2.5), "Ruin Sentinel": ("sentry", 1.3), "Ruin Archer": ("sentry", 1.0), "Stairwarden": ("sentry", 2.2),
    "Stonehorn Ram": ("pack", 2.0),
    "Bandit Crossbowman": ("sentry", 1.0), "Hedge Hexer": ("sentry", 1.1),     # S4: the mixed packs' ranged one and caster
    # small game on the open lawns (Q94): loners, harmless, a tenth of an ordinary monster
    "Meadow Hare": ("loner", 0.1), "Dapple Fawn": ("loner", 0.1), "Thistle Hen": ("loner", 0.1), "Acorn Squirrel": ("loner", 0.1),
    # Floor 1 elites (FLOOR1_REVIEW.md F1-11): alone, rare, each counts for about two and a half
    "Old Bristleback": ("loner", 2.5), "Moonhowl": ("loner", 2.5), "Mossback Snapper": ("loner", 2.5),
    "Blackthorn": ("loner", 2.5), "Prism Shardling": ("loner", 2.5), "Granite Warden": ("loner", 2.5),
    # AD4 rare roamers (tools/gen_adventure.py): out one at a time for 15 minutes; the toad flees, so it is light
    "Goldback Toad": ("loner", 1.5), "Frenzied Boar": ("loner", 2.5), "Pale Stag": ("loner", 2.5), "The Paymaster": ("loner", 2.5),
    # Floor 2 (maps/floor2_plan.py, R13b/S6): every habit once, weights against Floor 2's ordinary monster
    "Horned Grazer": ("pair", 1.0), "Dust Strider": ("swarm", 0.5), "Ridge Cat": ("loner", 1.6),
    "Blight Wasp": ("colony", 0.6), "Hill Cutthroat": ("sentry", 1.1), "Stonehide Bull": ("pack", 1.5),
    "Herd Bull": ("loner", 2.5), "Mesa Wyrmling": ("loner", 3.0),
    # Floor 3 (maps/floor3_plan.py, S6)
    "Bark Mantis": ("pair", 1.0), "Spore Bat": ("swarm", 0.5), "Fog Lurker": ("loner", 1.6),
    "Moss Crawler": ("colony", 0.7), "Lantern Wisp": ("sentry", 1.0), "Rootbound Husk": ("pack", 1.5),
    "Moss Elder": ("loner", 2.5), "Grove Hydraling": ("loner", 3.0),
    # Floor 4 (maps/floor4_plan.py, S6)
    "Drowned Footman": ("pair", 1.0), "Lake Eel": ("swarm", 0.5), "Helm Knight": ("loner", 1.8),
    "Tide Crab": ("colony", 0.8), "Reed Witch": ("sentry", 1.0), "Castle Hound": ("pack", 1.2),
    "Drowned Sergeant": ("loner", 2.5), "Siege Beast": ("loner", 3.0),
}
# Group shapes per habit: the sizes a group of that habit may have, by band (nest = the colony's nest or a den).
HABIT_SIZES = {"loner": (1, 1), "pair": (1, 2), "pack": (3, 5), "swarm": (1, 8), "colony": (1, 12), "sentry": (1, 4)}
# Every hunting ground has a type. budget = the most weight that may come at one player at once, by band;
# reward = target experience/gold per person per hour against the floor's training baseline; players = who it is for.
# H14 (Jay, 2026-11-25: "challenge, not calm"): roughly double the old budgets past the calm zone; a nest may overwhelm a
# player of the ground's level on purpose (DESIGN.md 9.4). The gate (approach) stays at 0.
GROUND_TYPES = {
    "training": dict(budget=dict(approach=0, calm=5, middle=8, deep=10, nest=16), reward=1.0, players=(1, 1)),
    "class": dict(budget=dict(approach=0, calm=6, middle=9, deep=16, nest=22), reward=1.2, players=(1, 1)),
    "mixed": dict(budget=dict(approach=0, calm=6, middle=9, deep=16, nest=22), reward=1.1, players=(1, 2)),
    "group": dict(budget=dict(approach=0, calm=8, middle=14, deep=22, nest=28), reward=1.5, players=(3, 4)),
    "large": dict(budget=dict(approach=0, calm=12, middle=20, deep=28, nest=36), reward=1.75, players=(4, 8)),
}
CLASSES = ("Vanguard", "Ranger", "Arcanist", "Mystic")
PARTY_MAX = 8                                   # DESIGN.md 7.1: a large-group ground fits in one party


def weight(name):
    return HABITS[name][1]


def budget(gtype, band):
    """The danger budget of a band in a ground of this type. A party level is a group ground inside any ground."""
    if band == "party":
        return GROUND_TYPES["group"]["budget"]["deep"]
    return GROUND_TYPES[gtype]["budget"][band]


def spawn_rule_problems():
    """DESIGN.md 9.4 as checks: every ground has a type, every class a ground, every monster a habit."""
    sys.path.insert(0, str(ROOT / "maps"))
    from floor1_plan import CAMPS, DESIGNS, APEX
    out = []
    for h, w in HABITS.values():
        if h not in HABIT_KINDS or w <= 0:
            out.append(f"bad habit or weight: {h} {w}")
    for t, d in GROUND_TYPES.items():
        b = [d["budget"][k] for k in ("approach", "calm", "middle", "deep", "nest")]
        if b[0] != 0 or b != sorted(b):
            out.append(f"ground type {t}: the budget must be 0 at the gate and rise inward ({b})")
    grounds = CAMPS + [APEX]
    classes = {}
    for c in grounds:
        t = c.get("type")
        if t not in GROUND_TYPES:
            out.append(f"{c['title']}: no ground type (one of {', '.join(GROUND_TYPES)})")
        if t == "class":
            if c.get("cls") not in CLASSES:
                out.append(f"{c['title']}: a class ground must name its class")
            classes.setdefault(c.get("cls"), []).append(c["title"])
        mons = {m for g in c.get("groups", []) + c.get("den_groups", []) for m, _n in g}
        if c.get("design"):
            for lv in DESIGNS[c["design"]]["levels"].values():
                for cl in lv["clearings"]:
                    if isinstance(cl[6], list):
                        mons |= {m for grp in cl[6] for m, _n in grp}
        for part in ("courtyard", "inner", "cave"):
            mons |= {m for g in c.get(part, {}).get("groups", []) for m, _n in g}
        for mname in sorted(mons):
            if mname not in HABITS:
                out.append(f"{c['title']}: {mname} has no habit")
    for k in CLASSES:
        if k not in classes:
            out.append(f"Floor 1 has no class ground for the {k}")
    if sum(1 for c in grounds if c.get("type") == "large") > 1:
        out.append("Floor 1 has more than one large-group ground (Jay: occasional)")
    if not any(c.get("type") == "group" or c.get("den") for c in grounds):
        out.append("Floor 1 has no group ground")
    for n in range(2, 11):
        out += floor_recipe_problems(n)
    return out


def floor_recipe_problems(n):
    """DESIGN.md 9.4 layer 3 for a floor with its own plan (maps/floor<n>_plan.py): 1-2 training grounds, one class
    ground per class, 2-3 mixed, at least one group ground (or party cave), at most one large; every monster has a habit
    and its group sizes fit that habit; no two grounds share a habit in the same kind of layout."""
    import importlib
    sys.path.insert(0, str(ROOT / "maps"))
    try:
        plan = importlib.import_module(f"floor{n}_plan")
    except ImportError:
        return []
    out, F = [], f"Floor {n}"
    grounds = plan.CAMPS + [plan.APEX]
    count = lambda t: sum(1 for c in grounds if c.get("type") == t)     # noqa: E731
    if not 1 <= count("training") <= 2:
        out.append(f"{F}: wants 1 or 2 training grounds, has {count('training')}")
    if not 2 <= count("mixed") <= 3:
        out.append(f"{F}: wants 2 or 3 mixed grounds, has {count('mixed')}")
    if count("large") > 1:
        out.append(f"{F}: more than one large-group ground")
    if not (count("group") or any(c.get("den") for c in plan.CAMPS)):
        out.append(f"{F}: no group ground")
    have = {c.get("cls") for c in grounds if c.get("type") == "class"}
    out += [f"{F}: no class ground for the {k}" for k in CLASSES if k not in have]
    looks = {}
    for c in plan.CAMPS:
        if c.get("type") not in GROUND_TYPES:
            out.append(f"{F} {c['title']}: no ground type")
        for g in c.get("groups", []) + c.get("den_groups", []):
            for mname, k in g:
                if mname not in HABITS:
                    out.append(f"{F} {c['title']}: {mname} has no habit")
                    continue
                lo, hi = HABIT_SIZES[HABITS[mname][0]]
                if len(g) == 1 and not lo <= k <= hi:
                    out.append(f"{F} {c['title']}: a group of {k} {mname} does not fit its habit ({HABITS[mname][0]})")
        lead = max({mn for g in c["groups"] for mn, _k in g}, key=lambda mn: sum(k for g in c["groups"] for x, k in g if x == mn))
        key = (HABITS.get(lead, ("?",))[0], c["wall"], c["core"])
        if key in looks:
            out.append(f"{F}: {c['title']} and {looks[key]} use the same habit in the same kind of layout")
        looks[key] = c["title"]
    return out


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


# Review A3-1/E-1 (measured on a real character, 2026-11-26): the engine adds its own experience bonuses on top of our
# stages (Canary data/events/scripts/player.lua): 1.5x below level 50, and 1.5x more while stamina is above 39 hours
# (a rested character's first 3 hours of the day). The models report both; the targets and generators still use the
# plain stages. Q83 (Jay, 2026-11-27: "Yes, 11-15 hours"): the low-level bonus is now taken back out on every kill
# (server/core-patches/player_events_append.lua), so only the rested-stamina bonus is left.
ENGINE_LOW_LEVEL = (50, 1.0)
ENGINE_STAMINA = 1.5


def engine_bonus(level, rested=True):
    low = ENGINE_LOW_LEVEL[1] if level < ENGINE_LOW_LEVEL[0] else 1.0
    return low * (ENGINE_STAMINA if rested else 1.0)


def real_stage(level, rested=True):
    """What a kill really gives, as a multiple of the monster's base experience (measured: 22.5x at levels 1-8, 9x at
    9-20, 6.75x at 21-50 for a rested character)."""
    return stage(level) * engine_bonus(level, rested)


def rate_loot():
    """The engine multiplies every drop chance by this (server/config-overrides.lua rateLoot), capped at 100%."""
    m = re.search(r"^rateLoot\s*=\s*([\d.]+)", (ROOT / "server/config-overrides.lua").read_text(encoding="utf-8"), re.M)
    return float(m.group(1)) if m else 1.0


def dps(level):
    return 4 + level


def kills_per_hour(hp, level):
    return min(3600 / (hp / dps(level) + 8), 300)


def band_hours(xp_per_kill, hp, lo, hi, stage_fn=None):
    """Hand-hunting hours from level lo to hi at this floor's monsters (plain stages unless stage_fn is given)."""
    sf = stage_fn or stage
    return sum((xp_for(l + 1) - xp_for(l)) / (xp_per_kill * kills_per_hour(hp, l) * sf(l)) for l in range(lo, hi))


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


def coin_value(loot, rate=1.0):
    """Average coins per kill from loot rows (rate = the engine's loot rate; the generators use the plain 1)."""
    v = 0.0
    for iid, chance, mx in loot:
        p = min(1.0, chance * rate / 100000)
        if iid == GOLD:
            v += p * (mx + 1) / 2
        elif iid == PLAT:
            v += p * (mx + 1) / 2 * 100
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
    # strong from level 14 (server/core-overrides/scripts/actions/items/potions.lua, PT4 2026-11-26; Tibia says 50)
    table = [(7643, 875, 130), (239, 600, 80), (236, 300, 14), (266, 150, 0)]  # ultimate, great, strong, plain
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
        real_hours = band_hours(xp, hp, lo, hi, real_stage)          # with the engine's bonuses (review A3-1)
        real_gold = sum(coin_value(m["loot"], rate_loot()) for m in camp) / len(camp)   # with the engine's loot rate (review E-1; 1 since QA20)
        melee = sum(max((-a[2] for a in m["attacks"] if a[0] == "melee"), default=0) for m in camp) / len(camp)
        taken = melee / 2 * 0.6 * 0.8 * (hp / dps(mid)) / 2 * kph
        heal, price = potion_for(mid, prices)
        supplies = taken * 0.35 / heal * price
        town = TOWN_OF_FLOOR.get(n, n + 1)
        sizes = sorted(houses.get(town, []))
        net = max(1, gold * kph - supplies)
        median = sizes[len(sizes) // 2] if sizes else 0
        # R10c: a house's price per tile is set per floor so a typical house costs about HOUSE_TARGET hours of that
        # floor's coins (Floor 1 keeps the engine's 1,000 a tile). !buyhouse charges it (server/core-overrides).
        per_tile = 1000 if n == 1 or not median else max(1000, int(round(net * HOUSE_TARGET / median / 50.0)) * 50)
        house = median * per_tile
        house_h = house / net if house else 0
        row = dict(floor=n, levels=f"{lo}-{hi}", kills_h=round(kph), base_xp_h=round(xp * kph), gold_h=round(gold * kph),
                   supplies_h=round(supplies), band_hours=round(hours, 1), house_price=house, house_hours=round(house_h, 1),
                   house_per_tile=per_tile, real_band_hours=round(real_hours, 1), real_gold_h=round(real_gold * kph))
        rows.append(row)
        t = TARGETS[n]
        if n >= 2 and abs(hours - t["hours"]) > 0.15 * t["hours"]:
            problems.append(f"Floor {n}: {hours:.1f} hours to climb its levels, target {t['hours']}")
        if n >= 2 and abs(gold * kph - t["gold"]) > 0.15 * t["gold"]:
            problems.append(f"Floor {n}: {gold * kph:.0f} gold an hour, target {t['gold']} (a gold flood or a drought)")
        if supplies > SUPPLY_MAX_SHARE * gold * kph:
            problems.append(f"Floor {n}: supplies ({supplies:.0f}/h) eat more than {SUPPLY_MAX_SHARE:.0%} of the coins ({gold * kph:.0f}/h)")
        if house and not (HOUSE_HOURS[0] <= house_h <= HOUSE_HOURS[1]):
            problems.append(f"Floor {n}: a typical house costs {house_h:.1f} hours of hunting (want {HOUSE_HOURS[0]}-{HOUSE_HOURS[1]})")
    for t in tasks:
        m = monsters.get(t["monster"])
        if not m:
            problems.append(f"task {t['id']}: no monster called {t['monster']}")
            continue
        n = t.get("floor", 1)
        cap = t.get("cap") or task_cap(n, m, t["count"], floors[n]["band"])
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
    tasks = floor_tasks(monsters, floors)
    return monsters, floors, prices, houses, tasks


NOT_TASKS = {"Pen Rat",   # the Arrival Yard's tutorial rats (Claude's call, Jay can veto)
             # small game on the open lawns (Q94): harmless, they pay almost nothing, never a hunting task (2026-11-27:
             # 54fd3380 put them on the Taskmaster's list as 50-kill, 280-gold tasks)
             "Meadow Hare", "Dapple Fawn", "Thistle Hen", "Acorn Squirrel",
             "Sluice Warden"}          # the Underkeep Wing 1 mini-boss (one at a time, half-hour respawn): not a 20-kill task


def floor_of(x, y):
    from floors import origin, SIZE
    if 1000 <= x <= 1399 and 1000 <= y <= 1399:
        return 1
    for n in range(2, 11):
        ox, oy = origin(n)
        if ox <= x < ox + SIZE and oy <= y < oy + SIZE:
            return n
    return 0


def spawn_counts():
    """{floor: {monster: how many spawn on that floor}} from the real map's spawn file."""
    xml = (ROOT / "server/data-spirebound/world/spirebound-monster.xml").read_text(encoding="utf-8")
    out = {}
    for x, y, body in re.findall(r'<monster centerx="(\d+)" centery="(\d+)"[^>]*>(.*?)</monster>\s*(?=<monster centerx|</monsters>)', xml, re.S):
        n = floor_of(int(x), int(y))
        for name in re.findall(r'name="([^"]+)"', body):
            out.setdefault(n, {})
            out[n][name] = out[n].get(name, 0) + 1
    return out


def floor1_camps():
    """Floor 1 hunting grounds from the detailed economy (tools/gen_economy.py): monster -> (kills/h, gold/h, low level)."""
    from floor1_plan import CAMPS
    eco = {r["id"]: r for r in csv.DictReader(open(ROOT / "data/economy_floor1.csv")) if r["vocation"] == "Vanguard"}
    out = {}
    for c in CAMPS:
        r = eco.get(c["id"])
        if r and c["mix"][0][0] not in out:
            out[c["mix"][0][0]] = (int(r["kills_h"]), int(r["gold_h"]), c["levels"][0])
    return out


def floor_tasks(monsters, floors):
    """Every floor's full task list (Jay, 2026-11-13: each floor's taskmaster offers that floor's huntable monsters).
    One task per monster that spawns on the floor (bosses and NOT_TASKS left out). A task takes about 15-20 minutes
    of that monster and pays 80% of the most the check allows (TASK_GOLD_SHARE of what that hunting time earns)."""
    out = []
    camps1 = floor1_camps()
    for n, counts in sorted(spawn_counts().items()):
        if n < 1:
            continue
        f = floors[n]
        for name, spawns in sorted(counts.items(), key=lambda kv: (monsters.get(kv[0], {}).get("hp", 0), kv[0])):
            m = monsters.get(name)
            if not m or m.get("boss") or name in NOT_TASKS:
                continue
            if HABITS.get(name, ("",))[0] == "loner" and HABITS[name][1] >= 2.5 and n == 1:
                continue                     # a lone elite (one every 15 minutes) can't be a 20-kill task (H8, 2026-11-25)
            if n == 1 and name in camps1:
                kph, gph, low = camps1[name]
                count = max(20, min(100, int(kph * 0.25) // 5 * 5))
                cap = TASK_GOLD_SHARE * gph * count / kph
                points = 1 if low < 15 else 2
            else:
                kind = "apex" if name == f.get("apex") else "elite" if (name == f.get("elite") or spawns <= 9) else "camp"
                count = {"camp": 80, "elite": 40, "apex": 25}[kind] if n > 1 else {"camp": 50, "elite": 20, "apex": 20}[kind]
                cap = task_cap(n, m, count, f["band"])
                points = TASK_POINTS[kind] + n // 3 + (1 if n == 1 and kind == "camp" else 0)
            step = 100 if cap >= 2000 else 10
            gold = max(step, int(cap * 0.8) // step * step)
            out.append(dict(id=f"t{n}_{re.sub(r'[^a-z]', '', name.lower())}", floor=n, monster=name, count=count,
                            gold=gold, points=points, cap=cap))
    return out


def write(rows, problems, tasks):
    (ROOT / "data").mkdir(exist_ok=True)
    import crystals                                  # Waycrystals: priced from each floor's income (DESIGN.md 3.7)
    gold_h = {r["floor"]: r["gold_h"] for r in rows}
    (ROOT / "server/data-spirebound/lib/spirebound/crystals_data.lua").write_text(crystals.lua(gold_h), encoding="utf-8")
    with open(ROOT / "data/balance_floors.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    lua = ["-- GENERATED by tools/balance.py (roadmap R10). Do not edit by hand.",
           "-- Every floor's hunting tasks: one per monster that spawns there; each pays 80% of the most the check allows.",
           "SpireTasks.floorList = {"]
    for t in tasks:
        if True:
            lua.append(f'\t{{ id = "{t["id"]}", floor = {t["floor"]}, monster = "{t["monster"]}", count = {t["count"]}, '
                       f'gold = {t["gold"]}, points = {t["points"]} }},')
    lua.append("}")
    lua.append("for _, t in ipairs(SpireTasks.floorList) do\n\ttable.insert(SpireTasks.list, t)\nend")
    (ROOT / "server/data-spirebound/lib/spirebound/tasks_floors.lua").write_text("\n".join(lua) + "\n", encoding="utf-8")
    hp = ["-- Generated by tools/balance.py (R10c). Gold per house tile on each floor; !buyhouse charges it.",
          "SpireHouses = SpireHouses or {}", "SpireHouses.PRICE_PER_TILE = {"]
    hp += ["\t[%d] = %d," % (r["floor"], r["house_per_tile"]) for r in rows]
    hp.append("}")
    (ROOT / "server/data-spirebound/lib/spirebound/house_prices.lua").write_text("\n".join(hp) + "\n", encoding="utf-8")
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
          "## What the real game changes (review A3-1 and E-1, 2026-11-26)",
          f"The engine adds 1.5x more experience while stamina is above 39 hours (Tibia's rested bonus, the first 3 hours of a "
          f"day) and multiplies every drop chance by {rate_loot():g} (capped at 100%). Its hidden 1.5x below level 50 is taken "
          "back out on every kill (Q83, Jay 2026-11-27: Floor 1 should take 11-15 hours). The table above uses the plain "
          "numbers; this column is what a fully rested character gets. Loot waits on Q84.", "",
          "| Floor | Hours to climb (plan) | With the engine's bonuses | Gold/h (plan) | With loot rate |", "|---|---|---|---|---|"]
    for r in rows:
        L.append(f"| {r['floor']} | {r['band_hours']} | {r['real_band_hours']} | {r['gold_h']:,} | {r['real_gold_h']:,} |")
    off = [r for r in rows if r["floor"] >= 2 and abs(r["real_band_hours"] - TARGETS[r["floor"]]["hours"]) > 0.15 * TARGETS[r["floor"]]["hours"]]
    L += ["", "No longer within 15% of the hours target once the bonuses are counted: "
          + (", ".join(f"Floor {r['floor']} ({r['real_band_hours']} h against {TARGETS[r['floor']]['hours']})" for r in off) or "none") + ".", "",
          "## Waycrystals (a gold sink, DESIGN.md 3.7)",
          "Each floor's crystal costs about 4 minutes of that floor's hunting income (a trip there and back about 8): "
          + ", ".join(f"Floor {r['floor']} {__import__('crystals').price(r['floor'], {x['floor']: x['gold_h'] for x in rows}):,}" for r in rows) + ".", "",
          "## Cooking (FD4, a comfort, never power)",
          "Dishes give one small comfort out of a fight (no damage, defence, experience or loot); a feast lasts "
          f"{__import__('gen_depth').FEAST_MULT:g}x as long: "
          + "; ".join(f"{d['name']} ({d['comfort']} {d['amount']}, {d['minutes']} min)" for d in __import__('gen_depth').DISHES) + ".", "",
          "## Rules the check enforces", f"- Each floor's climb within 15% of its hours target, and its coins within 15% of its gold target.",
          f"- Supplies never eat more than {SUPPLY_MAX_SHARE:.0%} of the coins.",
          f"- A typical house on Floors 1-2 costs {HOUSE_HOURS[0]}-{HOUSE_HOURS[1]} hours of hunting.",
          f"- A hunting task pays at most {TASK_GOLD_SHARE:.0%} of what the hunting time it takes earns on its floor.",
          "- No shop sells anything back for as much as it charges.", "",
          "## Checks", "All checks pass." if not problems else "**Problems:**\n" + "\n".join("- " + p for p in problems)]
    (ROOT / "BALANCE.md").write_text("\n".join(L) + "\n", encoding="utf-8")


# ---------------------------------------------------------------- gear progression (docs/superpowers/specs/2026-11-23-gear-progression-design.md)
def gear_problems():
    """Ceiling rule (4.3), shop rule (4.9), pacing of style (4.2) and Hearth Shards (4.4)."""
    import gen_gear as g
    out = []
    p = g.weapon_power
    f1max, f2new = p(1, 5, 10, True), p(2, 0, 0, False)
    if not 0.90 <= f2new / f1max <= 0.95:
        out.append(f"gear: a new Floor 2 weapon is {f2new / f1max:.0%} of a maxed Floor 1 weapon (want 90-95%)")
    if not f1max < p(2, 2, 5, False):
        out.append("gear: a maxed Floor 1 weapon beats a Floor 2 weapon at tier 2, familiarity 5")
    h = g.hours_to_pass(2)
    if not 2 <= h <= 3:
        out.append(f"gear: a Floor 2 weapon passes a maxed Floor 1 weapon after {h:.1f} h (want 2-3 h)")
    if not g.shop_power() < p(1, 2, 0, False):
        out.append("gear: shop starter weapon is not beaten by the Floor 1 main weapon at tier 2")
    if not g.shop_power() > 1.0:
        out.append("gear: shop starter weapon is no better than shop gear")
    # ST1 (style trees v2): no finished style deals more than about 25% extra damage (Reaver's off-hand strike and
    # Stormbreaker's cleave are counted at their full share), and every extreme final pays with a minus
    for voc, (key, _n, paths) in g.STYLE.items():
        for pk, *_rest, finals in paths:
            for fk, *_f in finals:
                dmg = 0.0
                for k in (key, pk, fk):
                    for kind, v in g.PASSIVES[k]:
                        if kind in ("damage", "damage_noshield", "far_damage", "single_damage"):
                            dmg += 10 * v
                        if kind == "offhand":
                            dmg += 10 * v * 0.66 / 2          # an off-hand blade is about two thirds of a main weapon
                if dmg > 0.40 or (pk != "reaver" and dmg > 0.27):
                    out.append(f"style: {fk} finishes at +{dmg:.0%} damage (want at most about 25%; Reaver about 35-40%)")
                if fk in g.EXTREME_FINALS and fk != "blightcaller" and not any(v < 0 for _k, v in g.PASSIVES[fk]):
                    out.append(f"style: {fk} is an extreme final with no minus")
    for stage, (lo, hi) in {1: (35, 40), 2: (80, 90), 3: (250, 300)}.items():
        lvl = g.style_stage_level(stage)
        if not lo <= lvl <= hi:
            out.append(f"gear: style stage {stage} finishes at level {lvl} (want {lo}-{hi})")
    lvl = g.shard_tier5_level()
    if not 30 <= lvl <= 35:
        out.append(f"gear: a solo player saving every shard reaches tier 5 at level {lvl} (want 30-35)")
    return out


def reward_problems():
    """S1b: what a ground pays per person against its type (GROUND_TYPES reward), from tools/gen_economy.py's model.
    Solo grounds: experience and gold against the floor's smoothed solo ladder, within 0.75x-1.5x of the type's target.
    Party levels (a group of 3-4): each member earns at least 0.95x the group target times what a solo hunter earns on
    the same ground (team hunting beats solo, DESIGN.md 7.1)."""
    import csv
    f = ROOT / "data" / "economy_rewards.csv"
    if not f.exists():
        return ["data/economy_rewards.csv is missing: run tools/gen_economy.py"]
    out = []
    for r in csv.DictReader(open(f, encoding="utf-8")):
        target = GROUND_TYPES[r["type"]]["reward"]
        if r["kind"] == "solo":
            ratio = float(r["ratio"])
            if not 0.75 * target <= ratio <= 1.5 * target:
                out.append(f"reward: {r['ground']} ({r['type']}) pays {ratio}x the floor baseline, want {target}x (0.75x-1.5x of it)")
        elif float(r["vs_solo"]) < 0.95 * target:
            out.append(f"reward: a party of four in {r['ground']} earns {r['vs_solo']}x a solo hunter there, want {target}x")
    return out


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
    problems += spawn_rule_problems()
    problems += gear_problems()
    problems += reward_problems()
    import gen_adventure                           # AD4/AD5: roamers and dig spots fit their grounds and danger budgets
    problems += gen_adventure.problems()
    import gen_depth                               # FD2/FD4/FD5: dishes are comforts only, features stay small, Works sink gold
    gen_depth.build()
    problems += gen_depth.problems()
    write(rows, problems, tasks)
    print(f"wrote BALANCE.md, data/balance_floors.csv and tasks_floors.lua ({len(rows)} floors, {len(tasks)} tasks)")
    if problems:
        print("BALANCE PROBLEMS:\n" + "\n".join(problems))
        if "--check" in argv:
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
