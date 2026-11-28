#!/usr/bin/env python3
"""The adventure layer's Session B tables (roadmap AD4, AD5; docs/superpowers/specs/2026-11-27-adventure-layer-design.md
4.4 and 4.5): rare roamers, treasure maps and their keepsakes, the addon hunts and the hidden places' items.

One table, generated files (never hand-edit them):
    server/data-spirebound/lib/spirebound/adventure_data.lua   read by roamers.lua, treasure_maps.lua, addon_hunts.lua
    data/item_renames_adventure.json                           merged into items.xml by tools/build_server.py

Money comes from the Floor 1 economy model (data/economy_rewards.csv, tools/gen_economy.py): a roamer's purse is about
10 minutes of its grounds' solo income, a dig 5 to 10 minutes of that ground's. `problems()` is called by
`python tools/balance.py --check`.
Usage: python tools/gen_adventure.py
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_LUA = ROOT / "server/data-spirebound/lib/spirebound/adventure_data.lua"
OUT_JSON = ROOT / "data/item_renames_adventure.json"

ROUGH, CUT, EMBER = 16124, 16119, 9636

# ---------------------------------------------------------------- AD4 rare roamers (design 4.4; names are Claude's call)
# weight: how much it counts against a ground's danger budget (tools/balance.py HABITS); the toad flees, so it is light.
# guards: monsters that come out with it and leave with it.
ROAMERS = [
    dict(id="goldback_toad", name="Goldback Toad", band=(5, 12), weight=1.5,
         grounds=["starter_east", "starter_south", "wasp_fields"],
         keepsake=(5799, "Goldback's Crown", "Goldback's Crowns",
                   "A tiny golden crown that sat on the Goldback Toad's head. A keepsake for a house shelf."),
         title="Toadcatcher"),
    dict(id="frenzied_boar", name="Frenzied Boar", band=(9, 18), weight=2.5,
         grounds=["boar_meadow", "burrow_hills"],
         keepsake=(3044, "Frenzied Tusk", "Frenzied Tusks",
                   "A tusk with a red scorch at the root, from the Frenzied Boar. A keepsake for a house wall."),
         title="Boarbane"),
    dict(id="pale_stag", name="Pale Stag", band=(14, 24), weight=2.5,
         grounds=["wolf_copse", "bramble_run", "thornsnap_hollow"],
         keepsake=(12544, "Pale Antlers", "Pale Antlers",
                   "White antlers from the Pale Stag, mounted for a house wall."),
         title="Staghunter"),
    dict(id="paymaster", name="The Paymaster", band=(19, 30), weight=2.5,
         grounds=["bandit_road", "smugglers_ridge", "fallen_bastion"],
         guards=[("Road Bandit", 2)],
         keepsake=(35571, "Paymaster's Strongbox", "Paymaster's Strongboxes",
                   "The bandits' payroll chest, empty now, with the Paymaster's tally still scratched inside the lid."),
         title="Payday"),
]
ROAMER_EVERY = (25 * 60, 45 * 60)     # a roamer comes out every 25 to 45 minutes (random)
ROAMER_STAYS = 15 * 60               # and is gone after 15 minutes
ROAMER_GATE_GAP = 8                  # never within 8 tiles of a gate
ROAMER_SIGHT = 7                     # "sighted" when a player first comes within 7 tiles
ROAMER_PURSE_MINUTES = 10
ROAMER_SHARDS = 2                    # rough Hearth Shards on every roamer
ROAMER_EMBER = 0.25                  # chance of a Beacon Ember
KEEPSAKE_CHANCE = 0.04               # 4%, with the shards' pity rule (sure at three times the expected wait)

# ---------------------------------------------------------------- AD5 treasure maps (design 4.5)
MAP_ITEM = (5706, "Tattered map", "Tattered maps",
            "A torn treasure map. Use it to read where it leads; use it again inside that ground to know if you are close.")
SHOVEL = 3457
# map drops (chance per kill; the engine's loot rate is 1 since QA20): 1% from these, 10% from Bandit Captains
MAP_DROPS = {"Road Bandit": 0.01, "Bandit Crossbowman": 0.01, "Hedge Hexer": 0.01, "Ruin Sentinel": 0.01,
             "Ruin Archer": 0.01, "Bandit Captain": 0.10}
# dig grounds (levels 12-30) and how many dig spots each: 24 in all, more in the level 20-28 grounds
DIG_GROUNDS = {"burrow_hills": 2, "wolf_copse": 2, "reed_marsh": 2, "bramble_run": 2, "thornsnap_hollow": 2,
               "shard_fields": 3, "bandit_road": 3, "smugglers_ridge": 3, "old_quarry": 3, "fallen_bastion": 2}
# the monsters that rise from a guarded dig (half the time, 2 to 3 of them): the ground's own
DIG_GUARDS = {"burrow_hills": "Burrow Mole", "wolf_copse": "Meadow Wolf", "reed_marsh": "Reed Snapper",
              "bramble_run": "Thornsnap", "thornsnap_hollow": "Thornsnap", "shard_fields": "Field Shardling",
              "bandit_road": "Road Bandit", "smugglers_ridge": "Road Bandit", "old_quarry": "Ruin Sentinel",
              "fallen_bastion": "Ruin Archer"}
DIG_MINUTES = (5, 10)
DIG_GUARD_CHANCE = 0.5
DIG_SHARD_CHANCE = 0.4               # 1-2 cut Hearth Shards
DIG_EMBER = 0.15
DIG_TITLE = (10, "Treasure Hunter")  # ten maps dug
TREASURE_KEEPSAKES = [
    ("smugglers_lantern", 10289, "Smuggler's Lantern", "Smuggler's Lanterns",
     "A shuttered lantern the smugglers signalled with. A keepsake for a house."),
    ("bandit_banner", 10415, "Bandit Banner", "Bandit Banners",
     "The road gang's tattered banner, dug out of a buried stash. A keepsake for a house wall."),
    ("ruin_idol", 8146, "Ruin Idol", "Ruin Idols",
     "A small stone idol from before the tower. Nobody knows who it was meant to be."),
    ("captains_sea_chest", 8773, "Captain's Sea Chest", "Captain's Sea Chests",
     "A bandit captain's chest, salt-stained from some far coast. A keepsake for a house."),
    ("climbers_compass", 10302, "Old Climber's Compass", "Old Climber's Compasses",
     "A compass that points up, not north. It belonged to a climber long before you."),
    ("wardwright_tablet", 28538, "Wardwright Tablet", "Wardwright Tablets",
     "A clay tablet marked by the Wardwrights, the tower's builders. A keepsake for a house."),
]

# ---------------------------------------------------------------- AD5 addon hunts (design 4.5; Q71)
# quest id -> the named target, the kind to kill first, how many, and the ground it waits in
ADDON_HUNTS = {
    "o_ran2": dict(target="Deadeye Sorrel", kind="Bandit Crossbowman", count=15, ground="smugglers_ridge"),
    "o_arc2": dict(target="The Page-Thief", kind="Hedge Hexer", count=15, ground="bandit_road"),
    "o_mys2": dict(target="Glasswing", kind="Field Shardling", count=15, ground="shard_fields"),
}

# ---------------------------------------------------------------- AD5 hidden places (s14, s15)
# Secret items say nothing about what they open or where (Jay, 2026-11-27: secrets are found by riddles and exploring)
VAULT_KEY = (9172, "Vault Key", "Vault Keys", "A heavy iron key stamped with a coin.")
VAULT_KEY_DROP = {"Bandit Captain": 0.02}
RUBBINGS = [  # the three marked stones of the Sealed Cut, named by the mark, never by the place
    ("old_quarry", 2819, "hammer-mark rubbing", "hammer-mark rubbings", "A charcoal rubbing of a mason's mark: a hammer."),
    ("fallen_bastion", 2833, "star-mark rubbing", "star-mark rubbings", "A charcoal rubbing of a mason's mark: a six-pointed star."),
    ("shard_fields", 4831, "wheel-mark rubbing", "wheel-mark rubbings", "A charcoal rubbing of a mason's mark: a wheel."),
]


def solo_gold():
    out = {}
    for r in csv.DictReader(open(ROOT / "data/economy_rewards.csv", encoding="utf-8")):
        if r["kind"] == "solo":
            out[r["id"]] = float(r["per_person_gold_h"])
    return out


def purse(roamer, gold):
    hour = sum(gold[g] for g in roamer["grounds"]) / len(roamer["grounds"])
    return int(round(hour * ROAMER_PURSE_MINUTES / 60 / 10) * 10)


def dig_gold(gid, gold):
    return tuple(int(round(gold[gid] * m / 60 / 10) * 10) for m in DIG_MINUTES)


def lua(v):
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return repr(v)
    if isinstance(v, str):
        return '"' + v.replace("\\", "\\\\").replace('"', '\\"') + '"'
    if isinstance(v, (list, tuple)):
        return "{ " + ", ".join(lua(x) for x in v) + " }"
    if isinstance(v, dict):
        return "{ " + ", ".join(f"{k} = {lua(x)}" for k, x in v.items()) + " }"
    raise TypeError(v)


def build():
    gold = solo_gold()
    roamers = []
    for r in ROAMERS:
        kid, kname, _kp, _kd = r["keepsake"]
        roamers.append(dict(id=r["id"], name=r["name"], lo=r["band"][0], hi=r["band"][1], grounds=r["grounds"],
                            purse=purse(r, gold), keepsake=kid, keepsakeName=kname, title=r["title"],
                            guards=[dict(name=n, count=c) for n, c in r.get("guards", [])]))
    digs = {g: dict(spots=n, guard=DIG_GUARDS[g], gold=list(dig_gold(g, gold))) for g, n in DIG_GROUNDS.items()}
    hunts = {q: dict(h) for q, h in ADDON_HUNTS.items()}
    L = ["-- Generated by tools/gen_adventure.py: edit the tables there, not this file.",
         "SpireAdventureData = {",
         f"\troamerEvery = {lua(list(ROAMER_EVERY))}, roamerStays = {ROAMER_STAYS}, roamerGateGap = {ROAMER_GATE_GAP},",
         f"\troamerSight = {ROAMER_SIGHT}, roamerShards = {ROAMER_SHARDS}, roamerEmber = {ROAMER_EMBER}, keepsakeChance = {KEEPSAKE_CHANCE},",
         f"\trough = {ROUGH}, cut = {CUT}, ember = {EMBER}, shovel = {SHOVEL}, mapItem = {MAP_ITEM[0]},",
         f"\tdigGuardChance = {DIG_GUARD_CHANCE}, digShardChance = {DIG_SHARD_CHANCE}, digEmber = {DIG_EMBER},",
         f"\tdigTitle = {lua(list(DIG_TITLE))},",
         "\troamers = {"]
    L += [f"\t\t{lua(r)}," for r in roamers]
    L.append("\t},")
    L.append("\tdigs = {")
    L += [f"\t\t{g} = {lua(d)}," for g, d in digs.items()]
    L.append("\t},")
    L.append("\ttreasureKeepsakes = {")
    L += [f"\t\t{lua(dict(id=i, item=iid, name=n))}," for i, iid, n, _p, _d in TREASURE_KEEPSAKES]
    L.append("\t},")
    L.append("\taddonHunts = {")
    L += [f"\t\t{q} = {lua(h)}," for q, h in hunts.items()]
    L.append("\t},")
    L.append(f"\tvaultKey = {VAULT_KEY[0]},")
    L.append("\trubbings = { " + ", ".join(f"{g} = {iid}" for g, iid, *_ in RUBBINGS) + " },")
    L.append("}")
    OUT_LUA.write_bytes(("\n".join(L) + "\n").encode("utf-8"))
    renames = {}
    items = [MAP_ITEM, VAULT_KEY] + [r["keepsake"] for r in ROAMERS] + [(iid, n, p, d) for _i, iid, n, p, d in TREASURE_KEEPSAKES] + \
        [(iid, n, p, d) for _g, iid, n, p, d in RUBBINGS]
    for iid, name, plural, desc in items:
        assert str(iid) not in renames, f"item {iid} used twice"
        renames[str(iid)] = dict(name=name, plural=plural, description=desc)
    OUT_JSON.write_bytes((json.dumps(renames, indent=1) + "\n").encode("utf-8"))
    return roamers, digs


def problems():
    """Checks for tools/balance.py --check: roamers and dig spots fit the grounds and the danger budgets."""
    import re
    import sys
    sys.path.insert(0, str(ROOT / "tools"))
    from balance import GROUND_TYPES, weight
    from gen_monsters import MONSTERS
    text = (ROOT / "server/data-spirebound/lib/spirebound/wilds_data.lua").read_text(encoding="utf-8")
    grounds = {m[0]: dict(type=m[1], lo=int(m[2]), hi=int(m[3])) for m in
               re.findall(r'\{ id = "([a-z_]+)", title = "[^"]*", type = "([a-z]+)".*?lo = (\d+), hi = (\d+)', text)}
    out = []
    for r in ROAMERS:
        if r["name"] not in MONSTERS:
            out.append(f"roamer {r['name']}: no such monster in tools/gen_monsters.py")
        load = r["weight"] + sum(weight(n) * c for n, c in r.get("guards", []))
        for g in r["grounds"]:
            gd = grounds.get(g)
            if not gd:
                out.append(f"roamer {r['name']}: ground {g} does not exist")
                continue
            if gd["lo"] > r["band"][1] or gd["hi"] < r["band"][0]:
                out.append(f"roamer {r['name']} (levels {r['band']}): {g} is levels {gd['lo']}-{gd['hi']}")
            b = GROUND_TYPES[gd["type"]]["budget"]
            # it appears past the gate (a calm, middle or deep band): it must fit in the room between middle and deep
            if load > b["deep"] - b["middle"]:
                out.append(f"roamer {r['name']}: weight {load} is more than {g}'s room between middle and deep "
                           f"({b['deep'] - b['middle']})")
    if sum(DIG_GROUNDS.values()) != 24:
        out.append(f"treasure maps: {sum(DIG_GROUNDS.values())} dig spots, the design says about 24")
    for g in DIG_GROUNDS:
        gd = grounds.get(g)
        if not gd or gd["lo"] < 11 or gd["hi"] > 30:
            out.append(f"treasure maps: {g} is not a level 12-30 ground")
        if DIG_GUARDS.get(g) not in MONSTERS:
            out.append(f"treasure maps: {g}'s dig guard {DIG_GUARDS.get(g)} is not a monster")
    for q, h in ADDON_HUNTS.items():
        for k in ("target", "kind"):
            if h[k] not in MONSTERS:
                out.append(f"addon hunt {q}: {h[k]} is not a monster")
        if h["ground"] not in grounds:
            out.append(f"addon hunt {q}: ground {h['ground']} does not exist")
    for name in list(MAP_DROPS) + list(VAULT_KEY_DROP):
        if name not in MONSTERS:
            out.append(f"map drops: {name} is not a monster")
    return out


if __name__ == "__main__":
    roamers, digs = build()
    total = sum(d["spots"] for d in digs.values())
    print(f"wrote {OUT_LUA.name} ({len(roamers)} roamers, {total} dig spots in {len(digs)} grounds) and {OUT_JSON.name}")
    for r in roamers:
        print(f"  {r['name']}: purse {r['purse']} gold")
