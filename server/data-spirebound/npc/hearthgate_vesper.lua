-- Vesper, the Info Broker (DESIGN.md 8.1). Buys secrets and makes them public.
local npcName = "Vesper"
local npcType = Game.createNpcType(npcName)
local npcConfig = {}
npcConfig.name = npcName
npcConfig.description = "Vesper, the information broker"
npcConfig.health = 100
npcConfig.maxHealth = npcConfig.health
npcConfig.walkInterval = 0
npcConfig.walkRadius = 0
npcConfig.outfit = { lookType = 133, lookHead = 95, lookBody = 113, lookLegs = 114, lookFeet = 95, lookAddons = 3 }
npcConfig.flags = { floorchange = false }
npcConfig.voices = { interval = 20000, chance = 30, { text = "Everything has a price. Especially what nobody else knows." } }

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
	if lower == "secrets" or lower == "mine" then
		local names = {}
		for _, s in ipairs(SpireSecrets.foundList(player)) do
			local by = SpireSecrets.publicBy(s.id)
			table.insert(names, s.name .. (by and " (public)" or (" (unsold, " .. SpireSecrets.payout(s) .. " gold)")))
		end
		npcHandler:say(#names == 0 and "You haven't found anything yet. Go and look." or ("You know of: " .. table.concat(names, ", ") .. ". Say {sell} and the name to sell one."), npc, player)
		return true
	end
	if lower == "list" or lower == "board" then
		local lines = {}
		for _, s in ipairs(SpireSecrets.list) do
			local by = SpireSecrets.publicBy(s.id)
			if by then
				table.insert(lines, s.name .. " (Floor " .. s.floor .. "): " .. s.hint)
			end
		end
		npcHandler:say(#lines == 0 and "Nobody has sold me anything yet." or table.concat(lines, " | "), npc, player)
		return true
	end
	local name = lower:match("^sell%s+(.+)$")
	if name then
		for _, s in ipairs(SpireSecrets.list) do
			if s.name:lower() == name then
				local ok, why = SpireSecrets.canSell(SpireSecrets.hasFound(player, s.id), SpireSecrets.publicBy(s.id))
				if not ok then
					npcHandler:say(why, npc, player)
					return true
				end
				local pay = SpireSecrets.payout(s)
				SpireSecrets.markPublic(s.id, player:getName())
				player:setBankBalance(player:getBankBalance() + pay)
				player:kv():scoped("spirebound-informant"):set(s.id, os.time())
				npcHandler:say("A pleasure. " .. pay .. " gold, straight to your bank.", npc, player)
				Game.broadcastMessage(string.format("%s has sold word of %s on Floor %d! Ask Vesper in Hearthgate for directions.", player:getName(), s.name, s.floor), MESSAGE_EVENT_ADVANCE)
				return true
			end
		end
		npcHandler:say("I don't know a secret by that name.", npc, player)
		return true
	end
	return true
end

npcHandler:setMessage(MESSAGE_GREET, "Ah, |PLAYERNAME|. Found something? Say {secrets} to see what you know, {sell} <name> to sell it, or {list} for what's already public. Keeping a secret is your right. It never stops anyone else from finding it.")
npcHandler:setMessage(MESSAGE_FAREWELL, "Keep your eyes open.")
npcHandler:setCallback(CALLBACK_MESSAGE_DEFAULT, creatureSayCallback)
npcHandler:addModule(FocusModule:new(), npcConfig.name, true, true, true)
npcType:register(npcConfig)
