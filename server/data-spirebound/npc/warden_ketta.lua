-- Warden Ketta: keeps the Proving under the Arrival Yard (roadmap G2, scripts/spirebound/proving.lua).
local npcName = "Warden Ketta"
local npcType = Game.createNpcType(npcName)
local npcConfig = {}
npcConfig.name = npcName
npcConfig.description = "the Warden of the Proving"
npcConfig.health = 100
npcConfig.maxHealth = npcConfig.health
npcConfig.walkInterval = 0
npcConfig.walkRadius = 0
npcConfig.outfit = { lookType = 139, lookHead = 96, lookBody = 95, lookLegs = 114, lookFeet = 95, lookAddons = 0 }
npcConfig.flags = { floorchange = false }

local keywordHandler = KeywordHandler:new()
local npcHandler = NpcHandler:new(keywordHandler)
npcType.onThink = function(npc, interval) npcHandler:onThink(npc, interval) end
npcType.onAppear = function(npc, creature) npcHandler:onAppear(npc, creature) end
npcType.onDisappear = function(npc, creature) npcHandler:onDisappear(npc, creature) end
npcType.onMove = function(npc, creature, from, to) npcHandler:onMove(npc, creature, from, to) end
npcType.onSay = function(npc, creature, type, message) npcHandler:onSay(npc, creature, type, message) end
npcType.onCloseChannel = function(npc, player) npcHandler:onCloseChannel(npc, player) end

local ANSWERS = {
	{ { "spell", "spells", "bar", "attack" }, "Your first attack spell and your heal are on the action bar at the bottom: click one, or say its words. An attack spell needs a target: click the monster first. Say !spells for the whole list." },
	{ { "bramblejaw", "boss", "pit", "stone", "fight" }, "Bramblejaw is an old boar from the yard. Step on the red glowing stone in the east and you face it alone. It bites, and now and then it rears up: red smoke rises around it, so step away before it stomps. Keep your health above half. You can't die down here: I pull you out." },
	{ { "skip", "hearthgate", "leave", "portal" }, "The blue swirl in the north-east corner takes you straight to Hearthgate (it asks first). But the Proving pays gold, and it is the best place to learn your spells." },
	{ { "rat", "rats", "practice" }, "The rats are for practice. Try your attack spell on one before you face Bramblejaw." },
}

local function creatureSayCallback(npc, player, type, msg)
	if not npcHandler:checkInteraction(npc, player) then
		return false
	end
	if MsgContains(msg, "heal") then
		player:addHealth(player:getMaxHealth() - player:getHealth())
		player:addMana(player:getMaxMana() - player:getMana())
		player:getPosition():sendMagicEffect(CONST_ME_MAGIC_BLUE)
		npcHandler:say("There. Go on, show me what the Registrar gave you.", npc, player)
		return true
	end
	for _, row in ipairs(ANSWERS) do
		for _, word in ipairs(row[1]) do
			if MsgContains(msg, word) then
				npcHandler:say(row[2], npc, player)
				return true
			end
		end
	end
	npcHandler:say("Ask me about your {spells}, {Bramblejaw}, the {rats}, or how to {skip} to Hearthgate.", npc, player)
	return true
end

npcHandler:setMessage(MESSAGE_GREET, "Welcome to the Proving, climber. Try your new {spells} on the {rats}, then step on the red glowing stone to face {Bramblejaw} alone. I can {heal} you, or tell you how to {skip}.")
npcHandler:setCallback(CALLBACK_MESSAGE_DEFAULT, creatureSayCallback)
npcHandler:setMessage(MESSAGE_FAREWELL, "Go well.")
npcHandler:addModule(FocusModule:new(), npcConfig.name, true, true, true)
npcType:register(npcConfig)
