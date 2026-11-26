#!/usr/bin/env python3
"""Floor 1 economy model: gold earned vs supplies burned, per hunting ground and vocation (Jay, 2026-11-11: "what is the
economies burn rate going to be for runes, ammo, potions, etc?").

Reads the real game data (tools/gen_monsters.py loot, maps/floor1_plan.py camps, tools/gen_npcs.py prices,
server/data-spirebound/lib/spirebound/crafting.lua recipes) and writes ECONOMY.md (plain English for Jay) and
data/economy_floor1.csv. Fails the build if a vocation loses money at a hunting ground meant for its level, or if a
crafting recipe is worse than just buying the result.

The player model is deliberately simple and written down in ECONOMY.md (Claude's call, Jay can veto):
  * damage per second rises with level; a kill takes monster HP / DPS plus a few seconds of walking;
  * attacks come every 2 seconds; rangers fire one arrow per attack (arrows are always used up), spears break 3%;
  * damage taken comes from the monster's melee; Vanguards and Rangers heal it with health potions,
    Arcanists and Mystics with mana potions (their spells and runes run on mana).
Usage: python tools/gen_economy.py
"""
from __future__ import annotations

import csv
ROLE = {"xp": "experience", "money": "money"}
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "maps"))

from floor1_plan import CAMPS  # noqa: E402
from gen_monsters import MONSTERS, GOLD, PLAT  # noqa: E402
from gen_npcs import NPCS  # noqa: E402

def stage(level):
    """Experience stage (server/core-overrides/stages.lua; Q30, FLOOR1_WILDS_PLAN.md 3.1)."""
    return 10 if level <= 8 else 4 if level <= 20 else 3


# the ladder (FLOOR1_WILDS_PLAN.md 3.2): base experience per hour (before the stage) for a Vanguard at the middle level
LADDER_TARGET = {"starter_west": 1800, "starter_east": 2500, "starter_south": 3500, "wasp_fields": 5000, "boar_meadow": 7500,
                 "burrow_hills": 9000, "wolf_copse": 11000, "reed_marsh": 9000, "thornsnap_hollow": 13000, "shard_fields": 16000,
                 "bandit_road": 14500, "old_quarry": 19000}
# S1b: how fast each class kills against a Vanguard, measured 2026-11-26 in the client (routes s1b_<class>: three minutes
# each at Wolf Copse, level 15, and Bandit Road, level 23, fight kit on): kills 16 / 21 / 20 / 19.
CLASS_SPEED = {"Vanguard": 1.0, "Ranger (arrows)": 1.3, "Ranger (spears)": 1.3, "Arcanist/Mystic": 1.2}
PARTY = ("Vanguard", "Ranger (arrows)", "Arcanist/Mystic", "Arcanist/Mystic")   # the group the party levels are made for
# a party meets monsters in packs, so it spends less time finding the next kill: measured 2026-11-26 in the Smugglers'
# Cellar (tools/party_run.py, five Pilots): 56 kills in 353 s of hunting = 6.3 s a kill, about 1.5 s of it fighting
PARTY_FIND = 4.8
WATCHTOWER_BASE = 26000                     # not modelled yet: the plan's target for the outer courtyard
PRICE = {}                                  # item id -> cheapest NPC price (what a player pays)
BUYBACK = {}                                # item id -> best NPC buy-back (what an NPC pays the player)
for d in NPCS.values():
    for _n, cid, buy, sell in d.get("shop", []):
        if buy:
            PRICE[cid] = min(PRICE.get(cid, buy), buy)
        if sell:
            BUYBACK[cid] = max(BUYBACK.get(cid, sell), sell)
HP_POT, MP_POT, ARROW, SPEAR = 266, 268, 3447, 3277


def recipes():
    """Crafting recipes from the Lua table, so the model and the game can't disagree."""
    text = (ROOT / "server/data-spirebound/lib/spirebound/crafting.lua").read_text(encoding="utf-8")
    out = []
    for m in re.finditer(r'\{ npc = "([^"]+)", name = "([^"]+)", item = (\d+), count = (\d+), gold = (\d+), '
                         r'needs = \{ ((?:\{ \d+, \d+ \},? ?)+) \}, worth = (\d+)', text):
        needs = [(int(a), int(b)) for a, b in re.findall(r"\{ (\d+), (\d+) \}", m.group(6))]
        out.append(dict(npc=m.group(1), name=m.group(2), item=int(m.group(3)), count=int(m.group(4)),
                        gold=int(m.group(5)), needs=needs, worth=int(m.group(7))))
    return out


RECIPES = recipes()
# what a material is worth to players: the gold a crafted result saves, shared out over its materials
MATERIAL = {}
for r in RECIPES:
    saved = r["worth"] - r["gold"]
    units = sum(c for _i, c in r["needs"])
    for iid, c in r["needs"]:
        MATERIAL[iid] = max(MATERIAL.get(iid, 0), saved / units)


def dps(level):
    return 4 + 1.0 * level


def drop_value(name):
    """Average gold per kill, NPC buy-back of the loot, and player value of crafting materials."""
    gold = npc = mat = 0.0
    for iid, chance, maxc in MONSTERS[name].get("loot", []):
        avg = chance / 100000 * (maxc + 1) / 2
        if iid == GOLD:
            gold += avg
        elif iid == PLAT:
            gold += avg * 100
        elif iid in MATERIAL:
            mat += avg * MATERIAL[iid]
            npc += avg * BUYBACK.get(iid, 0)
        else:
            npc += avg * BUYBACK.get(iid, 0)
    return gold, npc, mat


def melee(name):
    return max((-a[2] for a in MONSTERS[name]["attacks"] if a[0] == "melee"), default=0)


def placed(design, lv):
    """The monsters a level really holds: each clearing's groups repeated by band (H14 BAND_DENSITY, as maps/designed.py
    places them; a lone loner is never repeated)."""
    from floor1_plan import BAND_DENSITY
    from balance import HABITS
    density = dict(BAND_DENSITY, **design.get("density", {}))
    out = []
    for cl in lv["clearings"]:
        if not isinstance(cl[6], list):
            continue
        for grp in cl[6]:
            lone = len(grp) == 1 and grp[0][1] == 1 and HABITS.get(grp[0][0], ("",))[0] == "loner"
            out += list(grp) * (1 if lone else density.get(cl[4], 1))
    return out


def refill(c):
    """Kills an hour a ground can supply: the monsters on its solo levels times 3600 / respawn. Designed grounds count
    their clearings (the party level is left out); the old loop grounds are dense enough not to limit anyone."""
    from floor1_plan import DESIGNS
    if not c.get("design"):
        return 10 ** 6
    d = DESIGNS[c["design"]]
    n = sum(k for lv in d["levels"].values() if not lv.get("party") for _m, k in placed(d, lv))
    return n * 3600 / c["respawn"]


ROWS = []
for c in CAMPS:
    lo, hi = c["levels"]
    lvl = (lo + hi) // 2
    mons = [(n, share) for n, _g, share in c["mix"]]
    hp = sum(MONSTERS[n]["hp"] * s for n, s in mons)
    base_xp = sum(MONSTERS[n]["xp"] * s for n, s in mons)
    xp = base_xp * stage(lvl)
    g = sum(drop_value(n)[0] * s for n, s in mons)
    npc = sum(drop_value(n)[1] * s for n, s in mons)
    mat = sum(drop_value(n)[2] * s for n, s in mons)
    kill_s = hp / dps(lvl) + 8                     # fighting, then about 8 s to find and reach the next one
    kph = min(3600 / kill_s, 300)                  # a hunting ground can't feed one hunter more than ~300 kills an hour
    kph = min(kph, refill(c))                      # nor more than its monsters can respawn (FLOOR1_REVIEW.md F1-33)
    # damage taken per hour: half the monster's max melee every 2 s while fighting, ~60% of hits land, armour soaks a bit
    taken = sum(melee(n) * s for n, s in mons) / 2 * 0.6 * 0.8 * (hp / dps(lvl)) / 2 * kph
    hp_pots = taken * 0.35 / 100                   # regeneration and healing spells cover ~65%; potions the rest (~100 each)
    mp_pots = taken * 0.5 / 120                    # mages heal with spells and refill that mana with potions; wand shots run on regeneration
    runes = kph * 0.3 if lvl >= 15 else 0          # from level 15 mages conjure attack runes: about one per three kills
    for voc in ("Vanguard", "Ranger (arrows)", "Ranger (spears)", "Arcanist/Mystic"):
        kph = min(3600 / (hp / (dps(lvl) * CLASS_SPEED[voc]) + 8), 300, refill(c))   # S1b: each class at its own speed
        attacks = (hp / (dps(lvl) * CLASS_SPEED[voc])) / 2 * kph
        if voc == "Vanguard":
            cost = hp_pots * PRICE[HP_POT]
        elif voc == "Ranger (arrows)":
            cost = hp_pots * PRICE[HP_POT] + attacks * PRICE[ARROW]
        elif voc == "Ranger (spears)":
            cost = hp_pots * PRICE[HP_POT] + attacks * 0.03 * PRICE[SPEAR]
        else:
            cost = mp_pots * PRICE[MP_POT] + runes * PRICE[3147]
        gross = (g + npc) * kph
        ROWS.append(dict(id=c["id"], base_xp_h=round(base_xp * kph), camp=c["title"], levels=f"{lo}-{hi}", role=c["role"], vocation=voc, kills_h=round(kph),
                         xp_h=round(xp * kph), gold_h=round(g * kph), loot_npc_h=round(npc * kph),
                         materials_market_h=round(mat * kph), supplies_h=round(cost), net_npc_h=round(gross - cost),
                         net_with_trading_h=round(gross + mat * kph - cost)))

problems = []
# the ladder: each target met within 10%, and experience grounds rise at every step
ladder = []
for c in CAMPS:
    r = next(r for r in ROWS if r["id"] == c["id"])
    t = LADDER_TARGET[c["id"]]
    ladder.append((c, r["base_xp_h"], t))
    if abs(r["base_xp_h"] - t) > 0.1 * t:
        problems.append(f"{c['title']}: base experience {r['base_xp_h']}/h is not within 10% of the target {t}")
xp_steps = [(c, b) for c, b, _t in ladder if c["role"] == "xp"]
for (a, ba), (b, bb) in zip(xp_steps, xp_steps[1:]):
    if bb <= ba:
        problems.append(f"the ladder dips: {b['title']} ({bb}/h) is not better than {a['title']} ({ba}/h)")


def exp_for(level):
    return int(50 / 3 * (level ** 3 - 6 * level ** 2 + 17 * level - 12))


# the timeline: at each level hunt the best ground whose level range covers it (the Watchtower from 28)
timeline, hours = {}, 0.0
for lvl in range(1, 41):
    best = max([b for c, b, _t in ladder if c["levels"][0] <= lvl <= c["levels"][1]] + ([WATCHTOWER_BASE] if lvl >= 28 else []))
    hours += (exp_for(lvl + 1) - exp_for(lvl)) / (best * stage(lvl))
    timeline[lvl + 1] = hours
for r in ROWS:
    if r["vocation"] == "Ranger (arrows)" and r["levels"].split("-")[0] in ("1", "3", "5"):
        continue                                   # nobody is expected to fire paid arrows at rats: spears are the early ammo
    if r["net_with_trading_h"] < 0:
        problems.append(f"{r['vocation']} loses {-r['net_with_trading_h']} gold an hour at {r['camp']}")
    # FLOOR1_REVIEW.md F1-13: a small server (alpha, a quiet hour) has no market, so selling to NPCs alone must pay too
    if r["net_npc_h"] < 0:
        problems.append(f"{r['vocation']} loses {-r['net_npc_h']} gold an hour at {r['camp']} selling only to NPCs")
for rc in RECIPES:
    if rc["gold"] >= rc["worth"]:
        problems.append(f"recipe {rc['name']} costs {rc['gold']} gold but is only worth {rc['worth']}: nobody would craft it")



def party_share(exp, n, vocs):
    """server/core-overrides/events/scripts/party.lua SpirePartyShare: what each member gets of one kill."""
    return exp * (1 + 0.50 * (n - 1) + 0.10 * (max(vocs, 1) - 1)) / n


# S1b: reward per person against the floor's baseline. A ground pays in experience and in gold (money grounds pay more
# gold, experience grounds more experience), so its reward is the average of the two ratios. Each baseline is the solo
# ladder smoothed into one curve: an exponential fitted through every solo ground's class average at its middle level.
import math  # noqa: E402
SOLO_XP, SOLO_GOLD = {}, {}
for r in ROWS:
    SOLO_XP.setdefault(r["id"], []).append(r["base_xp_h"])
    SOLO_GOLD.setdefault(r["id"], []).append(r["gold_h"] + r["loot_npc_h"])


def avg(v):
    return sum(v) / len(v)


def fit(table):
    pts = [((c["levels"][0] + c["levels"][1]) / 2, math.log(max(avg(table[c["id"]]), 1))) for c in CAMPS]
    mx, my = avg([p[0] for p in pts]), avg([p[1] for p in pts])
    k = sum((x - mx) * (y - my) for x, y in pts) / sum((x - mx) ** 2 for x, _y in pts)
    return lambda level: math.exp(my + k * (level - mx))


BASE_XP, BASE_GOLD = fit(SOLO_XP), fit(SOLO_GOLD)
REWARDS = []


def reward(c, kind, name, gtype, lvl, xp, gold):
    rx, rg = xp / BASE_XP(lvl), gold / BASE_GOLD(lvl)
    REWARDS.append(dict(id=c["id"], ground=name, kind=kind, type=gtype, level=lvl, per_person_base_xp_h=round(xp),
                        per_person_gold_h=round(gold), xp_ratio=round(rx, 2), gold_ratio=round(rg, 2), ratio=round((rx + rg) / 2, 2),
                        vs_solo=""))


from floor1_plan import DESIGNS, CAVE_RESPAWN  # noqa: E402
for c in CAMPS:
    lo, hi = c["levels"]
    lvl = (lo + hi) / 2
    reward(c, "solo", c["title"], c["type"], lvl, avg(SOLO_XP[c["id"]]), avg(SOLO_GOLD[c["id"]]))
    # the ground's party level: a group of 3-4 inside any ground (balance.py budget("party"))
    lv = next((v for v in DESIGNS[c["design"]]["levels"].values() if v.get("party")), None) if c.get("design") else None
    if not lv:
        continue
    mons = placed(DESIGNS[c["design"]], lv)
    total = sum(k for _m, k in mons)
    hp = sum(MONSTERS[m]["hp"] * k for m, k in mons) / total
    bx = sum(MONSTERS[m]["xp"] * k for m, k in mons) / total
    loot = sum((drop_value(m)[0] + drop_value(m)[1]) * k for m, k in mons) / total
    group_dps = dps(lvl) * sum(CLASS_SPEED[v] for v in PARTY)
    kph = min(3600 / (hp / group_dps + PARTY_FIND), 300 * len(PARTY), total * 3600 / CAVE_RESPAWN)
    solo_xp = avg(SOLO_XP[c["id"]])
    reward(c, "party", c["title"] + ": " + lv["name"], "group", lvl,
           party_share(bx, len(PARTY), 4) * kph,             # one of each class: 4 vocations
           loot * kph / len(PARTY))                          # the loot split evenly
    REWARDS[-1]["vs_solo"] = round(REWARDS[-1]["per_person_base_xp_h"] / solo_xp, 2)

# S1c: the Old Watchtower, the large-group ground (4-8 players), modelled as a party of six: two Vanguards, two Rangers,
# an Arcanist and a Mystic (4 vocations), at level 34. Its courtyard, inner room and cave all count. With no solo ground
# at its levels, a member's experience is compared with the solo ladder's curve at that level.
from floor1_plan import APEX  # noqa: E402
WT_PARTY = ("Vanguard", "Vanguard", "Ranger (arrows)", "Ranger (arrows)", "Arcanist/Mystic", "Arcanist/Mystic")
wt_lvl = 34
wt_mons, wt_refill = [], 0.0
for part in ("courtyard", "inner", "cave"):
    groups = APEX[part]["groups"]
    n = sum(k for g in groups for _m, k in g)
    wt_mons += [(m, k) for g in groups for m, k in g]
    wt_refill += n * 3600 / APEX[part]["respawn"]
wt_total = sum(k for _m, k in wt_mons)
wt_hp = sum(MONSTERS[m]["hp"] * k for m, k in wt_mons) / wt_total
wt_bx = sum(MONSTERS[m]["xp"] * k for m, k in wt_mons) / wt_total
wt_loot = sum((drop_value(m)[0] + drop_value(m)[1]) * k for m, k in wt_mons) / wt_total
wt_kph = min(3600 / (wt_hp / (dps(wt_lvl) * sum(CLASS_SPEED[v] for v in WT_PARTY)) + PARTY_FIND), 300 * len(WT_PARTY), wt_refill)
reward(APEX, "party", APEX["title"] + " (a party of six)", "large", wt_lvl,
       party_share(wt_bx, len(WT_PARTY), 4) * wt_kph, wt_loot * wt_kph / len(WT_PARTY))
REWARDS[-1]["vs_solo"] = round(REWARDS[-1]["per_person_base_xp_h"] / BASE_XP(wt_lvl), 2)

(ROOT / "data").mkdir(exist_ok=True)
with open(ROOT / "data/economy_rewards.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(REWARDS[0].keys()))
    w.writeheader()
    w.writerows(REWARDS)
with open(ROOT / "data/economy_floor1.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(ROWS[0].keys()))
    w.writeheader()
    w.writerows(ROWS)

L = ["# Spirebound economy (Floor 1)", "",
     "*Generated by `tools/gen_economy.py` from the real monsters, shops and crafting recipes. Do not edit by hand.*", "",
     "## How gold moves",
     "- **Gold comes in** from monster drops, quest rewards, secrets, fishing and selling loot to NPCs.",
     "- **Gold goes out** on potions, ammunition, blank runes, blessings, house rent, carriage fares, guild and war fees, "
     "the Fortune Hall's 5% cut, skull fines, and crafting fees. Potions and ammunition are the everyday sink.",
     "- **Players trade with each other** because:",
     "  - every Floor 1 monster drops a **material** (honeycomb, wolf paw, turtle shell, rope belt...);",
     "  - NPCs pay almost nothing for materials, but crafters turn them into **things you can't buy** (sniper arrows, "
     "piercing bolts, cheaper strong potions, outfit addons);",
     "  - so a ranger needs the wolf hunter's paws, and a mage needs the wasp hunter's honeycombs;",
     "  - NPCs buy gear back at about a fifth of its price, so selling to another player on the market always pays more.",
     "- **Where:** the market opens from any depot locker (the Trade Hall in Hearthgate has five), and the Market Square has "
     "free stalls for face-to-face trades.", "",
     "## Burn rate per hour of hunting (at the middle level of each hunting ground)",
     "| Hunting ground | Levels | Vocation | Kills/h | XP/h | Gold/h | Supplies/h | Net (NPC only) | Net with trading |",
     "|---|---|---|---|---|---|---|---|---|"]
for r in ROWS:
    L.append(f"| {r['camp']} | {r['levels']} | {r['vocation']} | {r['kills_h']} | {r['xp_h']:,} | {r['gold_h'] + r['loot_npc_h']:,} | "
             f"{r['supplies_h']:,} | {r['net_npc_h']:,} | {r['net_with_trading_h']:,} |")
L += ["", "Net with trading counts what the materials are worth when sold to other players (the gold a crafted item saves).", "",
      "## Crafting recipes (gold sinks that need traded materials)", "| Crafter | Makes | Fee | Materials | Worth (shop price or value) |", "|---|---|---|---|---|"]
for rc in RECIPES:
    L.append(f"| {rc['npc']} | {rc['count']} x {rc['name']} | {rc['gold']} | " + ", ".join(f"{c} x {i}" for i, c in rc["needs"]) + f" | {rc['worth']} |")
L += ["", "## The model (Claude's call, Jay can veto)",
      "- Damage per second = 4 + level. A kill takes the monster's health divided by that, plus 8 seconds to reach the next one (at most 300 kills an hour).",
      "- One attack every 2 seconds. Arrows are always used up; spears break 3% of the time.",
      "- Damage taken: half the monster's best melee hit every 2 seconds, 60% of hits land, armour soaks 20%.",
      "- Vanguards and Rangers: regeneration and healing spells cover about 65% of it; health potions (about 100 each) the rest.",
      "- Arcanists and Mystics: heal with spells and refill half of that mana with potions; wand shots run on regeneration; from level 15 they conjure an attack rune for about every third kill (a blank rune each).",
      "", "## The levelling ladder (FLOOR1_WILDS_PLAN.md Part 3)",
      "Base experience per hour is before the stage (levels 1-8: 10x, 9-20: 4x, 21-50: 3x), for a Vanguard at the middle level.",
      "", "| Ground | Levels | Role | Base XP/h | Target |", "|---|---|---|---|---|"]
for c, b, t in ladder:
    L.append(f"| {c['title']} | {c['levels'][0]}-{c['levels'][1]} | {ROLE[c['role']]} | {b:,} | {t:,} |")
L.append(f"| The Old Watchtower | 28-40 | both | not modelled | {WATCHTOWER_BASE:,} |")
L += ["", "## What each ground pays per person, by class and in a party (S1b)",
      "Each class kills at its measured speed (against a Vanguard: Ranger 1.3x, Arcanist and Mystic 1.2x; measured in the client, "
      "2026-11-26). A party level is modelled as one of each class (shared experience, +50% per extra member and +10% per extra "
      "vocation, split four ways; the loot split evenly; monsters met in packs, about 4.8 s to the next kill, measured in the "
      "Smugglers' Cellar). The ratio is against the floor's smoothed solo ladder (experience and gold averaged); a party level "
      "is also compared with a solo hunter on the same ground. Targets (tools/balance.py GROUND_TYPES): training 1.0, class 1.2, "
      "mixed 1.1, group 1.5, large group 1.75 (the Old Watchtower is not modelled yet).", "",
      "| Ground | Kind | Type | Base XP/h per person | Gold/h per person | Ratio | Party vs solo |", "|---|---|---|---|---|---|---|"]
for r in REWARDS:
    L.append(f"| {r['ground']} | {r['kind']} | {r['type']} | {r['per_person_base_xp_h']:,} | {r['per_person_gold_h']:,} | {r['ratio']} | {r['vs_solo']} |")
L += ["", "Hours of hunting by hand to reach each level, by the model (real play is about 40% slower, the cavebot a little over twice as slow):", "",
      "| Level | Hours |", "|---|---|"]
for lvl in (6, 9, 11, 14, 18, 21, 25, 30, 35, 40):
    L.append(f"| {lvl} | {timeline[lvl]:.1f} |")
L += ["", "## Checks", ("All checks pass." if not problems else "**Problems:**\n" + "\n".join("- " + p for p in problems))]
(ROOT / "ECONOMY.md").write_text("\n".join(L) + "\n", encoding="utf-8")
print(f"wrote ECONOMY.md and data/economy_floor1.csv ({len(ROWS)} rows, {len(RECIPES)} recipes)")
if problems:
    sys.exit("economy check failed:\n" + "\n".join(problems))
