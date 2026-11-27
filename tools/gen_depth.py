#!/usr/bin/env python3
"""Floor 1 depth, Session D's tables (roadmap FD2, FD4, FD5; docs/superpowers/specs/2026-11-27-floor1-depth-design.md
4.2, 4.4 and 4.5): cooking on the hub fires, one feature per hunting ground, and the Town Works.

One table, generated files (never hand-edit them):
    server/data-spirebound/lib/spirebound/depth_data.lua   read by cooking.lua, ground_features.lua, works.lua
    data/item_renames_depth.json                           merged into items.xml by tools/build_server.py

Rules the check enforces (`problems()`, called by `python tools/balance.py --check`):
  - a dish only gives a comfort from COMFORTS (no damage, defence, experience or loot: DESIGN.md 8.2, design 4.4);
  - comforts stay small and slow (caps below), feasts at most twice as long as eating alone;
  - every dish is reachable from ingredients that drop, are fished or come from a ground feature;
  - a ground feature's reward stays under a few minutes of that ground's income (it adds variety, not a farm);
  - the Works are a gold sink: given gold is destroyed and the project size follows the active accounts.
Usage: python tools/gen_depth.py
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_LUA = ROOT / "server/data-spirebound/lib/spirebound/depth_data.lua"
OUT_JSON = ROOT / "data/item_renames_depth.json"

# ================================================================ FD4 cooking (design 4.4)
# Things that count as a fire: hub campfires, coal basins, ovens (house kits), a lit Beacon bowl, fireplaces.
FIRES = [1996, 1997, 2002, 2003, 2113, 2535, 2536, 2537, 2538, 2539, 2540, 2541, 2542, 30965]
FIRE_REACH = 1                     # stand next to the fire (or on it) to cook

# Comforts: small, slow and out of a fight. Nothing else is allowed (the check refuses any other kind).
#   regen  health per tick out of a fight       mana  mana per tick out of a fight
#   cap    extra carrying strength (oz)         light a light around you (level)
#   townspeed  walking speed inside a town or other safe zone (speed points)
COMFORTS = ("regen", "mana", "cap", "light", "townspeed")
COMFORT_CAP = {"regen": 8, "mana": 8, "cap": 120, "light": 9, "townspeed": 60}
COMFORT_TICK = 3                   # seconds between regen/mana ticks
MAX_MINUTES = 60                   # no dish lasts longer than an hour eaten alone
FEAST_MULT = 2.0                   # eating from a feast lasts this many times longer than eating alone (design: "longer")
FEAST_SERVINGS = 4                 # a feast feeds four
FEAST_MINUTES = 10                 # and stays by the fire for ten minutes
TITLES = [(5, "Camp Cook"), (None, "Hearth Cook")]   # None = every dish of Floor 1

# Ingredients: item id -> (name in the game, where it comes from). Renamed placeholders say what they are.
INGREDIENTS = {
    3578: ("fish", "Hearth Minnow, from fishing"),
    7159: ("green perch", "River Perch, from fishing"),
    3579: ("salmon", "Silver Carp, from fishing"),
    901: ("Old Whiskers", "the legendary fish of Floor 1"),
    3577: ("meat", "boars, wolves, wasps and most beasts"),
    3582: ("ham", "Bristle Boars and their elders"),
    5902: ("honeycomb", "Meadow Wasps, and burnt-out nests in Waspgrass Fields"),
    3728: ("truffle", "dug where a Boar Meadow boar has rooted"),
    5678: ("turtle egg", "turtle nests on Reedmarsh's sandbars at low tide"),
    3588: ("bramble berry", "the bushes of the Bramble Run"),
    3738: ("sling herb", "Sproutlings and Hedge Hexers"),
}
RENAMED_INGREDIENTS = {   # placeholders that need a Spirebound name (the rest keep the client's own)
    901: ("Old Whiskers", "Old Whiskers", "The legendary catfish of Floor 1's waters, whiskers as long as your arm. Some say it cooks."),
    3728: ("truffle", "truffles", "A knobbly black truffle that smells of earth and rain. Cook it on a fire."),
    5678: ("turtle egg", "turtle eggs", "A leathery turtle egg from a Reedmarsh sandbar. Cook it on a fire."),
    3588: ("bramble berry", "bramble berries", "A dark, sweet berry from the Bramble Run."),
}

# Dishes. raw = cooked from one ingredient on a fire; base + add = a combined dish (use add on base by a fire).
# hint = said by an NPC for the three that are hard to guess (design: "NPC lines ... hint at them plainly").
DISHES = [
    dict(id="grilled_minnow", name="Grilled Minnow", item=13992, raw=3578, comfort="regen", amount=2, minutes=20, food=12),
    dict(id="smoked_perch", name="Smoked Perch", item=14085, raw=7159, comfort="mana", amount=2, minutes=20, food=13),
    dict(id="seared_meat", name="Seared Meat", item=22187, raw=3577, comfort="regen", amount=2, minutes=15, food=15),
    dict(id="boar_roast", name="Boar Roast", item=12310, raw=3582, comfort="cap", amount=40, minutes=30, food=30),
    dict(id="roast_truffle", name="Roast Truffle", item=3724, raw=3728, comfort="light", amount=6, minutes=30, food=8),
    dict(id="baked_turtle_egg", name="Baked Turtle Egg", item=10453, raw=5678, comfort="townspeed", amount=20, minutes=30, food=10),
    dict(id="carp_steak", name="Carp Steak", item=10219, raw=3579, comfort="regen", amount=4, minutes=25, food=18),
    dict(id="whiskers_pie", name="Whiskers Pie", item=16103, raw=901, comfort="regen", amount=8, minutes=60, food=40),
    dict(id="hunters_roast", name="Hunter's Roast", item=3583, base="boar_roast", add=3728, comfort="cap", amount=100, minutes=45, food=40),
    dict(id="honey_glazed_ham", name="Honey-Glazed Ham", item=31560, base="boar_roast", add=5902, comfort="regen", amount=5, minutes=40, food=35),
    dict(id="truffle_omelette", name="Truffle Omelette", item=17820, base="baked_turtle_egg", add=3728, comfort="light", amount=9, minutes=60, food=20,
         hint="A turtle egg baked, then a truffle shaved over it while it is still on the fire. Lights your way for an hour."),
    dict(id="bramble_tart", name="Bramble Tart", item=6393, base="baked_turtle_egg", add=3588, comfort="townspeed", amount=50, minutes=45, food=20,
         hint="Bake a turtle egg, then stir in a handful of bramble berries before it leaves the fire. You will fly through town."),
    dict(id="herb_crusted_perch", name="Herb-Crusted Perch", item=3602, base="smoked_perch", add=3738, comfort="mana", amount=6, minutes=40, food=25,
         hint="Smoke a perch, then press a sling herb into it on the fire. Clears the head like nothing else."),
]
DISH_SELL = 0.1    # NPCs pay a tenth of what the ingredients would fetch (design: "NPCs buy them for little")
COMFORT_TEXT = {"regen": "you heal a little faster out of a fight", "mana": "your mana returns a little faster out of a fight",
                "cap": "you can carry a little more", "light": "a warm light goes with you",
                "townspeed": "you walk faster in town"}


def dish_desc(d):
    how = (f"Cooked from {INGREDIENTS[d['raw']][0]} on a fire" if d.get("raw")
           else f"A {next(x['name'] for x in DISHES if x['id'] == d['base'])} finished with {INGREDIENTS[d['add']][0]} on the fire")
    return f"{how}. Eat it and {COMFORT_TEXT[d['comfort']]} for {d['minutes']} minutes."


# ================================================================ FD2 one feature per ground (design 4.2)
# id = ground id (the "Ground lore" row on the Discoveries page). gold = minutes of that ground's solo income a reward
# pays (data/economy_rewards.csv), kept small so no feature becomes a farm (the check caps it). Map spots: maps/floor1_features.py.
FEATURES = [
    dict(id="starter_west", name="The Ratcatcher's Bell", bell=dict(cooldown=1200, rats=12, monster="Field Rat", seconds=60)),
    dict(id="starter_east", name="The night lilies", lilies=dict(toads=2, monster="Hopper Toad", luck=3)),
    dict(id="starter_south", name="Seedlings", seedling=dict(chance=0.35, grow=120, elder="Elder Sproutling", item=3737)),
    dict(id="wasp_fields", name="The wasp nests", nests=dict(regrow=600, wasps=3, monster="Meadow Wasp", queen="Nest Queen", honey=2)),
    dict(id="boar_meadow", name="Truffles", truffles=dict(every=20, chance=0.12, root=8, lasts=180, item=6482)),
    dict(id="burrow_hills", name="The mole tunnels", moles=dict(collapse=60, closed=5708)),
    dict(id="wolf_copse", name="The Howling Stone", howl=dict(cooldown=600, ground_gap=120, night_extra=3, monster="Meadow Wolf", stay=180)),
    dict(id="reed_marsh", name="The tide", tide=dict(every=1800, low=600, nests=3, eggs=2, sand=104, nest_item=14759,
                                                     chest_item=2472, chest_gold_min=4)),
    dict(id="thornsnap_hollow", name="The vine walls", vines=dict(every=1200, share=0.5, vine=3696)),
    dict(id="shard_fields", name="The chimes", chimes=dict(wind=180, cache_gold_min=6, shard_chance=0.3)),
    dict(id="bandit_road", name="The wanted poster", poster=dict(every=3600, stays=3000, monster="Bandit Lieutenant",
                                                                 badge=9218, bounty_min=8)),
    dict(id="old_quarry", name="The lift", lift=dict()),
    dict(id="apex_watchtower", name="The signal fire", signal=dict(hold=180, wave_every=30, wave=3, monster="Stonehorn Ram",
                                                                    burns=1200, gold_bonus=0.10)),
    dict(id="bramble_run", name="Bramble berries", berries=dict(rouse=0.15, monster="Thornsnap")),
    dict(id="smugglers_ridge", name="The contraband stashes", stash=dict(every=3600, glint=60, gold_min=5, guards=2,
                                                                         monster="Road Bandit")),
    dict(id="fallen_bastion", name="The old ballista", ballista=dict(cooldown=120, reach=12, dmg=(60, 120))),
]
FEATURE_GOLD_CAP_MIN = 10        # no feature reward pays more than ten minutes of its ground's solo income
BADGE = (9218, "Lieutenant's Badge", "Lieutenant's Badges", "A bandit lieutenant's tin badge. The wanted poster on the Bandit Road pays for it.")

# ================================================================ FD5 the Town Works (design 4.5)
# Size follows the accounts active in the last week so a project fills in about three to five days: each active account
# is expected to give about PER_ACCOUNT_DAY gold a day (about 15 minutes of a mid-Floor 1 hunter's coins), and a project
# wants FILL_DAYS of that. Given gold is destroyed (a sink). One account may give at most DAILY_CAP of a project a day.
WORKS = [
    dict(id="bridge", name="The River Bridge", title="Bridgewright",
         done="The broken bridge south of the Fisher's Huts is rebuilt: a short way across the river to the marsh side."),
    dict(id="lanterns", name="The Road Lanterns", title="Lamplighter",
         done="The lamp posts on the road to Millcross are lit."),
    dict(id="camp", name="The Stair Camp", title="Campmaster",
         done="The Stair Camp stands at the foot of the labyrinth: a fire to cook on, a healer's shrine and a supply crate."),
    dict(id="keepgate", name="The Watchtower Gate", title="Stairwright",
         done="The fallen north gate of the Old Watchtower's keep is cleared: a second way into the keep."),
    dict(id="garden", name="The Monument Garden", title="Gardener",
         done="Flower beds and benches round the Monument, and a plaque with every giver's name."),
]
PER_ACCOUNT_DAY = 1000
FILL_DAYS = 4
STEP = [1.0, 1.2, 1.4, 1.6, 1.8]      # later projects are a little bigger
MIN_SIZE = 20000                       # never smaller than this (five testers still need a few days)
DAILY_CAP = 0.25                       # one account gives at most a quarter of a project a day
CAMP_POTIONS = (266, 10)               # the Stair Camp's supply crate: ten health potions at the shop price

# ================================================================ helpers
def lua(v):
    if isinstance(v, bool):
        return "true" if v else "false"
    if v is None:
        return "nil"
    if isinstance(v, (int, float)):
        return repr(v)
    if isinstance(v, str):
        return '"' + v.replace("\\", "\\\\").replace('"', '\\"') + '"'
    if isinstance(v, (list, tuple)):
        return "{ " + ", ".join(lua(x) for x in v) + " }"
    if isinstance(v, dict):
        return "{ " + ", ".join(f"{k} = {lua(x)}" for k, x in v.items()) + " }"
    raise TypeError(v)


def solo_gold():
    out = {}
    for r in csv.DictReader(open(ROOT / "data/economy_rewards.csv", encoding="utf-8")):
        if r["kind"] == "solo":
            out[r["id"]] = float(r["per_person_gold_h"])
    return out


def build():
    L = ["-- Generated by tools/gen_depth.py: edit the tables there, not this file.",
         "SpireDepthData = SpireDepthData or {}",
         "SpireDepthData.cooking = {",
         f"\tfires = {lua(FIRES)}, reach = {FIRE_REACH}, tick = {COMFORT_TICK},",
         f"\tfeastMult = {FEAST_MULT}, feastServings = {FEAST_SERVINGS}, feastMinutes = {FEAST_MINUTES},",
         "\ttitles = { " + ", ".join(f"{{ {lua(n)}, {lua(t)} }}" for n, t in TITLES) + " },",
         "\tingredients = {"]
    L += [f"\t\t[{iid}] = {lua(dict(name=n, from_=w)).replace('from_', 'from')}," for iid, (n, w) in INGREDIENTS.items()]
    L.append("\t},")
    L.append("\tdishes = {")
    for d in DISHES:
        row = {k: d[k] for k in ("id", "name", "item", "comfort", "amount", "minutes", "food")}
        for k in ("raw", "base", "add", "hint"):
            if d.get(k) is not None:
                row[k] = d[k]
        L.append(f"\t\t{lua(row)},")
    L.append("\t},")
    L.append("}")
    gold = solo_gold()
    gold["apex_watchtower"] = gold.get("old_quarry", 10000)
    L.append("SpireDepthData.features = {")
    for f in FEATURES:
        row = dict(f)
        for key, sub in f.items():
            if isinstance(sub, dict):
                sub = dict(sub)
                for k in list(sub):
                    if k.endswith("_min"):      # minutes of the ground's income -> gold
                        sub[k[:-4]] = int(round(gold[f["id"]] * sub.pop(k) / 60 / 10) * 10)
                row[key] = sub
        L.append(f"	{lua(row)},")
    L.append("}")
    L.append("SpireDepthData.works = {")
    L.append(f"	perAccountDay = {PER_ACCOUNT_DAY}, fillDays = {FILL_DAYS}, minSize = {MIN_SIZE}, dailyCap = {DAILY_CAP},")
    L.append(f"	step = {lua(STEP)}, campPotions = {lua(list(CAMP_POTIONS))},")
    L.append("	projects = {")
    L += [f"		{lua(w)}," for w in WORKS]
    L.append("	},")
    L.append("}")
    OUT_LUA.write_bytes(("\n".join(L) + "\n").encode("utf-8"))
    renames = {}
    for iid, (n, p, desc) in RENAMED_INGREDIENTS.items():
        renames[str(iid)] = dict(name=n, plural=p, description=desc)
    for d in DISHES:
        assert str(d["item"]) not in renames, f"item {d['item']} used twice"
        renames[str(d["item"])] = dict(name=d["name"], plural=d["name"] + ("" if d["name"].endswith("s") else "s"),
                                       description=dish_desc(d))
    renames[str(BADGE[0])] = dict(name=BADGE[1], plural=BADGE[2], description=BADGE[3])
    OUT_JSON.write_bytes((json.dumps(renames, indent=1) + "\n").encode("utf-8"))
    return renames


def problems():
    out = []
    ids = {d["id"] for d in DISHES}
    items = [d["item"] for d in DISHES]
    if len(set(items)) != len(items):
        out.append("cooking: two dishes share an item")
    if not 10 <= len(DISHES) <= 15:
        out.append(f"cooking: {len(DISHES)} dishes, the design says about twelve")
    for d in DISHES:
        if d["comfort"] not in COMFORTS:
            out.append(f"cooking: {d['name']} gives '{d['comfort']}', not a comfort (no damage, defence, experience or loot)")
            continue
        if d["amount"] > COMFORT_CAP[d["comfort"]]:
            out.append(f"cooking: {d['name']} gives {d['amount']} {d['comfort']}, the cap is {COMFORT_CAP[d['comfort']]}")
        if d["minutes"] > MAX_MINUTES:
            out.append(f"cooking: {d['name']} lasts {d['minutes']} minutes, the cap is {MAX_MINUTES}")
        if d.get("raw") and d["raw"] not in INGREDIENTS:
            out.append(f"cooking: {d['name']} is cooked from item {d['raw']}, which is no ingredient")
        if d.get("base") and (d["base"] not in ids or d.get("add") not in INGREDIENTS):
            out.append(f"cooking: {d['name']} combines things that do not exist")
        if bool(d.get("raw")) == bool(d.get("base")):
            out.append(f"cooking: {d['name']} must be either cooked from one ingredient or combined")
    if FEAST_MULT > 2:
        out.append(f"cooking: a feast lasts {FEAST_MULT}x eating alone, at most 2x")
    if sum(1 for d in DISHES if d.get("hint")) != 3:
        out.append("cooking: the design wants exactly three hard-to-guess dishes with an NPC hint")
    pairs = [(d["base"], d["add"]) for d in DISHES if d.get("base")]
    if len(set(pairs)) != len(pairs):
        out.append("cooking: two combined dishes use the same pair")
    raws = [d["raw"] for d in DISHES if d.get("raw")]
    if len(set(raws)) != len(raws):
        out.append("cooking: one ingredient cooks into two dishes")
    if len(WORKS) != 5 or len(STEP) != len(WORKS):
        out.append("works: the design has five projects, each with a size step")
    for n in (5, 50, 500):
        days = max(MIN_SIZE, n * PER_ACCOUNT_DAY * FILL_DAYS) / (n * PER_ACCOUNT_DAY)
        if n >= 20 and not 3 <= days <= 5:
            out.append(f"works: with {n} active accounts the first project takes {days:.1f} days, the design says 3 to 5")
    gids = [f["id"] for f in FEATURES]
    if len(set(gids)) != len(gids):
        out.append("features: a ground has two features")
    for f in FEATURES:
        for sub in f.values():
            if isinstance(sub, dict):
                for k, v in sub.items():
                    if k.endswith("_min") and v > FEATURE_GOLD_CAP_MIN:
                        out.append(f"features: {f['name']} pays {v} minutes of income, the cap is {FEATURE_GOLD_CAP_MIN}")
    return out


if __name__ == "__main__":
    r = build()
    print(f"wrote {OUT_LUA.name} ({len(DISHES)} dishes) and {OUT_JSON.name} ({len(r)} renamed items)")
    p = problems()
    if p:
        print("PROBLEMS:\n" + "\n".join(p))
