-- Every floor's taskmaster (Jay, 2026-11-13): the same task menu everywhere, each with its own floor's monsters.
-- Saying hi (or "tasks") opens the task window in the client; the chat words still work as a fallback.
-- Names and the rules: lib/spirebound/tasks.lua. Map placement: maps/layout_floor1.py, maps/layout_floor.py.
local LOOKS = {
	{ lookType = 129, lookHead = 115, lookBody = 76, lookLegs = 76, lookFeet = 115, lookAddons = 2 },
	{ lookType = 134, lookHead = 78, lookBody = 58, lookLegs = 58, lookFeet = 95, lookAddons = 1 },
	{ lookType = 137, lookHead = 95, lookBody = 76, lookLegs = 114, lookFeet = 115, lookAddons = 1 },
}

local function openMenu(player, floor)
	SpireClient.send(player, SpireTasks.menu(player, floor))
end

for floor, npcName in pairs(SpireTasks.MASTERS) do
	local npcType = Game.createNpcType(npcName)
	local npcConfig = {}
	npcConfig.name = npcName
	npcConfig.description = "the taskmaster"
	npcConfig.health = 100
	npcConfig.maxHealth = npcConfig.health
	npcConfig.walkInterval = 0
	npcConfig.walkRadius = 0
	npcConfig.outfit = LOOKS[(floor - 1) % #LOOKS + 1]
	npcConfig.flags = { floorchange = false }

	local keywordHandler = KeywordHandler:new()
	local npcHandler = NpcHandler:new(keywordHandler)
	npcType.onThink = function(npc, interval) npcHandler:onThink(npc, interval) end
	npcType.onAppear = function(npc, creature) npcHandler:onAppear(npc, creature) end
	npcType.onDisappear = function(npc, creature) npcHandler:onDisappear(npc, creature) end
	npcType.onMove = function(npc, creature, from, to) npcHandler:onMove(npc, creature, from, to) end
	npcType.onSay = function(npc, creature, type, message) npcHandler:onSay(npc, creature, type, message) end
	npcType.onCloseChannel = function(npc, player) npcHandler:onCloseChannel(npc, player) end

	local function greet(npc, player)
		openMenu(player, floor)
		return true
	end

	local function creatureSayCallback(npc, player, type, msg)
		if not npcHandler:checkInteraction(npc, player) then
			return false
		end
		local lower = msg:lower()
		if MsgContains(lower, "tasks") or MsgContains(lower, "list") or MsgContains(lower, "menu") then
			openMenu(player, floor)
			local names = {}
			for _, t in ipairs(SpireTasks.forFloor(floor)) do
				table.insert(names, string.format("{%s}", t.monster:lower()))
			end
			npcHandler:say("Pick one from the task window, or name it: " .. table.concat(names, ", ") .. ".", npc, player)
			return true
		end
		if MsgContains(lower, "report") then
			local _, text = SpireTasks.report(player)
			npcHandler:say(text, npc, player)
			openMenu(player, floor)
			return true
		end
		if MsgContains(lower, "cancel") then
			local _, text = SpireTasks.cancel(player)
			npcHandler:say(text, npc, player)
			openMenu(player, floor)
			return true
		end
		for _, t in ipairs(SpireTasks.forFloor(floor)) do
			if MsgContains(lower, t.monster:lower()) then
				local _, text = SpireTasks.take(player, t.id)
				npcHandler:say(text, npc, player)
				openMenu(player, floor)
				return true
			end
		end
		return true
	end

	npcHandler:setMessage(MESSAGE_GREET, "Looking for work, |PLAYERNAME|? Here are my {tasks}. {Report} when you're done, or {cancel} a task.")
	npcHandler:setMessage(MESSAGE_FAREWELL, "Good hunting.")
	npcHandler:setCallback(CALLBACK_GREET, greet)
	npcHandler:setCallback(CALLBACK_MESSAGE_DEFAULT, creatureSayCallback)
	npcHandler:addModule(FocusModule:new(), npcConfig.name, true, true, true)
	npcType:register(npcConfig)
end
