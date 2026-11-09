-- Taskmaster Ren (Hearthgate): daily hunting tasks (lib/spirebound/tasks.lua).
local npcName = "Taskmaster Ren"
local npcType = Game.createNpcType(npcName)
local npcConfig = {}
npcConfig.name = npcName
npcConfig.description = "the taskmaster"
npcConfig.health = 100
npcConfig.maxHealth = npcConfig.health
npcConfig.walkInterval = 0
npcConfig.walkRadius = 0
npcConfig.outfit = { lookType = 129, lookHead = 115, lookBody = 76, lookLegs = 76, lookFeet = 115, lookAddons = 2 }
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
	local lower = msg:lower()
	local s = SpireTasks.scope(player)
	local active = s:get("active")
	if MsgContains(lower, "tasks") or MsgContains(lower, "list") then
		local names = {}
		for _, t in ipairs(SpireTasks.list) do
			table.insert(names, string.format("{%s} (%d, %d gold)", t.monster:lower(), t.count, t.gold))
		end
		npcHandler:say("Hunting work: " .. table.concat(names, ", ") .. ". Name the monster to take the task.", npc, player)
		return true
	end
	if MsgContains(lower, "report") then
		local t = active and SpireTasks.get(active)
		if not t then
			npcHandler:say("You have no task. Ask me for the {tasks}.", npc, player)
		elseif (s:get("kills") or 0) < t.count then
			npcHandler:say(string.format("Not yet: %d of %d %ss.", s:get("kills") or 0, t.count, t.monster), npc, player)
		else
			s:remove("active")
			s:set("kills", 0)
			s:set("done_" .. t.id, os.time())
			s:set("points", (s:get("points") or 0) + t.points)
			player:addMoney(t.gold)
			npcHandler:say(string.format("Good work. %d gold and %d task point%s (you have %d).", t.gold, t.points, t.points > 1 and "s" or "", s:get("points")), npc, player)
		end
		return true
	end
	if MsgContains(lower, "cancel") and active then
		s:remove("active")
		s:set("kills", 0)
		npcHandler:say("Task dropped.", npc, player)
		return true
	end
	for _, t in ipairs(SpireTasks.list) do
		if MsgContains(lower, t.monster:lower()) then
			local ok, why = SpireTasks.canTake(active, s:get("done_" .. t.id), os.time())
			if not ok then
				npcHandler:say(why, npc, player)
			else
				s:set("active", t.id)
				s:set("kills", 0)
				npcHandler:say(string.format("Hunt %d %ss, then come back and {report}.", t.count, t.monster), npc, player)
			end
			return true
		end
	end
	return true
end

npcHandler:setMessage(MESSAGE_GREET, "Looking for work, |PLAYERNAME|? Ask me for the {tasks}, {report} when you're done, or {cancel} a task.")
npcHandler:setMessage(MESSAGE_FAREWELL, "Good hunting.")
npcHandler:setCallback(CALLBACK_MESSAGE_DEFAULT, creatureSayCallback)
npcHandler:addModule(FocusModule:new(), npcConfig.name, true, true, true)
npcType:register(npcConfig)
