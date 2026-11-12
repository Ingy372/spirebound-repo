-- Ascendant Veyra: promotion at level 20 for 20,000 gold (DESIGN.md 5.2). Vocation ids: 1-4 promote to 5-8.
local npcName = "Ascendant Veyra"
local npcType = Game.createNpcType(npcName)
local npcConfig = {}
npcConfig.name = npcName
npcConfig.description = "the Ascendant of Hearthgate"
npcConfig.health = 100
npcConfig.maxHealth = npcConfig.health
npcConfig.walkInterval = 0
npcConfig.walkRadius = 0
npcConfig.outfit = { lookType = 140, lookHead = 0, lookBody = 87, lookLegs = 57, lookFeet = 76, lookAddons = 0 }
npcConfig.flags = { floorchange = false }

local keywordHandler = KeywordHandler:new()
local npcHandler = NpcHandler:new(keywordHandler)
npcType.onThink = function(npc, interval) npcHandler:onThink(npc, interval) end
npcType.onAppear = function(npc, creature) npcHandler:onAppear(npc, creature) end
npcType.onDisappear = function(npc, creature) npcHandler:onDisappear(npc, creature) end
npcType.onMove = function(npc, creature, from, to) npcHandler:onMove(npc, creature, from, to) end
npcType.onSay = function(npc, creature, type, message) npcHandler:onSay(npc, creature, type, message) end
npcType.onCloseChannel = function(npc, player) npcHandler:onCloseChannel(npc, player) end

local PROMOTION_LEVEL = 20
local PROMOTION_PRICE = 20000

local function creatureSayCallback(npc, player, type, msg)
	if not npcHandler:checkInteraction(npc, player) then
		return false
	end
	local pid = player:getId()
	local voc = player:getVocation()
	local id = voc:getId()
	if MsgContains(msg, "promot") or MsgContains(msg, "ascend") then
		if id >= 5 then
			npcHandler:say("You have already ascended, " .. voc:getName() .. ". There is no higher step.", npc, player)
		elseif id == 0 then
			npcHandler:say("You have no path yet. Speak to Registrar Maelis first.", npc, player)
		elseif player:getLevel() < PROMOTION_LEVEL then
			npcHandler:say(string.format("Come back at level %d. You are level %d.", PROMOTION_LEVEL, player:getLevel()), npc, player)
		else
			npcHandler:say(string.format("For %d gold I can promote you to a %s. Your body and mind recover faster. Do you accept? {yes} or {no}.", PROMOTION_PRICE, Vocation(id + 4):getName()), npc, player)
			npcHandler:setTopic(pid, 1)
		end
		return true
	end
	if npcHandler:getTopic(pid) == 1 then
		npcHandler:setTopic(pid, 0)
		if MsgContains(msg, "yes") then
			if id < 1 or id > 4 or player:getLevel() < PROMOTION_LEVEL then
				npcHandler:say("Something has changed. Ask me again.", npc, player)
			elseif not player:removeMoney(PROMOTION_PRICE) then
				npcHandler:say("You do not have enough gold with you.", npc, player)
			else
				player:setVocation(Vocation(id + 4))
				player:getPosition():sendMagicEffect(CONST_ME_GIFT_WRAPS)
				npcHandler:say("It is done. You are now a " .. player:getVocation():getName() .. ".", npc, player)
			end
		else
			npcHandler:say("As you wish.", npc, player)
		end
		return true
	end
	return true
end

npcHandler:setMessage(MESSAGE_GREET, "Welcome to the Ascendancy, |PLAYERNAME|. Climbers of level 20 may be {promoted} here, for a fee.")
npcHandler:setMessage(MESSAGE_FAREWELL, "Climb well.")
npcHandler:setCallback(CALLBACK_MESSAGE_DEFAULT, creatureSayCallback)
npcHandler:addModule(FocusModule:new(), npcConfig.name, true, true, true)
npcType:register(npcConfig)
