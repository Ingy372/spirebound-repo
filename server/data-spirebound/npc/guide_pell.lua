-- Guide Pell: the Arrival Yard guide. Explains the basics in plain words and answers where to hunt.
local npcName = "Guide Pell"
local npcType = Game.createNpcType(npcName)
local npcConfig = {}
npcConfig.name = npcName
npcConfig.description = "the guide of the Arrival Yard"
npcConfig.health = 100
npcConfig.maxHealth = npcConfig.health
npcConfig.walkInterval = 0
npcConfig.walkRadius = 0
npcConfig.outfit = { lookType = 128, lookHead = 78, lookBody = 69, lookLegs = 76, lookFeet = 115, lookAddons = 0 }
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
	{ { "fight", "fighting", "attack", "combat" }, "To attack, click the monster's name in the Battle List (Ctrl+B opens it), or right-click the monster and choose Attack. When it falls, right-click the body to loot. Your health is the red bar: when it runs low, drink a health potion or step back into the safe square here. Use the practice club in your hand until the Registrar gives you real gear." },
	{ { "skill", "skills", "sword", "bar" }, "Your sword skills sit on the bar at the right of the screen: Shift+1 to Shift+6. Press J at any time to open the Journal: secrets, fishing, quests, tasks and the list of climbers." },
	{ { "spell", "spells", "magic" }, "Spells are learned on their own when you reach their level: no teacher, no cost. The first comes at level 8. Say !spells to read your list." },
	{ { "gold", "money", "coin", "shop", "sell" }, "Monsters drop coins and gear. Sell gear to the merchants, keep coins safe with Banker Tolliver, buy potions from Alchemist Ivo and arrows from Fletcher Tamsin. Anything you want to sell to other climbers goes on the market in any depot." },
	{ { "quest", "quests", "mission" }, "Townsfolk ask for help: Captain Dorrow at the north gate, Hunter Brannoch in the Hunters' Hall, Miller Agna in Millcross, Fisher Corwin by the river. Say 'quest' to them and 'report' when you finish. Your quest log always names the next step." },
	{ { "death", "die", "dying" }, "Dying costs experience and some items, unless you wear the blessings Priest Odran sells. Hardcore costs more. In Death Game, a death at the hands of a monster ends the character for good. Choose carefully." },
	{ { "registrar", "mode", "normal", "hardcore", "path", "vocation" }, "Registrar Maelis waits at the end of the path. She will ask your path (Vanguard, Ranger, Arcanist or Mystic) and how hard you will live (Normal, Hardcore or Death Game). Then you are sent to Hearthgate." },
	{ { "house", "houses", "home" }, "Houses are for sale in Hearthgate, Millcross and beside the river. You need level 20. Housewright Orla in Hearthgate sells furniture." },
	{ { "walk", "move" }, "Click the ground to walk, or use the arrow keys. Hold Ctrl and click to look at things." },
}

local function creatureSayCallback(npc, player, type, msg)
	if not npcHandler:checkInteraction(npc, player) then
		return false
	end
	if SpireHunt and MsgContains(msg, "hunt") then
		npcHandler:say(SpireHunt.advice(player:getLevel()), npc, player)
		return true
	end
	if MsgContains(msg, "heal") or MsgContains(msg, "hurt") then
		if player:getLevel() < 10 then  -- newcomers can be patched up before they reach the temple (2026-11-12 playthrough)
			player:addHealth(player:getMaxHealth() - player:getHealth())
			player:getPosition():sendMagicEffect(CONST_ME_MAGIC_BLUE)
			npcHandler:say("There, good as new. Priest Odran in Hearthgate heals climbers for free until level 50.", npc, player)
		else
			npcHandler:say("You have outgrown my bandages. Priest Odran in the Hearthgate temple can help you.", npc, player)
		end
		return true
	end
	if SpireQuests.talk(npc, npcHandler, player, msg, npcName) then
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
	npcHandler:say("Ask me about {fighting}, {skills}, {spells}, {gold}, {quests}, {death}, {registrar}, {house} or where to {hunt}.", npc, player)
	return true
end

npcHandler:setMessage(MESSAGE_GREET, "Welcome, climber. I am Guide Pell. Walk the stone path east and each stop teaches one thing. Take on my {quest} to learn to fight, ask me to {heal} you, or ask about {skills}, {spells}, {gold}, {death} or where to {hunt}.")
npcHandler:setMessage(MESSAGE_FAREWELL, "Good luck, climber.")
npcHandler:setCallback(CALLBACK_MESSAGE_DEFAULT, creatureSayCallback)
npcHandler:addModule(FocusModule:new(), npcConfig.name, true, true, true)
npcType:register(npcConfig)
