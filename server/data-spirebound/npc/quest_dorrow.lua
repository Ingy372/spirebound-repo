-- Captain Dorrow: story quest giver (lib/spirebound/quests.lua).
local npcName = "Captain Dorrow"
local npcType = Game.createNpcType(npcName)
local npcConfig = {}
npcConfig.name = npcName
npcConfig.description = "the captain of the north gate"
npcConfig.health = 100
npcConfig.maxHealth = npcConfig.health
npcConfig.walkInterval = 0
npcConfig.walkRadius = 0
local l = { 134, 95, 94, 94, 95, 1 }
npcConfig.outfit = { lookType = l[1], lookHead = l[2], lookBody = l[3], lookLegs = l[4], lookFeet = l[5], lookAddons = l[6] }
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

npcHandler:setMessage(MESSAGE_GREET, "Halt, |PLAYERNAME|. Hearthgate's north gate. If you're looking for honest work, ask about a {quest}. {Report} when it's done.")
npcHandler:setMessage(MESSAGE_FAREWELL, "Safe travels.")
npcHandler:setCallback(CALLBACK_MESSAGE_DEFAULT, creatureSayCallback)
npcHandler:addModule(FocusModule:new(), npcConfig.name, true, true, true)
npcType:register(npcConfig)
