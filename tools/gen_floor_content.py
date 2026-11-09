#!/usr/bin/env python3
"""Generates the per-floor content for floors 2-10 from maps/floors.py (roadmap phases 4-5):
  - town NPCs (priest, banker, quartermaster, merchant, outfitter, two quest givers) -> server/data-spirebound/npc/floor<N>_*.lua
  - story quests, secrets, fish, perks, floor areas, house towns -> server/data-spirebound/lib/spirebound/floor_content.lua
  - quest-log entries -> server/data-spirebound/lib/core/quests/catalog/q<N>_<k>.lua (+ init.lua list)
Only floors whose map exists (tools/mapgen.py BUILT_FLOORS) are wired into the world, but content is generated for all.
Usage: python3 tools/gen_floor_content.py
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "maps"))
sys.path.insert(0, str(ROOT / "tools"))
from floors import FLOORS, origin, SIZE  # noqa: E402
import gen_npcs  # noqa: E402
import gen_monsters  # noqa: E402

DP = ROOT / "server" / "data-spirebound"
NPC_DIR = DP / "npc"
CATALOG = DP / "lib" / "core" / "quests" / "catalog"

PERKS = {
    2: [("field_medic", "Field Medic", "+15% healing from potions"), ("deep_reserves", "Deep Reserves", "+10% maximum mana")],
    3: [("fog_sense", "Fog Sense", "+1 light radius, +5% dodge in fog"), ("hunters_eye", "Hunter's Eye", "+3% critical chance")],
    4: [("iron_will", "Iron Will", "-20% duration of slows and stuns"), ("second_wind_perk", "Second Wind", "heal 15% when dropping below 25% (every 5 min)")],
    5: [("executioner", "Executioner", "+10% damage to targets under 30% health"), ("bulwark", "Bulwark", "+5% damage reduction")],
    6: [("ember_skin", "Ember Skin", "+10% fire protection"), ("forgehand", "Forgehand", "+5% melee and distance skill")],
    7: [("marsh_walker", "Marsh Walker", "+15 speed in swamps"), ("toxin_ward", "Toxin Ward", "+10% earth protection")],
    8: [("frost_blood", "Frost Blood", "+10% ice protection"), ("winter_vigor", "Winter Vigor", "+5% maximum health")],
    9: [("haggler", "Haggler", "NPC prices 5% better"), ("lucky_find", "Lucky Find", "+3% loot chance")],
    10: [("cobalt_heart", "Cobalt Heart", "+5% maximum health and mana"), ("ruinbreaker", "Ruinbreaker's Edge", "+5% damage to bosses")],
}
TIERS = ["large", "large", "medium", "medium", "small", "medium", "large", "medium", "small", "small", "small", "small"]
SECRET_WORDS = ["Hidden Cache", "Whispering Stone", "Lost Shrine", "Old Camp", "Forgotten Ledge", "Sunken Box", "Quiet Grove",
                "Hollow Tree", "Broken Statue", "Smuggler's Nook", "Silent Pool", "Last Lookout"]


def lua_str(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def old_secrets():
    out = {}
    with open(ROOT / "tools" / "secrets_src.csv", newline="") as f:
        for r in csv.DictReader(f):
            out.setdefault(int(r["floor"]), []).append((r["name"], r["tier"].lower().replace("mid", "medium"), r["trigger"]))
    return out


def npc_defs(n, f):
    town = f["town"]
    gear = gen_monsters.GEAR.get(n, [])
    gear_names = {3352: "chain helmet", 3359: "brass armor", 3282: "morning star", 3426: "studded shield", 3357: "plate armor",
                  3351: "steel helmet", 3279: "war hammer", 3065: "terra rod", 3068: "crystal wand", 3370: "knight armor",
                  3371: "knight legs", 3303: "great axe", 3070: "moonlight rod", 3072: "wand of decay", 3381: "crown armor",
                  3382: "crown legs", 3385: "crown helmet", 3281: "giant sword", 3067: "hailstorm rod", 3073: "wand of cosmic energy",
                  3364: "golden legs", 3392: "royal helmet", 3415: "guardian shield", 3280: "fire sword", 3422: "great shield",
                  3360: "golden armor", 3366: "magic plate armor"}
    out = {}
    out[f"floor{n}_priest"] = dict(name=f"Priest of {town}", desc=f"the priest of {town}", look=(57,), kind="priest",
                                   greet=f"Peace, |PLAYERNAME|. I can {{heal}} you, and offer {{blessings}}.", voices=[])
    out[f"floor{n}_banker"] = dict(name=f"Banker of {town}", desc=f"the banker of {town}", look=(132, 115, 76, 35, 116, 0),
                                   kind="bank", greet="Welcome, |PLAYERNAME|. Your {balance}? {Deposit}? {Withdraw}?", voices=[])
    out[f"floor{n}_quartermaster"] = dict(name=f"Quartermaster of {town}", desc="the quartermaster", look=(131, 95, 95, 95, 95, 0),
                                          greet="Supplies, |PLAYERNAME|? Ask for a {trade}.", voices=[],
                                          shop=[("health potion", 266, 50, None), ("mana potion", 268, 56, None),
                                                ("strong health potion", 236, 115, None), ("strong mana potion", 237, 108, None),
                                                ("great health potion", 239, 225, None), ("great mana potion", 238, 144, None),
                                                ("arrow", 3447, 3, None), ("bolt", 3446, 4, None), ("spear", 3277, 10, 3)])
    out[f"floor{n}_merchant"] = dict(name=f"Merchant of {town}", desc="the merchant", look=(136, 78, 86, 107, 115, 0),
                                     greet="Hello, |PLAYERNAME|! Ask for a {trade}.", voices=[],
                                     shop=[("rope", 3003, 50, 15), ("shovel", 3457, 50, 8), ("backpack", 2854, 20, None),
                                           ("fishing rod", 3483, 150, 40), ("worm", 3492, 1, None), ("ham", 3582, 8, None)])
    shop = []
    town_buy = {}
    for d in gen_npcs.NPCS.values():
        for _nm, cid, buy, _sell in d.get("shop", []):
            if buy:
                town_buy[cid] = min(town_buy.get(cid, buy), buy)
    for g in gear:
        price = 2000 * n * n // 10
        if g in town_buy:
            price = min(price, max(1, town_buy[g] // 3))  # never more than Hearthgate sells it for
        shop.append((gear_names.get(g, "item"), g, None, price))  # buys only: floor gear is earned by hunting
    out[f"floor{n}_outfitter"] = dict(name=f"Outfitter of {town}", desc="the outfitter", look=(139, 113, 38, 76, 96, 0),
                                      greet="I buy the gear you find on this floor, |PLAYERNAME|. Ask for a {trade}.", voices=[],
                                      shop=shop)
    return out


def quest_rows(n, f):
    town = f["town"]
    elder, scout = f"Elder of {town}", f"Scout of {town}"
    base = 50000 + n * 100
    q = []
    q.append(dict(id=f"q{n}_1", floor=n, name=f"{town}: Thinning the Herd", giver=elder, storage=base + 1, killStorage=base + 11,
                  target=f["camp"][0], count=30, gold=1500 * n,
                  offer=f"The {f['camp'][0].lower()}s are everywhere. Thin them out: 30 of them. Will you?",
                  step=f"Hunt {f['camp'][0]}s on Floor {n}: %d of %d.", report=f"Return to {elder} in {town} and say 'report'.",
                  thanks="Well done. The roads are safer already."))
    q.append(dict(id=f"q{n}_2", floor=n, name=f"{town}: Clearing the Road", giver=elder, storage=base + 2, killStorage=base + 12,
                  target=f["camp"][2], count=30, gold=2000 * n, requires=f"q{n}_1",
                  offer=f"Now the {f['camp'][2].lower()}s. 30 more, and the traders can come back. Yes?",
                  step=f"Hunt {f['camp'][2]}s on Floor {n}: %d of %d.", report=f"Return to {elder} in {town} and say 'report'.",
                  thanks="The traders will sing about you."))
    q.append(dict(id=f"q{n}_3", floor=n, name=f"{town}: The Elite", giver=scout, storage=base + 3, killStorage=base + 13,
                  target=f["elite"], count=3, gold=3500 * n,
                  offer=f"Scouts report {f['elite'].lower()}s leading the packs. Bring down three. Can you?",
                  step=f"Defeat {f['elite']}s on Floor {n}: %d of %d.", report=f"Return to {scout} at {town}'s north gate and say 'report'.",
                  thanks="Three leaders down. The packs scatter."))
    return q


def main():
    lua = ["-- Generated by tools/gen_floor_content.py from maps/floors.py. Do not edit by hand.",
           "-- Floors 2-10: story quests, secrets, fish, perks, floor areas and house towns."]
    olds = old_secrets()
    catalog_modules = ["q1_1", "q1_2", "q1_3"]
    for f_old in CATALOG.glob("q*.lua"):
        if not f_old.name.startswith("q1_"):
            f_old.unlink()
    for n, f in FLOORS.items():
        x0, y0 = origin(n)
        lua.append(f"table.insert(Floors.areas, {{ floor = {n}, x1 = {x0}, y1 = {y0}, x2 = {x0 + SIZE - 1}, y2 = {y0 + SIZE - 1} }})")
        lua.append(f"SpireHouses.floorTown[{n}] = {n + 1}")
        # quests
        for q in quest_rows(n, f):
            fields = [f"id = {lua_str(q['id'])}", f"floor = {n}", f"name = {lua_str(q['name'])}", f"giver = {lua_str(q['giver'])}",
                      f"storage = {q['storage']}", f"killStorage = {q['killStorage']}", f"target = {lua_str(q['target'])}",
                      f"count = {q['count']}", f"reward = {{ gold = {q['gold']} }}", f"offer = {lua_str(q['offer'])}",
                      f"step = {lua_str(q['step'])}", f"report = {lua_str(q['report'])}", f"thanks = {lua_str(q['thanks'])}"]
            if q.get("requires"):
                fields.append(f"requires = {lua_str(q['requires'])}")
            lua.append("table.insert(SpireQuests.list, { " + ", ".join(fields) + " })")
            catalog_modules.append(q["id"])
            (CATALOG / f"{q['id']}.lua").write_text(
                f'-- Generated by tools/gen_floor_content.py\nlocal q = SpireQuests.get("{q["id"]}")\nif not q then\n\treturn {{ name = "{q["id"]}", missions = {{}} }}\nend\n'
                'return {\n\tname = q.name,\n\tstartStorageId = q.storage,\n\tstartStorageValue = 1,\n\tmissions = {\n\t\t[1] = {\n'
                f'\t\t\tname = q.name,\n\t\t\tstorageId = q.storage,\n\t\t\tmissionId = {n * 10 + int(q["id"][-1])},\n'
                '\t\t\tstartValue = 1,\n\t\t\tendValue = 3,\n\t\t\tdescription = function(player)\n'
                '\t\t\t\treturn SpireQuests.logText(q, SpireQuests.state(player, q), SpireQuests.progress(player, q))\n'
                '\t\t\tend,\n\t\t},\n\t},\n}\n')
        # perks
        perks = PERKS[n]
        lua.append(f"SpireQuests.PERKS[{n}] = {{ " + ", ".join(
            f"{{ key = {lua_str(k)}, name = {lua_str(nm)}, text = {lua_str(t)} }}" for k, nm, t in perks) + " }")
        # secrets
        names = olds.get(n, [])
        for k in range(12):
            if k < len(names):
                nm, tier, trig = names[k]
                hint = trig[0].upper() + trig[1:] + "."
            else:
                nm, tier = f"{f['town']} {SECRET_WORDS[k]}", TIERS[k]
                hint = f"Somewhere on Floor {n}, off the beaten path."
            reward_gold = {"small": 300, "medium": 900, "large": 2000}[tier] * n
            lua.append(f"table.insert(SpireSecrets.list, {{ id = \"f{n}s{k + 1}\", floor = {n}, tier = {lua_str(tier)}, name = {lua_str(nm)}, "
                       f"hint = {lua_str(hint)}, point = \"f{n}_secret_{k + 1}\", reward = {{ gold = {reward_gold} }} }})")
        # fish
        fish = f["fish"]
        weights = [45, 25, 12, 8, 5, 4, 0.3]
        rows = []
        items = [3578, 7159, 3579, 3581, 7158, 3580, 3580]
        for i, nm in enumerate(fish):
            extra = ", night = true" if i == 5 else (", legendary = true" if i == 6 else "")
            kg = (0.2 * n, 1.0 * n) if i < 6 else (8 * n, 12 * n)
            rows.append(f"{{ id = \"f{n}_fish{i + 1}\", name = {lua_str(nm)}, item = {items[i]}, weight = {weights[i]}, kg = {{ {kg[0]:.1f}, {kg[1]:.1f} }}{extra} }}")
        rows.append(f"{{ id = \"f{n}_purse\", name = \"a sunken purse\", item = 3035, count = {3 + n}, weight = 2, treasure = true }}")
        rows.append("{ id = \"junk\", name = \"old boots\", item = 3123, weight = 8, junk = true }")
        lua.append(f"SpireFishing.tables[{n}] = {{ " + ", ".join(rows) + " }")
        # NPCs
        for key, d in npc_defs(n, f).items():
            (NPC_DIR / f"{key}.lua").write_text(gen_npcs.render(d))
        for role, nm in (("elder", f"Elder of {f['town']}"), ("scout", f"Scout of {f['town']}")):
            (NPC_DIR / f"floor{n}_{role}.lua").write_text(QUEST_NPC.replace("@NAME@", nm).replace("@TOWN@", f["town"]))
    (DP / "lib" / "spirebound" / "floor_content.lua").write_text("\n".join(lua) + "\n")
    (CATALOG / "init.lua").write_text("local questModules = {\n" + "".join(f'\t"{m}",\n' for m in catalog_modules) +
                                      "}\n\nlocal catalog = dofile(CORE_DIRECTORY .. \"/lib/core/quests/catalog.lua\")\n\n"
                                      "return catalog.build(DATA_DIRECTORY .. \".lib.core.quests.catalog\", questModules)\n")
    print(f"floors {min(FLOORS)}-{max(FLOORS)}: {len(catalog_modules) - 3} quests, {12 * len(FLOORS)} secrets, NPCs written")


QUEST_NPC = '''-- Generated by tools/gen_floor_content.py: story quest giver.
local npcName = "@NAME@"
local npcType = Game.createNpcType(npcName)
local npcConfig = {}
npcConfig.name = npcName
npcConfig.description = "a resident of @TOWN@"
npcConfig.health = 100
npcConfig.maxHealth = npcConfig.health
npcConfig.walkInterval = 0
npcConfig.walkRadius = 0
npcConfig.outfit = { lookType = 133, lookHead = 78, lookBody = 88, lookLegs = 96, lookFeet = 115, lookAddons = 0 }
npcConfig.flags = { floorchange = false }
local keywordHandler = KeywordHandler:new()
local npcHandler = NpcHandler:new(keywordHandler)
npcType.onThink = function(npc, interval) npcHandler:onThink(npc, interval) end
npcType.onAppear = function(npc, creature) npcHandler:onAppear(npc, creature) end
npcType.onDisappear = function(npc, creature) npcHandler:onDisappear(npc, creature) end
npcType.onMove = function(npc, creature, from, to) npcHandler:onMove(npc, creature, from, to) end
npcType.onSay = function(npc, creature, type, message) npcHandler:onSay(npc, creature, type, message) end
npcType.onCloseChannel = function(npc, player) npcHandler:onCloseChannel(npc, player) end
local function creatureSayCallback(npc, player, type, msg)
	if not npcHandler:checkInteraction(npc, player) then
		return false
	end
	SpireQuests.talk(npc, npcHandler, player, msg, npcName)
	return true
end
npcHandler:setMessage(MESSAGE_GREET, "Welcome to @TOWN@, |PLAYERNAME|. Looking for a {quest}? Or here to {report}?")
npcHandler:setMessage(MESSAGE_FAREWELL, "Climb well.")
npcHandler:setCallback(CALLBACK_MESSAGE_DEFAULT, creatureSayCallback)
npcHandler:addModule(FocusModule:new(), npcConfig.name, true, true, true)
npcType:register(npcConfig)
'''

if __name__ == "__main__":
    main()
