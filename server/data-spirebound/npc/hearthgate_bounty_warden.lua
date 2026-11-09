-- Bounty Warden Cass (Hearthgate): bounty board on murderers (DESIGN.md 6.4 item 5).
local npcName = "Bounty Warden Cass"
local npcType = Game.createNpcType(npcName)
local npcConfig = {}
npcConfig.name = npcName
npcConfig.description = "the bounty warden"
npcConfig.health = 100
npcConfig.maxHealth = npcConfig.health
npcConfig.walkInterval = 0
npcConfig.walkRadius = 0
npcConfig.outfit = { lookType = 131, lookHead = 0, lookBody = 94, lookLegs = 94, lookFeet = 94, lookAddons = 0 }
npcConfig.flags = { floorchange = false }
npcConfig.voices = { interval = 20000, chance = 30, { text = "Murderers walk among us. Their heads are worth gold." } }

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
	if MsgContains(lower, "board") or MsgContains(lower, "list") then
		local list = SpireBounty.list()
		if #list == 0 then
			npcHandler:say("No bounties right now. The tower is quiet.", npc, player)
		else
			local lines = {}
			for i = 1, math.min(10, #list) do
				table.insert(lines, string.format("%s: %d gold", list[i].name or "?", list[i].total))
			end
			npcHandler:say("Wanted: " .. table.concat(lines, ", ") .. ".", npc, player)
		end
		return true
	end
	-- "bounty <amount> <name>"
	local amount, name = lower:match("^bounty%s+(%d+)%s+(.+)$")
	if amount then
		amount = tonumber(amount)
		local target = Player(name)
		if not target then
			npcHandler:say("I only post bounties on murderers who are in the tower right now.", npc, player)
		elseif not SpirePvP.isMurderer(target) then
			npcHandler:say(target:getName() .. " is no murderer. I won't post a bounty.", npc, player)
		elseif amount < SpireBounty.MIN_PLAYER_BOUNTY then
			npcHandler:say("The smallest bounty I post is " .. SpireBounty.MIN_PLAYER_BOUNTY .. " gold.", npc, player)
		elseif player:getBankBalance() < amount then
			npcHandler:say("You don't have that much in the bank.", npc, player)
		else
			player:setBankBalance(player:getBankBalance() - amount)
			local total = SpireBounty.add(target:getGuid(), target:getName(), amount, player:getName())
			npcHandler:say("Posted. " .. target:getName() .. "'s head is now worth " .. total .. " gold.", npc, player)
			Game.broadcastMessage(string.format("The bounty on %s is now %d gold.", target:getName(), total), MESSAGE_EVENT_ADVANCE)
		end
		return true
	end
	return true
end

npcHandler:setMessage(MESSAGE_GREET, "Looking for work, |PLAYERNAME|? See the {board}, or post one: say {bounty} <amount> <name>. Gold comes from your bank. Friends, guildmates and partners can't collect on each other.")
npcHandler:setMessage(MESSAGE_FAREWELL, "Keep your blade clean.")
npcHandler:setCallback(CALLBACK_MESSAGE_DEFAULT, creatureSayCallback)
npcHandler:addModule(FocusModule:new(), npcConfig.name, true, true, true)
npcType:register(npcConfig)
