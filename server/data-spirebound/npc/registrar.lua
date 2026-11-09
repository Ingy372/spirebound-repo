-- The Registrar: end of the Arrival Yard. New characters pick a vocation and a difficulty here
-- (DESIGN.md 5.1, 5.4). Later the Registrar also lets characters step DOWN a difficulty.
local npcName = "Registrar Maelis"

local npcType = Game.createNpcType(npcName)
local npcConfig = {}
npcConfig.name = npcName
npcConfig.description = "the Registrar of Hearthgate"
npcConfig.health = 100
npcConfig.maxHealth = npcConfig.health
npcConfig.walkInterval = 0
npcConfig.walkRadius = 0
npcConfig.outfit = { lookType = 141, lookHead = 41, lookBody = 72, lookLegs = 39, lookFeet = 76, lookAddons = 0 }
npcConfig.flags = { floorchange = false }

local keywordHandler = KeywordHandler:new()
local npcHandler = NpcHandler:new(keywordHandler)

npcType.onThink = function(npc, interval) npcHandler:onThink(npc, interval) end
npcType.onAppear = function(npc, creature) npcHandler:onAppear(npc, creature) end
npcType.onDisappear = function(npc, creature) npcHandler:onDisappear(npc, creature) end
npcType.onMove = function(npc, creature, from, to) npcHandler:onMove(npc, creature, from, to) end
npcType.onSay = function(npc, creature, type, message) npcHandler:onSay(npc, creature, type, message) end
npcType.onCloseChannel = function(npc, player) npcHandler:onCloseChannel(npc, player) end

-- Vocation ids follow server/core-overrides/XML/vocations.xml
local VOCATIONS = {
	vanguard = { id = 4, text = "Vanguards hold the front line with sword, axe or club and a shield." },
	ranger = { id = 3, text = "Rangers strike from afar with bow, crossbow or spear." },
	arcanist = { id = 1, text = "Arcanists wield wands and fill the field with fire and lightning." },
	mystic = { id = 2, text = "Mystics wield rods, heal their allies and command nature." },
}

-- Starter kits (client item ids, Tibia 15.11)
local KITS = {
	[4] = { { 3264, 1 }, { 3412, 1 } }, -- sword, wooden shield
	[3] = { { 3350, 1 }, { 3447, 100 }, { 3277, 2 } }, -- bow, arrows, spears
	[1] = { { 3074, 1 } }, -- wand of vortex
	[2] = { { 3066, 1 } }, -- snakebite rod
}
local COMMON_KIT = { { 3361, 1 }, { 3355, 1 }, { 3559, 1 }, { 3552, 1 }, { 3582, 5 }, { 266, 5 }, { 268, 5 }, { 3003, 1 }, { 3457, 1 } }
-- leather armor, leather helmet, leather legs, leather boots, ham, health/mana potions, rope, shovel

local MODES = {
	["normal"] = { id = Difficulty.NORMAL, text = "Normal: the tower's usual rules. Death costs experience, as it always has." },
	["hardcore"] = { id = Difficulty.HARDCORE, text = "Hardcore: deaths cost half again as much, but you earn 25% more experience and 15% more loot." },
	["death game"] = { id = Difficulty.DEATHGAME, text = "Death Game: if a monster or the tower kills you, this character is gone for good. In return: 50% more experience, 30% more loot, and honours no one else can earn. Another player can never end you this way." },
}

local chosen = {} -- playerId -> { voc = id, mode = id }

local function giveKit(player, vocId)
	for _, list in ipairs({ KITS[vocId] or {}, COMMON_KIT }) do
		for _, entry in ipairs(list) do
			player:addItem(entry[1], entry[2])
		end
	end
end

local function greetCallback(npc, player)
	if Difficulty.get(player) == Difficulty.NONE then
		npcHandler:setMessage(MESSAGE_GREET, "Welcome to Hearthgate, |PLAYERNAME|. Before you climb, choose your path: {vanguard}, {ranger}, {arcanist} or {mystic}?")
	else
		npcHandler:setMessage(MESSAGE_GREET, "Back again, |PLAYERNAME|? If the tower weighs too heavy, I can let you {step down} to an easier way of living.")
	end
	return true
end

local function creatureSayCallback(npc, player, type, msg)
	local pid = player:getId()
	if not npcHandler:checkInteraction(npc, player) then
		return false
	end
	local topic = npcHandler:getTopic(pid)
	local lower = msg:lower()

	if Difficulty.get(player) == Difficulty.NONE then
		for key, voc in pairs(VOCATIONS) do
			if MsgContains(lower, key) and topic <= 1 then
				chosen[pid] = { voc = voc.id }
				npcHandler:say(voc.text .. " Will you walk the path of the " .. key .. "? {yes} or {no}?", npc, player)
				npcHandler:setTopic(pid, 1)
				return true
			end
		end
		if topic == 1 and MsgContains(lower, "yes") then
			npcHandler:say("Good. Now choose how you will live in the tower: {normal}, {hardcore} or {death game}? You may always step down later, but never up.", npc, player)
			npcHandler:setTopic(pid, 2)
			return true
		end
		if topic == 2 or topic == 3 then
			for key, mode in pairs(MODES) do
				if MsgContains(lower, key) and not (key == "normal" and MsgContains(lower, "death")) then
					chosen[pid].mode = mode.id
					npcHandler:say(mode.text .. " Is that your choice? {yes} or {no}?", npc, player)
					npcHandler:setTopic(pid, 3)
					return true
				end
			end
		end
		if topic == 3 and MsgContains(lower, "yes") and chosen[pid] and chosen[pid].mode then
			local c = chosen[pid]
			if not Difficulty.set(player, c.mode) then
				npcHandler:say("Something is wrong with your papers. Speak to a gamemaster.", npc, player)
				return true
			end
			player:setVocation(Vocation(c.voc))
			giveKit(player, c.voc)
			player:getPosition():sendMagicEffect(CONST_ME_HOLYAREA)
			npcHandler:say(string.format("It is written: %s, %s. The temple is through the gate. Climb well.", player:getVocation():getName(), Difficulty.names[c.mode]), npc, player)
			player:teleportTo(player:getTown():getTemplePosition())
			chosen[pid] = nil
			npcHandler:setTopic(pid, 0)
			return true
		end
		if MsgContains(lower, "no") then
			npcHandler:say("Then choose again: {vanguard}, {ranger}, {arcanist} or {mystic}?", npc, player)
			npcHandler:setTopic(pid, 0)
			return true
		end
		return true
	end

	-- Floor perks (DESIGN.md 8.3): one choice per floor, after all of that floor's story quests
	if MsgContains(lower, "perk") then
		for floor = 1, Floors.LAUNCH_FLOORS do
			local opts = SpireQuests.PERKS[floor]
			if opts and SpireQuests.floorStoryDone(player, floor) and not SpirePerks.get(player, floor) then
				npcHandler:say(string.format("Floor %d perk. Choose one: {%s} (%s) or {%s} (%s).", floor, opts[1].name, opts[1].text, opts[2].name, opts[2].text), npc, player)
				npcHandler:setTopic(pid, 100 + floor)
				return true
			end
		end
		npcHandler:say("No perk is waiting for you. Perks come from finishing every story quest on a floor.", npc, player)
		return true
	end
	if topic > 100 and topic <= 100 + Floors.LAUNCH_FLOORS then
		local floor = topic - 100
		for _, o in ipairs(SpireQuests.PERKS[floor] or {}) do
			if MsgContains(lower, o.name:lower()) then
				SpirePerks.choose(player, floor, o.key)
				npcHandler:say("It is written: " .. o.name .. ".", npc, player)
				npcHandler:setTopic(pid, 0)
				return true
			end
		end
	end

	-- Already registered: stepping down
	local current = Difficulty.get(player)
	if MsgContains(lower, "step down") then
		local options = {}
		for key, mode in pairs(MODES) do
			if Difficulty.canChange(current, mode.id) then
				table.insert(options, "{" .. key .. "}")
			end
		end
		if #options == 0 then
			npcHandler:say("You already live by the gentlest rules the tower has.", npc, player)
		else
			npcHandler:say("You may step down to " .. table.concat(options, " or ") .. ". This can never be undone.", npc, player)
			npcHandler:setTopic(pid, 10)
		end
		return true
	end
	if topic == 10 then
		for key, mode in pairs(MODES) do
			if MsgContains(lower, key) and not (key == "normal" and MsgContains(lower, "death")) and Difficulty.canChange(current, mode.id) then
				chosen[pid] = { mode = mode.id }
				npcHandler:say("Step down to " .. Difficulty.names[mode.id] .. " forever? {yes} or {no}?", npc, player)
				npcHandler:setTopic(pid, 11)
				return true
			end
		end
	end
	if topic == 11 and MsgContains(lower, "yes") and chosen[pid] then
		Difficulty.set(player, chosen[pid].mode)
		npcHandler:say("It is written. You now live by the " .. Difficulty.names[chosen[pid].mode] .. " rules.", npc, player)
		chosen[pid] = nil
		npcHandler:setTopic(pid, 0)
		return true
	end
	return true
end

npcHandler:setCallback(CALLBACK_GREET, greetCallback)
npcHandler:setCallback(CALLBACK_MESSAGE_DEFAULT, creatureSayCallback)
npcHandler:setMessage(MESSAGE_FAREWELL, "May the tower be kind to you.")
npcHandler:setMessage(MESSAGE_WALKAWAY, "Come back when you are ready to choose.")
npcHandler:addModule(FocusModule:new(), npcConfig.name, true, true, true)
npcType:register(npcConfig)
