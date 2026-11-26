-- Patrolman Teodric (P9b, quest "The Last of the Patrol"): the Lost Patrol's survivor, held in the Smugglers' Cellar.
-- Placed at start-up by scripts/spirebound/escort.lua. Say "follow" and he walks with you (a companion of yours).
local npcName = "Patrolman Teodric"
local npcType = Game.createNpcType(npcName)
local npcConfig = {}
npcConfig.name = npcName
npcConfig.description = "a bruised patrolman of the Hearthgate watch"
npcConfig.health = 100
npcConfig.maxHealth = npcConfig.health
npcConfig.walkInterval = 0
npcConfig.walkRadius = 0
npcConfig.outfit = { lookType = 134, lookHead = 95, lookBody = 94, lookLegs = 94, lookFeet = 95, lookAddons = 0 }
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
	if MsgContains(msg, "follow") or MsgContains(msg, "home") or MsgContains(msg, "yes") then
		npcHandler:say(SpireEscort.start(player, npc), npc, player)
		return true
	end
	return false
end

npcHandler:setMessage(MESSAGE_GREET, "You're not a bandit... Did Captain Dorrow send you? Cut these ropes and I'll {follow} you home. I can't fight much, so keep them off me.")
npcHandler:setMessage(MESSAGE_FAREWELL, "Don't leave me here long.")
npcHandler:setCallback(CALLBACK_MESSAGE_DEFAULT, creatureSayCallback)
npcHandler:addModule(FocusModule:new(), npcConfig.name, true, true, true)
npcType:register(npcConfig)
