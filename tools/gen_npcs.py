#!/usr/bin/env python3
"""Writes Spirebound NPC files (Canary Lua) from the table below (roadmap 1.15).
Never hand-edit the generated server/data-spirebound/npc/hearthgate_*.lua; change the table and rerun.
The Registrar (npc/registrar.lua) is hand-written because its dialogue is a small state machine.

Prices: ammunition and potions are the everyday gold sink (DESIGN.md 5.3b: no conjured ammo).
Usage: python3 tools/gen_npcs.py
"""
from __future__ import annotations

from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from junk_prices import JUNK  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "server" / "data-spirebound" / "npc"

# shop rows: (item name shown in trade, client id, buy price or None, sell price or None)
NPCS = {
    "hearthgate_priest": dict(
        name="Priest Odran", desc="the priest of Hearthgate", look=(57, 0, 0, 0, 0, 0),
        greet="Peace, |PLAYERNAME|. I can {heal} you, and my prayers, the {blessings}, soften the tower's price for death.",
        kind="priest", voices=["The tower takes, the temple gives back.", "Wounded? Come, sit."]),
    "hearthgate_banker": dict(
        name="Banker Tolliver", desc="the banker of Hearthgate", look=(132, 115, 76, 35, 116, 0),
        greet="Welcome to the bank, |PLAYERNAME|. Ask about your {balance}, or {deposit} and {withdraw} gold. Your account {vault} is shared by all your characters. Guild members can use the {guild balance} too.",
        kind="bank", voices=["Coins are safer here than in your pockets."]),
    "hearthgate_merchant": dict(
        name="Merchant Wenna", desc="the general merchant", look=(136, 78, 86, 107, 115, 0),
        greet="Hello, |PLAYERNAME|! Rope, shovels, food, fishing gear: ask for a {trade}. Lost? Ask me where to {hunt}.",
        voices=["Ropes! Shovels! Fresh bread!"],
        shop=[("rope", 3003, 50, 15), ("shovel", 3457, 50, 8), ("torch", 2920, 2, None), ("bag", 2853, 4, None),
              ("backpack", 2854, 20, None), ("fishing rod", 3483, 150, 40), ("worm", 3492, 1, None),
              ("bread", 3600, 4, None), ("ham", 3582, 8, None), ("meat", 3577, 5, None)]),
    "hearthgate_quartermaster": dict(
        name="Quartermaster Bryn", desc="the quartermaster", look=(131, 95, 95, 95, 95, 0),
        greet="Supplies, |PLAYERNAME|? Potions and ammunition. Nobody conjures arrows in this tower. Ask for a {trade}.",
        voices=["Potions and arrows! Don't climb without them!"],
        shop=[("health potion", 266, 50, None), ("mana potion", 268, 56, None),
              ("strong health potion", 236, 115, None), ("strong mana potion", 237, 108, None),
              ("arrow", 3447, 3, None), ("bolt", 3446, 4, None), ("spear", 3277, 10, 3)]),
    "hearthgate_weaponsmith": dict(
        name="Weaponsmith Garrick", desc="the weaponsmith", look=(131, 76, 76, 38, 76, 0),
        greet="Steel for the climb, |PLAYERNAME|. Swords, axes, clubs, bows, wands and rods: ask for a {trade}.",
        voices=["Sharp steel! Fair prices!"],
        shop=[("sword", 3264, 85, 25), ("longsword", 3285, 160, 51), ("sabre", 3273, 35, 12), ("spike sword", 3271, 8000, 240),
              ("hand axe", 3268, 8, 4), ("axe", 3274, 20, 7),
              ("club", 3270, 5, 1), ("mace", 3286, 90, 30),
              ("bow", 3350, 400, 100), ("crossbow", 3349, 500, 120), ("spear", 3277, 10, 3),
              ("wand of vortex", 3074, 500, 100), ("snakebite rod", 3066, 500, 100)]),
    "hearthgate_junk_trader": dict(
        name="Trader Osric", desc="the trader of the Hearth", look=(129, 95, 116, 121, 115, 0),
        greet="Back from the field, |PLAYERNAME|? I buy nearly everything monsters drop: gear, hides, gems, odds and ends. Ask for a {trade} and sell me your loot.",
        voices=["I buy loot! Bring me everything!", "Gear, hides, gems: I pay in gold!"],
        shop=[(n, i, None, v) for n, i, v in JUNK]),
    "hearthgate_banker_branch": dict(
        name="Banker Ansel", desc="the banker of the north wall", look=(132, 115, 76, 35, 116, 0),
        greet="The north-wall branch of the bank, |PLAYERNAME|. Your {balance}, {deposit}, {withdraw} and your account {vault}, all here too.",
        kind="bank", voices=["Banking, near the shops."]),
    "hearthgate_fletcher": dict(
        name="Fletcher Tamsin", desc="the fletcher", look=(137, 59, 63, 58, 114, 0),
        greet="Arrows, bolts and spears, |PLAYERNAME|. Bring materials and I'll {craft} better ones. Nobody conjures them in this tower, so I never run out of customers. Ask for a {trade}.",
        voices=["Fresh-cut arrows!", "Bolts, a hundred at a time!"],
        shop=[("arrow", 3447, 3, None), ("bolt", 3446, 4, None), ("spear", 3277, 9, 3), ("bow", 3350, 400, 100), ("crossbow", 3349, 500, 120), ("quiver", 35562, 150, None)]),
    "hearthgate_alchemist": dict(
        name="Alchemist Ivo", desc="the alchemist", look=(130, 0, 87, 87, 95, 0),
        greet="Potions, |PLAYERNAME|. Bring back your empty flasks and I'll pay for them, or bring materials and I'll {craft} strong potions cheaply. Ask for a {trade}.",
        voices=["Health and mana, bottled!", "I buy empty flasks!"],
        shop=[("health potion", 266, 45, None), ("mana potion", 268, 50, None), ("strong health potion", 236, 100, None),
              ("strong mana potion", 237, 93, None), ("great health potion", 239, 190, None), ("great mana potion", 238, 144, None),
              ("empty potion flask", 283, None, 5), ("empty potion flask", 284, None, 5), ("empty potion flask", 285, None, 5)]),
    "hearthgate_runewright": dict(
        name="Runewright Mael", desc="the runewright", look=(130, 76, 94, 94, 114, 0),
        greet="Blank runes for your conjuring, |PLAYERNAME|, made cheaper if you bring gems to {craft} with, and wands and rods for those who need one. Ask for a {trade}.",
        voices=["Blank runes! Ready for your spells!"],
        shop=[("blank rune", 3147, 10, None), ("wand of vortex", 3074, 500, 100), ("snakebite rod", 3066, 500, 100),
              ("temple teleport scroll", 25718, 300, None)]),
    "hearthgate_tailor": dict(
        name="Tailor Quill", desc="the tailor", look=(128, 95, 113, 114, 76, 0),
        greet="Good cloth for the climb, |PLAYERNAME|, and strong bags to carry your loot home. Bring furs and cloth and I'll {craft} you a hunter's outfit. Ask for a {trade}.",
        voices=["Bags! Backpacks! Sturdy and cheap!"],
        shop=[("bag", 2853, 4, None), ("backpack", 2854, 20, None), ("jacket", 3561, 12, 1), ("coat", 3562, 30, 3),
              ("leather legs", 3559, 15, 3)]),
    "hearthgate_postmaster": dict(
        name="Postmaster Hobb", desc="the postmaster", look=(128, 76, 94, 94, 114, 0),
        greet="Letters and parcels, |PLAYERNAME|. Write the name on a label, put it in the parcel and drop it in a mailbox. Ask for a {trade}.",
        voices=["Parcels go anywhere in the tower!"],
        shop=[("parcel", 3503, 15, None), ("label", 3507, 1, None), ("letter", 3505, 8, None)]),
    "hearthgate_broker": dict(
        name="Broker Nell", desc="the market broker", look=(136, 95, 113, 114, 76, 0),
        greet="The market, |PLAYERNAME|: open it from any depot locker. Post what you want to sell or buy, and other climbers will deal with you even when you're away.",
        voices=["Buy low, sell to a climber in a hurry."]),
    "hearthgate_innkeeper": dict(
        name="Innkeeper Roan", desc="the innkeeper of Hearthgate", look=(128, 78, 96, 59, 115, 0),
        greet="Welcome to the Lantern & Lark, |PLAYERNAME|. Food and drink, or ask me where to {hunt}. Ask for a {trade}.",
        voices=["Hot food! Cold ale!"],
        shop=[("bread", 3600, 4, None), ("ham", 3582, 8, None), ("meat", 3577, 5, None), ("cheese", 3607, 6, None), ("fish", 3578, 6, None)]),
    "hearthgate_coachman": dict(
        name="Coachman Ferro", desc="the coachman", look=(128, 58, 68, 109, 115, 0),
        greet="Need a ride, |PLAYERNAME|? I drive to {Millcross} and back to {Hearthgate}.",
        kind="travel", voices=["Carriage leaving soon!"]),
    "millcross_coachman": dict(
        name="Coachwoman Dara", desc="the Millcross coachwoman", look=(136, 58, 68, 109, 115, 0),
        greet="Back to the city, |PLAYERNAME|? I drive to {Hearthgate}.",
        kind="travel", voices=["Carriage to Hearthgate!"]),
    "millcross_innkeeper": dict(
        name="Innkeeper Bess", desc="the innkeeper of Millcross", look=(137, 78, 96, 59, 115, 0),
        greet="Welcome to the Millcross Inn, |PLAYERNAME|. Hot food, cold ale and good advice. Ask for a {trade}, or ask me where to {hunt}.",
        voices=["Stew's hot!", "Climbers eat free if they bring the boars home. Well, nearly free."],
        shop=[("bread", 3600, 4, None), ("ham", 3582, 8, None), ("meat", 3577, 5, None), ("cheese", 3607, 6, None)]),
    "hearthgate_housewright": dict(
        name="Housewright Orla", desc="the housewright", look=(128, 58, 68, 109, 115, 0),
        greet="A house should do things, |PLAYERNAME|. Furniture kits, tapestries and an exercise dummy for your own training room: ask for a {trade}. Kits are built by using them on your house floor.",
        voices=["Furniture kits! Make your house a home!"],
        shop=[("exercise dummy kit", 23398, 250000, None),
              ("sofa chair kit", 2779, 1200, None), ("wooden chair kit", 2777, 400, None), ("square table kit", 2784, 800, None),
              ("small table kit", 2782, 600, None), ("dresser kit", 2790, 1500, None), ("locker kit", 2791, 1500, None),
              ("table lamp kit", 2798, 900, None), ("indoor plant kit", 2811, 700, None), ("barrel kit", 2793, 500, None),
              ("red tapestry", 2656, 1000, None), ("blue tapestry", 2659, 1000, None), ("green tapestry", 2647, 1000, None)]),
    "hearthgate_armorer": dict(
        name="Armorer Hesta", desc="the armorer", look=(139, 113, 38, 76, 96, 0),
        greet="Armor keeps climbers breathing, |PLAYERNAME|. Ask for a {trade}.",
        voices=["Leather, chain, brass! Get armored!"],
        shop=[("leather helmet", 3355, 12, 4), ("leather armor", 3361, 12, 5), ("leather legs", 3559, 10, 1), ("leather boots", 3552, 2, 1),
              ("studded helmet", 3376, 63, 20), ("studded armor", 3378, 90, 25), ("studded legs", 3362, 50, 15),
              ("chain helmet", 3352, 52, 17), ("brass armor", 3359, 450, 150), ("brass legs", 3372, 195, 49),
              ("wooden shield", 3412, 15, 5), ("studded shield", 3426, 50, 16), ("brass shield", 3411, 65, 25)]),
}

MURDERER = '''
-- Murderers (red/black) get no service in town (DESIGN.md 6.4)
local function refuseMurderers(npc, player)
	if SpirePvP and SpirePvP.isMurderer(player) then
		npcHandler:say("I don't deal with murderers. Get out.", npc, player)
		return false
	end
	return true
end
'''

TRAVEL = '''
-- carriage routes: keyword, map point (tools/mapgen.py world_points), fare in gold
local ROUTES = { { "millcross", "carriage_millcross", 20 }, { "hearthgate", "carriage_hearthgate", 20 } }

local function creatureSayCallback(npc, player, type, msg)
	if not npcHandler:checkInteraction(npc, player) then
		return false
	end
	local pid = player:getId()
	for i, r in ipairs(ROUTES) do
		if MsgContains(msg, r[1]) and WorldPoints and WorldPoints[r[2]] then
			npcHandler:say("To " .. r[1] .. " for " .. r[3] .. " gold? Climb in and say {yes}.", npc, player)
			npcHandler:setTopic(pid, i)
			return true
		end
	end
	if MsgContains(msg, "yes") and npcHandler:getTopic(pid) > 0 then
		local r = ROUTES[npcHandler:getTopic(pid)]
		npcHandler:setTopic(pid, 0)
		if player:isPzLocked() then
			npcHandler:say("Not with blood still on your hands. Calm down first.", npc, player)
		elseif not player:removeMoneyBank(r[3]) then
			npcHandler:say("You can't pay the fare.", npc, player)
		else
			npcHandler:say("Hold on to your hat!", npc, player)
			player:teleportTo(WorldPoints[r[2]])
			WorldPoints[r[2]]:sendMagicEffect(CONST_ME_TELEPORT)
		end
		return true
	end
	if MsgContains(msg, "route") or MsgContains(msg, "travel") or MsgContains(msg, "where") then
		npcHandler:say("I drive between {Millcross} and {Hearthgate}. The fare is 20 gold.", npc, player)
	end
	return true
end
'''

PRIEST = '''
local HEAL_LEVEL = 50 -- free healing below this level (catch-up for new climbers)

local function creatureSayCallback(npc, player, type, msg)
	if not npcHandler:checkInteraction(npc, player) then
		return false
	end
	local pid = player:getId()
	if MsgContains(msg, "heal") then
		if player:getLevel() < HEAL_LEVEL or player:getHealth() < player:getMaxHealth() * 0.4 then
			player:addHealth(player:getMaxHealth() - player:getHealth())
			player:removeCondition(CONDITION_POISON)
			player:removeCondition(CONDITION_FIRE)
			player:removeCondition(CONDITION_ENERGY)
			player:removeCondition(CONDITION_BLEEDING)
			player:getPosition():sendMagicEffect(CONST_ME_MAGIC_BLUE)
			npcHandler:say("Be whole again.", npc, player)
		else
			npcHandler:say("You are not hurt badly enough to need my help.", npc, player)
		end
	elseif MsgContains(msg, "bless") then
		npcHandler:say("For " .. Blessings.getBlessingCost(player:getLevel(), false) * 5 .. " gold I will pray all five protections over you. They soften the experience you lose when you die. Do you want them?", npc, player)
		npcHandler:setTopic(pid, 1)
	elseif MsgContains(msg, "yes") and npcHandler:getTopic(pid) == 1 then
		local cost = Blessings.getBlessingCost(player:getLevel(), false) * 5
		local missing = false
		for i = 2, 6 do
			if not player:hasBlessing(i) then
				missing = true
			end
		end
		if not missing then
			npcHandler:say("You already carry every prayer I know.", npc, player)
		elseif player:removeMoneyBank(cost) then
			for i = 2, 6 do
				if not player:hasBlessing(i) then
					player:addBlessing(i, 1)
				end
			end
			player:getPosition():sendMagicEffect(CONST_ME_HOLYAREA)
			npcHandler:say("It is done. Walk carefully all the same.", npc, player)
		else
			npcHandler:say("You don't have enough gold, in your backpack or the bank.", npc, player)
		end
		npcHandler:setTopic(pid, 0)
	end
	return true
end
'''

BANK = '''
local function creatureSayCallback(npc, player, type, msg)
	if not npcHandler:checkInteraction(npc, player) then
		return false
	end
	if SpireVault and SpireVault.talk(npc, npcHandler, player, msg) then
		return true
	end
	npc:parseBank(msg, npc, player, npcHandler)
	npc:parseGuildBank(msg, npc, player, player:getId(), npcHandler)
	npc:parseBankMessages(msg, npc, player, npcHandler)
	return true
end
'''

TEMPLATE = '''-- Generated by tools/gen_npcs.py: edit the table there, not this file.
local npcName = "{name}"
local npcType = Game.createNpcType(npcName)
local npcConfig = {{}}
npcConfig.name = npcName
npcConfig.description = "{desc}"
npcConfig.health = 100
npcConfig.maxHealth = npcConfig.health
npcConfig.walkInterval = 2000
npcConfig.walkRadius = 2
npcConfig.outfit = {{ lookType = {l0}, lookHead = {l1}, lookBody = {l2}, lookLegs = {l3}, lookFeet = {l4}, lookAddons = {l5} }}
npcConfig.flags = {{ floorchange = false }}
npcConfig.voices = {{
	interval = 15000,
	chance = 30,
{voices}}}
{shop}
local keywordHandler = KeywordHandler:new()
local npcHandler = NpcHandler:new(keywordHandler)
npcType.onThink = function(npc, interval) npcHandler:onThink(npc, interval) end
npcType.onAppear = function(npc, creature) npcHandler:onAppear(npc, creature) end
npcType.onDisappear = function(npc, creature) npcHandler:onDisappear(npc, creature) end
npcType.onMove = function(npc, creature, from, to) npcHandler:onMove(npc, creature, from, to) end
npcType.onSay = function(npc, creature, type, message) npcHandler:onSay(npc, creature, type, message) end
npcType.onCloseChannel = function(npc, player) npcHandler:onCloseChannel(npc, player) end
npcType.onBuyItem = function(npc, player, itemId, subType, amount, ignore, inBackpacks, totalCost)
	npc:sellItem(player, itemId, amount, subType, 0, ignore, inBackpacks)
end
npcType.onSellItem = function(npc, player, itemId, subtype, amount, ignore, name, totalCost)
	player:sendTextMessage(MESSAGE_TRADE, string.format("Sold %ix %s for %i gold.", amount, name, totalCost))
end
npcType.onCheckItem = function(npc, player, clientId, subType) end
{logic}
npcHandler:setMessage(MESSAGE_GREET, "{greet}")
npcHandler:setMessage(MESSAGE_FAREWELL, "Good climbing, |PLAYERNAME|.")
npcHandler:setMessage(MESSAGE_WALKAWAY, "Good climbing.")
{callbacks}npcHandler:addModule(FocusModule:new(), npcConfig.name, true, true, true)
npcType:register(npcConfig)
'''


def render(d):
    look = list(d["look"]) + [0] * (6 - len(d["look"]))
    voices = "".join(f'\t{{ text = "{v}" }},\n' for v in d.get("voices", []))
    shop = ""
    if d.get("shop"):
        rows = []
        for name, cid, buy, sell in d["shop"]:
            parts = [f'itemName = "{name}"', f"clientId = {cid}"]
            if buy:
                parts.append(f"buy = {buy}")
            if sell:
                parts.append(f"sell = {sell}")
            rows.append("\t{ " + ", ".join(parts) + " },")
        shop = "npcConfig.shop = {\n" + "\n".join(rows) + "\n}\n"
    logic, callbacks = MURDERER, ""
    if d.get("kind") == "priest":
        logic = MURDERER + PRIEST
        callbacks = "npcHandler:setCallback(CALLBACK_GREET, refuseMurderers)\nnpcHandler:setCallback(CALLBACK_MESSAGE_DEFAULT, creatureSayCallback)\n"
    elif d.get("kind") == "travel":
        logic = MURDERER + TRAVEL
        callbacks = "npcHandler:setCallback(CALLBACK_GREET, refuseMurderers)\nnpcHandler:setCallback(CALLBACK_MESSAGE_DEFAULT, creatureSayCallback)\n"
    elif d.get("kind") == "bank":
        logic = MURDERER + BANK
        callbacks = ("npcHandler:setCallback(CALLBACK_GREET, function(npc, player) return refuseMurderers(npc, player) and NpcBankGreetCallback(npc, player) end)\n"
                     "npcHandler:setCallback(CALLBACK_MESSAGE_DEFAULT, creatureSayCallback)\n")
    elif d.get("shop"):
        callbacks = ("npcHandler:setCallback(CALLBACK_GREET, refuseMurderers)\n"
                     "npcHandler:setCallback(CALLBACK_MESSAGE_DEFAULT, function(npc, player, type, msg)\n"
                     "\tif SpireCraft and SpireCraft.talk(npc, npcHandler, player, msg, npcConfig.name) then\n"
                     "\t\treturn false\n"
                     "\tend\n"
                     "\tif SpireHunt and MsgContains(msg, \"hunt\") then\n"
                     "\t\tnpcHandler:say(SpireHunt.advice(player:getLevel()), npc, player)\n"
                     "\t\treturn false\n"
                     "\tend\n"
                     "\treturn true\n"
                     "end)\n")
        logic = MURDERER + '\nkeywordHandler:addKeyword({ "job" }, StdModule.say, { npcHandler = npcHandler, text = "' + d["desc"].capitalize() + '. Ask me for a {trade}." })\n'
    return TEMPLATE.format(name=d["name"], desc=d["desc"], l0=look[0], l1=look[1], l2=look[2], l3=look[3], l4=look[4], l5=look[5],
                           voices=voices, shop=shop, logic=logic, greet=d["greet"], callbacks=callbacks)


def check_prices():
    """No buy-low/sell-high loops between NPCs: every sell price must be below every buy price for that item."""
    buys, sells = {}, {}
    for d in NPCS.values():
        for name, cid, buy, sell in d.get("shop", []):
            if buy:
                buys[cid] = min(buys.get(cid, buy), buy)
            if sell:
                sells[cid] = max(sells.get(cid, sell), sell)
    bad = [f"item {cid}: sells for {sells[cid]} but can be bought for {buys[cid]}" for cid in sells if cid in buys and sells[cid] >= buys[cid]]
    if bad:
        raise SystemExit("price loop:\n" + "\n".join(bad))


def main():
    check_prices()
    # only rewrite this generator's own files (hand-written NPCs live next to them)
    for key, d in NPCS.items():
        (OUT / f"{key}.lua").write_text(render(d))
    print(f"wrote {len(NPCS)} NPCs")


if __name__ == "__main__":
    main()
